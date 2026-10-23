"""HTTP server and pages, built only on the Python standard library."""

import email.parser
import email.policy
import hashlib
import hmac
import html
import mimetypes
import os
import re
import secrets
import traceback
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlencode, urlparse

from . import content, services as svc
from .db import connect, get_setting, set_setting

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
COOKIE = "t1_session"
PAGE_SIZE = 50
MAX_BODY = 20 * 1024 * 1024  # 20 MB, enough for a CSV of 10,000+ associates

esc = html.escape


class Redirect(Exception):
    def __init__(self, location):
        self.location = location


class HttpError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message


def redirect(path, msg=None, error=None):
    params = {}
    if msg:
        params["msg"] = msg
    if error:
        params["error"] = error
    if params:
        path += ("&" if "?" in path else "?") + urlencode(params)
    raise Redirect(path)


# ---------------------------------------------------------------------------
# Request context
# ---------------------------------------------------------------------------

class Request:
    def __init__(self, handler, method):
        self.handler = handler
        self.method = method
        parsed = urlparse(handler.path)
        self.path = parsed.path.rstrip("/") or "/"
        self.query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        self.form = {}
        self.form_lists = {}
        self.files = {}
        self.conn = None
        self.user = None
        self.csrf = None
        self.token = None
        jar = cookies.SimpleCookie(handler.headers.get("Cookie", ""))
        if COOKIE in jar:
            self.token = jar[COOKIE].value
        self.set_cookie = None

    def read_body(self):
        length = int(self.handler.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise HttpError(413, "The upload is too large.")
        raw = self.handler.rfile.read(length) if length else b""
        ctype = self.handler.headers.get("Content-Type", "")
        if ctype.startswith("multipart/form-data"):
            msg = email.parser.BytesParser(policy=email.policy.HTTP).parsebytes(
                b"Content-Type: " + ctype.encode() + b"\r\n\r\n" + raw
            )
            for part in msg.iter_parts():
                name = part.get_param("name", header="content-disposition")
                if not name:
                    continue
                payload = part.get_payload(decode=True) or b""
                if part.get_filename():
                    self.files[name] = payload
                else:
                    value = payload.decode("utf-8", "replace")
                    self.form[name] = value
                    self.form_lists.setdefault(name, []).append(value)
        else:
            parsed = parse_qs(raw.decode("utf-8", "replace"), keep_blank_values=True)
            self.form_lists = parsed
            self.form = {k: v[0] for k, v in parsed.items()}

    def get(self, key, default=""):
        return self.form.get(key, default)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout(req, title, body, active=""):
    user = req.user
    org = esc(get_setting(req.conn, "org_name", "Our Organization"))
    nav = ""
    if user:
        links = [
            ("dashboard", "/dashboard", "My course"),
            ("lab", "/lab", "Lab"),
            ("charter", "/charter", "My agent charter"),
            ("templates", "/templates", "Templates"),
            ("final", "/final", "Final assessment"),
        ]
        if user["role"] == "admin":
            links.insert(0, ("admin", "/admin", "Admin"))
        items = "".join(
            '<a href="{}" class="{}">{}</a>'.format(url, "active" if key == active else "", label)
            for key, url, label in links
        )
        nav = """<nav class="topnav" aria-label="Main">{items}</nav>
<div class="userbox"><a href="/account">{name}</a>
<form method="post" action="/logout" class="inline">{csrf}<button class="linklike" type="submit">Sign out</button></form></div>""".format(
            items=items, name=esc(user["name"]), csrf=csrf_field(req)
        )
    flash = ""
    if req.query.get("msg"):
        flash += '<div class="flash ok" role="status">{}</div>'.format(esc(req.query["msg"]))
    if req.query.get("error"):
        flash += '<div class="flash err" role="alert">{}</div>'.format(esc(req.query["error"]))
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Copilot Agent Builder Training</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site">
<div class="brand"><a href="/"><span class="logo" aria-hidden="true">T1</span> Copilot Agent Builder Training</a>
<span class="org">{org}</span></div>
{nav}
</header>
<main id="main">
{flash}
{body}
</main>
<footer class="site">Simple Copilot Agent Builder (T1) &middot; content edition {edition} &middot;
Microsoft features vary by licence and tenant; always check your own screen.</footer>
<script src="/static/app.js"></script>
</body>
</html>""".format(title=esc(title), org=org, nav=nav, flash=flash, body=body, edition=content.EDITION_DATE)


def csrf_field(req):
    return '<input type="hidden" name="csrf" value="{}">'.format(esc(req.csrf or ""))


def progress_bar(percent, label=None):
    label = label or "{}% complete".format(percent)
    return (
        '<div class="progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{0}" '
        'aria-label="{1}"><div class="bar" style="width:{0}%"></div></div><div class="progress-label">{1}</div>'
    ).format(percent, esc(label))


def check(ok):
    return '<span class="badge ok">Done</span>' if ok else '<span class="badge todo">To do</span>'


# ---------------------------------------------------------------------------
# Signing for final-assessment question sets
# ---------------------------------------------------------------------------

def _secret(conn):
    value = get_setting(conn, "secret")
    if not value:
        value = secrets.token_hex(32)
        set_setting(conn, "secret", value)
        conn.commit()
    return value


def sign(conn, text):
    return hmac.new(_secret(conn).encode(), text.encode(), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Auth pages
# ---------------------------------------------------------------------------

def page_setup(req):
    if svc.admin_exists(req.conn):
        redirect("/login")
    error = ""
    if req.method == "POST":
        try:
            if req.get("password") != req.get("password2"):
                raise ValueError("The passwords do not match.")
            err = svc.validate_password(req.get("password"))
            if err:
                raise ValueError(err)
            svc.create_user(req.conn, req.get("associate_id"), req.get("name"), req.get("password"), role="admin")
            if req.get("org_name").strip():
                set_setting(req.conn, "org_name", req.get("org_name").strip())
                req.conn.commit()
            redirect("/login", msg="Administrator created. Please sign in.")
        except ValueError as e:
            error = str(e)
        except Exception as e:  # e.g. duplicate ID
            if isinstance(e, Redirect):
                raise
            error = "Could not create the account: {}".format(e)
    body = """
<section class="card narrow">
<h1>Welcome! Set up the training app</h1>
<p>Create the first administrator account. Administrators can import associates, track progress and download reports.</p>
{err}
<form method="post" class="form">
<label>Organization name <input name="org_name" value="{org}" maxlength="100"></label>
<label>Administrator ID <input name="associate_id" required maxlength="50" value="admin"></label>
<label>Display name <input name="name" required maxlength="100" value="{name}"></label>
<label>Password (8+ characters) <input type="password" name="password" required minlength="8"></label>
<label>Confirm password <input type="password" name="password2" required minlength="8"></label>
<button type="submit" class="btn primary">Create administrator</button>
</form>
</section>""".format(
        err='<div class="flash err" role="alert">{}</div>'.format(esc(error)) if error else "",
        org=esc(req.get("org_name", "")), name=esc(req.get("name", "Training Administrator")),
    )
    return layout(req, "Set up", body)


def page_login(req):
    if req.user:
        redirect("/")
    error = ""
    if req.method == "POST":
        user = svc.authenticate(req.conn, req.get("associate_id"), req.get("password"))
        if user:
            req.token = svc.create_session(req.conn, user["id"])
            req.set_cookie = req.token
            redirect("/")
        error = "Associate ID or password is not correct."
    body = """
<section class="card narrow">
<h1>Sign in</h1>
<p>Build your own helpful AI agent with Microsoft 365 Copilot Agent Builder. No coding needed.</p>
{err}
<form method="post" class="form">
<label>Associate ID <input name="associate_id" required autofocus maxlength="50" value="{aid}" autocomplete="username"></label>
<label>Password <input type="password" name="password" required autocomplete="current-password"></label>
<button type="submit" class="btn primary">Sign in</button>
</form>
<p class="muted">First time here? <a href="/register">Create your learner account</a>.</p>
</section>""".format(
        err='<div class="flash err" role="alert">{}</div>'.format(esc(error)) if error else "",
        aid=esc(req.get("associate_id")),
    )
    return layout(req, "Sign in", body)


def page_register(req):
    if req.user:
        redirect("/")
    error = ""
    if req.method == "POST":
        try:
            if req.get("password") != req.get("password2"):
                raise ValueError("The passwords do not match.")
            user = svc.register(
                req.conn, req.get("associate_id"), req.get("name"), req.get("password"),
                department=req.get("department"), email=req.get("email"),
            )
            req.token = svc.create_session(req.conn, user["id"])
            req.set_cookie = req.token
            redirect("/dashboard", msg="Welcome, {}! Your account is ready.".format(user["name"]))
        except ValueError as e:
            error = str(e)
    depts = svc.departments(req.conn)
    datalist = "".join('<option value="{}">'.format(esc(d)) for d in depts)
    body = """
<section class="card narrow">
<h1>Create your learner account</h1>
<p>Use your company associate ID. If your administrator already loaded your details, they will be kept.</p>
{err}
<form method="post" class="form">
<label>Associate ID <input name="associate_id" required maxlength="50" value="{aid}" autocomplete="username"></label>
<label>Full name <input name="name" required maxlength="100" value="{name}"></label>
<label>Work email (optional) <input type="email" name="email" maxlength="150" value="{email}"></label>
<label>Department <input name="department" maxlength="100" list="depts" value="{dept}"></label>
<datalist id="depts">{datalist}</datalist>
<label>Password (8+ characters) <input type="password" name="password" required minlength="8" autocomplete="new-password"></label>
<label>Confirm password <input type="password" name="password2" required minlength="8" autocomplete="new-password"></label>
<button type="submit" class="btn primary">Create account</button>
</form>
<p class="muted">Already registered? <a href="/login">Sign in</a>.</p>
</section>""".format(
        err='<div class="flash err" role="alert">{}</div>'.format(esc(error)) if error else "",
        aid=esc(req.get("associate_id")), name=esc(req.get("name")), email=esc(req.get("email")),
        dept=esc(req.get("department")), datalist=datalist,
    )
    return layout(req, "Register", body)


def page_logout(req):
    if req.token:
        svc.end_session(req.conn, req.token)
    req.set_cookie = ""
    redirect("/login", msg="You have signed out.")


def page_account(req):
    if req.method == "POST":
        if not svc.verify_password(req.get("current"), req.user["password_hash"]):
            redirect("/account", error="Your current password is not correct.")
        if req.get("password") != req.get("password2"):
            redirect("/account", error="The new passwords do not match.")
        try:
            svc.set_password(req.conn, req.user["id"], req.get("password"))
        except ValueError as e:
            redirect("/account", error=str(e))
        req.set_cookie = ""
        redirect("/login", msg="Password changed. Please sign in again.")
    u = req.user
    body = """
<section class="card narrow">
<h1>My account</h1>
<dl class="facts"><dt>Associate ID</dt><dd>{aid}</dd><dt>Name</dt><dd>{name}</dd>
<dt>Department</dt><dd>{dept}</dd><dt>Email</dt><dd>{email}</dd></dl>
<h2>Change password</h2>
<form method="post" class="form">{csrf}
<label>Current password <input type="password" name="current" required></label>
<label>New password (8+ characters) <input type="password" name="password" required minlength="8"></label>
<label>Confirm new password <input type="password" name="password2" required minlength="8"></label>
<button class="btn primary" type="submit">Change password</button>
</form>
</section>""".format(
        aid=esc(u["associate_id"]), name=esc(u["name"]), dept=esc(u["department"] or "-"),
        email=esc(u["email"] or "-"), csrf=csrf_field(req),
    )
    return layout(req, "My account", body)


# ---------------------------------------------------------------------------
# Learner pages
# ---------------------------------------------------------------------------

def page_home(req):
    if req.user["role"] == "admin":
        redirect("/admin")
    redirect("/dashboard")


def page_dashboard(req):
    uid = req.user["id"]
    prog = svc.user_progress(req.conn, uid)
    done = svc.completed_lesson_ids(req.conn, uid)
    passed = svc.passed_module_ids(req.conn, uid)
    label, url = svc.next_step(req.conn, uid)
    rows = []
    for m in svc.list_modules(req.conn):
        lessons = svc.module_lessons(req.conn, m["id"])
        n_done = sum(1 for l in lessons if l["id"] in done)
        has_quiz = bool(svc.module_questions(req.conn, m["id"]))
        if n_done == len(lessons) and (not has_quiz or m["id"] in passed):
            status = '<span class="badge ok">Complete</span>'
        elif n_done:
            status = '<span class="badge prog">In progress</span>'
        else:
            status = '<span class="badge todo">Not started</span>'
        quiz = ""
        if has_quiz:
            quiz = (
                '<span class="badge ok">Quiz passed</span>' if m["id"] in passed
                else '<a href="/module/{}/quiz">Quiz</a>'.format(m["slug"])
            )
        rows.append(
            """<li class="module-row"><div><a class="module-title" href="/module/{slug}">{title}</a>
<div class="muted">{summary}</div></div>
<div class="module-meta">{n}/{t} lessons &middot; {mins} min &middot; {quiz} {status}</div></li>""".format(
                slug=m["slug"], title=esc(m["title"]), summary=esc(m["summary"]), n=n_done, t=len(lessons),
                mins=m["minutes"], quiz=quiz, status=status,
            )
        )
    final = prog["final"]
    final_txt = "Not taken yet"
    if final:
        final_txt = "Best score {}/{} ({})".format(final["score"], final["total"], "passed" if final["passed"] else "not passed yet")
    body = """
<section class="hero">
<h1>Hello, {name}</h1>
<p>Your goal: build <strong>one agent with one purpose</strong>, test it, and use it safely.</p>
{bar}
<a class="btn primary" href="{url}">{label}</a>
</section>
<section class="grid-4">
<div class="stat"><div class="num">{dl}/{tl}</div><div>Lessons {lk}</div></div>
<div class="stat"><div class="num">{pm}/{qm}</div><div>Module quizzes passed</div></div>
<div class="stat"><div class="num">{lab}/{labreq}</div><div>Required lab steps {labk}</div></div>
<div class="stat"><div class="num">{fk}</div><div>Final: {final}</div></div>
</section>
<section>
<h2>Course modules</h2>
<ol class="modules">{rows}</ol>
</section>
<section class="card">
<h2>Requirements for your certificate</h2>
<ul class="checklist">
<li>{c1} Complete every lesson</li>
<li>{c2} Complete lab steps 1 to {labreq} in Microsoft 365 Copilot</li>
<li>{c3} Pass the final assessment ({pm_pct}% or higher)</li>
</ul>
<p>{cert}</p>
<p class="muted">Finished? <a href="/feedback">Tell us what you thought of the course</a>.</p>
</section>""".format(
        name=esc(req.user["name"]), bar=progress_bar(prog["percent"]), url=url, label=esc(label),
        dl=prog["done_lessons"], tl=prog["total_lessons"], lk=check(prog["lessons_ok"]),
        pm=prog["passed_modules"], qm=prog["quiz_modules"], lab=prog["lab_required_done"],
        labreq=content.LAB_REQUIRED_STEPS, labk=check(prog["lab_ok"]),
        fk="Passed" if prog["final_ok"] else "-", final=esc(final_txt), rows="".join(rows),
        c1=check(prog["lessons_ok"]), c2=check(prog["lab_ok"]), c3=check(prog["final_ok"]),
        pm_pct=esc(get_setting(req.conn, "pass_mark")),
        cert='<a class="btn primary" href="/certificate">View your certificate</a>' if prog["certified"]
        else "Your certificate unlocks when all three are done.",
    )
    return layout(req, "My course", body, "dashboard")


def _module_or_404(req, slug):
    m = svc.get_module(req.conn, slug)
    if not m:
        raise HttpError(404, "That module does not exist.")
    return m


def page_module(req, slug):
    m = _module_or_404(req, slug)
    done = svc.completed_lesson_ids(req.conn, req.user["id"])
    lessons = svc.module_lessons(req.conn, m["id"])
    items = "".join(
        '<li><a href="/module/{}/lesson/{}">{}</a> <span class="muted">({} min)</span> {}</li>'.format(
            m["slug"], l["slug"], esc(l["title"]), l["minutes"], check(l["id"] in done)
        )
        for l in lessons
    )
    questions = svc.module_questions(req.conn, m["id"])
    quiz = ""
    if questions:
        passed = m["id"] in svc.passed_module_ids(req.conn, req.user["id"])
        quiz = """<div class="card"><h2>Module quiz</h2><p>{n} questions. Pass mark {pm}%. You can retry as often as you like.</p>
<p>{status}</p><a class="btn" href="/module/{slug}/quiz">{label}</a></div>""".format(
            n=len(questions), pm=esc(get_setting(req.conn, "pass_mark")), slug=m["slug"],
            status=check(passed) + (" Passed" if passed else ""), label="Retake quiz" if passed else "Start quiz",
        )
    body = """<p class="crumbs"><a href="/dashboard">My course</a> &rsaquo; {title}</p>
<h1>{title}</h1><p class="lead">{summary}</p>
<div class="card"><h2>Lessons</h2><ol class="lesson-list">{items}</ol></div>{quiz}""".format(
        title=esc(m["title"]), summary=esc(m["summary"]), items=items, quiz=quiz
    )
    return layout(req, m["title"], body, "dashboard")


def page_lesson(req, slug, lslug):
    m = _module_or_404(req, slug)
    lesson = svc.get_lesson(req.conn, m["id"], lslug)
    if not lesson:
        raise HttpError(404, "That lesson does not exist.")
    lessons = svc.module_lessons(req.conn, m["id"])
    idx = [l["id"] for l in lessons].index(lesson["id"])
    if req.method == "POST":
        svc.complete_lesson(req.conn, req.user["id"], lesson["id"])
        if idx + 1 < len(lessons):
            redirect("/module/{}/lesson/{}".format(slug, lessons[idx + 1]["slug"]), msg="Lesson complete.")
        if svc.module_questions(req.conn, m["id"]):
            redirect("/module/{}/quiz".format(slug), msg="All lessons done. Check your understanding with the quiz.")
        label, url = svc.next_step(req.conn, req.user["id"])
        redirect(url, msg="Module complete.")
    done = lesson["id"] in svc.completed_lesson_ids(req.conn, req.user["id"])
    prev_link = (
        '<a class="btn" href="/module/{}/lesson/{}">&larr; Previous</a>'.format(slug, lessons[idx - 1]["slug"])
        if idx > 0 else '<a class="btn" href="/module/{}">&larr; Module overview</a>'.format(slug)
    )
    body = """<p class="crumbs"><a href="/dashboard">My course</a> &rsaquo; <a href="/module/{slug}">{mtitle}</a> &rsaquo; Lesson {n} of {t}</p>
<article class="lesson card">
<h1>{title}</h1>
<p class="muted">About {mins} minutes</p>
{content}
</article>
<div class="lesson-nav">{prev}
<form method="post" class="inline">{csrf}<button class="btn primary" type="submit">{btn}</button></form></div>""".format(
        slug=slug, mtitle=esc(m["title"]), n=idx + 1, t=len(lessons), title=esc(lesson["title"]),
        mins=lesson["minutes"], content=lesson["body_html"], prev=prev_link, csrf=csrf_field(req),
        btn="Next &rarr;" if done else "Mark lesson complete &rarr;",
    )
    return layout(req, lesson["title"], body, "dashboard")


def _quiz_form(req, questions, action, intro, signed=False):
    blocks = []
    for n, q in enumerate(questions, start=1):
        opts = "".join(
            '<label class="option"><input type="radio" name="q{qid}" value="{i}" required> {text}</label>'.format(
                qid=q["id"], i=i, text=esc(t)
            )
            for i, t in svc.shuffled_options(q)
        )
        tag = ' <span class="badge prog">Scenario</span>' if q["scenario"] else ""
        blocks.append(
            '<fieldset class="question"><legend><span class="qnum">{n}.</span> {prompt}{tag}</legend>{opts}</fieldset>'.format(
                n=n, prompt=esc(q["prompt"]), tag=tag, opts=opts
            )
        )
    qids = ",".join(str(q["id"]) for q in questions)
    sig = '<input type="hidden" name="sig" value="{}">'.format(sign(req.conn, qids)) if signed else ""
    return """{intro}<form method="post" action="{action}" class="quiz">{csrf}
<input type="hidden" name="qids" value="{qids}">{sig}
{blocks}
<button type="submit" class="btn primary">Submit answers</button></form>""".format(
        intro=intro, action=action, csrf=csrf_field(req), qids=qids, sig=sig, blocks="".join(blocks)
    )


def _read_answers(req, allowed_ids):
    answers = {}
    for qid in allowed_ids:
        raw = req.get("q{}".format(qid))
        answers[qid] = int(raw) if raw.isdigit() else None
    return answers


def page_module_quiz(req, slug):
    m = _module_or_404(req, slug)
    questions = svc.module_questions(req.conn, m["id"])
    if not questions:
        redirect("/module/" + slug, msg="This module has no quiz.")
    if req.method == "POST":
        ids = [q["id"] for q in questions]
        attempt = svc.grade_attempt(req.conn, req.user["id"], "module", ids, _read_answers(req, ids), m["id"])
        redirect("/attempt/{}".format(attempt))
    intro = """<p class="crumbs"><a href="/dashboard">My course</a> &rsaquo; <a href="/module/{slug}">{title}</a> &rsaquo; Quiz</p>
<h1>Quiz: {title}</h1><p>Answer all {n} questions. Pass mark {pm}%.</p>""".format(
        slug=slug, title=esc(m["title"]), n=len(questions), pm=esc(get_setting(req.conn, "pass_mark"))
    )
    return layout(req, "Quiz", _quiz_form(req, questions, "/module/{}/quiz".format(slug), intro), "dashboard")


def page_final(req):
    uid = req.user["id"]
    if req.method == "POST":
        qids = req.get("qids")
        if not hmac.compare_digest(sign(req.conn, qids), req.get("sig")):
            redirect("/final", error="The assessment form expired. Please start again.")
        ids = [int(x) for x in qids.split(",") if x.isdigit()]
        attempt = svc.grade_attempt(req.conn, uid, "final", ids, _read_answers(req, ids))
        redirect("/attempt/{}".format(attempt))
    prog = svc.user_progress(req.conn, uid)
    if req.query.get("start") != "1":
        history = req.conn.execute(
            "SELECT * FROM quiz_attempts WHERE user_id = ? AND kind = 'final' ORDER BY completed_at DESC", (uid,)
        ).fetchall()
        hist = "".join(
            '<tr><td>{}</td><td>{}/{}</td><td>{}</td><td><a href="/attempt/{}">Review</a></td></tr>'.format(
                esc(a["completed_at"]), a["score"], a["total"], "Passed" if a["passed"] else "Not passed", a["id"]
            )
            for a in history
        )
        warn = ""
        if not prog["lessons_ok"]:
            warn = '<div class="callout note">We recommend finishing all lessons first ({}/{} done). You can still try the assessment.</div>'.format(
                prog["done_lessons"], prog["total_lessons"]
            )
        body = """<h1>Final assessment</h1>
<p>{n} questions drawn from the question bank, including the three key knowledge-check questions. Pass mark {pm}%.
A new set of questions is chosen each time, and you can retake it.</p>
{warn}
<a class="btn primary" href="/final?start=1">Start the final assessment</a>
{hist}""".format(
            n=content.FINAL_QUESTION_COUNT, pm=esc(get_setting(req.conn, "pass_mark")), warn=warn,
            hist="<h2>Your attempts</h2><table class='grid'><tr><th>Date (UTC)</th><th>Score</th><th>Result</th><th></th></tr>{}</table>".format(hist) if hist else "",
        )
        return layout(req, "Final assessment", body, "final")
    questions = svc.final_questions(req.conn)
    intro = "<h1>Final assessment</h1><p>Answer all {} questions, then submit.</p>".format(len(questions))
    return layout(req, "Final assessment", _quiz_form(req, questions, "/final", intro, signed=True), "final")


def page_attempt(req, attempt_id):
    owner = None if req.user["role"] == "admin" else req.user["id"]
    attempt, answers = svc.attempt_review(req.conn, int(attempt_id), owner)
    if not attempt:
        raise HttpError(404, "Attempt not found.")
    pct = round(100 * attempt["score"] / attempt["total"]) if attempt["total"] else 0
    items = []
    for n, a in enumerate(answers, start=1):
        opts = svc.question_options(a)
        ci = a["chosen_index"]
        chosen = opts[ci] if ci is not None and 0 <= ci < len(opts) else "(no answer)"
        src = (
            '<div class="muted small">Reference: <a href="{0}" target="_blank" rel="noopener">{0}</a></div>'.format(esc(a["source_url"]))
            if a["source_url"] else ""
        )
        items.append(
            """<div class="review {cls}"><h3>{n}. {prompt}</h3>
<p><strong>{verdict}</strong> Your answer: {chosen}</p>
{correct}<p class="why">{rationale}</p>{src}</div>""".format(
                cls="right" if a["correct"] else "wrong", n=n, prompt=esc(a["prompt"]),
                verdict="Correct." if a["correct"] else "Not quite.", chosen=esc(chosen),
                correct="" if a["correct"] else "<p>Correct answer: <strong>{}</strong></p>".format(esc(opts[a["correct_index"]])),
                rationale=esc(a["rationale"]), src=src,
            )
        )
    if attempt["kind"] == "module":
        mod = req.conn.execute("SELECT * FROM modules WHERE id = ?", (attempt["module_id"],)).fetchone()
        retry = "/module/{}/quiz".format(mod["slug"])
        title = "Quiz result: " + mod["title"]
    else:
        retry = "/final?start=1"
        title = "Final assessment result"
    label, url = svc.next_step(req.conn, attempt["user_id"])
    body = """<h1>{title}</h1>
<div class="result {cls}"><div class="num">{score}/{total}</div><div>{pct}% &middot; {verdict}</div></div>
<p><a class="btn" href="{retry}">Try again</a> <a class="btn primary" href="{url}">{label}</a></p>
<h2>Review your answers</h2>{items}""".format(
        title=esc(title), cls="pass" if attempt["passed"] else "fail", score=attempt["score"], total=attempt["total"],
        pct=pct, verdict="Passed" if attempt["passed"] else "Not passed yet. Read the explanations and try again.",
        retry=retry, url=url, label=esc(label), items="".join(items),
    )
    return layout(req, title, body, "final" if attempt["kind"] == "final" else "dashboard")


def page_lab(req):
    uid = req.user["id"]
    if req.method == "POST":
        step = int(req.get("step", "0") or 0)
        if 1 <= step <= len(content.LAB_STEPS):
            svc.set_lab_step(req.conn, uid, step, req.get("done") == "1", req.get("note"))
        redirect("/lab#step{}".format(step) if step else "/lab", msg="Lab progress saved.")
    done = svc.lab_done_steps(req.conn, uid)
    req_done = sum(1 for s in range(1, content.LAB_REQUIRED_STEPS + 1) if s in done)
    rows = []
    for no, instruction, evidence in content.LAB_STEPS:
        d = done.get(no)
        rows.append(
            """<li class="lab-step {cls}" id="step{no}">
<div class="lab-head"><span class="stepno">{no}</span><div><strong>{instr}</strong>{opt}
<div class="muted">Done when: {evidence}</div></div></div>
<form method="post" class="lab-form">{csrf}<input type="hidden" name="step" value="{no}">
<label class="sr-only" for="note{no}">Note for step {no}</label>
<input id="note{no}" name="note" placeholder="Optional note (no confidential data)" value="{note}" maxlength="1000">
<input type="hidden" name="done" value="{next}">
<button class="btn {btncls}" type="submit">{btn}</button></form></li>""".format(
                cls="done" if d else "", no=no, instr=esc(instruction), evidence=esc(evidence),
                opt="" if no <= content.LAB_REQUIRED_STEPS else ' <span class="badge todo">Optional</span>',
                csrf=csrf_field(req), note=esc(d["note"]) if d else "", next="0" if d else "1",
                btncls="" if d else "primary", btn="Undo" if d else "Mark done",
            )
        )
    pct = round(100 * req_done / content.LAB_REQUIRED_STEPS)
    body = """<h1>Hands-on lab: build, test, improve, verify</h1>
<p>Do these steps in <strong>Microsoft 365 Copilot</strong> while this page is open, and tick each one when its
"Done when" check is true. Main lab: build the <em>Email Clarity Coach</em> (copy its instructions from
<a href="/templates">Templates</a>). Steps 1 to {req} are required; 11 and 12 are recommended.</p>
{bar}
<ol class="lab">{rows}</ol>
<div class="callout note">Never share real confidential content as evidence. A safe screenshot of your agent's name and
configuration, your charter, three prompts and your test card are enough for your facilitator.</div>""".format(
        req=content.LAB_REQUIRED_STEPS, bar=progress_bar(pct, "{} of {} required steps done".format(req_done, content.LAB_REQUIRED_STEPS)),
        rows="".join(rows),
    )
    return layout(req, "Lab", body, "lab")


def page_charter(req):
    uid = req.user["id"]
    if req.method == "POST":
        svc.save_charter(req.conn, uid, req.form)
        redirect("/charter", msg="Charter saved.")
    data, updated = svc.get_charter(req.conn, uid)
    fields = []
    for key, label, hint in svc.CHARTER_FIELDS:
        multiline = key in ("in_scope", "out_scope", "prompts", "purpose")
        if multiline:
            inp = '<textarea name="{k}" rows="3" placeholder="{h}" maxlength="2000">{v}</textarea>'
        else:
            inp = '<input name="{k}" placeholder="{h}" value="{v}" maxlength="2000">'
        fields.append("<label>{} {}</label>".format(esc(label), inp.format(k=key, h=esc(hint), v=esc(data.get(key, "")))))
    preview = ""
    if data:
        preview = """<div class="card"><h2>Your charter as text</h2>{charter}
<h2>Draft instructions from your charter</h2><p class="muted">Paste into the Instructions box in Agent Builder, then review and test.</p>{instr}
<p><a class="btn" href="/charter.txt">Download as .txt</a></p></div>""".format(
            charter=content._copy_block(svc.charter_text(data)),
            instr=content._copy_block(svc.charter_instructions(data)),
        )
    body = """<h1>My agent charter</h1>
<p>Plan your agent before you build it. Keep it to <strong>one purpose</strong>. Do not include confidential data.</p>
{updated}
<form method="post" class="form wide card">{csrf}{fields}
<button class="btn primary" type="submit">Save charter</button></form>
{preview}""".format(
        updated='<p class="muted">Last saved {} UTC</p>'.format(esc(updated)) if updated else "",
        csrf=csrf_field(req), fields="".join(fields), preview=preview,
    )
    return layout(req, "My agent charter", body, "charter")


def page_charter_txt(req):
    data, _ = svc.get_charter(req.conn, req.user["id"])
    text = svc.charter_text(data) + "\n\n--- DRAFT INSTRUCTIONS ---\n" + svc.charter_instructions(data) + "\n"
    return ("text/plain; charset=utf-8", text.encode(), {"Content-Disposition": 'attachment; filename="agent_charter.txt"'})


def page_templates(req):
    cards = "".join(
        '<section class="card" id="{slug}"><h2>{title}</h2><p class="muted">{use}</p>{block}</section>'.format(
            slug=t["slug"], title=esc(t["title"]), use=esc(t["use"]), block=content._copy_block(t["body"])
        )
        for t in content.TEMPLATES
    )
    body = "<h1>Ready-to-use templates</h1><p>Press <strong>Copy</strong>, paste into Agent Builder or a document, and replace every [bracket].</p>" + cards
    return layout(req, "Templates", body, "templates")


def page_certificate(req):
    prog = svc.user_progress(req.conn, req.user["id"])
    if not prog["certified"]:
        redirect("/dashboard", error="Your certificate unlocks after you finish all lessons, the required lab steps and the final assessment.")
    final = prog["final"]
    body = """<div class="certificate">
<div class="cert-org">{org}</div>
<div class="cert-title">Certificate of Completion</div>
<p>This certifies that</p>
<div class="cert-name">{name}</div>
<p class="muted">Associate ID {aid}</p>
<p>has completed</p>
<div class="cert-course">Simple Copilot Agent Builder (T1): One Agent, One Purpose</div>
<p>including the hands-on lab and the final assessment (score {score}/{total}).</p>
<p class="muted">Completed {date} UTC &middot; content edition {edition}</p>
</div>
<p class="noprint"><button class="btn primary" type="button" onclick="window.print()">Print or save as PDF</button></p>""".format(
        org=esc(get_setting(req.conn, "org_name")), name=esc(req.user["name"]), aid=esc(req.user["associate_id"]),
        score=final["score"], total=final["total"], date=esc(final["completed_at"][:10]), edition=content.EDITION_DATE,
    )
    return layout(req, "Certificate", body)


def page_feedback(req):
    if req.method == "POST":
        rating = req.get("rating")
        if rating not in ("1", "2", "3", "4", "5"):
            redirect("/feedback", error="Please choose a rating from 1 to 5.")
        svc.add_feedback(req.conn, req.user["id"], int(rating), req.get("comment"))
        redirect("/dashboard", msg="Thank you for your feedback!")
    stars = "".join(
        '<label class="option inline-opt"><input type="radio" name="rating" value="{0}" required> {0}</label>'.format(i)
        for i in range(1, 6)
    )
    body = """<section class="card narrow"><h1>Course feedback</h1>
<form method="post" class="form">{csrf}
<fieldset><legend>How useful was this course? (1 = not useful, 5 = very useful)</legend>{stars}</fieldset>
<label>What should we improve? (optional) <textarea name="comment" rows="4" maxlength="2000"></textarea></label>
<button class="btn primary" type="submit">Send feedback</button></form></section>""".format(csrf=csrf_field(req), stars=stars)
    return layout(req, "Feedback", body)


# ---------------------------------------------------------------------------
# Admin pages
# ---------------------------------------------------------------------------

def _require_admin(req):
    if req.user["role"] != "admin":
        raise HttpError(403, "Administrators only.")


def admin_nav(active):
    links = [
        ("overview", "/admin", "Overview"), ("learners", "/admin/learners", "Learners"),
        ("import", "/admin/import", "Import associates"), ("questions", "/admin/questions", "Question bank"),
        ("feedback", "/admin/feedback", "Feedback"), ("settings", "/admin/settings", "Settings"),
    ]
    return '<nav class="subnav" aria-label="Admin">{}</nav>'.format(
        "".join('<a href="{}" class="{}">{}</a>'.format(u, "active" if k == active else "", l) for k, u, l in links)
    )


def _pct(n, d):
    return round(100 * n / d) if d else 0


def page_admin(req):
    _require_admin(req)
    s = svc.overview_stats(req.conn)
    total = s["total"]
    c = s["counts"]
    dept_rows = "".join(
        """<tr><td>{d}</td><td>{t}</td><td>{a}</td><td>{cert}</td><td>{bar}</td>
<td><a href="/admin/learners?department={q}">View</a> &middot; <a href="/admin/export.csv?department={q}">CSV</a></td></tr>""".format(
            d=esc(name), t=v["total"], a=v["active"], cert=v["Certified"],
            bar=progress_bar(_pct(v["Certified"], v["total"]), "{}% certified".format(_pct(v["Certified"], v["total"]))),
            q=quote(name if name != "(none)" else ""),
        )
        for name, v in s["departments"]
    )
    funnel = svc.module_funnel(req.conn)
    funnel_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(esc(f["title"]), f["completed"], f["passed"]) for f in funnel
    )
    body = """{nav}<h1>Training overview</h1>
<section class="grid-4">
<div class="stat"><div class="num">{total}</div><div>Associates loaded</div></div>
<div class="stat"><div class="num">{cert}</div><div>Certified ({certp}%)</div></div>
<div class="stat"><div class="num">{prog}</div><div>In progress</div></div>
<div class="stat"><div class="num">{notstarted}</div><div>Not started / registered only</div></div>
</section>
<section class="grid-4">
<div class="stat"><div class="num">{active}</div><div>Signed in during the last 7 days</div></div>
<div class="stat"><div class="num">{favg}</div><div>Average final score ({fatt} attempts)</div></div>
<div class="stat"><div class="num">{fb}</div><div>Average feedback ({fbc} responses)</div></div>
<div class="stat"><div class="num"><a href="/admin/export.csv">CSV</a></div><div>Download full progress report</div></div>
</section>
<section class="card"><h2>Overall certification</h2>{bar}</section>
<section class="card"><h2>By department</h2>
<table class="grid"><tr><th>Department</th><th>Associates</th><th>Active</th><th>Certified</th><th>Certification rate</th><th></th></tr>{dept_rows}</table></section>
<section class="card"><h2>Module funnel</h2><p class="muted">How many learners finished each module's lessons and passed its quiz. A sharp drop shows where people get stuck.</p>
<table class="grid"><tr><th>Module</th><th>Lessons completed</th><th>Quiz passed</th></tr>{funnel_rows}</table></section>""".format(
        nav=admin_nav("overview"), total=total, cert=c["Certified"], certp=_pct(c["Certified"], total),
        prog=c["In progress"], notstarted=c["Not started"] + c["Registered"], active=s["active_week"],
        favg="{}%".format(s["final_avg"]) if s["final_avg"] is not None else "-", fatt=s["final_attempts"],
        fb="{}/5".format(s["feedback_avg"]) if s["feedback_avg"] is not None else "-", fbc=s["feedback_count"],
        bar=progress_bar(_pct(c["Certified"], total), "{} of {} associates certified".format(c["Certified"], total)),
        dept_rows=dept_rows or '<tr><td colspan="6">No associates yet. <a href="/admin/import">Import a CSV</a>.</td></tr>',
        funnel_rows=funnel_rows,
    )
    return layout(req, "Admin", body, "admin")


def page_admin_learners(req):
    _require_admin(req)
    search = req.query.get("q", "")
    dept = req.query.get("department", "")
    status = req.query.get("status", "")
    page = max(1, int(req.query.get("page", "1")) if req.query.get("page", "1").isdigit() else 1)
    rows, total = svc.learner_rows(req.conn, search, dept, status, PAGE_SIZE, (page - 1) * PAGE_SIZE)
    dept_opts = "".join(
        '<option value="{0}" {1}>{0}</option>'.format(esc(d), "selected" if d == dept else "") for d in svc.departments(req.conn)
    )
    status_opts = "".join(
        '<option {1}>{0}</option>'.format(s, "selected" if s == status else "")
        for s in ("Certified", "In progress", "Registered", "Not started")
    )
    trs = "".join(
        """<tr><td><a href="/admin/learner/{id}">{aid}</a></td><td>{name}</td><td>{dept}</td><td>{status}</td>
<td>{ld}/{tl}</td><td>{qp}</td><td>{lab}/{labreq}</td><td>{final}</td><td>{last}</td></tr>""".format(
            id=r["id"], aid=esc(r["associate_id"]), name=esc(r["name"]), dept=esc(r["department"]),
            status=esc(r["status"]), ld=r["lessons_done"], tl=r["total_lessons"], qp=r["quizzes_passed"],
            lab=r["lab_done"], labreq=content.LAB_REQUIRED_STEPS,
            final="{}%".format(int(r["final_best_pct"])) if r["final_best_pct"] is not None else "-",
            last=esc((r["last_login"] or "-")[:16]),
        )
        for r in rows
    )
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    base = {"q": search, "department": dept, "status": status}
    pager = ""
    if pages > 1:
        prev_l = '<a href="?{}">&larr; Previous</a>'.format(urlencode(dict(base, page=page - 1))) if page > 1 else ""
        next_l = '<a href="?{}">Next &rarr;</a>'.format(urlencode(dict(base, page=page + 1))) if page < pages else ""
        pager = '<div class="pager">{} Page {} of {} {}</div>'.format(prev_l, page, pages, next_l)
    body = """{nav}<h1>Learners</h1>
<form method="get" class="filters">
<label>Search <input name="q" value="{q}" placeholder="ID, name or email"></label>
<label>Department <select name="department"><option value="">All</option>{dept_opts}</select></label>
<label>Status <select name="status"><option value="">All</option>{status_opts}</select></label>
<button class="btn" type="submit">Filter</button>
<a class="btn" href="/admin/export.csv?{exp}">Export these to CSV</a>
</form>
<p class="muted">{total} learners match.</p>
<div class="table-wrap"><table class="grid"><tr><th>Associate ID</th><th>Name</th><th>Department</th><th>Status</th><th>Lessons</th>
<th>Quizzes passed</th><th>Lab</th><th>Best final</th><th>Last sign-in (UTC)</th></tr>{trs}</table></div>{pager}""".format(
        nav=admin_nav("learners"), q=esc(search), dept_opts=dept_opts, status_opts=status_opts,
        exp=urlencode({"department": dept}), total=total, trs=trs or '<tr><td colspan="9">No learners found.</td></tr>',
        pager=pager,
    )
    return layout(req, "Learners", body, "admin")


def page_admin_learner(req, user_id):
    _require_admin(req)
    u = req.conn.execute("SELECT * FROM users WHERE id = ?", (int(user_id),)).fetchone()
    if not u:
        raise HttpError(404, "Learner not found.")
    if req.method == "POST":
        action = req.get("action")
        if action == "reset-password":
            svc.reset_password(req.conn, u["id"])
            redirect("/admin/learner/{}".format(u["id"]), msg="Password cleared. The associate can register again with the same ID; progress is kept.")
        if action == "update":
            req.conn.execute(
                "UPDATE users SET name = ?, email = ?, department = ?, location = ? WHERE id = ?",
                (req.get("name").strip() or u["name"], req.get("email").strip(), req.get("department").strip(),
                 req.get("location").strip(), u["id"]),
            )
            req.conn.commit()
            redirect("/admin/learner/{}".format(u["id"]), msg="Details updated.")
    prog = svc.user_progress(req.conn, u["id"])
    attempts = req.conn.execute(
        """SELECT a.*, m.title AS module_title FROM quiz_attempts a LEFT JOIN modules m ON m.id = a.module_id
           WHERE a.user_id = ? ORDER BY a.completed_at DESC LIMIT 50""",
        (u["id"],),
    ).fetchall()
    att_rows = "".join(
        '<tr><td>{}</td><td>{}</td><td>{}/{}</td><td>{}</td><td><a href="/attempt/{}">Review</a></td></tr>'.format(
            esc(a["completed_at"]), esc(a["module_title"] or "Final assessment"), a["score"], a["total"],
            "Passed" if a["passed"] else "Not passed", a["id"],
        )
        for a in attempts
    )
    lab = svc.lab_done_steps(req.conn, u["id"])
    lab_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            no, esc(instr), check(no in lab), esc(lab[no]["note"]) if no in lab else ""
        )
        for no, instr, _ in content.LAB_STEPS
    )
    charter, _ = svc.get_charter(req.conn, u["id"])
    body = """{nav}<p class="crumbs"><a href="/admin/learners">Learners</a> &rsaquo; {name}</p>
<h1>{name}</h1>
<section class="grid-2">
<div class="card"><h2>Details</h2>
<form method="post" class="form">{csrf}<input type="hidden" name="action" value="update">
<p>Associate ID: <strong>{aid}</strong> &middot; Registered: {reg} &middot; Last sign-in: {last}</p>
<label>Name <input name="name" value="{name}"></label>
<label>Email <input name="email" value="{email}"></label>
<label>Department <input name="department" value="{dept}"></label>
<label>Location <input name="location" value="{loc}"></label>
<button class="btn" type="submit">Save details</button></form>
<form method="post" class="inline" onsubmit="return confirm('Clear this password? Progress is kept.')">{csrf}
<input type="hidden" name="action" value="reset-password"><button class="btn danger" type="submit">Reset password</button></form>
</div>
<div class="card"><h2>Progress</h2>{bar}
<ul class="checklist"><li>{c1} Lessons {dl}/{tl}</li><li>{c2} Required lab steps {lr}/{labreq}</li>
<li>{c3} Final assessment</li><li>Module quizzes passed: {pm}/{qm}</li></ul>
<p>{cert}</p></div>
</section>
<section class="card"><h2>Quiz attempts</h2><table class="grid"><tr><th>Date (UTC)</th><th>Quiz</th><th>Score</th><th>Result</th><th></th></tr>{att}</table></section>
<section class="card"><h2>Lab steps</h2><table class="grid"><tr><th>#</th><th>Step</th><th>Status</th><th>Learner note</th></tr>{lab}</table></section>
<section class="card"><h2>Agent charter</h2>{charter}</section>""".format(
        nav=admin_nav("learners"), name=esc(u["name"]), csrf=csrf_field(req), aid=esc(u["associate_id"]),
        reg="Yes" if u["password_hash"] else "No", last=esc(u["last_login"] or "never"), email=esc(u["email"]),
        dept=esc(u["department"]), loc=esc(u["location"]), bar=progress_bar(prog["percent"]),
        c1=check(prog["lessons_ok"]), c2=check(prog["lab_ok"]), c3=check(prog["final_ok"]),
        dl=prog["done_lessons"], tl=prog["total_lessons"], lr=prog["lab_required_done"], labreq=content.LAB_REQUIRED_STEPS,
        pm=prog["passed_modules"], qm=prog["quiz_modules"],
        cert="<strong>Certified</strong>" if prog["certified"] else "Not certified yet",
        att=att_rows or '<tr><td colspan="5">No attempts yet.</td></tr>', lab=lab_rows,
        charter="<pre class='plain'>{}</pre>".format(esc(svc.charter_text(charter))) if charter else "<p class='muted'>Not started.</p>",
    )
    return layout(req, u["name"], body, "admin")


def page_admin_export(req):
    _require_admin(req)
    data = svc.export_progress_csv(req.conn, req.query.get("department", ""))
    return ("text/csv; charset=utf-8", ("﻿" + data).encode("utf-8"),
            {"Content-Disposition": 'attachment; filename="training_progress.csv"'})


def page_admin_import(req):
    _require_admin(req)
    result = ""
    if req.method == "POST":
        raw = req.files.get("file") or req.get("csv_text").encode("utf-8")
        if not raw.strip():
            redirect("/admin/import", error="Choose a CSV file or paste CSV text.")
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        created, updated, errors = svc.import_users_csv(req.conn, text)
        err_html = ""
        if errors:
            shown = errors[:20]
            err_html = "<ul class='errors'>{}</ul>".format("".join("<li>{}</li>".format(esc(e)) for e in shown))
            if len(errors) > 20:
                err_html += "<p>...and {} more.</p>".format(len(errors) - 20)
        result = '<div class="flash {}" role="status">Import finished: {} added, {} updated, {} skipped.</div>{}'.format(
            "err" if errors else "ok", created, updated, len(errors), err_html
        )
    body = """{nav}<h1>Import associates</h1>
{result}
<div class="card">
<p>Upload a CSV with a header row. Required columns: <code>associate_id</code>, <code>name</code>.
Optional: <code>email</code>, <code>department</code>, <code>location</code>. Existing IDs are updated; progress and passwords are kept.
Imported associates then create their password on the <em>Register</em> page using their associate ID.</p>
<p><a href="/static/associates_template.csv" download>Download a CSV template</a></p>
<form method="post" enctype="multipart/form-data" class="form">{csrf}
<label>CSV file <input type="file" name="file" accept=".csv,text/csv"></label>
<label>...or paste CSV text <textarea name="csv_text" rows="6" placeholder="associate_id,name,email,department,location"></textarea></label>
<button class="btn primary" type="submit">Import</button></form>
</div>""".format(nav=admin_nav("import"), result=result, csrf=csrf_field(req))
    return layout(req, "Import associates", body, "admin")


def page_admin_questions(req):
    _require_admin(req)
    mods = svc.list_modules(req.conn)
    if req.method == "POST":
        if req.get("action") == "toggle":
            svc.set_question_active(req.conn, int(req.get("id")), req.get("active") == "1")
            redirect("/admin/questions", msg="Question updated.")
        try:
            options = [req.get("opt{}".format(i)) for i in range(4)]
            correct = int(req.get("correct", "-1"))
            module_id = int(req.get("module_id"))
            code = svc.add_custom_question(
                req.conn, module_id, req.get("prompt"), options, correct, req.get("rationale"), req.get("category")
            )
            redirect("/admin/questions", msg="Question {} added.".format(code))
        except ValueError as e:
            redirect("/admin/questions", error=str(e))
    stats = svc.question_stats(req.conn)
    trs = "".join(
        """<tr class="{cls}"><td>{code}</td><td>{prompt}</td><td>{cat}</td><td>{ans}</td><td>{rate}</td>
<td><form method="post" class="inline">{csrf}<input type="hidden" name="action" value="toggle"><input type="hidden" name="id" value="{id}">
<input type="hidden" name="active" value="{next}"><button class="btn small" type="submit">{btn}</button></form></td></tr>""".format(
            cls="" if q["active"] else "inactive", code=esc(q["code"]), prompt=esc(q["prompt"]), cat=esc(q["category"]),
            ans=q["answered"], rate="{}%".format(_pct(q["correct"] or 0, q["answered"])) if q["answered"] else "-",
            csrf=csrf_field(req), id=q["id"], next="0" if q["active"] else "1", btn="Disable" if q["active"] else "Enable",
        )
        for q in stats
    )
    mod_opts = "".join('<option value="{}">{}</option>'.format(m["id"], esc(m["title"])) for m in mods)
    body = """{nav}<h1>Question bank</h1>
<p>Questions are listed hardest first, by the share of learners who answered correctly. Low rates can mean the topic needs
clearer teaching, or the question needs rewording. Disabled questions are not used in quizzes.
Built-in questions come from <code>training/content.py</code>; running <code>python app.py reseed</code> re-enables them.</p>
<div class="table-wrap"><table class="grid"><tr><th>ID</th><th>Question</th><th>Category</th><th>Answered</th><th>Correct</th><th></th></tr>{trs}</table></div>
<section class="card"><h2>Add an organization-specific question</h2>
<form method="post" class="form wide">{csrf}<input type="hidden" name="action" value="add">
<label>Module <select name="module_id">{mod_opts}</select></label>
<label>Category <input name="category" value="Organization policy" maxlength="50"></label>
<label>Question <textarea name="prompt" rows="2" required maxlength="1000"></textarea></label>
<label>Option A <input name="opt0" required maxlength="300"></label>
<label>Option B <input name="opt1" required maxlength="300"></label>
<label>Option C (optional) <input name="opt2" maxlength="300"></label>
<label>Option D (optional) <input name="opt3" maxlength="300"></label>
<label>Correct option <select name="correct"><option value="0">A</option><option value="1">B</option><option value="2">C</option><option value="3">D</option></select></label>
<label>Explanation shown after answering <textarea name="rationale" rows="2" required maxlength="1000"></textarea></label>
<button class="btn primary" type="submit">Add question</button></form></section>""".format(
        nav=admin_nav("questions"), trs=trs, csrf=csrf_field(req), mod_opts=mod_opts
    )
    return layout(req, "Question bank", body, "admin")


def page_admin_feedback(req):
    _require_admin(req)
    rows = req.conn.execute(
        """SELECT f.*, u.name, u.department FROM feedback f JOIN users u ON u.id = f.user_id
           ORDER BY f.created_at DESC LIMIT 500"""
    ).fetchall()
    dist = {r[0]: r[1] for r in req.conn.execute("SELECT rating, COUNT(*) FROM feedback GROUP BY rating")}
    total = sum(dist.values())
    dist_html = "".join(
        "<tr><td>{} / 5</td><td>{}</td><td>{}</td></tr>".format(
            i, dist.get(i, 0), progress_bar(_pct(dist.get(i, 0), total), "{}%".format(_pct(dist.get(i, 0), total)))
        )
        for i in range(5, 0, -1)
    )
    trs = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            esc(r["created_at"][:16]), esc(r["name"]), esc(r["department"]), r["rating"], esc(r["comment"])
        )
        for r in rows
    )
    body = """{nav}<h1>Learner feedback</h1>
<section class="card"><h2>Ratings ({total})</h2><table class="grid">{dist}</table></section>
<section class="card"><h2>Latest comments</h2><div class="table-wrap"><table class="grid"><tr><th>Date</th><th>Name</th><th>Department</th><th>Rating</th><th>Comment</th></tr>{trs}</table></div></section>""".format(
        nav=admin_nav("feedback"), total=total, dist=dist_html, trs=trs or '<tr><td colspan="5">No feedback yet.</td></tr>'
    )
    return layout(req, "Feedback", body, "admin")


def page_admin_settings(req):
    _require_admin(req)
    if req.method == "POST":
        pm = req.get("pass_mark")
        if not pm.isdigit() or not 1 <= int(pm) <= 100:
            redirect("/admin/settings", error="Pass mark must be a number from 1 to 100.")
        set_setting(req.conn, "pass_mark", pm)
        if req.get("org_name").strip():
            set_setting(req.conn, "org_name", req.get("org_name").strip()[:100])
        req.conn.commit()
        redirect("/admin/settings", msg="Settings saved.")
    admins = req.conn.execute("SELECT associate_id, name FROM users WHERE role = 'admin' ORDER BY name").fetchall()
    body = """{nav}<h1>Settings</h1>
<section class="card narrow"><form method="post" class="form">{csrf}
<label>Organization name (shown in the header and on certificates) <input name="org_name" value="{org}" maxlength="100"></label>
<label>Pass mark for quizzes and the final assessment (%) <input name="pass_mark" type="number" min="1" max="100" value="{pm}"></label>
<button class="btn primary" type="submit">Save settings</button></form></section>
<section class="card narrow"><h2>Administrators</h2><ul>{admins}</ul>
<p class="muted">Add more administrators from the command line: <code>python app.py create-admin</code>.</p></section>""".format(
        nav=admin_nav("settings"), csrf=csrf_field(req), org=esc(get_setting(req.conn, "org_name")),
        pm=esc(get_setting(req.conn, "pass_mark")),
        admins="".join("<li>{} ({})</li>".format(esc(a["name"]), esc(a["associate_id"])) for a in admins),
    )
    return layout(req, "Settings", body, "admin")


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

PUBLIC = "public"
LOGIN = "login"

ROUTES = [
    (r"/setup", page_setup, PUBLIC),
    (r"/login", page_login, PUBLIC),
    (r"/register", page_register, PUBLIC),
    (r"/logout", page_logout, LOGIN),
    (r"/", page_home, LOGIN),
    (r"/account", page_account, LOGIN),
    (r"/dashboard", page_dashboard, LOGIN),
    (r"/module/([\w-]+)", page_module, LOGIN),
    (r"/module/([\w-]+)/lesson/([\w-]+)", page_lesson, LOGIN),
    (r"/module/([\w-]+)/quiz", page_module_quiz, LOGIN),
    (r"/final", page_final, LOGIN),
    (r"/attempt/(\d+)", page_attempt, LOGIN),
    (r"/lab", page_lab, LOGIN),
    (r"/charter", page_charter, LOGIN),
    (r"/charter\.txt", page_charter_txt, LOGIN),
    (r"/templates", page_templates, LOGIN),
    (r"/certificate", page_certificate, LOGIN),
    (r"/feedback", page_feedback, LOGIN),
    (r"/admin", page_admin, LOGIN),
    (r"/admin/learners", page_admin_learners, LOGIN),
    (r"/admin/learner/(\d+)", page_admin_learner, LOGIN),
    (r"/admin/export\.csv", page_admin_export, LOGIN),
    (r"/admin/import", page_admin_import, LOGIN),
    (r"/admin/questions", page_admin_questions, LOGIN),
    (r"/admin/feedback", page_admin_feedback, LOGIN),
    (r"/admin/settings", page_admin_settings, LOGIN),
]
COMPILED = [(re.compile("^" + pattern + "$"), fn, access) for pattern, fn, access in ROUTES]


class Handler(BaseHTTPRequestHandler):
    server_version = "T1Training/1.0"
    db_path = None
    quiet = False

    def log_message(self, fmt, *args):
        if not self.quiet:
            super().log_message(fmt, *args)

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def send(self, status, ctype, body, headers=None, cookie=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        if ctype.startswith("text/html"):
            self.send_header("Cache-Control", "no-store")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        if cookie is not None:
            if cookie:
                self.send_header("Set-Cookie", "{}={}; Path=/; HttpOnly; SameSite=Lax; Max-Age={}".format(
                    COOKIE, cookie, svc.SESSION_HOURS * 3600))
            else:
                self.send_header("Set-Cookie", "{}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0".format(COOKIE))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def serve_static(self, name):
        path = os.path.normpath(os.path.join(STATIC_DIR, name))
        if not path.startswith(STATIC_DIR + os.sep) or not os.path.isfile(path):
            return self.send(404, "text/plain; charset=utf-8", b"Not found")
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript",):
            ctype += "; charset=utf-8"
        with open(path, "rb") as f:
            data = f.read()
        self.send(200, ctype, data, {"Cache-Control": "max-age=300"})

    def dispatch(self, method):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/static/"):
            return self.serve_static(parsed.path[len("/static/"):])
        req = Request(self, method)
        req.conn = connect(self.db_path)
        try:
            req.user, req.csrf = svc.session_user(req.conn, req.token)
            if not svc.admin_exists(req.conn) and req.path != "/setup":
                raise Redirect("/setup")
            for pattern, fn, access in COMPILED:
                m = pattern.match(req.path)
                if not m:
                    continue
                if access == LOGIN and not req.user:
                    raise Redirect("/login")
                if method == "POST":
                    req.read_body()
                    if req.user and not hmac.compare_digest(req.get("csrf"), req.csrf or ""):
                        raise HttpError(400, "Your form expired. Go back, refresh the page and try again.")
                result = fn(req, *m.groups())
                if isinstance(result, tuple):
                    ctype, body, headers = result
                    return self.send(200, ctype, body, headers, req.set_cookie)
                return self.send(200, "text/html; charset=utf-8", result.encode("utf-8"), cookie=req.set_cookie)
            raise HttpError(404, "Page not found.")
        except Redirect as r:
            self.send(303, "text/plain; charset=utf-8", b"", {"Location": r.location}, req.set_cookie)
        except HttpError as e:
            body = layout(req, "Error", '<section class="card narrow"><h1>{}</h1><p>{}</p><p><a href="/">Go to home</a></p></section>'.format(
                e.status, esc(e.message)))
            self.send(e.status, "text/html; charset=utf-8", body.encode("utf-8"))
        except Exception:
            traceback.print_exc()
            self.send(500, "text/plain; charset=utf-8", b"Something went wrong. Check the server window for details.")
        finally:
            req.conn.close()


def make_server(host, port, db_path=None, quiet=False):
    handler = type("BoundHandler", (Handler,), {"db_path": db_path, "quiet": quiet})
    return ThreadingHTTPServer((host, port), handler)

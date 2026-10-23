"""Sign-in, course, lab, toolkit and learning-path pages."""

import hmac
from urllib.parse import urlparse

from . import blocks, content, hub, i18n, services as svc
from .core import (Raw, HttpError, check, csrf_field, esc, flash_html, layout, options, progress_bar, redirect,
                   sign, LANG_COOKIE)
from .db import get_setting, set_setting


# ---------------------------------------------------------------------------
# Language
# ---------------------------------------------------------------------------

def page_lang(req):
    code = req.query.get("code", "")
    nxt = req.query.get("next", "/")
    parsed = urlparse(nxt)
    if parsed.scheme or parsed.netloc or not nxt.startswith("/"):
        nxt = "/"
    if code in i18n.CODES:
        req.cookies_out.append("{}={}; Path=/; SameSite=Lax; Max-Age=31536000".format(LANG_COOKIE, code))
        if req.user:
            req.conn.execute("UPDATE users SET lang = ? WHERE id = ?", (code, req.user["id"]))
            req.conn.commit()
    redirect(nxt)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def page_setup(req):
    T = req.t
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
            error = T(str(e))
        except Exception as e:  # duplicate ID and similar
            if hasattr(e, "location"):
                raise
            error = T("Could not create the account: {error}", error=e)
    body = """
<section class="card narrow">
<h1>{h1}</h1>
<p>{intro}</p>
{err}
<form method="post" class="form">
<label>{l_org} <input name="org_name" value="{org}" maxlength="100"></label>
<label>{l_id} <input name="associate_id" required maxlength="50" value="admin"></label>
<label>{l_name} <input name="name" required maxlength="100" value="{name}"></label>
<label>{l_pw} <input type="password" name="password" required minlength="8"></label>
<label>{l_pw2} <input type="password" name="password2" required minlength="8"></label>
<button type="submit" class="btn primary">{btn}</button>
</form>
</section>""".format(
        h1=T("Welcome! Set up the Copilot Agent Hub"),
        intro=T("Create the first administrator account. Administrators run the CoE: they import associates, approve agents and licences, and see all reports."),
        err=flash_html(error), l_org=T("Organization name"), org=esc(req.get("org_name", "")),
        l_id=T("Administrator ID"), l_name=T("Display name"), name=esc(req.get("name", "Training Administrator")),
        l_pw=T("Password (8+ characters)"), l_pw2=T("Confirm password"), btn=T("Create administrator"),
    )
    return layout(req, T("Set up"), body)


def page_login(req):
    T = req.t
    if req.user:
        redirect("/")
    error = ""
    if req.method == "POST":
        user = svc.authenticate(req.conn, req.get("associate_id"), req.get("password"))
        if user:
            req.token = svc.create_session(req.conn, user["id"])
            req.set_cookie = req.token
            if not user["lang"]:
                req.conn.execute("UPDATE users SET lang = ? WHERE id = ?", (req.lang, user["id"]))
                req.conn.commit()
            redirect("/")
        error = T("Associate ID or password is not correct.")
    body = """
<section class="card narrow">
<h1>{h1}</h1>
<p>{intro}</p>
{err}
<form method="post" class="form">
<label>{l_id} <input name="associate_id" required autofocus maxlength="50" value="{aid}" autocomplete="username"></label>
<label>{l_pw} <input type="password" name="password" required autocomplete="current-password"></label>
<button type="submit" class="btn primary">{btn}</button>
</form>
<p class="muted">{first} <a href="/register">{create}</a>.</p>
</section>""".format(
        h1=T("Sign in"),
        intro=T("Your front door for Microsoft 365 Copilot agents: learn, build, get approval, share ideas and track the value."),
        err=flash_html(error), l_id=T("Associate ID"), aid=esc(req.get("associate_id")), l_pw=T("Password"),
        btn=T("Sign in"), first=T("First time here?"), create=T("Create your account"),
    )
    return layout(req, T("Sign in"), body)


def page_register(req):
    T = req.t
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
            req.conn.execute("UPDATE users SET lang = ? WHERE id = ?", (req.lang, user["id"]))
            req.conn.commit()
            req.token = svc.create_session(req.conn, user["id"])
            req.set_cookie = req.token
            redirect("/dashboard", msg="Welcome! Your account is ready.")
        except ValueError as e:
            error = T(str(e))
    datalist = "".join('<option value="{}">'.format(esc(d)) for d in svc.departments(req.conn))
    body = """
<section class="card narrow">
<h1>{h1}</h1>
<p>{intro}</p>
{err}
<form method="post" class="form">
<label>{l_id} <input name="associate_id" required maxlength="50" value="{aid}" autocomplete="username"></label>
<label>{l_name} <input name="name" required maxlength="100" value="{name}"></label>
<label>{l_email} <input type="email" name="email" maxlength="150" value="{email}"></label>
<label>{l_dept} <input name="department" maxlength="100" list="depts" value="{dept}"></label>
<datalist id="depts">{datalist}</datalist>
<label>{l_pw} <input type="password" name="password" required minlength="8" autocomplete="new-password"></label>
<label>{l_pw2} <input type="password" name="password2" required minlength="8" autocomplete="new-password"></label>
<button type="submit" class="btn primary">{btn}</button>
</form>
<p class="muted">{already} <a href="/login">{signin}</a>.</p>
</section>""".format(
        h1=T("Create your account"),
        intro=T("Use your company associate ID. If your administrator already loaded your details, they will be kept."),
        err=flash_html(error), l_id=T("Associate ID"), aid=esc(req.get("associate_id")), l_name=T("Full name"),
        name=esc(req.get("name")), l_email=T("Work email (optional)"), email=esc(req.get("email")),
        l_dept=T("Department"), dept=esc(req.get("department")), datalist=datalist,
        l_pw=T("Password (8+ characters)"), l_pw2=T("Confirm password"), btn=T("Create account"),
        already=T("Already registered?"), signin=T("Sign in"),
    )
    return layout(req, T("Create your account"), body)


def page_logout(req):
    if req.token:
        svc.end_session(req.conn, req.token)
    req.set_cookie = ""
    redirect("/login", msg="You have signed out.")


def page_account(req):
    T = req.t
    u = req.user
    if req.method == "POST":
        if req.get("action") == "profile":
            req.conn.execute("UPDATE users SET office_hours = ? WHERE id = ?", (req.get("office_hours").strip()[:300], u["id"]))
            req.conn.commit()
            redirect("/account", msg="Saved.")
        if not svc.verify_password(req.get("current"), u["password_hash"]):
            redirect("/account", error="Your current password is not correct.")
        if req.get("password") != req.get("password2"):
            redirect("/account", error="The new passwords do not match.")
        try:
            svc.set_password(req.conn, u["id"], req.get("password"))
        except ValueError as e:
            redirect("/account", error=str(e))
        req.set_cookie = ""
        redirect("/login", msg="Password changed. Please sign in again.")
    coach = ""
    if u["is_reviewer"]:
        coach = """<h2>{h}</h2><form method="post" class="form">{csrf}<input type="hidden" name="action" value="profile">
<label>{l} <input name="office_hours" value="{v}" maxlength="300" placeholder="{ph}"></label>
<button class="btn" type="submit">{btn}</button></form>""".format(
            h=T("Coach profile"), csrf=csrf_field(req), l=T("Office hours shown in the coach directory"),
            v=esc(u["office_hours"]), ph=T("e.g. Tuesdays 14:00-15:00, Teams"), btn=T("Save"),
        )
    body = """
<section class="card narrow">
<h1>{h1}</h1>
<dl class="facts"><dt>{l_id}</dt><dd>{aid}</dd><dt>{l_name}</dt><dd>{name}</dd>
<dt>{l_dept}</dt><dd>{dept}</dd><dt>{l_email}</dt><dd>{email}</dd><dt>{l_role}</dt><dd>{role}</dd></dl>
{coach}
<h2>{h2}</h2>
<form method="post" class="form">{csrf}
<label>{l_cur} <input type="password" name="current" required></label>
<label>{l_new} <input type="password" name="password" required minlength="8"></label>
<label>{l_new2} <input type="password" name="password2" required minlength="8"></label>
<button class="btn primary" type="submit">{btn}</button>
</form>
</section>""".format(
        h1=T("My account"), l_id=T("Associate ID"), aid=esc(u["associate_id"]), l_name=T("Name"), name=esc(u["name"]),
        l_dept=T("Department"), dept=esc(u["department"] or "-"), l_email=T("Email"), email=esc(u["email"] or "-"),
        l_role=T("Role"), role=", ".join(
            [T("Administrator (CoE)") if u["role"] == "admin" else T("Associate")] + ([T("Copilot coach")] if u["is_reviewer"] else [])
        ),
        coach=coach, h2=T("Change password"), csrf=csrf_field(req), l_cur=T("Current password"),
        l_new=T("New password (8+ characters)"), l_new2=T("Confirm new password"), btn=T("Change password"),
    )
    return layout(req, T("My account"), body)


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------

def mod_title(req, m):
    return i18n.module(req.lang, m["slug"], "title", m["title"])


def mod_summary(req, m):
    return i18n.module(req.lang, m["slug"], "summary", m["summary"])


def les_title(req, m, l):
    return i18n.lesson(req.lang, m["slug"], l["slug"], "title", l["title"])


def next_label(req, step):
    T = req.t
    kind = step["kind"]
    if kind == "lesson":
        return T("Continue: {title}", title=les_title(req, step["module"], step["lesson"]))
    if kind == "quiz":
        return T("Take the quiz for {title}", title=mod_title(req, step["module"]))
    if kind == "lab":
        return T("Work through the hands-on lab")
    if kind == "final":
        return T("Take the final assessment")
    return T("View your certificate")


def page_home(req):
    if req.user["role"] == "admin":
        redirect("/admin")
    redirect("/dashboard")


def _module_rows(req, track):
    T = req.t
    uid = req.user["id"]
    done = svc.completed_lesson_ids(req.conn, uid)
    passed = svc.passed_module_ids(req.conn, uid)
    rows = []
    for m in svc.list_modules(req.conn, track):
        lessons = svc.module_lessons(req.conn, m["id"])
        n_done = sum(1 for l in lessons if l["id"] in done)
        has_quiz = bool(svc.module_questions(req.conn, m["id"]))
        if n_done == len(lessons) and (not has_quiz or m["id"] in passed):
            status = '<span class="badge ok">{}</span>'.format(T("Complete"))
        elif n_done:
            status = '<span class="badge prog">{}</span>'.format(T("In progress"))
        else:
            status = '<span class="badge todo">{}</span>'.format(T("Not started"))
        quiz = ""
        if has_quiz:
            quiz = ('<span class="badge ok">{}</span>'.format(T("Quiz passed")) if m["id"] in passed
                    else '<a href="/module/{}/quiz">{}</a>'.format(m["slug"], T("Quiz")))
        rows.append(
            """<li class="module-row"><div><a class="module-title" href="/module/{slug}">{title}</a>
<div class="muted">{summary}</div></div>
<div class="module-meta">{lessons} &middot; {mins} &middot; {quiz} {status}</div></li>""".format(
                slug=m["slug"], title=esc(mod_title(req, m)), summary=esc(mod_summary(req, m)),
                lessons=T("{done}/{total} lessons", done=n_done, total=len(lessons)),
                mins=T("{n} min", n=m["minutes"]), quiz=quiz, status=status,
            )
        )
    return "".join(rows)


def page_dashboard(req):
    T = req.t
    uid = req.user["id"]
    prog = svc.user_progress(req.conn, uid)
    step = svc.next_step(req.conn, uid)
    final = prog["final"]
    final_txt = T("Not taken yet")
    if final:
        final_txt = T("Best score {score}/{total}", score=final["score"], total=final["total"])
    levels = hub.builder_levels(req.conn, req.user)
    reached = [(k, n) for k, n, _, _ in content.BUILDER_LEVELS if levels[k]]
    level_txt = i18n.label(req.lang, "levels", reached[-1][0], reached[-1][1]) if reached else T("Not started")
    my_agents = hub.list_agents(req.conn, owner_id=uid, limit=5)
    agents_html = "".join(
        '<li><a href="/hub/agents/{}">{}</a> <span class="badge {}">{}</span></li>'.format(
            a["id"], esc(a["name"]), "ok" if a["status"] == "approved" else "prog",
            esc(i18n.label(req.lang, "agent_status", a["status"], dict(content.AGENT_STATUSES)[a["status"]])),
        )
        for a in my_agents
    ) or "<li class='muted'>{}</li>".format(T("No agents registered yet."))
    body = """
<section class="hero">
<h1>{hello}</h1>
<p>{goal}</p>
{bar}
<a class="btn primary" href="{url}">{label}</a>
</section>
<section class="grid-4">
<div class="stat"><div class="num">{dl}/{tl}</div><div>{l_lessons} {lk}</div></div>
<div class="stat"><div class="num">{pm}/{qm}</div><div>{l_quiz}</div></div>
<div class="stat"><div class="num">{lab}/{labreq}</div><div>{l_lab} {labk}</div></div>
<div class="stat"><div class="num">{fk}</div><div>{l_final}: {final}</div></div>
</section>
<section class="grid-2">
<div class="card"><h2>{h_level}</h2><p class="big">{level}</p><p><a href="/paths">{see_paths}</a></p></div>
<div class="card"><h2>{h_agents}</h2><ul>{agents}</ul><p><a class="btn" href="/hub/agents/new">{register}</a></p></div>
</section>
<section>
<h2>{h_modules}</h2>
<ol class="modules">{rows}</ol>
</section>
<section class="card">
<h2>{h_cert}</h2>
<ul class="checklist">
<li>{c1} {r1}</li>
<li>{c2} {r2}</li>
<li>{c3} {r3}</li>
</ul>
<p>{cert}</p>
<p class="muted">{fb}</p>
</section>""".format(
        hello=T("Hello, {name}", name=req.user["name"]),
        goal=T("Your goal: build one agent with one purpose, test it, and use it safely."),
        bar=progress_bar(prog["percent"], T("{n}% complete", n=prog["percent"])), url=step["url"],
        label=esc(next_label(req, step)), dl=prog["done_lessons"], tl=prog["total_lessons"],
        l_lessons=T("Lessons"), lk=check(req, prog["lessons_ok"]), pm=prog["passed_modules"], qm=prog["quiz_modules"],
        l_quiz=T("Module quizzes passed"), lab=prog["lab_required_done"], labreq=content.LAB_REQUIRED_STEPS,
        l_lab=T("Required lab steps"), labk=check(req, prog["lab_ok"]),
        fk=T("Passed") if prog["final_ok"] else "-", l_final=T("Final"), final=esc(final_txt),
        h_level=T("Your builder level"), level=esc(level_txt), see_paths=T("See learning paths and what unlocks next"),
        h_agents=T("My agents"), agents=agents_html, register=T("Register an agent"),
        h_modules=T("Core course: Simple Copilot Agent Builder (T1)"), rows=_module_rows(req, "core"),
        h_cert=T("Requirements for your certificate"),
        c1=check(req, prog["lessons_ok"]), r1=T("Complete every lesson"),
        c2=check(req, prog["lab_ok"]), r2=T("Complete lab steps 1 to {n} in Microsoft 365 Copilot", n=content.LAB_REQUIRED_STEPS),
        c3=check(req, prog["final_ok"]), r3=T("Pass the final assessment ({n}% or higher)", n=get_setting(req.conn, "pass_mark")),
        cert='<a class="btn primary" href="/certificate">{}</a>'.format(T("View your certificate")) if prog["certified"]
        else T("Your certificate unlocks when all three are done."),
        fb=T("Finished? {link}", link=Raw('<a href="/feedback">{}</a>'.format(T("Tell us what you thought of the course")))),
    )
    return layout(req, T("My course"), body, "dashboard")


def _module_or_404(req, slug):
    m = svc.get_module(req.conn, slug)
    if not m:
        raise HttpError(404, "That module does not exist.")
    return m


def page_module(req, slug):
    T = req.t
    m = _module_or_404(req, slug)
    done = svc.completed_lesson_ids(req.conn, req.user["id"])
    lessons = svc.module_lessons(req.conn, m["id"])
    items = "".join(
        '<li><a href="/module/{}/lesson/{}">{}</a> <span class="muted">({})</span> {}</li>'.format(
            m["slug"], l["slug"], esc(les_title(req, m, l)), T("{n} min", n=l["minutes"]), check(req, l["id"] in done)
        )
        for l in lessons
    )
    questions = svc.module_questions(req.conn, m["id"])
    quiz = ""
    if questions:
        passed = m["id"] in svc.passed_module_ids(req.conn, req.user["id"])
        quiz = """<div class="card"><h2>{h}</h2><p>{info}</p>
<p>{status}</p><a class="btn" href="/module/{slug}/quiz">{label}</a></div>""".format(
            h=T("Module quiz"),
            info=T("{n} questions. Pass mark {pm}%. You can retry as often as you like.", n=len(questions), pm=get_setting(req.conn, "pass_mark")),
            slug=m["slug"], status=check(req, passed), label=T("Retake quiz") if passed else T("Start quiz"),
        )
    track_note = ""
    if m["track"] != "core":
        track_note = '<p class="tag">{}</p>'.format(T("Optional track. Not required for the T1 certificate."))
    back = "/paths" if m["track"] != "core" else "/dashboard"
    body = """<p class="crumbs"><a href="{back}">{home}</a> &rsaquo; {title}</p>
<h1>{title}</h1><p class="lead">{summary}</p>{track}
<div class="card"><h2>{h}</h2><ol class="lesson-list">{items}</ol></div>{quiz}""".format(
        back=back, home=T("My course") if m["track"] == "core" else T("Learning paths"), title=esc(mod_title(req, m)),
        summary=esc(mod_summary(req, m)), track=track_note, h=T("Lessons"), items=items, quiz=quiz,
    )
    return layout(req, mod_title(req, m), body, "dashboard")


def page_lesson(req, slug, lslug):
    T = req.t
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
        if m["track"] != "core":
            redirect("/paths", msg="Module complete.")
        redirect(svc.next_step(req.conn, req.user["id"])["url"], msg="Module complete.")
    done = lesson["id"] in svc.completed_lesson_ids(req.conn, req.user["id"])
    prev_link = (
        '<a class="btn" href="/module/{}/lesson/{}">&larr; {}</a>'.format(slug, lessons[idx - 1]["slug"], T("Previous"))
        if idx > 0 else '<a class="btn" href="/module/{}">&larr; {}</a>'.format(slug, T("Module overview"))
    )
    content_html = i18n.lesson(req.lang, m["slug"], lesson["slug"], "body", lesson["body_html"])
    body = """<p class="crumbs"><a href="/dashboard">{home}</a> &rsaquo; <a href="/module/{slug}">{mtitle}</a> &rsaquo; {pos}</p>
<article class="lesson card">
<h1>{title}</h1>
<p class="muted">{mins}</p>
{content}
</article>
<div class="lesson-nav">{prev}
<form method="post" class="inline">{csrf}<button class="btn primary" type="submit">{btn}</button></form></div>""".format(
        home=T("My course"), slug=slug, mtitle=esc(mod_title(req, m)),
        pos=T("Lesson {n} of {total}", n=idx + 1, total=len(lessons)), title=esc(les_title(req, m, lesson)),
        mins=T("About {n} minutes", n=lesson["minutes"]), content=content_html, prev=prev_link, csrf=csrf_field(req),
        btn=(T("Next") if done else T("Mark lesson complete")) + " &rarr;",
    )
    return layout(req, les_title(req, m, lesson), body, "dashboard")


def q_text(req, q):
    return i18n.question(req.lang, q["code"], q["prompt"], svc.question_options(q), q["rationale"], bool(q["custom"]))


def _quiz_form(req, questions, action, intro, signed=False):
    T = req.t
    blocks_html = []
    for n, q in enumerate(questions, start=1):
        prompt, opts_text, _ = q_text(req, q)
        order = [i for i, _ in svc.shuffled_options(q)]
        opts = "".join(
            '<label class="option"><input type="radio" name="q{qid}" value="{i}" required> {text}</label>'.format(
                qid=q["id"], i=i, text=esc(opts_text[i])
            )
            for i in order
        )
        tag = ' <span class="badge prog">{}</span>'.format(T("Scenario")) if q["scenario"] else ""
        blocks_html.append(
            '<fieldset class="question"><legend><span class="qnum">{n}.</span> {prompt}{tag}</legend>{opts}</fieldset>'.format(
                n=n, prompt=esc(prompt), tag=tag, opts=opts
            )
        )
    qids = ",".join(str(q["id"]) for q in questions)
    sig = '<input type="hidden" name="sig" value="{}">'.format(sign(req.conn, qids)) if signed else ""
    return """{intro}<form method="post" action="{action}" class="quiz">{csrf}
<input type="hidden" name="qids" value="{qids}">{sig}
{blocks}
<button type="submit" class="btn primary">{btn}</button></form>""".format(
        intro=intro, action=action, csrf=csrf_field(req), qids=qids, sig=sig, blocks="".join(blocks_html),
        btn=T("Submit answers"),
    )


def _read_answers(req, allowed_ids):
    answers = {}
    for qid in allowed_ids:
        raw = req.get("q{}".format(qid))
        answers[qid] = int(raw) if raw.isdigit() else None
    return answers


def page_module_quiz(req, slug):
    T = req.t
    m = _module_or_404(req, slug)
    questions = svc.module_questions(req.conn, m["id"])
    if not questions:
        redirect("/module/" + slug, msg="This module has no quiz.")
    if req.method == "POST":
        ids = [q["id"] for q in questions]
        attempt = svc.grade_attempt(req.conn, req.user["id"], "module", ids, _read_answers(req, ids), m["id"])
        redirect("/attempt/{}".format(attempt))
    intro = """<p class="crumbs"><a href="/dashboard">{home}</a> &rsaquo; <a href="/module/{slug}">{title}</a> &rsaquo; {quiz}</p>
<h1>{h1}</h1><p>{info}</p>""".format(
        home=T("My course"), slug=slug, title=esc(mod_title(req, m)), quiz=T("Quiz"),
        h1=T("Quiz: {title}", title=mod_title(req, m)),
        info=T("Answer all {n} questions. Pass mark {pm}%.", n=len(questions), pm=get_setting(req.conn, "pass_mark")),
    )
    return layout(req, T("Quiz"), _quiz_form(req, questions, "/module/{}/quiz".format(slug), intro), "dashboard")


def page_final(req):
    T = req.t
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
            '<tr><td>{}</td><td>{}/{}</td><td>{}</td><td><a href="/attempt/{}">{}</a></td></tr>'.format(
                esc(a["completed_at"]), a["score"], a["total"], T("Passed") if a["passed"] else T("Not passed"),
                a["id"], T("Review"),
            )
            for a in history
        )
        warn = ""
        if not prog["lessons_ok"]:
            warn = '<div class="callout note">{}</div>'.format(T(
                "We recommend finishing all lessons first ({done}/{total} done). You can still try the assessment.",
                done=prog["done_lessons"], total=prog["total_lessons"]))
        body = """<h1>{h1}</h1>
<p>{info}</p>
{warn}
<a class="btn primary" href="/final?start=1">{start}</a>
{hist}""".format(
            h1=T("Final assessment"),
            info=T("{n} questions drawn from the question bank, including the three key knowledge-check questions. Pass mark {pm}%. A new set of questions is chosen each time, and you can retake it.",
                   n=content.FINAL_QUESTION_COUNT, pm=get_setting(req.conn, "pass_mark")),
            warn=warn, start=T("Start the final assessment"),
            hist="<h2>{}</h2><table class='grid'><tr><th>{}</th><th>{}</th><th>{}</th><th></th></tr>{}</table>".format(
                T("Your attempts"), T("Date (UTC)"), T("Score"), T("Result"), hist) if hist else "",
        )
        return layout(req, T("Final assessment"), body, "dashboard")
    questions = svc.final_questions(req.conn)
    intro = "<h1>{}</h1><p>{}</p>".format(T("Final assessment"), T("Answer all {n} questions, then submit.", n=len(questions)))
    return layout(req, T("Final assessment"), _quiz_form(req, questions, "/final", intro, signed=True), "dashboard")


def page_attempt(req, attempt_id):
    T = req.t
    owner = None if req.user["role"] == "admin" else req.user["id"]
    attempt, answers = svc.attempt_review(req.conn, int(attempt_id), owner)
    if not attempt:
        raise HttpError(404, "Attempt not found.")
    pct_ = round(100 * attempt["score"] / attempt["total"]) if attempt["total"] else 0
    items = []
    for n, a in enumerate(answers, start=1):
        prompt, opts, rationale = q_text(req, a)
        ci = a["chosen_index"]
        chosen = opts[ci] if ci is not None and 0 <= ci < len(opts) else T("(no answer)")
        src = (
            '<div class="muted small">{0}: <a href="{1}" target="_blank" rel="noopener">{1}</a></div>'.format(T("Reference"), esc(a["source_url"]))
            if a["source_url"] else ""
        )
        items.append(
            """<div class="review {cls}"><h3>{n}. {prompt}</h3>
<p><strong>{verdict}</strong> {yours}: {chosen}</p>
{correct}<p class="why">{rationale}</p>{src}</div>""".format(
                cls="right" if a["correct"] else "wrong", n=n, prompt=esc(prompt),
                verdict=T("Correct.") if a["correct"] else T("Not quite."), yours=T("Your answer"), chosen=esc(chosen),
                correct="" if a["correct"] else "<p>{}: <strong>{}</strong></p>".format(T("Correct answer"), esc(opts[a["correct_index"]])),
                rationale=esc(rationale), src=src,
            )
        )
    if attempt["kind"] == "module":
        mod = req.conn.execute("SELECT * FROM modules WHERE id = ?", (attempt["module_id"],)).fetchone()
        retry = "/module/{}/quiz".format(mod["slug"])
        title = T("Quiz result: {title}", title=mod_title(req, mod))
    else:
        retry = "/final?start=1"
        title = T("Final assessment result")
    step = svc.next_step(req.conn, attempt["user_id"])
    body = """<h1>{title}</h1>
<div class="result {cls}"><div class="num">{score}/{total}</div><div>{pct}% &middot; {verdict}</div></div>
<p><a class="btn" href="{retry}">{again}</a> <a class="btn primary" href="{url}">{label}</a></p>
<h2>{h2}</h2>{items}""".format(
        title=esc(title), cls="pass" if attempt["passed"] else "fail", score=attempt["score"], total=attempt["total"],
        pct=pct_, verdict=T("Passed") if attempt["passed"] else T("Not passed yet. Read the explanations and try again."),
        retry=retry, again=T("Try again"), url=step["url"], label=esc(next_label(req, step)),
        h2=T("Review your answers"), items="".join(items),
    )
    return layout(req, title, body, "dashboard")


def page_lab(req):
    T = req.t
    uid = req.user["id"]
    if req.method == "POST":
        step = int(req.get("step", "0") or 0)
        if 1 <= step <= len(content.LAB_STEPS):
            svc.set_lab_step(req.conn, uid, step, req.get("done") == "1", req.get("note"))
        redirect("/lab", msg="Lab progress saved.")
    done = svc.lab_done_steps(req.conn, uid)
    req_done = sum(1 for s in range(1, content.LAB_REQUIRED_STEPS + 1) if s in done)
    rows = []
    for no, instruction, evidence in content.LAB_STEPS:
        instruction, evidence = i18n.lab_step(req.lang, no, instruction, evidence)
        d = done.get(no)
        rows.append(
            """<li class="lab-step {cls}" id="step{no}">
<div class="lab-head"><span class="stepno">{no}</span><div><strong>{instr}</strong>{opt}
<div class="muted">{dw}: {evidence}</div></div></div>
<form method="post" class="lab-form">{csrf}<input type="hidden" name="step" value="{no}">
<label class="sr-only" for="note{no}">{notel}</label>
<input id="note{no}" name="note" placeholder="{ph}" value="{note}" maxlength="1000">
<input type="hidden" name="done" value="{next}">
<button class="btn {btncls}" type="submit">{btn}</button></form></li>""".format(
                cls="done" if d else "", no=no, instr=esc(instruction), dw=T("Done when"), evidence=esc(evidence),
                opt="" if no <= content.LAB_REQUIRED_STEPS else ' <span class="badge todo">{}</span>'.format(T("Optional")),
                csrf=csrf_field(req), notel=T("Note for step {n}", n=no), ph=T("Optional note (no confidential data)"),
                note=esc(d["note"]) if d else "", next="0" if d else "1",
                btncls="" if d else "primary", btn=T("Undo") if d else T("Mark done"),
            )
        )
    pct_ = round(100 * req_done / content.LAB_REQUIRED_STEPS)
    body = """<h1>{h1}</h1>
<p>{intro}</p>
{bar}
<ol class="lab">{rows}</ol>
<div class="callout note">{note}</div>""".format(
        h1=T("Hands-on lab: build, test, improve, verify"),
        intro=T("Do these steps in Microsoft 365 Copilot while this page is open, and tick each one when its \"Done when\" check is true. Main lab: build the Email Clarity Coach (copy its instructions from Templates). Steps 1 to {n} are required; 11 and 12 are recommended.", n=content.LAB_REQUIRED_STEPS),
        bar=progress_bar(pct_, T("{done} of {total} required steps done", done=req_done, total=content.LAB_REQUIRED_STEPS)),
        rows="".join(rows),
        note=T("Never share real confidential content as evidence. A safe screenshot of your agent's name and configuration, your charter, three prompts and your test card are enough for your facilitator."),
    )
    return layout(req, T("Lab"), body, "lab")


# ---------------------------------------------------------------------------
# Toolkit pages
# ---------------------------------------------------------------------------

def charter_labels(req):
    return [(k, i18n.label(req.lang, "charter_label", k, l), i18n.label(req.lang, "charter_hint", k, h))
            for k, l, h in svc.CHARTER_FIELDS]


def page_charter(req):
    T = req.t
    uid = req.user["id"]
    if req.method == "POST":
        svc.save_charter(req.conn, uid, req.form)
        redirect("/charter", msg="Charter saved.")
    data, updated = svc.get_charter(req.conn, uid)
    fields = []
    for key, label, hint in charter_labels(req):
        multiline = key in ("in_scope", "out_scope", "prompts", "purpose")
        if multiline:
            inp = '<textarea name="{k}" rows="3" placeholder="{h}" maxlength="2000">{v}</textarea>'
        else:
            inp = '<input name="{k}" placeholder="{h}" value="{v}" maxlength="2000">'
        fields.append("<label>{} {}</label>".format(esc(label), inp.format(k=key, h=esc(hint), v=esc(data.get(key, "")))))
    preview = ""
    if data:
        preview = """<div class="card"><h2>{h1}</h2>{charter}
<h2>{h2}</h2><p class="muted">{tip}</p>{instr}
<p><a class="btn" href="/charter.txt">{dl}</a> <a class="btn primary" href="/hub/agents/new?from=charter">{reg}</a></p></div>""".format(
            h1=T("Your charter as text"), charter=blocks.copy(svc.charter_text(data)),
            h2=T("Draft instructions from your charter"),
            tip=T("Paste into the Instructions box on the Configure tab, then review and test."),
            instr=blocks.copy(svc.charter_instructions(data)), dl=T("Download as .txt"),
            reg=T("Register this agent in the hub"),
        )
    body = """<h1>{h1}</h1>
<p>{intro}</p>
{updated}
<form method="post" class="form wide card">{csrf}{fields}
<button class="btn primary" type="submit">{btn}</button></form>
{preview}""".format(
        h1=T("My agent charter"),
        intro=T("Plan your agent before you build it. Keep it to one purpose. Do not include confidential data."),
        updated='<p class="muted">{}</p>'.format(T("Last saved {date} UTC", date=updated)) if updated else "",
        csrf=csrf_field(req), fields="".join(fields), btn=T("Save charter"), preview=preview,
    )
    return layout(req, T("My agent charter"), body, "toolkit")


def page_charter_txt(req):
    data, _ = svc.get_charter(req.conn, req.user["id"])
    text = svc.charter_text(data) + "\n\n--- DRAFT INSTRUCTIONS ---\n" + svc.charter_instructions(data) + "\n"
    return ("text/plain; charset=utf-8", text.encode(), {"Content-Disposition": 'attachment; filename="agent_charter.txt"'})


def page_templates(req):
    T = req.t
    cards = []
    for t in content.TEMPLATES:
        title = i18n.template(req.lang, t["slug"], "title", t["title"])
        use = i18n.template(req.lang, t["slug"], "use", t["use"])
        body_txt = i18n.template(req.lang, t["slug"], "body", t["body"])
        original = ""
        if req.lang != i18n.DEFAULT:
            original = "<details><summary>{}</summary>{}</details>".format(T("English original"), blocks.copy(t["body"]))
        cards.append('<section class="card" id="{}"><h2>{}</h2><p class="muted">{}</p>{}{}</section>'.format(
            t["slug"], esc(title), esc(use), blocks.copy(body_txt), original))
    body = "<h1>{}</h1><p>{}</p>{}".format(
        T("Ready-to-use templates"),
        T("Press Copy, paste into Agent Builder or a document, and replace every [bracket]. Agent instructions can be written in your own language if your organization allows it."),
        "".join(cards),
    )
    return layout(req, T("Templates"), body, "toolkit")


def page_certificate(req):
    T = req.t
    prog = svc.user_progress(req.conn, req.user["id"])
    if not prog["certified"]:
        redirect("/dashboard", error="Your certificate unlocks after you finish all lessons, the required lab steps and the final assessment.")
    final = prog["final"]
    body = """<div class="certificate">
<div class="cert-org">{org}</div>
<div class="cert-title">{title}</div>
<p>{certifies}</p>
<div class="cert-name">{name}</div>
<p class="muted">{aid}</p>
<p>{completed}</p>
<div class="cert-course">{course}</div>
<p>{incl}</p>
<p class="muted">{date}</p>
</div>
<p class="noprint"><button class="btn primary" type="button" onclick="window.print()">{print}</button></p>""".format(
        org=esc(get_setting(req.conn, "org_name")), title=T("Certificate of Completion"),
        certifies=T("This certifies that"), name=esc(req.user["name"]),
        aid=T("Associate ID {id}", id=req.user["associate_id"]), completed=T("has completed"),
        course=T("Simple Copilot Agent Builder (T1): One Agent, One Purpose"),
        incl=T("including the hands-on lab and the final assessment (score {score}/{total}).", score=final["score"], total=final["total"]),
        date=T("Completed {date} UTC · content edition {edition}", date=final["completed_at"][:10], edition=content.EDITION_DATE),
        print=T("Print or save as PDF"),
    )
    return layout(req, T("Certificate"), body)


def page_feedback(req):
    T = req.t
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
    body = """<section class="card narrow"><h1>{h1}</h1>
<form method="post" class="form">{csrf}
<fieldset><legend>{q}</legend>{stars}</fieldset>
<label>{l} <textarea name="comment" rows="4" maxlength="2000"></textarea></label>
<button class="btn primary" type="submit">{btn}</button></form></section>""".format(
        h1=T("Course feedback"), csrf=csrf_field(req), q=T("How useful was this course? (1 = not useful, 5 = very useful)"),
        stars=stars, l=T("What should we improve? (optional)"), btn=T("Send feedback"),
    )
    return layout(req, T("Feedback"), body)


def page_toolkit(req):
    T = req.t
    tiles = [
        ("/charter", T("My agent charter"), T("Plan one agent with one purpose; get draft instructions.")),
        ("/templates", T("Templates"), T("Copy-ready charter, instructions, test card and two examples.")),
        ("/quickref", T("Quick reference card"), T("One printable page: Plan, Build, Test, Use safely.")),
        ("/glossary", T("Glossary"), T("Plain-language meanings of Copilot and agent terms.")),
        ("/resources", T("Microsoft references"), T("The official Microsoft Learn and Support pages this course is based on, with dates.")),
        ("/facilitator", T("Facilitator guide"), T("150-minute agenda, 60-minute route and preparation checklist.")),
        ("/help", T("Policy and help"), T("Acceptable-use guideline, data rules and Ask the CoE.")),
    ]
    body = "<h1>{}</h1><div class='tiles'>{}</div>".format(
        T("Toolkit"),
        "".join('<a class="tile" href="{}"><strong>{}</strong><span>{}</span></a>'.format(u, esc(t), esc(d)) for u, t, d in tiles),
    )
    return layout(req, T("Toolkit"), body, "toolkit")


def page_resources(req):
    T = req.t
    rows = "".join(
        '<tr><td><a href="{url}" target="_blank" rel="noopener">{title}</a></td><td>{upd}</td><td>{ver}</td></tr>'.format(
            url=s["url"], title=esc(s["title"]), upd=esc(s["updated"] or "-"), ver=blocks.VERIFIED_DATE)
        for s in blocks.SOURCES.values()
    )
    facts = i18n.block(req.lang, "KEY_FACTS", KEY_FACTS)
    body = """<h1>{h1}</h1><p>{intro}</p>
<div class="table-wrap"><table class="grid"><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th></tr>{rows}</table></div>
<section class="card"><h2>{h2}</h2><ul>{facts}</ul></section>""".format(
        h1=T("Microsoft references"),
        intro=T("This course was checked against these official Microsoft pages. Microsoft updates them often, so facilitators should re-check them before each cohort."),
        c1=T("Page"), c2=T("Last updated (shown on page)"), c3=T("Checked by us"), rows=rows,
        h2=T("Key facts from Microsoft Learn"), facts="".join("<li>{}</li>".format(esc(f)) for f in facts),
    )
    return layout(req, T("Microsoft references"), body, "toolkit")


KEY_FACTS = [
    "Agent Builder is available in the Microsoft 365 Copilot app, at microsoft365.com/chat and in Teams (desktop and web), not in mobile apps.",
    "Start from Agents > New agent: use the Describe tab, Skip to configure, or Start with a template.",
    "Limits: name 30 characters, description 1,000, instructions 8,000.",
    "Knowledge limits per agent: 4 public URLs, 100 SharePoint files, 50 OneDrive files, 20 uploaded files.",
    "Test on the Try it tab; it is enabled once the agent has a name, description and instructions.",
    "New agents are private. Share roles are Can chat and Can edit; groups can only get Can chat.",
    "Edits to a shared agent reach users only after you select Update.",
    "Agents respect each user's permissions and sensitivity labels; people you share with do not get access to your email.",
    "Only use specified sources prioritizes your sources but does not fully block general AI knowledge.",
    "Agent Builder cannot create actions that connect to external services; copy the agent to Copilot Studio for that.",
    "Agent Builder agents cannot be used in Teams group or 1:1 chats.",
    "Shared chat links are snapshots; manage them in Settings > Data controls > Shared links.",
    "Copilot memory (preview) lives in Settings > Personalization; deleting a chat does not delete saved memories.",
    "In Microsoft's zoned governance guidance, Agent Builder belongs to Zone 1 (citizen development).",
]


def page_glossary(req):
    T = req.t
    terms = i18n.block(req.lang, "GLOSSARY", content.GLOSSARY)
    body = "<h1>{}</h1><dl class='glossary'>{}</dl>".format(
        T("Glossary"), "".join("<dt>{}</dt><dd>{}</dd>".format(esc(a), esc(b)) for a, b in terms))
    return layout(req, T("Glossary"), body, "toolkit")


def page_quickref(req):
    T = req.t
    q = i18n.block(req.lang, "QUICKREF", content.QUICKREF)
    cols = "".join(
        "<div class='qr-col'><h2>{}</h2><ul>{}</ul></div>".format(
            esc(h), "".join("<li>{}</li>".format(esc(x)) for x in items))
        for h, items in q["steps"]
    )
    body = """<div class="quickref"><h1>{title}</h1>
<p class="qr-key">{key}</p>
<div class="qr-grid">{cols}</div>
<div class="qr-tests"><strong>{tests_h}</strong> {tests}</div>
<p class="muted small">{edition}</p></div>
<p class="noprint"><button class="btn primary" type="button" onclick="window.print()">{print}</button></p>""".format(
        title=esc(q["title"]), key=T("One agent = one purpose. Use the right chat for the right topic. Always verify important outputs."),
        cols=cols, tests_h=T("3-test card:"),
        tests=T("1. On topic: does the job. 2. Vague: asks for what is missing. 3. Off topic: redirects to Copilot Chat."),
        edition=T("Checked against Microsoft Learn on {date}. Features vary by licence and tenant.", date=content.EDITION_DATE),
        print=T("Print or save as PDF (A4)"),
    )
    return layout(req, q["title"], body, "toolkit")


def page_facilitator(req):
    T = req.t
    fac = i18n.block(req.lang, "FACILITATOR", {"agenda": content.FACILITATOR_AGENDA, "prep": content.FACILITATOR_PREP})
    rows = "".join("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(esc(a), m, esc(b), esc(c))
                   for a, m, b, c in fac["agenda"])
    prep = "".join("<li>{}</li>".format(esc(p)) for p in fac["prep"])
    body = """<h1>{h1}</h1>
<section class="card"><h2>{h_agenda}</h2>
<table class="grid"><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th><th>{c4}</th></tr>{rows}</table>
<p><strong>{h_ess}</strong> {ess}</p></section>
<section class="card"><h2>{h_prep}</h2><ul class="checklist">{prep}</ul></section>
<section class="card"><h2>{h_quiz}</h2><p>{quiz}</p></section>""".format(
        h1=T("Facilitator guide"), h_agenda=T("150-minute agenda"), c1=T("Start"), c2=T("Minutes"), c3=T("Topic"),
        c4=T("In this app"), rows=rows, h_ess=T("60-minute essentials route:"),
        ess=T("modules 2, 3, 4, 6 and 7, then lab steps 1 to 8."), h_prep=T("Preparation checklist"), prep=prep,
        h_quiz=T("Quiz answers"),
        quiz=T("Every quiz shows the correct answer and explanation after submitting. Administrators can review any learner's attempt and download the full question bank with answers from Admin > Question bank."),
    )
    return layout(req, T("Facilitator guide"), body, "toolkit")


# ---------------------------------------------------------------------------
# Learning paths and skills self-assessment
# ---------------------------------------------------------------------------

def page_paths(req):
    T = req.t
    levels = hub.builder_levels(req.conn, req.user)
    cards = []
    for key, name, requirement, unlocks in content.BUILDER_LEVELS:
        ok = levels[key]
        cards.append("""<div class="level {cls}"><h3>{badge} {name}</h3><p><strong>{l_req}</strong> {req_}</p>
<p><strong>{l_unl}</strong> {unl}</p></div>""".format(
            cls="ok" if ok else "", badge=check(req, ok), name=esc(i18n.label(req.lang, "levels", key, name)),
            l_req=T("Requirement:"), req_=esc(i18n.label(req.lang, "level_req", key, requirement)),
            l_unl=T("Unlocks:"), unl=esc(i18n.label(req.lang, "level_unlocks", key, unlocks)),
        ))
    tracks = []
    for track, title, desc in (
        ("leader", T("Leader track"), T("For managers and executives: what leading companies do, tiered governance, value and roadmap.")),
        ("coach", T("Coach track"), T("For Copilot coaches: helping colleagues, running promptathons and reviewing agents.")),
    ):
        n, total, mods = hub.track_progress(req.conn, req.user["id"], track)
        link = '<a class="btn" href="/module/{}">{}</a>'.format(mods[0]["slug"], T("Open")) if mods else ""
        tracks.append("""<div class="card"><h3>{t}</h3><p>{d}</p>{bar}{link}</div>""".format(
            t=esc(title), d=esc(desc), bar=progress_bar(round(100 * n / total) if total else 0, T("{done}/{total} lessons", done=n, total=total)),
            link=link))
    answers = hub.get_assessment(req.conn, req.user["id"])
    rec = hub.recommendations(answers)
    if answers is None:
        rec_html = '<p>{}</p><a class="btn primary" href="/paths/assess">{}</a>'.format(
            T("Take a 2-minute skills check to get personal recommendations."), T("Start the skills check"))
    elif rec:
        items = []
        for slug in rec:
            m = svc.get_module(req.conn, slug)
            if m:
                items.append('<li><a href="/module/{}">{}</a></li>'.format(slug, esc(mod_title(req, m))))
        rec_html = '<p>{}</p><ul>{}</ul><a class="btn" href="/paths/assess">{}</a>'.format(
            T("Based on your skills check, study these next:"), "".join(items), T("Retake the skills check"))
    else:
        rec_html = '<p>{}</p><a class="btn" href="/paths/assess">{}</a>'.format(
            T("Your skills check shows no gaps. Consider the coach track and register your agents."), T("Retake the skills check"))
    body = """<h1>{h1}</h1><p>{intro}</p>
<section class="card"><h2>{h_rec}</h2>{rec}</section>
<h2>{h_levels}</h2><div class="levels">{cards}</div>
<h2>{h_tracks}</h2><div class="grid-2">{tracks}</div>""".format(
        h1=T("Learning paths"),
        intro=T("Everyone starts with the foundation. Each builder level unlocks wider sharing in the Agent hub, as in Hitachi's certification-led approach."),
        h_rec=T("Recommended for you"), rec=rec_html, h_levels=T("Builder levels"), cards="".join(cards),
        h_tracks=T("Optional tracks"), tracks="".join(tracks),
    )
    return layout(req, T("Learning paths"), body, "dashboard")


def page_assess(req):
    T = req.t
    if req.method == "POST":
        try:
            hub.save_assessment(req.conn, req.user["id"], req.form)
        except ValueError as e:
            redirect("/paths/assess", error=str(e))
        redirect("/paths", msg="Skills check saved.")
    current = hub.get_assessment(req.conn, req.user["id"]) or {}
    rows = []
    for key, text in content.SKILL_STATEMENTS:
        opts = "".join(
            '<label class="option inline-opt"><input type="radio" name="{k}" value="{v}" required{c}> {l}</label>'.format(
                k=key, v=v, c=" checked" if str(current.get(key)) == v else "", l=esc(i18n.label(req.lang, "skill_scale", v, l)))
            for v, l in content.SKILL_SCALE
        )
        rows.append("<fieldset class='question'><legend>{}</legend>{}</fieldset>".format(
            esc(i18n.label(req.lang, "skills", key, text)), opts))
    body = """<h1>{h1}</h1><p>{intro}</p><form method="post" class="quiz">{csrf}{rows}
<button class="btn primary" type="submit">{btn}</button></form>""".format(
        h1=T("Skills check"), intro=T("Rate each statement honestly. Your answers are only used to recommend modules."),
        csrf=csrf_field(req), rows="".join(rows), btn=T("Save and see recommendations"),
    )
    return layout(req, T("Skills check"), body, "dashboard")

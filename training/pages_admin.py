"""Administrator pages: reports, learners, coaches, import, question bank, settings."""

import csv
import io

from . import content, hub, i18n, services as svc
from .core import (HttpError, PAGE_SIZE, check, csrf_field, esc, layout, pct, progress_bar, quote, redirect,
                   urlencode)
from .db import get_setting, set_setting


def _require_admin(req):
    if req.user["role"] != "admin":
        raise HttpError(403, "Administrators only.")


def admin_nav(req, active):
    T = req.t
    links = [
        ("overview", "/admin", T("Overview")), ("learners", "/admin/learners", T("Learners")),
        ("import", "/admin/import", T("Import associates")), ("questions", "/admin/questions", T("Question bank")),
        ("feedback", "/admin/feedback", T("Feedback")), ("settings", "/admin/settings", T("Settings")),
    ]
    return '<nav class="subnav" aria-label="{}">{}</nav>'.format(T("Admin"), "".join(
        '<a href="{}" class="{}">{}</a>'.format(u, "active" if k == active else "", l) for k, u, l in links))


def page_admin(req):
    _require_admin(req)
    T = req.t
    s = svc.overview_stats(req.conn)
    total = s["total"]
    c = s["counts"]
    dept_rows = "".join(
        """<tr><td>{d}</td><td>{t}</td><td>{a}</td><td>{cert}</td><td>{bar}</td>
<td><a href="/admin/learners?department={q}">{view}</a> &middot; <a href="/admin/export.csv?department={q}">CSV</a></td></tr>""".format(
            d=esc(name), t=v["total"], a=v["active"], cert=v["Certified"],
            bar=progress_bar(pct(v["Certified"], v["total"]), T("{n}% certified", n=pct(v["Certified"], v["total"]))),
            q=quote(name if name != "(none)" else ""), view=T("View"),
        )
        for name, v in s["departments"]
    )
    funnel_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            esc(i18n.module(req.lang, f["slug"], "title", f["title"])),
            f["completed"], f["passed"])
        for f in svc.module_funnel(req.conn)
    )
    body = """{nav}<h1>{h1}</h1>
<section class="grid-4">
<div class="stat"><div class="num">{total}</div><div>{l_total}</div></div>
<div class="stat"><div class="num">{cert}</div><div>{l_cert}</div></div>
<div class="stat"><div class="num">{prog}</div><div>{l_prog}</div></div>
<div class="stat"><div class="num">{notstarted}</div><div>{l_ns}</div></div>
</section>
<section class="grid-4">
<div class="stat"><div class="num">{active}</div><div>{l_active}</div></div>
<div class="stat"><div class="num">{favg}</div><div>{l_favg}</div></div>
<div class="stat"><div class="num">{fb}</div><div>{l_fb}</div></div>
<div class="stat"><div class="num"><a href="/admin/export.csv">CSV</a></div><div>{l_csv}</div></div>
</section>
<p><a class="btn" href="/insights">{insights}</a> <a class="btn" href="/hub/reviews">{reviews}</a> <a class="btn" href="/hub/licences">{licences}</a></p>
<section class="card"><h2>{h_overall}</h2>{bar}</section>
<section class="card"><h2>{h_dept}</h2>
<div class="table-wrap"><table class="grid"><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th><th>{c4}</th><th>{c5}</th><th></th></tr>{dept_rows}</table></div></section>
<section class="card"><h2>{h_funnel}</h2><p class="muted">{funnel_p}</p>
<table class="grid"><tr><th>{f1}</th><th>{f2}</th><th>{f3}</th></tr>{funnel_rows}</table></section>""".format(
        nav=admin_nav(req, "overview"), h1=T("Training overview"), total=total, l_total=T("Associates loaded"),
        cert=c["Certified"], l_cert=T("Certified ({n}%)", n=pct(c["Certified"], total)),
        prog=c["In progress"], l_prog=T("In progress"), notstarted=c["Not started"] + c["Registered"],
        l_ns=T("Not started / registered only"), active=s["active_week"], l_active=T("Signed in during the last 7 days"),
        favg="{}%".format(s["final_avg"]) if s["final_avg"] is not None else "-",
        l_favg=T("Average final score ({n} attempts)", n=s["final_attempts"]),
        fb="{}/5".format(s["feedback_avg"]) if s["feedback_avg"] is not None else "-",
        l_fb=T("Average feedback ({n} responses)", n=s["feedback_count"]), l_csv=T("Download full progress report"),
        insights=T("Adoption dashboard"), reviews=T("Review queue"), licences=T("Licence requests"),
        h_overall=T("Overall certification"),
        bar=progress_bar(pct(c["Certified"], total), T("{n} of {total} associates certified", n=c["Certified"], total=total)),
        h_dept=T("By department"), c1=T("Department"), c2=T("Associates"), c3=T("Active"), c4=T("Certified"),
        c5=T("Certification rate"),
        dept_rows=dept_rows or '<tr><td colspan="6">{}</td></tr>'.format(T("No associates yet. Import a CSV.")),
        h_funnel=T("Module funnel"),
        funnel_p=T("How many learners finished each module's lessons and passed its quiz. A sharp drop shows where people get stuck."),
        f1=T("Module"), f2=T("Lessons completed"), f3=T("Quiz passed"), funnel_rows=funnel_rows,
    )
    return layout(req, T("Admin"), body, "admin")


STATUSES = ("Certified", "In progress", "Registered", "Not started")


def page_admin_learners(req):
    _require_admin(req)
    T = req.t
    search = req.query.get("q", "")
    dept = req.query.get("department", "")
    status = req.query.get("status", "")
    coaches_only = req.query.get("coaches") == "1"
    page = int(req.query.get("page", "1")) if req.query.get("page", "1").isdigit() else 1
    page = max(1, page)
    rows, total = svc.learner_rows(req.conn, search, dept, status, PAGE_SIZE, (page - 1) * PAGE_SIZE, coaches_only)
    dept_opts = "".join(
        '<option value="{0}"{1}>{0}</option>'.format(esc(d), " selected" if d == dept else "") for d in svc.departments(req.conn))
    status_opts = "".join(
        '<option value="{}"{}>{}</option>'.format(s, " selected" if s == status else "", T(s)) for s in STATUSES)
    trs = "".join(
        """<tr><td><a href="/admin/learner/{id}">{aid}</a></td><td>{name}{coach}</td><td>{dept}</td><td>{status}</td>
<td>{ld}/{tl}</td><td>{qp}</td><td>{lab}/{labreq}</td><td>{final}</td><td>{last}</td></tr>""".format(
            id=r["id"], aid=esc(r["associate_id"]), name=esc(r["name"]),
            coach=' <span class="badge ok">{}</span>'.format(T("Coach")) if r["is_reviewer"] else "",
            dept=esc(r["department"]), status=esc(T(r["status"])), ld=r["lessons_done"], tl=r["total_lessons"],
            qp=r["quizzes_passed"], lab=r["lab_done"], labreq=content.LAB_REQUIRED_STEPS,
            final="{}%".format(int(r["final_best_pct"])) if r["final_best_pct"] is not None else "-",
            last=esc((r["last_login"] or "-")[:16]),
        )
        for r in rows
    )
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    base = {"q": search, "department": dept, "status": status, "coaches": "1" if coaches_only else ""}
    pager = ""
    if pages > 1:
        prev_l = '<a href="?{}">&larr; {}</a>'.format(urlencode(dict(base, page=page - 1)), T("Previous")) if page > 1 else ""
        next_l = '<a href="?{}">{} &rarr;</a>'.format(urlencode(dict(base, page=page + 1)), T("Next")) if page < pages else ""
        pager = '<div class="pager">{} {} {}</div>'.format(prev_l, T("Page {n} of {total}", n=page, total=pages), next_l)
    body = """{nav}<h1>{h1}</h1>
<form method="get" class="filters">
<label>{l_search} <input name="q" value="{q}" placeholder="{ph}"></label>
<label>{l_dept} <select name="department"><option value="">{all}</option>{dept_opts}</select></label>
<label>{l_status} <select name="status"><option value="">{all}</option>{status_opts}</select></label>
<label class="option inline-opt"><input type="checkbox" name="coaches" value="1"{cchk}> {l_coaches}</label>
<button class="btn" type="submit">{filter}</button>
<a class="btn" href="/admin/export.csv?{exp}">{export}</a>
</form>
<p class="muted">{match}</p>
<div class="table-wrap"><table class="grid"><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th><th>{c4}</th><th>{c5}</th>
<th>{c6}</th><th>{c7}</th><th>{c8}</th><th>{c9}</th></tr>{trs}</table></div>{pager}""".format(
        nav=admin_nav(req, "learners"), h1=T("Learners"), l_search=T("Search"), q=esc(search), ph=T("ID, name or email"),
        l_dept=T("Department"), all=T("All"), dept_opts=dept_opts, l_status=T("Status"), status_opts=status_opts,
        cchk=" checked" if coaches_only else "", l_coaches=T("Coaches only"), filter=T("Filter"),
        exp=urlencode({"department": dept}), export=T("Export these to CSV"), match=T("{n} learners match.", n=total),
        c1=T("Associate ID"), c2=T("Name"), c3=T("Department"), c4=T("Status"), c5=T("Lessons"), c6=T("Quizzes passed"),
        c7=T("Lab"), c8=T("Best final"), c9=T("Last sign-in (UTC)"),
        trs=trs or '<tr><td colspan="9">{}</td></tr>'.format(T("No learners found.")), pager=pager,
    )
    return layout(req, T("Learners"), body, "admin")


def page_admin_learner(req, user_id):
    _require_admin(req)
    T = req.t
    u = req.conn.execute("SELECT * FROM users WHERE id = ?", (int(user_id),)).fetchone()
    if not u:
        raise HttpError(404, "Learner not found.")
    here = "/admin/learner/{}".format(u["id"])
    if req.method == "POST":
        action = req.get("action")
        if action == "reset-password":
            svc.reset_password(req.conn, u["id"])
            redirect(here, msg="Password cleared. The associate can register again with the same ID; progress is kept.")
        if action == "update":
            req.conn.execute(
                "UPDATE users SET name = ?, email = ?, department = ?, location = ? WHERE id = ?",
                (req.get("name").strip() or u["name"], req.get("email").strip(), req.get("department").strip(),
                 req.get("location").strip(), u["id"]),
            )
            req.conn.commit()
            redirect(here, msg="Details updated.")
        if action == "coach":
            make = req.get("value") == "1"
            req.conn.execute("UPDATE users SET is_reviewer = ? WHERE id = ?", (int(make), u["id"]))
            if make:
                hub.notify(req.conn, u["id"], "You are now a Copilot coach. You can review agents and answer how-to questions.", "/hub/reviews")
            req.conn.commit()
            redirect(here, msg="Coach role updated.")
        raise HttpError(400, "Unknown action.")
    prog = svc.user_progress(req.conn, u["id"])
    attempts = req.conn.execute(
        """SELECT a.*, m.title AS module_title, m.slug AS module_slug FROM quiz_attempts a LEFT JOIN modules m ON m.id = a.module_id
           WHERE a.user_id = ? ORDER BY a.completed_at DESC LIMIT 50""",
        (u["id"],),
    ).fetchall()
    att_rows = "".join(
        '<tr><td>{}</td><td>{}</td><td>{}/{}</td><td>{}</td><td><a href="/attempt/{}">{}</a></td></tr>'.format(
            esc(a["completed_at"]),
            esc(i18n.module(req.lang, a["module_slug"], "title", a["module_title"]) if a["module_slug"] else T("Final assessment")),
            a["score"], a["total"], T("Passed") if a["passed"] else T("Not passed"), a["id"], T("Review"))
        for a in attempts
    )
    lab = svc.lab_done_steps(req.conn, u["id"])
    lab_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            no, esc(i18n.lab_step(req.lang, no, instr, ev)[0]), check(req, no in lab), esc(lab[no]["note"]) if no in lab else "")
        for no, instr, ev in content.LAB_STEPS
    )
    agents = hub.list_agents(req.conn, owner_id=u["id"])
    agent_rows = "".join('<li><a href="/hub/agents/{}">{}</a> ({})</li>'.format(
        a["id"], esc(a["name"]), esc(i18n.label(req.lang, "agent_status", a["status"], dict(content.AGENT_STATUSES)[a["status"]])))
        for a in agents)
    levels = hub.builder_levels(req.conn, u)
    level_list = "".join("<li>{} {}</li>".format(check(req, levels[k]), esc(i18n.label(req.lang, "levels", k, n)))
                         for k, n, _, _ in content.BUILDER_LEVELS)
    charter, _ = svc.get_charter(req.conn, u["id"])
    coach_form = """<form method="post" class="inline">{csrf}<input type="hidden" name="action" value="coach">
<input type="hidden" name="value" value="{v}"><button class="btn" type="submit">{btn}</button></form>""".format(
        csrf=csrf_field(req), v="0" if u["is_reviewer"] else "1",
        btn=T("Remove coach role") if u["is_reviewer"] else T("Make this person a coach"))
    body = """{nav}<p class="crumbs"><a href="/admin/learners">{learners}</a> &rsaquo; {name}</p>
<h1>{name}</h1>
<section class="grid-2">
<div class="card"><h2>{h_details}</h2>
<form method="post" class="form">{csrf}<input type="hidden" name="action" value="update">
<p>{l_aid}: <strong>{aid}</strong> &middot; {l_reg}: {reg} &middot; {l_last}: {last}</p>
<label>{l_name} <input name="name" value="{name}"></label>
<label>{l_email} <input name="email" value="{email}"></label>
<label>{l_dept} <input name="department" value="{dept}"></label>
<label>{l_loc} <input name="location" value="{loc}"></label>
<button class="btn" type="submit">{save}</button></form>
<form method="post" class="inline" onsubmit="return confirm(this.dataset.q)" data-q="{confirm}">{csrf}
<input type="hidden" name="action" value="reset-password"><button class="btn danger" type="submit">{reset}</button></form>
<h3>{h_coach}</h3><p class="muted">{coach_p}</p>{coach_form}
</div>
<div class="card"><h2>{h_prog}</h2>{bar}
<ul class="checklist"><li>{c1} {l_lessons} {dl}/{tl}</li><li>{c2} {l_lab} {lr}/{labreq}</li>
<li>{c3} {l_final}</li><li>{l_quiz}: {pm}/{qm}</li></ul>
<p>{cert}</p><h3>{h_levels}</h3><ul class="checklist">{levels}</ul>
<h3>{h_agents}</h3><ul>{agents}</ul></div>
</section>
<section class="card"><h2>{h_att}</h2><table class="grid"><tr><th>{a1}</th><th>{a2}</th><th>{a3}</th><th>{a4}</th><th></th></tr>{att}</table></section>
<section class="card"><h2>{h_labs}</h2><table class="grid"><tr><th>#</th><th>{s1}</th><th>{s2}</th><th>{s3}</th></tr>{lab}</table></section>
<section class="card"><h2>{h_charter}</h2>{charter}</section>""".format(
        nav=admin_nav(req, "learners"), learners=T("Learners"), name=esc(u["name"]), h_details=T("Details"),
        csrf=csrf_field(req), l_aid=T("Associate ID"), aid=esc(u["associate_id"]), l_reg=T("Registered"),
        reg=T("Yes") if u["password_hash"] else T("No"), l_last=T("Last sign-in"), last=esc(u["last_login"] or T("never")),
        l_name=T("Name"), l_email=T("Email"), email=esc(u["email"]), l_dept=T("Department"), dept=esc(u["department"]),
        l_loc=T("Location"), loc=esc(u["location"]), save=T("Save details"),
        confirm=esc(T("Clear this password? Progress is kept.")), reset=T("Reset password"),
        h_coach=T("Copilot coach"),
        coach_p=T("Coaches review agents shared with teams, answer how-to questions and host events. Aim for about 1 coach per 60 associates."),
        coach_form=coach_form, h_prog=T("Progress"), bar=progress_bar(prog["percent"], "{}%".format(prog["percent"])),
        c1=check(req, prog["lessons_ok"]), c2=check(req, prog["lab_ok"]), c3=check(req, prog["final_ok"]),
        l_lessons=T("Lessons"), dl=prog["done_lessons"], tl=prog["total_lessons"], l_lab=T("Required lab steps"),
        lr=prog["lab_required_done"], labreq=content.LAB_REQUIRED_STEPS, l_final=T("Final assessment"),
        l_quiz=T("Module quizzes passed"), pm=prog["passed_modules"], qm=prog["quiz_modules"],
        cert="<strong>{}</strong>".format(T("Certified")) if prog["certified"] else T("Not certified yet"),
        h_levels=T("Builder levels"), levels=level_list, h_agents=T("Agents"),
        agents=agent_rows or "<li class='muted'>{}</li>".format(T("None yet.")),
        h_att=T("Quiz attempts"), a1=T("Date (UTC)"), a2=T("Quiz"), a3=T("Score"), a4=T("Result"),
        att=att_rows or '<tr><td colspan="5">{}</td></tr>'.format(T("No attempts yet.")),
        h_labs=T("Lab steps"), s1=T("Step"), s2=T("Status"), s3=T("Learner note"), lab=lab_rows, h_charter=T("Agent charter"),
        charter="<pre class='plain'>{}</pre>".format(esc(svc.charter_text(charter))) if charter else "<p class='muted'>{}</p>".format(T("Not started.")),
    )
    return layout(req, u["name"], body, "admin")


def page_admin_export(req):
    _require_admin(req)
    data = svc.export_progress_csv(req.conn, req.query.get("department", ""))
    return ("text/csv; charset=utf-8", ("﻿" + data).encode("utf-8"),
            {"Content-Disposition": 'attachment; filename="training_progress.csv"'})


def page_admin_import(req):
    _require_admin(req)
    T = req.t
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
            err_html = "<ul class='errors'>{}</ul>".format("".join("<li>{}</li>".format(esc(e)) for e in errors[:20]))
            if len(errors) > 20:
                err_html += "<p>{}</p>".format(T("...and {n} more.", n=len(errors) - 20))
        result = '<div class="flash {}" role="status">{}</div>{}'.format(
            "err" if errors else "ok",
            T("Import finished: {created} added, {updated} updated, {skipped} skipped.", created=created, updated=updated, skipped=len(errors)),
            err_html)
    body = """{nav}<h1>{h1}</h1>
{result}
<div class="card">
<p>{p1}</p>
<p><a href="/static/associates_template.csv" download>{tmpl}</a></p>
<form method="post" enctype="multipart/form-data" class="form">{csrf}
<label>{l_file} <input type="file" name="file" accept=".csv,text/csv"></label>
<label>{l_paste} <textarea name="csv_text" rows="6" placeholder="associate_id,name,email,department,location"></textarea></label>
<button class="btn primary" type="submit">{btn}</button></form>
</div>""".format(
        nav=admin_nav(req, "import"), h1=T("Import associates"), result=result,
        p1=T("Upload a CSV with a header row. Required columns: associate_id, name. Optional: email, department, location. Existing IDs are updated; progress and passwords are kept. Imported associates then create their password on the Register page using their associate ID."),
        tmpl=T("Download a CSV template"), csrf=csrf_field(req), l_file=T("CSV file"), l_paste=T("...or paste CSV text"),
        btn=T("Import"))
    return layout(req, T("Import associates"), body, "admin")


QUESTION_BANK_COLUMNS = [
    "Question_ID", "Track", "Locale", "Category", "Difficulty", "Pre_or_Post", "Question", "Option_A", "Option_B",
    "Option_C", "Option_D", "Correct_Option", "Rationale", "Microsoft_Source_URL", "Last_Verified_Date",
    "Slide_Reference", "Status",
]


def question_bank_csv(conn, langs=None):
    """The question bank in every language, one row per question and locale."""
    rows = conn.execute(
        """SELECT q.*, m.slug AS module_slug, m.track FROM questions q JOIN modules m ON m.id = q.module_id
           ORDER BY q.code"""
    ).fetchall()
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(QUESTION_BANK_COLUMNS)
    for lang in langs or i18n.CODES:
        for q in rows:
            opts = svc.question_options(q)
            prompt, options, rationale = i18n.question(lang, q["code"], q["prompt"], opts, q["rationale"], bool(q["custom"]))
            options = list(options) + [""] * (4 - len(options))
            w.writerow([
                q["code"], "T1 " + (q["track"] or "core"), lang, q["category"], q["difficulty"],
                "Knowledge check" if q["in_slide_check"] else "Post", prompt, *options[:4], "ABCD"[q["correct_index"]],
                rationale, q["source_url"], content.EDITION_DATE, q["module_slug"], "Active" if q["active"] else "Inactive",
            ])
    return out.getvalue()


def page_admin_questions_csv(req):
    _require_admin(req)
    lang = req.query.get("lang", "")
    data = question_bank_csv(req.conn, [lang] if lang in i18n.CODES else None)
    return ("text/csv; charset=utf-8", ("﻿" + data).encode("utf-8"),
            {"Content-Disposition": 'attachment; filename="question_bank.csv"'})


def page_admin_questions(req):
    _require_admin(req)
    T = req.t
    mods = svc.list_modules(req.conn)
    if req.method == "POST":
        if req.get("action") == "toggle":
            svc.set_question_active(req.conn, int(req.get("id")), req.get("active") == "1")
            redirect("/admin/questions", msg="Question updated.")
        try:
            options = [req.get("opt{}".format(i)) for i in range(4)]
            code = svc.add_custom_question(
                req.conn, int(req.get("module_id")), req.get("prompt"), options, int(req.get("correct", "-1")),
                req.get("rationale"), req.get("category"))
        except ValueError as e:
            redirect("/admin/questions", error=str(e))
        redirect("/admin/questions", msg="Question added.")
    stats = svc.question_stats(req.conn)
    trs = "".join(
        """<tr class="{cls}"><td>{code}</td><td>{prompt}</td><td>{cat}</td><td>{ans}</td><td>{rate}</td>
<td><form method="post" class="inline">{csrf}<input type="hidden" name="action" value="toggle"><input type="hidden" name="id" value="{id}">
<input type="hidden" name="active" value="{next}"><button class="btn small" type="submit">{btn}</button></form></td></tr>""".format(
            cls="" if q["active"] else "inactive", code=esc(q["code"]),
            prompt=esc(q["prompt"] if q["custom"] else _q_prompt(req, q)),
            cat=esc(q["category"]), ans=q["answered"],
            rate="{}%".format(pct(q["correct"] or 0, q["answered"])) if q["answered"] else "-",
            csrf=csrf_field(req), id=q["id"], next="0" if q["active"] else "1", btn=T("Disable") if q["active"] else T("Enable"),
        )
        for q in stats
    )
    mod_opts = "".join('<option value="{}">{}</option>'.format(m["id"], esc(i18n.module(req.lang, m["slug"], "title", m["title"]))) for m in mods)
    lang_links = " ".join('<a href="/admin/questions.csv?lang={}">{}</a>'.format(code, esc(name)) for code, name in i18n.LANGS)
    body = """{nav}<h1>{h1}</h1>
<p>{intro}</p>
<p><a class="btn" href="/admin/questions.csv">{dl}</a> <span class="muted small">{one}: {lang_links}</span></p>
<div class="table-wrap"><table class="grid"><tr><th>ID</th><th>{c1}</th><th>{c2}</th><th>{c3}</th><th>{c4}</th><th></th></tr>{trs}</table></div>
<section class="card"><h2>{h_add}</h2><p class="muted">{add_p}</p>
<form method="post" class="form wide">{csrf}<input type="hidden" name="action" value="add">
<label>{l_mod} <select name="module_id">{mod_opts}</select></label>
<label>{l_cat} <input name="category" value="{cat_v}" maxlength="50"></label>
<label>{l_q} <textarea name="prompt" rows="2" required maxlength="1000"></textarea></label>
<label>{l_a} <input name="opt0" required maxlength="300"></label>
<label>{l_b} <input name="opt1" required maxlength="300"></label>
<label>{l_c} <input name="opt2" maxlength="300"></label>
<label>{l_d} <input name="opt3" maxlength="300"></label>
<label>{l_correct} <select name="correct"><option value="0">A</option><option value="1">B</option><option value="2">C</option><option value="3">D</option></select></label>
<label>{l_rat} <textarea name="rationale" rows="2" required maxlength="1000"></textarea></label>
<button class="btn primary" type="submit">{btn}</button></form></section>""".format(
        nav=admin_nav(req, "questions"), h1=T("Question bank"),
        intro=T("Questions are listed hardest first, by the share of learners who answered correctly. Low rates can mean the topic needs clearer teaching, or the question needs rewording. Disabled questions are not used in quizzes. Built-in questions come from training/content.py; running python app.py reseed re-enables them."),
        dl=T("Download the question bank in all languages (CSV)"), one=T("One language"), lang_links=lang_links,
        c1=T("Question"), c2=T("Category"), c3=T("Answered"), c4=T("Correct"), trs=trs, h_add=T("Add an organization-specific question"),
        add_p=T("Organization questions are shown as written, in every language."), csrf=csrf_field(req),
        l_mod=T("Module"), mod_opts=mod_opts, l_cat=T("Category"), cat_v=esc(T("Organization policy")), l_q=T("Question"),
        l_a=T("Option A"), l_b=T("Option B"), l_c=T("Option C (optional)"), l_d=T("Option D (optional)"),
        l_correct=T("Correct option"), l_rat=T("Explanation shown after answering"), btn=T("Add question"),
    )
    return layout(req, T("Question bank"), body, "admin")


def _q_prompt(req, q):
    return i18n.tr(req.lang, q["prompt"])


def page_admin_feedback(req):
    _require_admin(req)
    T = req.t
    rows = req.conn.execute(
        """SELECT f.*, u.name, u.department FROM feedback f JOIN users u ON u.id = f.user_id
           ORDER BY f.created_at DESC LIMIT 500"""
    ).fetchall()
    dist = {r[0]: r[1] for r in req.conn.execute("SELECT rating, COUNT(*) FROM feedback GROUP BY rating")}
    total = sum(dist.values())
    dist_html = "".join(
        "<tr><td>{} / 5</td><td>{}</td><td>{}</td></tr>".format(
            i, dist.get(i, 0), progress_bar(pct(dist.get(i, 0), total), "{}%".format(pct(dist.get(i, 0), total))))
        for i in range(5, 0, -1)
    )
    trs = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            esc(r["created_at"][:16]), esc(r["name"]), esc(r["department"]), r["rating"], esc(r["comment"]))
        for r in rows
    )
    body = """{nav}<h1>{h1}</h1>
<section class="card"><h2>{h_r}</h2><table class="grid">{dist}</table></section>
<section class="card"><h2>{h_c}</h2><div class="table-wrap"><table class="grid"><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th><th>{c4}</th><th>{c5}</th></tr>{trs}</table></div></section>""".format(
        nav=admin_nav(req, "feedback"), h1=T("Learner feedback"), h_r=T("Ratings ({n})", n=total), dist=dist_html,
        h_c=T("Latest comments"), c1=T("Date"), c2=T("Name"), c3=T("Department"), c4=T("Rating"), c5=T("Comment"),
        trs=trs or '<tr><td colspan="5">{}</td></tr>'.format(T("No feedback yet.")),
    )
    return layout(req, T("Feedback"), body, "admin")


def page_admin_settings(req):
    _require_admin(req)
    T = req.t
    if req.method == "POST":
        pm = req.get("pass_mark")
        if not pm.isdigit() or not 1 <= int(pm) <= 100:
            redirect("/admin/settings", error="Pass mark must be a number from 1 to 100.")
        set_setting(req.conn, "pass_mark", pm)
        if req.get("org_name").strip():
            set_setting(req.conn, "org_name", req.get("org_name").strip()[:100])
        policy = req.get("policy_text").strip()
        set_setting(req.conn, "policy_text", policy[:20000])
        req.conn.commit()
        redirect("/admin/settings", msg="Settings saved.")
    admins = req.conn.execute("SELECT associate_id, name FROM users WHERE role = 'admin' ORDER BY name").fetchall()
    body = """{nav}<h1>{h1}</h1>
<section class="card"><form method="post" class="form wide">{csrf}
<label>{l_org} <input name="org_name" value="{org}" maxlength="100"></label>
<label>{l_pm} <input name="pass_mark" type="number" min="1" max="100" value="{pm}"></label>
<label>{l_policy} <textarea name="policy_text" rows="14" maxlength="20000" placeholder="{ph}">{policy}</textarea></label>
<p class="muted small">{policy_p}</p>
<button class="btn primary" type="submit">{save}</button></form></section>
<section class="card narrow"><h2>{h_admins}</h2><ul>{admins}</ul>
<p class="muted">{admins_p}</p></section>""".format(
        nav=admin_nav(req, "settings"), h1=T("Settings"), csrf=csrf_field(req),
        l_org=T("Organization name (shown in the header and on certificates)"), org=esc(get_setting(req.conn, "org_name") or ""),
        l_pm=T("Pass mark for quizzes and the final assessment (%)"), pm=esc(get_setting(req.conn, "pass_mark") or ""),
        l_policy=T("Acceptable-use guideline shown on the Policy and help page"),
        ph=esc(content.DEFAULT_POLICY[:200]), policy=esc(get_setting(req.conn, "policy_text") or ""),
        policy_p=T("Leave empty to show the built-in guideline, translated into each language. Text you enter here is shown as written."),
        save=T("Save settings"), h_admins=T("Administrators"),
        admins="".join("<li>{} ({})</li>".format(esc(a["name"]), esc(a["associate_id"])) for a in admins),
        admins_p=T("Add more administrators from the command line: python app.py create-admin"),
    )
    return layout(req, T("Settings"), body, "admin")

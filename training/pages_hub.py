"""Agent hub, ideas, community, help, inbox, insights and benchmarks."""

import json

from . import content, hub, i18n, services as svc
from .core import (Raw, HttpError, check, csrf_field, esc, flash_html, layout, lbl, options, pct, progress_bar,
                   redirect, urlencode)
from .db import get_setting, set_setting


def status_badge(req, status):
    cls = {"approved": "ok", "in_review": "prog", "changes": "prog", "rejected": "bad", "retired": "todo"}.get(status, "todo")
    return '<span class="badge {}">{}</span>'.format(cls, esc(lbl(req, "agent_status", content.AGENT_STATUSES, status)))


def tier_short(req, tier):
    return req.t("Tier {n}", n=tier)


def hub_nav(req, active):
    T = req.t
    links = [
        ("overview", "/hub", T("Overview")),
        ("agents", "/hub/agents", T("Agent registry")),
        ("licences", "/hub/licences", T("Licence requests")),
        ("community", "/community", T("Coaches and events")),
        ("prompts", "/community/prompts", T("Prompt library")),
        ("help", "/help", T("Policy and help")),
    ]
    if hub.is_reviewer(req.user):
        links.insert(2, ("reviews", "/hub/reviews", T("Review queue")))
    return '<nav class="subnav" aria-label="{}">{}</nav>'.format(T("Agent hub"), "".join(
        '<a href="{}" class="{}">{}</a>'.format(u, "active" if k == active else "", l) for k, u, l in links))


# ---------------------------------------------------------------------------
# Hub overview and value log
# ---------------------------------------------------------------------------

def page_hub(req):
    T = req.t
    u = req.user
    if req.method == "POST":
        agent_id = req.get("agent_id")
        try:
            hub.log_value(req.conn, u["id"], req.get("hours"), int(agent_id) if agent_id.isdigit() else None, req.get("note"))
        except ValueError as e:
            redirect("/hub", error=str(e))
        redirect("/hub", msg="Thank you. Hours saved this week recorded.")
    levels = hub.builder_levels(req.conn, u)
    mine = hub.list_agents(req.conn, owner_id=u["id"])
    approved = hub.list_agents(req.conn, status="approved", limit=6)
    logs = hub.my_value_logs(req.conn, u["id"])
    agent_opts = '<option value="">{}</option>'.format(T("(general Copilot use)")) + "".join(
        '<option value="{}">{}</option>'.format(a["id"], esc(a["name"])) for a in mine if a["status"] != "retired")
    log_rows = "".join("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(esc(l["week"]), l["hours"], esc(l["note"])) for l in logs)
    steps = [
        (levels["level1"], T("Finish the T1 course and earn your certificate"), "/dashboard"),
        (bool(mine), T("Register the agent you built"), "/hub/agents/new"),
        (any(a["status"] == "approved" for a in mine), T("Get it approved before sharing with a team or the organization"), "/hub/agents"),
        (bool(logs), T("Log the hours it saves each week"), "#value"),
    ]
    step_html = "".join('<li>{} <a href="{}">{}</a></li>'.format(check(req, ok), url, esc(text)) for ok, text, url in steps)
    gallery = "".join(
        '<li><a href="/hub/agents/{}">{}</a> <span class="muted">{} &middot; {}</span></li>'.format(
            a["id"], esc(a["name"]), esc(a["department"] or "-"), esc(a["purpose"][:90]))
        for a in approved
    ) or "<li class='muted'>{}</li>".format(T("No approved agents yet."))
    body = """{nav}<h1>{h1}</h1><p class="lead">{intro}</p>
<section class="grid-2">
<div class="card"><h2>{h_steps}</h2><ul class="checklist">{steps}</ul></div>
<div class="card"><h2>{h_gallery}</h2><p class="muted">{reuse}</p><ul>{gallery}</ul><a href="/hub/agents?view=catalogue">{all}</a></div>
</section>
<section class="card" id="value"><h2>{h_value}</h2><p>{value_intro}</p>
<form method="post" class="filters">{csrf}
<label>{l_hours} <input type="number" name="hours" min="0" max="40" step="0.5" required></label>
<label>{l_agent} <select name="agent_id">{agent_opts}</select></label>
<label>{l_note} <input name="note" maxlength="500" placeholder="{ph}"></label>
<button class="btn primary" type="submit">{save}</button></form>
{log_table}</section>""".format(
        nav=hub_nav(req, "overview"), h1=T("Agent hub"),
        intro=T("The single front door for Copilot agents in our organization: register what you build, get it reviewed, reuse what others built, and show the value."),
        h_steps=T("Your path"), steps=step_html, h_gallery=T("Approved agents you can reuse"),
        reuse=T("Before building, check whether an approved agent already does the job."), gallery=gallery,
        all=T("See the full catalogue"), h_value=T("Hours saved this week"),
        value_intro=T("Leading companies track time saved per person (Vodafone's trial reported about 3 hours a week). One number a week is enough."),
        csrf=csrf_field(req), l_hours=T("Hours saved this week"), l_agent=T("Mainly with"), agent_opts=agent_opts,
        l_note=T("Note (optional)"), ph=T("e.g. faster email drafts"), save=T("Save"),
        log_table="<table class='grid small'><tr><th>{}</th><th>{}</th><th>{}</th></tr>{}</table>".format(
            T("Week"), T("Hours"), T("Note"), log_rows) if log_rows else "",
    )
    return layout(req, T("Agent hub"), body, "hub")


# ---------------------------------------------------------------------------
# Agent registry
# ---------------------------------------------------------------------------

def page_agents(req):
    T = req.t
    view = req.query.get("view", "mine")
    search = req.query.get("q", "")
    dept = req.query.get("department", "")
    if view == "catalogue":
        rows = hub.list_agents(req.conn, status="approved", search=search, department=dept)
    elif view == "all" and hub.is_reviewer(req.user):
        rows = hub.list_agents(req.conn, search=search, department=dept, limit=500)
    else:
        view = "mine"
        rows = hub.list_agents(req.conn, owner_id=req.user["id"], search=search)
    trs = "".join(
        """<tr><td><a href="/hub/agents/{id}">{name}</a></td><td>{purpose}</td><td>{owner}</td><td>{dept}</td>
<td>{tier}</td><td>{scope}</td><td>{status}</td><td>{review}</td></tr>""".format(
            id=a["id"], name=esc(a["name"]), purpose=esc(a["purpose"][:120]), owner=esc(a["owner_name"]),
            dept=esc(a["department"] or "-"), tier=esc(tier_short(req, a["tier"])),
            scope=esc(lbl(req, "scopes", content.SHARING_SCOPES, a["sharing_scope"])),
            status=status_badge(req, a["status"]), review=esc(a["review_date"] or "-"))
        for a in rows
    )
    tabs = [("mine", T("My agents")), ("catalogue", T("Approved catalogue"))]
    if hub.is_reviewer(req.user):
        tabs.append(("all", T("All agents")))
    tab_html = "".join('<a class="btn {}" href="?view={}">{}</a> '.format("primary" if k == view else "", k, l) for k, l in tabs)
    depts = "".join('<option value="{0}"{1}>{0}</option>'.format(esc(d), " selected" if d == dept else "") for d in svc.departments(req.conn))
    body = """{nav}<h1>{h1}</h1><p>{intro}</p>
<p>{tabs} <a class="btn primary" href="/hub/agents/new">+ {new}</a></p>
<form method="get" class="filters"><input type="hidden" name="view" value="{view}">
<label>{l_search} <input name="q" value="{q}"></label>
<label>{l_dept} <select name="department"><option value="">{all}</option>{depts}</select></label>
<button class="btn" type="submit">{filter}</button></form>
<div class="table-wrap"><table class="grid"><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th><th>{c4}</th><th>{c5}</th><th>{c6}</th><th>{c7}</th><th>{c8}</th></tr>{trs}</table></div>""".format(
        nav=hub_nav(req, "agents"), h1=T("Agent registry"),
        intro=T("Every agent shared beyond its owner is registered here with an owner, tier, data sources, one KPI and a review date. Agents that are not registered are not supported."),
        tabs=tab_html, new=T("Register an agent"), view=view, l_search=T("Search"), q=esc(search),
        l_dept=T("Department"), all=T("All"), depts=depts, filter=T("Filter"),
        c1=T("Agent"), c2=T("Purpose"), c3=T("Owner"), c4=T("Department"), c5=T("Tier"), c6=T("Sharing"),
        c7=T("Status"), c8=T("Review date"), trs=trs or '<tr><td colspan="8">{}</td></tr>'.format(T("No agents found.")),
    )
    return layout(req, T("Agent registry"), body, "hub")


def _agent_form(req, a=None, prefill=None):
    T = req.t
    a = dict(a) if a else {}
    pre = prefill or {}

    def v(key, default=""):
        return esc(str(a.get(key, pre.get(key, default)) or ""))
    kinds = (a.get("knowledge_types") or "none").split(",")
    know = "".join(
        '<label class="option inline-opt"><input type="checkbox" name="knowledge_types" value="{k}"{c}> {l}</label>'.format(
            k=k, c=" checked" if k in kinds else "", l=esc(i18n.label(req.lang, "knowledge", k, l)))
        for k, l in content.KNOWLEDGE_TYPES
    )
    ideas = hub.list_ideas(req.conn, req.user["id"], limit=100)
    idea_opts = '<option value="">-</option>' + "".join(
        '<option value="{}"{}>{}</option>'.format(i["id"], " selected" if a.get("idea_id") == i["id"] or str(pre.get("idea_id")) == str(i["id"]) else "", esc(i["title"]))
        for i in ideas)
    return """<form method="post" class="form wide card">{csrf}
<label>{l_name} <input name="name" required maxlength="30" value="{name}"></label>
<label>{l_purpose} <textarea name="purpose" rows="2" required maxlength="1000">{purpose}</textarea></label>
<label>{l_aud} <input name="audience" maxlength="2000" value="{audience}"></label>
<label>{l_tier} <select name="tier">{tiers}</select></label>
<p class="muted small">{tier_help}</p>
<fieldset><legend>{l_know}</legend>{know}</fieldset>
<label>{l_kd} <textarea name="knowledge_detail" rows="2" maxlength="2000">{kd}</textarea></label>
<label>{l_sens} <select name="sensitivity">{sens}</select></label>
<label>{l_scope} <select name="sharing_scope">{scopes}</select></label>
<p class="muted small">{scope_help}</p>
<label>{l_kpi} <input name="kpi_name" maxlength="2000" value="{kpi}" placeholder="{kpi_ph}"></label>
<label>{l_base} <input name="kpi_baseline" maxlength="2000" value="{base}" placeholder="{base_ph}"></label>
<label>{l_tests} <textarea name="test_notes" rows="3" maxlength="2000" placeholder="{tests_ph}">{tests}</textarea></label>
<label>{l_link} <input name="link" maxlength="2000" value="{link}" placeholder="https://"></label>
<label>{l_review} <input type="date" name="review_date" value="{review}"></label>
<label>{l_idea} <select name="idea_id">{idea_opts}</select></label>
<button class="btn primary" type="submit">{btn}</button></form>""".format(
        csrf=csrf_field(req), l_name=T("Agent name (max 30 characters, as in Agent Builder)"), name=v("name"),
        l_purpose=T("One purpose (the agent's description)"), purpose=v("purpose"),
        l_aud=T("Who uses it"), audience=v("audience"),
        l_tier=T("Tier: what can the agent do?"), tiers=options(content.AGENT_TIERS, a.get("tier", "1"), req, "tiers"),
        tier_help=T("Agents built with Agent Builder are Tier 1 or 2. Tier 3 and 4 need Copilot Studio or IT and are reviewed by the CoE."),
        l_know=T("Knowledge sources"), know=know, l_kd=T("Which sources exactly? (names, sites, owners)"), kd=v("knowledge_detail"),
        l_sens=T("Most sensitive data it uses"), sens=options(content.SENSITIVITY_LEVELS, a.get("sensitivity", "internal"), req, "sensitivity"),
        l_scope=T("Who will you share it with?"), scopes=options(content.SHARING_SCOPES, a.get("sharing_scope", "private"), req, "scopes"),
        scope_help=T("Sharing with a team, a group or the organization, or using confidential data, needs a governance review first."),
        l_kpi=T("One KPI: how will you know it helps?"), kpi=v("kpi_name"), kpi_ph=T("e.g. minutes to draft a customer reply"),
        l_base=T("KPI baseline today"), base=v("kpi_baseline"), base_ph=T("e.g. 20 minutes"),
        l_tests=T("Test results (on-topic, vague, off-topic)"), tests=v("test_notes"),
        tests_ph=T("1. On topic: ... 2. Vague: ... 3. Off topic: ..."),
        l_link=T("Agent chat link (Copy chat link in Agent Builder)"), link=v("link"),
        l_review=T("Review date (set to 90 days after approval if empty)"), review=v("review_date"),
        l_idea=T("Built from an idea on the Ideas board?"), idea_opts=idea_opts, btn=T("Save"),
    )


def page_agent_new(req):
    T = req.t
    if req.method == "POST":
        try:
            agent_id = hub.create_agent(req.conn, req.user, req.form, req.getlist("knowledge_types"))
        except ValueError as e:
            redirect("/hub/agents/new", error=str(e))
        redirect("/hub/agents/{}".format(agent_id), msg="Agent registered.")
    prefill = {}
    if req.query.get("from") == "charter":
        data, _ = svc.get_charter(req.conn, req.user["id"])
        prefill = {"name": data.get("agent_name", "")[:30], "purpose": data.get("purpose", ""),
                   "knowledge_detail": data.get("knowledge", ""), "review_date": data.get("review_date", "")}
    if req.query.get("idea", "").isdigit():
        prefill["idea_id"] = int(req.query["idea"])
    body = "{}<h1>{}</h1><p>{}</p>{}".format(
        hub_nav(req, "agents"), T("Register an agent"),
        T("Register agents you built in Agent Builder. Personal agents need no approval; wider sharing needs a governance review."),
        _agent_form(req, prefill=prefill))
    return layout(req, T("Register an agent"), body, "hub")


def page_agent(req, agent_id):
    T = req.t
    a = hub.get_agent(req.conn, int(agent_id))
    if not a:
        raise HttpError(404, "Agent not found.")
    u = req.user
    is_owner = a["owner_id"] == u["id"]
    reviewer = hub.is_reviewer(u)
    if a["status"] != "approved" and not (is_owner or reviewer):
        raise HttpError(403, "This agent is not in the approved catalogue.")
    if req.method == "POST":
        action = req.get("action")
        if action == "edit" and is_owner:
            try:
                status = hub.update_agent(req.conn, a, req.form, req.getlist("knowledge_types"))
            except ValueError as e:
                redirect("/hub/agents/{}?edit=1".format(a["id"]), error=str(e))
            redirect("/hub/agents/{}".format(a["id"]),
                     msg="Saved. Scope or data changed, so the agent needs a new review." if status != a["status"] else "Saved.")
        if action == "submit" and is_owner:
            err = hub.submit_for_review(req.conn, a, u)
            redirect("/hub/agents/{}".format(a["id"]), error=err) if err else redirect("/hub/agents/{}".format(a["id"]), msg="Submitted for review.")
        if action == "review" and reviewer:
            try:
                hub.review_agent(req.conn, a, u, req.get("decision"), req.getlist("checks"), req.get("comment"))
            except ValueError as e:
                redirect("/hub/agents/{}".format(a["id"]), error=str(e))
            redirect("/hub/reviews", msg="Review saved.")
        if action == "value" and is_owner:
            try:
                hub.value_review(req.conn, a, req.get("kpi_result"), req.get("keep") == "1")
            except ValueError as e:
                redirect("/hub/agents/{}".format(a["id"]), error=str(e))
            redirect("/hub/agents/{}".format(a["id"]), msg="Value review saved.")
        if action == "retire" and (is_owner or reviewer):
            hub.retire_agent(req.conn, a)
            redirect("/hub/agents/{}".format(a["id"]), msg="Agent retired.")
        raise HttpError(403, "You cannot do that.")
    if req.query.get("edit") == "1" and is_owner:
        body = "{}<h1>{}</h1>{}".format(hub_nav(req, "agents"), T("Edit agent"), _agent_form(req, a))
        return layout(req, T("Edit agent"), body, "hub")
    kinds = ", ".join(lbl(req, "knowledge", content.KNOWLEDGE_TYPES, k) for k in a["knowledge_types"].split(","))
    needs = hub.needs_review(a["sharing_scope"], a["sensitivity"], a["tier"])
    facts = [
        (T("Owner"), esc(a["owner_name"])), (T("Department"), esc(a["department"] or "-")),
        (T("Who uses it"), esc(a["audience"] or "-")), (T("Tier"), esc(lbl(req, "tiers", content.AGENT_TIERS, a["tier"]))),
        (T("Knowledge sources"), esc(kinds)), (T("Which sources exactly?"), esc(a["knowledge_detail"] or "-")),
        (T("Data sensitivity"), esc(lbl(req, "sensitivity", content.SENSITIVITY_LEVELS, a["sensitivity"]))),
        (T("Sharing"), esc(lbl(req, "scopes", content.SHARING_SCOPES, a["sharing_scope"]))),
        (T("KPI"), esc(a["kpi_name"] or "-")), (T("KPI baseline"), esc(a["kpi_baseline"] or "-")),
        (T("KPI result"), esc(a["kpi_result"] or "-")), (T("Review date"), esc(a["review_date"] or "-")),
        (T("Test results"), "<pre class='plain'>{}</pre>".format(esc(a["test_notes"])) if a["test_notes"] else "-"),
        (T("Chat link"), '<a href="{0}" target="_blank" rel="noopener">{0}</a>'.format(esc(a["link"])) if a["link"] else "-"),
    ]
    if a["idea_id"]:
        facts.append((T("Idea"), '<a href="/hub/ideas/{}">{}</a>'.format(a["idea_id"], T("View the idea"))))
    facts_html = "".join("<dt>{}</dt><dd>{}</dd>".format(k, v) for k, v in facts)
    actions = []
    if is_owner and a["status"] != "retired":
        actions.append('<a class="btn" href="?edit=1">{}</a>'.format(T("Edit")))
        if needs and a["status"] in ("registered", "changes", "rejected"):
            actions.append('<form method="post" class="inline">{}<input type="hidden" name="action" value="submit"><button class="btn primary" type="submit">{}</button></form>'.format(
                csrf_field(req), T("Submit for governance review")))
    if (is_owner or reviewer) and a["status"] != "retired":
        actions.append('<form method="post" class="inline" onsubmit="return confirm(this.dataset.q)" data-q="{}">{}<input type="hidden" name="action" value="retire"><button class="btn danger" type="submit">{}</button></form>'.format(
            esc(T("Retire this agent?")), csrf_field(req), T("Retire")))
    notice = ""
    if needs and a["status"] == "registered":
        notice = '<div class="callout note">{}</div>'.format(T("This agent's sharing scope, data or tier needs a governance review. Do not share it widely until it is approved."))
    elif not needs and a["status"] == "registered":
        notice = '<div class="callout">{}</div>'.format(T("Personal or small-group agent: no review needed. Keep it registered so others can find and reuse it."))
    similar = hub.similar_agents(req.conn, a["name"] + " " + a["purpose"], exclude_id=a["id"])
    sim_html = ""
    if similar:
        sim_html = '<section class="card"><h2>{}</h2><ul>{}</ul></section>'.format(
            T("Similar approved agents"), "".join('<li><a href="/hub/agents/{}">{}</a> ({})</li>'.format(s["id"], esc(s["name"]), esc(s["owner_name"])) for s in similar))
    value_html = ""
    if is_owner and a["status"] == "approved":
        value_html = """<section class="card"><h2>{h}</h2><p>{p}</p>
<form method="post" class="form">{csrf}<input type="hidden" name="action" value="value">
<label>{l} <input name="kpi_result" required maxlength="500" value="{v}"></label>
<label class="option"><input type="radio" name="keep" value="1" checked> {keep}</label>
<label class="option"><input type="radio" name="keep" value="0"> {retire}</label>
<button class="btn primary" type="submit">{btn}</button></form></section>""".format(
            h=T("90-day value review"), p=T("Record the KPI result against the baseline ({base}). Keep agents that deliver; retire the rest.", base=a["kpi_baseline"] or "-"),
            csrf=csrf_field(req), l=T("KPI result now"), v=esc(a["kpi_result"]), keep=T("Keep: it delivers value (next review in 90 days)"),
            retire=T("Retire: it does not deliver enough value"), btn=T("Save value review"))
    review_html = ""
    if reviewer and a["status"] == "in_review" and not is_owner:
        checks = "".join(
            '<label class="option"><input type="checkbox" name="checks" value="{}"> {}</label>'.format(k, esc(i18n.label(req.lang, "checklist", k, t)))
            for k, t in content.GOVERNANCE_CHECKLIST)
        review_html = """<section class="card"><h2>{h}</h2>
<form method="post" class="form">{csrf}<input type="hidden" name="action" value="review">
<fieldset><legend>{l_checks}</legend>{checks}</fieldset>
<label>{l_dec} <select name="decision"><option value="approved">{a}</option><option value="changes">{c}</option><option value="rejected">{r}</option></select></label>
<label>{l_com} <textarea name="comment" rows="3" maxlength="2000"></textarea></label>
<button class="btn primary" type="submit">{btn}</button></form></section>""".format(
            h=T("Governance review"), csrf=csrf_field(req), l_checks=T("Governance checklist (all required to approve)"), checks=checks,
            l_dec=T("Decision"), a=T("Approve"), c=T("Request changes"), r=T("Not approve"), l_com=T("Comment to the owner"),
            btn=T("Save review"))
    history = hub.agent_reviews(req.conn, a["id"])
    hist_html = ""
    if history and (is_owner or reviewer):
        hist_html = '<section class="card"><h2>{}</h2><ul>{}</ul></section>'.format(T("Review history"), "".join(
            "<li><strong>{}</strong> &middot; {} &middot; {}<br>{}</li>".format(
                esc(lbl(req, "agent_status", content.AGENT_STATUSES, h["decision"])), esc(h["reviewer_name"]),
                esc(h["created_at"][:16]), esc(h["comment"]))
            for h in history))
    body = """{nav}<p class="crumbs"><a href="/hub/agents">{reg}</a> &rsaquo; {name}</p>
<h1>{name} {status}</h1><p class="lead">{purpose}</p>{notice}
<p>{actions}</p>
<section class="card"><dl class="facts">{facts}</dl></section>
{review}{value}{similar}{history}""".format(
        nav=hub_nav(req, "agents"), reg=T("Agent registry"), name=esc(a["name"]), status=status_badge(req, a["status"]),
        purpose=esc(a["purpose"]), notice=notice, actions=" ".join(actions), facts=facts_html, review=review_html,
        value=value_html, similar=sim_html, history=hist_html,
    )
    return layout(req, a["name"], body, "hub")


def page_reviews(req):
    T = req.t
    if not hub.is_reviewer(req.user):
        raise HttpError(403, "Coaches and administrators only.")
    waiting = hub.list_agents(req.conn, status="in_review")
    overdue = hub.overdue_agents(req.conn)

    def table(rows, empty):
        trs = "".join(
            "<tr><td><a href='/hub/agents/{}'>{}</a></td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                a["id"], esc(a["name"]), esc(a["owner_name"]), esc(a["department"] or "-"), esc(tier_short(req, a["tier"])),
                esc(lbl(req, "scopes", content.SHARING_SCOPES, a["sharing_scope"])), esc((a["submitted_at"] or a["review_date"] or "")[:10]))
            for a in rows)
        return "<table class='grid'><tr><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr>{}</table>".format(
            T("Agent"), T("Owner"), T("Department"), T("Tier"), T("Sharing"), T("Date"),
            trs or "<tr><td colspan='6'>{}</td></tr>".format(empty))
    body = """{nav}<h1>{h1}</h1>
<section class="card"><h2>{h_wait}</h2>{wait}</section>
<section class="card"><h2>{h_over}</h2><p class="muted">{over_p}</p>{over}</section>""".format(
        nav=hub_nav(req, "reviews"), h1=T("Review queue"), h_wait=T("Waiting for review"), wait=table(waiting, T("Nothing waiting.")),
        h_over=T("Retirement queue: value review overdue"),
        over_p=T("Approved agents past their review date. Ask the owner for the KPI result, then keep or retire."),
        over=table(overdue, T("Nothing overdue.")),
    )
    return layout(req, T("Review queue"), body, "hub")


# ---------------------------------------------------------------------------
# Ideas (use-case intake)
# ---------------------------------------------------------------------------

def page_ideas(req):
    T = req.t
    if req.method == "POST":
        try:
            idea_id = hub.create_idea(req.conn, req.user, req.get("title"), req.get("description"), req.get("category"))
        except ValueError as e:
            redirect("/hub/ideas", error=str(e))
        redirect("/hub/ideas/{}".format(idea_id), msg="Idea posted.")
    cat = req.query.get("category", "")
    status = req.query.get("status", "")
    sort = req.query.get("sort", "votes")
    ideas = hub.list_ideas(req.conn, req.user["id"], cat, status, sort)
    cards = "".join(
        """<li class="idea"><div class="votes"><strong>{votes}</strong><span>{l_votes}</span></div>
<div><a href="/hub/ideas/{id}" class="module-title">{title}</a> <span class="badge todo">{cat}</span> <span class="badge {scls}">{status}</span>
<div class="muted">{desc}</div><div class="muted small">{author} &middot; {dept} &middot; {comments}</div></div></li>""".format(
            votes=i["votes"], l_votes=T("votes"), id=i["id"], title=esc(i["title"]),
            cat=esc(lbl(req, "categories", content.IDEA_CATEGORIES, i["category"])),
            scls="ok" if i["status"] == "built" else "prog" if i["status"] == "planned" else "todo",
            status=esc(lbl(req, "idea_status", content.IDEA_STATUSES, i["status"])), desc=esc(i["description"][:200]),
            author=esc(i["author"]), dept=esc(i["department"] or "-"), comments=T("{n} comments", n=i["comments"]))
        for i in ideas
    )
    body = """<h1>{h1}</h1><p>{intro}</p>
<section class="card"><h2>{h_new}</h2>
<form method="post" class="form wide">{csrf}
<label>{l_title} <input name="title" required maxlength="120"></label>
<label>{l_desc} <textarea name="description" rows="3" required maxlength="2000" placeholder="{ph}"></textarea></label>
<label>{l_cat} <select name="category">{cats}</select></label>
<button class="btn primary" type="submit">{post}</button></form></section>
<form method="get" class="filters">
<label>{l_cat} <select name="category"><option value="">{all}</option>{cat_f}</select></label>
<label>{l_status} <select name="status"><option value="">{all}</option>{status_f}</select></label>
<label>{l_sort} <select name="sort"><option value="votes"{sv}>{most}</option><option value="new"{sn}>{newest}</option></select></label>
<button class="btn" type="submit">{filter}</button></form>
<ul class="ideas">{cards}</ul>""".format(
        h1=T("Ideas board"),
        intro=T("Post a task Copilot could help with, vote for the ideas you want, and turn the best ones into registered agents. Coaches and the CoE use votes to decide what to build next."),
        h_new=T("Share an idea"), csrf=csrf_field(req), l_title=T("Idea"), l_desc=T("What task, for whom, and how much time it takes today"),
        ph=T("e.g. Our team spends 2 hours a week answering the same travel-policy questions."),
        l_cat=T("Category"), cats=options(content.IDEA_CATEGORIES, "", req, "categories"), post=T("Post idea"),
        all=T("All"), cat_f=options(content.IDEA_CATEGORIES, cat, req, "categories"), l_status=T("Status"),
        status_f=options(content.IDEA_STATUSES, status, req, "idea_status"), l_sort=T("Sort"),
        sv=" selected" if sort == "votes" else "", sn=" selected" if sort == "new" else "",
        most=T("Most votes"), newest=T("Newest"), filter=T("Filter"),
        cards=cards or "<li class='muted'>{}</li>".format(T("No ideas yet. Be the first!")),
    )
    return layout(req, T("Ideas board"), body, "ideas")


def page_idea(req, idea_id):
    T = req.t
    i = hub.get_idea(req.conn, int(idea_id), req.user["id"])
    if not i:
        raise HttpError(404, "Idea not found.")
    if req.method == "POST":
        action = req.get("action")
        if action == "vote":
            hub.toggle_vote(req.conn, i["id"], req.user["id"])
        elif action == "comment":
            try:
                hub.add_comment(req.conn, i, req.user, req.get("body"))
            except ValueError as e:
                redirect("/hub/ideas/{}".format(i["id"]), error=str(e))
        elif action == "status" and hub.is_reviewer(req.user):
            hub.set_idea_status(req.conn, i["id"], req.get("status"))
        redirect("/hub/ideas/{}".format(i["id"]))
    comments = "".join(
        "<li><strong>{}</strong> <span class='muted small'>{}</span><br>{}</li>".format(esc(c["author"]), esc(c["created_at"][:16]), esc(c["body"]))
        for c in hub.idea_comments(req.conn, i["id"]))
    agents = "".join('<li><a href="/hub/agents/{}">{}</a></li>'.format(a["id"], esc(a["name"])) for a in hub.idea_agents(req.conn, i["id"]))
    status_form = ""
    if hub.is_reviewer(req.user):
        status_form = '<form method="post" class="filters">{}<input type="hidden" name="action" value="status"><label>{} <select name="status">{}</select></label><button class="btn" type="submit">{}</button></form>'.format(
            csrf_field(req), T("Status"), options(content.IDEA_STATUSES, i["status"], req, "idea_status"), T("Save"))
    body = """<p class="crumbs"><a href="/hub/ideas">{board}</a></p>
<h1>{title}</h1>
<p><span class="badge todo">{cat}</span> <span class="badge prog">{status}</span> <span class="muted">{author} &middot; {dept} &middot; {date}</span></p>
<section class="card"><p>{desc}</p>
<form method="post" class="inline">{csrf}<input type="hidden" name="action" value="vote"><button class="btn {vcls}" type="submit">&#9650; {vlabel} ({votes})</button></form>
<a class="btn" href="/hub/agents/new?idea={id}">{build}</a></section>
{status_form}
<section class="card"><h2>{h_agents}</h2><ul>{agents}</ul></section>
<section class="card"><h2>{h_com}</h2><ul class="comments">{comments}</ul>
<form method="post" class="form">{csrf}<input type="hidden" name="action" value="comment">
<label>{l_com} <textarea name="body" rows="2" required maxlength="2000"></textarea></label>
<button class="btn" type="submit">{post}</button></form></section>""".format(
        board=T("Ideas board"), title=esc(i["title"]), cat=esc(lbl(req, "categories", content.IDEA_CATEGORIES, i["category"])),
        status=esc(lbl(req, "idea_status", content.IDEA_STATUSES, i["status"])), author=esc(i["author"]),
        dept=esc(i["department"] or "-"), date=esc(i["created_at"][:10]), desc=esc(i["description"]),
        csrf=csrf_field(req), vcls="primary" if i["my_vote"] else "", vlabel=T("Voted") if i["my_vote"] else T("Vote"),
        votes=i["votes"], id=i["id"], build=T("I built an agent for this"), status_form=status_form,
        h_agents=T("Agents built from this idea"), agents=agents or "<li class='muted'>{}</li>".format(T("None yet.")),
        h_com=T("Comments"), comments=comments, l_com=T("Add a comment"), post=T("Post"),
    )
    return layout(req, i["title"], body, "ideas")


# ---------------------------------------------------------------------------
# Licence requests
# ---------------------------------------------------------------------------

LICENCE_STATUSES = [("pending", "Pending"), ("approved", "Approved"), ("declined", "Declined")]


def page_licences(req):
    T = req.t
    admin = req.user["role"] == "admin"
    if req.method == "POST":
        try:
            if req.get("action") == "decide" and admin:
                hub.decide_licence(req.conn, int(req.get("id")), req.get("decision") == "approve", req.get("wave"), req.get("note"))
            else:
                hub.create_licence_request(req.conn, req.user, req.get("seats"), req.get("use_case"), req.get("expected_hours"))
        except ValueError as e:
            redirect("/hub/licences", error=str(e))
        redirect("/hub/licences", msg="Saved.")
    rows = hub.licence_requests(req.conn, None if admin else req.user["id"])
    trs = []
    for r in rows:
        decide = ""
        if admin and r["status"] == "pending":
            decide = """<form method="post" class="filters">{csrf}<input type="hidden" name="action" value="decide"><input type="hidden" name="id" value="{id}">
<input name="wave" placeholder="{wave}" maxlength="50" size="8"><input name="note" placeholder="{note}" maxlength="1000">
<button class="btn small primary" name="decision" value="approve" type="submit">{a}</button>
<button class="btn small" name="decision" value="decline" type="submit">{d}</button></form>""".format(
                csrf=csrf_field(req), id=r["id"], wave=T("Wave"), note=T("Note"), a=T("Approve"), d=T("Decline"))
        trs.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            esc(r["created_at"][:10]), esc(r["requester"]), esc(r["department"] or "-"), r["seats"], esc(r["use_case"]),
            r["expected_hours"], esc(lbl(req, "licence_status", LICENCE_STATUSES, r["status"]))
            + (" ({})".format(esc(r["wave"])) if r["wave"] else ""), decide or esc(r["decision_note"])))
    body = """{nav}<h1>{h1}</h1><p>{intro}</p>
<section class="card"><h2>{h_new}</h2><form method="post" class="form wide">{csrf}
<label>{l_seats} <input type="number" name="seats" min="1" max="5000" required></label>
<label>{l_use} <textarea name="use_case" rows="3" required maxlength="2000"></textarea></label>
<label>{l_hours} <input type="number" name="expected_hours" min="0" max="40" step="0.5"></label>
<button class="btn primary" type="submit">{btn}</button></form></section>
<div class="table-wrap"><table class="grid"><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th><th>{c4}</th><th>{c5}</th><th>{c6}</th><th>{c7}</th><th></th></tr>{trs}</table></div>""".format(
        nav=hub_nav(req, "licences"), h1=T("Licence requests"),
        intro=T("Everyone starts with Copilot Chat. Full Microsoft 365 Copilot licences are given in waves to teams that complete training and show a use case, as Lloyds did. Requests with the most expected value are listed first."),
        h_new=T("Request licences for your team"), csrf=csrf_field(req), l_seats=T("Seats needed"),
        l_use=T("Use case: what will people do with Copilot?"), l_hours=T("Expected hours saved per person per week"),
        btn=T("Send request"), c1=T("Date"), c2=T("Requested by"), c3=T("Department"), c4=T("Seats"), c5=T("Use case"),
        c6=T("Hours/week"), c7=T("Status"),
        trs="".join(trs) or "<tr><td colspan='8'>{}</td></tr>".format(T("No requests yet.")),
    )
    return layout(req, T("Licence requests"), body, "hub")


# ---------------------------------------------------------------------------
# Community: coaches, events, prompts
# ---------------------------------------------------------------------------

def page_community(req):
    T = req.t
    can_host = hub.is_reviewer(req.user)
    if req.method == "POST":
        if req.get("action") == "signup":
            hub.toggle_signup(req.conn, int(req.get("id")), req.user["id"])
            redirect("/community")
        if can_host:
            try:
                hub.create_event(req.conn, req.user, req.get("kind"), req.get("title"), req.get("starts_at"),
                                 req.get("place"), req.get("details"))
            except ValueError as e:
                redirect("/community", error=str(e))
            redirect("/community", msg="Event added.")
        raise HttpError(403, "Coaches and administrators only.")
    dept = req.query.get("department", "")
    coach_rows = "".join("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
        esc(c["name"]), esc(c["department"] or "-"), esc(c["email"] or "-"), esc(c["office_hours"] or "-"))
        for c in hub.coaches(req.conn, dept))
    events = "".join(
        """<li class="event"><div class="date">{date}</div><div><strong>{title}</strong> <span class="badge todo">{kind}</span>
<div class="muted">{place} &middot; {host} &middot; {n}</div><div>{details}</div>
<form method="post" class="inline">{csrf}<input type="hidden" name="action" value="signup"><input type="hidden" name="id" value="{id}">
<button class="btn small {cls}" type="submit">{btn}</button></form></div></li>""".format(
            date=esc(e["starts_at"].replace("T", " ")), title=esc(e["title"]), kind=esc(lbl(req, "event_kinds", content.EVENT_KINDS, e["kind"])),
            place=esc(e["place"] or "-"), host=esc(e["host"]), n=T("{n} joining", n=e["signups"]), details=esc(e["details"]),
            csrf=csrf_field(req), id=e["id"], cls="primary" if e["joined"] else "", btn=T("Joined") if e["joined"] else T("Join"))
        for e in hub.upcoming_events(req.conn, req.user["id"]))
    host_form = ""
    if can_host:
        host_form = """<section class="card"><h2>{h}</h2><form method="post" class="form wide">{csrf}
<label>{l_kind} <select name="kind">{kinds}</select></label>
<label>{l_title} <input name="title" required maxlength="120"></label>
<label>{l_when} <input type="datetime-local" name="starts_at" required></label>
<label>{l_place} <input name="place" maxlength="200"></label>
<label>{l_details} <textarea name="details" rows="2" maxlength="2000"></textarea></label>
<button class="btn primary" type="submit">{btn}</button></form></section>""".format(
            h=T("Add an event"), csrf=csrf_field(req), l_kind=T("Type"), kinds=options(content.EVENT_KINDS, "", req, "event_kinds"),
            l_title=T("Title"), l_when=T("Date and time"), l_place=T("Where (room or Teams link)"), l_details=T("Details"), btn=T("Add event"))
    depts = "".join('<option value="{0}"{1}>{0}</option>'.format(esc(d), " selected" if d == dept else "") for d in svc.departments(req.conn))
    m = hub.adoption_metrics(req.conn)
    target = max(1, round((m["associates"] or 1) / 60))
    body = """{nav}<h1>{h1}</h1><p>{intro}</p>
<section class="card"><h2>{h_events}</h2><ul class="events">{events}</ul></section>
{host_form}
<section class="card"><h2>{h_coaches}</h2><p class="muted">{ratio}</p>
<form method="get" class="filters"><label>{l_dept} <select name="department"><option value="">{all}</option>{depts}</select></label><button class="btn" type="submit">{filter}</button></form>
<table class="grid"><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th><th>{c4}</th></tr>{coaches}</table></section>""".format(
        nav=hub_nav(req, "community"), h1=T("Coaches and events"),
        intro=T("Peer coaching is how leaders scale: Lloyds trained 10,000+ colleagues through 1,000 volunteer coaches. Find a coach in your department or join a promptathon."),
        h_events=T("Upcoming events"), events=events or "<li class='muted'>{}</li>".format(T("No upcoming events.")),
        host_form=host_form, h_coaches=T("Coach directory"),
        ratio=T("{n} coaches today; target about {target} (1 per 60 associates).", n=m["coaches"], target=target),
        l_dept=T("Department"), all=T("All"), depts=depts, filter=T("Filter"),
        c1=T("Name"), c2=T("Department"), c3=T("Email"), c4=T("Office hours"),
        coaches=coach_rows or "<tr><td colspan='4'>{}</td></tr>".format(T("No coaches yet.")),
    )
    return layout(req, T("Coaches and events"), body, "hub")


def page_prompts(req):
    T = req.t
    if req.method == "POST":
        try:
            if req.get("action") == "rate":
                hub.rate_prompt(req.conn, int(req.get("id")), req.user["id"], int(req.get("rating") or 0))
            else:
                hub.add_prompt(req.conn, req.user, req.get("title"), req.get("body"), req.get("category"))
        except ValueError as e:
            redirect("/community/prompts", error=str(e))
        redirect("/community/prompts", msg="Saved.")
    cat = req.query.get("category", "")
    search = req.query.get("q", "")
    from . import blocks
    items = []
    for p in hub.list_prompts(req.conn, req.user["id"], cat, search):
        stars = "".join(
            '<button class="star{}" name="rating" value="{}" type="submit" aria-label="{}">&#9733;</button>'.format(
                " on" if p["my_rating"] and n <= p["my_rating"] else "", n, T("Rate {n} of 5", n=n))
            for n in range(1, 6))
        items.append("""<section class="card prompt"><h3>{title} <span class="badge todo">{cat}</span></h3>
<div class="muted small">{author} &middot; {avg}</div>{block}
<form method="post" class="inline stars">{csrf}<input type="hidden" name="action" value="rate"><input type="hidden" name="id" value="{id}">{stars}</form></section>""".format(
            title=esc(p["title"]), cat=esc(lbl(req, "categories", content.IDEA_CATEGORIES, p["category"])), author=esc(p["author"]),
            avg=T("Rated {avg} from {n} ratings", avg=round(p["avg_rating"], 1), n=p["ratings"]) if p["ratings"] else T("Not rated yet"),
            block=blocks.copy(p["body"]), csrf=csrf_field(req), id=p["id"], stars=stars))
    body = """{nav}<h1>{h1}</h1><p>{intro}</p>
<form method="get" class="filters"><label>{l_search} <input name="q" value="{q}"></label>
<label>{l_cat} <select name="category"><option value="">{all}</option>{cats}</select></label><button class="btn" type="submit">{filter}</button></form>
{items}
<section class="card"><h2>{h_add}</h2><form method="post" class="form wide">{csrf}
<label>{l_title} <input name="title" required maxlength="120"></label>
<label>{l_body} <textarea name="body" rows="4" required maxlength="4000"></textarea></label>
<label>{l_cat} <select name="category">{cats2}</select></label>
<button class="btn primary" type="submit">{btn}</button></form></section>""".format(
        nav=hub_nav(req, "prompts"), h1=T("Prompt library"),
        intro=T("Prompts that work for colleagues, rated by the community. Never include confidential data in a shared prompt."),
        l_search=T("Search"), q=esc(search), l_cat=T("Category"), all=T("All"), cats=options(content.IDEA_CATEGORIES, cat, req, "categories"),
        filter=T("Filter"), items="".join(items) or "<p class='muted'>{}</p>".format(T("No prompts yet.")),
        h_add=T("Share a prompt"), csrf=csrf_field(req), l_title=T("Title"), l_body=T("Prompt text"),
        cats2=options(content.IDEA_CATEGORIES, "", req, "categories"), btn=T("Share prompt"),
    )
    return layout(req, T("Prompt library"), body, "hub")


# ---------------------------------------------------------------------------
# Policy and help
# ---------------------------------------------------------------------------

def page_help(req):
    T = req.t
    reviewer = hub.is_reviewer(req.user)
    if req.method == "POST":
        try:
            if req.get("action") == "answer" and reviewer:
                hub.answer_coe(req.conn, int(req.get("id")), req.user, req.get("answer"))
            else:
                hub.ask_coe(req.conn, req.user, req.get("topic"), req.get("question"))
        except ValueError as e:
            redirect("/help", error=str(e))
        redirect("/help", msg="Sent.")
    policy = get_setting(req.conn, "policy_text") or i18n.block(req.lang, "DEFAULT_POLICY", content.DEFAULT_POLICY)
    sens = "".join("<tr><td>{}</td><td>{}</td></tr>".format(
        esc(lbl(req, "sensitivity", content.SENSITIVITY_LEVELS, k)),
        esc(i18n.label(req.lang, "sensitivity_rule", k, SENS_RULES[k]))) for k, _ in content.SENSITIVITY_LEVELS)
    qs = hub.coe_questions(req.conn) if reviewer else hub.coe_questions(req.conn, req.user["id"])
    q_html = []
    for q in qs:
        answer = ""
        if q["answer"]:
            answer = "<div class='answer'><strong>{}</strong> {}</div>".format(esc(q["answerer"] or ""), esc(q["answer"]))
        elif reviewer and (q["topic"] in ("howto",) or req.user["role"] == "admin"):
            answer = """<form method="post" class="form">{}<input type="hidden" name="action" value="answer"><input type="hidden" name="id" value="{}">
<textarea name="answer" rows="2" required maxlength="3000"></textarea><button class="btn small primary" type="submit">{}</button></form>""".format(
                csrf_field(req), q["id"], T("Answer"))
        else:
            answer = "<div class='muted'>{}</div>".format(T("Waiting for an answer."))
        q_html.append("<li id='q{}'><span class='badge todo'>{}</span> <strong>{}</strong> <span class='muted small'>{}</span><p>{}</p>{}</li>".format(
            q["id"], esc(lbl(req, "topics", content.QUESTION_TOPICS, q["topic"])), esc(q["asker"]), esc(q["created_at"][:16]),
            esc(q["question"]), answer))
    body = """{nav}<h1>{h1}</h1>
<section class="card"><h2>{h_policy}</h2><pre class="plain policy">{policy}</pre></section>
<section class="card"><h2>{h_data}</h2><table class="grid"><tr><th>{c1}</th><th>{c2}</th></tr>{sens}</table></section>
<section class="card"><h2>{h_ask}</h2><p>{ask_p}</p>
<form method="post" class="form wide">{csrf}<label>{l_topic} <select name="topic">{topics}</select></label>
<label>{l_q} <textarea name="question" rows="3" required maxlength="3000"></textarea></label>
<button class="btn primary" type="submit">{send}</button></form></section>
<section class="card"><h2>{h_qs}</h2><ul class="questions">{qs}</ul></section>""".format(
        nav=hub_nav(req, "help"), h1=T("Policy and help"), h_policy=T("Acceptable-use guideline"), policy=esc(policy),
        h_data=T("Data rules"), c1=T("Data"), c2=T("Rule"), sens=sens, h_ask=T("Ask the CoE"),
        ask_p=T("Coaches answer how-to questions. Policy, data, licence and incident questions go to the CoE (administrators). Report any suspected data exposure straight away."),
        csrf=csrf_field(req), l_topic=T("Topic"), topics=options(content.QUESTION_TOPICS, "howto", req, "topics"),
        l_q=T("Your question"), send=T("Send"), h_qs=T("All questions") if reviewer else T("My questions"),
        qs="".join(q_html) or "<li class='muted'>{}</li>".format(T("No questions yet.")),
    )
    return layout(req, T("Policy and help"), body, "toolkit")


SENS_RULES = {
    "public": "Fine for any agent and any sharing scope.",
    "internal": "Fine for registered agents; share only with people who need it.",
    "confidential": "Needs a governance review and approved sources; never paste it into prompts.",
}


# ---------------------------------------------------------------------------
# Inbox
# ---------------------------------------------------------------------------

def page_inbox(req):
    T = req.t
    rows = hub.notifications(req.conn, req.user["id"])
    items = []
    for n in rows:
        params = json.loads(n["params_json"] or "{}")
        text = req.t(n["message"], **params)
        items.append('<li class="{}"><a href="{}">{}</a> <span class="muted small">{}</span></li>'.format(
            "" if n["is_read"] else "unread", esc(n["link"] or "#"), text, esc(n["created_at"][:16])))
    hub.mark_all_read(req.conn, req.user["id"])
    body = "<h1>{}</h1><ul class='inbox'>{}</ul>".format(
        T("Notifications"), "".join(items) or "<li class='muted'>{}</li>".format(T("Nothing new.")))
    return layout(req, T("Notifications"), body)


# ---------------------------------------------------------------------------
# Insights: adoption dashboard and benchmarks
# ---------------------------------------------------------------------------

def insights_nav(req, active):
    T = req.t
    links = [("dashboard", "/insights", T("Adoption dashboard")), ("benchmarks", "/insights/benchmarks", T("Benchmarks"))]
    return '<nav class="subnav">{}</nav>'.format("".join(
        '<a href="{}" class="{}">{}</a>'.format(u, "active" if k == active else "", l) for k, u, l in links))


def bar_chart(rows, keys, labels):
    """A small accessible bar chart as an HTML table."""
    peak = max([r[k] for r in rows for k in keys] + [1])
    out = []
    for r in rows:
        cells = "".join(
            '<td><div class="hbar s{}" style="width:{}%"></div><span>{}</span></td>'.format(i, round(100 * r[k] / peak), r[k])
            for i, k in enumerate(keys))
        out.append("<tr><th>{}</th>{}</tr>".format(esc(r["month"]), cells))
    head = "".join("<th>{}</th>".format(esc(l)) for l in labels)
    return "<table class='chart'><tr><th></th>{}</tr>{}</table>".format(head, "".join(out))


def page_insights(req):
    T = req.t
    m = hub.adoption_metrics(req.conn)
    n = m["associates"] or 1
    tiles = [
        (m["associates"], T("Associates")),
        ("{}%".format(pct(m["certified"], n)), T("Certified (T1)")),
        ("{}%".format(m["monthly_active_pct"]), T("Signed in during the last 30 days")),
        (m["agents_total"], T("Registered agents")),
        (m["by_status"].get("approved", 0), T("Approved for sharing")),
        (m["in_review"], T("Waiting for review")),
        ("{}".format(m["hours_avg"]) if m["hours_avg"] is not None else "-", T("Average hours saved per week (last 4 weeks)")),
        (m["coaches"], T("Copilot coaches")),
        (m["ideas_total"], T("Ideas posted")),
        ("{} / {}".format(m["licences_approved"], m["licences_pending"]), T("Licence seats approved / pending")),
        ("{} d".format(m["turnaround_days"]) if m["turnaround_days"] is not None else "-", T("Average review turnaround")),
        (m["overdue"], T("Agents overdue for value review")),
    ]
    tile_html = "".join('<div class="stat"><div class="num">{}</div><div>{}</div></div>'.format(v, esc(l)) for v, l in tiles)
    tiers = "".join("<tr><td>{}</td><td>{}</td></tr>".format(esc(lbl(req, "tiers", content.AGENT_TIERS, k)), v) for k, v in m["tiers"].items())
    dept_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}%</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            esc(name), d["associates"], pct(d["certified"], d["associates"]), d["builders"], d["approved"], d["ideas"],
            progress_bar(d["score"], "{}/100".format(d["score"])))
        for name, d in m["departments"])
    body = """{nav}<h1>{h1}</h1><p>{intro}</p>
<section class="grid-4">{tiles}</section>
<section class="card"><h2>{h_trend}</h2>{chart}</section>
<section class="grid-2"><div class="card"><h2>{h_tiers}</h2><table class="grid">{tiers}</table></div>
<div class="card"><h2>{h_funnel}</h2><table class="grid">{funnel}</table></div></section>
<section class="card"><h2>{h_dept}</h2><p class="muted small">{index}</p>
<div class="table-wrap"><table class="grid"><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th><th>{c4}</th><th>{c5}</th><th>{c6}</th><th>{c7}</th></tr>{depts}</table></div></section>""".format(
        nav=insights_nav(req, "dashboard"), h1=T("Adoption dashboard"),
        intro=T("One view across training, agents, ideas and value. Compare with the benchmark targets on the Benchmarks tab."),
        tiles=tile_html, h_trend=T("Last 6 months"),
        chart=bar_chart(m["trend"], ["certified", "agents"], [T("Newly certified"), T("Agents registered")]),
        h_tiers=T("Agents by tier"), tiers=tiers, h_funnel=T("Agents by status"),
        funnel="".join("<tr><td>{}</td><td>{}</td></tr>".format(esc(lbl(req, "agent_status", content.AGENT_STATUSES, k)), v) for k, v in m["by_status"].items()),
        h_dept=T("By department"),
        index=T("Adoption index (course design, not a Microsoft metric): 40% trained, 30% building agents, 20% approved shared agents, 10% ideas."),
        c1=T("Department"), c2=T("Associates"), c3=T("Certified"), c4=T("Builders"), c5=T("Approved agents"), c6=T("Ideas"),
        c7=T("Adoption index"), depts=dept_rows or "<tr><td colspan='7'>-</td></tr>",
    )
    return layout(req, T("Adoption dashboard"), body, "insights")


def page_benchmarks(req):
    T = req.t
    m = hub.adoption_metrics(req.conn)
    actual = hub.benchmark_actuals(req.conn, m)
    rows = []
    for b in content.BENCHMARKS:
        def f(key):
            return esc(i18n.tr(req.lang, b[key]))
        srcs = " ".join('<a href="{}" target="_blank" rel="noopener">[{}]</a>'.format(content.BENCHMARK_SOURCES[s][1], s) for s in b["sources"])
        rows.append("<tr><td><strong>{}</strong><br><span class='muted small'>{}</span></td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            esc(b["company"]), f("region"), f("scale"), f("platform"), f("governance"), f("skilling"), f("result"), srcs))
    copies = "".join("<li><strong>{}:</strong> {}</li>".format(esc(b["company"]), esc(i18n.tr(req.lang, b["copy"])))
                     for b in content.BENCHMARKS)
    habits = i18n.block(req.lang, "BENCHMARK_HABITS", content.BENCHMARK_HABITS)
    habits_html = "".join("<div class='card'><h3>{}</h3><p>{}</p></div>".format(esc(h), esc(d)) for h, d in habits)
    targets = []
    for key, name, target, basis in content.BENCHMARK_TARGETS:
        cur = actual.get(key)
        if cur is None:
            now_txt, bar = "-", ""
        else:
            val, goal = cur
            now_txt = "-" if val is None else ("{}%" if key in ("monthly_active", "kpi") else "{}").format(val)
            bar = progress_bar(min(100, pct(val or 0, goal)), T("{n}% of target", n=min(100, pct(val or 0, goal)))) if goal else ""
        targets.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td class='muted small'>{}</td></tr>".format(
            esc(i18n.label(req.lang, "target_name", key, name)), esc(i18n.label(req.lang, "target_value", key, target)),
            now_txt, bar, esc(i18n.label(req.lang, "target_basis", key, basis))))
    roadmap = i18n.block(req.lang, "BENCHMARK_ROADMAP", content.BENCHMARK_ROADMAP)
    road_html = "".join("<div class='card'><h3>{}</h3><p><strong>{}</strong></p><ul>{}</ul><p class='muted'>{}</p></div>".format(
        esc(a), esc(b), "".join("<li>{}</li>".format(esc(x)) for x in items), esc(g)) for a, b, items, g in roadmap)
    zones = "".join("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(*[esc(x) for x in z])
                    for z in i18n.block(req.lang, "ZONES", content.ZONES))
    sources = "".join('<li>[{}] <a href="{}" target="_blank" rel="noopener">{}</a></li>'.format(k, v[1], esc(v[0])) for k, v in content.BENCHMARK_SOURCES.items())
    body = """{nav}<h1>{h1}</h1><p>{intro}</p>
<div class="callout note">{trust}</div>
<section class="card"><h2>{h_targets}</h2><p class="muted">{t_intro}</p>
<div class="table-wrap"><table class="grid"><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th><th>{c4}</th><th>{c5}</th></tr>{targets}</table></div></section>
<h2>{h_habits}</h2><div class="grid-3">{habits}</div>
<section class="card"><h2>{h_copy}</h2><ul>{copies}</ul></section>
<section class="card"><h2>{h_table}</h2><div class="table-wrap"><table class="grid small"><tr><th>{k1}</th><th>{k2}</th><th>{k3}</th><th>{k4}</th><th>{k5}</th><th>{k6}</th><th>{k7}</th></tr>{rows}</table></div></section>
<section class="card"><h2>{h_zones}</h2><table class="grid small"><tr><th>{z1}</th><th>{z2}</th><th>{z3}</th><th>{z4}</th></tr>{zones}</table></section>
<h2>{h_road}</h2><div class="grid-4 roadmap">{road}</div>
<section class="card"><h2>{h_src}</h2><ol class="small sources-list">{sources}</ol></section>""".format(
        nav=insights_nav(req, "benchmarks"), h1=T("Benchmarks: how leading companies adopt Copilot and agents"),
        intro=T("Toyota, Siemens, Hitachi, Rabobank and five comparable enterprises: what they did, and what an organization of our size should copy. Research date: {date}.", date=content.BENCHMARK_DATE),
        trust=T("Most results are company- or vendor-reported and not independently audited. Usage counts do not prove productivity. Targets are planning assumptions derived from the cited ratios."),
        h_targets=T("Our progress against benchmark targets"), t_intro=T("Live numbers from this hub, compared with targets scaled to our number of associates."),
        c1=T("Measure"), c2=T("Target"), c3=T("Today"), c4=T("Progress"), c5=T("Basis"), targets="".join(targets),
        h_habits=T("Six habits the leaders share"), habits=habits_html, h_copy=T("What to copy from each"), copies=copies,
        h_table=T("What each company did"), k1=T("Company"), k2=T("Scale"), k3=T("Platform and agents"), k4=T("Governance"),
        k5=T("Skilling"), k6=T("Published result"), k7=T("Sources"), rows="".join(rows),
        h_zones=T("Microsoft's governance zones"), z1=T("Zone"), z2=T("Who builds"), z3=T("Tools"), z4=T("Purpose"), zones=zones,
        h_road=T("12-month roadmap"), road=road_html, h_src=T("Sources"), sources=sources,
    )
    return layout(req, T("Benchmarks"), body, "insights")

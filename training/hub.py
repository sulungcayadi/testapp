"""Agent hub: registry, governance review, ideas, notifications and
organization-wide adoption metrics."""

import json
import re
from datetime import date, datetime, timedelta, timezone

from . import content, services as svc
from .db import now

SCOPES = [k for k, _ in content.SHARING_SCOPES]
SENSITIVITY = [k for k, _ in content.SENSITIVITY_LEVELS]
KNOWLEDGE = [k for k, _ in content.KNOWLEDGE_TYPES]
CHECKLIST = [k for k, _ in content.GOVERNANCE_CHECKLIST]
CATEGORIES = [k for k, _ in content.IDEA_CATEGORIES]
IDEA_STATUSES = [k for k, _ in content.IDEA_STATUSES]


# ---------------------------------------------------------------------------
# Notifications. Messages are stored as English UI strings with {params}
# and translated when shown.
# ---------------------------------------------------------------------------

def notify(conn, user_id, message, link="", **params):
    conn.execute(
        "INSERT INTO notifications(user_id, message, params_json, link, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, message, json.dumps(params), link, now()),
    )


def notifications(conn, user_id, limit=50):
    return conn.execute(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit)
    ).fetchall()


def unread_count(conn, user_id):
    return conn.execute(
        "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,)
    ).fetchone()[0]


def mark_all_read(conn, user_id):
    conn.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    conn.commit()


def reviewers(conn):
    return conn.execute(
        "SELECT * FROM users WHERE is_reviewer = 1 OR role = 'admin' ORDER BY department, name"
    ).fetchall()


def is_reviewer(user):
    return bool(user and (user["role"] == "admin" or user["is_reviewer"]))


# ---------------------------------------------------------------------------
# Agent registry
# ---------------------------------------------------------------------------

AGENT_FIELDS = ["name", "purpose", "audience", "knowledge_detail", "test_notes", "link", "review_date",
                "kpi_name", "kpi_baseline"]
TIERS = [k for k, _ in content.AGENT_TIERS]


def needs_review(scope, sensitivity, tier="1"):
    return scope in content.REVIEW_REQUIRED_SCOPES or sensitivity == "confidential" or tier in content.COE_ONLY_TIERS


def clean_agent(form, knowledge_list):
    data = {k: (form.get(k) or "").strip() for k in AGENT_FIELDS}
    data["name"] = data["name"][:30]
    data["purpose"] = data["purpose"][:1000]
    for k in ("audience", "knowledge_detail", "test_notes", "link", "kpi_name", "kpi_baseline"):
        data[k] = data[k][:2000]
    tier = form.get("tier") or "1"
    if tier not in TIERS:
        raise ValueError("Choose the agent's tier.")
    data["tier"] = tier
    if not data["name"] or not data["purpose"]:
        raise ValueError("Agent name and purpose are required.")
    if data["link"] and not re.match(r"^https://", data["link"]):
        raise ValueError("The agent link must start with https://")
    if data["review_date"]:
        try:
            date.fromisoformat(data["review_date"])
        except ValueError:
            raise ValueError("Review date must look like 2027-01-31.")
    scope = form.get("sharing_scope") or "private"
    sensitivity = form.get("sensitivity") or "internal"
    if scope not in SCOPES or sensitivity not in SENSITIVITY:
        raise ValueError("Choose a sharing scope and data sensitivity.")
    kinds = [k for k in knowledge_list if k in KNOWLEDGE] or ["none"]
    if "none" in kinds and len(kinds) > 1:
        kinds.remove("none")
    data.update(sharing_scope=scope, sensitivity=sensitivity, knowledge_types=",".join(kinds))
    idea = form.get("idea_id") or ""
    data["idea_id"] = int(idea) if idea.isdigit() else None
    return data


def create_agent(conn, owner, form, knowledge_list):
    data = clean_agent(form, knowledge_list)
    cur = conn.execute(
        """INSERT INTO agents(owner_id, name, purpose, department, audience, knowledge_types, knowledge_detail,
               sensitivity, sharing_scope, test_notes, link, status, review_date, tier, kpi_name, kpi_baseline,
               idea_id, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'registered', ?, ?, ?, ?, ?, ?, ?)""",
        (owner["id"], data["name"], data["purpose"], owner["department"], data["audience"], data["knowledge_types"],
         data["knowledge_detail"], data["sensitivity"], data["sharing_scope"], data["test_notes"], data["link"],
         data["review_date"], data["tier"], data["kpi_name"], data["kpi_baseline"], data["idea_id"], now(), now()),
    )
    conn.commit()
    return cur.lastrowid


def update_agent(conn, agent, form, knowledge_list):
    data = clean_agent(form, knowledge_list)
    status = agent["status"]
    # Changing an approved agent's scope or data means it must be reviewed again.
    if status == "approved" and (
        data["sharing_scope"] != agent["sharing_scope"] or data["sensitivity"] != agent["sensitivity"]
        or data["knowledge_types"] != agent["knowledge_types"] or data["tier"] != agent["tier"]
    ):
        status = "registered"
    conn.execute(
        """UPDATE agents SET name=?, purpose=?, audience=?, knowledge_types=?, knowledge_detail=?, sensitivity=?,
               sharing_scope=?, test_notes=?, link=?, review_date=?, tier=?, kpi_name=?, kpi_baseline=?, idea_id=?,
               status=?, updated_at=? WHERE id=?""",
        (data["name"], data["purpose"], data["audience"], data["knowledge_types"], data["knowledge_detail"],
         data["sensitivity"], data["sharing_scope"], data["test_notes"], data["link"], data["review_date"],
         data["tier"], data["kpi_name"], data["kpi_baseline"], data["idea_id"], status, now(), agent["id"]),
    )
    conn.commit()
    return status


def get_agent(conn, agent_id):
    return conn.execute(
        """SELECT a.*, u.name AS owner_name, u.associate_id AS owner_aid
           FROM agents a JOIN users u ON u.id = a.owner_id WHERE a.id = ?""",
        (agent_id,),
    ).fetchone()


def list_agents(conn, owner_id=None, status=None, search="", department="", limit=200):
    sql = """SELECT a.*, u.name AS owner_name FROM agents a JOIN users u ON u.id = a.owner_id WHERE 1 = 1"""
    args = []
    if owner_id is not None:
        sql += " AND a.owner_id = ?"
        args.append(owner_id)
    if status:
        if isinstance(status, (list, tuple, set)):
            sql += " AND a.status IN ({})".format(",".join("?" * len(status)))
            args.extend(status)
        else:
            sql += " AND a.status = ?"
            args.append(status)
    if search:
        sql += " AND (a.name LIKE ? OR a.purpose LIKE ?)"
        args += ["%" + search + "%"] * 2
    if department:
        sql += " AND a.department = ?"
        args.append(department)
    sql += " ORDER BY a.updated_at DESC LIMIT ?"
    args.append(limit)
    return conn.execute(sql, args).fetchall()


STOPWORDS = {"the", "and", "for", "with", "that", "this", "helps", "help", "agent", "from", "into", "your", "my", "our", "me"}


def similar_agents(conn, text, exclude_id=None, limit=5):
    """Approved agents that look like they do the same job, so people reuse
    instead of duplicating."""
    words = {w for w in re.findall(r"[a-z0-9]{4,}", (text or "").lower()) if w not in STOPWORDS}
    if not words:
        return []
    scored = []
    for a in conn.execute(
        "SELECT a.*, u.name AS owner_name FROM agents a JOIN users u ON u.id = a.owner_id WHERE a.status = 'approved'"
    ):
        if a["id"] == exclude_id:
            continue
        theirs = set(re.findall(r"[a-z0-9]{4,}", (a["name"] + " " + a["purpose"]).lower()))
        overlap = len(words & theirs)
        if overlap >= 2:
            scored.append((overlap, a))
    scored.sort(key=lambda x: -x[0])
    return [a for _, a in scored[:limit]]


def submit_for_review(conn, agent, owner):
    """Returns None on success, or an English error message."""
    prog = svc.user_progress(conn, owner["id"])
    if not prog["certified"]:
        return "Complete the T1 training (certificate) before you submit an agent for wider sharing."
    if not agent["test_notes"].strip():
        return "Add your test results (on-topic, vague and off-topic) before submitting."
    if not agent["kpi_name"].strip() or not agent["kpi_baseline"].strip():
        return "Declare one KPI and its baseline before submitting."
    if agent["status"] not in ("registered", "changes", "rejected"):
        return "This agent is already in review or approved."
    conn.execute(
        "UPDATE agents SET status = 'in_review', submitted_at = ?, updated_at = ? WHERE id = ?",
        (now(), now(), agent["id"]),
    )
    coe_only = agent["tier"] in content.COE_ONLY_TIERS
    for r in reviewers(conn):
        if coe_only and r["role"] != "admin":
            continue
        if r["id"] != owner["id"]:
            notify(conn, r["id"], "New agent waiting for review: {name}", "/hub/agents/{}".format(agent["id"]),
                   name=agent["name"])
    conn.commit()
    return None


def review_agent(conn, agent, reviewer, decision, checked, comment):
    if decision not in ("approved", "changes", "rejected"):
        raise ValueError("Choose a decision.")
    if agent["status"] != "in_review":
        raise ValueError("This agent is not waiting for review.")
    if agent["owner_id"] == reviewer["id"]:
        raise ValueError("You cannot review your own agent.")
    if agent["tier"] in content.COE_ONLY_TIERS and reviewer["role"] != "admin":
        raise ValueError("Tier 3 and 4 agents are reviewed by the CoE (administrators).")
    checked = [c for c in checked if c in CHECKLIST]
    if decision == "approved" and len(set(checked)) < len(CHECKLIST):
        raise ValueError("Every governance check must be ticked before approving.")
    if decision != "approved" and not comment.strip():
        raise ValueError("Explain what needs to change.")
    conn.execute(
        "INSERT INTO agent_reviews(agent_id, reviewer_id, decision, checklist_json, comment, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (agent["id"], reviewer["id"], decision, json.dumps(sorted(set(checked))), comment.strip()[:2000], now()),
    )
    conn.execute(
        "UPDATE agents SET status = ?, decided_at = ?, updated_at = ? WHERE id = ?",
        (decision, now(), now(), agent["id"]),
    )
    if decision == "approved":
        # Every shared agent gets a value review 90 days after approval unless an earlier date is set.
        due = (date.today() + timedelta(days=90)).isoformat()
        if not agent["review_date"] or agent["review_date"] > due:
            conn.execute("UPDATE agents SET review_date = ? WHERE id = ?", (due, agent["id"]))
    messages = {
        "approved": "Your agent {name} was approved for sharing.",
        "changes": "Changes were requested for your agent {name}.",
        "rejected": "Your agent {name} was not approved.",
    }
    notify(conn, agent["owner_id"], messages[decision], "/hub/agents/{}".format(agent["id"]), name=agent["name"])
    if decision == "approved" and agent["idea_id"]:
        conn.execute("UPDATE ideas SET status = 'built' WHERE id = ?", (agent["idea_id"],))
        idea = conn.execute("SELECT * FROM ideas WHERE id = ?", (agent["idea_id"],)).fetchone()
        if idea and idea["user_id"] != agent["owner_id"]:
            notify(conn, idea["user_id"], "Your idea {title} now has an approved agent.",
                   "/hub/agents/{}".format(agent["id"]), title=idea["title"])
    conn.commit()


def value_review(conn, agent, kpi_result, keep):
    """The owner records the KPI result. Keeping the agent sets the next review
    in 90 days; otherwise it is retired."""
    kpi_result = kpi_result.strip()[:500]
    if not kpi_result:
        raise ValueError("Enter the KPI result.")
    nxt = (date.today() + timedelta(days=90)).isoformat()
    status = agent["status"] if keep else "retired"
    conn.execute(
        "UPDATE agents SET kpi_result = ?, value_reviewed_at = ?, review_date = ?, status = ?, updated_at = ? WHERE id = ?",
        (kpi_result, now(), nxt if keep else agent["review_date"], status, now(), agent["id"]),
    )
    conn.commit()


def retire_agent(conn, agent):
    conn.execute("UPDATE agents SET status = 'retired', updated_at = ? WHERE id = ?", (now(), agent["id"]))
    conn.commit()


def agent_reviews(conn, agent_id):
    return conn.execute(
        """SELECT r.*, u.name AS reviewer_name FROM agent_reviews r JOIN users u ON u.id = r.reviewer_id
           WHERE r.agent_id = ? ORDER BY r.id DESC""",
        (agent_id,),
    ).fetchall()


def overdue_agents(conn, today=None):
    today = today or date.today().isoformat()
    return conn.execute(
        """SELECT a.*, u.name AS owner_name FROM agents a JOIN users u ON u.id = a.owner_id
           WHERE a.status = 'approved' AND a.review_date != '' AND a.review_date < ? ORDER BY a.review_date""",
        (today,),
    ).fetchall()


# ---------------------------------------------------------------------------
# Ideas and community
# ---------------------------------------------------------------------------

def create_idea(conn, user, title, description, category):
    title, description = title.strip()[:120], description.strip()[:2000]
    if not title or not description:
        raise ValueError("Idea title and description are required.")
    if category not in CATEGORIES:
        category = "other"
    cur = conn.execute(
        "INSERT INTO ideas(user_id, title, description, category, department, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user["id"], title, description, category, user["department"], now()),
    )
    conn.execute("INSERT INTO idea_votes(idea_id, user_id) VALUES (?, ?)", (cur.lastrowid, user["id"]))
    conn.commit()
    return cur.lastrowid


def list_ideas(conn, user_id, category="", status="", sort="votes", limit=200):
    sql = """SELECT i.*, u.name AS author,
                (SELECT COUNT(*) FROM idea_votes v WHERE v.idea_id = i.id) AS votes,
                (SELECT COUNT(*) FROM idea_comments c WHERE c.idea_id = i.id) AS comments,
                EXISTS(SELECT 1 FROM idea_votes v WHERE v.idea_id = i.id AND v.user_id = ?) AS my_vote
             FROM ideas i JOIN users u ON u.id = i.user_id WHERE 1 = 1"""
    args = [user_id]
    if category:
        sql += " AND i.category = ?"
        args.append(category)
    if status:
        sql += " AND i.status = ?"
        args.append(status)
    sql += " ORDER BY votes DESC, i.id DESC" if sort == "votes" else " ORDER BY i.id DESC"
    sql += " LIMIT ?"
    args.append(limit)
    return conn.execute(sql, args).fetchall()


def get_idea(conn, idea_id, user_id):
    rows = conn.execute(
        """SELECT i.*, u.name AS author,
              (SELECT COUNT(*) FROM idea_votes v WHERE v.idea_id = i.id) AS votes,
              EXISTS(SELECT 1 FROM idea_votes v WHERE v.idea_id = i.id AND v.user_id = ?) AS my_vote
           FROM ideas i JOIN users u ON u.id = i.user_id WHERE i.id = ?""",
        (user_id, idea_id),
    ).fetchone()
    return rows


def toggle_vote(conn, idea_id, user_id):
    if conn.execute("SELECT 1 FROM idea_votes WHERE idea_id = ? AND user_id = ?", (idea_id, user_id)).fetchone():
        conn.execute("DELETE FROM idea_votes WHERE idea_id = ? AND user_id = ?", (idea_id, user_id))
    else:
        conn.execute("INSERT INTO idea_votes(idea_id, user_id) VALUES (?, ?)", (idea_id, user_id))
    conn.commit()


def add_comment(conn, idea, user, body):
    body = body.strip()[:2000]
    if not body:
        raise ValueError("Write a comment first.")
    conn.execute(
        "INSERT INTO idea_comments(idea_id, user_id, body, created_at) VALUES (?, ?, ?, ?)",
        (idea["id"], user["id"], body, now()),
    )
    if idea["user_id"] != user["id"]:
        notify(conn, idea["user_id"], "{name} commented on your idea {title}.", "/hub/ideas/{}".format(idea["id"]),
               name=user["name"], title=idea["title"])
    conn.commit()


def idea_comments(conn, idea_id):
    return conn.execute(
        """SELECT c.*, u.name AS author FROM idea_comments c JOIN users u ON u.id = c.user_id
           WHERE c.idea_id = ? ORDER BY c.id""",
        (idea_id,),
    ).fetchall()


def set_idea_status(conn, idea_id, status):
    if status in IDEA_STATUSES:
        conn.execute("UPDATE ideas SET status = ? WHERE id = ?", (status, idea_id))
        conn.commit()


def idea_agents(conn, idea_id):
    return conn.execute("SELECT * FROM agents WHERE idea_id = ? ORDER BY id", (idea_id,)).fetchall()


# ---------------------------------------------------------------------------
# Adoption metrics across training, agents and ideas
# ---------------------------------------------------------------------------

def _days_between(a, b):
    fmt = "%Y-%m-%d %H:%M:%S"
    return (datetime.strptime(b, fmt) - datetime.strptime(a, fmt)).total_seconds() / 86400


def adoption_metrics(conn):
    learners, total = svc.learner_rows(conn)
    certified = {r["id"] for r in learners if r["status"] == "Certified"}
    agents = conn.execute("SELECT a.*, u.department AS owner_dept FROM agents a JOIN users u ON u.id = a.owner_id").fetchall()
    by_status = {k: 0 for k, _ in content.AGENT_STATUSES}
    for a in agents:
        by_status[a["status"]] = by_status.get(a["status"], 0) + 1
    builders = {a["owner_id"] for a in agents if a["status"] != "retired"}
    ideas = conn.execute("SELECT * FROM ideas").fetchall()
    idea_status = {k: 0 for k in IDEA_STATUSES}
    for i in ideas:
        idea_status[i["status"]] = idea_status.get(i["status"], 0) + 1
    decided = conn.execute(
        "SELECT submitted_at, decided_at FROM agents WHERE submitted_at IS NOT NULL AND decided_at IS NOT NULL AND decided_at >= submitted_at"
    ).fetchall()
    turnaround = round(sum(_days_between(r[0], r[1]) for r in decided) / len(decided), 1) if decided else None
    in_review = conn.execute(
        "SELECT COUNT(*) FROM agents WHERE status = 'in_review'"
    ).fetchone()[0]

    depts = {}
    for r in learners:
        d = depts.setdefault(r["department"] or "-", {"associates": 0, "certified": 0, "builders": 0, "agents": 0, "approved": 0, "ideas": 0})
        d["associates"] += 1
        if r["id"] in certified:
            d["certified"] += 1
        if r["id"] in builders:
            d["builders"] += 1
    for a in agents:
        if a["status"] == "retired":
            continue
        d = depts.setdefault(a["owner_dept"] or "-", {"associates": 0, "certified": 0, "builders": 0, "agents": 0, "approved": 0, "ideas": 0})
        d["agents"] += 1
        if a["status"] == "approved":
            d["approved"] += 1
    for i in ideas:
        d = depts.setdefault(i["department"] or "-", {"associates": 0, "certified": 0, "builders": 0, "agents": 0, "approved": 0, "ideas": 0})
        d["ideas"] += 1
    for d in depts.values():
        d["score"] = maturity_score(d)

    # Monthly trend for the last 6 months: certifications and agents registered.
    trend = []
    today = date.today().replace(day=1)
    months = []
    y, m = today.year, today.month
    for _ in range(6):
        months.append("{:04d}-{:02d}".format(y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    months.reverse()
    cert_by_month = {}
    for row in conn.execute(
        """SELECT user_id, MIN(completed_at) AS first_pass FROM quiz_attempts
           WHERE kind = 'final' AND passed = 1 GROUP BY user_id"""
    ):
        if row["user_id"] in certified:
            key = row["first_pass"][:7]
            cert_by_month[key] = cert_by_month.get(key, 0) + 1
    agents_by_month = {}
    for a in agents:
        key = a["created_at"][:7]
        agents_by_month[key] = agents_by_month.get(key, 0) + 1
    for mo in months:
        trend.append({"month": mo, "certified": cert_by_month.get(mo, 0), "agents": agents_by_month.get(mo, 0)})

    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    monthly_active = conn.execute(
        "SELECT COUNT(*) FROM users WHERE role = 'learner' AND last_login >= ?", (month_ago,)
    ).fetchone()[0]
    four_weeks = [this_week(date.today() - timedelta(weeks=i)) for i in range(4)]
    hrs = conn.execute(
        "SELECT AVG(hours), COUNT(DISTINCT user_id), SUM(hours) FROM value_logs WHERE week IN ({})".format(",".join("?" * 4)),
        four_weeks,
    ).fetchone()
    tiers = {k: 0 for k in TIERS}
    for a in agents:
        if a["status"] != "retired":
            tiers[a["tier"]] = tiers.get(a["tier"], 0) + 1
    licences = conn.execute(
        "SELECT COALESCE(SUM(CASE WHEN status = 'approved' THEN seats END), 0), COALESCE(SUM(CASE WHEN status = 'pending' THEN seats END), 0) FROM licence_requests"
    ).fetchone()
    return {
        "monthly_active": monthly_active,
        "monthly_active_pct": round(100 * monthly_active / total) if total else 0,
        "hours_avg": round(hrs[0], 1) if hrs[0] is not None else None,
        "hours_reporters": hrs[1],
        "hours_total_4w": round(hrs[2] or 0),
        "tiers": tiers,
        "coaches": conn.execute("SELECT COUNT(*) FROM users WHERE is_reviewer = 1").fetchone()[0],
        "licences_approved": licences[0],
        "licences_pending": licences[1],
        "with_kpi": sum(1 for a in agents if a["status"] == "approved" and a["kpi_name"]),
        "associates": total,
        "certified": len(certified),
        "builders": len(builders),
        "agents_total": sum(by_status.values()) - by_status.get("retired", 0),
        "by_status": by_status,
        "ideas_total": len(ideas),
        "idea_status": idea_status,
        "turnaround_days": turnaround,
        "in_review": in_review,
        "overdue": len(overdue_agents(conn)),
        "departments": sorted(depts.items(), key=lambda kv: -kv[1]["score"]),
        "trend": trend,
    }


def maturity_score(d):
    """0-100 adoption index for a department. Course design, not a Microsoft
    metric: 40% trained, 30% building, 20% sharing approved agents, 10% ideas."""
    n = d["associates"] or 1
    trained = min(1.0, d["certified"] / n)
    building = min(1.0, d["builders"] / n / 0.2)  # target: 20% of associates build an agent
    approved = min(1.0, d["approved"] / max(1.0, n / 50))  # target: 1 shared agent per 50 people
    ideas = min(1.0, d["ideas"] / max(1.0, n / 20))  # target: 1 idea per 20 people
    return round(100 * (0.4 * trained + 0.3 * building + 0.2 * approved + 0.1 * ideas))


# ---------------------------------------------------------------------------
# Learning paths and builder levels
# ---------------------------------------------------------------------------

FOUNDATION_MODULES = ("welcome", "basics", "safety")


def builder_levels(conn, user):
    """Which levels the user has reached, in order (see content.BUILDER_LEVELS)."""
    uid = user["id"]
    done = svc.completed_lesson_ids(conn, uid)
    passed = svc.passed_module_ids(conn, uid)
    foundation = True
    for slug in FOUNDATION_MODULES:
        m = svc.get_module(conn, slug)
        if not m:
            continue
        lessons = svc.module_lessons(conn, m["id"])
        if any(l["id"] not in done for l in lessons):
            foundation = False
        if svc.module_questions(conn, m["id"]) and m["id"] not in passed:
            foundation = False
    prog = svc.user_progress(conn, uid)
    level1 = prog["certified"]
    approved = conn.execute(
        "SELECT COUNT(*) FROM agents WHERE owner_id = ? AND status = 'approved'", (uid,)
    ).fetchone()[0]
    reviewed = conn.execute(
        "SELECT COUNT(*) FROM agents WHERE owner_id = ? AND value_reviewed_at IS NOT NULL AND kpi_result != ''", (uid,)
    ).fetchone()[0]
    level2 = level1 and approved > 0
    level3 = level2 and reviewed > 0
    return {"foundation": foundation, "level1": level1, "level2": level2, "level3": level3,
            "coach": bool(user["is_reviewer"]), "progress": prog}


def track_progress(conn, user_id, track):
    mods = svc.list_modules(conn, track)
    done = svc.completed_lesson_ids(conn, user_id)
    total = n = 0
    for m in mods:
        for l in svc.module_lessons(conn, m["id"]):
            total += 1
            n += l["id"] in done
    return n, total, mods


def save_assessment(conn, user_id, answers):
    keys = [k for k, _ in content.SKILL_STATEMENTS]
    clean = {k: int(answers.get(k)) for k in keys if str(answers.get(k, "")) in ("1", "2", "3", "4")}
    if len(clean) != len(keys):
        raise ValueError("Answer every statement.")
    conn.execute(
        """INSERT INTO skill_assessments(user_id, answers_json, updated_at) VALUES (?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET answers_json = excluded.answers_json, updated_at = excluded.updated_at""",
        (user_id, json.dumps(clean), now()),
    )
    conn.commit()
    return clean


def get_assessment(conn, user_id):
    row = conn.execute("SELECT * FROM skill_assessments WHERE user_id = ?", (user_id,)).fetchone()
    return json.loads(row["answers_json"]) if row else None


# Which module to recommend for each weak skill.
SKILL_MODULES = {
    "chat": "basics", "purpose": "plan", "build": "build", "test": "test",
    "safety": "safety", "value": "leader", "lead": "leader",
}


def recommendations(answers):
    """Module slugs to study next, weakest skills first."""
    if not answers:
        return []
    weak = sorted((v, k) for k, v in answers.items() if v <= 2)
    out = []
    for _, k in weak:
        slug = SKILL_MODULES.get(k)
        if slug and slug not in out:
            out.append(slug)
    return out


# ---------------------------------------------------------------------------
# Licence requests (allocated in waves)
# ---------------------------------------------------------------------------

def create_licence_request(conn, user, seats, use_case, expected_hours):
    try:
        seats = int(seats)
        expected_hours = float(expected_hours or 0)
    except ValueError:
        raise ValueError("Seats and hours must be numbers.")
    if not 1 <= seats <= 5000:
        raise ValueError("Request between 1 and 5,000 seats.")
    if not use_case.strip():
        raise ValueError("Describe the use case.")
    conn.execute(
        """INSERT INTO licence_requests(user_id, department, seats, use_case, expected_hours, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user["id"], user["department"], seats, use_case.strip()[:2000], max(0.0, expected_hours), now()),
    )
    conn.commit()


def licence_requests(conn, user_id=None):
    sql = """SELECT r.*, u.name AS requester FROM licence_requests r JOIN users u ON u.id = r.user_id"""
    args = []
    if user_id is not None:
        sql += " WHERE r.user_id = ?"
        args.append(user_id)
    sql += " ORDER BY CASE r.status WHEN 'pending' THEN 0 ELSE 1 END, r.expected_hours * r.seats DESC, r.id DESC"
    return conn.execute(sql, args).fetchall()


def decide_licence(conn, request_id, approve, wave, note):
    row = conn.execute("SELECT * FROM licence_requests WHERE id = ?", (request_id,)).fetchone()
    if not row or row["status"] != "pending":
        raise ValueError("This request has already been decided.")
    status = "approved" if approve else "declined"
    conn.execute(
        "UPDATE licence_requests SET status = ?, wave = ?, decision_note = ?, decided_at = ? WHERE id = ?",
        (status, wave.strip()[:50], note.strip()[:1000], now(), request_id),
    )
    notify(conn, row["user_id"],
           "Your licence request for {seats} seats was approved (wave {wave})." if approve
           else "Your licence request for {seats} seats was declined.",
           "/hub/licences", seats=row["seats"], wave=wave.strip() or "-")
    conn.commit()


# ---------------------------------------------------------------------------
# Community: coaches, events, prompt library
# ---------------------------------------------------------------------------

def coaches(conn, department=""):
    sql = "SELECT * FROM users WHERE is_reviewer = 1"
    args = []
    if department:
        sql += " AND department = ?"
        args.append(department)
    return conn.execute(sql + " ORDER BY department, name", args).fetchall()


EVENT_KINDS = [k for k, _ in content.EVENT_KINDS]


def create_event(conn, user, kind, title, starts_at, place, details):
    if kind not in EVENT_KINDS:
        raise ValueError("Choose an event type.")
    title = title.strip()[:120]
    try:
        datetime.strptime(starts_at.strip(), "%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValueError("Enter a valid date and time.")
    if not title:
        raise ValueError("Give the event a title.")
    conn.execute(
        "INSERT INTO events(created_by, kind, title, starts_at, place, details, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user["id"], kind, title, starts_at.strip(), place.strip()[:200], details.strip()[:2000], now()),
    )
    conn.commit()


def upcoming_events(conn, user_id, limit=50):
    today = datetime.now().strftime("%Y-%m-%dT00:00")
    return conn.execute(
        """SELECT e.*, u.name AS host,
              (SELECT COUNT(*) FROM event_signups s WHERE s.event_id = e.id) AS signups,
              EXISTS(SELECT 1 FROM event_signups s WHERE s.event_id = e.id AND s.user_id = ?) AS joined
           FROM events e JOIN users u ON u.id = e.created_by WHERE e.starts_at >= ? ORDER BY e.starts_at LIMIT ?""",
        (user_id, today, limit),
    ).fetchall()


def toggle_signup(conn, event_id, user_id):
    if conn.execute("SELECT 1 FROM event_signups WHERE event_id = ? AND user_id = ?", (event_id, user_id)).fetchone():
        conn.execute("DELETE FROM event_signups WHERE event_id = ? AND user_id = ?", (event_id, user_id))
    else:
        conn.execute("INSERT INTO event_signups(event_id, user_id) VALUES (?, ?)", (event_id, user_id))
    conn.commit()


def add_prompt(conn, user, title, body, category):
    title, body = title.strip()[:120], body.strip()[:4000]
    if not title or not body:
        raise ValueError("Give the prompt a title and text.")
    if category not in CATEGORIES:
        category = "other"
    conn.execute(
        "INSERT INTO prompts(user_id, title, body, category, created_at) VALUES (?, ?, ?, ?, ?)",
        (user["id"], title, body, category, now()),
    )
    conn.commit()


def list_prompts(conn, user_id, category="", search=""):
    sql = """SELECT p.*, u.name AS author,
                (SELECT AVG(rating) FROM prompt_ratings r WHERE r.prompt_id = p.id) AS avg_rating,
                (SELECT COUNT(*) FROM prompt_ratings r WHERE r.prompt_id = p.id) AS ratings,
                (SELECT rating FROM prompt_ratings r WHERE r.prompt_id = p.id AND r.user_id = ?) AS my_rating
             FROM prompts p JOIN users u ON u.id = p.user_id WHERE 1 = 1"""
    args = [user_id]
    if category:
        sql += " AND p.category = ?"
        args.append(category)
    if search:
        sql += " AND (p.title LIKE ? OR p.body LIKE ?)"
        args += ["%" + search + "%"] * 2
    sql += " ORDER BY COALESCE(avg_rating, 0) DESC, ratings DESC, p.id DESC LIMIT 200"
    return conn.execute(sql, args).fetchall()


def rate_prompt(conn, prompt_id, user_id, rating):
    if rating not in (1, 2, 3, 4, 5):
        raise ValueError("Rate from 1 to 5.")
    conn.execute(
        """INSERT INTO prompt_ratings(prompt_id, user_id, rating) VALUES (?, ?, ?)
           ON CONFLICT(prompt_id, user_id) DO UPDATE SET rating = excluded.rating""",
        (prompt_id, user_id, rating),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Ask the CoE
# ---------------------------------------------------------------------------

TOPICS = [k for k, _ in content.QUESTION_TOPICS]


def ask_coe(conn, user, topic, question):
    if topic not in TOPICS:
        topic = "howto"
    question = question.strip()[:3000]
    if not question:
        raise ValueError("Write your question first.")
    cur = conn.execute(
        "INSERT INTO coe_questions(user_id, topic, question, created_at) VALUES (?, ?, ?, ?)",
        (user["id"], topic, question, now()),
    )
    for r in reviewers(conn):
        if topic in ("data", "incident", "policy", "licence") and r["role"] != "admin":
            continue
        if r["id"] != user["id"]:
            notify(conn, r["id"], "New question for the CoE from {name}.", "/help#q{}".format(cur.lastrowid), name=user["name"])
    conn.commit()


def coe_questions(conn, user_id=None, open_only=False):
    sql = """SELECT q.*, u.name AS asker, a.name AS answerer FROM coe_questions q
             JOIN users u ON u.id = q.user_id LEFT JOIN users a ON a.id = q.answered_by WHERE 1 = 1"""
    args = []
    if user_id is not None:
        sql += " AND q.user_id = ?"
        args.append(user_id)
    if open_only:
        sql += " AND q.answer = ''"
    return conn.execute(sql + " ORDER BY q.id DESC LIMIT 200", args).fetchall()


def answer_coe(conn, question_id, answerer, answer):
    answer = answer.strip()[:3000]
    if not answer:
        raise ValueError("Write an answer first.")
    q = conn.execute("SELECT * FROM coe_questions WHERE id = ?", (question_id,)).fetchone()
    if not q:
        raise ValueError("Question not found.")
    conn.execute(
        "UPDATE coe_questions SET answer = ?, answered_by = ?, answered_at = ? WHERE id = ?",
        (answer, answerer["id"], now(), question_id),
    )
    notify(conn, q["user_id"], "Your question to the CoE was answered.", "/help#q{}".format(question_id))
    conn.commit()


# ---------------------------------------------------------------------------
# Value logging (hours saved per week)
# ---------------------------------------------------------------------------

def this_week(today=None):
    y, w, _ = (today or date.today()).isocalendar()
    return "{:04d}-W{:02d}".format(y, w)


def log_value(conn, user_id, hours, agent_id=None, note=""):
    try:
        hours = float(hours)
    except ValueError:
        raise ValueError("Hours must be a number.")
    if not 0 <= hours <= 40:
        raise ValueError("Enter between 0 and 40 hours.")
    conn.execute(
        """INSERT INTO value_logs(user_id, week, hours, agent_id, note, created_at) VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(user_id, week) DO UPDATE SET hours = excluded.hours, agent_id = excluded.agent_id,
           note = excluded.note""",
        (user_id, this_week(), hours, agent_id, note.strip()[:500], now()),
    )
    conn.commit()


def my_value_logs(conn, user_id):
    return conn.execute("SELECT * FROM value_logs WHERE user_id = ? ORDER BY week DESC LIMIT 12", (user_id,)).fetchall()


def benchmark_actuals(conn, metrics):
    """Live values for content.BENCHMARK_TARGETS."""
    n = metrics["associates"] or 1
    shared = conn.execute(
        "SELECT COUNT(*), SUM(kpi_name != '') FROM agents WHERE status = 'approved'"
    ).fetchone()
    return {
        "coaches": (metrics["coaches"], max(1, round(n / 60))),
        "builders": (metrics["certified"], round(n * 0.10)),
        "monthly_active": (metrics["monthly_active_pct"], 55),
        "hours": (metrics["hours_avg"], 3),
        "kpi": (pct_or_none(shared[1] or 0, shared[0]), 100),
    }


def pct_or_none(a, b):
    return round(100 * a / b) if b else None

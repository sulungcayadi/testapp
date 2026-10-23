"""Business logic: accounts, progress, quizzes, lab, charters and reports.

Everything here takes an open sqlite3 connection so it can be used by the web
server, the command line and the tests alike.
"""

import csv
import hashlib
import hmac
import io
import json
import random
import secrets
from datetime import datetime, timedelta, timezone

from . import content
from .db import get_setting, now

SESSION_HOURS = 12
PBKDF2_ROUNDS = 200_000


# ---------------------------------------------------------------------------
# Passwords and sessions
# ---------------------------------------------------------------------------

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ROUNDS).hex()
    return "pbkdf2${}${}${}".format(PBKDF2_ROUNDS, salt, digest)


def verify_password(password, stored):
    if not stored:
        return False
    try:
        _, rounds, salt, digest = stored.split("$")
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds)).hex()
    return hmac.compare_digest(check, digest)


def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters."
    return None


def create_session(conn, user_id):
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(24)
    expires = (datetime.now(timezone.utc) + timedelta(hours=SESSION_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("DELETE FROM sessions WHERE expires_at < ?", (now(),))
    conn.execute(
        "INSERT INTO sessions(token, user_id, csrf, expires_at) VALUES (?, ?, ?, ?)",
        (token, user_id, csrf, expires),
    )
    conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now(), user_id))
    conn.commit()
    return token


def session_user(conn, token):
    if not token:
        return None, None
    row = conn.execute(
        """SELECT u.*, s.csrf FROM sessions s JOIN users u ON u.id = s.user_id
           WHERE s.token = ? AND s.expires_at > ?""",
        (token, now()),
    ).fetchone()
    if not row:
        return None, None
    return row, row["csrf"]


def end_session(conn, token):
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def admin_exists(conn):
    return conn.execute("SELECT 1 FROM users WHERE role = 'admin' LIMIT 1").fetchone() is not None


def get_user_by_associate_id(conn, associate_id):
    return conn.execute("SELECT * FROM users WHERE associate_id = ?", (associate_id.strip(),)).fetchone()


def create_user(conn, associate_id, name, password=None, role="learner", email="", department="", location=""):
    associate_id = associate_id.strip()
    if not associate_id or not name.strip():
        raise ValueError("Associate ID and name are required.")
    conn.execute(
        """INSERT INTO users(associate_id, name, email, department, location, role, password_hash, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (associate_id, name.strip(), email.strip(), department.strip(), location.strip(), role,
         hash_password(password) if password else None, now()),
    )
    conn.commit()
    return get_user_by_associate_id(conn, associate_id)


def register(conn, associate_id, name, password, department="", email="", location=""):
    """Self-registration. If an admin pre-loaded this associate ID without a
    password, the learner claims that record (keeping the admin's department)."""
    err = validate_password(password)
    if err:
        raise ValueError(err)
    existing = get_user_by_associate_id(conn, associate_id)
    if existing:
        if existing["password_hash"]:
            raise ValueError("That associate ID is already registered. Please sign in.")
        conn.execute(
            """UPDATE users SET password_hash = ?, name = COALESCE(NULLIF(?, ''), name),
               department = COALESCE(NULLIF(department, ''), ?),
               email = COALESCE(NULLIF(email, ''), ?),
               location = COALESCE(NULLIF(location, ''), ?) WHERE id = ?""",
            (hash_password(password), name.strip(), department.strip(), email.strip(),
             location.strip(), existing["id"]),
        )
        conn.commit()
        return get_user_by_associate_id(conn, associate_id)
    return create_user(conn, associate_id, name, password, "learner", email, department, location)


def authenticate(conn, associate_id, password):
    user = get_user_by_associate_id(conn, associate_id)
    if user and verify_password(password, user["password_hash"]):
        return user
    return None


def set_password(conn, user_id, password):
    err = validate_password(password)
    if err:
        raise ValueError(err)
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(password), user_id))
    conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    conn.commit()


def reset_password(conn, user_id):
    """Clear a learner's password so they can register again with the same ID."""
    conn.execute("UPDATE users SET password_hash = NULL WHERE id = ?", (user_id,))
    conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    conn.commit()


IMPORT_COLUMNS = ["associate_id", "name", "email", "department", "location"]


def import_users_csv(conn, text):
    """Bulk-load associates from CSV text. Existing IDs are updated (name,
    email, department, location); passwords and progress are untouched.
    Returns (created, updated, errors)."""
    reader = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    if not reader.fieldnames:
        return 0, 0, ["The file is empty."]
    fields = {f.strip().lower(): f for f in reader.fieldnames if f}
    if "associate_id" not in fields or "name" not in fields:
        return 0, 0, ["The CSV needs at least the columns associate_id and name."]
    created = updated = 0
    errors = []
    for line_no, row in enumerate(reader, start=2):
        rec = {c: (row.get(fields[c]) or "").strip() if c in fields else "" for c in IMPORT_COLUMNS}
        if not rec["associate_id"] or not rec["name"]:
            errors.append("Line {}: associate_id and name are required.".format(line_no))
            continue
        cur = conn.execute(
            """UPDATE users SET name = ?, email = ?, department = ?, location = ?
               WHERE associate_id = ?""",
            (rec["name"], rec["email"], rec["department"], rec["location"], rec["associate_id"]),
        )
        if cur.rowcount:
            updated += 1
        else:
            conn.execute(
                """INSERT INTO users(associate_id, name, email, department, location, role, created_at)
                   VALUES (?, ?, ?, ?, ?, 'learner', ?)""",
                (rec["associate_id"], rec["name"], rec["email"], rec["department"], rec["location"], now()),
            )
            created += 1
    conn.commit()
    return created, updated, errors


# ---------------------------------------------------------------------------
# Course structure and progress
# ---------------------------------------------------------------------------

CORE_LESSONS_SQL = """SELECT COUNT(*) FROM lessons l JOIN modules m ON m.id = l.module_id
    WHERE l.active = 1 AND m.track = 'core'"""


def list_modules(conn, track=None):
    if track:
        return conn.execute("SELECT * FROM modules WHERE track = ? ORDER BY position", (track,)).fetchall()
    return conn.execute("SELECT * FROM modules ORDER BY position").fetchall()


def get_module(conn, slug):
    return conn.execute("SELECT * FROM modules WHERE slug = ?", (slug,)).fetchone()


def module_lessons(conn, module_id):
    return conn.execute(
        "SELECT * FROM lessons WHERE module_id = ? AND active = 1 ORDER BY position", (module_id,)
    ).fetchall()


def get_lesson(conn, module_id, slug):
    return conn.execute(
        "SELECT * FROM lessons WHERE module_id = ? AND slug = ? AND active = 1", (module_id, slug)
    ).fetchone()


def complete_lesson(conn, user_id, lesson_id):
    conn.execute(
        "INSERT OR IGNORE INTO lesson_progress(user_id, lesson_id, completed_at) VALUES (?, ?, ?)",
        (user_id, lesson_id, now()),
    )
    conn.commit()


def completed_lesson_ids(conn, user_id):
    return {r[0] for r in conn.execute("SELECT lesson_id FROM lesson_progress WHERE user_id = ?", (user_id,))}


def passed_module_ids(conn, user_id):
    return {
        r[0]
        for r in conn.execute(
            "SELECT DISTINCT module_id FROM quiz_attempts WHERE user_id = ? AND kind = 'module' AND passed = 1",
            (user_id,),
        )
    }


def best_final(conn, user_id):
    return conn.execute(
        """SELECT * FROM quiz_attempts WHERE user_id = ? AND kind = 'final'
           ORDER BY passed DESC, (score * 1.0 / total) DESC, completed_at LIMIT 1""",
        (user_id,),
    ).fetchone()


def lab_done_steps(conn, user_id):
    return {r["step_no"]: r for r in conn.execute("SELECT * FROM lab_progress WHERE user_id = ?", (user_id,))}


def user_progress(conn, user_id):
    """Summary used by the dashboard, certificate and admin reports."""
    total_lessons = conn.execute(CORE_LESSONS_SQL).fetchone()[0]
    done_lessons = conn.execute(
        """SELECT COUNT(*) FROM lesson_progress lp JOIN lessons l ON l.id = lp.lesson_id
           JOIN modules m ON m.id = l.module_id WHERE lp.user_id = ? AND l.active = 1 AND m.track = 'core'""",
        (user_id,),
    ).fetchone()[0]
    modules_with_quiz = {
        r[0] for r in conn.execute(
            """SELECT DISTINCT q.module_id FROM questions q JOIN modules m ON m.id = q.module_id
               WHERE q.active = 1 AND m.track = 'core'"""
        )
    }
    passed_modules = passed_module_ids(conn, user_id) & modules_with_quiz
    lab = lab_done_steps(conn, user_id)
    lab_required_done = sum(1 for s in range(1, content.LAB_REQUIRED_STEPS + 1) if s in lab)
    final = best_final(conn, user_id)
    lessons_ok = done_lessons >= total_lessons
    lab_ok = lab_required_done >= content.LAB_REQUIRED_STEPS
    final_ok = bool(final and final["passed"])
    parts = [
        done_lessons / total_lessons if total_lessons else 1,
        len(passed_modules) / len(modules_with_quiz) if modules_with_quiz else 1,
        lab_required_done / content.LAB_REQUIRED_STEPS,
        1 if final_ok else 0,
    ]
    return {
        "total_lessons": total_lessons,
        "done_lessons": done_lessons,
        "quiz_modules": len(modules_with_quiz),
        "passed_modules": len(passed_modules),
        "lab_done": len(lab),
        "lab_required_done": lab_required_done,
        "final": final,
        "lessons_ok": lessons_ok,
        "lab_ok": lab_ok,
        "final_ok": final_ok,
        "certified": lessons_ok and lab_ok and final_ok,
        "percent": round(100 * sum(parts) / len(parts)),
    }


def next_step(conn, user_id):
    """The learner's next suggested action in the core course, as a dict with
    kind (lesson, quiz, lab, final, certificate), url, and module/lesson rows."""
    done = completed_lesson_ids(conn, user_id)
    passed = passed_module_ids(conn, user_id)
    for mod in list_modules(conn, "core"):
        for les in module_lessons(conn, mod["id"]):
            if les["id"] not in done:
                return {"kind": "lesson", "module": mod, "lesson": les,
                        "url": "/module/{}/lesson/{}".format(mod["slug"], les["slug"])}
        if mod["id"] not in passed and module_questions(conn, mod["id"]):
            return {"kind": "quiz", "module": mod, "url": "/module/{}/quiz".format(mod["slug"])}
    prog = user_progress(conn, user_id)
    if not prog["lab_ok"]:
        return {"kind": "lab", "url": "/lab"}
    if not prog["final_ok"]:
        return {"kind": "final", "url": "/final"}
    return {"kind": "certificate", "url": "/certificate"}


# ---------------------------------------------------------------------------
# Quizzes
# ---------------------------------------------------------------------------

def module_questions(conn, module_id):
    return conn.execute(
        "SELECT * FROM questions WHERE module_id = ? AND active = 1 ORDER BY code", (module_id,)
    ).fetchall()


def final_questions(conn, count=None, rng=None):
    """Random final-assessment set: always the in-slide checks, then a spread
    across modules, scenario questions first."""
    count = count or content.FINAL_QUESTION_COUNT
    rng = rng or random.SystemRandom()
    rows = conn.execute(
        """SELECT q.* FROM questions q LEFT JOIN modules m ON m.id = q.module_id
           WHERE q.active = 1 AND COALESCE(m.track, 'core') = 'core'"""
    ).fetchall()
    chosen = [r for r in rows if r["in_slide_check"]]
    rest = [r for r in rows if not r["in_slide_check"]]
    rng.shuffle(rest)
    by_module = {}
    for r in rest:
        by_module.setdefault(r["module_id"], []).append(r)
    # Round-robin across modules for coverage.
    while len(chosen) < count and any(by_module.values()):
        for mid in list(by_module):
            if by_module[mid] and len(chosen) < count:
                chosen.append(by_module[mid].pop())
    rng.shuffle(chosen)
    return chosen


def question_options(q):
    return json.loads(q["options_json"])


def shuffled_options(q, rng=None):
    """List of (original_index, text) in a random display order, so correct
    answers are not always in the same position."""
    rng = rng or random.SystemRandom()
    opts = list(enumerate(question_options(q)))
    rng.shuffle(opts)
    return opts


def grade_attempt(conn, user_id, kind, question_ids, answers, module_id=None):
    """answers: {question_id: chosen original index or None}. Returns attempt id."""
    pass_mark = int(get_setting(conn, "pass_mark", content.DEFAULT_PASS_MARK))
    rows = {
        r["id"]: r
        for r in conn.execute(
            "SELECT * FROM questions WHERE id IN ({})".format(",".join("?" * len(question_ids))),
            list(question_ids),
        )
    } if question_ids else {}
    results = []
    for qid in question_ids:
        q = rows.get(qid)
        if not q:
            continue
        chosen = answers.get(qid)
        results.append((qid, chosen, int(chosen is not None and chosen == q["correct_index"])))
    total = len(results)
    score = sum(r[2] for r in results)
    passed = int(total > 0 and score * 100 >= pass_mark * total)
    cur = conn.execute(
        "INSERT INTO quiz_attempts(user_id, kind, module_id, score, total, passed, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, kind, module_id, score, total, passed, now()),
    )
    attempt_id = cur.lastrowid
    conn.executemany(
        "INSERT INTO attempt_answers(attempt_id, question_id, chosen_index, correct) VALUES (?, ?, ?, ?)",
        [(attempt_id, qid, chosen, ok) for qid, chosen, ok in results],
    )
    conn.commit()
    return attempt_id


def attempt_review(conn, attempt_id, user_id=None):
    sql = "SELECT * FROM quiz_attempts WHERE id = ?"
    args = [attempt_id]
    if user_id is not None:
        sql += " AND user_id = ?"
        args.append(user_id)
    attempt = conn.execute(sql, args).fetchone()
    if not attempt:
        return None, []
    answers = conn.execute(
        """SELECT a.chosen_index, a.correct, q.* FROM attempt_answers a
           JOIN questions q ON q.id = a.question_id WHERE a.attempt_id = ? ORDER BY a.rowid""",
        (attempt_id,),
    ).fetchall()
    return attempt, answers


# ---------------------------------------------------------------------------
# Lab, charter, feedback
# ---------------------------------------------------------------------------

def set_lab_step(conn, user_id, step_no, done, note=""):
    if done:
        conn.execute(
            """INSERT INTO lab_progress(user_id, step_no, note, completed_at) VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id, step_no) DO UPDATE SET note = excluded.note""",
            (user_id, step_no, note.strip()[:1000], now()),
        )
    else:
        conn.execute("DELETE FROM lab_progress WHERE user_id = ? AND step_no = ?", (user_id, step_no))
    conn.commit()


CHARTER_FIELDS = [
    ("agent_name", "Agent name", "Short and specific, e.g. Email Clarity Coach"),
    ("purpose", "One purpose", "This agent helps me [one clear task] for [audience]."),
    ("in_scope", "In scope", "2-4 things it should do"),
    ("out_scope", "Out of scope", "2-4 things it must not do"),
    ("knowledge", "Knowledge", "None, or the specific approved source(s)"),
    ("output_style", "Output style", "Short answer / steps / table / example"),
    ("when_unsure", "When unsure", "Say what is missing; ask or refer to an authorized source."),
    ("privacy", "Privacy rule", "Do not request or expose unnecessary sensitive data."),
    ("prompts", "Starter prompts", "1. ...  2. ...  3. ..."),
    ("owner", "Owner (role)", "Your role; avoid personal details in training copies"),
    ("review_date", "Review date", "YYYY-MM-DD"),
]


def get_charter(conn, user_id):
    row = conn.execute("SELECT * FROM charters WHERE user_id = ?", (user_id,)).fetchone()
    return (json.loads(row["data_json"]), row["updated_at"]) if row else ({}, None)


def save_charter(conn, user_id, data):
    clean = {k: (data.get(k) or "").strip()[:2000] for k, _, _ in CHARTER_FIELDS}
    conn.execute(
        """INSERT INTO charters(user_id, data_json, updated_at) VALUES (?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET data_json = excluded.data_json, updated_at = excluded.updated_at""",
        (user_id, json.dumps(clean), now()),
    )
    conn.commit()


def charter_text(data):
    lines = []
    for key, label, _ in CHARTER_FIELDS:
        lines.append("{}: {}".format(label.upper(), data.get(key, "")))
    return "\n".join(lines)


def charter_instructions(data):
    """Draft agent instructions (Template B) from a learner's charter."""
    name = data.get("agent_name") or "[Agent Name]"
    purpose = data.get("purpose") or "[single, measurable task]"
    knowledge = data.get("knowledge") or "[authorized sources]"
    style = data.get("output_style") or "[requested output format]"
    lines = [
        "You are {}.".format(name),
        "Your ONE purpose: {}".format(purpose),
    ]
    if data.get("in_scope"):
        lines.append("You may: {}".format(data["in_scope"]))
    if data.get("out_scope"):
        lines.append("You must not: {}".format(data["out_scope"]))
    lines += [
        "Use only {} when facts must be grounded.".format(knowledge),
        "Reply with {} in simple English.".format(style),
        "If information is unclear or missing, ask for clarification or say you cannot confirm it.",
        "Never invent facts, policy limits, citations, or decisions.",
        "Do not reveal sensitive data or bypass access rules.",
        "If a request is outside your purpose, briefly say so and recommend standard Copilot Chat or a suitable agent.",
    ]
    return "\n".join(lines)


def add_feedback(conn, user_id, rating, comment):
    conn.execute(
        "INSERT INTO feedback(user_id, rating, comment, created_at) VALUES (?, ?, ?, ?)",
        (user_id, rating, comment.strip()[:2000], now()),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Admin reports
# ---------------------------------------------------------------------------

def _learner_stats_sql():
    """One row per learner with progress counts, computed in SQL so reports
    stay fast with tens of thousands of associates."""
    return """
    WITH lessons_done AS (
        SELECT lp.user_id, COUNT(*) AS n FROM lesson_progress lp
        JOIN lessons l ON l.id = lp.lesson_id AND l.active = 1
        JOIN modules m ON m.id = l.module_id AND m.track = 'core' GROUP BY lp.user_id
    ),
    quiz_passed AS (
        SELECT a.user_id, COUNT(DISTINCT a.module_id) AS n FROM quiz_attempts a
        JOIN modules m ON m.id = a.module_id AND m.track = 'core'
        WHERE a.kind = 'module' AND a.passed = 1 GROUP BY a.user_id
    ),
    lab_req AS (
        SELECT user_id, COUNT(*) AS n FROM lab_progress WHERE step_no <= :lab_required GROUP BY user_id
    ),
    final_best AS (
        SELECT user_id, MAX(passed) AS passed, MAX(ROUND(100.0 * score / total)) AS best_pct,
               COUNT(*) AS attempts FROM quiz_attempts WHERE kind = 'final' GROUP BY user_id
    )
    SELECT u.id, u.associate_id, u.name, u.email, u.department, u.location, u.created_at, u.last_login,
           u.is_reviewer, u.password_hash IS NOT NULL AS registered,
           COALESCE(ld.n, 0) AS lessons_done,
           COALESCE(qp.n, 0) AS quizzes_passed,
           COALESCE(lr.n, 0) AS lab_done,
           COALESCE(fb.passed, 0) AS final_passed,
           fb.best_pct AS final_best_pct,
           COALESCE(fb.attempts, 0) AS final_attempts
    FROM users u
    LEFT JOIN lessons_done ld ON ld.user_id = u.id
    LEFT JOIN quiz_passed qp ON qp.user_id = u.id
    LEFT JOIN lab_req lr ON lr.user_id = u.id
    LEFT JOIN final_best fb ON fb.user_id = u.id
    WHERE u.role = 'learner'
    """


def learner_status(row, total_lessons):
    if row["final_passed"] and row["lessons_done"] >= total_lessons and row["lab_done"] >= content.LAB_REQUIRED_STEPS:
        return "Certified"
    if row["lessons_done"] or row["quizzes_passed"] or row["lab_done"] or row["final_attempts"]:
        return "In progress"
    if row["registered"]:
        return "Registered"
    return "Not started"


def learner_rows(conn, search="", department="", status="", limit=None, offset=0, coaches_only=False):
    total_lessons = conn.execute(CORE_LESSONS_SQL).fetchone()[0]
    sql = "SELECT * FROM (" + _learner_stats_sql() + ") WHERE 1 = 1"
    params = {"lab_required": content.LAB_REQUIRED_STEPS}
    if search:
        sql += " AND (associate_id LIKE :q OR name LIKE :q OR email LIKE :q)"
        params["q"] = "%" + search.strip() + "%"
    if department:
        sql += " AND department = :dept"
        params["dept"] = department
    if coaches_only:
        sql += " AND is_reviewer = 1"
    sql += " ORDER BY department, name"
    rows = []
    for r in conn.execute(sql, params):
        d = dict(r)
        d["status"] = learner_status(r, total_lessons)
        d["total_lessons"] = total_lessons
        if status and d["status"] != status:
            continue
        rows.append(d)
    total = len(rows)
    if limit is not None:
        rows = rows[offset: offset + limit]
    return rows, total


def overview_stats(conn):
    rows, total = learner_rows(conn)
    counts = {"Certified": 0, "In progress": 0, "Registered": 0, "Not started": 0}
    for r in rows:
        counts[r["status"]] += 1
    depts = {}
    for r in rows:
        d = depts.setdefault(r["department"] or "(none)", {"total": 0, "Certified": 0, "In progress": 0, "active": 0})
        d["total"] += 1
        if r["status"] in ("Certified", "In progress"):
            d[r["status"]] += 1
            d["active"] += 1
    avg = conn.execute(
        "SELECT AVG(100.0 * score / total), COUNT(*) FROM quiz_attempts WHERE kind = 'final'"
    ).fetchone()
    fb = conn.execute("SELECT AVG(rating), COUNT(*) FROM feedback").fetchone()
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    active_week = conn.execute(
        "SELECT COUNT(*) FROM users WHERE role = 'learner' AND last_login >= ?", (week_ago,)
    ).fetchone()[0]
    return {
        "total": total,
        "counts": counts,
        "departments": sorted(depts.items()),
        "final_avg": round(avg[0]) if avg[0] is not None else None,
        "final_attempts": avg[1],
        "feedback_avg": round(fb[0], 1) if fb[0] is not None else None,
        "feedback_count": fb[1],
        "active_week": active_week,
    }


def module_funnel(conn):
    """Per module: learners who completed all lessons, and who passed its quiz."""
    out = []
    for m in list_modules(conn):
        n_lessons = conn.execute(
            "SELECT COUNT(*) FROM lessons WHERE module_id = ? AND active = 1", (m["id"],)
        ).fetchone()[0]
        completed = conn.execute(
            """SELECT COUNT(*) FROM (SELECT lp.user_id FROM lesson_progress lp
               JOIN lessons l ON l.id = lp.lesson_id WHERE l.module_id = ? AND l.active = 1
               GROUP BY lp.user_id HAVING COUNT(*) >= ?)""",
            (m["id"], n_lessons),
        ).fetchone()[0]
        passed = conn.execute(
            "SELECT COUNT(DISTINCT user_id) FROM quiz_attempts WHERE module_id = ? AND passed = 1", (m["id"],)
        ).fetchone()[0]
        out.append({"slug": m["slug"], "title": m["title"], "completed": completed, "passed": passed})
    return out


def question_stats(conn):
    """How often each question is answered correctly, hardest first."""
    return conn.execute(
        """SELECT q.id, q.code, q.prompt, q.category, q.difficulty, q.active, q.custom,
                  COUNT(a.question_id) AS answered,
                  SUM(a.correct) AS correct
           FROM questions q LEFT JOIN attempt_answers a ON a.question_id = q.id
           GROUP BY q.id
           ORDER BY CASE WHEN COUNT(a.question_id) = 0 THEN 1 ELSE 0 END,
                    1.0 * SUM(a.correct) / NULLIF(COUNT(a.question_id), 0), q.code"""
    ).fetchall()


EXPORT_COLUMNS = [
    "associate_id", "name", "email", "department", "location", "status", "lessons_done",
    "total_lessons", "quizzes_passed", "lab_done", "final_passed", "final_best_pct",
    "final_attempts", "last_login",
]


def export_progress_csv(conn, department=""):
    rows, _ = learner_rows(conn, department=department)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(EXPORT_COLUMNS)
    for r in rows:
        w.writerow([r.get(c) if r.get(c) is not None else "" for c in EXPORT_COLUMNS])
    return buf.getvalue()


def departments(conn):
    return [
        r[0] for r in conn.execute(
            "SELECT DISTINCT department FROM users WHERE role = 'learner' AND department != '' ORDER BY department"
        )
    ]


def add_custom_question(conn, module_id, prompt, options, correct_index, rationale, category="Custom", difficulty="Medium"):
    options = [o.strip() for o in options if o.strip()]
    if not prompt.strip() or len(options) < 2:
        raise ValueError("A question needs text and at least two options.")
    if not 0 <= correct_index < len(options):
        raise ValueError("Choose which option is correct.")
    n = conn.execute("SELECT COUNT(*) FROM questions WHERE custom = 1").fetchone()[0] + 1
    code = "ORG-Q{:02d}".format(n)
    while conn.execute("SELECT 1 FROM questions WHERE code = ?", (code,)).fetchone():
        n += 1
        code = "ORG-Q{:02d}".format(n)
    conn.execute(
        """INSERT INTO questions(code, module_id, category, difficulty, scenario, prompt, options_json,
               correct_index, rationale, source_url, in_slide_check, active, custom)
           VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, '', 0, 1, 1)""",
        (code, module_id, category.strip() or "Custom", difficulty, prompt.strip(), json.dumps(options),
         correct_index, rationale.strip()),
    )
    conn.commit()
    return code


def set_question_active(conn, question_id, active):
    conn.execute("UPDATE questions SET active = ? WHERE id = ?", (int(bool(active)), question_id))
    conn.commit()

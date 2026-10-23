"""SQLite storage: schema, connection helper and content seeding."""

import json
import os
import sqlite3
from datetime import datetime, timezone

from . import content

DEFAULT_DB_PATH = os.environ.get(
    "TRAINING_DB",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "training.db"),
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    associate_id TEXT NOT NULL UNIQUE COLLATE NOCASE,
    name TEXT NOT NULL,
    email TEXT NOT NULL DEFAULT '',
    department TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    role TEXT NOT NULL DEFAULT 'learner' CHECK (role IN ('learner', 'admin')),
    password_hash TEXT,
    created_at TEXT NOT NULL,
    last_login TEXT
);
CREATE INDEX IF NOT EXISTS idx_users_department ON users(department);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    csrf TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    minutes INTEGER NOT NULL,
    position INTEGER NOT NULL,
    track TEXT NOT NULL DEFAULT 'core'
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(id),
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    body_html TEXT NOT NULL,
    minutes INTEGER NOT NULL,
    position INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    UNIQUE (module_id, slug)
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    module_id INTEGER REFERENCES modules(id),
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    scenario INTEGER NOT NULL DEFAULT 0,
    prompt TEXT NOT NULL,
    options_json TEXT NOT NULL,
    correct_index INTEGER NOT NULL,
    rationale TEXT NOT NULL,
    source_url TEXT NOT NULL DEFAULT '',
    in_slide_check INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    custom INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lesson_progress (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    completed_at TEXT NOT NULL,
    PRIMARY KEY (user_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN ('module', 'final')),
    module_id INTEGER REFERENCES modules(id),
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    passed INTEGER NOT NULL,
    completed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts_user ON quiz_attempts(user_id, kind);

CREATE TABLE IF NOT EXISTS attempt_answers (
    attempt_id INTEGER NOT NULL REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(id),
    chosen_index INTEGER,
    correct INTEGER NOT NULL,
    PRIMARY KEY (attempt_id, question_id)
);
CREATE INDEX IF NOT EXISTS idx_answers_question ON attempt_answers(question_id);

CREATE TABLE IF NOT EXISTS lab_progress (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    step_no INTEGER NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    completed_at TEXT NOT NULL,
    PRIMARY KEY (user_id, step_no)
);

CREATE TABLE IF NOT EXISTS charters (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    data_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    purpose TEXT NOT NULL,
    department TEXT NOT NULL DEFAULT '',
    audience TEXT NOT NULL DEFAULT '',
    knowledge_types TEXT NOT NULL DEFAULT 'none',
    knowledge_detail TEXT NOT NULL DEFAULT '',
    sensitivity TEXT NOT NULL DEFAULT 'internal',
    sharing_scope TEXT NOT NULL DEFAULT 'private',
    test_notes TEXT NOT NULL DEFAULT '',
    link TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'registered',
    review_date TEXT NOT NULL DEFAULT '',
    tier TEXT NOT NULL DEFAULT '1',
    kpi_name TEXT NOT NULL DEFAULT '',
    kpi_baseline TEXT NOT NULL DEFAULT '',
    kpi_result TEXT NOT NULL DEFAULT '',
    value_reviewed_at TEXT,
    idea_id INTEGER REFERENCES ideas(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    submitted_at TEXT,
    decided_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_agents_owner ON agents(owner_id);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);

CREATE TABLE IF NOT EXISTS agent_reviews (
    id INTEGER PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    reviewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    decision TEXT NOT NULL CHECK (decision IN ('approved', 'changes', 'rejected')),
    checklist_json TEXT NOT NULL,
    comment TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'other',
    department TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS idea_votes (
    idea_id INTEGER NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (idea_id, user_id)
);

CREATE TABLE IF NOT EXISTS idea_comments (
    id INTEGER PRIMARY KEY,
    idea_id INTEGER NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    params_json TEXT NOT NULL DEFAULT '{}',
    link TEXT NOT NULL DEFAULT '',
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);

CREATE TABLE IF NOT EXISTS licence_requests (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    department TEXT NOT NULL DEFAULT '',
    seats INTEGER NOT NULL,
    use_case TEXT NOT NULL,
    expected_hours REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    wave TEXT NOT NULL DEFAULT '',
    decision_note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    decided_at TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    starts_at TEXT NOT NULL,
    place TEXT NOT NULL DEFAULT '',
    details TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event_signups (
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (event_id, user_id)
);

CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'other',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompt_ratings (
    prompt_id INTEGER NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    PRIMARY KEY (prompt_id, user_id)
);

CREATE TABLE IF NOT EXISTS coe_questions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL DEFAULT '',
    answered_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL,
    answered_at TEXT
);

CREATE TABLE IF NOT EXISTS value_logs (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week TEXT NOT NULL,
    hours REAL NOT NULL,
    agent_id INTEGER REFERENCES agents(id) ON DELETE SET NULL,
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    PRIMARY KEY (user_id, week)
);

CREATE TABLE IF NOT EXISTS skill_assessments (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    answers_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

# Columns added after the first release. init_db adds them to older databases.
MIGRATIONS = [
    ("users", "lang", "TEXT NOT NULL DEFAULT ''"),
    ("users", "is_reviewer", "INTEGER NOT NULL DEFAULT 0"),
    ("users", "office_hours", "TEXT NOT NULL DEFAULT ''"),
    ("modules", "track", "TEXT NOT NULL DEFAULT 'core'"),
    ("agents", "tier", "TEXT NOT NULL DEFAULT '1'"),
    ("agents", "kpi_name", "TEXT NOT NULL DEFAULT ''"),
    ("agents", "kpi_baseline", "TEXT NOT NULL DEFAULT ''"),
    ("agents", "kpi_result", "TEXT NOT NULL DEFAULT ''"),
    ("agents", "value_reviewed_at", "TEXT"),
]


def _migrate(conn):
    for table, column, ddl in MIGRATIONS:
        cols = {r[1] for r in conn.execute("PRAGMA table_info({})".format(table))}
        if column not in cols:
            conn.execute("ALTER TABLE {} ADD COLUMN {} {}".format(table, column, ddl))


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def connect(path=None):
    path = path or DEFAULT_DB_PATH
    if path != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 15000")
    return conn


def init_db(path=None):
    """Create tables and load course content if the database is new."""
    conn = connect(path)
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(SCHEMA)
        _migrate(conn)
        if conn.execute("SELECT COUNT(*) FROM modules").fetchone()[0] == 0:
            seed_content(conn)
        elif get_setting(conn, "content_edition") != content.EDITION_DATE + "/" + str(len(content.QUESTIONS)):
            seed_content(conn)
        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value) VALUES ('pass_mark', ?)",
            (str(content.DEFAULT_PASS_MARK),),
        )
        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value) VALUES ('org_name', 'Our Organization')"
        )
        conn.commit()
    finally:
        conn.close()


def seed_content(conn):
    """Insert or update modules, lessons and built-in questions from content.py.

    Matching is by slug / question code, so learner progress and attempts are
    kept. Lessons or built-in questions removed from content.py are deactivated,
    not deleted. Questions added by admins in the app are left alone.
    """
    for pos, mod in enumerate(content.MODULES, start=1):
        conn.execute(
            """INSERT INTO modules(slug, title, summary, minutes, position, track) VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(slug) DO UPDATE SET title=excluded.title, summary=excluded.summary,
               minutes=excluded.minutes, position=excluded.position, track=excluded.track""",
            (mod["slug"], mod["title"], mod["summary"], mod["minutes"], pos, mod.get("track", "core")),
        )
        module_id = conn.execute("SELECT id FROM modules WHERE slug = ?", (mod["slug"],)).fetchone()[0]
        conn.execute("UPDATE lessons SET active = 0 WHERE module_id = ?", (module_id,))
        for lpos, les in enumerate(mod["lessons"], start=1):
            conn.execute(
                """INSERT INTO lessons(module_id, slug, title, body_html, minutes, position, active)
                   VALUES (?, ?, ?, ?, ?, ?, 1)
                   ON CONFLICT(module_id, slug) DO UPDATE SET title=excluded.title,
                   body_html=excluded.body_html, minutes=excluded.minutes,
                   position=excluded.position, active=1""",
                (module_id, les["slug"], les["title"], les["body"].strip(), les["minutes"], lpos),
            )

    set_setting(conn, "content_edition", content.EDITION_DATE + "/" + str(len(content.QUESTIONS)))
    module_ids = {r["slug"]: r["id"] for r in conn.execute("SELECT id, slug FROM modules")}
    conn.execute("UPDATE questions SET active = 0 WHERE custom = 0")
    for q in content.QUESTIONS:
        conn.execute(
            """INSERT INTO questions(code, module_id, category, difficulty, scenario, prompt,
                   options_json, correct_index, rationale, source_url, in_slide_check, active, custom)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
               ON CONFLICT(code) DO UPDATE SET module_id=excluded.module_id,
               category=excluded.category, difficulty=excluded.difficulty,
               scenario=excluded.scenario, prompt=excluded.prompt,
               options_json=excluded.options_json, correct_index=excluded.correct_index,
               rationale=excluded.rationale, source_url=excluded.source_url,
               in_slide_check=excluded.in_slide_check, active=1""",
            (
                q["code"], module_ids[q["module"]], q["category"], q["difficulty"],
                int(q["scenario"]), q["prompt"], json.dumps(q["options"]), q["correct"],
                q["rationale"], q["source_url"], int(q["in_slide_check"]),
            ),
        )
    conn.commit()


def get_setting(conn, key, default=None):
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(conn, key, value):
    conn.execute(
        "INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )

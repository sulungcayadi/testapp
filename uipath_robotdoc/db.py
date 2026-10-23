"""SQLite store for parsed packages, plus the query layer the renderers read from."""
from __future__ import annotations

import sqlite3
from collections import Counter
from datetime import datetime, timezone

from .parser import Package, resolve_invoke

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS packages (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, version TEXT NOT NULL DEFAULT '',
    description TEXT, authors TEXT, source TEXT, main TEXT,
    expression_language TEXT, target_framework TEXT, ingested_at TEXT NOT NULL,
    UNIQUE (name, version)
);
CREATE TABLE IF NOT EXISTS dependencies (
    id INTEGER PRIMARY KEY, package_id INTEGER NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
    name TEXT NOT NULL, version TEXT
);
CREATE TABLE IF NOT EXISTS workflows (
    id INTEGER PRIMARY KEY, package_id INTEGER NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
    path TEXT NOT NULL, name TEXT NOT NULL, class_name TEXT, root_type TEXT,
    annotation TEXT, is_main INTEGER NOT NULL DEFAULT 0, parse_error TEXT
);
CREATE TABLE IF NOT EXISTS arguments (
    id INTEGER PRIMARY KEY, workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    name TEXT NOT NULL, direction TEXT NOT NULL, type TEXT
);
CREATE TABLE IF NOT EXISTS variables (
    id INTEGER PRIMARY KEY, workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    name TEXT NOT NULL, type TEXT, default_value TEXT, scope TEXT
);
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY, workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    seq INTEGER NOT NULL, depth INTEGER NOT NULL, type TEXT NOT NULL,
    display_name TEXT, annotation TEXT, detail TEXT
);
CREATE TABLE IF NOT EXISTS invocations (
    id INTEGER PRIMARY KEY, caller_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    target_path TEXT NOT NULL, callee_id INTEGER REFERENCES workflows(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_wf_pkg ON workflows(package_id);
CREATE INDEX IF NOT EXISTS idx_act_wf ON activities(workflow_id);
"""


def connect(path: str) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def ingest(con: sqlite3.Connection, pkg: Package) -> int:
    """Store `pkg`, replacing any earlier ingest of the same name+version. Returns the package id."""
    with con:
        con.execute("DELETE FROM packages WHERE name = ? AND version = ?", (pkg.name, pkg.version))
        pid = con.execute(
            "INSERT INTO packages (name, version, description, authors, source, main, expression_language,"
            " target_framework, ingested_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (pkg.name, pkg.version, pkg.description, pkg.authors, pkg.source, pkg.main,
             pkg.expression_language, pkg.target_framework, datetime.now(timezone.utc).isoformat(timespec="seconds")),
        ).lastrowid
        con.executemany("INSERT INTO dependencies (package_id, name, version) VALUES (?,?,?)",
                        [(pid, n, v) for n, v in pkg.dependencies])
        ids: dict[str, int] = {}
        main_norm = pkg.main.replace("\\", "/")
        for wf in pkg.workflows:
            wid = con.execute(
                "INSERT INTO workflows (package_id, path, name, class_name, root_type, annotation, is_main, parse_error)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (pid, wf.path, wf.name, wf.class_name, wf.root_type, wf.annotation,
                 int(wf.path == main_norm), wf.parse_error)).lastrowid
            ids[wf.path] = wid
            con.executemany("INSERT INTO arguments (workflow_id, name, direction, type) VALUES (?,?,?,?)",
                            [(wid, a.name, a.direction, a.type) for a in wf.arguments])
            con.executemany("INSERT INTO variables (workflow_id, name, type, default_value, scope) VALUES (?,?,?,?,?)",
                            [(wid, v.name, v.type, v.default, v.scope) for v in wf.variables])
            con.executemany(
                "INSERT INTO activities (workflow_id, seq, depth, type, display_name, annotation, detail) VALUES (?,?,?,?,?,?,?)",
                [(wid, a.seq, a.depth, a.type, a.display_name, a.annotation, a.detail) for a in wf.activities])
        for wf in pkg.workflows:
            for target in wf.invokes:
                resolved = resolve_invoke(target, list(ids))
                con.execute("INSERT INTO invocations (caller_id, target_path, callee_id) VALUES (?,?,?)",
                            (ids[wf.path], target, ids.get(resolved) if resolved else None))
    return pid


def load_model(con: sqlite3.Connection, package_id: int) -> dict:
    """Everything a renderer needs, read back from SQLite as plain dicts."""
    q = lambda sql, *a: [dict(r) for r in con.execute(sql, a)]  # noqa: E731
    pkg = q("SELECT * FROM packages WHERE id = ?", package_id)[0]
    workflows = q("SELECT * FROM workflows WHERE package_id = ? ORDER BY is_main DESC, path", package_id)
    by_id = {w["id"]: w for w in workflows}
    for w in workflows:
        wid = w["id"]
        w["arguments"] = q("SELECT name, direction, type FROM arguments WHERE workflow_id = ? ORDER BY id", wid)
        w["variables"] = q("SELECT name, type, default_value, scope FROM variables WHERE workflow_id = ? ORDER BY id", wid)
        w["activities"] = q("SELECT seq, depth, type, display_name, annotation, detail FROM activities"
                            " WHERE workflow_id = ? ORDER BY seq", wid)
        w["invokes"] = q("SELECT target_path, callee_id FROM invocations WHERE caller_id = ? ORDER BY id", wid)
        for inv in w["invokes"]:
            inv["callee"] = by_id[inv["callee_id"]]["path"] if inv["callee_id"] else None
        w["invoked_by"] = [by_id[r["caller_id"]]["path"] for r in
                           q("SELECT caller_id FROM invocations WHERE callee_id = ?", wid)]
        w["type_counts"] = dict(Counter(a["type"] for a in w["activities"]).most_common())
    all_types = Counter()
    for w in workflows:
        all_types.update(w["type_counts"])
    orphans = [w["path"] for w in workflows if not w["invoked_by"] and not w["is_main"] and not w["parse_error"]]
    return {
        "package": pkg,
        "dependencies": q("SELECT name, version FROM dependencies WHERE package_id = ? ORDER BY name", package_id),
        "workflows": workflows,
        "stats": {
            "workflows": len(workflows),
            "activities": sum(len(w["activities"]) for w in workflows),
            "arguments": sum(len(w["arguments"]) for w in workflows),
            "variables": sum(len(w["variables"]) for w in workflows),
            "invocations": sum(len(w["invokes"]) for w in workflows),
            "dependencies": len(q("SELECT 1 FROM dependencies WHERE package_id = ?", package_id)),
            "top_activities": all_types.most_common(15),
            "unreferenced": orphans,
            "unresolved_invokes": [(w["path"], i["target_path"]) for w in workflows for i in w["invokes"] if not i["callee"]],
            "parse_errors": [(w["path"], w["parse_error"]) for w in workflows if w["parse_error"]],
        },
    }

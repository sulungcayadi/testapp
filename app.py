#!/usr/bin/env python3
"""Copilot Agent Builder (T1) training app.

Run with:  python app.py
Then open http://127.0.0.1:8000 in your browser.

Other commands (see README.md):
  python app.py create-admin            Add an administrator account
  python app.py import-users FILE.csv   Load associates from a CSV file
  python app.py export FILE.csv         Save the progress report to a CSV file
  python app.py reseed                  Reload course content after editing training/content.py
  python app.py demo-data [N]           Add N fictional learners with random progress (for trying the reports)
"""

import argparse
import getpass
import os
import random
import sys
import threading
import webbrowser

if sys.version_info < (3, 8):
    sys.exit("Python 3.8 or newer is required. You have " + sys.version.split()[0])

from training import content, db, services as svc  # noqa: E402
from training.web import make_server  # noqa: E402


def cmd_run(args):
    db.init_db(args.db)
    server = make_server(args.host, args.port, args.db)
    url = "http://{}:{}".format("127.0.0.1" if args.host in ("0.0.0.0", "") else args.host, args.port)
    print("Copilot Agent Builder training is running at " + url)
    print("Database: " + os.path.abspath(args.db))
    print("Press Ctrl+C to stop.")
    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


def cmd_create_admin(args):
    db.init_db(args.db)
    conn = db.connect(args.db)
    associate_id = args.id or input("Administrator ID: ").strip()
    name = args.name or input("Display name: ").strip()
    password = args.password or getpass.getpass("Password (8+ characters): ")
    err = svc.validate_password(password)
    if err:
        sys.exit(err)
    existing = svc.get_user_by_associate_id(conn, associate_id)
    if existing:
        conn.execute("UPDATE users SET role = 'admin' WHERE id = ?", (existing["id"],))
        conn.commit()
        svc.set_password(conn, existing["id"], password)
        print("Existing account {} is now an administrator.".format(associate_id))
    else:
        svc.create_user(conn, associate_id, name or associate_id, password, role="admin")
        print("Administrator {} created.".format(associate_id))
    conn.close()


def cmd_import(args):
    db.init_db(args.db)
    conn = db.connect(args.db)
    with open(args.file, "r", encoding="utf-8-sig", errors="replace") as f:
        created, updated, errors = svc.import_users_csv(conn, f.read())
    print("Added {}, updated {}, skipped {}.".format(created, updated, len(errors)))
    for e in errors[:50]:
        print("  " + e)
    conn.close()


def cmd_export(args):
    db.init_db(args.db)
    conn = db.connect(args.db)
    with open(args.file, "w", encoding="utf-8-sig", newline="") as f:
        f.write(svc.export_progress_csv(conn))
    print("Progress report written to " + args.file)
    conn.close()


def cmd_reseed(args):
    db.init_db(args.db)
    conn = db.connect(args.db)
    db.seed_content(conn)
    print("Course content reloaded from training/content.py. Learner progress was kept.")
    conn.close()


DEMO_DEPTS = ["Finance", "Sales", "Operations", "Human Resources", "IT", "Marketing", "Customer Service", "Legal"]
DEMO_FIRST = ["Alex", "Sam", "Priya", "Kenji", "Mei", "Somchai", "Fatima", "Lucas", "Ana", "Omar", "Nok", "Yuki", "Chen", "Grace"]
DEMO_LAST = ["Tan", "Sato", "Wong", "Garcia", "Khan", "Silva", "Nguyen", "Lee", "Patel", "Suzuki", "Li", "Brown"]


def cmd_demo(args):
    """Fictional learners with random progress so admins can explore the reports."""
    db.init_db(args.db)
    conn = db.connect(args.db)
    rng = random.Random(42)
    lessons = conn.execute("SELECT id, module_id FROM lessons WHERE active = 1 ORDER BY module_id, position").fetchall()
    modules = svc.list_modules(conn)
    start = conn.execute("SELECT COUNT(*) FROM users WHERE associate_id LIKE 'DEMO%'").fetchone()[0]
    for i in range(start, start + args.count):
        aid = "DEMO{:05d}".format(i + 1)
        name = "{} {} (demo)".format(rng.choice(DEMO_FIRST), rng.choice(DEMO_LAST))
        conn.execute(
            "INSERT INTO users(associate_id, name, department, location, role, created_at) VALUES (?, ?, ?, ?, 'learner', ?)",
            (aid, name, rng.choice(DEMO_DEPTS), "", db.now()),
        )
        uid = conn.execute("SELECT id FROM users WHERE associate_id = ?", (aid,)).fetchone()[0]
        depth = rng.random()
        if depth < 0.25:
            continue
        n_lessons = int(len(lessons) * min(1.0, depth * 1.3))
        conn.executemany(
            "INSERT OR IGNORE INTO lesson_progress(user_id, lesson_id, completed_at) VALUES (?, ?, ?)",
            [(uid, l["id"], db.now()) for l in lessons[:n_lessons]],
        )
        done_modules = {l["module_id"] for l in lessons[:n_lessons]}
        for m in modules:
            qs = svc.module_questions(conn, m["id"])
            if m["id"] in done_modules and qs:
                ans = {q["id"]: (q["correct_index"] if rng.random() < 0.85 else -1) for q in qs}
                svc.grade_attempt(conn, uid, "module", [q["id"] for q in qs], ans, m["id"])
        if n_lessons == len(lessons):
            for s in range(1, len(content.LAB_STEPS) + 1):
                if rng.random() < 0.92:
                    svc.set_lab_step(conn, uid, s, True)
            qs = svc.final_questions(conn, rng=rng)
            ans = {q["id"]: (q["correct_index"] if rng.random() < 0.88 else -1) for q in qs}
            svc.grade_attempt(conn, uid, "final", [q["id"] for q in qs], ans)
            if rng.random() < 0.5:
                svc.add_feedback(conn, uid, rng.choice([3, 4, 4, 5, 5]), "")
    conn.commit()
    print("Added {} fictional demo learners (IDs start with DEMO).".format(args.count))
    conn.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Copilot Agent Builder (T1) training app")
    parser.add_argument("--db", default=db.DEFAULT_DB_PATH, help="Path to the SQLite database file")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="Start the web app (default)")
    for p in (parser, run):
        p.add_argument("--host", default="127.0.0.1", help="Address to listen on (use 0.0.0.0 to share on your network)")
        p.add_argument("--port", type=int, default=8000, help="Port to listen on (default 8000)")
        p.add_argument("--no-browser", action="store_true", help="Do not open a browser window")

    ca = sub.add_parser("create-admin", help="Add an administrator")
    ca.add_argument("--id")
    ca.add_argument("--name")
    ca.add_argument("--password")

    imp = sub.add_parser("import-users", help="Import associates from CSV")
    imp.add_argument("file")

    exp = sub.add_parser("export", help="Export the progress report to CSV")
    exp.add_argument("file")

    sub.add_parser("reseed", help="Reload course content from training/content.py")

    demo = sub.add_parser("demo-data", help="Add fictional learners for trying the reports")
    demo.add_argument("count", nargs="?", type=int, default=200)

    args = parser.parse_args(argv)
    handlers = {
        None: cmd_run, "run": cmd_run, "create-admin": cmd_create_admin, "import-users": cmd_import,
        "export": cmd_export, "reseed": cmd_reseed, "demo-data": cmd_demo,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()

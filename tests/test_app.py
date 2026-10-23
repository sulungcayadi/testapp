"""End-to-end and unit tests. Run with:  python -m unittest discover -s tests -v"""

import http.cookiejar
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training import content, db, services as svc  # noqa: E402
from training.web import make_server  # noqa: E402


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Client:
    def __init__(self, base):
        self.base = base
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def get(self, path):
        with self.opener.open(self.base + path) as r:
            return r.status, r.geturl(), r.read().decode("utf-8")

    def post(self, path, data, content_type=None, raw=None):
        body = raw if raw is not None else urllib.parse.urlencode(data, doseq=True).encode()
        req = urllib.request.Request(self.base + path, data=body)
        if content_type:
            req.add_header("Content-Type", content_type)
        with self.opener.open(req) as r:
            return r.status, r.geturl(), r.read().decode("utf-8")

    def csrf(self, path="/dashboard"):
        _, _, html = self.get(path)
        return re.search(r'name="csrf" value="([^"]+)"', html).group(1)


class AppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.tmp, "test.db")
        db.init_db(cls.db_path)
        cls.server = make_server("127.0.0.1", 0, cls.db_path, quiet=True)
        cls.base = "http://127.0.0.1:{}".format(cls.server.server_address[1])
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def conn(self):
        return db.connect(self.db_path)


class T01Setup(AppTestCase):
    def test_setup_then_login_and_register(self):
        c = Client(self.base)
        _, url, html = c.get("/")
        self.assertTrue(url.endswith("/setup"))
        self.assertIn("Create administrator", html)
        _, url, _ = c.post("/setup", {"org_name": "Acme", "associate_id": "admin", "name": "Admin",
                                      "password": "adminpass1", "password2": "adminpass1"})
        self.assertIn("/login", url)
        # setup is closed once an admin exists
        _, url, _ = c.get("/setup")
        self.assertIn("/login", url)

        # admin login lands on admin overview
        _, url, html = c.post("/login", {"associate_id": "admin", "password": "adminpass1"})
        self.assertTrue(url.endswith("/admin"))
        self.assertIn("Training overview", html)
        self.assertIn("Acme", html)

        # wrong password
        c2 = Client(self.base)
        _, _, html = c2.post("/login", {"associate_id": "admin", "password": "nope"})
        self.assertIn("not correct", html)


class T02LearnerJourney(AppTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        conn = db.connect(cls.db_path)
        svc.create_user(conn, "admin", "Admin", "adminpass1", role="admin")
        conn.close()

    def test_full_journey_to_certificate(self):
        c = Client(self.base)
        _, url, html = c.post("/register", {"associate_id": "A1", "name": "Pat Learner", "department": "Finance",
                                            "password": "learner123", "password2": "learner123"})
        self.assertTrue(url.endswith("/dashboard") or "/dashboard?" in url)
        self.assertIn("Hello, Pat Learner", html)
        self.assertIn("0% complete", html)

        # certificate locked
        _, url, html = c.get("/certificate")
        self.assertIn("/dashboard", url)

        conn = self.conn()
        modules = svc.list_modules(conn)
        token = c.csrf()

        # POST without csrf is rejected
        lesson = svc.module_lessons(conn, modules[0]["id"])[0]
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            c.post("/module/{}/lesson/{}".format(modules[0]["slug"], lesson["slug"]), {})
        self.assertEqual(ctx.exception.code, 400)

        for m in modules:
            _, _, html = c.get("/module/" + m["slug"])
            self.assertIn(m["title"].split(". ", 1)[1], html.replace("&amp;", "&"))
            for les in svc.module_lessons(conn, m["id"]):
                _, _, html = c.get("/module/{}/lesson/{}".format(m["slug"], les["slug"]))
                self.assertIn("Mark lesson complete", html)
                c.post("/module/{}/lesson/{}".format(m["slug"], les["slug"]), {"csrf": token})
            qs = svc.module_questions(conn, m["id"])
            if qs:
                _, _, html = c.get("/module/{}/quiz".format(m["slug"]))
                self.assertEqual(html.count('class="question"'), len(qs))
                # first attempt: all wrong except nothing -> fail
                data = {"csrf": token}
                for q in qs:
                    data["q{}".format(q["id"])] = str((q["correct_index"] + 1) % len(svc.question_options(q)))
                _, url, html = c.post("/module/{}/quiz".format(m["slug"]), data)
                self.assertIn("/attempt/", url)
                self.assertIn("Not passed yet", html)
                self.assertIn("Correct answer:", html)
                # second attempt: all right -> pass
                for q in qs:
                    data["q{}".format(q["id"])] = str(q["correct_index"])
                _, _, html = c.post("/module/{}/quiz".format(m["slug"]), data)
                self.assertIn("Passed", html)

        uid = svc.get_user_by_associate_id(conn, "A1")["id"]
        prog = svc.user_progress(conn, uid)
        self.assertTrue(prog["lessons_ok"])
        self.assertEqual(prog["passed_modules"], prog["quiz_modules"])
        self.assertFalse(prog["certified"])

        # lab
        for step in range(1, content.LAB_REQUIRED_STEPS + 1):
            c.post("/lab", {"csrf": token, "step": str(step), "done": "1", "note": "ok step {}".format(step)})
        _, _, html = c.get("/lab")
        self.assertIn("10 of 10 required steps done", html)
        c.post("/lab", {"csrf": token, "step": "3", "done": "0"})
        self.assertFalse(svc.user_progress(conn, uid)["lab_ok"])
        c.post("/lab", {"csrf": token, "step": "3", "done": "1"})

        # final: tampered question set is rejected
        _, _, html = c.get("/final?start=1")
        qids = re.search(r'name="qids" value="([^"]+)"', html).group(1)
        sig = re.search(r'name="sig" value="([^"]+)"', html).group(1)
        ids = [int(x) for x in qids.split(",")]
        self.assertEqual(len(ids), content.FINAL_QUESTION_COUNT)
        in_slide = {r[0] for r in conn.execute("SELECT id FROM questions WHERE in_slide_check = 1")}
        self.assertTrue(in_slide.issubset(set(ids)))
        _, url, _ = c.post("/final", {"csrf": token, "qids": qids.split(",")[0], "sig": sig})
        self.assertIn("error=", url)

        rows = {r["id"]: r for r in conn.execute("SELECT * FROM questions")}
        data = {"csrf": token, "qids": qids, "sig": sig}
        for i in ids:
            data["q{}".format(i)] = str(rows[i]["correct_index"])
        _, url, html = c.post("/final", data)
        self.assertIn("Final assessment result", html)
        self.assertIn("{0}/{0}".format(len(ids)), html)

        prog = svc.user_progress(conn, uid)
        self.assertTrue(prog["certified"])
        self.assertEqual(prog["percent"], 100)
        _, _, html = c.get("/certificate")
        self.assertIn("Certificate of Completion", html)
        self.assertIn("Pat Learner", html)

        # charter + download
        c.post("/charter", {"csrf": token, "agent_name": "Email Clarity Coach", "purpose": "Rewrite my emails",
                            "out_scope": "Unrelated topics"})
        _, _, html = c.get("/charter")
        self.assertIn("You are Email Clarity Coach.", html)
        _, _, txt = c.get("/charter.txt")
        self.assertIn("AGENT NAME: Email Clarity Coach", txt)

        # feedback
        c.post("/feedback", {"csrf": token, "rating": "5", "comment": "Great <b>course</b>"})
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0], 1)

        # learners cannot open admin pages
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            c.get("/admin")
        self.assertEqual(ctx.exception.code, 403)

        # templates page has copy buttons for all templates
        _, _, html = c.get("/templates")
        self.assertEqual(html.count('class="copy-btn"'), len(content.TEMPLATES))

        # admin sees the learner as certified, comment is escaped
        a = Client(self.base)
        a.post("/login", {"associate_id": "admin", "password": "adminpass1"})
        _, _, html = a.get("/admin/learners?status=Certified")
        self.assertIn("Pat Learner", html)
        _, _, html = a.get("/admin/feedback")
        self.assertIn("Great &lt;b&gt;course&lt;/b&gt;", html)
        _, _, csv_text = a.get("/admin/export.csv")
        self.assertIn("A1,Pat Learner", csv_text)
        self.assertIn("Certified", csv_text)
        conn.close()

    def test_logout_and_password_change(self):
        c = Client(self.base)
        c.post("/register", {"associate_id": "B2", "name": "Bo", "password": "password1", "password2": "password1"})
        token = c.csrf()
        _, url, _ = c.post("/account", {"csrf": token, "current": "password1", "password": "password2", "password2": "password2"})
        self.assertIn("/login", url)
        _, url, _ = c.get("/dashboard")
        self.assertIn("/login", url)
        _, url, _ = c.post("/login", {"associate_id": "B2", "password": "password2"})
        self.assertTrue(url.endswith("/dashboard"))
        token = c.csrf()
        c.post("/logout", {"csrf": token})
        _, url, _ = c.get("/dashboard")
        self.assertIn("/login", url)

    def test_duplicate_registration_rejected(self):
        c = Client(self.base)
        c.post("/register", {"associate_id": "C3", "name": "Cy", "password": "password1", "password2": "password1"})
        c2 = Client(self.base)
        _, _, html = c2.post("/register", {"associate_id": "c3", "name": "Other", "password": "password9", "password2": "password9"})
        self.assertIn("already registered", html)


class T03Admin(AppTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        conn = db.connect(cls.db_path)
        svc.create_user(conn, "admin", "Admin", "adminpass1", role="admin")
        conn.close()

    def login(self):
        c = Client(self.base)
        c.post("/login", {"associate_id": "admin", "password": "adminpass1"})
        return c

    def test_import_upload_and_claim(self):
        c = self.login()
        token = c.csrf("/admin/import")
        boundary = "----testboundary"
        csv_text = "associate_id,name,email,department,location\nX1,Xia One,x1@example.com,Sales,Tokyo\nX2,Xia Two,,Sales,\n,Missing,,,\n"
        body = (
            "--{b}\r\nContent-Disposition: form-data; name=\"csrf\"\r\n\r\n{t}\r\n"
            "--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.csv\"\r\nContent-Type: text/csv\r\n\r\n{csv}\r\n"
            "--{b}--\r\n"
        ).format(b=boundary, t=token, csv=csv_text).encode()
        _, _, html = c.post("/admin/import", None, "multipart/form-data; boundary=" + boundary, raw=body)
        self.assertIn("2 added, 0 updated, 1 skipped", html)

        # paste update
        _, _, html = c.post("/admin/import", {"csrf": token, "csv_text": "associate_id,name,department\nX1,Xia Uno,Marketing\n"})
        self.assertIn("0 added, 1 updated", html)

        # imported associate claims their record by registering
        learner = Client(self.base)
        _, url, _ = learner.post("/register", {"associate_id": "X1", "name": "Xia Uno", "department": "Ignored",
                                               "password": "password1", "password2": "password1"})
        self.assertIn("/dashboard", url)
        conn = self.conn()
        u = svc.get_user_by_associate_id(conn, "X1")
        self.assertEqual(u["department"], "Marketing")

        _, _, html = c.get("/admin/learners?department=Marketing")
        self.assertIn("Xia Uno", html)
        self.assertIn("Registered", html)

        # reset password lets them register again; progress kept
        svc.complete_lesson(conn, u["id"], conn.execute("SELECT id FROM lessons LIMIT 1").fetchone()[0])
        c.post("/admin/learner/{}".format(u["id"]), {"csrf": token, "action": "reset-password"})
        self.assertIsNone(svc.get_user_by_associate_id(conn, "X1")["password_hash"])
        learner2 = Client(self.base)
        learner2.post("/register", {"associate_id": "X1", "name": "Xia Uno", "password": "password7", "password2": "password7"})
        self.assertEqual(len(svc.completed_lesson_ids(conn, u["id"])), 1)
        conn.close()

    def test_question_bank_and_settings(self):
        c = self.login()
        token = c.csrf("/admin/questions")
        conn = self.conn()
        mod = svc.list_modules(conn)[0]
        _, url, _ = c.post("/admin/questions", {"csrf": token, "action": "add", "module_id": str(mod["id"]),
                                                "category": "Org", "prompt": "Who approves agent sharing here?",
                                                "opt0": "Your manager", "opt1": "Anyone", "opt2": "", "opt3": "",
                                                "correct": "0", "rationale": "Per our internal policy."})
        self.assertIn("ORG-Q01", urllib.parse.unquote_plus(url))
        q = conn.execute("SELECT * FROM questions WHERE code = 'ORG-Q01'").fetchone()
        self.assertEqual(json.loads(q["options_json"]), ["Your manager", "Anyone"])
        c.post("/admin/questions", {"csrf": token, "action": "toggle", "id": str(q["id"]), "active": "0"})
        self.assertEqual(conn.execute("SELECT active FROM questions WHERE id = ?", (q["id"],)).fetchone()[0], 0)

        # reseed keeps custom questions and their state
        db.seed_content(conn)
        self.assertEqual(conn.execute("SELECT active FROM questions WHERE id = ?", (q["id"],)).fetchone()[0], 0)

        _, url, _ = c.post("/admin/settings", {"csrf": token, "pass_mark": "150", "org_name": "X"})
        self.assertIn("error=", url)
        c.post("/admin/settings", {"csrf": token, "pass_mark": "70", "org_name": "Globex"})
        self.assertEqual(db.get_setting(conn, "pass_mark"), "70")
        _, _, html = c.get("/admin")
        self.assertIn("Globex", html)
        conn.close()


class T04Services(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "s.db")
        db.init_db(self.path)
        self.conn = db.connect(self.path)

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_content_integrity(self):
        codes = [q["code"] for q in content.QUESTIONS]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(sum(1 for q in content.QUESTIONS if q["in_slide_check"]), 3)
        slugs = {m["slug"] for m in content.MODULES}
        for q in content.QUESTIONS:
            self.assertIn(q["module"], slugs)
            self.assertTrue(0 <= q["correct"] < len(q["options"]), q["code"])
        scenario = sum(1 for q in content.QUESTIONS if q["scenario"])
        self.assertGreaterEqual(scenario * 2, len(content.QUESTIONS))
        self.assertEqual(len(content.LAB_STEPS), 12)

    def test_password_hashing(self):
        h = svc.hash_password("secret123")
        self.assertTrue(svc.verify_password("secret123", h))
        self.assertFalse(svc.verify_password("secret124", h))
        self.assertFalse(svc.verify_password("x", None))

    def test_reseed_is_idempotent(self):
        before = self.conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
        db.seed_content(self.conn)
        db.seed_content(self.conn)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0], before)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0], len(content.QUESTIONS))

    def test_reports_scale_to_10000_associates(self):
        import time
        rows = "\n".join("E{0:05d},Person {0},,Dept {1},".format(i, i % 25) for i in range(10000))
        created, updated, errors = svc.import_users_csv(self.conn, "associate_id,name,email,department,location\n" + rows)
        self.assertEqual((created, updated, errors), (10000, 0, []))
        t = time.time()
        stats = svc.overview_stats(self.conn)
        page, total = svc.learner_rows(self.conn, department="Dept 3", limit=50)
        csv_text = svc.export_progress_csv(self.conn)
        elapsed = time.time() - t
        self.assertEqual(stats["total"], 10000)
        self.assertEqual(len(stats["departments"]), 25)
        self.assertEqual(total, 400)
        self.assertEqual(len(page), 50)
        self.assertEqual(csv_text.count("\n"), 10001)
        self.assertLess(elapsed, 10)

    def test_grade_and_pass_mark(self):
        u = svc.create_user(self.conn, "Z1", "Zed", "password1")
        qs = svc.module_questions(self.conn, svc.list_modules(self.conn)[1]["id"])
        ids = [q["id"] for q in qs]
        ans = {q["id"]: q["correct_index"] for q in qs}
        ans[ids[0]] = None
        a = svc.grade_attempt(self.conn, u["id"], "module", ids, ans, qs[0]["module_id"])
        row = self.conn.execute("SELECT * FROM quiz_attempts WHERE id = ?", (a,)).fetchone()
        self.assertEqual(row["score"], len(ids) - 1)
        self.assertEqual(row["passed"], int((len(ids) - 1) * 100 >= 80 * len(ids)))

    def test_charter_instructions(self):
        text = svc.charter_instructions({"agent_name": "Notes Helper", "purpose": "Turn notes into actions"})
        self.assertIn("You are Notes Helper.", text)
        self.assertIn("recommend standard Copilot Chat", text)


if __name__ == "__main__":
    unittest.main()

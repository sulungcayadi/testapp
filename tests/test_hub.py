"""Tests for the agent hub, community, insights and every page in every language.
Run with:  python -m unittest discover -s tests -v"""

import os
import re
import sys
import unittest
import urllib.error
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from training import content, db, hub, i18n, services as svc  # noqa: E402
from training.db import now  # noqa: E402
from test_app import AppTestCase, Client  # noqa: E402


def certify(conn, user_id):
    """Shortcut: complete the core course for a user without clicking through it."""
    for m in svc.list_modules(conn, "core"):
        for les in svc.module_lessons(conn, m["id"]):
            svc.complete_lesson(conn, user_id, les["id"])
        if svc.module_questions(conn, m["id"]):
            conn.execute("INSERT INTO quiz_attempts(user_id, kind, module_id, score, total, passed, completed_at) "
                         "VALUES (?, 'module', ?, 1, 1, 1, ?)", (user_id, m["id"], now()))
    for step in range(1, content.LAB_REQUIRED_STEPS + 1):
        svc.set_lab_step(conn, user_id, step, True, "ok")
    conn.execute("INSERT INTO quiz_attempts(user_id, kind, module_id, score, total, passed, completed_at) "
                 "VALUES (?, 'final', NULL, 15, 15, 1, ?)", (user_id, now()))
    conn.commit()


AGENT_FORM = {
    "name": "Travel Policy Helper", "purpose": "Answers travel policy questions from the travel policy site",
    "audience": "Finance team", "tier": "2", "knowledge_types": ["sharepoint"],
    "knowledge_detail": "Travel policy SharePoint site", "sensitivity": "internal", "sharing_scope": "team",
    "kpi_name": "Minutes to answer a travel question", "kpi_baseline": "15 minutes",
    "test_notes": "1. On topic: correct. 2. Vague: asked a question. 3. Off topic: declined.",
    "link": "", "review_date": "", "idea_id": "",
}


class HubTestCase(AppTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        conn = db.connect(cls.db_path)
        svc.create_user(conn, "admin", "Admin", "adminpass1", role="admin")
        svc.create_user(conn, "B1", "Bo Builder", "builder123", department="Finance")
        svc.create_user(conn, "C1", "Cam Coach", "coach1234", department="Finance")
        conn.execute("UPDATE users SET is_reviewer = 1 WHERE associate_id = 'C1'")
        conn.commit()
        conn.close()

    def login(self, aid, pw):
        c = Client(self.base)
        c.post("/login", {"associate_id": aid, "password": pw})
        return c


class T10AgentLifecycle(HubTestCase):
    def test_register_submit_review_value(self):
        b = self.login("B1", "builder123")
        token = b.csrf("/hub")
        conn = self.conn()
        bid = svc.get_user_by_associate_id(conn, "B1")["id"]

        # an idea, then an agent built from it
        _, url, _ = b.post("/hub/ideas", {"csrf": token, "title": "Travel questions bot",
                                          "description": "We answer the same travel questions every week.",
                                          "category": "finance"})
        idea_id = int(re.search(r"/hub/ideas/(\d+)", url).group(1))
        form = dict(AGENT_FORM, csrf=token, idea_id=str(idea_id))
        _, url, html = b.post("/hub/agents/new", form)
        agent_id = int(re.search(r"/hub/agents/(\d+)", url).group(1))
        self.assertIn("needs a governance review", html)

        # not certified yet: submission is blocked
        _, url, _ = b.post("/hub/agents/{}".format(agent_id), {"csrf": token, "action": "submit"})
        self.assertIn("error=", url)
        self.assertEqual(hub.get_agent(conn, agent_id)["status"], "registered")

        certify(conn, bid)
        _, url, _ = b.post("/hub/agents/{}".format(agent_id), {"csrf": token, "action": "submit"})
        self.assertNotIn("error=", url)
        self.assertEqual(hub.get_agent(conn, agent_id)["status"], "in_review")

        # the coach was notified and sees it in the queue
        coach = self.login("C1", "coach1234")
        ctoken = coach.csrf("/hub/reviews")
        _, _, html = coach.get("/hub/reviews")
        self.assertIn("Travel Policy Helper", html)
        _, _, html = coach.get("/inbox")
        self.assertIn("Travel Policy Helper", html)

        # approving without every checklist item fails
        _, url, _ = coach.post("/hub/agents/{}".format(agent_id), {"csrf": ctoken, "action": "review",
                                                                    "decision": "approved", "checks": ["one_purpose"]})
        self.assertIn("error=", url)
        # the owner cannot review their own agent
        with self.assertRaises(urllib.error.HTTPError):
            b.post("/hub/agents/{}".format(agent_id), {"csrf": token, "action": "review", "decision": "approved"})

        checks = [k for k, _ in content.GOVERNANCE_CHECKLIST]
        coach.post("/hub/agents/{}".format(agent_id), {"csrf": ctoken, "action": "review", "decision": "approved",
                                                         "checks": checks, "comment": "Good"})
        a = hub.get_agent(conn, agent_id)
        self.assertEqual(a["status"], "approved")
        self.assertEqual(a["review_date"], (date.today() + timedelta(days=90)).isoformat())
        self.assertEqual(hub.get_idea(conn, idea_id, bid)["status"], "built")
        self.assertTrue(hub.builder_levels(conn, svc.get_user_by_associate_id(conn, "B1"))["level2"])

        # approved agents appear in the catalogue for everyone
        _, _, html = coach.get("/hub/agents?view=catalogue")
        self.assertIn("Travel Policy Helper", html)

        # widening the data sensitivity sends it back for review
        b.post("/hub/agents/{}".format(agent_id), dict(AGENT_FORM, csrf=token, action="edit", sensitivity="confidential"))
        self.assertEqual(hub.get_agent(conn, agent_id)["status"], "registered")
        conn.execute("UPDATE agents SET status = 'approved', review_date = ? WHERE id = ?",
                     ((date.today() - timedelta(days=1)).isoformat(), agent_id))
        conn.commit()
        self.assertEqual([r["id"] for r in hub.overdue_agents(conn)], [agent_id])

        # value review records the KPI result and reaches level 3
        b.post("/hub/agents/{}".format(agent_id), {"csrf": token, "action": "value", "kpi_result": "4 minutes", "keep": "1"})
        a = hub.get_agent(conn, agent_id)
        self.assertEqual(a["kpi_result"], "4 minutes")
        self.assertTrue(hub.builder_levels(conn, svc.get_user_by_associate_id(conn, "B1"))["level3"])
        self.assertEqual(hub.overdue_agents(conn), [])

        # hours saved
        b.post("/hub", {"csrf": token, "hours": "2.5", "agent_id": str(agent_id), "note": "faster"})
        m = hub.adoption_metrics(conn)
        self.assertEqual(m["hours_avg"], 2.5)
        self.assertEqual(m["by_status"]["approved"], 1)
        conn.close()

    def test_tier3_needs_coe(self):
        conn = self.conn()
        owner = svc.get_user_by_associate_id(conn, "B1")
        coach = svc.get_user_by_associate_id(conn, "C1")
        admin = svc.get_user_by_associate_id(conn, "admin")
        certify(conn, owner["id"])
        aid = hub.create_agent(conn, owner, dict(AGENT_FORM, name="Order bot", tier="3", sharing_scope="private"), ["none"])
        a = hub.get_agent(conn, aid)
        self.assertTrue(hub.needs_review(a["sharing_scope"], a["sensitivity"], a["tier"]))
        self.assertIsNone(hub.submit_for_review(conn, a, owner))
        a = hub.get_agent(conn, aid)
        with self.assertRaises(ValueError):
            hub.review_agent(conn, a, coach, "approved", [k for k, _ in content.GOVERNANCE_CHECKLIST], "")
        hub.review_agent(conn, a, admin, "changes", [], "Needs IT build in Copilot Studio")
        self.assertEqual(hub.get_agent(conn, aid)["status"], "changes")
        conn.close()


class T11Community(HubTestCase):
    def test_ideas_licences_events_prompts_coe(self):
        b = self.login("B1", "builder123")
        token = b.csrf("/hub")
        coach = self.login("C1", "coach1234")
        ctoken = coach.csrf("/hub")
        admin = self.login("admin", "adminpass1")
        atoken = admin.csrf("/admin")
        conn = self.conn()

        # ideas: vote toggles, comments notify the author
        _, url, _ = b.post("/hub/ideas", {"csrf": token, "title": "Meeting notes", "description": "Summaries", "category": "meetings"})
        iid = int(re.search(r"/hub/ideas/(\d+)", url).group(1))
        coach.post("/hub/ideas/{}".format(iid), {"csrf": ctoken, "action": "vote"})
        coach.post("/hub/ideas/{}".format(iid), {"csrf": ctoken, "action": "comment", "body": "Yes please"})
        idea = hub.get_idea(conn, iid, 0)
        self.assertEqual(idea["votes"], 2)
        self.assertGreater(hub.unread_count(conn, svc.get_user_by_associate_id(conn, "B1")["id"]), 0)
        coach.post("/hub/ideas/{}".format(iid), {"csrf": ctoken, "action": "status", "status": "planned"})
        self.assertEqual(hub.get_idea(conn, iid, 0)["status"], "planned")

        # licences in waves
        b.post("/hub/licences", {"csrf": token, "seats": "25", "use_case": "Monthly close", "expected_hours": "3"})
        req = hub.licence_requests(conn)[0]
        admin.post("/hub/licences", {"csrf": atoken, "action": "decide", "id": str(req["id"]), "decision": "approve",
                                     "wave": "Wave 1", "note": ""})
        req = hub.licence_requests(conn)[0]
        self.assertEqual((req["status"], req["wave"]), ("approved", "Wave 1"))
        self.assertEqual(hub.adoption_metrics(conn)["licences_approved"], 25)

        # events: coaches host, anyone joins; learners cannot host
        when = (date.today() + timedelta(days=3)).isoformat() + "T10:00"
        coach.post("/community", {"csrf": ctoken, "kind": "promptathon", "title": "Finance promptathon",
                                  "starts_at": when, "place": "Room 1", "details": ""})
        ev = hub.upcoming_events(conn, 0)[0]
        b.post("/community", {"csrf": token, "action": "signup", "id": str(ev["id"])})
        self.assertEqual(hub.upcoming_events(conn, 0)[0]["signups"], 1)
        with self.assertRaises(urllib.error.HTTPError):
            b.post("/community", {"csrf": token, "kind": "promptathon", "title": "x", "starts_at": when})

        # prompt library with ratings
        b.post("/community/prompts", {"csrf": token, "title": "Summarize a thread", "body": "Summarize this thread in 5 bullets.",
                                      "category": "email"})
        p = hub.list_prompts(conn, 0)[0]
        coach.post("/community/prompts", {"csrf": ctoken, "action": "rate", "id": str(p["id"]), "rating": "4"})
        self.assertEqual(hub.list_prompts(conn, 0)[0]["avg_rating"], 4)

        # Ask the CoE: data questions go to administrators only
        b.post("/help", {"csrf": token, "topic": "data", "question": "Can I use customer data?"})
        q = hub.coe_questions(conn)[0]
        coach_id = svc.get_user_by_associate_id(conn, "C1")["id"]
        self.assertFalse(any("CoE" in n["message"] for n in hub.notifications(conn, coach_id)))
        admin.post("/help", {"csrf": atoken, "action": "answer", "id": str(q["id"]), "answer": "Only confidential-approved agents."})
        self.assertTrue(hub.coe_questions(conn)[0]["answer"])

        # admin makes someone a coach
        bid = svc.get_user_by_associate_id(conn, "B1")["id"]
        admin.post("/admin/learner/{}".format(bid), {"csrf": atoken, "action": "coach", "value": "1"})
        self.assertEqual(svc.get_user_by_associate_id(conn, "B1")["is_reviewer"], 1)
        conn.close()


GET_PAGES = [
    "/", "/dashboard", "/paths", "/assess", "/lab", "/charter", "/templates", "/feedback", "/toolkit", "/resources",
    "/glossary", "/quickref", "/facilitator", "/account", "/hub", "/hub/agents", "/hub/agents?view=catalogue",
    "/hub/agents?view=all", "/hub/agents/new", "/hub/reviews", "/hub/ideas", "/hub/licences", "/community",
    "/community/prompts", "/help", "/inbox", "/insights", "/insights/benchmarks", "/final",
    "/admin", "/admin/learners", "/admin/import", "/admin/questions", "/admin/feedback", "/admin/settings",
]


class T12EveryPageEveryLanguage(HubTestCase):
    def test_pages_render_without_missing_translations(self):
        conn = self.conn()
        admin_user = svc.get_user_by_associate_id(conn, "admin")
        b = svc.get_user_by_associate_id(conn, "B1")
        certify(conn, b["id"])
        aid = hub.create_agent(conn, b, AGENT_FORM, ["sharepoint"])
        hub.submit_for_review(conn, hub.get_agent(conn, aid), b)
        hub.create_idea(conn, b, "Idea", "Text", "other")
        hub.add_prompt(conn, b, "Prompt", "Body", "other")
        hub.ask_coe(conn, b, "howto", "How?")
        hub.create_licence_request(conn, b, 5, "Use", 2)
        hub.create_event(conn, admin_user, "office_hours", "Office hours",
                         (date.today() + timedelta(days=1)).isoformat() + "T09:00", "Teams", "")
        modules = svc.list_modules(conn)
        conn.close()
        pages = list(GET_PAGES) + ["/hub/agents/{}".format(aid), "/hub/ideas/1", "/admin/learner/{}".format(b["id"])]
        for m in modules:
            pages.append("/module/" + m["slug"])
            les = svc.module_lessons(self.conn(), m["id"])
            pages += ["/module/{}/lesson/{}".format(m["slug"], l["slug"]) for l in les]
            pages.append("/module/{}/quiz".format(m["slug"]))
        c = self.login("admin", "adminpass1")
        for code in i18n.CODES:
            c.get("/lang?code={}&next=/dashboard".format(code))
            i18n.MISSING.clear()
            for path in pages:
                with self.subTest(lang=code, path=path):
                    status, _, html = c.get(path)
                    self.assertEqual(status, 200)
                    self.assertIn('lang="{}"'.format(code), html)
            with self.subTest(lang=code, check="missing"):
                self.assertEqual(sorted(i18n.MISSING)[:20], [])  # first 20 shown


class T13Translations(unittest.TestCase):
    def test_every_locale_covers_every_segment(self):
        from training import i18n_tools
        for code in i18n.CODES:
            if code == i18n.DEFAULT:
                continue
            with self.subTest(lang=code):
                self.assertEqual(i18n_tools.missing(code)[:20], [])
                self.assertEqual(i18n_tools.placeholder_errors(code)[:20], [])

    def test_html_segments_round_trip(self):
        src = '<p>Open <strong>Agents</strong> &gt; New agent.</p><ul><li>One</li><li>Two <a href="x">link</a></li></ul><pre>Line one\nLine two</pre>'
        self.assertEqual(i18n.html_segments(src),
                         ["Open <strong>Agents</strong> &gt; New agent.", "One", "Two <a href=\"x\">link</a>", "Line one", "Line two"])
        i18n._cache["xx"] = {"One": "Satu", "Line two": "Baris dua"}
        try:
            out = i18n.html("xx", src)
        finally:
            i18n._cache.pop("xx")
            i18n.MISSING.clear()
        self.assertIn("<li>Satu</li>", out)
        self.assertIn("Line one\nBaris dua", out)


if __name__ == "__main__":
    unittest.main()

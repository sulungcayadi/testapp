"""HTTP server and routing, built only on the Python standard library."""

import hmac
import mimetypes
import os
import re
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from . import services as svc
from . import pages_admin as A
from . import pages_hub as H
from . import pages_learn as L
from .core import COOKIE, HttpError, Redirect, Request, error_page
from .db import connect

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

PUBLIC = "public"
LOGIN = "login"

ROUTES = [
    (r"/setup", L.page_setup, PUBLIC),
    (r"/login", L.page_login, PUBLIC),
    (r"/register", L.page_register, PUBLIC),
    (r"/lang", L.page_lang, PUBLIC),
    (r"/logout", L.page_logout, LOGIN),
    (r"/", L.page_home, LOGIN),
    (r"/account", L.page_account, LOGIN),
    (r"/dashboard", L.page_dashboard, LOGIN),
    (r"/paths", L.page_paths, LOGIN),
    (r"/assess", L.page_assess, LOGIN),
    (r"/module/([\w-]+)", L.page_module, LOGIN),
    (r"/module/([\w-]+)/lesson/([\w-]+)", L.page_lesson, LOGIN),
    (r"/module/([\w-]+)/quiz", L.page_module_quiz, LOGIN),
    (r"/final", L.page_final, LOGIN),
    (r"/attempt/(\d+)", L.page_attempt, LOGIN),
    (r"/lab", L.page_lab, LOGIN),
    (r"/charter", L.page_charter, LOGIN),
    (r"/charter\.txt", L.page_charter_txt, LOGIN),
    (r"/templates", L.page_templates, LOGIN),
    (r"/certificate", L.page_certificate, LOGIN),
    (r"/feedback", L.page_feedback, LOGIN),
    (r"/toolkit", L.page_toolkit, LOGIN),
    (r"/resources", L.page_resources, LOGIN),
    (r"/glossary", L.page_glossary, LOGIN),
    (r"/quickref", L.page_quickref, LOGIN),
    (r"/facilitator", L.page_facilitator, LOGIN),
    (r"/hub", H.page_hub, LOGIN),
    (r"/hub/agents", H.page_agents, LOGIN),
    (r"/hub/agents/new", H.page_agent_new, LOGIN),
    (r"/hub/agents/(\d+)", H.page_agent, LOGIN),
    (r"/hub/reviews", H.page_reviews, LOGIN),
    (r"/hub/ideas", H.page_ideas, LOGIN),
    (r"/hub/ideas/(\d+)", H.page_idea, LOGIN),
    (r"/hub/licences", H.page_licences, LOGIN),
    (r"/community", H.page_community, LOGIN),
    (r"/community/prompts", H.page_prompts, LOGIN),
    (r"/help", H.page_help, LOGIN),
    (r"/inbox", H.page_inbox, LOGIN),
    (r"/insights", H.page_insights, LOGIN),
    (r"/insights/benchmarks", H.page_benchmarks, LOGIN),
    (r"/admin", A.page_admin, LOGIN),
    (r"/admin/learners", A.page_admin_learners, LOGIN),
    (r"/admin/learner/(\d+)", A.page_admin_learner, LOGIN),
    (r"/admin/export\.csv", A.page_admin_export, LOGIN),
    (r"/admin/import", A.page_admin_import, LOGIN),
    (r"/admin/questions", A.page_admin_questions, LOGIN),
    (r"/admin/questions\.csv", A.page_admin_questions_csv, LOGIN),
    (r"/admin/feedback", A.page_admin_feedback, LOGIN),
    (r"/admin/settings", A.page_admin_settings, LOGIN),
]
COMPILED = [(re.compile("^" + pattern + "$"), fn, access) for pattern, fn, access in ROUTES]


class Handler(BaseHTTPRequestHandler):
    server_version = "T1Training/2.0"
    db_path = None
    quiet = False

    def log_message(self, fmt, *args):
        if not self.quiet:
            super().log_message(fmt, *args)

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def send(self, status, ctype, body, headers=None, req=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        if ctype.startswith("text/html"):
            self.send_header("Cache-Control", "no-store")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        if req is not None:
            if req.set_cookie is not None:
                if req.set_cookie:
                    self.send_header("Set-Cookie", "{}={}; Path=/; HttpOnly; SameSite=Lax; Max-Age={}".format(
                        COOKIE, req.set_cookie, svc.SESSION_HOURS * 3600))
                else:
                    self.send_header("Set-Cookie", "{}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0".format(COOKIE))
            for c in req.cookies_out:
                self.send_header("Set-Cookie", c)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def serve_static(self, name):
        path = os.path.normpath(os.path.join(STATIC_DIR, name))
        if not path.startswith(STATIC_DIR + os.sep) or not os.path.isfile(path):
            return self.send(404, "text/plain; charset=utf-8", b"Not found")
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript",):
            ctype += "; charset=utf-8"
        with open(path, "rb") as f:
            data = f.read()
        self.send(200, ctype, data, {"Cache-Control": "max-age=300"})

    def dispatch(self, method):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/static/"):
            return self.serve_static(parsed.path[len("/static/"):])
        req = Request(self, method)
        req.conn = connect(self.db_path)
        try:
            req.user, req.csrf = svc.session_user(req.conn, req.token)
            req.choose_lang()
            if not svc.admin_exists(req.conn) and req.path not in ("/setup", "/lang"):
                raise Redirect("/setup")
            for pattern, fn, access in COMPILED:
                m = pattern.match(req.path)
                if not m:
                    continue
                if access == LOGIN and not req.user:
                    raise Redirect("/login")
                if method == "POST":
                    req.read_body()
                    if req.user and not hmac.compare_digest(req.get("csrf"), req.csrf or ""):
                        raise HttpError(400, "Your form expired. Go back, refresh the page and try again.")
                result = fn(req, *m.groups())
                if isinstance(result, tuple):
                    ctype, body, headers = result
                    return self.send(200, ctype, body, headers, req)
                return self.send(200, "text/html; charset=utf-8", result.encode("utf-8"), req=req)
            raise HttpError(404, "Page not found.")
        except Redirect as r:
            self.send(303, "text/plain; charset=utf-8", b"", {"Location": r.location}, req)
        except HttpError as e:
            self.send(e.status, "text/html; charset=utf-8", error_page(req, e.status, e.message).encode("utf-8"), req=req)
        except Exception:
            traceback.print_exc()
            self.send(500, "text/plain; charset=utf-8", b"Something went wrong. Check the server window for details.")
        finally:
            req.conn.close()


def make_server(host, port, db_path=None, quiet=False):
    handler = type("BoundHandler", (Handler,), {"db_path": db_path, "quiet": quiet})
    return ThreadingHTTPServer((host, port), handler)

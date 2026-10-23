"""Request handling helpers and the shared page layout."""

import email.parser
import email.policy
import hashlib
import hmac
import html
import secrets
from http import cookies
from urllib.parse import parse_qs, quote, urlencode, urlparse

from . import content, hub, i18n
from .db import get_setting, set_setting

COOKIE = "t1_session"
LANG_COOKIE = "t1_lang"
PAGE_SIZE = 50
MAX_BODY = 20 * 1024 * 1024  # 20 MB, enough for a CSV of 10,000+ associates

esc = html.escape


class Raw(str):
    """A value that is already safe HTML and must not be escaped again."""


class Redirect(Exception):
    def __init__(self, location):
        self.location = location


class HttpError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message


def redirect(path, msg=None, error=None):
    params = {}
    if msg:
        params["msg"] = msg
    if error:
        params["error"] = error
    if params:
        path += ("&" if "?" in path else "?") + urlencode(params)
    raise Redirect(path)


class Request:
    def __init__(self, handler, method):
        self.handler = handler
        self.method = method
        parsed = urlparse(handler.path)
        self.full_path = handler.path
        self.path = parsed.path.rstrip("/") or "/"
        self.query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        self.form = {}
        self.form_lists = {}
        self.files = {}
        self.conn = None
        self.user = None
        self.csrf = None
        self.token = None
        self.lang = i18n.DEFAULT
        self.cookies_out = []
        jar = cookies.SimpleCookie()
        try:
            jar.load(handler.headers.get("Cookie", ""))
        except cookies.CookieError:
            pass
        self.jar = jar
        if COOKIE in jar:
            self.token = jar[COOKIE].value
        self.set_cookie = None

    def choose_lang(self):
        if self.user and self.user["lang"] in i18n.CODES:
            self.lang = self.user["lang"]
        elif LANG_COOKIE in self.jar and self.jar[LANG_COOKIE].value in i18n.CODES:
            self.lang = self.jar[LANG_COOKIE].value
        else:
            self.lang = i18n.pick(self.handler.headers.get("Accept-Language", ""))

    def t(self, text, **kw):
        safe = {k: (v if isinstance(v, Raw) else esc(str(v))) for k, v in kw.items()}
        return i18n.t(self.lang, text, **safe)

    def read_body(self):
        length = int(self.handler.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise HttpError(413, "The upload is too large.")
        raw = self.handler.rfile.read(length) if length else b""
        ctype = self.handler.headers.get("Content-Type", "")
        if ctype.startswith("multipart/form-data"):
            msg = email.parser.BytesParser(policy=email.policy.HTTP).parsebytes(
                b"Content-Type: " + ctype.encode() + b"\r\n\r\n" + raw
            )
            for part in msg.iter_parts():
                name = part.get_param("name", header="content-disposition")
                if not name:
                    continue
                payload = part.get_payload(decode=True) or b""
                if part.get_filename():
                    self.files[name] = payload
                else:
                    value = payload.decode("utf-8", "replace")
                    self.form[name] = value
                    self.form_lists.setdefault(name, []).append(value)
        else:
            parsed = parse_qs(raw.decode("utf-8", "replace"), keep_blank_values=True)
            self.form_lists = parsed
            self.form = {k: v[0] for k, v in parsed.items()}

    def get(self, key, default=""):
        return self.form.get(key, default)

    def getlist(self, key):
        return self.form_lists.get(key, [])


# ---------------------------------------------------------------------------
# Small HTML helpers
# ---------------------------------------------------------------------------

def csrf_field(req):
    return '<input type="hidden" name="csrf" value="{}">'.format(esc(req.csrf or ""))


def progress_bar(percent, label):
    return (
        '<div class="progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{0}" '
        'aria-label="{1}"><div class="bar" style="width:{0}%"></div></div><div class="progress-label">{1}</div>'
    ).format(percent, esc(label))


def check(req, ok):
    return '<span class="badge ok">{}</span>'.format(req.t("Done")) if ok else '<span class="badge todo">{}</span>'.format(req.t("To do"))


def flash_html(text):
    return '<div class="flash err" role="alert">{}</div>'.format(esc(text)) if text else ""


def options(pairs, selected, req=None, list_name=None):
    out = []
    for key, label in pairs:
        if req and list_name:
            label = i18n.label(req.lang, list_name, key, label)
        out.append('<option value="{}"{}>{}</option>'.format(esc(key), " selected" if key == selected else "", esc(label)))
    return "".join(out)


def pct(n, d):
    return round(100 * n / d) if d else 0


def lbl(req, list_name, pairs, key):
    return i18n.label(req.lang, list_name, key, dict(pairs).get(key, key))


# ---------------------------------------------------------------------------
# Final-assessment signing
# ---------------------------------------------------------------------------

def _secret(conn):
    value = get_setting(conn, "secret")
    if not value:
        value = secrets.token_hex(32)
        set_setting(conn, "secret", value)
        conn.commit()
    return value


def sign(conn, text):
    return hmac.new(_secret(conn).encode(), text.encode(), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def nav_links(req):
    T = req.t
    links = [
        ("dashboard", "/dashboard", T("My course")),
        ("lab", "/lab", T("Lab")),
        ("toolkit", "/toolkit", T("Toolkit")),
        ("hub", "/hub", T("Agent hub")),
        ("ideas", "/hub/ideas", T("Ideas")),
        ("insights", "/insights", T("Insights")),
    ]
    if req.user["role"] == "admin":
        links.append(("admin", "/admin", T("Admin")))
    return links


def lang_switcher(req):
    opts = "".join(
        '<option value="{}"{}>{}</option>'.format(code, " selected" if code == req.lang else "", esc(name))
        for code, name in i18n.LANGS
    )
    return """<form method="get" action="/lang" class="lang-form">
<label class="sr-only" for="lang-select">{label}</label>
<select id="lang-select" name="code" class="lang-select" aria-label="{label}">{opts}</select>
<input type="hidden" name="next" value="{next}">
<noscript><button type="submit" class="btn small">OK</button></noscript>
</form>""".format(label=req.t("Language"), opts=opts, next=esc(req.full_path))


def layout(req, title, body, active=""):
    T = req.t
    org = esc(get_setting(req.conn, "org_name", "Our Organization"))
    nav = ""
    if req.user:
        items = "".join(
            '<a href="{}" class="{}">{}</a>'.format(url, "active" if key == active else "", label)
            for key, url, label in nav_links(req)
        )
        unread = hub.unread_count(req.conn, req.user["id"])
        bell = '<a href="/inbox" class="bell" aria-label="{label}">&#128276;{badge}</a>'.format(
            label=T("Notifications"),
            badge='<span class="count">{}</span>'.format(unread) if unread else "",
        )
        nav = """<nav class="topnav" aria-label="{main}">{items}</nav>
<div class="userbox">{switch}{bell}<a href="/account">{name}</a>
<form method="post" action="/logout" class="inline">{csrf}<button class="linklike" type="submit">{signout}</button></form></div>""".format(
            main=T("Main menu"), items=items, switch=lang_switcher(req), bell=bell,
            name=esc(req.user["name"]), csrf=csrf_field(req), signout=T("Sign out"),
        )
    else:
        nav = '<div class="userbox">{}</div>'.format(lang_switcher(req))
    flash = ""
    if req.query.get("msg"):
        flash += '<div class="flash ok" role="status">{}</div>'.format(esc(T(req.query["msg"])))
    if req.query.get("error"):
        flash += '<div class="flash err" role="alert">{}</div>'.format(esc(T(req.query["error"])))
    return """<!doctype html>
<html lang="{lang}" data-copy="{copy}" data-copied="{copied}" data-copyfail="{copyfail}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | {app}</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<a class="skip" href="#main">{skip}</a>
<header class="site">
<div class="brand"><a href="/"><span class="logo" aria-hidden="true">T1</span> {app}</a>
<span class="org">{org}</span></div>
{nav}
</header>
<main id="main">
{flash}
{body}
</main>
<footer class="site">{footer}</footer>
<script src="/static/app.js"></script>
</body>
</html>""".format(
        lang=esc(req.lang), copy=esc(T("Copy")), copied=esc(T("Copied!")), copyfail=esc(T("Select and copy")),
        title=esc(title), app=T("Copilot Agent Hub"), skip=T("Skip to content"), org=org, nav=nav, flash=flash,
        body=body,
        footer=T("Simple Copilot Agent Builder (T1) · content checked against Microsoft Learn on {date} · Microsoft features vary by licence and tenant; always check your own screen.",
                 date=content.EDITION_DATE),
    )


def error_page(req, status, message):
    body = '<section class="card narrow"><h1>{}</h1><p>{}</p><p><a href="/">{}</a></p></section>'.format(
        status, esc(req.t(message)), req.t("Go to home")
    )
    return layout(req, req.t("Error"), body)


__all__ = [
    "Raw", "Redirect", "HttpError", "redirect", "Request", "csrf_field", "progress_bar", "check", "flash_html",
    "options", "pct", "lbl", "sign", "layout", "error_page", "esc", "quote", "urlencode", "PAGE_SIZE", "COOKIE",
    "LANG_COOKIE",
]

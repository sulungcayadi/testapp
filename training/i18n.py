"""Translations.

English text in content.py and the page modules is the source. Each language
file in training/locales/ has one dictionary, TEXT, that maps English text to
its translation. Lookups work on three kinds of text:

* short strings (UI labels, titles, quiz options): looked up whole;
* HTML (lesson bodies): split into runs of text between block tags such as
  <p>, <li> or <h3>; each run keeps its inline tags (<strong>, <a>, <code>);
* plain text with line breaks (templates, the policy): looked up line by line.

Whitespace inside a key is normalized, so indentation in content.py does not
matter. Anything missing falls back to English and is recorded in MISSING, so
tests report gaps. `python app.py i18n-extract` lists every English segment.
"""

import importlib
import re

from .blocks import SOURCES

LANGS = [
    ("en", "English"),
    ("ja", "日本語"),
    ("zh-CN", "简体中文"),
    ("th", "ไทย"),
    ("id", "Bahasa Indonesia"),
    ("vi", "Tiếng Việt"),
]
CODES = [c for c, _ in LANGS]
DEFAULT = "en"

MISSING = set()
_cache = {}

BLOCK_TAGS = {
    "p", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "div", "section", "table", "thead", "tbody", "tr",
    "td", "th", "dl", "dt", "dd", "pre", "blockquote", "details", "summary", "figure", "figcaption", "br", "hr",
    "button", "fieldset", "legend", "label", "nav", "header", "footer", "form", "caption",
}
_TAG = re.compile(r"(<[^>]+>)")
_NAME = re.compile(r"</?\s*([a-zA-Z0-9]+)")
_LETTER = re.compile(r"[^\W\d_]", re.UNICODE)

# Text that stays in English everywhere: official Microsoft page titles in source lists.
KEEP = {" ".join(s["title"].split()) for s in SOURCES.values()}


def norm(text):
    return " ".join(text.split())


def catalog(lang):
    if lang not in _cache:
        if lang == DEFAULT or lang not in CODES:
            _cache[lang] = {}
        else:
            mod = importlib.import_module("training.locales." + lang.replace("-", "_"))
            _cache[lang] = {norm(k): v for k, v in mod.TEXT.items()}
    return _cache[lang]


def translatable(text):
    """Worth translating: has letters, is not a URL or path, is not kept in English."""
    plain = norm(_TAG.sub(" ", text))
    if not plain or not _LETTER.search(plain):
        return False
    if plain.startswith(("http://", "https://", "/")) and " " not in plain:
        return False
    return plain not in KEEP


def tr(lang, text):
    """Translate one string looked up whole."""
    if lang == DEFAULT or not text or not translatable(text):
        return text
    key = norm(text)
    found = catalog(lang).get(key)
    if found is None:
        MISSING.add((lang, key))
        return text
    return found


def t(lang, text, **kw):
    """Translate a UI string. Use {name} placeholders for values."""
    text = tr(lang, text)
    return text.format(**kw) if kw else text


# ---------------------------------------------------------------------------
# Segmenting
# ---------------------------------------------------------------------------

def html_runs(html):
    """Yield (start, end) offsets of text runs between block tags."""
    pos = 0
    start = None
    in_pre = False
    for part in _TAG.split(html):
        end = pos + len(part)
        if part.startswith("<"):
            m = _NAME.match(part)
            name = m.group(1).lower() if m else ""
            if name in BLOCK_TAGS:
                if start is not None:
                    yield start, pos
                    start = None
                if name == "pre":
                    in_pre = not part.startswith("</")
            elif start is None:
                start = pos
        else:
            if in_pre:
                # inside <pre>: one run per line
                offset = pos
                for line in part.split("\n"):
                    if start is not None:
                        yield start, offset
                        start = None
                    if line.strip():
                        yield offset, offset + len(line)
                    offset += len(line) + 1
            elif start is None and part.strip():
                start = pos
        pos = end
    if start is not None:
        yield start, pos


def html_segments(html):
    out = []
    for a, b in html_runs(html):
        run = html[a:b]
        if translatable(run):
            out.append(norm(run))
    return out


def html(lang, source):
    """Translate an HTML fragment run by run, keeping all block markup."""
    if lang == DEFAULT or not source:
        return source
    pieces = []
    last = 0
    for a, b in html_runs(source):
        run = source[a:b]
        pieces.append(source[last:a])
        if translatable(run):
            lead = run[: len(run) - len(run.lstrip())]
            trail = run[len(run.rstrip()):]
            pieces.append(lead + tr(lang, run) + trail)
        else:
            pieces.append(run)
        last = b
    pieces.append(source[last:])
    return "".join(pieces)


def text_segments(text):
    return [norm(line) for line in text.split("\n") if translatable(line)]


def text(lang, source):
    """Translate plain text line by line, keeping indentation and blank lines."""
    if lang == DEFAULT or not source:
        return source
    out = []
    for line in source.split("\n"):
        if translatable(line):
            indent = line[: len(line) - len(line.lstrip())]
            out.append(indent + tr(lang, line))
        else:
            out.append(line)
    return "\n".join(out)


def deep(lang, value):
    """Translate every string inside lists, tuples and dict values."""
    if lang == DEFAULT:
        return value
    if isinstance(value, str):
        return text(lang, value) if "\n" in value else tr(lang, value)
    if isinstance(value, tuple):
        return tuple(deep(lang, v) for v in value)
    if isinstance(value, list):
        return [deep(lang, v) for v in value]
    if isinstance(value, dict):
        return {k: deep(lang, v) for k, v in value.items()}
    return value


def deep_segments(value):
    if isinstance(value, str):
        return text_segments(value) if "\n" in value else ([norm(value)] if translatable(value) else [])
    if isinstance(value, (list, tuple)):
        return [s for v in value for s in deep_segments(v)]
    if isinstance(value, dict):
        return [s for v in value.values() for s in deep_segments(v)]
    return []


# ---------------------------------------------------------------------------
# Helpers used by the pages (kept stable so pages read clearly)
# ---------------------------------------------------------------------------

def module(lang, slug, field, default):
    return tr(lang, default)


def lesson(lang, module_slug, lesson_slug, field, default):
    return html(lang, default) if field == "body" else tr(lang, default)


def question(lang, code, prompt, options, rationale, custom=False):
    """Return (prompt, options, rationale) in the language. Organization
    questions added by admins are shown as written."""
    if lang == DEFAULT or custom:
        return prompt, options, rationale
    return tr(lang, prompt), [tr(lang, o) for o in options], tr(lang, rationale)


def lab_step(lang, no, instruction, evidence):
    return tr(lang, instruction), tr(lang, evidence)


def template(lang, slug, field, default):
    return text(lang, default) if field == "body" else tr(lang, default)


def label(lang, list_name, key, default):
    """Labels for option lists such as sharing scopes or checklist items."""
    return tr(lang, default)


def block(lang, name, default):
    """Whole structures: GLOSSARY, QUICKREF, FACILITATOR, BENCHMARKS."""
    return deep(lang, default)


def pick(accept_language):
    """Choose a supported language from an Accept-Language header."""
    if not accept_language:
        return DEFAULT
    for part in accept_language.split(","):
        tag = part.split(";")[0].strip().lower()
        if not tag:
            continue
        if tag.startswith("zh"):
            return "zh-CN"
        base = tag.split("-")[0]
        if base == "in":  # legacy code for Indonesian
            base = "id"
        if base in CODES:
            return base
    return DEFAULT

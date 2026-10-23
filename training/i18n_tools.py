"""Find every English segment the app can show, for translators and tests.

    python app.py i18n-extract            # all segments
    python app.py i18n-extract --missing ja   # segments not yet in ja
"""

import ast
import os

from . import content, i18n, services as svc

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_FILES = ["core.py", "pages_learn.py", "pages_hub.py", "pages_admin.py", "hub.py", "services.py", "web.py"]


def _const(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def code_strings():
    """Strings passed to T(), req.t(), i18n.t()/tr(), redirect(msg/error), notify(),
    raised as ValueError/HttpError, or returned as error messages by hub/services."""
    found = []
    for name in CODE_FILES:
        with open(os.path.join(HERE, name), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                fname = fn.id if isinstance(fn, ast.Name) else fn.attr if isinstance(fn, ast.Attribute) else ""
                owner = fn.value.id if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) else ""
                args = node.args
                if fname in ("T", "t", "tr"):
                    idx = 1 if owner == "i18n" else 0
                    if len(args) > idx and _const(args[idx]):
                        found.append(_const(args[idx]))
                elif fname in ("ValueError", "HttpError"):
                    found += [_const(a) for a in args if _const(a)]
                elif fname == "redirect":
                    found += [_const(k.value) for k in node.keywords if k.arg in ("msg", "error") and _const(k.value)]
                elif fname == "notify" and len(args) > 2:
                    value = args[2]
                    if isinstance(value, ast.IfExp):
                        found += [s for s in (_const(value.body), _const(value.orelse)) if s]
                    elif _const(value):
                        found.append(_const(value))
            elif isinstance(node, ast.Return) and name in ("hub.py", "services.py"):
                s = _const(node.value) if node.value is not None else None
                if s and " " in s and s.rstrip().endswith("."):
                    found.append(s)
            elif isinstance(node, ast.Dict) and name == "hub.py":
                # message tables such as the review decision notifications
                for v in node.values:
                    s = _const(v)
                    if s and "{" in s and " " in s:
                        found.append(s)
    return found


def _pairs(rows, *idx):
    return [row[i] for row in rows for i in idx]


def content_segments():
    from . import pages_admin, pages_hub, pages_learn
    segs = []
    for m in content.MODULES:
        segs += [m["title"], m["summary"]]
        for les in m["lessons"]:
            segs.append(les["title"])
            segs += i18n.html_segments(les["body"])
    for q in content.QUESTIONS:
        segs += [q["prompt"], *q["options"], q["rationale"]]
    for _, instr, ev in content.LAB_STEPS:
        segs += [instr, ev]
    for t in content.TEMPLATES:
        segs += [t["title"], t["use"]] + i18n.text_segments(t["body"])
    for rows in (content.AGENT_STATUSES, content.AGENT_TIERS, content.EVENT_KINDS, content.GOVERNANCE_CHECKLIST,
                 content.IDEA_CATEGORIES, content.IDEA_STATUSES, content.KNOWLEDGE_TYPES, content.QUESTION_TOPICS,
                 content.SENSITIVITY_LEVELS, content.SHARING_SCOPES, content.SKILL_SCALE, content.SKILL_STATEMENTS):
        segs += _pairs(rows, 1)
    segs += _pairs(content.BUILDER_LEVELS, 1, 2, 3)
    segs += _pairs(content.BENCHMARK_TARGETS, 1, 2, 3)
    segs += _pairs(svc.CHARTER_FIELDS, 1, 2)
    for b in content.BENCHMARKS:
        segs += [b[k] for k in ("region", "scale", "platform", "governance", "skilling", "result", "copy")]
    for value in (content.GLOSSARY, content.QUICKREF, content.FACILITATOR_AGENDA, content.FACILITATOR_PREP,
                  content.BENCHMARK_HABITS, content.BENCHMARK_ROADMAP, content.ZONES, content.DEFAULT_POLICY,
                  pages_learn.KEY_FACTS, list(pages_hub.SENS_RULES.values()), [l for _, l in pages_hub.LICENCE_STATUSES], list(pages_admin.STATUSES)):
        segs += i18n.deep_segments(value)
    return segs


def all_segments():
    seen = []
    known = set()
    for s in code_strings() + content_segments():
        key = i18n.norm(s)
        if key and i18n.translatable(key) and key not in known:
            known.add(key)
            seen.append(key)
    return seen


def missing(lang):
    cat = i18n.catalog(lang)
    return [s for s in all_segments() if s not in cat]


def placeholder_errors(lang):
    """Translations whose {placeholders} differ from the English."""
    import re
    ph = re.compile(r"\{(\w*)\}")
    cat = i18n.catalog(lang)
    return [k for k, v in cat.items() if sorted(ph.findall(k)) != sorted(ph.findall(v))]

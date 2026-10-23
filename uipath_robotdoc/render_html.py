from __future__ import annotations

import base64
from pathlib import Path

from jinja2 import Environment

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ p.name }} - Robot Documentation</title>
<style>
:root{--fg:#111827;--muted:#6b7280;--line:#e5e7eb;--bg:#fff;--soft:#f9fafb;--accent:#2563eb}
@media(prefers-color-scheme:dark){:root{--fg:#e5e7eb;--muted:#9ca3af;--line:#374151;--bg:#111827;--soft:#1f2937;--accent:#60a5fa}}
body{font:15px/1.5 system-ui,sans-serif;color:var(--fg);background:var(--bg);margin:0;display:flex}
nav{width:260px;position:sticky;top:0;height:100vh;overflow:auto;padding:20px;border-right:1px solid var(--line);box-sizing:border-box;flex:none}
nav a{display:block;color:var(--fg);text-decoration:none;padding:2px 0;font-size:13px}nav a:hover{color:var(--accent)}
main{padding:24px 40px;max-width:1000px;min-width:0}
h1{margin-top:0}h2{border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:40px}
table{border-collapse:collapse;width:100%;margin:8px 0 16px;font-size:13px}
th,td{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}th{background:var(--soft)}
.cards{display:flex;flex-wrap:wrap;gap:12px}.card{background:var(--soft);border:1px solid var(--line);border-radius:8px;padding:10px 16px}
.card b{display:block;font-size:22px}.muted{color:var(--muted)}.warn{color:#b45309}
img{max-width:100%}code{background:var(--soft);padding:1px 4px;border-radius:3px}
details{margin:8px 0}summary{cursor:pointer}.outline td:first-child{white-space:nowrap}
@media(max-width:800px){body{display:block}nav{position:static;width:auto;height:auto;border:0}main{padding:16px}}
</style></head><body>
<nav><b>{{ p.name }}</b><br><a href="#overview">Overview</a><a href="#diagrams">Diagrams</a><a href="#deps">Dependencies</a>
{% for w in wfs %}<a href="#wf-{{ loop.index }}">{{ w.path }}</a>{% endfor %}</nav>
<main>
<h1>{{ p.name }} <span class="muted">{{ p.version }}</span></h1>
<p>{{ p.description or "No description provided." }}</p>
<h2 id="overview">Overview</h2>
<div class="cards">
{% for label, val in cards %}<div class="card"><b>{{ val }}</b>{{ label }}</div>{% endfor %}
</div>
<table><tr><th>Entry point</th><td>{{ p.main or "-" }}</td></tr><tr><th>Expression language</th><td>{{ p.expression_language or "-" }}</td></tr>
<tr><th>Target framework</th><td>{{ p.target_framework or "-" }}</td></tr><tr><th>Authors</th><td>{{ p.authors or "-" }}</td></tr>
<tr><th>Source</th><td>{{ p.source }}</td></tr></table>
{% if stats.unreferenced or stats.unresolved_invokes or stats.parse_errors %}
<h3>Review notes</h3><ul class="warn">
{% for u in stats.unreferenced %}<li>{{ u }} is not invoked by any other workflow.</li>{% endfor %}
{% for a, b in stats.unresolved_invokes %}<li>{{ a }} invokes {{ b }}, which is not in the package.</li>{% endfor %}
{% for a, b in stats.parse_errors %}<li>{{ a }} could not be parsed: {{ b }}</li>{% endfor %}</ul>{% endif %}
<h2 id="diagrams">Diagrams</h2>
{% if graph %}<img alt="Workflow call graph" src="data:image/png;base64,{{ graph }}">{% endif %}
{% if mix %}<img alt="Activity usage" src="data:image/png;base64,{{ mix }}">{% endif %}
{% if not graph %}<p class="muted">Install matplotlib to include diagrams.</p>{% endif %}
<h2 id="deps">Dependencies</h2>
{% if deps %}<table><tr><th>Package</th><th>Version</th></tr>{% for d in deps %}<tr><td>{{ d.name }}</td><td>{{ d.version }}</td></tr>{% endfor %}</table>
{% else %}<p class="muted">None declared.</p>{% endif %}
{% for w in wfs %}
<h2 id="wf-{{ loop.index }}">{{ w.path }}{% if w.is_main %} <span class="muted">(main)</span>{% endif %}</h2>
{% if w.parse_error %}<p class="warn">{{ w.parse_error }}</p>{% endif %}
<p>{{ w.annotation }}</p>
<p class="muted">Root: {{ w.root_type or "-" }} &middot; {{ w.activities|length }} activities
{% if w.invoked_by %}&middot; invoked by {{ w.invoked_by|join(", ") }}{% endif %}</p>
{% if w.arguments %}<h4>Arguments</h4><table><tr><th>Name</th><th>Direction</th><th>Type</th></tr>
{% for a in w.arguments %}<tr><td>{{ a.name }}</td><td>{{ a.direction }}</td><td>{{ a.type }}</td></tr>{% endfor %}</table>{% endif %}
{% if w.variables %}<h4>Variables</h4><table><tr><th>Name</th><th>Type</th><th>Default</th><th>Scope</th></tr>
{% for v in w.variables %}<tr><td>{{ v.name }}</td><td>{{ v.type }}</td><td>{{ v.default_value }}</td><td>{{ v.scope }}</td></tr>{% endfor %}</table>{% endif %}
{% if w.invokes %}<h4>Invokes</h4><ul>{% for i in w.invokes %}<li>{{ i.target_path }}{% if not i.callee %} <span class="warn">(not found)</span>{% endif %}</li>{% endfor %}</ul>{% endif %}
{% if w.activities %}<details><summary>Activity outline ({{ w.activities|length }})</summary>
<table class="outline"><tr><th>Activity</th><th>Type</th><th>Detail</th></tr>
{% for a in w.activities %}<tr><td style="padding-left:{{ 8 + a.depth * 14 }}px">{{ a.display_name }}</td><td>{{ a.type }}</td>
<td>{{ a.detail }}{% if a.annotation %}<br><i>{{ a.annotation }}</i>{% endif %}</td></tr>{% endfor %}</table></details>{% endif %}
{% endfor %}
</main></body></html>"""


def _b64(path: Path | None) -> str:
    return base64.b64encode(path.read_bytes()).decode() if path and path.exists() else ""


def render(model: dict, out: Path, graph: Path | None, mix: Path | None) -> Path:
    s = model["stats"]
    cards = [("workflows", s["workflows"]), ("activities", s["activities"]), ("arguments", s["arguments"]),
             ("variables", s["variables"]), ("invocations", s["invocations"]), ("dependencies", s["dependencies"])]
    env = Environment(autoescape=True)
    html = env.from_string(TEMPLATE).render(p=model["package"], wfs=model["workflows"], deps=model["dependencies"],
                                            stats=s, cards=cards, graph=_b64(graph), mix=_b64(mix))
    out.write_text(html, encoding="utf-8")
    return out

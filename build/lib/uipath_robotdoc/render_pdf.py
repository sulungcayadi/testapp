from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

MAX_OUTLINE = 200


def render(model: dict, out: Path, graph: Path | None, mix: Path | None) -> Path:
    ss = getSampleStyleSheet()
    cell = ss["BodyText"].clone("cell", fontSize=8, leading=10)
    P = lambda t, st=None: Paragraph(escape(str(t if t is not None else "")), st or ss["BodyText"])  # noqa: E731
    width = A4[0] - 4 * cm

    def table(header, rows):
        data = [[Paragraph(f"<b>{escape(h)}</b>", cell) for h in header]]
        data += [[P(v, cell) for v in r] for r in rows]
        t = Table(data, repeatRows=1, colWidths=[width / len(header)] * len(header))
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                               ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                               ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        return t

    def image(path):
        from PIL import Image as PILImage
        w, h = PILImage.open(path).size
        return Image(str(path), width=width, height=width * h / w)

    p, s = model["package"], model["stats"]
    story = [P(f"{p['name']} - Robot Documentation", ss["Title"]),
             P(f"Version {p['version'] or '-'}. {p['description'] or ''}"),
             Spacer(1, 10), P("Overview", ss["Heading1"]),
             table(["Item", "Value"], [
                 ("Entry point", p["main"] or "-"), ("Expression language", p["expression_language"] or "-"),
                 ("Target framework", p["target_framework"] or "-"), ("Workflows", s["workflows"]),
                 ("Activities", s["activities"]), ("Arguments", s["arguments"]), ("Variables", s["variables"]),
                 ("Dependencies", s["dependencies"])])]
    notes = ([f"{u} is not invoked by any other workflow." for u in s["unreferenced"]]
             + [f"{a} invokes {b}, which is not in the package." for a, b in s["unresolved_invokes"]]
             + [f"{a} could not be parsed: {b}" for a, b in s["parse_errors"]])
    if notes:
        story += [P("Review notes", ss["Heading2"])] + [P("- " + n) for n in notes]
    for img in (graph, mix):
        if img and img.exists():
            story += [Spacer(1, 8), image(img)]
    story.append(P("Dependencies", ss["Heading1"]))
    story.append(table(["Package", "Version"], [(d["name"], d["version"]) for d in model["dependencies"]])
                 if model["dependencies"] else P("None declared."))
    for w in model["workflows"]:
        story.append(P(w["path"] + (" (main)" if w["is_main"] else ""), ss["Heading1"]))
        if w["parse_error"]:
            story.append(P("Parse error: " + w["parse_error"]))
        if w["annotation"]:
            story.append(P(w["annotation"]))
        story.append(P(f"Root: {w['root_type'] or '-'} | {len(w['activities'])} activities"
                       + (f" | invoked by {', '.join(w['invoked_by'])}" if w["invoked_by"] else "")))
        if w["arguments"]:
            story += [P("Arguments", ss["Heading3"]), table(["Name", "Direction", "Type"],
                                                           [(a["name"], a["direction"], a["type"]) for a in w["arguments"]])]
        if w["variables"]:
            story += [P("Variables", ss["Heading3"]), table(["Name", "Type", "Default", "Scope"],
                      [(v["name"], v["type"], v["default_value"], v["scope"]) for v in w["variables"]])]
        if w["invokes"]:
            story += [P("Invokes", ss["Heading3"])] + [P("- " + i["target_path"] + ("" if i["callee"] else " (not found)")) for i in w["invokes"]]
        if w["activities"]:
            rows = [(a["seq"], "\u00a0\u00a0" * a["depth"] + (a["display_name"] or ""), a["type"], a["detail"]) for a in w["activities"][:MAX_OUTLINE]]
            story += [P("Activity outline", ss["Heading3"]), table(["#", "Activity", "Type", "Detail"], rows)]
            if len(w["activities"]) > MAX_OUTLINE:
                story.append(P(f"... {len(w['activities']) - MAX_OUTLINE} more activities (see the xlsx/html output)."))
    SimpleDocTemplate(str(out), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm,
                      bottomMargin=2 * cm, title=f"{p['name']} - Robot Documentation").build(story)
    return out

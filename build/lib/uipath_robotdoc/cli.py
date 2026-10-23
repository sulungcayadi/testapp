from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from . import db, diagrams, parser, render_docx, render_html, render_pdf, render_pptx, render_xlsx

FORMATS = ("html", "docx", "pptx", "xlsx", "pdf", "png")


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_") or "package"


def build(input_path: str, out_dir: Path, formats: list[str], con) -> list[Path]:
    pkg = parser.read_input(input_path)
    model = db.load_model(con, db.ingest(con, pkg))
    base = slug(f"{pkg.name}_{pkg.version}" if pkg.version else pkg.name)
    out_dir.mkdir(parents=True, exist_ok=True)

    graph = mix = None
    needs_images = set(formats) & {"html", "docx", "pptx", "pdf", "png"}
    if needs_images and diagrams.have_matplotlib():
        graph = diagrams.call_graph_png(model, out_dir / f"{base}_callgraph.png")
        mix = diagrams.activity_mix_png(model, out_dir / f"{base}_activities.png")
    elif "png" in formats:
        print("warning: matplotlib is not installed; skipping png output", file=sys.stderr)

    written: list[Path] = []
    for fmt, mod in (("html", render_html), ("docx", render_docx), ("pptx", render_pptx),
                     ("xlsx", render_xlsx), ("pdf", render_pdf)):
        if fmt in formats:
            written.append(mod.render(model, out_dir / f"{base}.{fmt}", graph, mix))
    if "png" in formats and graph:
        written += [graph, mix]
    elif graph:  # generated only as an embedded image; not a requested output
        for img in (graph, mix):
            img.unlink(missing_ok=True)
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="uipath_robotdoc", description="Generate robot documentation from UiPath .nupkg files, project folders or .xaml files.")
    ap.add_argument("inputs", nargs="*", help=".nupkg, project folder or .xaml file (several allowed)")
    ap.add_argument("-o", "--out", default="robot_docs", help="output directory (default: robot_docs)")
    ap.add_argument("-f", "--formats", default="all", help=f"comma list of {','.join(FORMATS)} or 'all'")
    ap.add_argument("--db", help="SQLite file to keep parsed data in (default: <out>/robot_docs.db)")
    ap.add_argument("--make-sample", metavar="PATH", help="write a sample .nupkg to PATH and exit")
    args = ap.parse_args(argv)

    if args.make_sample:
        from .sample import write_sample_nupkg
        print(write_sample_nupkg(Path(args.make_sample)))
        return 0
    if not args.inputs:
        ap.error("give at least one input (or use --make-sample)")
    formats = list(FORMATS) if args.formats == "all" else [f.strip().lower() for f in args.formats.split(",") if f.strip()]
    bad = [f for f in formats if f not in FORMATS]
    if bad:
        ap.error(f"unknown format(s): {', '.join(bad)}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    con = db.connect(args.db or str(out_dir / "robot_docs.db"))
    status = 0
    for item in args.inputs:
        try:
            for path in build(item, out_dir, formats, con):
                print(path)
        except parser.PackageError as exc:
            print(f"error: {item}: {exc}", file=sys.stderr)
            status = 1
    return status

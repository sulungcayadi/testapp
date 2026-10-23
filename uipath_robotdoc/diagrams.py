"""PNG diagrams (call graph + activity mix). Needs matplotlib; callers treat it as optional."""
from __future__ import annotations

from collections import deque
from pathlib import Path


def have_matplotlib() -> bool:
    try:
        import matplotlib  # noqa: F401
        return True
    except ImportError:
        return False


def _pyplot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def call_graph_png(model: dict, out: Path) -> Path:
    """Layered call graph: Main (or any root) on the left, callees to the right."""
    plt = _pyplot()
    wfs = {w["path"]: w for w in model["workflows"]}
    edges = [(w["path"], i["callee"]) for w in wfs.values() for i in w["invokes"] if i["callee"]]
    roots = [p for p, w in wfs.items() if w["is_main"]] or [p for p, w in wfs.items() if not w["invoked_by"]] or list(wfs)[:1]
    level: dict[str, int] = {}
    queue = deque((r, 0) for r in roots)
    while queue:
        node, lv = queue.popleft()
        if node in level and level[node] >= lv:
            continue
        level[node] = lv
        if lv > len(wfs):  # cycle guard
            continue
        queue.extend((b, lv + 1) for a, b in edges if a == node)
    top = max(level.values(), default=0) + 1
    for p in wfs:  # unreferenced workflows go in a trailing column
        level.setdefault(p, top)
    cols: dict[int, list[str]] = {}
    for p, lv in sorted(level.items(), key=lambda kv: (kv[1], kv[0])):
        cols.setdefault(lv, []).append(p)
    rows = max(len(c) for c in cols.values())
    fig, ax = plt.subplots(figsize=(3.6 * len(cols) + 1, 0.9 * rows + 1.6), dpi=130)
    pos = {p: (lv, (len(c) - 1) / 2 - i) for lv, c in cols.items() for i, p in enumerate(c)}
    texts = {}
    for p, (x, y) in pos.items():
        w = wfs[p]
        face = "#dbeafe" if w["is_main"] else ("#f3f4f6" if level[p] == top and not w["invoked_by"] else "#e0f2fe")
        texts[p] = ax.text(x, y, w["name"], ha="center", va="center", fontsize=9, color="#111827", zorder=3,
                           bbox=dict(boxstyle="round,pad=0.45", fc=face, ec="#3b82f6" if w["is_main"] else "#9ca3af"))
    for a, b in edges:
        ax.annotate("", xy=pos[b], xytext=pos[a], zorder=2,
                    arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.1, shrinkA=2, shrinkB=2,
                                    patchA=texts[a].get_bbox_patch(), patchB=texts[b].get_bbox_patch()))
    ax.set_xlim(-0.6, max(cols) + 0.6)
    ax.set_ylim(min(y for _, y in pos.values()) - 0.8, max(y for _, y in pos.values()) + 0.8)
    ax.axis("off")
    ax.set_title(f"{model['package']['name']} - workflow call graph", fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


def activity_mix_png(model: dict, out: Path) -> Path:
    plt = _pyplot()
    data = model["stats"]["top_activities"][:12] or [("(none)", 0)]
    labels, values = zip(*reversed(data))
    fig, ax = plt.subplots(figsize=(7, 0.38 * len(data) + 1.4), dpi=130)
    bars = ax.barh(labels, values, color="#3b82f6")
    ax.bar_label(bars, padding=3, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(f"{model['package']['name']} - most used activities", fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out

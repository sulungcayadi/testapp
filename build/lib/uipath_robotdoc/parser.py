"""Read a UiPath .nupkg, project folder or single .xaml file into plain dataclasses."""
from __future__ import annotations

import json
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

MAX_MEMBER_BYTES = 50 * 1024 * 1024

# Activities that do not carry a DisplayName but are still activities.
STATEMENT_TAGS = {
    "Sequence", "Flowchart", "StateMachine", "State", "FlowStep", "FlowDecision", "FlowSwitch",
    "If", "IfElseIfV2", "Switch", "While", "DoWhile", "ForEach", "ParallelForEach", "Parallel",
    "TryCatch", "Throw", "Rethrow", "Assign", "Delay", "WriteLine", "InvokeMethod", "Interruptible",
    "Transition", "CancellationScope", "Pick", "PickBranch", "Persist", "Terminate",
}
# Property elements / helper nodes whose subtree never contains documentable activities.
SKIP_TAGS = {
    "Members", "Property", "Variable", "InArgument", "OutArgument", "InOutArgument", "Argument",
    "Collection", "Dictionary", "List", "Literal", "VisualBasicValue", "VisualBasicReference",
    "CSharpValue", "CSharpReference", "TextExpression", "ViewStateManager", "WorkflowViewState",
    "ViewStateData", "ViewState", "Reference", "AssemblyReference", "ActivityAction", "DelegateInArgument",
    "DelegateOutArgument", "Rect", "Point", "Size", "Annotation",
}
SKIP_PROPERTY_SUFFIXES = (".Variables", ".Arguments", ".ViewState", ".Attributes", ".Imports",
                          ".References", ".ViewStateManager", ".Condition", ".Expression", ".Value",
                          ".Target", ".To", ".From", ".Message")
DETAIL_ATTRS = ("WorkflowFileName", "Selector", "QueueName", "AssetName", "Message", "Text",
                "FilePath", "Url", "Level", "To", "Value", "Condition", "Expression")
ARG_RE = re.compile(r"^(InOut|In|Out)Argument\((.*)\)$", re.S)


class PackageError(Exception):
    """Raised for unreadable or unsafe input."""


@dataclass
class Argument:
    name: str
    direction: str
    type: str


@dataclass
class Variable:
    name: str
    type: str
    default: str
    scope: str


@dataclass
class ActivityNode:
    seq: int
    depth: int
    type: str
    display_name: str
    annotation: str
    detail: str


@dataclass
class Workflow:
    path: str
    name: str
    class_name: str = ""
    root_type: str = ""
    annotation: str = ""
    arguments: list[Argument] = field(default_factory=list)
    variables: list[Variable] = field(default_factory=list)
    activities: list[ActivityNode] = field(default_factory=list)
    invokes: list[str] = field(default_factory=list)
    parse_error: str = ""


@dataclass
class Package:
    name: str
    version: str = ""
    description: str = ""
    authors: str = ""
    source: str = ""
    main: str = ""
    expression_language: str = ""
    target_framework: str = ""
    dependencies: list[tuple[str, str]] = field(default_factory=list)
    workflows: list[Workflow] = field(default_factory=list)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def clean_type(t: str) -> str:
    """x:String -> String, scg:Dictionary(x:String, x:Object) -> Dictionary(String, Object)."""
    return re.sub(r"\b[A-Za-z0-9_]+:", "", t or "").strip()


def attr(el: ET.Element, name: str) -> str:
    """Attribute lookup that ignores namespace prefixes (sap2010:Annotation.AnnotationText etc.)."""
    for k, v in el.attrib.items():
        lk = local(k)
        if lk == name or lk.endswith("." + name):
            return v
    return ""


def _is_activity(el: ET.Element) -> bool:
    name = local(el.tag)
    if "." in name or name in SKIP_TAGS:
        return False
    if attr(el, "DisplayName") or name in STATEMENT_TAGS:
        return True
    return "uipath" in el.tag.lower()


def parse_xaml(data: bytes, path: str) -> Workflow:
    wf = Workflow(path=path, name=posixpath.splitext(posixpath.basename(path))[0])
    upper = data[:4096].upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in data[:65536].upper():
        wf.parse_error = "DOCTYPE/ENTITY declarations are not allowed"
        return wf
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        wf.parse_error = f"XML parse error: {exc}"
        return wf

    wf.class_name = attr(root, "Class")
    wf.annotation = attr(root, "AnnotationText")

    for prop in root.iter():
        if local(prop.tag) == "Property" and attr(prop, "Name") and attr(prop, "Type"):
            m = ARG_RE.match(attr(prop, "Type"))
            if m:
                wf.arguments.append(Argument(attr(prop, "Name"), m.group(1), clean_type(m.group(2))))

    seen_invokes: list[str] = []

    def walk(el: ET.Element, depth: int, owner: str) -> None:
        name = local(el.tag)
        if name in SKIP_TAGS or name.endswith(SKIP_PROPERTY_SUFFIXES):
            return
        is_act = _is_activity(el)
        label = owner
        if is_act:
            display = attr(el, "DisplayName") or name
            detail = next((f"{k}={attr(el, k)}" for k in DETAIL_ATTRS if attr(el, k)), "")
            if not wf.root_type:
                wf.root_type = name
            wf.activities.append(ActivityNode(len(wf.activities) + 1, depth, name, display,
                                              attr(el, "AnnotationText"), detail[:300]))
            target = attr(el, "WorkflowFileName")
            if target:
                seen_invokes.append(target)
            label = display
        for child in el:
            cname = local(child.tag)
            if cname.endswith(".Variables"):
                for var in child:
                    if local(var.tag) == "Variable":
                        wf.variables.append(Variable(attr(var, "Name"), clean_type(attr(var, "TypeArguments")) or "Object",
                                                     attr(var, "Default"), label or wf.name))
            walk(child, depth + 1 if is_act else depth, label)

    for child in root:
        walk(child, 0, wf.name)
    wf.invokes = list(dict.fromkeys(seen_invokes))
    if not wf.annotation and wf.activities:  # UiPath stores the workflow note on the root activity
        wf.annotation = wf.activities[0].annotation
    return wf


def _parse_nuspec(data: bytes) -> dict[str, str]:
    out: dict[str, str] = {}
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return out
    for el in root.iter():
        n = local(el.tag)
        if n in ("id", "version", "authors", "description") and el.text:
            out.setdefault(n, el.text.strip())
    return out


def _project_from_files(files: dict[str, bytes], fallback_name: str, source: str) -> Package:
    """`files` maps archive-relative paths to bytes."""
    pj_paths = sorted((p for p in files if posixpath.basename(p).lower() == "project.json"), key=lambda p: p.count("/"))
    prefix = posixpath.dirname(pj_paths[0]) if pj_paths else ""
    nuspec = next((_parse_nuspec(d) for p, d in files.items() if p.lower().endswith(".nuspec")), {})
    pkg = Package(name=nuspec.get("id") or fallback_name, version=nuspec.get("version", ""),
                  description=nuspec.get("description", ""), authors=nuspec.get("authors", ""), source=source)
    if pj_paths:
        try:
            pj = json.loads(files[pj_paths[0]].decode("utf-8-sig"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise PackageError(f"project.json is not valid JSON: {exc}") from exc
        pkg.name = pj.get("name") or pkg.name
        pkg.version = pj.get("projectVersion") or pkg.version
        pkg.description = pj.get("description") or pkg.description
        pkg.main = pj.get("main", "")
        pkg.expression_language = pj.get("expressionLanguage", "")
        pkg.target_framework = pj.get("targetFramework", "")
        deps = pj.get("dependencies") or {}
        pkg.dependencies = sorted((k, str(v)) for k, v in deps.items())
    for path in sorted(files):
        if path.lower().endswith(".xaml") and (not prefix or path.startswith(prefix + "/")):
            rel = path[len(prefix) + 1:] if prefix else path
            pkg.workflows.append(parse_xaml(files[path], rel))
    if not pkg.main and pkg.workflows:
        pkg.main = next((w.path for w in pkg.workflows if w.name.lower() == "main"), pkg.workflows[0].path)
    return pkg


def read_input(path: str | Path) -> Package:
    p = Path(path)
    if not p.exists():
        raise PackageError(f"{p} does not exist")
    if p.is_dir():
        files = {f.relative_to(p).as_posix(): f.read_bytes() for f in p.rglob("*")
                 if f.is_file() and f.suffix.lower() in (".xaml", ".json", ".nuspec")
                 and ".local" not in f.relative_to(p).parts and ".objects" not in f.relative_to(p).parts}
        return _project_from_files(files, p.resolve().name, str(p))
    if p.suffix.lower() == ".xaml":
        return _project_from_files({p.name: p.read_bytes()}, p.stem, str(p))
    if zipfile.is_zipfile(p):
        files = {}
        with zipfile.ZipFile(p) as zf:
            for info in zf.infolist():
                if info.is_dir() or not info.filename.lower().endswith((".xaml", ".json", ".nuspec")):
                    continue
                if info.file_size > MAX_MEMBER_BYTES:
                    raise PackageError(f"{info.filename} is larger than {MAX_MEMBER_BYTES} bytes")
                files[posixpath.normpath(info.filename.replace("\\", "/")).lstrip("/")] = zf.read(info)
        return _project_from_files(files, p.stem, str(p))
    raise PackageError(f"{p} is not a .nupkg/.zip archive, a .xaml file or a folder")


def resolve_invoke(target: str, workflow_paths: list[str]) -> str | None:
    """Map a WorkflowFileName value to a known workflow path (None when unresolved)."""
    norm = posixpath.normpath(target.replace("\\", "/"))
    if norm in workflow_paths:
        return norm
    base = posixpath.basename(norm).lower()
    matches = [w for w in workflow_paths if posixpath.basename(w).lower() == base]
    return matches[0] if len(matches) == 1 else None

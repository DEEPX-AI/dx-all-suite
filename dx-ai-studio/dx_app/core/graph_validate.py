"""Check a graph with dx_app's own validator (`--check`) and pin every error to a node or an edge.

Studio does not re-implement the graph rules. It writes the graph to a temporary file, runs
`multi_model_graph_sync --check <file> --model-dir <models> [--json]`, and maps what the CLI reports onto canvas ids:
a node id, or an edge id "<from>-><to>". Until dx_app prints JSON the text format is parsed:

    ERROR [CODE] <where>: <what>
      -> <how>

followed on stdout, for a valid graph, by the node table with each model file's state.
Contract: tests/dx_app/test_graph_validate.py
"""
from __future__ import annotations

import json
import re
import subprocess

from dx_app.core import graph_cli

MAX_NODES = 64
_ERR = re.compile(r"^ERROR \[(?P<code>[A-Z_]+)\] (?P<where>.*?): (?P<what>.*)$")
_EDGE = re.compile(r'edge(?:\[\d+\])? "(?P<frm>[^"]+)"->"(?P<to>[^"]+)"')
_NODE = re.compile(r'node(?:\[(?P<idx>\d+)\])?(?: "(?P<id>[^"]+)")?')
_ROW = re.compile(r"^(?P<node>\S+)\s+(?P<model>\(source\)|\S+)\s+(?P<produces>\S+)\s+(?P<consumes>\S+)\s+"
                  r"(?P<artifact>\S+)(?:\s+\[(?P<state>[^\]]+)\])?\s*$")


def pin(where: str, graph: dict) -> tuple:
    """(node id, edge id) named by an error location; (None, None) when it names the whole graph."""
    m = _EDGE.search(where or "")
    if m:
        return None, f"{m['frm']}->{m['to']}"
    for m in _NODE.finditer(where or ""):
        if m["id"]:
            return m["id"], None
        if m["idx"] is not None:
            nodes = (graph or {}).get("nodes") or []
            i = int(m["idx"])
            if 0 <= i < len(nodes) and isinstance(nodes[i], dict):
                return nodes[i].get("id"), None
    return None, None


def parse_errors(text: str, graph: dict, check_path: str = "") -> tuple:
    """ERROR blocks and `note:` lines of a CLI run, in order. Used for --check and for a run's log."""
    errors, notes, cur = [], [], None
    for line in (text or "").splitlines():
        m = _ERR.match(line)
        if m:
            where = m["where"].replace(check_path, "graph").strip() if check_path else m["where"].strip()
            node, edge = pin(where, graph)
            cur = {"code": m["code"], "where": where, "what": m["what"].strip(), "how": "", "node": node,
                   "edge": edge}
            errors.append(cur)
        elif cur is not None and line.startswith("  -> "):
            cur["how"] = (cur["how"] + " " if cur["how"] else "") + line[5:].strip()
        elif cur is not None and line.startswith("  ") and line.strip():
            cur["what"] += "\n" + line.strip()
        elif line.startswith("note:"):
            notes.append(line[5:].strip())
            cur = None
        else:
            cur = None
    return errors, notes


def parse_table(stdout: str) -> list:
    """The node table --check prints for a valid graph."""
    rows, inside = [], False
    for line in (stdout or "").splitlines():
        if line.startswith("node ") and "artifact" in line:
            inside = True
            continue
        if not inside:
            continue
        if not line.strip():
            inside = False
            continue
        r = _ROW.match(line)
        if not r:
            continue
        state = r["state"] or ""
        source = r["model"] == "(source)"
        version = state.split(",", 1)[1].strip() if "," in state else None
        rows.append({"node": r["node"], "model": None if source else r["model"], "produces": r["produces"],
                     "consumes": r["consumes"], "artifact": r["artifact"],
                     "present": None if source else state.startswith("present"),
                     "file": version, "missing": state == "MISSING",
                     "state": None if source else _text_state(state, version), "engine": None})
    return rows


def _text_state(state: str, version) -> str:
    """The JSON `state` of a text table cell: "present, v9", "present, invalid", "present, v9 (needs ...)", "MISSING"."""
    if state == "MISSING":
        return "missing"
    if not state.startswith("present"):
        return "unknown"
    if version == "invalid":
        return "invalid"
    return "unloadable" if version and "needs" in version else "present"


UNUSABLE = ("invalid", "unloadable", "unknown")


def _summary(models: list) -> dict:
    return {"missing": [m["node"] for m in models if m["missing"]],
            "unusable": {m["node"]: m["state"] for m in models if m.get("state") in UNUSABLE}}


def parse_check_text(stdout: str, stderr: str, check_path: str, graph: dict) -> dict:
    errors, notes = parse_errors((stderr or "") + "\n" + (stdout or ""), graph, check_path)
    models = parse_table(stdout)
    return {"ok": not errors, "errors": errors, "models": models, **_summary(models), "notes": notes}


def parse_check_json(stdout: str, graph: dict, check_path: str = "") -> dict:
    """`--check --json`: {"ok", "graph", "errors": [{code, where, what, how, node, edge: {from, to} | null}],
    "models": [{node, model, file, container, state: present|missing|invalid|unknown, engine}], "notes"}.
    An edge may also come as "a->b"; a missing node/edge is recovered from `where`. Model rows written as
    {present, file: <version>, missing} are read too."""
    data = json.loads(stdout)
    if not isinstance(data, dict):
        raise ValueError("--check --json printed no object")
    rows, entries = data.get("models") or [], data.get("errors") or []
    if not isinstance(rows, list) or not isinstance(entries, list) or not all(
            isinstance(x, dict) for x in rows + entries):
        raise ValueError("--check --json printed errors or models that are not objects")
    errors = []
    for e in entries:
        node, edge = e.get("node"), e.get("edge")
        if isinstance(edge, dict):
            ends = edge.get("from"), edge.get("to")
            edge = f"{ends[0]}->{ends[1]}" if all(isinstance(x, str) and x for x in ends) else None
        elif not isinstance(edge, str) or "->" not in edge:
            edge = None
        where = str(e.get("where", ""))
        where = where.replace(check_path, "graph").strip() if check_path else where
        if not node and not edge:
            node, edge = pin(where, graph)
        errors.append({"code": e.get("code", ""), "where": where, "what": e.get("what", ""),
                       "how": e.get("how", ""), "node": node, "edge": edge})
    models = []
    for m in rows:
        state = str(m.get("state") or "")
        present = m.get("present") if "present" in m else (state == "present" if state else None)
        version = m.get("container") if "container" in m else m.get("file")
        missing = bool(m.get("missing")) or state == "missing"
        models.append({"node": m.get("node"), "model": m.get("model"), "produces": m.get("produces"),
                       "consumes": m.get("consumes"), "artifact": m.get("artifact") or m.get("file"),
                       "present": present, "file": version, "missing": missing,
                       "state": state or ("missing" if missing else "present" if present else None),
                       "engine": m.get("engine") if isinstance(m.get("engine"), dict) else None})
    return {"ok": bool(data.get("ok")) and not errors, "errors": errors, "models": models, **_summary(models),
            "notes": list(data.get("notes") or [])}


def engine_graph(graph: dict, caps: dict) -> dict:
    """The graph as this dx_app build accepts it: without the node "engine" key when the build does not know it."""
    out = json.loads(json.dumps(graph))
    if not caps.get("engine_key"):
        for n in out.get("nodes") or []:
            if isinstance(n, dict):
                n.pop("engine", None)
    return out


def _studio_error(code: str, what: str, how: str = "") -> dict:
    return {"ok": False, "errors": [{"code": code, "where": "graph", "what": what, "how": how, "node": None,
                                     "edge": None}], "models": [], "missing": [], "unusable": {}, "notes": []}


def validate(graph: dict) -> dict:
    if not isinstance(graph, dict) or not isinstance(graph.get("nodes"), list):
        return _studio_error("STUDIO_INVALID", "the graph must be an object with a nodes list")
    if len(graph["nodes"]) > MAX_NODES:
        return _studio_error("STUDIO_INVALID", f"a graph may have at most {MAX_NODES} nodes")
    if graph_cli.binary("sync") is None:
        res = _studio_error("GRAPH_BINARY_MISSING", "multi_model_graph_sync is not built",
                            "build dx_app (./build.sh)")
        res["available"] = False
        return res
    caps = graph_cli.capabilities()
    data = engine_graph(graph, caps)
    path = graph_cli.scratch_file("check")
    path.write_text(json.dumps(data), encoding="utf-8")
    try:
        args = ["--check", str(path), "--model-dir", str(graph_cli.models_dir())] + (["--json"] if caps["json"] else [])
        r = graph_cli.run(args, timeout=20)
    except subprocess.TimeoutExpired:
        return _studio_error("CHECK_TIMEOUT", "--check did not answer in 20 s")
    except (subprocess.SubprocessError, OSError) as e:
        return _studio_error("CHECK_FAILED", str(e))
    finally:
        path.unlink(missing_ok=True)
    try:
        res = (parse_check_json(r.stdout, graph, str(path)) if caps["json"]
               else parse_check_text(r.stdout, r.stderr, str(path), graph))
    except ValueError:
        res = _studio_error("CHECK_UNREADABLE", (r.stdout or r.stderr).strip()[:300])
    if r.returncode not in (0, 1) and not res["errors"]:
        res = _studio_error("CHECK_FAILED", (r.stderr or r.stdout).strip()[:300])
    res["ok"] = res["ok"] and r.returncode == 0
    res["available"] = True
    res["engine_ignored"] = not caps["engine_key"] and any(
        isinstance(n, dict) and "engine" in n for n in graph["nodes"])
    return res

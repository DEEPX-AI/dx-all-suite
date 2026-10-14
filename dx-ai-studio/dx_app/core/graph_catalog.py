"""What the Graph Composer palette offers: the models this dx_app build can put in a graph (with their install state and
a download link), the CPU ops, and the shipped example graphs.

Models come from `multi_model_graph_sync --list-models` (JSON with --json when the build has it, else the text table)
and are cached by the binary's and the models directory's mtimes, so a finished download shows up without a restart.
Contract: tests/dx_app/test_graph_catalog.py
"""
from __future__ import annotations

import json
import re
import subprocess
import threading
from pathlib import Path

from dx_app.core import config, graph_cli

# The graph engine's two CPU reductions (README "three node kinds"): what they take over "carry": "result" edges.
CPU_OPS = [
    {"op": "headpose", "inputs": ["boxes"], "params": {}},
    {"op": "volume", "inputs": ["boxes", "instances", "densemap"], "params": {"scale_factor": 1.0}},
]

_FILE = re.compile(r"^(?P<file>v\d+(?: \(needs DX-RT >= (?P<needs>[\d.]+)\))?|missing|invalid)\s+"
                   r"(?P<ready>yes|no)\b\s*(?P<rest>.*)$")
_ALIAS = re.compile(r"^(?P<name>\S+)\s+alias of\s+(?P<target>\S+)\s*$")

_lock = threading.Lock()
_cache: dict = {"key": None, "value": None}


def _entry(name, task, produces, consumes, size, published, file_state, needs, ready, reason, ports) -> dict:
    if not ready:
        state = "not_ready"
    elif file_state == "missing":
        state = "missing"
    elif file_state == "invalid":
        state = "invalid"
    elif needs:
        state = "needs_runtime"
    else:
        state = "installed"
    return {"name": name, "task": task, "produces": produces, "consumes": consumes, "input": size,
            "published": bool(published), "file": file_state, "needs_dxrt": needs or None, "ready": bool(ready),
            "reason": reason or "", "ports": dict(ports or {}), "state": state, "installed": state == "installed"}


def parse_list_models_text(text: str) -> dict:
    """The --list-models table: model, task, produces, consumes, input, published, file, ready[, note].

    `file` may read "v9 (needs DX-RT >= 3.5.0)"; the note is "ports: name=shape ..." or, for a model that is not
    ready, the reason."""
    models, aliases = [], []
    for line in (text or "").splitlines():
        if not line.strip() or line.startswith("model ") or set(line.strip()) == {"-"}:
            continue
        m = _ALIAS.match(line)
        if m:
            aliases.append({"name": m["name"], "alias_of": m["target"]})
            continue
        parts = line.split(None, 6)
        if len(parts) < 7:
            continue
        name, task, produces, consumes, size, published, rest = parts
        fm = _FILE.match(rest)
        if not fm:
            continue
        note, ports, reason = fm["rest"].strip(), {}, ""
        if note.startswith("ports:"):
            for item in note[len("ports:"):].split():
                k, _, v = item.partition("=")
                if k and v:
                    ports[k] = v
        elif fm["ready"] == "no":
            reason = note
        models.append(_entry(name, task, produces, consumes, size, published == "yes", fm["file"].split()[0],
                             fm["needs"], fm["ready"] == "yes", reason, ports))
    return {"models": models, "aliases": aliases}


def _input_text(v) -> str:
    if isinstance(v, dict) and v.get("width") and v.get("height"):
        return f"{v['width']}x{v['height']}"
    return str(v or "")


def _ports(v) -> dict:
    if isinstance(v, dict):
        return dict(v)
    return {p["name"]: p.get("shape", "") for p in v or [] if isinstance(p, dict) and p.get("name")}


def parse_list_models_json(text: str) -> dict:
    """`--list-models --json`. dx_app prints a list of rows {model, task, produces, consumes, input: {width, height},
    published, file: "<stem>.dxnn", container: v8|v9|missing|invalid[ (needs DX-RT >= x)], ready, reason,
    ports: [{name, shape}], alias_of}; an `alias_of` row is an alias. A {"models": [...], "aliases": [...]} document
    with `file` as the state is read too."""
    data = json.loads(text)
    rows = data if isinstance(data, list) else data.get("models") or []
    aliases = [] if isinstance(data, list) else [
        {"name": a.get("name"), "alias_of": a.get("alias_of")}
        for a in data.get("aliases") or [] if isinstance(a, dict) and a.get("name")]
    models = []
    for m in rows:
        name = m.get("model") or m.get("name") if isinstance(m, dict) else None
        if not name:
            continue
        if m.get("alias_of"):
            aliases.append({"name": name, "alias_of": m["alias_of"]})
            continue
        state = str(m.get("container") or m.get("file") or "missing")
        needs = m.get("needs_dxrt") or (re.search(r"needs DX-RT >= ([\d.]+)", state) or [None, None])[1]
        models.append(_entry(name, m.get("task", ""), m.get("produces", ""), m.get("consumes", ""),
                             _input_text(m.get("input")), m.get("published", True), state.split()[0], needs,
                             m.get("ready", True), m.get("reason", ""), _ports(m.get("ports"))))
    return {"models": models, "aliases": aliases}


def list_models(refresh: bool = False) -> dict:
    b = graph_cli.binary("sync")
    if b is None:
        return {"models": [], "aliases": [], "error": "graph_binary_missing"}
    mdir = graph_cli.models_dir()
    key = (str(b), graph_cli.mtime(b), str(mdir), graph_cli.mtime(mdir))
    with _lock:
        if not refresh and _cache["key"] == key:
            return _cache["value"]
    caps = graph_cli.capabilities()
    args = ["--list-models", "--model-dir", str(mdir)] + (["--json"] if caps["json"] else [])
    try:
        r = graph_cli.run(args, timeout=30)
    except (subprocess.SubprocessError, OSError) as e:
        return {"models": [], "aliases": [], "error": f"list_models_failed: {e}"}
    if r.returncode != 0:
        return {"models": [], "aliases": [], "error": "list_models_failed: " + (r.stderr or r.stdout).strip()[:300]}
    try:
        value = parse_list_models_json(r.stdout) if caps["json"] else parse_list_models_text(r.stdout)
    except ValueError as e:
        return {"models": [], "aliases": [], "error": f"list_models_unreadable: {e}"}
    value["error"] = None
    with _lock:
        _cache.update(key=key, value=value)
    return value


def _download_index() -> dict:
    """.dxnn stem -> {name, dxnn_url, json_url} from the Model Zoo catalog dx_app already uses for Download."""
    try:
        from dx_app.core.models import get_catalog
        rows = get_catalog()
    except Exception:
        return {}
    idx = {}
    for row in rows or []:
        stem = Path(str(row.get("model_file") or "")).stem
        if stem and row.get("dxnn_url"):
            idx[stem] = {"name": row.get("mz_name") or row.get("name") or stem,
                         "dxnn_url": row["dxnn_url"], "json_url": row.get("json_url")}
    return idx


def examples() -> list[dict]:
    """The shipped sample graphs (dx_app src/cpp_example/multi_model_graph/*.json)."""
    d = Path(config.DX_APP_ROOT) / "src" / "cpp_example" / "multi_model_graph"
    out = []
    for p in sorted(d.glob("*.json")):
        try:
            g = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(g, dict) or not isinstance(g.get("nodes"), list):
            continue
        models = sorted({n["model"] for n in g["nodes"] if isinstance(n, dict) and n.get("model")})
        out.append({"id": p.stem, "name": g.get("name") or p.stem, "graph": g, "models": models,
                    "nodes": len(g["nodes"]), "edges": len(g.get("edges") or [])})
    return out


def catalog(refresh: bool = False) -> dict:
    available = graph_cli.binary("sync") is not None
    lm = list_models(refresh)
    downloads = _download_index() if any(m["state"] in ("missing", "invalid") for m in lm["models"]) else {}
    models = []
    for m in lm["models"]:
        e = dict(m)
        e["download"] = downloads.get(m["name"]) if m["state"] in ("missing", "invalid") else None
        models.append(e)
    return {"available": available, "error": lm.get("error"), "models": models, "aliases": lm["aliases"],
            "cpu_ops": CPU_OPS, "examples": examples(),
            "capabilities": graph_cli.capabilities() if available else {"json": False, "engine_key": False,
                                                                         "report_timing": False}}

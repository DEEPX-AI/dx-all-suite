"""The logic blocks a dx_app build can put in a graph, from `multi_model_graph_sync --list-ops --json`.

dx_app prints one JSON array: the eight logic ops ("type": "logic"), then the two cpu ops ("type": "cpu"), each

    {"op", "type", "summary", "inputs": {"min", "max", "accepts": [{"shape", "per_crop"}]},
     "output": "same" | "records", "tracking", "events", "numbers",
     "params": [{"name", "type": number|text|choice|text_list|polygon|line, "required", "default", "min",
                 "min_exclusive", "max", "choices", "min_points", "points", "help"}]}

(dx_app src/cpp_example/multi_model_graph/README.md, "--list-ops --json"). Studio keeps the logic ops, checks every
field's type, and hands them to the page as they are: the palette's Logic group and the inspector's form are built
from them, so a block dx_app adds later needs no Studio change. Cached by the binary's path and mtime.
Contract: tests/dx_app/test_graph_ops.py
"""
from __future__ import annotations

import json
import re
import subprocess
import threading

from dx_app.core import graph_cli

# Param types the inspector has a field for; any other type is shown as a text field.
PARAM_TYPES = ("number", "text", "choice", "text_list", "polygon", "line")
_OP = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")
_SHAPE = re.compile(r"^[a-z0-9_]{1,32}$")

_lock = threading.Lock()
_cache: dict = {"key": None, "value": None}


def _num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _strings(v) -> list:
    return [str(x) for x in v if isinstance(x, str)] if isinstance(v, list) else []


def _param(p) -> dict | None:
    if not isinstance(p, dict) or not isinstance(p.get("name"), str) or not _NAME.fullmatch(p["name"]):
        return None
    kind = p.get("type") if p.get("type") in PARAM_TYPES else "text"
    out = {"name": p["name"], "type": kind, "required": bool(p.get("required")),
           "help": p["help"] if isinstance(p.get("help"), str) else ""}
    for k in ("min", "max"):
        if _num(p.get(k)) is not None:
            out[k] = p[k]
    if p.get("min_exclusive") is True:
        out["min_exclusive"] = True
    if kind == "choice":
        out["choices"] = _strings(p.get("choices"))
    if kind == "polygon":
        out["min_points"] = p["min_points"] if isinstance(p.get("min_points"), int) and p["min_points"] >= 3 else 3
    if kind == "line":
        out["points"] = 2
    if "default" in p and not out["required"]:
        d = p["default"]
        if (kind == "number" and _num(d) is not None) or (kind in ("text", "choice") and isinstance(d, str)) \
                or (kind == "text_list" and isinstance(d, list)):
            out["default"] = d
    return out


def _inputs(v) -> dict:
    v = v if isinstance(v, dict) else {}
    lo = v.get("min") if isinstance(v.get("min"), int) and v["min"] >= 0 else 1
    hi = v.get("max") if isinstance(v.get("max"), int) and v["max"] >= max(lo, 1) else max(lo, 1)
    accepts = [{"shape": a["shape"], "per_crop": bool(a.get("per_crop"))} for a in v.get("accepts") or []
               if isinstance(a, dict) and isinstance(a.get("shape"), str) and _SHAPE.fullmatch(a["shape"])]
    return {"min": lo, "max": hi, "accepts": accepts}


def parse_list_ops(text: str) -> list:
    """The logic ops of `--list-ops --json` (a list; a {"ops": [...]} document is read too), in dx_app's order.
    Cpu ops and malformed entries are left out."""
    data = json.loads(text)
    rows = data.get("ops") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise ValueError("--list-ops --json printed no list of ops")
    ops = []
    for r in rows:
        if not isinstance(r, dict) or not isinstance(r.get("op"), str) or not _OP.fullmatch(r["op"]):
            continue
        if r.get("type", "logic") != "logic":
            continue
        ops.append({"op": r["op"], "summary": r["summary"] if isinstance(r.get("summary"), str) else "",
                    "inputs": _inputs(r.get("inputs")),
                    "output": r["output"] if r.get("output") in ("same", "records") else "records",
                    "tracking": r.get("tracking") is True, "events": _strings(r.get("events")),
                    "numbers": _strings(r.get("numbers")),
                    "params": [q for q in (_param(p) for p in r.get("params") or []) if q]})
    return ops


def list_ops(refresh: bool = False) -> dict:
    """{"ops": [...], "error": None} — or no ops and why: this build has no --list-ops, no binary, or bad output."""
    found = graph_cli.available()
    if found is None:
        return {"ops": [], "error": "graph_binary_missing"}
    b = found[1]
    key = (str(b), graph_cli.mtime(b))
    with _lock:
        if not refresh and _cache["key"] == key:
            return _cache["value"]
    if not graph_cli.capabilities().get("list_ops"):
        value = {"ops": [], "error": "list_ops_unsupported"}
    else:
        try:
            r = graph_cli.run(["--list-ops", "--json"], timeout=20)
            if r.returncode != 0:
                raise ValueError((r.stderr or r.stdout).strip()[:300])
            value = {"ops": parse_list_ops(r.stdout), "error": None}
        except (subprocess.SubprocessError, OSError) as e:
            return {"ops": [], "error": f"list_ops_failed: {e}"}
        except ValueError as e:
            return {"ops": [], "error": f"list_ops_unreadable: {e}"}
    with _lock:
        _cache.update(key=key, value=value)
    return value

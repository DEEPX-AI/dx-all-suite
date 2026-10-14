"""NPU memory of a graph: what each model's engine holds (parse_model), what the device has (DX-RT DeviceStatus, else
dxrt-cli), and how the node "engine" options change the sum.

The Studio's own venv has no dx_engine, so when shared.hardware has no real DeviceStatus reading the free memory is
read by a short subprocess in the DX-RT runtime venv (venv-dx-runtime); the device size comes from `dxrt-cli -s`.

parse_model prints the per-model figure ("Model Memory Usage: Total"), and most of it is the buffer pool ("Buffers",
"Buffer Pool Size : x6"). An engine created with N buffers instead of the pool's P holds
(Total - Buffers) + Buffers * N / P. Nodes with "engine": {"share": true} on the same model use one engine.
Figures are cached by the .dxnn's content hash. Contract: tests/dx_app/test_graph_memory.py
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

from dx_app.core import graph_cli
from shared.paths import DX_RUNTIME_ROOT

MB = 1024 * 1024
_TOTAL = re.compile(r"-\s*Total\s*:\s*[\d.]+\s*MB\s*\(([\d,]+) bytes\)")
_BUFFERS = re.compile(r"-\s*Buffers\s*:\s*[\d.]+\s*MB\s*\(([\d,]+) bytes\)")
_POOL = re.compile(r"Buffer Pool Size\s*:\s*x(\d+)")
_DEVICE = re.compile(r"Memory\s*:.*?([\d.]+)\s*(GiB|MiB|GB|MB)\b")
_UNIT = {"GiB": 1024 ** 3, "GB": 1000 ** 3, "MiB": MB, "MB": 1000 ** 2}

_lock = threading.Lock()
_hash_cache: dict = {}
_mem_cache: dict = {}
_device_cache: dict = {"at": 0.0, "value": None}


def parse_model_text(text: str) -> dict:
    t = _TOTAL.search(text or "")
    if not t:
        raise ValueError("parse_model printed no 'Model Memory Usage: Total' line")
    b, p = _BUFFERS.search(text), _POOL.search(text)
    total = int(t.group(1).replace(",", ""))
    buffers = int(b.group(1).replace(",", "")) if b else 0
    return {"total_bytes": total, "buffers_bytes": min(buffers, total), "pool": max(int(p.group(1)) if p else 6, 1)}


def parse_dxrt_status(text: str):
    """Device memory size from `dxrt-cli -s` ("* Memory : LPDDR5 5600 Mbps, 3.92GiB"), in bytes; None if absent."""
    m = _DEVICE.search(text or "")
    return int(float(m.group(1)) * _UNIT[m.group(2)]) if m else None


def engine_bytes(info: dict, buffers=None) -> int:
    pool = info["pool"]
    n = pool if buffers is None else max(1, int(buffers))
    return int(info["total_bytes"] - info["buffers_bytes"] + info["buffers_bytes"] * n / pool)


def _tool(name: str):
    found = shutil.which(name)
    if found:
        return found
    for cand in (Path("/usr/local/bin") / name, Path(DX_RUNTIME_ROOT) / "dx_rt" / "bin" / name):
        if cand.is_file():
            return str(cand)
    return None


def parse_model_binary():
    return _tool("parse_model")


def dxrt_cli_binary():
    return _tool("dxrt-cli")


def _file_hash(p: Path) -> str:
    st = p.stat()
    key = (str(p), st.st_size, st.st_mtime_ns)
    with _lock:
        if key in _hash_cache:
            return _hash_cache[key]
    h = hashlib.sha1()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    digest = h.hexdigest()
    with _lock:
        _hash_cache[key] = digest
    return digest


def model_memory(path):
    """parse_model's figures for one .dxnn, or None when the file is missing, empty or unreadable."""
    p = Path(path)
    try:
        if not p.is_file() or p.stat().st_size == 0:
            return None
    except OSError:
        return None
    digest = _file_hash(p)
    with _lock:
        if digest in _mem_cache:
            return dict(_mem_cache[digest])
    exe = parse_model_binary()
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "-m", str(p)], capture_output=True, text=True, timeout=30, env=graph_cli.env())
        info = parse_model_text(r.stdout + "\n" + r.stderr)
    except (subprocess.SubprocessError, OSError, ValueError):
        return None
    with _lock:
        _mem_cache[digest] = dict(info)
    return info


# Run in the DX-RT runtime venv: every device's DeviceStatus memory figures, as one JSON line.
DEVICE_PROBE = (
    "import json\n"
    "from dx_engine.device_status import DeviceStatus\n"
    "rows = []\n"
    "for i in range(DeviceStatus.get_device_count()):\n"
    "    s = DeviceStatus.get_current_status(i)\n"
    "    rows.append({'id': i, 'valid': bool(s.is_valid()), 'used': int(s.get_memory_used()),\n"
    "                 'free': int(s.get_memory_free())})\n"
    "print(json.dumps(rows))\n"
)


def runtime_python():
    """The DX-RT runtime venv's interpreter (the venv-dx-runtime roots Studio probes everywhere), or None."""
    from shared.runtime import runtime_venv_roots
    for root in runtime_venv_roots():
        for name in ("python3", "python"):
            p = Path(root) / "bin" / name
            if p.is_file():
                return str(p)
    return None


def _run_device_probe(python: str) -> str:
    r = subprocess.run([python, "-c", DEVICE_PROBE], capture_output=True, text=True, timeout=10,
                       env=graph_cli.env(), cwd="/")
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[-300:])
    return r.stdout


_probe_runner = _run_device_probe


def parse_device_probe(text: str):
    """{used_bytes, free_bytes} of the valid device with the least free memory (DX-RT loads a graph's engines on
    every device it uses, so that one is the budget); None when no device reports valid figures."""
    lines = [ln for ln in (text or "").splitlines() if ln.strip()]
    rows = json.loads(lines[-1]) if lines else []
    best = None
    for r in rows if isinstance(rows, list) else []:
        if not isinstance(r, dict) or not r.get("valid"):
            continue
        used, free = r.get("used"), r.get("free")
        if not isinstance(used, int) or not isinstance(free, int) or used < 0 or free < 0:
            continue
        if best is None or free < best["free_bytes"]:
            best = {"used_bytes": used, "free_bytes": free}
    return best


def runtime_device_status():
    py = runtime_python()
    if not py:
        return None
    try:
        return parse_device_probe(_probe_runner(py))
    except (subprocess.SubprocessError, OSError, RuntimeError, ValueError):
        return None


def _dxrt_cli_total():
    exe = dxrt_cli_binary()
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "-s"], capture_output=True, text=True, timeout=15, env=graph_cli.env())
    except (subprocess.SubprocessError, OSError):
        return None
    return parse_dxrt_status(r.stdout)


def device_memory() -> dict:
    """{total_bytes, used_bytes, free_bytes, source}; cached for 5 s."""
    now = time.time()
    with _lock:
        if _device_cache["value"] is not None and now - _device_cache["at"] < 5:
            return dict(_device_cache["value"])
    value = {"total_bytes": None, "used_bytes": None, "free_bytes": None, "source": "unknown"}
    try:
        from shared.hardware import get_hw
        hw = get_hw()
        npus = [n for n in hw.get("npus") or [] if isinstance(n, dict)]
        if npus and not hw.get("mock") and (npus[0].get("dram_total_mb") or -1) > 0:
            total = int(npus[0]["dram_total_mb"] * MB)
            used = int(max(0, npus[0].get("dram_used_mb") or 0) * MB)
            value = {"total_bytes": total, "used_bytes": used, "free_bytes": total - used, "source": "device_status"}
    except Exception:
        pass
    if value["source"] == "unknown":
        status = runtime_device_status()
        total = _dxrt_cli_total()
        if status:
            value = {"total_bytes": total or status["used_bytes"] + status["free_bytes"],
                     "used_bytes": status["used_bytes"], "free_bytes": status["free_bytes"],
                     "source": "device_status"}
        elif total:
            value = {"total_bytes": total, "used_bytes": None, "free_bytes": total, "source": "dxrt_cli"}
    with _lock:
        _device_cache.update(at=now, value=dict(value))
    return value


def _engines(nodes: list) -> list:
    engines, shared = [], {}
    for n in nodes:
        eng = n.get("engine") if isinstance(n.get("engine"), dict) else {}
        buffers = _buffers_of(n)
        if eng.get("share"):
            e = shared.get(n["model"])
            if e is None:
                e = shared[n["model"]] = {"model": n["model"], "nodes": [], "buffers": buffers}
                engines.append(e)
            elif e["buffers"] is None or buffers is None:
                e["buffers"] = None
            else:
                e["buffers"] = max(e["buffers"], buffers)
            e["nodes"].append(n["id"])
        else:
            engines.append({"model": n["model"], "nodes": [n["id"]], "buffers": buffers})
    return engines


def _buffers_of(node: dict):
    eng = node.get("engine") if isinstance(node.get("engine"), dict) else {}
    try:
        return int(eng["buffers"]) if eng.get("buffers") is not None else None
    except (TypeError, ValueError):
        return None


def _share_patch(owner: dict, ids: list) -> dict:
    """Node id -> the keys to set so every node shares the owner's engine. dx_app accepts sharing nodes only with the
    owner's "params" and "buffers" (GRAPH_SCHEMA on node "<id>" "engine" otherwise); a key set to None is removed."""
    engine = {"share": True}
    if _buffers_of(owner) is not None:
        engine["buffers"] = _buffers_of(owner)
    params = owner.get("params") if isinstance(owner.get("params"), dict) and owner.get("params") else None
    return {nid: {"engine": dict(engine), "params": json.loads(json.dumps(params)) if params is not None else None}
            for nid in ids}


def suggestions(engines: list, infos: dict, nodes=None) -> list:
    """Ways to shrink the sum, biggest saving first: share an engine between nodes of one model, or use 2 buffers.

    A share suggestion lists the nodes in graph order and carries `patch`: the first node's params and buffers for
    every node of the model, because dx_app's owner of a shared engine is the first sharing node and the others
    must match it."""
    out, by_model = [], {}
    order = {n.get("id"): i for i, n in enumerate(nodes or []) if isinstance(n, dict)}
    by_id = {n.get("id"): n for n in nodes or [] if isinstance(n, dict)}
    for e in engines:
        by_model.setdefault(e["model"], []).append(e)
    for model, es in by_model.items():
        if model in infos and len(es) > 1:
            ids = sorted((n for e in es for n in e["nodes"]), key=lambda nid: order.get(nid, len(order)))
            owner = by_id.get(ids[0], {})
            shared = engine_bytes(infos[model], _buffers_of(owner))
            out.append({"kind": "share", "model": model, "nodes": ids,
                        "saves_bytes": max(0, sum(e["bytes"] or 0 for e in es) - shared),
                        "patch": _share_patch(owner, ids)})
    for e in engines:
        info = infos.get(e["model"])
        current = e["buffers"] if e["buffers"] is not None else (info or {}).get("pool", 0)
        if info and current > 2:
            saves = (e["bytes"] or 0) - engine_bytes(info, 2)
            if saves > 0:
                out.append({"kind": "buffers", "model": e["model"], "nodes": list(e["nodes"]), "buffers": 2,
                            "saves_bytes": saves})
    out.sort(key=lambda s: -s["saves_bytes"])
    return out


def estimate(graph: dict) -> dict:
    nodes = [n for n in (graph or {}).get("nodes") or [] if isinstance(n, dict) and n.get("model") and n.get("id")]
    mdir = graph_cli.models_dir()
    infos, unknown = {}, []
    for n in nodes:
        name = n["model"]
        if name in infos or name in unknown:
            continue
        info = model_memory(mdir / f"{name}.dxnn")
        if info is None:
            unknown.append(name)
        else:
            infos[name] = info
    engines, per_node, total = _engines(nodes), {}, 0
    for e in engines:
        info = infos.get(e["model"])
        e["bytes"] = engine_bytes(info, e["buffers"]) if info else None
        total += e["bytes"] or 0
        for i, nid in enumerate(e["nodes"]):
            per_node[nid] = {"model": e["model"], "bytes": e["bytes"] if i == 0 else 0,
                             "shared_with": [x for x in e["nodes"] if x != nid],
                             "buffers": e["buffers"] if e["buffers"] is not None else (info or {}).get("pool")}
    device = device_memory()
    free = device.get("free_bytes")
    return {"nodes": per_node, "engines": engines, "total_bytes": total, "device": device,
            "over_budget": bool(free is not None and total > free), "unknown_models": unknown,
            "suggestions": suggestions(engines, infos, nodes)}

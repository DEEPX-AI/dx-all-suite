"""dx_app's multi-model graph CLI as Studio calls it: where the binaries are, the environment they run in, and what this
build supports (JSON output with --json, the node "engine" key).

The binaries are multi_model_graph_sync / multi_model_graph_async (dx_app src/cpp_example/multi_model_graph). Studio
does not link them: every call is a subprocess with a timeout, started in the dx_app root so a relative "uri" resolves
the way the CLI documents. Contract: tests/dx_app/test_graph_cli.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import uuid
from pathlib import Path

from dx_app.core import config
from shared import dxrt
from shared.paths import var_dir
from shared.runtime import ld_library_path

NAMES = {"sync": "multi_model_graph_sync", "async": "multi_model_graph_async"}
# A model every dx_app registry has (eight of the thirteen shipped sample graphs use it); the "engine" probe needs one.
PROBE_MODEL = "yolov8-n_640x640"

_caps_lock = threading.Lock()
_caps_cache: dict = {}


class GraphCliMissing(RuntimeError):
    """The graph binary is neither built (dx_app ./build.sh) nor shipped in bin/."""


def _search_dirs() -> list[Path]:
    root = Path(config.DX_APP_ROOT)
    return [Path(config.BUILD_DIR), root / "bin", root / "build_x86_64" / "src" / "cpp_example",
            root / "build_aarch64" / "src" / "cpp_example"]


def binary(variant: str = "sync") -> Path | None:
    name = NAMES[variant]
    for d in _search_dirs():
        p = d / name
        if p.is_file() and os.access(p, os.X_OK):
            return p
    return None


def available():
    """(variant, path) of the graph binary Studio uses for --check, --list-models and probes: sync, else async."""
    for v in ("sync", "async"):
        b = binary(v)
        if b is not None:
            return v, b
    return None


def models_dir() -> Path:
    return Path(config.MODELS_DIR)


def env() -> dict:
    """Environment of every graph CLI call: DX-RT libraries, Qt off screen, the runner's [PROGRESS] lines on."""
    return dxrt.run_env({**os.environ, "QT_QPA_PLATFORM": "offscreen",
                         "LD_LIBRARY_PATH": ld_library_path(), "DXAPP_PROGRESS": "1"})


def run(args: list[str], variant: str | None = None, timeout: float = 30.0) -> subprocess.CompletedProcess:
    """Run a graph binary: `variant`, or with None whichever build exists (available())."""
    if variant is None:
        found = available()
        variant = found[0] if found else "sync"
    b = binary(variant)
    if b is None:
        raise GraphCliMissing(f"{NAMES[variant]} not found: build dx_app (./build.sh --target multi_model_graph_sync multi_model_graph_async)")
    return subprocess.run([str(b), *args], capture_output=True, text=True, cwd=str(config.DX_APP_ROOT),
                          env=env(), timeout=timeout)


def mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0


def scratch_file(prefix: str) -> Path:
    """A fresh path for a temporary graph file (var/dx_app/graph_check)."""
    return var_dir("dx_app", "graph_check") / f"{prefix}_{uuid.uuid4().hex}.json"


def _probe_engine_key() -> bool:
    probe = {"version": 1, "name": "studio-probe",
             "nodes": [{"id": "cam", "type": "source", "uri": "sample/img/sample_people.jpg"},
                       {"id": "m", "model": PROBE_MODEL, "engine": {"buffers": 2, "share": True}}],
             "edges": [{"from": "cam", "to": "m"}]}
    path = scratch_file("probe")
    path.write_text(json.dumps(probe), encoding="utf-8")
    try:
        r = run(["--check", str(path), "--model-dir", str(models_dir())], timeout=10)
    except (subprocess.SubprocessError, OSError):
        return False
    finally:
        path.unlink(missing_ok=True)
    out = r.stdout + r.stderr
    if 'unknown key "engine"' in out:
        return False
    if r.returncode == 0 and ("OK: graph" in out or re.search(r'"ok"\s*:\s*true', out)):
        return True
    # The graph was read with its "engine" key and failed later (a model that is missing or cannot load).
    codes = set(re.findall(r"ERROR \[([A-Z_]+)\]", out)) | set(re.findall(r'"code"\s*:\s*"([A-Z_]+)"', out))
    return bool(codes) and "GRAPH_SCHEMA" not in codes


# What --help names for each capability Studio reads from it.
_HELP_FLAGS = {"json": "--json", "report_timing": "--report-timing", "list_ops": "--list-ops",
               "events": "--events", "loop": "--loop", "draw": "--draw", "output_layers": "--output-layers"}


def no_capabilities() -> dict:
    return {"json": False, "engine_key": False, "report_timing": False, "list_ops": False, "events": False,
            "loop": False, "draw": False, "output_layers": False}


def capabilities() -> dict:
    """{"json": --list-models / --check print JSON with --json, "engine_key": nodes accept "engine",
    "report_timing": --report-timing adds per-node ms to --report, "list_ops": --list-ops --json lists the logic
    blocks, "events": --events <file.jsonl> writes every event, "loop": --loop restarts video sources at the end,
    "draw": --draw <ids> draws only those nodes, "output_layers": --output-layers <dir> writes each node's drawing
    alone (README "Results for front ends")}.

    Probed once per binary build (keyed by the binary's path and mtime)."""
    found = available()
    if found is None:
        return no_capabilities()
    b = found[1]
    key = (str(b), mtime(b))
    with _caps_lock:
        if key in _caps_cache:
            return dict(_caps_cache[key])
    caps = no_capabilities()
    try:
        r = run(["--help"], timeout=10)
        text = r.stdout + r.stderr
        for name, flag in _HELP_FLAGS.items():
            caps[name] = re.search(re.escape(flag) + r"(?![\w-])", text) is not None
    except (subprocess.SubprocessError, OSError):
        pass
    caps["engine_key"] = _probe_engine_key()
    with _caps_lock:
        _caps_cache.clear()
        _caps_cache[key] = dict(caps)
    return caps

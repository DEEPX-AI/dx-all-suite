"""Graph Composer Phase 3: take a graph away as a standalone C++ (CMake) project.

dx_app's scripts/export_graph_project.py does the work, so Studio holds no C++ knowledge: it copies the engine and the
factories of the graph's models, writes the user-logic stubs, CMakeLists.txt, main.cpp, setup.sh, run.sh and a README.
This module prepares the graph the way a run does (the run panel's input per source, inputs and galleries under the
input roots, never a run's upload; the node "engine" settings kept for the exported engine), asks the exporter for a
plan, and exports into
outputs/dx_app/graph/exports/<name>-<stamp>/: the project folder and its zip. The newest KEEP exports are kept.

    POST /api/graph/export/plan {graph, name?, inputs?}                  plan(): what an export holds, its size
    POST /api/graph/export      {graph, name, include_models?, inputs?}  export(): the folder and a zip to download
                                                                         (include_models: false unless true)

An export does not touch the NPU, so it runs beside a run or a Live; one export runs at a time.
Contract: tests/dx_app/test_graph_export.py
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import threading
import time
import zipfile
from pathlib import Path

from dx_app.core import config, graph_cli, graph_run

EXPORTER = Path("scripts") / "export_graph_project.py"
SCHEMA = "export_graph_project 1"
NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,47}")
KEEP = 5
TIMEOUT_S = 300
HEADROOM = 256 * 1024 * 1024        # what an export leaves free on the disk
_STORED = (".dxnn", ".bin", ".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi", ".mkv", ".webm")
# The exporter's refusals that are the graph's or the request's doing; anything else is a server error.
CLIENT_ERRORS = {"graph_unreadable", "name_invalid", "model_unknown", "model_not_ready", "user_name_invalid",
                 "user_kind_invalid", "user_kind_conflict", "input_missing", "gallery_missing"}

_lock = threading.Lock()             # one export at a time
_probe = {"key": None, "value": False}


def exporter() -> Path | None:
    p = Path(config.DX_APP_ROOT) / EXPORTER
    return p if p.is_file() else None


def available() -> bool:
    """dx_app ships the exporter and it speaks this schema (`--version`); probed once per version of the file."""
    p = exporter()
    if p is None:
        return False
    key = (str(p), graph_cli.mtime(p))
    if _probe["key"] == key:
        return _probe["value"]
    try:
        r = subprocess.run([sys.executable, str(p), "--version"], capture_output=True, text=True, timeout=30,
                           cwd=str(config.DX_APP_ROOT))
        ok = r.returncode == 0 and r.stdout.strip() == SCHEMA
    except (OSError, subprocess.SubprocessError):
        return False        # a busy host or a passing error: not remembered, the next call asks again
    _probe.update(key=key, value=ok)
    return ok


def exports_dir() -> Path:
    d = Path(config.OUTPUTS_DIR) / "graph" / "exports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _fail(key: str, text: str, status: int = 400) -> tuple:
    return {"ok": False, "error": text, "error_key": key}, status


class Refused(ValueError):
    def __init__(self, key: str, text: str):
        super().__init__(text)
        self.key = key


def check_name(name) -> str:
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise Refused("export_name_invalid", "the folder name must be 1 to 48 letters, digits, _ or -, starting with "
                                             "a letter")
    return name


def prepare(graph: dict, inputs=None) -> dict:
    """The graph an export writes: the node "engine" settings kept, each source reading the run panel's
    input for it (a sample path; an upload is not exported) or its own "uri", a file made absolute once it is found
    under the input roots, a camera or a stream kept as it is."""
    if inputs is not None and not isinstance(inputs, dict):
        raise Refused("invalid_payload", "inputs must be an object")
    problem = graph_run.gallery_problem(graph)
    if problem:
        raise Refused("gallery_outside_roots", problem[1])
    # The node "engine" settings stay whatever the local graph binary reads: the project is built from this dx_app's
    # sources, which have the exporter and so read them.
    out = json.loads(json.dumps(graph))
    for n in out.get("nodes") or []:
        if not isinstance(n, dict) or n.get("type") != "source":
            continue
        uri = (inputs or {}).get(n.get("id")) or n.get("uri") or ""
        if not isinstance(uri, str):
            raise Refused("invalid_input", f"source {n.get('id')!r}: the input must be a path")
        if not uri or uri.startswith(graph_run._LIVE):
            n["uri"] = uri
            continue
        try:
            found = graph_run._resolve_uri(uri)
        except ValueError:
            raise Refused("invalid_input", f"source {n.get('id')!r}: {uri} is not an image or a video under the "
                                           "dx_app, sample, assets or outputs folders")
        if any(_under(found, d) for d in _UPLOAD_DIRS()):
            raise Refused("invalid_input", f"source {n.get('id')!r}: {uri} is an upload kept by a run; an upload is "
                                           "not exported (pick a sample or keep the graph's own input)")
        n["uri"] = str(found)
    return out


def _UPLOAD_DIRS() -> tuple:
    """Where runs and Lives keep their uploads: graph_run.runs_dir() and graph_live.live_dir(), named here without
    making them (a plan writes nothing)."""
    graph = Path(config.OUTPUTS_DIR) / "graph"
    return graph / "runs", graph / "live"


def _under(path: Path, folder: Path) -> bool:
    real, base = Path(path).resolve(), Path(folder).resolve()
    return real == base or base in real.parents


def _run(args: list, timeout: float = TIMEOUT_S) -> tuple:
    """(the exporter's JSON answer, HTTP status) of one call with --json."""
    p = exporter()
    if p is None or not available():
        return _fail("export_unsupported", "this dx_app has no scripts/export_graph_project.py of schema 1", 409)
    try:
        r = subprocess.run([sys.executable, str(p), *args, "--json"], capture_output=True, text=True,
                           timeout=timeout, cwd=str(config.DX_APP_ROOT))
    except subprocess.TimeoutExpired:
        return _fail("export_failed", f"the export took longer than {timeout:.0f} s", 500)
    except OSError as e:
        return _fail("export_failed", str(e), 500)
    lines = r.stdout.strip().splitlines()
    try:
        body = json.loads(lines[-1]) if lines else None
    except ValueError:
        body = None
    if not isinstance(body, dict):
        return _fail("export_failed", (r.stderr or r.stdout).strip()[-500:] or f"exit {r.returncode}", 500)
    if r.returncode != 0 or body.get("ok") is not True:
        key = body.get("error_key") or "export_failed"
        status = 400 if key in CLIENT_ERRORS else 409 if key == "model_file_missing" else 500
        return _fail(key, body.get("error") or "the export failed", status)
    return body, 200


def _graph_file(graph: dict) -> Path:
    path = graph_cli.scratch_file("export")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph), encoding="utf-8")
    return path


def _model_args(include_models: bool) -> list:
    return ["--model-dir", str(graph_cli.models_dir())] + ([] if include_models else ["--no-models"])


def plan(graph: dict, name=None, inputs=None) -> tuple:
    """What an export of `graph` would hold, without writing it: the exporter's --dry-run answer."""
    try:
        if name not in (None, ""):
            check_name(name)
        g = prepare(graph, inputs)
    except Refused as e:
        return _fail(e.key, str(e))
    path = _graph_file(g)
    try:
        return _run(["--graph", str(path), "--dry-run"] + (["--name", name] if name else []) + _model_args(True))
    finally:
        path.unlink(missing_ok=True)


def export(graph: dict, name, include_models: bool = False, inputs=None) -> tuple:
    """Export `graph` as <exports>/<name>-<stamp>/<name>/ and <name>.zip beside it; ({..., folder, zip_url,
    zip_bytes}, 200) or ({error, error_key}, status)."""
    try:
        check_name(name)
        g = prepare(graph, inputs)
    except Refused as e:
        return _fail(e.key, str(e))
    if not _lock.acquire(blocking=False):
        return _fail("export_busy", "another export is running; wait for it", 409)
    path, folder = None, None
    try:
        path = _graph_file(g)
        args = ["--graph", str(path), "--name", name] + _model_args(include_models)
        planned, code = _run(args + ["--dry-run"])
        if code != 200:
            return planned, code
        need = 2 * int(planned.get("bytes") or 0) + HEADROOM          # the folder, its zip, and room to spare
        free = shutil.disk_usage(exports_dir()).free
        if free < need:
            body, status = _fail("export_no_space", f"the export needs {need / 1048576:.0f} MB free (the project "
                                                    f"and its zip) and the disk has {free / 1048576:.0f} MB", 507)
            body.update(need_bytes=need, free_bytes=free)
            return body, status
        base = exports_dir() / f"{name}-{time.strftime('%Y%m%d-%H%M%S')}"
        folder, k = base, 2
        while folder.exists():
            folder, k = Path(f"{base}-{k}"), k + 1
        folder.mkdir(parents=True)
        body, code = _run(args + ["--out", str(folder / name)])
        if code != 200:
            shutil.rmtree(folder, ignore_errors=True)
            return body, code
        zip_path = folder / f"{name}.zip"
        _zip(folder / name, zip_path, name)
        body.update(folder=str(folder / name), zip_bytes=zip_path.stat().st_size,
                    zip_url="/outputs/" + zip_path.relative_to(Path(config.OUTPUTS_DIR)).as_posix())
        _prune(KEEP, keep_too=folder)          # only once this export is whole: a failed one costs no old export
        return body, 200
    except Exception as e:                     # anything after the folder is made: nothing half-written stays
        if folder is not None:
            shutil.rmtree(folder, ignore_errors=True)
        return _fail("export_failed", str(e) or type(e).__name__, 500)
    finally:
        if path is not None:
            path.unlink(missing_ok=True)
        _lock.release()


def _zip(src: Path, zip_path: Path, root: str) -> None:
    """`src` as `<root>/...` in `zip_path`: models and media stored, text deflated, each file's mode kept (setup.sh
    and run.sh stay executable when unzipped)."""
    part = zip_path.with_name(zip_path.name + ".part")
    with zipfile.ZipFile(part, "w") as z:
        for p in sorted(src.rglob("*")):
            if p.is_symlink() or not p.is_file():
                continue
            method = zipfile.ZIP_STORED if p.suffix.lower() in _STORED else zipfile.ZIP_DEFLATED
            z.write(p, f"{root}/{p.relative_to(src).as_posix()}", compress_type=method)
    part.replace(zip_path)


def _prune(keep: int, keep_too: Path | None = None) -> None:
    """Keep the newest `keep` export folders (`keep_too`, the export just made, counts as one and always stays)."""
    dirs = sorted((p for p in exports_dir().iterdir() if p.is_dir() and p != keep_too),
                  key=lambda p: p.stat().st_mtime, reverse=True)
    for p in dirs[max(keep - (1 if keep_too is not None else 0), 0):]:
        shutil.rmtree(p, ignore_errors=True)

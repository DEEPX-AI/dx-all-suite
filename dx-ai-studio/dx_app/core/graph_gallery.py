"""Build a gallery for the graph's `gallery` logic op: a DXGAL1 `.bin` of embeddings, made from an image folder by
dx_app's own builder (the same preprocessing as the model's runner, so the vectors match what the graph computes):

    <runtime python> scripts/build_gallery_database.py --variant <model> --images <folder> --out <file>.bin
                     --models-dir <models>

The folder lies under the run's input roots (graph_run.input_roots(); no `..`, folders only). One subfolder per
person names each image after its folder; images in one folder are named after their files. The script runs in the
DX-RT runtime venv (numpy, cv2, dx_engine), holds the NPU like every other job (npu_jobs.py), and is stopped after
_TIMEOUT seconds or when the server shuts down. The file goes to outputs/dx_app/graph/galleries/<name>.bin (written to
a temporary name first, so a failed build leaves no file).

    POST /api/graph/gallery/build {folder, model, name?}
      200 {path, gallery, url, name, model, images, people, names, dim, log_tail}

Contract: tests/dx_app/test_graph_gallery.py
"""
from __future__ import annotations

import atexit
import os
import re
import struct
import subprocess
import threading
import uuid
from pathlib import Path

from dx_app.core import config, graph_cli, graph_run, npu_jobs
from dx_app.core.dx_app_security import resolve_existing_path

SCRIPT = Path("scripts") / "build_gallery_database.py"
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
MAX_IMAGES = 20000
_TIMEOUT = float(os.environ.get("DX_GRAPH_GALLERY_MAX_SECONDS") or 1800)
_STOP_GRACE = 5.0
_LOG_TAIL = 4000
_NAME = re.compile(r"^[A-Za-z0-9_-][A-Za-z0-9_.-]{0,63}$")
_MODEL = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.+-]{0,127}$")
_MAGIC = b"DXGAL1\0\0"

# Why a gallery cannot be built now, by the kind of job holding the NPU (npu_jobs.py)
_BUSY = {"gallery": {"error": "a gallery is already being built", "error_key": "gallery_busy"},
         "graph_run": {"error": "a graph run is running", "error_key": "graph_run_busy"},
         "graph_live": {"error": "a graph Live is running; stop it first", "error_key": "graph_live_busy"},
         "live": {"error": "the Run page has a Live run; stop it first", "error_key": "live_busy"}}

_lock = threading.Lock()
_procs: dict = {}               # job_id -> the running builder


def galleries_dir() -> Path:
    return Path(config.OUTPUTS_DIR) / "graph" / "galleries"


def _python():
    """The DX-RT runtime interpreter Studio runs dx_app's Python examples with (numpy, cv2), or None."""
    return getattr(config, "_RUNTIME_PYTHON", None)


def _env() -> dict:
    env = graph_cli.env()
    extra = getattr(config, "_RUNTIME_PYTHONPATH", "")
    if extra:                    # dx_engine is on PYTHONPATH, not pip-installed (as for the Python examples)
        env["PYTHONPATH"] = extra + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def _err(key: str, msg: str, code: int, **extra) -> tuple:
    return {"error": msg, "error_key": key, **extra}, code


def _folder(value) -> Path:
    """The gallery folder: an existing directory under the input roots (relative paths from the dx_app root)."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("folder is required")
    cand = Path(value) if Path(value).is_absolute() else Path(config.DX_APP_ROOT) / value
    p = resolve_existing_path(str(cand), graph_run.input_roots())
    if not p.is_dir():
        raise ValueError(f"not a folder: {value}")
    return p


def _count_images(folder: Path) -> int:
    n = 0
    for p in folder.rglob("*"):
        if p.suffix.lower() in IMAGE_SUFFIXES and p.is_file():
            n += 1
            if n > MAX_IMAGES:
                break
    return n


def read_summary(path: Path):
    """{images, dim, model, people, names} of a DXGAL1 file (a name is the label, else the image's file stem), or
    None when it is not one."""
    try:
        with open(path, "rb") as fh:
            if fh.read(8) != _MAGIC:
                return None
            n, dim = struct.unpack("<II", fh.read(8))
            fh.seek(4 * n * dim, os.SEEK_CUR)
            blobs = []
            for _ in range(3):
                (size,) = struct.unpack("<I", fh.read(4))
                blobs.append(fh.read(size).decode("utf-8", "replace"))
    except (OSError, struct.error):
        return None
    model, paths, labels = blobs[0], blobs[1].split("\n") if blobs[1] else [], blobs[2].split("\n")
    names = sorted({(labels[i] if i < len(labels) and labels[i] else Path(p).stem) for i, p in enumerate(paths)})
    return {"images": n, "dim": dim, "model": model, "people": len(names), "names": names}


def build(folder, model, name=None) -> tuple:
    """Build a gallery; (summary, 200) or ({"error", "error_key"}, status)."""
    try:
        src = _folder(folder)
    except ValueError as e:
        return _err("invalid_folder", str(e), 400)
    if not isinstance(model, str) or not _MODEL.fullmatch(model) or ".." in model:
        return _err("invalid_model", "model must be a model name such as osnet_x0_25_256x128", 400)
    if name is not None and (not isinstance(name, str) or not _NAME.fullmatch(name) or ".." in name):
        return _err("invalid_name", "name must be 1-64 letters, digits, '_', '.' or '-'", 400)
    models = Path(graph_cli.models_dir())
    if not (models / f"{model}.dxnn").is_file():
        return _err("model_missing", f"{model}.dxnn is not installed; download it in the Model Zoo first", 409)
    images = _count_images(src)
    if images == 0:
        return _err("gallery_no_images", f"no images ({', '.join(IMAGE_SUFFIXES)}) in {folder}", 400)
    if images > MAX_IMAGES:
        return _err("gallery_too_many_images", f"a gallery takes at most {MAX_IMAGES} images", 400)
    script = Path(config.DX_APP_ROOT) / SCRIPT
    if not script.is_file():
        return _err("gallery_script_missing", f"{SCRIPT} is not in this dx_app", 409)
    python = _python()
    if not python:
        return _err("runtime_python_missing", "the DX-RT runtime Python (venv-dx-runtime) was not found", 409)
    stem = name or re.sub(r"[^A-Za-z0-9_.-]", "_", f"{src.name}_{model}")[:64].lstrip(".") or "gallery"
    out_dir = galleries_dir()
    final = out_dir / f"{stem}.bin"

    job_id = uuid.uuid4().hex
    holder = npu_jobs.acquire("gallery", job_id)
    if holder is not None:
        return dict(_BUSY[holder]), 409
    tmp = out_dir / f".{stem}.{job_id}.bin"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [python, str(script), "--variant", model, "--images", str(src), "--out", str(tmp),
               "--models-dir", str(models)]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                    errors="replace", cwd=str(config.DX_APP_ROOT), env=_env(), close_fds=True)
        except (OSError, subprocess.SubprocessError) as e:
            return _err("gallery_build_failed", str(e), 500)
        npu_jobs.attach(job_id, proc)
        with _lock:
            _procs[job_id] = proc
        try:
            log, _ = proc.communicate(timeout=_TIMEOUT)
        except subprocess.TimeoutExpired:
            graph_run._terminate(proc, _STOP_GRACE)
            log = (proc.communicate()[0] or "") if proc.stdout else ""
            return _err("gallery_timeout", f"the gallery build took longer than {_TIMEOUT:g} s and was stopped "
                        "(DX_GRAPH_GALLERY_MAX_SECONDS sets the limit)", 504, log_tail=log[-_LOG_TAIL:])
        finally:
            with _lock:
                _procs.pop(job_id, None)
        log = log or ""
        summary = read_summary(tmp) if proc.returncode == 0 else None
        if summary is None:
            errors = [ln.strip() for ln in log.splitlines() if "[ERROR]" in ln]
            why = errors[-1] if errors else (f"the builder exited with code {proc.returncode}"
                                             if proc.returncode else "the builder wrote no gallery file")
            return _err("gallery_build_failed", why, 422, log_tail=log[-_LOG_TAIL:])
        os.replace(tmp, final)
    finally:
        npu_jobs.release(job_id)
        tmp.unlink(missing_ok=True)
    url = "/outputs/" + final.relative_to(Path(config.OUTPUTS_DIR)).as_posix()
    return {"path": str(final), "gallery": str(final), "url": url, "name": stem, **summary,
            "log_tail": log[-_LOG_TAIL:]}, 200


def stop_all() -> None:
    """Stop a running build before the server exits (atexit, idle watchdog)."""
    with _lock:
        procs = list(_procs.values())
    for proc in procs:
        graph_run._terminate(proc, _STOP_GRACE)


atexit.register(stop_all)

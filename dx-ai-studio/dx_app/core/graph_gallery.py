"""Build a gallery for the graph's `gallery` logic op: a DXGAL1 `.bin` of embeddings, made from an image folder by
dx_app's own builder (the same preprocessing as the model's runner, so the vectors match what the graph computes):

    <runtime python> scripts/build_gallery_database.py --variant <model> --images <staged folder> --out <file>.bin
                     --models-dir <models>

The folder lies under the run's input roots (graph_run.input_roots(); no `..`, folders only). Studio lists it itself
(at most MAX_ENTRIES entries visited, MAX_IMAGES images), keeps only images whose real path (symlinks resolved) is
under the input roots, and hands the builder a staged temporary folder of links to those files in the same layout:
the builder never walks the folder itself. One subfolder per person names each image after its folder; images in
one folder are named after their files. The script runs in the DX-RT runtime venv (numpy, cv2, dx_engine) with no
terminal input, holds the NPU like every other job (npu_jobs.py), and is stopped after _TIMEOUT seconds, by the
page, or when the server shuts down; the hold ends with it. The file goes to outputs/dx_app/graph/galleries/<name>.bin
(written to a temporary name first, so a failed build leaves no file).

    POST /api/graph/gallery/build {folder, model, name?}
      200 {job_id, status: "started", images}            the build runs on; a refusal answers at once (400/409/500)
    GET  /api/graph/gallery/poll?id=
      200 {job_id, state: "running", elapsed, images}
      200 {job_id, state: "done", elapsed, path, gallery, url, name, model, images, people, names, dim, log_tail}
      200 {job_id, state: "failed", elapsed, error, error_key, log_tail}
          error_key gallery_build_failed | gallery_timeout | gallery_stopped | gallery_exists
      404 {error: "unknown_job", error_key: "unknown_job"}
    POST /api/graph/gallery/stop {id}   200 {status: "stopping" | "no_process"}

A gallery is never built over one that exists: a name already taken is refused at start (409 gallery_exists), and a
file of that name that appears while building fails the build with the same key, the file left as it is.
A finished build is kept _DONE_TTL seconds (at most _KEEP_DONE of them) for the page to poll.
Contract: tests/dx_app/test_graph_gallery.py
"""
from __future__ import annotations

import atexit
import os
import re
import shutil
import struct
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path

from dx_app.core import config, graph_cli, graph_run, npu_jobs
from dx_app.core.dx_app_security import resolve_existing_path

SCRIPT = Path("scripts") / "build_gallery_database.py"
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
MAX_IMAGES = 20000
MAX_ENTRIES = 100000        # files and folders a listing visits at most (folder "." is the whole dx_app tree)
_DONE_TTL = 600.0
_KEEP_DONE = 8
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
_jobs: dict = {}                # job_id -> {"id", "proc", "state", "result", "start", "end", "stop_reason", ...}


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


class _Refused(Exception):
    def __init__(self, key, msg):
        super().__init__(msg)
        self.key = key


def _images(folder: Path) -> list:
    """[(path relative to `folder`, real path)] of the images under `folder` whose real path (symlinks resolved) lies
    under the input roots, in a stable order. Symlinked folders are not entered. Raises _Refused past MAX_ENTRIES
    visited entries or MAX_IMAGES images, without walking the rest."""
    roots = [Path(r).resolve() for r in graph_run.input_roots()]
    out, visited = [], 0
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames.sort()
        visited += len(dirnames) + len(filenames)
        if visited > MAX_ENTRIES:
            raise _Refused("gallery_folder_too_large", f"the folder holds more than {MAX_ENTRIES} files and folders; "
                                                       "pick the folder of the gallery's images")
        for name in sorted(filenames):
            if Path(name).suffix.lower() not in IMAGE_SUFFIXES:
                continue
            p = Path(dirpath) / name
            try:
                real = p.resolve(strict=True)
            except (OSError, RuntimeError):
                continue
            if not real.is_file() or not any(real.is_relative_to(r) for r in roots):
                continue
            out.append((p.relative_to(folder), real))
            if len(out) > MAX_IMAGES:
                raise _Refused("gallery_too_many_images", f"a gallery takes at most {MAX_IMAGES} images")
    return out


def _stage(src: Path, images: list) -> tuple:
    """(temporary dir, the folder to hand the builder): links to the vetted images in their layout under `src`."""
    tmp = Path(tempfile.mkdtemp(prefix="dx-gallery-"))
    top = tmp / (src.name or "images")
    try:
        for rel, real in images:
            dst = top / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(real, dst)
    except OSError:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return tmp, top


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


def start(folder, model, name=None) -> tuple:
    """Start a build; ({"job_id", "status", "images"}, 200), or ({"error", "error_key"}, status) when refused."""
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
    try:
        images = _images(src)
    except _Refused as e:
        return _err(e.key, str(e), 400)
    if not images:
        return _err("gallery_no_images", f"no images ({', '.join(IMAGE_SUFFIXES)}) in {folder}", 400)
    script = Path(config.DX_APP_ROOT) / SCRIPT
    if not script.is_file():
        return _err("gallery_script_missing", f"{SCRIPT} is not in this dx_app", 409)
    python = _python()
    if not python:
        return _err("runtime_python_missing", "the DX-RT runtime Python (venv-dx-runtime) was not found", 409)
    stem = name or re.sub(r"[^A-Za-z0-9_.-]", "_", f"{src.name}_{model}")[:64].lstrip(".") or "gallery"
    out_dir = galleries_dir()
    if (out_dir / f"{stem}.bin").exists():
        return _exists(stem)

    job_id = uuid.uuid4().hex
    holder = npu_jobs.acquire("gallery", job_id)
    if holder is not None:
        return dict(_BUSY[holder]), 409
    job = {"id": job_id, "proc": None, "state": "running", "result": None, "start": time.time(), "end": None,
           "stop_reason": None, "images": len(images), "stem": stem, "final": out_dir / f"{stem}.bin",
           "tmp": out_dir / f".{stem}.{job_id}.bin", "stage": None}
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        job["stage"], staged = _stage(src, images)
        cmd = [python, str(script), "--variant", model, "--images", str(staged), "--out", str(job["tmp"]),
               "--models-dir", str(models)]
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, errors="replace", cwd=str(config.DX_APP_ROOT), env=_env(), close_fds=True)
    except (OSError, subprocess.SubprocessError) as e:
        npu_jobs.release(job_id)
        _cleanup(job)
        return _err("gallery_build_failed", str(e), 500)
    if not npu_jobs.attach(job_id, proc, kind="gallery"):
        npu_jobs.release(job_id)
        proc.kill()
        proc.communicate()
        _cleanup(job)
        return dict(npu_jobs.LOST), 409
    job["proc"] = proc
    with _lock:
        _prune(time.time())
        _jobs[job_id] = job
    threading.Thread(target=_run, args=(job,), daemon=True, name=f"graph-gallery-{job_id[:8]}").start()
    return {"job_id": job_id, "status": "started", "images": len(images)}, 200


def _exists(stem: str) -> tuple:
    return _err("gallery_exists", f"a gallery named {stem} already exists; pick another name", 409)


def _place(job: dict) -> None:
    """The built file under its name, never over a file of that name (os.replace would replace it): a hard link,
    which fails when the name is taken; where links are not supported, a check, then a rename."""
    try:
        os.link(job["tmp"], job["final"])
        return
    except FileExistsError:
        pass
    except OSError:
        if not job["final"].exists():
            os.replace(job["tmp"], job["final"])
            return
    body, _ = _exists(job["stem"])
    raise _Refused(body["error_key"], body["error"])


def _cleanup(job: dict) -> None:
    job["tmp"].unlink(missing_ok=True)
    if job["stage"] is not None:
        shutil.rmtree(job["stage"], ignore_errors=True)


def _run(job: dict) -> None:
    """Wait for the builder (at most _TIMEOUT seconds), then record how the build ended and give the NPU back."""
    proc, log, result = job["proc"], "", None
    try:
        try:
            log, _ = proc.communicate(timeout=_TIMEOUT)
        except subprocess.TimeoutExpired:
            job["stop_reason"] = job["stop_reason"] or "timeout"
            graph_run._terminate(proc, _STOP_GRACE)
            log = proc.communicate()[0]
        log = log or ""
        tail = log[-_LOG_TAIL:]
        if job["stop_reason"] == "timeout":
            result = {"state": "failed", "error_key": "gallery_timeout", "log_tail": tail,
                      "error": f"the gallery build took longer than {_TIMEOUT:g} s and was stopped "
                               "(DX_GRAPH_GALLERY_MAX_SECONDS sets the limit)"}
        elif job["stop_reason"]:
            result = {"state": "failed", "error_key": "gallery_stopped", "log_tail": tail,
                      "error": "the gallery build was stopped" + (" (the server is shutting down)"
                                                                  if job["stop_reason"] == "server" else "")}
        else:
            summary = read_summary(job["tmp"]) if proc.returncode == 0 else None
            if summary is None:
                errors = [ln.strip() for ln in log.splitlines() if "[ERROR]" in ln]
                why = errors[-1] if errors else (f"the builder exited with code {proc.returncode}"
                                                 if proc.returncode else "the builder wrote no gallery file")
                result = {"state": "failed", "error_key": "gallery_build_failed", "error": why, "log_tail": tail}
            else:
                _place(job)
                url = "/outputs/" + job["final"].relative_to(Path(config.OUTPUTS_DIR)).as_posix()
                result = {"state": "done", "path": str(job["final"]), "gallery": str(job["final"]), "url": url,
                          "name": job["stem"], **summary, "log_tail": tail}
    except _Refused as e:
        result = {"state": "failed", "error_key": e.key, "error": str(e), "log_tail": log[-_LOG_TAIL:]}
    except Exception as e:                      # the build must end in a state the page can read
        result = {"state": "failed", "error_key": "gallery_build_failed", "error": str(e), "log_tail": log[-_LOG_TAIL:]}
    finally:
        npu_jobs.release(job["id"])
        _cleanup(job)
        with _lock:
            job["result"] = result or {"state": "failed", "error_key": "gallery_build_failed",
                                       "error": "the build ended unexpectedly", "log_tail": ""}
            job["state"], job["end"] = job["result"]["state"], time.time()


def _prune(now: float) -> None:
    """Drop finished builds older than _DONE_TTL, keeping at most _KEEP_DONE. Caller holds _lock."""
    done = sorted((j for j in _jobs.values() if j["end"] is not None), key=lambda j: j["end"], reverse=True)
    for i, j in enumerate(done):
        if i >= _KEEP_DONE or now - j["end"] > _DONE_TTL:
            _jobs.pop(j["id"], None)


def poll(job_id) -> tuple:
    """(state of a build, 200), or ({"error", "error_key": "unknown_job"}, 404)."""
    with _lock:
        _prune(time.time())
        job = _jobs.get(job_id) if isinstance(job_id, str) else None
        if job is None:
            return {"error": "unknown_job", "error_key": "unknown_job"}, 404
        elapsed = round((job["end"] or time.time()) - job["start"], 1)
        if job["result"] is None:
            return {"job_id": job["id"], "state": "running", "elapsed": elapsed, "images": job["images"]}, 200
        return {"job_id": job["id"], "elapsed": elapsed, **job["result"]}, 200


def stop(job_id) -> dict:
    """Stop a running build (SIGTERM, then SIGKILL): it ends as failed with error_key gallery_stopped."""
    with _lock:
        job = _jobs.get(job_id) if isinstance(job_id, str) else None
    if job is None or job["result"] is not None or job["proc"].poll() is not None:
        return {"status": "no_process"}
    job["stop_reason"] = job["stop_reason"] or "user"
    threading.Thread(target=graph_run._terminate, args=(job["proc"], _STOP_GRACE), daemon=True).start()
    return {"status": "stopping"}


def stop_all() -> None:
    """Stop a running build before the server exits (atexit, idle watchdog); its NPU hold ends with it."""
    with _lock:
        jobs = [j for j in _jobs.values() if j["result"] is None and j["proc"] is not None]
    for job in jobs:
        job["stop_reason"] = job["stop_reason"] or "server"
        graph_run._terminate(job["proc"], _STOP_GRACE)


atexit.register(stop_all)

"""Run a graph once on an image or a video with dx_app's graph binary; report progress, per-node time and results.

One job is one subprocess

    multi_model_graph_{sync,async} --graph graph.json --input <source>=<file> ... --output result.jpg|raw.mp4
                                   --report report.json --model-dir <models> [--max-inflight N] [--frames N]

in its own folder outputs/dx_app/graph/runs/<job>. The page polls: progress comes from the runner's
`[PROGRESS] frames=N fps=F avg_fps=A node_ms=<id>:<ms>,...` lines (DXAPP_PROGRESS=1), results from --report once it
exits. Same lifetime rule as run_progress.py: a job nobody polls for _JOB_TTL seconds is stopped and dropped.
Camera and RTSP sources belong to Live (a later phase) and are refused here.
Contract: tests/dx_app/test_graph_run.py
"""
from __future__ import annotations

import base64
import binascii
import json
import re
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import unquote

from dx_app.core import config, graph_cli
from dx_app.core.dx_app_security import resolve_existing_file
from dx_app.core.graph_validate import engine_graph, parse_errors

_JOB_TTL = 600.0
_KEEP_RUN_DIRS = 20
_MAX_UPLOAD_B64 = 20 * 1024 * 1024
_IMAGE_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
_VIDEO_EXT = (".mp4", ".mov", ".avi", ".mkv", ".webm")
_LIVE = ("camera:", "rtsp://", "rtsps://", "http://", "https://")
_PROGRESS = re.compile(r"^\[PROGRESS\] (.*)$")

_lock = threading.Lock()
_jobs: dict = {}


def runs_dir() -> Path:
    d = Path(config.OUTPUTS_DIR) / "graph" / "runs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def input_roots() -> tuple:
    return (Path(config.DX_APP_ROOT), Path(config.SAMPLE_DIR), Path(config.ASSETS_DIR), Path(config.OUTPUTS_DIR))


def parse_progress_line(line: str):
    """{frames, fps, avg_fps, ..., node_ms: {id: ms}} from one [PROGRESS] line, else None."""
    m = _PROGRESS.match((line or "").strip())
    if not m:
        return None
    out = {"node_ms": {}}
    for part in m.group(1).split():
        key, _, value = part.partition("=")
        if key == "node_ms":
            for item in value.split(","):
                nid, _, ms = item.rpartition(":")
                try:
                    out["node_ms"][unquote(nid)] = float(ms)      # ids are percent-encoded by the runner
                except ValueError:
                    pass
        elif key:
            try:
                out[key] = float(value)
            except ValueError:
                pass
    return out


def _item(i: dict) -> dict:
    return {k: i[k] for k in ("class_name", "class_id", "score", "confidence", "track_id", "box") if k in i}


def summarize_report(path: Path, max_items: int = 20) -> dict:
    """Per-node results of a --report file: shape, how many frames and items, the last frame's items, average ms."""
    out = {"frames": 0, "error_frames": 0, "nodes": {}, "node_ms": {}}
    try:
        if not path.is_file() or path.stat().st_size > 256 * 1024 * 1024:
            return out
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return out
    frames = data.get("frames") or []
    out["frames"] = len(frames)
    ms_sum, ms_n = {}, {}

    def node(nid):
        return out["nodes"].setdefault(nid, {"shape": None, "frames": 0, "items_total": 0, "crops_total": 0,
                                              "last_items": []})

    for fr in frames:
        if fr.get("error"):
            out["error_frames"] += 1
        for nid, res in (fr.get("nodes") or {}).items():
            payload = (res or {}).get("payload") or {}
            items = payload.get("items") or []
            s = node(nid)
            s["shape"] = payload.get("shape") or s["shape"]
            s["frames"] += 1
            s["items_total"] += len(items)
            s["last_items"] = [_item(i) for i in items[:max_items] if isinstance(i, dict)]
        for nid, crops in (fr.get("roi_nodes") or {}).items():
            crops = crops or []
            s = node(nid)
            s["frames"] += 1
            s["crops_total"] += len(crops)
            last = []
            for c in crops[:max_items]:
                payload, origin = (c or {}).get("payload") or {}, (c or {}).get("origin") or {}
                s["shape"] = payload.get("shape") or s["shape"]
                entry = {"src_box": origin.get("src_box"), "track_id": origin.get("track_id")}
                items = [i for i in payload.get("items") or [] if isinstance(i, dict)]
                if items:
                    entry["top"] = _item(items[0])
                last.append(entry)
            s["last_items"] = last
        for nid, ms in (fr.get("node_ms") or {}).items():
            try:
                ms_sum[nid] = ms_sum.get(nid, 0.0) + float(ms)
                ms_n[nid] = ms_n.get(nid, 0) + 1
            except (TypeError, ValueError):
                pass
    out["node_ms"] = {k: round(ms_sum[k] / ms_n[k], 2) for k in ms_sum}
    return out


def _resolve_uri(uri) -> Path:
    if not isinstance(uri, str) or not uri.strip():
        raise ValueError("empty input")
    if uri.startswith(_LIVE):
        raise ValueError("live_source")
    cand = Path(uri) if Path(uri).is_absolute() else Path(config.DX_APP_ROOT) / uri
    return resolve_existing_file(str(cand), input_roots(), _IMAGE_EXT + _VIDEO_EXT)


def _write_upload(d: Path, sid: str, b64) -> Path:
    if not isinstance(b64, str):
        raise ValueError("upload must be a base64 string")
    raw = b64.split(",", 1)[1] if b64.startswith("data:") else b64
    if len(raw) > _MAX_UPLOAD_B64:
        raise ValueError("upload is too large")
    try:
        data = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("upload is not valid base64")
    ext = ".png" if data[:8] == b"\x89PNG\r\n\x1a\n" else ".jpg" if data[:2] == b"\xff\xd8" else None
    if not ext:
        raise ValueError("upload must be a JPEG or PNG image")
    p = d / f"input_{sid}{ext}"
    p.write_bytes(data)
    return p


def _prune_runs(keep: int = _KEEP_RUN_DIRS) -> None:
    with _lock:
        active = {str(j["dir"]) for j in _jobs.values()}
    dirs = sorted((p for p in runs_dir().iterdir() if p.is_dir()), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in dirs[keep:]:
        if str(p) not in active:
            shutil.rmtree(p, ignore_errors=True)


def _reap(now: float) -> None:
    """Drop jobs nobody polled for _JOB_TTL seconds, stopping a run that is still going. Caller holds _lock."""
    for jid in [j for j, e in _jobs.items() if now - e["touched"] > _JOB_TTL]:
        job = _jobs.pop(jid)
        if job["proc"].poll() is None:
            job["proc"].kill()


def _int_in(value, lo, hi, label):
    if value in (None, ""):
        return None
    try:
        v = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a whole number")
    if not lo <= v <= hi:
        raise ValueError(f"{label} must be between {lo} and {hi}")
    return v


def start(graph: dict, *, variant="sync", inputs=None, uploads=None, max_inflight=None, frames=None):
    """Start a run; returns ({"job_id"}, 200) or ({"error", "error_key"}, status)."""
    if variant not in graph_cli.NAMES:
        return {"error": f"unknown variant {variant!r}", "error_key": "invalid_payload"}, 400
    if inputs is not None and not isinstance(inputs, dict):
        return {"error": "inputs must be an object", "error_key": "invalid_payload"}, 400
    if uploads is not None and not isinstance(uploads, dict):
        return {"error": "uploads must be an object", "error_key": "invalid_payload"}, 400
    try:
        max_inflight = _int_in(max_inflight, 1, 64, "max_inflight")
        frames = _int_in(frames, 1, 100000, "frames")
    except ValueError as e:
        return {"error": str(e), "error_key": "invalid_payload"}, 400
    binary = graph_cli.binary(variant)
    if binary is None:
        return {"error": f"{graph_cli.NAMES[variant]} is not built", "error_key": "graph_binary_missing"}, 409
    sources = [n for n in graph.get("nodes") or [] if isinstance(n, dict) and n.get("type") == "source"]
    if not sources:
        return {"error": "the graph has no source", "error_key": "no_source"}, 400
    with _lock:
        _reap(time.time())
        if any(j["result"] is None for j in _jobs.values()):
            return {"error": "a graph run is already running", "error_key": "graph_run_busy"}, 409
    _prune_runs()
    job_id = uuid.uuid4().hex
    d = runs_dir() / job_id
    d.mkdir(parents=True)
    args, video = [], False
    try:
        for s in sources:
            sid = str(s.get("id") or "")
            if uploads and sid in uploads:
                p = _write_upload(d, sid, uploads[sid])
            else:
                p = _resolve_uri((inputs or {}).get(sid) or s.get("uri"))
            video = video or p.suffix.lower() in _VIDEO_EXT
            args += ["--input", f"{sid}={p}"]
    except ValueError as e:
        shutil.rmtree(d, ignore_errors=True)
        key = "live_source" if str(e) == "live_source" else "invalid_input"
        return {"error": str(e), "error_key": key}, 400
    caps = graph_cli.capabilities()
    (d / "graph.json").write_text(json.dumps(engine_graph(graph, caps)), encoding="utf-8")
    cmd = [str(binary), "--graph", str(d / "graph.json"), *args,
           "--output", str(d / ("raw.mp4" if video else "result.jpg")), "--report", str(d / "report.json"),
           "--model-dir", str(graph_cli.models_dir())]
    if caps.get("report_timing"):
        cmd.append("--report-timing")
    if variant == "async" and max_inflight:
        cmd += ["--max-inflight", str(max_inflight)]
    if frames:
        cmd += ["--frames", str(frames)]
    log = (d / "run.log").open("w", encoding="utf-8")
    try:
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=str(config.DX_APP_ROOT),
                                env=graph_cli.env(), text=True, close_fds=True)
    except OSError as e:
        log.close()
        shutil.rmtree(d, ignore_errors=True)
        return {"error": str(e), "error_key": "graph_run_failed"}, 500
    now = time.time()
    job = {"id": job_id, "dir": d, "proc": proc, "log": log, "graph": graph, "video": video, "start": now,
           "touched": now, "cursor": 0, "progress": {"node_ms": {}}, "result": None}
    with _lock:
        _jobs[job_id] = job
    threading.Thread(target=_wait, args=(job,), daemon=True, name=f"graph-run-{job_id[:8]}").start()
    return {"job_id": job_id, "status": "started"}, 200


def _outputs(d: Path, video: bool) -> list:
    out = []
    if video:
        from dx_app.core.performance import _cvt_video
        for raw in sorted(d.glob("raw*.mp4")):
            dst = d / ("result" + raw.name[len("raw"):])
            if _cvt_video(raw, dst):
                raw.unlink(missing_ok=True)
                out.append(dst)
    else:
        out = sorted(p for p in d.glob("result*") if p.suffix.lower() in _IMAGE_EXT)
    base = Path(config.OUTPUTS_DIR)
    return [{"url": "/outputs/" + p.relative_to(base).as_posix(), "kind": "video" if video else "image",
             "name": p.name} for p in out]


def _last_progress(text: str) -> dict:
    last = {"node_ms": {}}
    for line in (text or "").splitlines():
        p = parse_progress_line(line)
        if p:
            last = p
    return last


def _wait(job: dict) -> None:
    code = job["proc"].wait()
    job["log"].close()
    d = job["dir"]
    try:
        log = (d / "run.log").read_text(encoding="utf-8", errors="replace")
    except OSError:
        log = ""
    errors, _notes = parse_errors(log, job["graph"])
    report = summarize_report(d / "report.json")
    last = _last_progress(log)
    outputs = _outputs(d, job["video"])
    result = {"ok": code == 0 and not errors, "exit_code": code, "outputs": outputs,
              "frames": report["frames"] or int(last.get("frames", 0)), "error_frames": report["error_frames"],
              "fps": last.get("fps"), "avg_fps": last.get("avg_fps"),
              "node_ms": report["node_ms"] or last.get("node_ms") or {}, "nodes": report["nodes"],
              "errors": errors, "log_tail": log[-4000:], "elapsed": round(time.time() - job["start"], 1)}
    with _lock:
        job["result"] = result
        job["touched"] = time.time()


def poll(job_id: str) -> dict:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return {"error": "unknown_job"}
        job["touched"] = time.time()
        cursor = job["cursor"]
    try:
        with open(job["dir"] / "run.log", "rb") as f:
            f.seek(cursor)
            buf = f.read()
    except OSError:
        buf = b""
    nl = buf.rfind(b"\n")
    if nl != -1:
        latest = None
        for line in buf[: nl + 1].decode("utf-8", "replace").splitlines():
            latest = parse_progress_line(line) or latest
        with _lock:
            if job["cursor"] == cursor:
                job["cursor"] = cursor + nl + 1
                if latest:
                    job["progress"] = latest
    with _lock:
        p = dict(job["progress"])
        return {"running": job["result"] is None, "frames": int(p.get("frames", 0)), "fps": p.get("fps"),
                "avg_fps": p.get("avg_fps"), "node_ms": p.get("node_ms") or {},
                "elapsed": round(time.time() - job["start"], 1), "has_result": job["result"] is not None}


def result(job_id: str) -> dict:
    """{"running": True} until the run ends; then its result, once (the job is dropped)."""
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return {"error": "unknown_job"}
        job["touched"] = time.time()
        if job["result"] is None:
            return {"running": True}
        _jobs.pop(job_id)
        return job["result"]


def stop(job_id: str) -> dict:
    """SIGTERM: the runner finishes the frames in flight and finalizes --report and --output (README "Options")."""
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return {"status": "no_process"}
        job["touched"] = time.time()
        proc = job["proc"]
    if proc.poll() is None:
        proc.terminate()
        return {"status": "stopping"}
    return {"status": "no_process"}

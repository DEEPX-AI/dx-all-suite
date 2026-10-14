"""Run a graph once on an image or a video with dx_app's graph binary; report progress, per-node time and results.

One job is one subprocess

    multi_model_graph_{sync,async} --graph graph.json --input <source>=<file> ... --output result.jpg|raw.mp4
                                   --report report.json --model-dir <models> [--events events.jsonl]
                                   [--max-inflight N] [--frames N]

in its own folder outputs/dx_app/graph/runs/<job>. The page polls: progress comes from the runner's
`[PROGRESS] frames=N fps=F avg_fps=A node_ms=<id>:<ms>,...` lines (DXAPP_PROGRESS=1), results from --report once it
exits; events from its `[EVENT] {json}` lines while it runs (numbered, so a poll asks only for new ones) and from
--events once it exits (graph_events.py). Same lifetime rule as run_progress.py: a job nobody polls for _JOB_TTL seconds is stopped and dropped.
One NPU job at a time (npu_jobs.py: a run once, a graph Live or the Run page's Live): the NPU is taken before
anything is prepared and given back when the runner exits. A run is stopped (SIGTERM, then
SIGKILL after _STOP_GRACE seconds) when it outlives DX_GRAPH_RUN_MAX_SECONDS (default 600) or its log outgrows
_MAX_LOG_BYTES, and every run is stopped when the server shuts down (atexit and the idle watchdog).
Camera and RTSP sources belong to Live (a later phase) and are refused here.
Contract: tests/dx_app/test_graph_run.py
"""
from __future__ import annotations

import atexit
import base64
import binascii
import json
import os
import re
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import unquote

from dx_app.core import config, graph_cli, graph_events, npu_jobs
from dx_app.core.dx_app_security import resolve_existing_file
from dx_app.core.graph_validate import engine_graph, parse_errors

_JOB_TTL = 600.0
_STOP_GRACE = 5.0
_MAX_RUN_SECONDS = float(os.environ.get("DX_GRAPH_RUN_MAX_SECONDS") or 600)
_MAX_LOG_BYTES = 8 * 1024 * 1024
_POLL_READ_BYTES = 256 * 1024       # of the log per poll, from where the last poll stopped
_RESULT_LOG_BYTES = 4 * 1024 * 1024  # the log's tail a finished run is read from (errors, last progress, events)
_SOURCE_ID = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
_KEEP_RUN_DIRS = 20
_MAX_UPLOAD_B64 = 20 * 1024 * 1024
# All uploads of one run together. dx_app/server.py accepts at most 24 MB of JSON on /api/graph/run; the uploads stay
# below it with room for the graph, so too many images get this error instead of the server's bare 413.
MAX_UPLOADS_TOTAL_B64 = 20 * 1024 * 1024
_IMAGE_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
_VIDEO_EXT = (".mp4", ".mov", ".avi", ".mkv", ".webm")
_LIVE = ("camera:", "rtsp://", "rtsps://", "http://", "https://")
_PROGRESS = re.compile(r"^\[PROGRESS\] (.*)$")

_lock = threading.Lock()
_jobs: dict = {}
# Why a run once cannot start, by the kind of job holding the NPU (npu_jobs.py)
_BUSY = {"graph_run": {"error": "a graph run is already running", "error_key": "graph_run_busy"},
         "graph_live": {"error": "a graph Live is running; stop it first", "error_key": "graph_live_busy"},
         "live": {"error": "the Run page has a Live run; stop it first", "error_key": "live_busy"},
         "gallery": {"error": "a gallery is being built; wait for it", "error_key": "gallery_busy"}}


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


def summarize_report(path: Path, max_items: int = 20, sources=()) -> dict:
    """Per-node results of a --report file: shape, how many frames and items, the last frame's items, average ms.
    dx_app lists the source nodes too (an image digest); the ids in `sources` are left out of "nodes"."""
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
            if nid in sources:
                continue
            payload = (res or {}).get("payload") or {}
            items = payload.get("items") or []
            s = node(nid)
            s["shape"] = payload.get("shape") or s["shape"]
            s["frames"] += 1
            s["items_total"] += len(items)
            s["last_items"] = [_item(i) for i in items[:max_items] if isinstance(i, dict)]
            if payload.get("shape") == "records":                # logic and cpu nodes: numbers per record
                s["last_records"] = [{"numbers": dict(i.get("numbers") or {}), "text": dict(i.get("text") or {})}
                                     for i in items[:max_items] if isinstance(i, dict)]
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
    for jid in [j for j, e in _jobs.items() if now - e["touched"] > _JOB_TTL and e["proc"] is not None]:
        job = _jobs.pop(jid)
        if job["proc"].poll() is None:
            job["proc"].kill()


def _terminate(proc, grace=None) -> None:
    """SIGTERM (the runner finishes the frames in flight and closes its outputs), SIGKILL after `grace` seconds."""
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=_STOP_GRACE if grace is None else grace)
    except subprocess.TimeoutExpired:
        proc.kill()


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
    total = sum(len(v) for v in (uploads or {}).values() if isinstance(v, str))
    if total > MAX_UPLOADS_TOTAL_B64:
        return {"error": f"the uploaded images add up to {total / 1048576:.1f} MB; one run takes at most "
                         f"{MAX_UPLOADS_TOTAL_B64 // 1048576} MB of uploads",
                "error_key": "uploads_too_large", "limit_bytes": MAX_UPLOADS_TOTAL_B64}, 413
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
    bad = [s.get("id") for s in sources
           if not isinstance(s.get("id"), str) or not _SOURCE_ID.fullmatch(s["id"]) or not s["id"].strip(".")]
    if bad:
        return {"error": f"source id {bad[0]!r} must be 1-64 letters, digits, '_', '.' or '-'",
                "error_key": "invalid_source_id"}, 400
    job_id = uuid.uuid4().hex
    d = runs_dir() / job_id
    now = time.time()
    job = {"id": job_id, "dir": d, "proc": None, "log": None, "graph": graph, "video": False, "start": now,
           "touched": now, "cursor": 0, "progress": {"node_ms": {}}, "result": None, "stop_reason": None,
           "events": graph_events.EventLog()}
    with _lock:
        _reap(now)
        holder = npu_jobs.acquire("graph_run", job_id)    # the NPU is taken before anything is prepared
        if holder is not None:
            return dict(_BUSY[holder]), 409
        _jobs[job_id] = job

    def give_up(body, code):
        npu_jobs.release(job_id)
        with _lock:
            _jobs.pop(job_id, None)
        if job["log"] is not None:
            job["log"].close()
        shutil.rmtree(d, ignore_errors=True)
        return body, code

    try:
        _prune_runs()
        d.mkdir(parents=True)
        args, video = [], False
        for s in sources:
            sid = s["id"]
            if uploads and sid in uploads:
                p = _write_upload(d, sid, uploads[sid])
            else:
                p = _resolve_uri((inputs or {}).get(sid) or s.get("uri"))
            video = video or p.suffix.lower() in _VIDEO_EXT
            args += ["--input", f"{sid}={p}"]
        caps = graph_cli.capabilities()
        (d / "graph.json").write_text(json.dumps(engine_graph(graph, caps)), encoding="utf-8")
        cmd = [str(binary), "--graph", str(d / "graph.json"), *args,
               "--output", str(d / ("raw.mp4" if video else "result.jpg")), "--report", str(d / "report.json"),
               "--model-dir", str(graph_cli.models_dir())]
        if caps.get("report_timing"):
            cmd.append("--report-timing")
        if caps.get("events"):
            cmd += ["--events", str(d / "events.jsonl")]
        if variant == "async" and max_inflight:
            cmd += ["--max-inflight", str(max_inflight)]
        if frames:
            cmd += ["--frames", str(frames)]
        job["log"] = (d / "run.log").open("w", encoding="utf-8")
        proc = subprocess.Popen(cmd, stdout=job["log"], stderr=subprocess.STDOUT, cwd=str(config.DX_APP_ROOT),
                                env=graph_cli.env(), text=True, close_fds=True)
    except ValueError as e:
        key = "live_source" if str(e) == "live_source" else "invalid_input"
        return give_up({"error": str(e), "error_key": key}, 400)
    except (OSError, subprocess.SubprocessError) as e:
        return give_up({"error": str(e), "error_key": "graph_run_failed"}, 500)
    except BaseException:
        give_up({}, 500)
        raise
    if not npu_jobs.attach(job_id, proc, kind="graph_run"):
        proc.kill()
        proc.wait()
        return give_up(dict(npu_jobs.LOST), 409)
    with _lock:
        job["proc"], job["video"] = proc, video
        job["start"] = job["touched"] = time.time()
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
    rows = []
    for p in out:
        row = {"url": "/outputs/" + p.relative_to(base).as_posix(), "kind": "video" if video else "image",
               "name": p.name}
        if video:
            row["fps"] = video_fps(p)       # the event list seeks the video to an event's frame
        rows.append(row)
    return rows


def video_fps(path: Path):
    """Frames per second of a video (ffprobe's average rate), or None when unknown."""
    if not shutil.which("ffprobe"):
        return None
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=avg_frame_rate", "-of", "csv=p=0", str(path)],
                             stdin=subprocess.DEVNULL, capture_output=True, text=True,
                             timeout=15).stdout.strip().split(",")[0]
        num, _, den = out.partition("/")
        fps = float(num) / float(den or 1)
        return round(fps, 3) if fps > 0 else None
    except (OSError, subprocess.SubprocessError, ValueError, ZeroDivisionError):
        return None


def events_of(d: Path, log_text: str, log_cut: bool = False) -> dict:
    """A finished run's events: the --events file when dx_app wrote one, else the [EVENT] lines of its log. When
    `log_text` is only the log's tail (`log_cut`), those are the tail's events: their total and counts are
    "events_partial"."""
    f = d / "events.jsonl"
    if f.is_file():
        listing = graph_events.read_jsonl(f)
        url, partial = "/outputs/" + f.relative_to(Path(config.OUTPUTS_DIR)).as_posix(), False
    else:
        printed = graph_events.EventLog(keep=graph_events.LIST_MAX)
        printed.feed(log_text)
        listing, url, partial = printed.listing(), None, bool(log_cut)
    return {"events": listing["events"], "event_total": listing["total"], "event_counts": listing["counts"],
            "events_truncated": listing["truncated"], "events_url": url, "events_partial": partial}


def _last_progress(text: str) -> dict:
    last = {"node_ms": {}}
    for line in (text or "").splitlines():
        p = parse_progress_line(line)
        if p:
            last = p
    return last


def _read_tail(path: Path, limit: int) -> str:
    """At most the last `limit` bytes of a log."""
    try:
        with open(path, "rb") as f:
            size = f.seek(0, 2)
            f.seek(max(0, size - limit))
            return f.read(limit).decode("utf-8", "replace")
    except OSError:
        return ""


def _limit_error(reason: str) -> dict:
    if reason == "timeout":
        what = f"the run took longer than {_MAX_RUN_SECONDS:g} s and was stopped"
        how = "run fewer frames or a shorter video (DX_GRAPH_RUN_MAX_SECONDS sets the limit)"
        code = "RUN_TIMEOUT"
    else:
        what = f"the run printed more than {_MAX_LOG_BYTES // (1024 * 1024) or 1} MB of log and was stopped"
        how = "check the log tail for a message repeated on every frame"
        code = "RUN_LOG_LIMIT"
    return {"code": code, "where": "graph", "what": what, "how": how, "node": None, "edge": None}


def _wait(job: dict) -> None:
    proc, log_path = job["proc"], job["dir"] / "run.log"
    while True:
        try:
            code = proc.wait(timeout=0.2)
            break
        except subprocess.TimeoutExpired:
            pass
        if job["stop_reason"]:
            continue
        reason = None
        if time.time() - job["start"] > _MAX_RUN_SECONDS:
            reason = "timeout"
        else:
            try:
                if log_path.stat().st_size > _MAX_LOG_BYTES:
                    reason = "log"
            except OSError:
                pass
        if reason:
            job["stop_reason"] = reason
            threading.Thread(target=_terminate, args=(proc,), daemon=True).start()
    npu_jobs.release(job["id"])
    job["log"].close()
    d = job["dir"]
    log = _read_tail(log_path, _RESULT_LOG_BYTES)
    try:
        log_cut = log_path.stat().st_size > _RESULT_LOG_BYTES
    except OSError:
        log_cut = False
    errors, _notes = parse_errors(log, job["graph"])
    if job["stop_reason"] in ("timeout", "log"):
        errors.insert(0, _limit_error(job["stop_reason"]))
    sources = {n.get("id") for n in job["graph"].get("nodes") or []
               if isinstance(n, dict) and n.get("type") == "source"}
    report = summarize_report(d / "report.json", sources=sources)
    last = _last_progress(log)
    outputs = _outputs(d, job["video"])
    result = {"ok": code == 0 and not errors, "exit_code": code, "outputs": outputs,
              "frames": report["frames"] or int(last.get("frames", 0)), "error_frames": report["error_frames"],
              "fps": last.get("fps"), "avg_fps": last.get("avg_fps"),
              "node_ms": report["node_ms"] or last.get("node_ms") or {}, "nodes": report["nodes"],
              "errors": errors, "log_tail": log[-4000:], "elapsed": round(time.time() - job["start"], 1),
              **events_of(d, log, log_cut)}
    with _lock:
        job["result"] = result
        job["touched"] = time.time()


def poll(job_id: str, events_after=0) -> dict:
    """Progress of a run, and the events numbered after `events_after` (at most graph_events.PAGE)."""
    try:
        events_after = max(0, int(events_after or 0))
    except (TypeError, ValueError):
        events_after = 0
    with _lock:
        _reap(time.time())
        job = _jobs.get(job_id)
        if job is None:
            return {"error": "unknown_job", "error_key": "unknown_job"}
        job["touched"] = time.time()
        cursor = job["cursor"]
    try:
        with open(job["dir"] / "run.log", "rb") as f:
            f.seek(cursor)
            buf = f.read(_POLL_READ_BYTES)          # a bounded slice; the next poll goes on from the cursor
    except OSError:
        buf = b""
    nl = buf.rfind(b"\n")
    if nl == -1 and len(buf) >= _POLL_READ_BYTES:
        # one line longer than a slice: skip what was read of it (the rest begins the next slice)
        with _lock:
            if job["cursor"] == cursor:
                job["cursor"] = cursor + len(buf)
    elif nl != -1:
        latest, chunk = None, buf[: nl + 1].decode("utf-8", "replace")
        for line in chunk.splitlines():
            latest = parse_progress_line(line) or latest
        with _lock:
            if job["cursor"] == cursor:
                job["cursor"] = cursor + nl + 1
                job["events"].feed(chunk)
                if latest:
                    job["progress"] = latest
    with _lock:
        p = dict(job["progress"])
        return {"running": job["result"] is None, "frames": int(p.get("frames", 0)), "fps": p.get("fps"),
                "avg_fps": p.get("avg_fps"), "node_ms": p.get("node_ms") or {},
                "elapsed": round(time.time() - job["start"], 1), "has_result": job["result"] is not None,
                "events": job["events"].since(events_after), **job["events"].snapshot()}


def result(job_id: str) -> dict:
    """{"running": True} until the run ends; then its result, once (the job is dropped)."""
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return {"error": "unknown_job", "error_key": "unknown_job"}
        job["touched"] = time.time()
        if job["result"] is None:
            return {"running": True}
        _jobs.pop(job_id)
        return job["result"]


def stop(job_id: str) -> dict:
    """SIGTERM: the runner finishes the frames in flight and finalizes --report and --output (README "Options");
    SIGKILL when it is still running _STOP_GRACE seconds later."""
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return {"status": "no_process"}
        job["touched"] = time.time()
        proc = job["proc"]
    if proc is not None and proc.poll() is None:
        job["stop_reason"] = job["stop_reason"] or "user"
        threading.Thread(target=_terminate, args=(proc,), daemon=True).start()
        return {"status": "stopping"}
    return {"status": "no_process"}


def stop_all() -> None:
    """Stop every run before the server exits (atexit, idle watchdog): SIGTERM all, SIGKILL what is left."""
    with _lock:
        procs = [j["proc"] for j in _jobs.values() if j["proc"] is not None and j["proc"].poll() is None]
    for proc in procs:
        proc.terminate()
    deadline = time.time() + _STOP_GRACE
    for proc in procs:
        try:
            proc.wait(timeout=max(0.0, deadline - time.time()))
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass


atexit.register(stop_all)

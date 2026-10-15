"""Run a graph Live: a camera, an RTSP stream or a looping video, shown through the Live display path of the Run
page (dx_app/core/live.py, camera.py): the runner draws each rendered frame in its own window (--display) on a
private Xvfb display, and the page watches an MJPEG stream grabbed from that display.

    multi_model_graph_{sync,async} --graph graph.json --input <source>=camera:N|rtsp://...|<video> ...
                                   --display [--loop] [--events events.jsonl] --model-dir <models>
                                   [--max-inflight N] [--draw <id,id...>]

`draw` (picked on the page before start) keeps the picture to those nodes; every node still runs and reports. With
several sources the runner's one window is a grid of the streams, each cell labelled with its source id, so the
MJPEG stream shows them all.

One graph Live at a time, on its own Xvfb slot (SLOT; the Run page's Live uses slots 0-7), so the two never draw on
one display. One NPU job at a time (npu_jobs.py): a graph Live, a graph run once and the Run page's Live never overlap
(each loads its engines on the NPU); the hold is taken before anything is prepared and ends when the runner exits.
stdout is read as it comes (line-buffered through coreutils' stdbuf when it exists: a pipe would otherwise hold the
runner's lines in a 4 KB buffer): [PROGRESS] lines give FPS and per-node ms, [EVENT] lines go to an EventLog
(bounded), everything else to a bounded tail for errors. A Live nobody polls for _TTL seconds is stopped (the page was closed),
as is one whose --events file outgrows _MAX_EVENTS_BYTES; every Live stops with the server.
Contract: tests/dx_app/test_graph_live.py
"""
from __future__ import annotations

import atexit
import hmac
import json
import os
import re
import shutil
import subprocess
import threading
import time
import uuid
from collections import deque
from pathlib import Path

from dx_app.core import config, graph_cli, graph_events, graph_run, npu_jobs
from dx_app.core.graph_validate import engine_graph, parse_errors

SLOT = 8
_TTL = 30.0
_STOP_GRACE = 5.0
_MAX_EVENTS_BYTES = 64 * 1024 * 1024
_TAIL_LINES = 400
_CAMERA = re.compile(r"^camera:(\d{1,2})$")
_STREAM = re.compile(r"^rtsp://[^\s]{1,500}$")    # rtsp:// only: what dx_app's runner opens as a stream
_KEEP_LIVE_DIRS = 20            # outputs/graph/live/<job>/ folders kept, newest first (the running one always)

_lock = threading.Lock()
_job = None                     # the one graph Live: dict, or None
# Why a graph Live cannot start, by the kind of job holding the NPU (npu_jobs.py)
_BUSY = {"graph_live": {"error": "a graph Live is already running", "error_key": "graph_live_busy"},
         "graph_run": {"error": "a graph run is running", "error_key": "graph_run_busy"},
         "live": {"error": "the Run page has a Live run; stop it first", "error_key": "live_busy"},
         "gallery": {"error": "a gallery is being built; wait for it", "error_key": "gallery_busy"}}


def live_dir() -> Path:
    d = Path(config.OUTPUTS_DIR) / "graph" / "live"
    d.mkdir(parents=True, exist_ok=True)
    return d


def running() -> bool:
    with _lock:
        return _job is not None and _job["proc"] is not None and _job["proc"].poll() is None


def _deps_missing() -> list:
    """What the Live display path needs on this host (the same check as the Run page's Live)."""
    from dx_app.core import camera
    missing = []
    if not shutil.which("Xvfb"):
        missing.append("Xvfb (sudo apt install xvfb)")
    if camera._xcb() is None:
        missing.append("libxcb (sudo apt install libxcb1)")
    try:
        import PIL  # noqa: F401
    except ImportError:
        missing.append("Pillow")
    return missing


def resolve_input(value) -> tuple:
    """(argument for --input, is a file) for one source: camera:N, an rtsp:// URL, or a video under the input roots."""
    v = str(value or "").strip()
    m = _CAMERA.fullmatch(v)
    if m:
        if not Path(f"/dev/video{int(m.group(1))}").exists():
            raise ValueError(f"camera {m.group(1)} is not connected (/dev/video{int(m.group(1))})")
        return v, False
    if v.lower().startswith("rtsps://"):
        raise ValueError("rtsps:// is not supported: dx_app opens rtsp:// streams")
    if v.startswith("rtsp://"):
        if not _STREAM.fullmatch(v):
            raise ValueError("an RTSP address is one rtsp:// URL without spaces")
        return v, False
    if not v:
        raise ValueError("empty input")
    cand = Path(v) if Path(v).is_absolute() else Path(config.DX_APP_ROOT) / v
    from dx_app.core.dx_app_security import resolve_existing_file
    p = resolve_existing_file(str(cand), graph_run.input_roots(), graph_run._VIDEO_EXT)
    return str(p), True


def _env() -> dict:
    from dx_app.core.camera import _XVFB_BASE, _XVFB_RES
    env = graph_cli.env()
    env.pop("QT_QPA_PLATFORM", None)            # the runner's window is drawn on the Xvfb display
    env["DISPLAY"] = f":{_XVFB_BASE + SLOT}"
    w, h = (int(v) for v in _XVFB_RES.split("x")[:2])
    env["DXAPP_SCREEN_W"], env["DXAPP_SCREEN_H"] = str(2 * w), str(2 * h)
    return env


def _draw_ids(graph: dict, draw) -> list:
    """The node ids of a `draw` pick, checked against the graph: a list of 1 to 256 ids (duplicates dropped) of
    nodes that are not sources. ValueError otherwise."""
    if not isinstance(draw, list) or not draw or len(draw) > 256 or not all(isinstance(i, str) for i in draw):
        raise ValueError("draw must list the ids of the nodes to draw")
    drawable = {n.get("id") for n in graph.get("nodes") or [] if isinstance(n, dict) and n.get("type") != "source"}
    bad = [i for i in draw if i not in drawable]
    if bad:
        raise ValueError(f"{bad[0]!r} is not a node of this graph that draws")
    return list(dict.fromkeys(draw))


def start(graph: dict, *, variant="sync", inputs=None, max_inflight=None, draw=None) -> tuple:
    """Start the graph Live; ({"job_id"}, 200) or ({"error", "error_key"}, status). `draw`: the node ids to draw
    (None: every node)."""
    if variant not in graph_cli.NAMES:
        return {"error": f"unknown variant {variant!r}", "error_key": "invalid_payload"}, 400
    if inputs is not None and not isinstance(inputs, dict):
        return {"error": "inputs must be an object", "error_key": "invalid_payload"}, 400
    try:
        max_inflight = graph_run._int_in(max_inflight, 1, 64, "max_inflight")
    except ValueError as e:
        return {"error": str(e), "error_key": "invalid_payload"}, 400
    if draw is not None:
        try:
            draw = _draw_ids(graph, draw)
        except ValueError as e:
            return {"error": str(e), "error_key": "invalid_draw"}, 400
    binary = graph_cli.binary(variant)
    if binary is None:
        return {"error": f"{graph_cli.NAMES[variant]} is not built", "error_key": "graph_binary_missing"}, 409
    sources = [n for n in graph.get("nodes") or [] if isinstance(n, dict) and n.get("type") == "source"]
    if not sources:
        return {"error": "the graph has no source", "error_key": "no_source"}, 400
    if any(not isinstance(s.get("id"), str) or not graph_run._SOURCE_ID.fullmatch(s["id"]) for s in sources):
        return {"error": "source ids must be 1-64 letters, digits, '_', '.' or '-'",
                "error_key": "invalid_source_id"}, 400
    missing = _deps_missing()
    if missing:
        return {"error": "Live needs: " + ", ".join(missing), "error_key": "live_deps_missing"}, 409
    args, files = [], False
    try:
        for s in sources:
            arg, is_file = resolve_input((inputs or {}).get(s["id"]) or s.get("uri"))
            files = files or is_file
            args += ["--input", f"{s['id']}={arg}"]
    except ValueError as e:
        return {"error": str(e), "error_key": "invalid_live_input"}, 400
    caps = graph_cli.capabilities()
    if draw and not caps.get("draw"):
        return {"error": "this dx_app build draws every node (no --draw)", "error_key": "draw_unsupported"}, 409
    if files and not caps.get("loop"):
        return {"error": "this dx_app build cannot loop a video (no --loop); use a camera or an RTSP stream",
                "error_key": "loop_unsupported"}, 409
    global _job
    job_id = uuid.uuid4().hex
    with _lock:
        holder = npu_jobs.acquire("graph_live", job_id)    # the NPU is taken before anything is prepared
        if holder is not None:
            return dict(_BUSY[holder]), 409
        old, _job = _job, None
    from dx_app.core import camera
    if old is not None:
        # Its runner has exited (the NPU was free), but its reader may still be draining stdout; it would close the
        # display after this Live opened it. It is no longer the current Live, so it leaves the display to this one.
        _finish(old)
        old["done"].wait(_STOP_GRACE + 2)
    d = live_dir() / job_id
    try:
        d.mkdir(parents=True)
        (d / "graph.json").write_text(json.dumps(engine_graph(graph, caps)), encoding="utf-8")
        graph_run._prune_runs(_KEEP_LIVE_DIRS, live_dir(), active=(d,))
    except OSError as e:
        npu_jobs.release(job_id)
        shutil.rmtree(d, ignore_errors=True)
        camera.stop_xvfb(SLOT)
        return {"error": str(e), "error_key": "graph_live_failed"}, 500
    cmd = [str(binary), "--graph", str(d / "graph.json"), *args, "--display", "--model-dir",
           str(graph_cli.models_dir())]
    if files:
        cmd.append("--loop")
    if caps.get("events"):
        cmd += ["--events", str(d / "events.jsonl")]
    if variant == "async" and max_inflight:
        cmd += ["--max-inflight", str(max_inflight)]
    if draw:
        cmd += ["--draw", ",".join(draw)]
    if shutil.which("stdbuf"):
        cmd = [shutil.which("stdbuf"), "-oL", "-eL"] + cmd
    try:
        camera._ensure_xvfb(SLOT)
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                cwd=str(config.DX_APP_ROOT), env=_env(), text=True, bufsize=1, errors="replace",
                                close_fds=True)
    except (OSError, subprocess.SubprocessError) as e:
        npu_jobs.release(job_id)
        shutil.rmtree(d, ignore_errors=True)
        camera.stop_xvfb(SLOT)
        return {"error": str(e), "error_key": "graph_live_failed"}, 500
    if not npu_jobs.attach(job_id, proc, kind="graph_live"):
        npu_jobs.release(job_id)
        proc.kill()
        proc.communicate()
        shutil.rmtree(d, ignore_errors=True)
        camera.stop_xvfb(SLOT)
        return dict(npu_jobs.LOST), 409
    now = time.time()
    job = {"id": job_id, "dir": d, "proc": proc, "graph": graph, "start": now, "touched": now,
           "progress": {"node_ms": {}}, "events": graph_events.EventLog(), "tail": deque(maxlen=_TAIL_LINES),
           "result": None, "stop_reason": None, "done": threading.Event(),
           "events_url": "/outputs/" + (d / "events.jsonl").relative_to(Path(config.OUTPUTS_DIR)).as_posix()}
    with _lock:
        _job = job
    threading.Thread(target=_read, args=(job,), daemon=True, name=f"graph-live-{job_id[:8]}").start()
    threading.Thread(target=_watch, args=(job,), daemon=True, name=f"graph-live-watch-{job_id[:8]}").start()
    return {"job_id": job_id, "status": "started", "frame_url": f"/api/graph/live/frame?id={job_id}"}, 200


def _read(job: dict) -> None:
    """The runner's stdout, line by line, until it exits. However it ends, the hold is given back and `done` is set;
    the display is closed only while this is still the current Live (a newer one may already draw on it)."""
    try:
        for line in job["proc"].stdout:
            p = graph_run.parse_progress_line(line)
            if p:
                job["progress"] = p
                continue
            ev = graph_events.parse_event_line(line)
            if ev:
                job["events"].add(ev)
                continue
            job["tail"].append(line.rstrip("\n"))
    finally:
        try:
            code = job["proc"].wait()
            npu_jobs.release(job["id"])
            tail = "\n".join(job["tail"])
            errors, _notes = parse_errors(tail, job["graph"])
            if job["stop_reason"] == "events":
                errors.insert(0, {"code": "LIVE_EVENTS_LIMIT", "where": "graph", "node": None, "edge": None,
                                  "what": f"the events file passed {_MAX_EVENTS_BYTES // 1048576} MB and Live was "
                                          "stopped",
                                  "how": "raise a condition's cooldown or narrow its zone so fewer events fire"})
            url = job["events_url"] if (job["dir"] / "events.jsonl").is_file() else None
            with _lock:
                job["result"] = {"exit_code": code, "errors": errors, "log_tail": tail[-4000:], "events_url": url,
                                 "stopped_by": job["stop_reason"]}
                current = _job is job
            if current:
                from dx_app.core import camera
                camera.stop_xvfb(SLOT)
        finally:
            npu_jobs.release(job["id"])
            if job["result"] is None:
                job["result"] = {"exit_code": None, "errors": [], "log_tail": "\n".join(job["tail"])[-4000:],
                                 "events_url": None, "stopped_by": job["stop_reason"]}
            job["done"].set()


def _watch(job: dict) -> None:
    """Stop a Live nobody polls any more, or whose events file grows past the limit."""
    f = job["dir"] / "events.jsonl"
    while job["proc"].poll() is None:
        time.sleep(1.0)
        reason = None
        if time.time() - job["touched"] > _TTL:
            reason = "unwatched"
        else:
            try:
                if f.stat().st_size > _MAX_EVENTS_BYTES:
                    reason = "events"
            except OSError:
                pass
        if reason:
            job["stop_reason"] = job["stop_reason"] or reason
            graph_run._terminate(job["proc"], _STOP_GRACE)
            return


def _finish(job: dict) -> None:
    graph_run._terminate(job["proc"], _STOP_GRACE)


def _current(job_id: str):
    """The graph Live whose id is `job_id`, else None. The id is the MJPEG stream's only key (an <img> cannot send
    the session token), so it is compared in constant time, as bytes (compare_digest refuses non-ASCII str)."""
    if not isinstance(job_id, str) or not job_id:
        return None
    with _lock:
        job = _job
    if job is None or not hmac.compare_digest(job["id"].encode(), job_id.encode("utf-8", "replace")):
        return None
    return job


def poll(job_id: str, events_after=0) -> dict:
    """FPS, per-node ms, the events numbered after `events_after`, and once the runner has exited, how it ended."""
    job = _current(job_id)
    if job is None:
        return {"error": "unknown_job", "error_key": "unknown_job"}
    job["touched"] = time.time()
    try:
        after = max(0, int(events_after or 0))
    except (TypeError, ValueError):
        after = 0
    p = dict(job["progress"])
    with _lock:
        result = job["result"]
    out = {"running": result is None, "frames": int(p.get("frames", 0)), "fps": p.get("fps"),
           "avg_fps": p.get("avg_fps"), "node_ms": p.get("node_ms") or {},
           "elapsed": round(time.time() - job["start"], 1), "events": job["events"].since(after),
           **job["events"].snapshot()}
    if result is not None:
        out.update(result)
    return out


def stop(job_id: str) -> dict:
    job = _current(job_id)
    if job is None or job["proc"].poll() is not None:
        return {"status": "no_process"}
    job["stop_reason"] = job["stop_reason"] or "user"
    threading.Thread(target=_finish, args=(job,), daemon=True).start()
    return {"status": "stopping"}


def frame_ok(job_id: str) -> bool:
    """True while `job_id` is the running graph Live (the MJPEG stream's gate)."""
    job = _current(job_id)
    return job is not None and job["proc"].poll() is None


def frame(job_id: str):
    """The current JPEG of the Live display, or None (no such Live, it has ended, or no frame yet)."""
    job = _current(job_id)
    if job is None or job["proc"].poll() is not None:
        return None
    from dx_app.core.camera import capture_live_frame
    return capture_live_frame(SLOT)


def stop_all() -> None:
    """Stop the graph Live before the server exits (atexit, idle watchdog)."""
    with _lock:
        job = _job
    if job is not None and job["proc"].poll() is None:
        job["stop_reason"] = job["stop_reason"] or "server"
        _finish(job)
    if job is not None:
        job["done"].wait(_STOP_GRACE + 2)          # the reader closes the display and records how it ended
    try:
        from dx_app.core import camera
        camera.stop_xvfb(SLOT)
    except Exception:
        pass


atexit.register(stop_all)

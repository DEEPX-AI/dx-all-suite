"""Async batch-inference job registry + progress polling.

The sync `/api/run` path (dx_app.core.inference.run_inference) holds the HTTP connection open
for the whole run, so the Run page shows only a static spinner. This module wraps that SAME
run_inference in a background thread and exposes a job registry the frontend can poll for live
progress — WITHOUT touching the synchronous path (run_inference just gains an optional job_id
that, when set, registers its already-existing stdout log + iteration total here).

Progress is derived by tailing the runner's stdout from a saved cursor (never re-reading the
whole file — avoids O(n^2) on long videos) and counting per-frame task tags ([DET] [SEG] ...),
the same lines live.py already parses. Percentage = frames / total when the total is known
(image loop count, or video frame_count x loop); otherwise the UI shows an indeterminate bar.

Safety: a janitor reaps jobs with no poll/result access for _JOB_TTL seconds — killing a leaked
subprocess if the user closed the tab mid-run — so async runs can't accumulate.
"""
from __future__ import annotations

import threading
import time
import uuid

# Per-frame stdout tag prefixes emitted by the C++/py runners (mirror live._parse_task_tags).
_TAG_PREFIXES = (
    "[DET] ", "[CLS]", "[SEG]", "[ISEG] ", "[DEPTH] ", "[POSE] ",
    "[FACE] ", "[ALIGN] ", "[HAND]", "[OBB] ", "[3D] ",
)

_RUN_JOBS = {}                      # job_id -> job dict
_RUN_JOBS_LOCK = threading.Lock()
_JOB_TTL = 300.0                    # seconds since last touch before a job is reaped/killed


def _count_tags(text):
    n = 0
    for line in text.split("\n"):
        for p in _TAG_PREFIXES:
            if line.startswith(p):
                n += 1
                break
    return n


def _janitor_locked(now):
    """Reap jobs untouched for _JOB_TTL — kill a still-running subprocess if orphaned.
    Caller must hold _RUN_JOBS_LOCK."""
    for jid in [j for j, e in _RUN_JOBS.items() if now - e["touched"] > _JOB_TTL]:
        entry = _RUN_JOBS.pop(jid, None)
        if not entry:
            continue
        proc = entry.get("proc")
        try:
            if proc is not None and proc.poll() is None:
                proc.kill()
        except Exception:
            pass


def register(job_id, log_file, loop, total, proc, start):
    """Called by run_inference (only when a job_id was passed) right after Popen, so poll_run
    can tail the live stdout. No-op if the job was already reaped."""
    with _RUN_JOBS_LOCK:
        entry = _RUN_JOBS.get(job_id)
        if entry is None:
            return
        entry.update({"log_file": log_file, "loop": loop, "total": total,
                      "proc": proc, "start": start, "touched": time.time()})


def start_run(fn, params):
    """Kick off fn(job_id=<id>, **params) in a daemon thread; return a job_id to poll.

    fn must accept a job_id kwarg and, when set, register its run here (via register()) so
    poll_run can report progress — run_inference does this, and run_composer_workflow forwards
    the job_id to its run_inference call. params must NOT contain job_id. Both the Run page
    (run_inference) and the Composer (run_composer_workflow) share this + the poll/result
    routes, so one registry serves every batch run."""
    job_id = uuid.uuid4().hex
    now = time.time()
    with _RUN_JOBS_LOCK:
        _janitor_locked(now)
        _RUN_JOBS[job_id] = {"running": True, "result": None, "log_file": None,
                             "cursor": 0, "frames": 0, "loop": 1, "total": None,
                             "start": now, "proc": None, "touched": now}

    def _worker():
        try:
            res = fn(job_id=job_id, **params)
        except Exception as e:  # defensive — the run fns already trap most failures
            res = {"error": str(e), "error_key": "inference_exception"}
        with _RUN_JOBS_LOCK:
            entry = _RUN_JOBS.get(job_id)
            if entry is not None:
                entry["result"] = res
                entry["running"] = False
                entry["touched"] = time.time()

    threading.Thread(target=_worker, daemon=True, name=f"run-{job_id[:8]}").start()
    return job_id


def poll_run(job_id):
    """Return a progress snapshot: {running, frames, total, pct, elapsed}. Tails only the bytes
    added since the last poll (cursor), counting complete lines to avoid split-line miscounts."""
    with _RUN_JOBS_LOCK:
        entry = _RUN_JOBS.get(job_id)
        if entry is None:
            return {"error": "unknown_job"}
        entry["touched"] = time.time()
        running = entry["running"]
        log = entry["log_file"]
        cursor = entry["cursor"]
        frames = entry["frames"]
        total = entry["total"]
        start = entry["start"]
        has_result = entry["result"] is not None

    if log:
        try:
            with open(log, "rb") as f:
                f.seek(cursor)
                buf = f.read()
        except OSError:
            buf = b""
        if buf:
            nl = buf.rfind(b"\n")
            if nl != -1:  # only consume complete lines; keep the partial tail for next poll
                added = _count_tags(buf[:nl + 1].decode("utf-8", "replace"))
                with _RUN_JOBS_LOCK:
                    e2 = _RUN_JOBS.get(job_id)
                    if e2 is not None and e2["cursor"] == cursor:
                        e2["cursor"] = cursor + nl + 1
                        e2["frames"] += added
                        frames = e2["frames"]
                    elif e2 is not None:
                        frames = e2["frames"]

    pct = None
    if total and total > 0:
        pct = 100 if (not running and has_result) else min(99, int(frames * 100 / total))
    return {"running": running, "frames": frames, "total": total, "pct": pct,
            "elapsed": round(time.time() - start, 1), "has_result": has_result}


def get_run_result(job_id):
    """{running:True} until the run finishes; then the full run_inference result dict, and the
    job is removed from the registry (one-shot)."""
    with _RUN_JOBS_LOCK:
        entry = _RUN_JOBS.get(job_id)
        if entry is None:
            return {"error": "unknown_job"}
        entry["touched"] = time.time()
        if entry["running"] or entry["result"] is None:
            return {"running": True}
        return _RUN_JOBS.pop(job_id)["result"]


def stop_run(job_id):
    """Kill a running job's subprocess (user pressed Stop / navigated away)."""
    with _RUN_JOBS_LOCK:
        entry = _RUN_JOBS.get(job_id)
        if entry is None:
            return {"status": "no_process"}
        entry["touched"] = time.time()
        proc = entry.get("proc")
    try:
        if proc is not None and proc.poll() is None:
            proc.kill()
            return {"status": "stopped"}
    except Exception:
        pass
    return {"status": "no_process"}

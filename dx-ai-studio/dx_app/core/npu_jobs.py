"""Who holds the NPU: one registry, one lock, for every Studio job that loads engines from more than one place.

    graph_run   a graph run once (graph_run.py)
    graph_live  a graph Live (graph_live.py)
    live        the Run page's Live, one holder per display slot (live.py); its slots run side by side

A job calls `acquire(kind, job_id)` before it prepares anything: it gets the NPU, or the kind of the job that holds
it. Once its process is started it calls `attach(job_id, proc)`; from then on the hold ends by itself when the
process exits (finish, stop, crash, timeout or shutdown), so a job that is never released explicitly cannot keep
the NPU. A hold without a process (still preparing) lapses after RESERVE_TTL seconds as a safety net; the callers
release it on every error path. `release(job_id)` ends a hold at once; `release_if_idle(job_id)` only when no live
process is attached (a slot restarted with bad arguments keeps the hold of the runner still on it).
Contract: tests/dx_app/test_npu_jobs.py
"""
from __future__ import annotations

import threading
import time

KINDS = ("graph_run", "graph_live", "live")
SHARED = frozenset({"live"})        # kinds whose holders may run side by side (the Run page's Live slots)
RESERVE_TTL = 120.0

_lock = threading.Lock()
_holders: dict = {}                 # job_id -> {"kind", "since", "proc"}


def _alive(h: dict, now: float) -> bool:
    proc = h["proc"]
    if proc is not None:
        try:
            return proc.poll() is None
        except Exception:
            return False
    return now - h["since"] < RESERVE_TTL


def _prune(now: float) -> None:
    """Drop holds whose process has exited or whose reservation lapsed. Caller holds _lock."""
    for jid in [j for j, h in _holders.items() if not _alive(h, now)]:
        del _holders[jid]


def acquire(kind: str, job_id: str):
    """Take the NPU for `job_id`: None when taken (or already held by `job_id`), else the kind that holds it."""
    if kind not in KINDS:
        raise ValueError(f"unknown NPU job kind {kind!r}")
    now = time.time()
    with _lock:
        _prune(now)
        mine = _holders.get(job_id)
        if mine is not None and mine["kind"] == kind:
            return None
        for jid, h in _holders.items():
            if jid != job_id and not (h["kind"] == kind and kind in SHARED):
                return h["kind"]
        _holders[job_id] = {"kind": kind, "since": now, "proc": None}
        return None


def attach(job_id: str, proc) -> None:
    """The process now running for `job_id`: the hold ends when it exits."""
    with _lock:
        h = _holders.get(job_id)
        if h is not None:
            h["proc"] = proc


def release(job_id: str) -> None:
    with _lock:
        _holders.pop(job_id, None)


def release_if_idle(job_id: str) -> None:
    """Release `job_id` unless a process still running is attached to it."""
    with _lock:
        h = _holders.get(job_id)
        if h is not None and not (h["proc"] is not None and _alive(h, time.time())):
            del _holders[job_id]


def busy():
    """{"kind", "job_id"} of a job holding the NPU (the oldest), or None."""
    with _lock:
        _prune(time.time())
        if not _holders:
            return None
        jid, h = min(_holders.items(), key=lambda kv: kv[1]["since"])
        return {"kind": h["kind"], "job_id": jid}


def held_by(kind: str) -> bool:
    """True while a job of `kind` holds the NPU."""
    with _lock:
        _prune(time.time())
        return any(h["kind"] == kind for h in _holders.values())


def _reset() -> None:
    """Tests only: forget every hold."""
    with _lock:
        _holders.clear()

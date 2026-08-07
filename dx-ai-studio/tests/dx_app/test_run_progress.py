"""Async batch-run job registry (dx_app.core.run_progress).

Covers the lifecycle the Run page depends on — start → poll (live frame count + %) → result
(one-shot) — plus the safety behaviours: unknown-job handling, orphan janitor reaping (kills a
leaked subprocess), and stop. run_inference itself is faked so these run without an NPU.
"""
import tempfile
import time

import pytest

from dx_app.core import run_progress as rp
from dx_app.core import inference as inf


class _FakeProc:
    def __init__(self):
        self.killed = False
        self._alive = True

    def poll(self):
        return None if self._alive else 0

    def kill(self):
        self.killed = True
        self._alive = False


def _install_fake_run(n_frames=8, sleep=0.02, total=None):
    """Patch inference.run_inference with a stand-in that registers a job, emits n_frames
    [DET] tag lines into its log over time, then returns a result dict. Returns the FakeProc
    so a test can assert kill()."""
    proc = _FakeProc()

    def fake_run(job_id=None, **kw):
        log = tempfile.mktemp(suffix=".log")
        open(log, "w").close()
        rp.register(job_id, log, loop=n_frames, total=total if total is not None else n_frames,
                    proc=proc, start=time.time())
        for i in range(n_frames):
            with open(log, "a") as f:
                f.write(f"[DET] cat 0.9{i}\n")
            time.sleep(sleep)
        return {"exit_code": 0, "model": kw.get("model_name"), "ok": True}

    inf.run_inference = fake_run
    return proc


@pytest.fixture(autouse=True)
def _restore_run_inference():
    orig = inf.run_inference
    orig_ttl = rp._JOB_TTL
    yield
    inf.run_inference = orig
    rp._JOB_TTL = orig_ttl
    with rp._RUN_JOBS_LOCK:
        rp._RUN_JOBS.clear()


def _drain(job_id, timeout=5.0):
    """Poll until the job stops running; return the list of poll snapshots."""
    snaps = []
    deadline = time.time() + timeout
    while time.time() < deadline:
        p = rp.poll_run(job_id)
        snaps.append(p)
        if p.get("error") or not p.get("running"):
            break
        time.sleep(0.02)
    return snaps


def test_lifecycle_progress_then_result():
    _install_fake_run(n_frames=8)
    job_id = rp.start_run(inf.run_inference, {"model_name": "m", "category": "c", "model_file": "x.dxnn"})
    snaps = _drain(job_id)

    # frames advanced monotonically and reached the total; pct ended at 100
    frames = [s["frames"] for s in snaps if "frames" in s]
    assert frames == sorted(frames)
    assert max(frames) == 8
    assert snaps[-1]["running"] is False

    result = rp.get_run_result(job_id)
    assert result.get("ok") is True and result.get("model") == "m"
    # one-shot: the job is gone afterwards
    assert rp.get_run_result(job_id) == {"error": "unknown_job"}


def test_percentage_reported_when_total_known():
    _install_fake_run(n_frames=10, total=10)
    job_id = rp.start_run(inf.run_inference, {"model_name": "m", "category": "c", "model_file": "x.dxnn"})
    snaps = _drain(job_id)
    pcts = [s["pct"] for s in snaps if s.get("pct") is not None]
    assert pcts, "expected a real percentage when total is known"
    assert all(0 <= p <= 100 for p in pcts)
    # never reports 100 while still running (reserved for completion)
    for s in snaps:
        if s.get("running") and s.get("pct") is not None:
            assert s["pct"] <= 99


def test_result_says_running_before_completion():
    _install_fake_run(n_frames=6, sleep=0.05)
    job_id = rp.start_run(inf.run_inference, {"model_name": "m", "category": "c", "model_file": "x.dxnn"})
    early = rp.get_run_result(job_id)
    assert early == {"running": True}
    _drain(job_id)
    assert rp.get_run_result(job_id).get("ok") is True


def test_unknown_job_ids_are_safe():
    assert rp.poll_run("nope") == {"error": "unknown_job"}
    assert rp.get_run_result("nope") == {"error": "unknown_job"}
    assert rp.stop_run("nope") == {"status": "no_process"}


def test_stop_kills_running_subprocess():
    proc = _install_fake_run(n_frames=100, sleep=0.05)  # long enough to stop mid-run
    job_id = rp.start_run(inf.run_inference, {"model_name": "m", "category": "c", "model_file": "x.dxnn"})
    time.sleep(0.1)
    assert rp.stop_run(job_id) == {"status": "stopped"}
    assert proc.killed is True


def test_janitor_reaps_and_kills_orphan():
    rp._JOB_TTL = 0.05
    orphan = _FakeProc()
    with rp._RUN_JOBS_LOCK:
        rp._RUN_JOBS["orphan"] = {"running": True, "result": None, "log_file": None,
                                  "cursor": 0, "frames": 0, "loop": 1, "total": None,
                                  "start": time.time() - 100, "proc": orphan,
                                  "touched": time.time() - 100}
    # starting any new run runs the janitor first
    _install_fake_run(n_frames=1)
    new_id = rp.start_run(inf.run_inference, {"model_name": "m", "category": "c", "model_file": "x.dxnn"})
    with rp._RUN_JOBS_LOCK:
        assert "orphan" not in rp._RUN_JOBS
    assert orphan.killed is True
    _drain(new_id)

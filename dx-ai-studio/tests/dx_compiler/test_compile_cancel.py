"""F-10: compile timeout / cancel must actually terminate the worker process.

The old behaviour only formatted an error message on timeout; the running
compile worker (and its child processes) kept running. These tests prove that
both an explicit cancel and the shared termination path used by the timeout
actually kill the *tracked* worker process — targeted by its own process group,
never a broad pkill.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dx_compiler.core import compiler_service as cs_mod
from dx_compiler.core.compiler_service import CompileJob, CompilerService


class _FakeProc:
    """Stand-in for subprocess.Popen with a real integer pid."""

    def __init__(self, pid=424242):
        self.pid = pid
        self.returncode = None
        self.terminated = False
        self.killed = False
        self.waited = False

    def poll(self):
        # Still running until terminated.
        return None if not self.terminated else 0

    def wait(self, timeout=None):
        self.waited = True
        self.returncode = 0
        return 0

    def terminate(self):
        self.terminated = True

    def kill(self):
        self.killed = True


def _make_service_with_running_job(monkeypatch, job_id="job1"):
    svc = CompilerService()
    job = CompileJob(job_id=job_id)
    job.mark_running()
    proc = _FakeProc()
    job.process = proc
    svc.jobs[job_id] = job

    killpg_calls = []
    monkeypatch.setattr(
        cs_mod.os, "killpg",
        lambda pgid, sig: killpg_calls.append((pgid, sig)),
    )
    monkeypatch.setattr(cs_mod.os, "getpgid", lambda pid: pid)
    return svc, job, proc, killpg_calls


def test_cancel_terminates_tracked_worker(monkeypatch):
    svc, job, proc, killpg_calls = _make_service_with_running_job(monkeypatch)

    result = svc.cancel("job1")

    assert result is True
    assert job.status == "error"
    # The kill must target the tracked worker's process group (pgid == pid here),
    # proving termination is targeted rather than a broad pkill.
    assert killpg_calls, "expected the tracked worker's process group to be signalled"
    assert killpg_calls[0][0] == proc.pid


def test_cancel_unknown_job_returns_false(monkeypatch):
    svc = CompilerService()
    assert svc.cancel("nope") is False


def test_terminate_job_kills_and_marks_error(monkeypatch):
    """This is the shared path invoked by the SSE timeout branch."""
    svc, job, proc, killpg_calls = _make_service_with_running_job(monkeypatch)

    svc.terminate_job(job, "Compile timed out after 5 seconds.")

    assert job.status == "error"
    assert "timed out" in (job.error or "")
    assert killpg_calls and killpg_calls[0][0] == proc.pid


def test_subprocess_run_tracks_worker_process(monkeypatch, tmp_path):
    """_run_compile_subprocess must store the Popen handle on job.process
    (so cancel/timeout can target it) and start it in its own session/group."""
    svc = CompilerService()
    job = CompileJob(job_id="jsub", output_dir=str(tmp_path))

    seen = {}

    class _FakeStdin:
        def write(self, s):
            pass

        def close(self):
            pass

    class _FakeStdout:
        def __init__(self):
            self._lines = iter(['{"type": "done"}\n'])

        def __iter__(self):
            return self

        def __next__(self):
            seen["process_during"] = job.process
            return next(self._lines)

    class _FakePopenProc:
        def __init__(self):
            self.stdin = _FakeStdin()
            self.stdout = _FakeStdout()
            self.returncode = 0
            self.pid = 4321

        def wait(self):
            return 0

    popen_kwargs = {}

    def fake_popen(cmd, **kwargs):
        popen_kwargs.update(kwargs)
        return _FakePopenProc()

    monkeypatch.setattr(cs_mod.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(svc, "_store_qxnn_artifact", lambda job: None)
    monkeypatch.setattr(svc, "_store_diagnosis_report", lambda job: None)

    svc._run_compile_subprocess(
        job, "/venv/py", "m.onnx", "c.json", str(tmp_path),
        1, False, False, False, False, None, False,
    )

    # Own session/group => os.killpg can target only this worker + its children.
    assert popen_kwargs.get("start_new_session") is True
    # Tracked while running, reset afterwards.
    assert seen.get("process_during") is not None
    assert job.process is None

"""Regression tests for compiler job-owned staging artifacts."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run_compile_args(output_dir: Path) -> tuple:
    return (
        str(output_dir),
        1,
        False,
        False,
        False,
        False,
        None,
        None,
        None,
        False,
    )


def _new_job(service, requested_output_dir: Path, *, mode: str = "compile"):
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(
        job_id=str(uuid.uuid4()),
        output_dir=str(requested_output_dir),
        requested_output_dir=str(requested_output_dir),
        mode=mode,
    )
    service._prepare_job_staging(job)
    return job


def test_direct_compile_finalizes_canonical_work_artifact_and_requested_copy(
    monkeypatch, tmp_path
):
    from dx_compiler.core import compiler_bridge
    from dx_compiler.core import setup_service as setup_module
    from dx_compiler.core.compiler_service import CompilerService

    requested = tmp_path / "requested"
    service = CompilerService(job_root=tmp_path / "jobs")
    job = _new_job(service, requested)
    seen = {}

    def fake_run_compile(**kwargs):
        seen["output_dir"] = kwargs["output_dir"]
        output = Path(kwargs["output_dir"])
        output.mkdir(parents=True, exist_ok=True)
        (output / "model.dxnn").write_bytes(b"direct bytes")

    monkeypatch.setattr(setup_module.setup_service, "get_venv_python", lambda: None)
    monkeypatch.setattr(service, "_is_dx_com_available", lambda: True)
    monkeypatch.setattr(compiler_bridge, "run_compile", fake_run_compile)

    service._run_compile(job, "model.onnx", "config.json", *_run_compile_args(requested))

    canonical = Path(job.canonical_dxnn_path)
    assert seen["output_dir"] == job.work_dir
    assert canonical == Path(job.work_dir) / "model.dxnn"
    assert canonical.read_bytes() == b"direct bytes"
    assert (requested / "model.dxnn").read_bytes() == b"direct bytes"
    assert job.dxnn_path == job.canonical_dxnn_path
    assert job.artifact_ready is True
    assert job.completed_at is not None
    assert job.status == "done"


def test_overlapping_direct_compiles_isolate_logs_and_restore_global_streams(
    monkeypatch, tmp_path
):
    """Direct jobs must not overlap while they own process-global streams."""
    from dx_compiler.core import compiler_bridge
    from dx_compiler.core import setup_service as setup_module
    from dx_compiler.core.compiler_service import CompilerService

    service = CompilerService(job_root=tmp_path / "jobs")
    first = _new_job(service, tmp_path / "first-requested")
    second = _new_job(service, tmp_path / "second-requested")
    original_stdout, original_stderr = sys.stdout, sys.stderr
    compile_barrier = threading.Barrier(2, timeout=0.25)
    first_entered_compiler = threading.Event()
    concurrent_output = {
        "first": threading.Event(),
        "second": threading.Event(),
    }
    release_concurrent_compiler = {
        "first": threading.Event(),
        "second": threading.Event(),
    }

    def fake_run_compile(**kwargs):
        label = Path(kwargs["model"]).stem
        if label == "first":
            first_entered_compiler.set()
        try:
            compile_barrier.wait()
        except threading.BrokenBarrierError:
            overlapped = False
        else:
            overlapped = True

        sys.stdout.write(f"{label}-stdout\n")
        sys.stderr.write(f"{label}-stderr\n")
        (Path(kwargs["output_dir"]) / f"{label}.dxnn").write_bytes(label.encode())

        if overlapped:
            concurrent_output[label].set()
            assert release_concurrent_compiler[label].wait(timeout=2)

    monkeypatch.setattr(setup_module.setup_service, "get_venv_python", lambda: None)
    monkeypatch.setattr(service, "_is_dx_com_available", lambda: True)
    monkeypatch.setattr(compiler_bridge, "run_compile", fake_run_compile)

    args = _run_compile_args(tmp_path / "unused-requested-path")
    first_thread = threading.Thread(
        target=service._run_compile,
        args=(first, "first.onnx", "config.json", *args),
    )
    second_thread = threading.Thread(
        target=service._run_compile,
        args=(second, "second.onnx", "config.json", *args),
    )

    first_thread.start()
    assert first_entered_compiler.wait(timeout=1)
    second_thread.start()

    if concurrent_output["first"].wait(timeout=1):
        assert concurrent_output["second"].wait(timeout=1)
        release_concurrent_compiler["first"].set()
        first_thread.join(timeout=2)
        release_concurrent_compiler["second"].set()

    first_thread.join(timeout=2)
    second_thread.join(timeout=2)

    assert not first_thread.is_alive()
    assert not second_thread.is_alive()
    assert sys.stdout is original_stdout
    assert sys.stderr is original_stderr
    assert first.log_buffer.get_new_lines(0) == ["first-stdout", "first-stderr"]
    assert second.log_buffer.get_new_lines(0) == ["second-stdout", "second-stderr"]


def test_worker_compile_finalizes_only_after_worker_success(monkeypatch, tmp_path):
    from dx_compiler.core import compiler_service as service_module
    from dx_compiler.core.compiler_service import CompilerService

    requested = tmp_path / "requested"
    service = CompilerService(job_root=tmp_path / "jobs")
    job = _new_job(service, requested)
    seen = {}

    class FakeStdin:
        def write(self, payload):
            seen["params"] = json.loads(payload)

        def close(self):
            return None

    class FakeProc:
        def __init__(self):
            self.stdin = FakeStdin()
            self.stdout = iter(['{"type": "done"}\n'])
            self.returncode = 0
            self.pid = 12

        def wait(self):
            Path(seen["params"]["output_dir"]).mkdir(parents=True, exist_ok=True)
            (Path(seen["params"]["output_dir"]) / "worker.dxnn").write_bytes(
                b"worker bytes"
            )
            return 0

    monkeypatch.setattr(service_module.subprocess, "Popen", lambda *args, **kwargs: FakeProc())

    service._run_compile_subprocess(
        job,
        "/venv/python",
        "worker.onnx",
        "config.json",
        str(requested),
        1,
        False,
        False,
        False,
        False,
        None,
        False,
    )

    assert seen["params"]["output_dir"] == job.work_dir
    assert Path(job.canonical_dxnn_path).read_bytes() == b"worker bytes"
    assert (requested / "worker.dxnn").read_bytes() == b"worker bytes"
    assert job.artifact_ready is True
    assert job.status == "done"


def test_resume_compile_finalizes_canonical_work_artifact(monkeypatch, tmp_path):
    from dx_compiler.core import compiler_service as service_module
    from dx_compiler.core import setup_service as setup_module
    from dx_compiler.core.compiler_service import CompilerService

    requested = tmp_path / "requested"
    service = CompilerService(job_root=tmp_path / "jobs")
    job = _new_job(service, requested, mode="resume")
    seen = {}

    class FakeStdout:
        def read(self, _size):
            return ""

    class FakeProc:
        def __init__(self, env):
            self.stdout = FakeStdout()
            self.env = env
            self.pid = 13

        def wait(self):
            args = json.loads(self.env["DX_COMPILER_RESUME_ARGS"])
            seen["output_dir"] = args["output_dir"]
            output = Path(args["output_dir"])
            output.mkdir(parents=True, exist_ok=True)
            (output / "resume.dxnn").write_bytes(b"resume bytes")
            return 0

    monkeypatch.setattr(
        service_module.subprocess,
        "Popen",
        lambda _cmd, **kwargs: FakeProc(kwargs["env"]),
    )
    monkeypatch.setattr(
        setup_module.setup_service,
        "get_venv_python",
        lambda: None,
    )

    service._run_resume(
        job,
        "checkpoint.qxnn",
        str(requested),
        None,
        None,
        False,
        None,
    )

    assert seen["output_dir"] == job.work_dir
    assert Path(job.canonical_dxnn_path).read_bytes() == b"resume bytes"
    assert (requested / "resume.dxnn").read_bytes() == b"resume bytes"
    assert job.artifact_ready is True
    assert job.status == "done"


@pytest.mark.parametrize(
    "artifacts, expected",
    [
        ([], "missing"),
        ([("one.dxnn", b"one"), ("two.dxnn", b"two")], "ambiguous"),
    ],
)
def test_finalization_rejects_missing_or_ambiguous_dxnn(tmp_path, artifacts, expected):
    from dx_compiler.core.compiler_service import CompilerService

    requested = tmp_path / "requested"
    service = CompilerService(job_root=tmp_path / "jobs")
    job = _new_job(service, requested)
    for filename, contents in artifacts:
        (Path(job.work_dir) / filename).write_bytes(contents)

    assert service._finalize_success(job) is False
    assert job.status == "error"
    assert expected in (job.error or "").lower()
    assert job.artifact_ready is False


def test_finalization_marks_publish_failure_as_error(monkeypatch, tmp_path):
    from dx_compiler.core import compiler_service as service_module
    from dx_compiler.core.compiler_service import CompilerService

    requested = tmp_path / "requested"
    service = CompilerService(job_root=tmp_path / "jobs")
    job = _new_job(service, requested)
    (Path(job.work_dir) / "model.dxnn").write_bytes(b"canonical")

    def fail_replace(_source, _target):
        raise OSError("disk full")

    monkeypatch.setattr(service_module.os, "replace", fail_replace)

    assert service._finalize_success(job) is False
    assert job.status == "error"
    assert "publish" in (job.error or "").lower()
    assert job.artifact_ready is False


def test_shared_requested_path_and_forced_equal_mtime_keep_individual_downloads(
    monkeypatch, tmp_path
):
    from dx_compiler.core import compiler_bridge
    from dx_compiler.core import setup_service as setup_module
    from dx_compiler.core.compiler_service import CompilerService
    import dx_compiler.server as server_mod

    requested = tmp_path / "requested"
    service = CompilerService(job_root=tmp_path / "jobs")
    first = _new_job(service, requested)
    second = _new_job(service, requested)

    # A fixed, fresh (future) timestamp shared by both artifacts → equal mtime that
    # still clears the freshness gate for both jobs.
    _EQ_MTIME_NS = int((time.time() + 60) * 1_000_000_000)

    def fake_run_compile(**kwargs):
        payload = (
            b"first-0000"
            if Path(kwargs["model"]).stem == "first"
            else b"second-000"
        )
        artifact = Path(kwargs["output_dir"]) / "shared.dxnn"
        artifact.write_bytes(payload)
        # Force BOTH jobs' artifacts to an identical mtime so the tie-break path is
        # exercised. It must be recent (>= job.start_time) or the _final_dxnn_candidates
        # freshness gate — which rejects stale leftover .dxnn files — would drop it as
        # if the compile produced nothing.
        os.utime(artifact, ns=(_EQ_MTIME_NS, _EQ_MTIME_NS))

    monkeypatch.setattr(setup_module.setup_service, "get_venv_python", lambda: None)
    monkeypatch.setattr(service, "_is_dx_com_available", lambda: True)
    monkeypatch.setattr(compiler_bridge, "run_compile", fake_run_compile)

    service._run_compile(first, "first.onnx", "config.json", *_run_compile_args(requested))
    service._run_compile(second, "second.onnx", "config.json", *_run_compile_args(requested))
    service.jobs.update({first.job_id: first, second.job_id: second})

    def download(job_id):
        captured = {}
        handler = server_mod.CompilerHandler.__new__(server_mod.CompilerHandler)
        handler.send_error_json = lambda code, message: captured.update(error=(code, message))
        handler.send_bytes = lambda body, content_type, filename=None: captured.update(
            body=body, content_type=content_type, filename=filename
        )
        monkeypatch.setattr(server_mod, "compiler_service", service)
        handler._compile_dxnn(job_id)
        return captured["body"]

    assert len(b"first-0000") == len(b"second-000")
    assert (requested / "shared.dxnn").read_bytes() == b"second-000"
    assert download(first.job_id) == b"first-0000"
    assert download(second.job_id) == b"second-000"


def test_sse_complete_requires_artifact_ready(monkeypatch, tmp_path):
    import dx_compiler.server as server_mod
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id=str(uuid.uuid4()), status="done", output_dir=str(tmp_path))

    class FakeCompilerService:
        def get_job(self, job_id):
            assert job_id == job.job_id
            return job

    events = []
    handler = server_mod.CompilerHandler.__new__(server_mod.CompilerHandler)
    handler.start_sse = lambda: None
    handler.end_sse = lambda: None
    handler.send_sse = lambda event, data: events.append((event, data)) or True
    monkeypatch.setattr(server_mod, "compiler_service", FakeCompilerService())

    handler._sse_progress(job.job_id)

    assert [event for event, _payload in events] == ["error"]
    assert "artifact" in (events[0][1]["error"] or "").lower()


def test_sse_complete_exposes_download_url_not_staging_path(monkeypatch, tmp_path):
    import dx_compiler.server as server_mod
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id=str(uuid.uuid4()), status="done", output_dir=str(tmp_path))
    job.artifact_ready = True
    job.canonical_dxnn_path = str(tmp_path / "jobs" / job.job_id / "work" / "model.dxnn")
    job.dxnn_path = job.canonical_dxnn_path

    class FakeCompilerService:
        def get_job(self, job_id):
            assert job_id == job.job_id
            return job

    events = []
    handler = server_mod.CompilerHandler.__new__(server_mod.CompilerHandler)
    handler.start_sse = lambda: None
    handler.end_sse = lambda: None
    handler.send_sse = lambda event, data: events.append((event, data)) or True
    monkeypatch.setattr(server_mod, "compiler_service", FakeCompilerService())

    handler._sse_progress(job.job_id)

    complete = next(payload for event, payload in events if event == "complete")
    assert complete["dxnn_path"] == "model.dxnn"
    assert complete["dxnn_download_url"] == f"/compile/{job.job_id}/dxnn"
    assert job.canonical_dxnn_path not in complete.values()


def test_download_rejects_artifact_outside_its_job_root(monkeypatch, tmp_path):
    from dx_compiler.core.compiler_service import CompilerService
    import dx_compiler.server as server_mod

    service = CompilerService(job_root=tmp_path / "jobs")
    job = _new_job(service, tmp_path / "requested")
    external = tmp_path / "external.dxnn"
    external.write_bytes(b"not canonical")
    job.status = "done"
    job.artifact_ready = True
    job.canonical_dxnn_path = str(external)
    job.dxnn_path = str(external)
    service.jobs[job.job_id] = job

    captured = {}
    handler = server_mod.CompilerHandler.__new__(server_mod.CompilerHandler)
    handler.send_error_json = lambda code, message: captured.update(error=(code, message))
    handler.send_bytes = lambda *args, **kwargs: captured.update(body=True)
    monkeypatch.setattr(server_mod, "compiler_service", service)

    handler._compile_dxnn(job.job_id)

    assert captured["error"][0] == 404
    assert "body" not in captured


def test_cleanup_removes_only_completed_job_roots_and_memory_records(tmp_path):
    from dx_compiler.core.compiler_service import CompilerService

    requested = tmp_path / "requested"
    requested.mkdir()
    service = CompilerService(job_root=tmp_path / "jobs")
    old = _new_job(service, requested)
    fresh = _new_job(service, requested)
    active = _new_job(service, requested)
    old.completed_at = 10.0
    fresh.completed_at = 100.0
    service._write_completion_marker(old)
    service._write_completion_marker(fresh)
    service.jobs = {old.job_id: old, fresh.job_id: fresh, active.job_id: active}

    removed = service.cleanup_completed_jobs(now=200.0, ttl_seconds=150.0, max_count=10)

    assert removed == [old.job_id]
    assert not (tmp_path / "jobs" / old.job_id).exists()
    assert (tmp_path / "jobs" / fresh.job_id).exists()
    assert (tmp_path / "jobs" / active.job_id).exists()
    assert requested.exists()
    assert old.job_id not in service.jobs
    assert fresh.job_id in service.jobs
    assert active.job_id in service.jobs

    newest = _new_job(service, requested)
    newest.completed_at = 150.0
    service._write_completion_marker(newest)
    service.jobs[newest.job_id] = newest
    removed = service.cleanup_completed_jobs(now=200.0, ttl_seconds=1_000.0, max_count=1)

    assert removed == [fresh.job_id]
    assert not (tmp_path / "jobs" / fresh.job_id).exists()
    assert (tmp_path / "jobs" / newest.job_id).exists()
    assert requested.exists()

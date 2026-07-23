"""Process-lifecycle cleanup tests (F-13 / F-14).

F-13/14a: on server shutdown and on watchdog restart, dx_app must terminate
          live-mode child processes (Xvfb, ffmpeg cam-mux, live inference) so
          they do not linger as orphans.
F-14b:    run_multi shares process handles across concurrent worker threads;
          access must be guarded (lock/snapshot) so a concurrent stop terminates
          every in-flight child, not just the last one written to the shared slot.
"""
import threading
import time

import pytest


class _FakeProc:
    """Minimal Popen stand-in with observable terminate/kill/poll."""

    def __init__(self, alive=True):
        self.returncode = 0
        self.terminated = False
        self.killed = False
        self._alive = alive

    def poll(self):
        return None if self._alive else 0

    def terminate(self):
        self.terminated = True
        self._alive = False

    def kill(self):
        self.killed = True
        self._alive = False

    def wait(self, timeout=None):
        self._alive = False
        return 0


def _reset_state(inference):
    import camera

    inference._live_procs.clear()
    inference._xvfb_procs.clear()
    # _cam_mux_proc is owned by dx_app.core.camera (P2-2-A inference.py split) —
    # it is a plain rebound scalar (not a dict/lock), so poking it via the
    # `inference` re-export name would only shadow a local attribute on the
    # `inference` module and never reach the real state camera.py's functions
    # read/write. Must go through the owning module directly.
    camera._cam_mux_proc = None
    with inference.config._proc_lock:
        inference.config._running_proc = None



def test_shutdown_terminates_live_xvfb_and_ffmpeg(monkeypatch):
    import inference
    import camera

    _reset_state(inference)
    monkeypatch.setattr(inference, "os", inference.os)  # keep os intact

    live0, live1 = _FakeProc(), _FakeProc()
    xvfb0 = _FakeProc()
    cam = _FakeProc()

    inference._live_procs[0] = live0
    inference._live_procs[1] = live1
    inference._xvfb_procs[0] = xvfb0
    camera._cam_mux_proc = cam

    assert hasattr(inference, "shutdown_live_processes"), \
        "inference must expose shutdown_live_processes() for shutdown/watchdog cleanup"

    inference.shutdown_live_processes()

    assert live0.terminated and live1.terminated, "live inference children not terminated"
    assert xvfb0.terminated, "Xvfb child not terminated"
    assert cam.terminated, "ffmpeg cam-mux child not terminated"
    # cam-mux handle must be cleared so a later start does not double-handle it
    assert camera._cam_mux_proc is None

    _reset_state(inference)


def test_shutdown_is_idempotent_on_empty_state(monkeypatch):
    import inference

    _reset_state(inference)
    # Must not raise even with no live children present.
    inference.shutdown_live_processes()
    _reset_state(inference)



def test_watchdog_triggers_live_process_cleanup(monkeypatch):
    import server
    import config

    calls = {"cleanup": 0, "stop": 0}

    monkeypatch.setattr(server, "stop_inference",
                        lambda: calls.__setitem__("stop", calls["stop"] + 1))
    assert hasattr(server, "shutdown_live_processes"), \
        "server must import shutdown_live_processes for watchdog cleanup"
    monkeypatch.setattr(server, "shutdown_live_processes",
                        lambda: calls.__setitem__("cleanup", calls["cleanup"] + 1))
    # Avoid the real 5s poll delay.
    monkeypatch.setattr(server.time, "sleep", lambda _s: None)

    # Force the heartbeat-timeout branch on the first iteration.
    config._HEARTBEAT = time.time() - 10_000

    class _Srv:
        def __init__(self):
            self.shutdown_called = False

        def shutdown(self):
            self.shutdown_called = True

    srv = _Srv()
    # Guard against an accidental infinite loop.
    monkeypatch.setattr(server, "_HB_TIMEOUT", 1)

    t = threading.Thread(target=server._watchdog, args=(srv,))
    t.start()
    t.join(timeout=5)

    assert not t.is_alive(), "watchdog did not exit"
    assert srv.shutdown_called
    assert calls["cleanup"] >= 1, "watchdog must call shutdown_live_processes()"



def test_multi_process_handles_are_guarded_by_lock():
    import inference

    assert hasattr(inference, "_multi_procs_lock"), "run_multi handles need a lock"
    lock = inference._multi_procs_lock
    assert lock.acquire(timeout=1)
    lock.release()
    assert hasattr(inference, "stop_multi"), "expose stop_multi() to stop the snapshot"


def test_run_multi_tracks_all_concurrent_handles(tmp_path, monkeypatch):
    """A concurrent stop must terminate EVERY in-flight child, not just the last
    one written to the shared config._running_proc slot."""
    import inference

    _reset_state(inference)
    if hasattr(inference, "_multi_procs"):
        with inference._multi_procs_lock:
            inference._multi_procs.clear()

    # ── minimal runtime so run_inference reaches Popen for an image run ──
    app_root = tmp_path / "app"
    build = app_root / "build"
    outp = app_root / "outputs"
    for p in (build, outp):
        p.mkdir(parents=True, exist_ok=True)
    (app_root / "model.dxnn").write_bytes(b"m")
    (app_root / "input.jpg").write_bytes(b"i")
    binary = build / "demo_sync"
    binary.write_text("#!/bin/sh\n")
    binary.chmod(0o755)

    monkeypatch.setattr(inference, "DX_APP_ROOT", app_root)
    monkeypatch.setattr(inference, "BUILD_DIR", build)
    monkeypatch.setattr(inference, "OUTPUTS_DIR", outp)
    monkeypatch.setattr(inference, "get_hw", lambda: {})
    monkeypatch.setattr(inference, "_parse_perf", lambda s: {"overall_fps": "30"})

    n = 3
    release = threading.Event()
    spawned = []
    spawned_lock = threading.Lock()

    class BlockingProc:
        def __init__(self, cmd, stdout=None, **kw):
            self.returncode = 0
            self.terminated = False
            self.killed = False
            self.cmd = cmd
            self._alive = True
            # Only the real inference launch blocks; incidental probes
            # (e.g. ldconfig via subprocess.run) return immediately.
            self._is_inference = bool(cmd) and str(cmd[0]).endswith("demo_sync")
            if self._is_inference:
                with spawned_lock:
                    spawned.append(self)

        def poll(self):
            return None if (self._is_inference and self._alive) else 0

        def terminate(self):
            self.terminated = True
            self._alive = False
            release.set()  # let the blocked wait() return

        def kill(self):
            self.killed = True
            self._alive = False
            release.set()

        def communicate(self, *a, **k):
            return ("", "")

        def wait(self, timeout=None):
            if not self._is_inference:
                return 0
            # Block until a stop terminates us (bounded to keep the test safe).
            release.wait(timeout=5)
            return 0

    monkeypatch.setattr(inference.subprocess, "Popen", BlockingProc)

    reqs = [
        {"model_name": "demo", "category": "object_detection",
         "model_file": "model.dxnn", "input_type": "image",
         "image_path": "input.jpg", "timeout": 10}
        for _ in range(n)
    ]

    result_holder = {}
    runner = threading.Thread(
        target=lambda: result_holder.setdefault("res", inference.run_multi(reqs)))
    runner.start()

    # Wait until all n children are registered in the guarded snapshot.
    deadline = time.time() + 5
    while time.time() < deadline:
        with inference._multi_procs_lock:
            if len(inference._multi_procs) >= n:
                break
        time.sleep(0.02)

    with inference._multi_procs_lock:
        tracked = len(inference._multi_procs)
    assert tracked == n, f"run_multi tracked {tracked} handles, expected {n}"

    # Concurrent stop must terminate the full snapshot.
    inference.stop_multi()
    runner.join(timeout=5)
    assert not runner.is_alive()

    assert len(spawned) == n
    assert all(p.terminated for p in spawned), \
        "stop_multi did not terminate every in-flight child (handle race)"

    _reset_state(inference)
    with inference._multi_procs_lock:
        inference._multi_procs.clear()

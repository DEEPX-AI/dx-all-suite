"""Module stderr is kept.

When a module server exits and the launcher brings it back, the reason must be recorded. stderr (tracebacks,
warnings, and the faulthandler dump of a native crash) goes to a size-capped log per module, and the watchdog
records the exit code.
"""
from __future__ import annotations

import io
import os
from unittest.mock import MagicMock

import launcher.launcher as lmod


def test_module_log_path_is_under_the_state_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    assert lmod._module_log_path("dx_app") == tmp_path / "dx-ai-studio" / "logs" / "dx_app.log"


def test_pump_writes_stderr_and_rotates_at_the_cap(tmp_path):
    log = tmp_path / "logs" / "m.log"
    lines = [f"line {i:04d} ".encode() + b"x" * 80 + b"\n" for i in range(60)]
    lmod._pump_module_stderr(io.BytesIO(b"".join(lines)), log, cap_bytes=2000)
    assert log.exists() and log.stat().st_size <= 2000 + 200
    assert (tmp_path / "logs" / "m.log.1").exists()
    assert b"line 0059" in log.read_bytes()


def test_spawn_keeps_stderr_and_enables_faulthandler(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    seen = {}

    def fake_popen(cmd, **kw):
        seen.update(kw)
        p = MagicMock(pid=4242)
        p.stderr = io.BytesIO(b"Traceback: boom\n")
        return p

    monkeypatch.setattr(lmod.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(lmod, "_await_reported_port", lambda pf, timeout=20: 50123)
    monkeypatch.setattr(lmod, "_save_pids", lambda: None)
    srv = tmp_path / "mod"
    srv.mkdir()
    (srv / "server.py").write_text("")
    assert lmod.start_sub_server("dx_test", srv, server_id="dx_test")
    assert seen["stderr"] == lmod.subprocess.PIPE
    assert seen["stdout"] == lmod.subprocess.DEVNULL
    assert seen["env"]["PYTHONFAULTHANDLER"] == "1"
    lmod._module_log_threads["dx_test"].join(2)
    assert b"Traceback: boom" in (tmp_path / "dx-ai-studio" / "logs" / "dx_test.log").read_bytes()
    lmod._LAUNCHER_PROXY_PORTS.pop("dx_test", None)
    lmod._procs.pop("dx_test", None)


def test_watchdog_records_the_exit_code_and_log(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    proc = MagicMock(pid=777, returncode=-11)
    proc.poll.return_value = -11
    lmod._register_module("dx_logtest", port=59871, cwd="/fake", proc=proc)
    lmod._watchdog_check_once()
    err = lmod._watchdog_registry["dx_logtest"]["last_error"]
    assert "code -11" in err and "SIGSEGV" in err and "dx_logtest.log" in err

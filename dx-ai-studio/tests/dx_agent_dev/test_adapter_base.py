"""SubprocessAdapter shared behavior: command building, cwd choice, normalize fallback, cancel."""
import signal
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_agent_adapter_is_abstract():
    from core.adapters.base import AgentAdapter
    with pytest.raises(TypeError):
        AgentAdapter()


def test_subprocess_adapter_requires_build_command():
    """A subclass without build_command raises NotImplementedError on run."""
    from core.adapters.base import SubprocessAdapter

    class Bare(SubprocessAdapter):
        cli_bin = "x"

    a = Bare(cli_path="/bin/true")
    with pytest.raises(NotImplementedError):
        a.build_command("p", Path("/tmp"), [])


def test_default_normalize_text_heuristic():
    from core.adapters.base import SubprocessAdapter

    class Bare(SubprocessAdapter):
        cli_bin = "x"

    a = Bare(cli_path="/bin/true")
    assert a.normalize("$ ls")["type"] == "command"
    assert a.normalize("+ build")["type"] == "command"
    assert a.normalize("hello")["type"] == "message"


def test_cwd_mode_session_default(tmp_path):
    from core.adapters.base import SubprocessAdapter

    class Bare(SubprocessAdapter):
        cli_bin = "x"

    a = Bare(cli_path="/bin/true")
    assert a._resolve_cwd(tmp_path, []) == tmp_path
    assert a._resolve_cwd(tmp_path, ["/harness"]) == tmp_path  # session mode


def test_cwd_mode_harness(tmp_path):
    from core.adapters.base import SubprocessAdapter

    class HarnessTool(SubprocessAdapter):
        cli_bin = "x"
        cwd_mode = "harness"

    a = HarnessTool(cli_path="/bin/true")
    assert a._resolve_cwd(tmp_path, ["/harness"]) == "/harness"
    assert a._resolve_cwd(tmp_path, []) == tmp_path  # no harness: falls back to the session


def test_is_available_resolves_cli_bin(monkeypatch):
    from core.adapters import base

    class Bare(base.SubprocessAdapter):
        cli_bin = "mytool"

    monkeypatch.setattr(base.shutil, "which", lambda n: "/usr/bin/mytool" if n == "mytool" else None)
    assert Bare().is_available() is True

    monkeypatch.setattr(base.shutil, "which", lambda n: None)
    assert Bare().is_available() is False


def test_run_launch_failure_emits_error(tmp_path):
    """A missing binary yields a "launch failed" error event."""
    from core.adapters.base import SubprocessAdapter

    class Echo(SubprocessAdapter):
        cli_bin = "x"

        def build_command(self, prompt, session_dir, harness_dirs, run_ctx=None):
            return ["/nonexistent/binary/xyz", prompt]

    a = Echo(cli_path="/nonexistent/binary/xyz")
    events = list(a.run("hi", tmp_path, []))
    assert events[0]["type"] == "error"
    assert "launch failed" in events[0]["text"]


def test_run_success_with_echo_emits_done(tmp_path):
    """Happy path with a real subprocess (echo): stdout lines are normalized, then done."""
    from core.adapters.base import SubprocessAdapter

    class Echo(SubprocessAdapter):
        cli_bin = "echo"

        def build_command(self, prompt, session_dir, harness_dirs, run_ctx=None):
            return ["/bin/echo", "hello from agent"]

    a = Echo(cli_path="/bin/echo")
    events = list(a.run("hi", tmp_path, []))
    assert events[-1]["type"] == "done"
    assert any(e["type"] == "message" and "hello from agent" in e["text"] for e in events)


def test_cancel_kills_process_group(monkeypatch):
    from core.adapters import base
    sent = {}
    monkeypatch.setattr(base.os, "getpgid", lambda pid: pid)
    monkeypatch.setattr(base.os, "killpg", lambda pgid, sig: sent.setdefault("sig", sig))

    class FakeProc:
        pid = 4321
        def poll(self): return None
        def wait(self, timeout=None): return 0

    class Bare(base.SubprocessAdapter):
        cli_bin = "x"

    a = Bare(cli_path="/bin/true")
    a._proc = FakeProc()
    a.cancel()
    assert sent.get("sig") == signal.SIGTERM

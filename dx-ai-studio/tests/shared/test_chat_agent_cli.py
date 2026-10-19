"""CLI-backed chat provider ("agent-cli"): chat through a logged-in coding-agent CLI.

One claude login covers both the chatbot and dx_agent_dev (no separate API key).
provider="agent-cli", model=<agent name> (claude/opencode/…).
"""
from unittest.mock import patch

import pytest

from shared.chat import providers
from shared.chat.providers import stream_chat, stream_agent_cli, ChatAPIError, _flatten_prompt


class _FakeProc:
    """Stand-in for subprocess.Popen used by stream_agent_cli's Popen+communicate path."""

    def __init__(self, cmd, stdout="", returncode=0, stderr=""):
        self.cmd = cmd
        self.returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    def communicate(self):
        return self._stdout, self._stderr

    def kill(self):
        pass


def _fake_popen(stdout="hello from agent", returncode=0, stderr=""):
    def popen(cmd, **kwargs):
        return _FakeProc(cmd, stdout=stdout, returncode=returncode, stderr=stderr)
    return popen


def test_flatten_prompt_joins_roles():
    msgs = [
        {"role": "system", "content": "You are X."},
        {"role": "user", "content": "hi"},
    ]
    out = _flatten_prompt(msgs)
    assert "You are X." in out and "hi" in out


def test_agent_cli_yields_stdout():
    with patch.object(providers.shutil, "which", lambda b: "/usr/bin/" + b), \
         patch.object(providers.subprocess, "Popen", _fake_popen("ANSWER")):
        out = list(stream_agent_cli("claude", None, [{"role": "user", "content": "q"}]))
    assert out == ["ANSWER"]


def test_agent_cli_builds_claude_command():
    captured = {}

    def popen(cmd, **kwargs):
        captured["cmd"] = cmd
        return _FakeProc(cmd, stdout="ok", returncode=0, stderr="")

    with patch.object(providers.shutil, "which", lambda b: "/usr/bin/" + b), \
         patch.object(providers.subprocess, "Popen", popen):
        list(stream_agent_cli("claude", None, [{"role": "user", "content": "q"}]))
    assert captured["cmd"][0] == "/usr/bin/claude"
    assert "-p" in captured["cmd"]


def test_agent_cli_unknown_agent_raises():
    with pytest.raises(ChatAPIError):
        list(stream_agent_cli("nope", None, [{"role": "user", "content": "q"}]))


def test_agent_cli_missing_binary_raises():
    with patch.object(providers.shutil, "which", lambda b: None):
        with pytest.raises(ChatAPIError):
            list(stream_agent_cli("claude", None, [{"role": "user", "content": "q"}]))


def test_stream_chat_dispatches_agent_cli():
    with patch.object(providers.shutil, "which", lambda b: "/usr/bin/" + b), \
         patch.object(providers.subprocess, "Popen", _fake_popen("ROUTED")):
        out = list(stream_chat(provider="agent-cli", api_key="", model="claude",
                               messages=[{"role": "user", "content": "q"}]))
    assert out == ["ROUTED"]


def test_agent_cli_error_path_uses_stderr():
    with patch.object(providers.shutil, "which", lambda b: "/usr/bin/" + b), \
         patch.object(providers.subprocess, "Popen",
                       _fake_popen(stdout="", returncode=1, stderr="boom")):
        with pytest.raises(ChatAPIError) as exc_info:
            list(stream_agent_cli("claude", None, [{"role": "user", "content": "q"}]))
    assert "boom" in str(exc_info.value)


def test_agent_cli_timeout_kills_and_raises():
    class _HangingProc(_FakeProc):
        def communicate(self):
            import time as _time
            _time.sleep(0.3)  # longer than the 0.1s test timeout, but short for the suite
            return "late", ""

    killed = {"called": False}

    def popen(cmd, **kwargs):
        proc = _HangingProc(cmd)
        orig_kill = proc.kill

        def kill():
            killed["called"] = True
            orig_kill()
        proc.kill = kill
        return proc

    with patch.object(providers.shutil, "which", lambda b: "/usr/bin/" + b), \
         patch.object(providers.subprocess, "Popen", popen):
        with pytest.raises(ChatAPIError) as exc_info:
            list(stream_agent_cli("claude", None, [{"role": "user", "content": "q"}], timeout=0.1))
    assert exc_info.value.error_type == "timeout"
    assert killed["called"]


def test_tests_never_run_a_real_installed_cli(monkeypatch):
    """With nothing saved, Chat answers through the logged-in CLI, so a test without a config could reach the real
    ~/.local/bin/claude. Under DX_AGENT_NO_REAL_RUN (tests/conftest.py) a CLI that exists outside the temp
    dir is refused; fake scripts in tmp_path still run."""
    import os
    assert os.environ.get("DX_AGENT_NO_REAL_RUN") == "1"
    launched = []
    monkeypatch.setattr(providers.shutil, "which", lambda b: "/bin/true")
    monkeypatch.setattr(providers.subprocess, "Popen", lambda cmd, **kw: launched.append(cmd))
    with pytest.raises(ChatAPIError) as err:
        list(stream_agent_cli("claude", None, [{"role": "user", "content": "q"}]))
    assert "disabled under tests" in str(err.value)
    assert launched == []


def test_a_fake_cli_in_tmp_still_runs(tmp_path, monkeypatch):
    fake = tmp_path / "claude"
    fake.write_text("#!/bin/sh\necho FAKE-OK\n")
    fake.chmod(0o755)
    monkeypatch.setattr(providers.shutil, "which", lambda b: str(fake))
    assert list(stream_agent_cli("claude", None, [{"role": "user", "content": "q"}])) == ["FAKE-OK"]


def test_the_cli_runs_outside_the_repo_so_project_agent_rules_stay_out(tmp_path, monkeypatch):
    """Run inside dx-all-suite, copilot follows that repo's AGENTS.md and answers a Chat question with
    "[DX-AGENT-DEV: START]" and the DEEPX banner. Chat carries its own knowledge in the prompt, so the
    CLI runs in a neutral directory with no project instruction files above it."""
    from pathlib import Path
    fake = tmp_path / "copilot"
    fake.write_text("#!/bin/sh\npwd\n")
    fake.chmod(0o755)
    monkeypatch.setattr(providers.shutil, "which", lambda b: str(fake))
    where = Path(list(stream_agent_cli("copilot", None, [{"role": "user", "content": "q"}]))[0].strip()).resolve()
    repo = Path(providers.__file__).resolve().parents[3]          # .../dx-all-suite
    assert not where.is_relative_to(repo), where
    for d in [where, *where.parents]:
        for name in ("CLAUDE.md", "AGENTS.md", ".github"):
            assert not (d / name).exists(), d / name


def test_cursor_trusts_the_neutral_dir_without_forcing_commands(monkeypatch):
    """Run outside the repo, cursor-agent stops at "Workspace Trust Required … Pass --trust, --yolo, or -f".
    --trust trusts the folder only; -f/--yolo would also auto-run commands."""
    seen = {}

    def popen(cmd, **kwargs):
        seen["cmd"] = cmd
        return _FakeProc(cmd, stdout="ok")
    monkeypatch.setattr(providers.shutil, "which", lambda b: "/nonexistent/" + b)
    monkeypatch.setattr(providers.subprocess, "Popen", popen)
    list(stream_agent_cli("cursor", None, [{"role": "user", "content": "q"}]))
    assert "--trust" in seen["cmd"]
    assert not {"-f", "--force", "--yolo"} & set(seen["cmd"])


@pytest.mark.parametrize("said", [
    "ActionRequiredError: Your team has reached its usage limit Please reach out to an admin",
    "Error: rate limit exceeded, retry later",
    "You have exceeded your monthly quota",
])
def test_a_cli_out_of_quota_is_a_rate_limit(monkeypatch, said):
    """When cursor says its team reached its usage limit, Chat must not call it "an error" and suggest signing in
    again. Usage, rate and quota limits are rate_limit, which Chat words as a limit, not a login problem."""
    monkeypatch.setattr(providers.shutil, "which", lambda b: "/nonexistent/" + b)
    monkeypatch.setattr(providers.subprocess, "Popen", _fake_popen(stdout="", returncode=1, stderr=said))
    with pytest.raises(ChatAPIError) as err:
        list(stream_agent_cli("cursor", None, [{"role": "user", "content": "q"}]))
    assert err.value.error_type == "rate_limit"
    assert said[:30] in str(err.value)


def test_a_rate_limited_cli_gets_no_sign_in_line():
    import importlib
    E = importlib.import_module("shared.chat.engine")
    text = E.ChatEngine(app_name="dx_app")._api_error_text(
        "agent-cli", E.ChatAPIError("rate_limit", "team reached its usage limit", 1), "en", agent="cursor")
    assert "limit" in text and "cursor-agent login" not in text

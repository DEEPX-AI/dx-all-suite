"""P4: CLI 백엔드 챗 provider("agent-cli") — 로그인된 코딩 에이전트 CLI로 채팅.

claude 로그인 1회로 챗봇 + dx_agent_dev 양쪽을 커버(별도 API 키 불필요).
provider="agent-cli", model=<agent 이름>(claude/opencode/…).
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

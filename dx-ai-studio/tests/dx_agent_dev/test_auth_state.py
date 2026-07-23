"""P1: 어댑터 인증 상태 감지(is_authenticated) + detect_available_agents의 authenticated 필드.

설계: is_authenticated() -> bool | None
  - True/False: 값싼 자격증명 파일 검사로 확정 가능한 경우
  - None: 확정 불가(unknown) — 거짓 음성(로그인했는데 안 됐다고 표시) 방지
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_base_adapter_auth_unknown_is_none():
    """자격증명 경로 미선언 어댑터 → unknown(None)."""
    from core.adapters.base import SubprocessAdapter

    class Bare(SubprocessAdapter):
        cli_bin = "x"

    assert Bare(cli_path="/usr/bin/x").is_authenticated() is None


def test_claude_authenticated_true_when_creds_present(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    cdir = tmp_path / ".claude"
    cdir.mkdir()
    (cdir / ".credentials.json").write_text(json.dumps({"claudeAiOauth": {"t": 1}}))
    from core.adapters.claude import ClaudeAdapter
    assert ClaudeAdapter(cli_path="/usr/bin/claude").is_authenticated() is True


def test_claude_authenticated_false_when_no_creds(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    from core.adapters.claude import ClaudeAdapter
    assert ClaudeAdapter(cli_path="/usr/bin/claude").is_authenticated() is False


def test_cursor_authenticated_reads_authinfo(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    cdir = tmp_path / ".cursor"
    cdir.mkdir()
    (cdir / "cli-config.json").write_text(json.dumps({"authInfo": {"email": "a@b.c"}}))
    from core.adapters.cursor import CursorAdapter
    assert CursorAdapter(cli_path="/usr/bin/cursor-agent").is_authenticated() is True


def test_copilot_authenticated_when_session_store_present(monkeypatch, tmp_path):
    """로그인 후 생성되는 session-store.db 존재 시 True."""
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    cdir = tmp_path / ".copilot"
    cdir.mkdir()
    (cdir / "session-store.db").write_bytes(b"sqlite")
    from core.adapters.copilot import CopilotAdapter
    assert CopilotAdapter(cli_path="/usr/bin/copilot").is_authenticated() is True


def test_copilot_authenticated_false_when_no_session_store(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    from core.adapters.copilot import CopilotAdapter
    assert CopilotAdapter(cli_path="/usr/bin/copilot").is_authenticated() is False


def test_detect_available_agents_includes_authenticated(monkeypatch):
    """status가 노출하는 agents 항목에 authenticated 필드가 포함된다."""
    from core import environment
    monkeypatch.setattr(
        environment.shutil, "which",
        lambda n: "/usr/bin/" + n if n == "claude" else None,
    )
    agents = environment.detect_available_agents()
    assert agents, "claude가 설치된 것으로 가정했으므로 비어있으면 안 됨"
    assert all("authenticated" in a for a in agents)

"""Adapter sign-in detection (is_authenticated) and the authenticated field of detect_available_agents.

is_authenticated() -> bool | None
  - True/False: when a cheap credential-file check can decide
  - None: cannot decide (unknown), to avoid false negatives (signed in but shown as signed out)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_base_adapter_auth_unknown_is_none():
    """An adapter that declares no credential path is unknown (None)."""
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


def test_copilot_authenticated_when_config_lists_a_user(monkeypatch, tmp_path):
    """`copilot login` keeps the token in the keyring and the account in config.json's loggedInUsers.
    session-store.db is not created by signing in, so it cannot be the signal."""
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    for var in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        monkeypatch.delenv(var, raising=False)
    cdir = tmp_path / ".copilot"
    cdir.mkdir()
    (cdir / "config.json").write_text('{"loggedInUsers": [{"host": "https://github.com", "login": "me"}]}')
    from core.adapters.copilot import CopilotAdapter
    assert CopilotAdapter(cli_path="/usr/bin/copilot").is_authenticated() is True


def test_copilot_authenticated_false_when_never_logged_in(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    for var in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        monkeypatch.delenv(var, raising=False)
    from core.adapters.copilot import CopilotAdapter
    assert CopilotAdapter(cli_path="/usr/bin/copilot").is_authenticated() is False


def test_detect_available_agents_includes_authenticated(monkeypatch):
    """The agents entries in status include the authenticated field."""
    from core import environment
    monkeypatch.setattr(
        environment.shutil, "which",
        lambda n: "/usr/bin/" + n if n == "claude" else None,
    )
    agents = environment.detect_available_agents()
    assert agents, "claude가 설치된 것으로 가정했으므로 비어있으면 안 됨"
    assert all("authenticated" in a for a in agents)

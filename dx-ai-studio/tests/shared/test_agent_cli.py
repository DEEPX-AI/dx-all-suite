"""Coding-agent CLIs: installed, logged in, the Studio-wide choice, and which one Chat uses."""
from __future__ import annotations

import json
import os
import stat

import pytest

from shared import agent_cli as A


@pytest.fixture()
def box(tmp_path, monkeypatch):
    """A fake HOME, an empty PATH with a bin dir, and an isolated Studio config dir."""
    home = tmp_path / "home"
    home.mkdir()
    bindir = tmp_path / "bin"
    bindir.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("PATH", str(bindir))
    monkeypatch.setenv("DX_CHAT_CONFIG_DIR", str(tmp_path / "cfg"))
    for v in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        monkeypatch.delenv(v, raising=False)

    class Box:
        def install(self, binary):
            p = bindir / binary
            p.write_text("#!/bin/sh\necho ok\n")
            p.chmod(0o755)

        def creds(self, rel, data):
            p = home.joinpath(*rel)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(data if isinstance(data, str) else json.dumps(data))
    return Box()


def test_login_rules_per_cli(box):
    assert A.authenticated("claude") is False
    box.creds((".claude", ".credentials.json"), {"claudeAiOauth": {"t": 1}})
    assert A.authenticated("claude") is True
    box.creds((".cursor", "cli-config.json"), {"authInfo": None})
    assert A.authenticated("cursor") is False
    box.creds((".cursor", "cli-config.json"), {"authInfo": {"email": "a"}})
    assert A.authenticated("cursor") is True
    box.creds((".copilot", "config.json"), '// comment\n{"loggedInUsers": [{"login": "u"}]}')
    assert A.authenticated("copilot") is True
    box.creds((".claude", ".credentials.json"), "{broken")
    assert A.authenticated("claude") is None
    assert A.authenticated("codex") is None


def test_copilot_token_env_counts_as_login(box, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "x")
    assert A.authenticated("copilot") is True


def test_detect_lists_every_agent_in_order(box):
    box.install("claude")
    box.install("cursor-agent")
    box.creds((".claude", ".credentials.json"), {"claudeAiOauth": {"t": 1}})
    rows = A.detect()
    assert [r["name"] for r in rows] == list(A.AGENT_ORDER)
    by = {r["name"]: r for r in rows}
    assert by["claude"]["installed"] and by["claude"]["authenticated"] is True
    assert by["cursor"]["installed"] and by["cursor"]["authenticated"] is False
    assert not by["copilot"]["installed"]
    assert by["copilot"]["login_hint"] == "copilot login"


def test_install_shims_are_not_cli(box, tmp_path, monkeypatch):
    shim_dir = tmp_path / "x" / "github.copilot-chat" / "copilotCli"
    shim_dir.mkdir(parents=True)
    shim = shim_dir / "copilot"
    shim.write_text("#!/bin/sh\n")
    shim.chmod(0o755)
    monkeypatch.setenv("PATH", str(shim_dir))
    assert A.find_cli("copilot") is None


def test_studio_agent_roundtrip_is_private(box, tmp_path):
    assert A.studio_agent() is None
    A.set_studio_agent("copilot", "claude-sonnet-5.5")
    assert A.studio_agent() == {"agent": "copilot", "model": "claude-sonnet-5.5"}
    path = tmp_path / "cfg" / "agent.json"
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    A.set_studio_agent("claude", None)
    assert A.studio_agent() == {"agent": "claude", "model": None}
    with pytest.raises(ValueError):
        A.set_studio_agent("rm -rf", None)
    with pytest.raises(ValueError):
        A.set_studio_agent("claude", "x" * 300)


def test_source_order_saved_then_studio_then_logged_in_then_none(box):
    assert A.resolve_chat_source(None)["kind"] == "none"
    box.install("copilot")                                   # installed, login unknown -> usable last
    box.creds((".copilot", "config.json"), {"loggedInUsers": []})
    assert A.resolve_chat_source(None)["kind"] == "none"     # copilot says logged out
    box.install("claude")
    box.creds((".claude", ".credentials.json"), {"claudeAiOauth": {"t": 1}})
    src = A.resolve_chat_source(None)
    assert src == {"kind": "auto", "provider": "agent-cli", "agent": "claude", "model": None}
    box.creds((".copilot", "config.json"), {"loggedInUsers": [{"login": "u"}]})
    A.set_studio_agent("copilot", "gpt-5.5")
    assert A.resolve_chat_source(None) == {"kind": "studio", "provider": "agent-cli",
                                           "agent": "copilot", "model": "gpt-5.5"}
    saved = {"provider": "anthropic", "model": "claude-sonnet-4-5", "api_key": "k"}
    assert A.resolve_chat_source(saved) == {"kind": "saved", "provider": "anthropic",
                                            "agent": None, "model": "claude-sonnet-4-5"}
    saved_cli = {"provider": "agent-cli", "model": "cursor::gpt-5"}
    assert A.resolve_chat_source(saved_cli)["agent"] == "cursor"


def test_studio_agent_that_is_logged_out_is_skipped(box):
    box.install("claude")
    box.creds((".claude", ".credentials.json"), {"claudeAiOauth": {"t": 1}})
    box.install("cursor-agent")
    box.creds((".cursor", "cli-config.json"), {"authInfo": None})
    A.set_studio_agent("cursor", None)
    assert A.resolve_chat_source(None)["agent"] == "claude"


def test_an_unknown_login_is_used_only_after_known_logins(box):
    box.install("codex")                                     # login unknown (None)
    assert A.resolve_chat_source(None)["agent"] == "codex"
    box.install("claude")
    box.creds((".claude", ".credentials.json"), {"claudeAiOauth": {"t": 1}})
    assert A.resolve_chat_source(None)["agent"] == "claude"

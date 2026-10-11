"""With nothing saved, Chat answers through the logged-in CLI — real subprocess, fake CLI scripts (spec §3.1)."""
from __future__ import annotations

import importlib
import json

import pytest


@pytest.fixture()
def env(tmp_path, monkeypatch):
    home, bindir, cfg = tmp_path / "home", tmp_path / "bin", tmp_path / "cfg"
    home.mkdir(); bindir.mkdir(); cfg.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("PATH", f"{bindir}:/usr/bin:/bin")
    monkeypatch.setenv("DX_CHAT_CONFIG_DIR", str(cfg))
    for v in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        monkeypatch.delenv(v, raising=False)
    E = importlib.import_module("shared.chat.engine")
    importlib.import_module("shared.chat.config")._cached_config = None

    class Env:
        cfgdir = cfg

        def cli(self, binary, answer=None, fail=None):
            body = f'echo "{answer} $*" | head -c 40\n' if answer else f'echo "{fail}" >&2\nexit 1\n'
            p = bindir / binary
            p.write_text("#!/bin/sh\n" + body)
            p.chmod(0o755)

        def login(self, name):
            rel = {"claude": (".claude", ".credentials.json", {"claudeAiOauth": {"t": 1}}),
                   "copilot": (".copilot", "config.json", {"loggedInUsers": [{"login": "u"}]}),
                   "cursor": (".cursor", "cli-config.json", {"authInfo": {"e": 1}})}[name]
            p = home / rel[0] / rel[1]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(rel[2]))

        def ask(self, lang="en"):
            return "".join(E.ChatEngine(app_name="dx_app").stream("hello?", lang=lang))
    return Env()


def test_nothing_saved_answers_with_the_logged_in_cli(env):
    env.cli("claude", answer="CLAUDE-SAYS")
    env.login("claude")
    assert "CLAUDE-SAYS" in env.ask()


def test_the_studio_agent_wins_over_the_order(env):
    from shared import agent_cli
    env.cli("claude", answer="CLAUDE-SAYS"); env.login("claude")
    env.cli("copilot", answer="COPILOT-SAYS"); env.login("copilot")
    agent_cli.set_studio_agent("copilot", None)
    assert "COPILOT-SAYS" in env.ask()


def test_a_failing_auto_cli_says_how_to_log_in_and_does_not_switch(env):
    env.cli("copilot", fail="not logged in"); env.login("copilot")
    env.cli("claude", answer="CLAUDE-SAYS")             # installed but not logged in → not chosen
    from shared import agent_cli
    agent_cli.set_studio_agent("copilot", None)
    text = env.ask("ko")
    assert "copilot login" in text and "CLAUDE-SAYS" not in text
    assert "not logged in" in text


def test_no_cli_gives_the_offline_answer(env):
    assert "agent-cli" in env.ask()                     # fallback text names the keyless ways


def test_a_saved_config_wins(env, monkeypatch):
    env.cli("claude", answer="CLAUDE-SAYS"); env.login("claude")
    (env.cfgdir / "chat_config.json").write_text(json.dumps(
        {"provider": "agent-cli", "api_key": "", "model": "cursor", "temperature": 0.7}))
    env.cli("cursor-agent", answer="CURSOR-SAYS")
    assert "CURSOR-SAYS" in env.ask()


def test_status_reports_source_and_agents(env):
    E = importlib.import_module("shared.chat.engine")
    env.cli("claude", answer="x"); env.login("claude")
    status = E.ChatEngine(app_name="dx_app").get_config_status()
    assert status["configured"] is False
    assert status["source"] == {"kind": "auto", "provider": "agent-cli", "agent": "claude", "model": None}
    assert [a["name"] for a in status["agents"]][0] == "claude"

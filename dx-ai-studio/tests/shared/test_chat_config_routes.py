"""Chat config routes: Studio agent, reset to automatic, test before save, keep the saved key (spec §3.3)."""
from __future__ import annotations

import json
import urllib.request

import pytest

from tests.server_helpers import start_module_server


@pytest.fixture()
def srv(tmp_path, monkeypatch):
    bindir = tmp_path / "bin"; bindir.mkdir()
    monkeypatch.setenv("PATH", f"{bindir}:/usr/bin:/bin")
    monkeypatch.setenv("DX_CHAT_CONFIG_DIR", str(tmp_path / "cfg"))
    import shared.chat.config as C
    C._cached_config = None
    server, port = start_module_server("dx_planner")

    def call(method, path, body=None):
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def cli(binary, script):
        p = bindir / binary
        p.write_text("#!/bin/sh\n" + script)
        p.chmod(0o755)
    yield call, cli, tmp_path / "cfg"
    server.shutdown()


def test_studio_agent_is_saved_and_validated(srv):
    call, _, cfg = srv
    assert call("POST", "/api/studio/agent", {"agent": "copilot", "model": "gpt-5.5"}) == (200, {"ok": True})
    assert json.loads((cfg / "agent.json").read_text()) == {"agent": "copilot", "model": "gpt-5.5"}
    assert call("POST", "/api/studio/agent", {"agent": "bash"})[0] == 400


def test_save_tests_first_and_refuses_a_failing_connection(srv):
    call, cli, cfg = srv
    cli("claude", 'echo "auth expired" >&2; exit 1\n')
    code, body = call("POST", "/api/chat/config", {"provider": "agent-cli", "model": "claude"})
    assert code == 200 and body["ok"] is False and "auth expired" in body["error"]
    assert not (cfg / "chat_config.json").exists()
    code, body = call("POST", "/api/chat/config", {"provider": "agent-cli", "model": "claude", "force": True})
    assert body["ok"] is True and (cfg / "chat_config.json").exists()


def test_save_after_a_good_test(srv):
    call, cli, cfg = srv
    cli("claude", 'echo OK\n')
    code, body = call("POST", "/api/chat/config", {"provider": "agent-cli", "model": "claude"})
    assert body == {"ok": True, "tested": True, "response": "OK"}


def test_a_blank_key_keeps_the_saved_key_for_the_same_provider(srv):
    call, _, cfg = srv
    call("POST", "/api/chat/config", {"provider": "openai", "api_key": "sk-secret-1234", "model": "gpt-4o",
                                      "force": True})
    call("POST", "/api/chat/config", {"provider": "openai", "api_key": "", "model": "gpt-4.1", "force": True})
    saved = json.loads((cfg / "chat_config.json").read_text())
    assert saved["api_key"] == "sk-secret-1234" and saved["model"] == "gpt-4.1"
    code, body = call("POST", "/api/chat/config", {"provider": "anthropic", "api_key": "", "model": "c", "force": True})
    assert code == 400


def test_reset_to_automatic(srv):
    call, cli, cfg = srv
    call("POST", "/api/chat/config", {"provider": "agent-cli", "model": "claude", "force": True})
    assert call("DELETE", "/api/chat/config") == (200, {"ok": True})
    assert not (cfg / "chat_config.json").exists()
    code, status = call("GET", "/api/chat/config")
    assert status["configured"] is False and "source" in status and "agents" in status

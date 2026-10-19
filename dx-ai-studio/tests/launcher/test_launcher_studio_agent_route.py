"""The launcher itself answers the Studio-agent and reset routes.

Home lives on the launcher, which hands only a fixed list of paths to the shared chat routes. Without /api/studio/agent
on that list, picking copilot in Home would save nothing and Chat would keep answering with claude. A browser test
that routes the call never reaches a server; this one talks to the real launcher server.
"""
import json
import urllib.request

import pytest

from shared import agent_cli
from tests.server_helpers import start_module_server


@pytest.fixture()
def launcher(tmp_path, monkeypatch):
    monkeypatch.setenv("DX_CHAT_CONFIG_DIR", str(tmp_path))
    srv, port = start_module_server("launcher")
    yield port, tmp_path
    srv.shutdown()


def _call(port, method, path, body=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json", "Referer": f"http://127.0.0.1:{port}/"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, {}


def test_home_can_save_the_studio_agent(launcher):
    port, cfg = launcher
    assert _call(port, "POST", "/api/studio/agent", {"agent": "copilot", "model": None}) == (200, {"ok": True})
    assert agent_cli.studio_agent() == {"agent": "copilot", "model": None}


def test_back_to_automatic_reaches_the_launcher(launcher):
    port, cfg = launcher
    (cfg / "chat_config.json").write_text(json.dumps({"provider": "agent-cli", "model": "claude"}))
    assert _call(port, "DELETE", "/api/chat/config") == (200, {"ok": True})
    assert not (cfg / "chat_config.json").exists()


def test_every_chat_route_reaches_the_launcher(launcher):
    """The same hand-kept list also left out local-model discovery and the knowledge refresh: Home's chat got a
    502 for both (found in the same check). The launcher now hands every shared chat route to the shared handler."""
    port, _ = launcher
    code, body = _call(port, "GET", "/api/chat/local/models?base=http://127.0.0.1:9")
    assert code == 200 and body.get("available") is False
    code, body = _call(port, "POST", "/api/chat/knowledge/refresh", {})
    assert code == 200 and "ok" in body

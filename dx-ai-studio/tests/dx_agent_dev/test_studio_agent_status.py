"""Agent Dev's status names the Studio-wide agent so its picker and Home's start on the same one (spec §3.5)."""
import json
import urllib.request

from shared import agent_cli
from tests.server_helpers import start_module_server


def test_status_carries_the_studio_agent(tmp_path, monkeypatch):
    monkeypatch.setenv("DX_CHAT_CONFIG_DIR", str(tmp_path))
    agent_cli.set_studio_agent("cursor", "gpt-5")
    srv, port = start_module_server("dx_agent_dev")
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/agent/status", timeout=10) as r:
            status = json.loads(r.read())
        assert status["studio_agent"] == {"agent": "cursor", "model": "gpt-5"}
    finally:
        srv.shutdown()


def test_adapters_use_the_shared_login_rules(tmp_path, monkeypatch):
    from dx_agent_dev.core.adapters.cursor import CursorAdapter
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".cursor").mkdir()
    (tmp_path / ".cursor" / "cli-config.json").write_text('// c\n{"authInfo": {"e": 1}}')
    # the shared rule strips // comments; the old per-adapter rule raised on them and answered None
    assert CursorAdapter(cli_path="/usr/bin/cursor-agent").is_authenticated() is True

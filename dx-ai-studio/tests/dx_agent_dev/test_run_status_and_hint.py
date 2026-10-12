"""Terminal lines show the whole command, and status says what the running job is.

- `_tool_arg_hint` must not cut a command at 50 characters, or home's terminal fills only half its width.
  Truncation is for runaway JSON; other keys (prompt, url, …) stay short.
- When Agent Dev takes over a run home started, it needs the first line (the user's request) and the conversation.
"""
from __future__ import annotations

import json
import time
import urllib.request

import pytest

from tests.server_helpers import start_module_server


def test_a_command_is_shown_whole():
    from dx_agent_dev.core.adapters.base import _tool_arg_hint

    cmd = "cd /home/deepx/hj_ws/dx-all-suite/dx-runtime/dx_app && ./build.sh --clean --verbose  && ls -la build"
    assert _tool_arg_hint({"command": cmd}) == " ".join(cmd.split())
    assert _tool_arg_hint({"cmd": "  a\n  b  "}) == "a b"


def test_other_hints_stay_short():
    from dx_agent_dev.core.adapters.base import _tool_arg_hint

    long_prompt = "x" * 120
    got = _tool_arg_hint({"prompt": long_prompt})
    assert len(got) <= 51 and got.endswith("…")


@pytest.fixture()
def agent(monkeypatch):
    monkeypatch.setenv("DX_AGENT_ADAPTER", "mock")
    monkeypatch.setenv("DX_AGENT_MOCK_DELAY", "0.3")
    server, port = start_module_server("dx_agent_dev")
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()


def test_status_names_the_running_request_and_its_conversation(agent):
    req = urllib.request.Request(agent + "/api/agent/run", data=json.dumps(
        {"prompt": "make a pose demo", "mode": "autopilot"}).encode(),
        headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=30)
    resp.readline()
    resp.close()
    time.sleep(0.2)
    with urllib.request.urlopen(agent + "/api/agent/status", timeout=10) as r:
        st = json.loads(r.read().decode())
    assert not st["run_done"]
    assert st["run_prompt"] == "make a pose demo"
    assert st["run_conversation_id"]
    assert st["run_mode"] == "autopilot"

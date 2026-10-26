"""In-UI sign-in help: /api/agent/login/status (install state, auth state, sign-in command).

Embedded device-code streaming needs a live CLI, so this covers the safe status-and-guidance path.
"""
import json
import os
import sys
import threading
import time
from pathlib import Path
from urllib.request import urlopen

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))

TEST_PORT = 18101
BASE = f"http://127.0.0.1:{TEST_PORT}"


@pytest.fixture(scope="module")
def server():
    os.environ["DX_AGENT_ADAPTER"] = "mock"
    from server import create_server
    httpd = create_server(port=TEST_PORT)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    time.sleep(0.5)
    yield httpd
    httpd.shutdown()
    os.environ.pop("DX_AGENT_ADAPTER", None)


def test_login_status_known_agent_has_fields(server):
    data = json.loads(urlopen(f"{BASE}/api/agent/login/status?agent=claude", timeout=5).read())
    assert data["agent"] == "claude"
    assert "installed" in data and "authenticated" in data
    assert data["hint"] and "claude" in data["hint"]


def test_login_status_unknown_agent(server):
    data = json.loads(urlopen(f"{BASE}/api/agent/login/status?agent=nope", timeout=5).read())
    assert data["installed"] is False
    assert data["hint"] is None


def test_login_hint_present_for_each_known_agent():
    from core.adapters import make_adapter
    for name in ("claude", "copilot", "cursor", "opencode"):
        a = make_adapter(name)
        assert a is not None and a.login_cmd_hint, f"{name} should have a login hint"

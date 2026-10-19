"""status agents field and run agent/model branches (offline Mock path)."""
import json
import os
import sys
import threading
import time

import pytest
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))

TEST_PORT = 18096
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


@pytest.fixture(scope="module")
def server():
    os.environ["DX_AGENT_ADAPTER"] = "mock"
    from server import create_server
    httpd = create_server(port=TEST_PORT)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)
    yield httpd
    httpd.shutdown()
    os.environ.pop("DX_AGENT_ADAPTER", None)


def _post_sse(payload):
    req = Request(f"{BASE_URL}/api/agent/run", data=json.dumps(payload).encode(),
                  headers={"Content-Type": "application/json"}, method="POST")
    raw = urlopen(req, timeout=10).read().decode()
    return [json.loads(l[6:]) for l in raw.splitlines()
            if l.startswith("data: ") and l[6:] != "[DONE]"]


def test_status_has_agents_list(server):
    data = json.loads(urlopen(f"{BASE_URL}/api/agent/status", timeout=5).read())
    assert "agents" in data
    assert isinstance(data["agents"], list)
    # existing fields are kept
    for k in ("available", "reason", "busy", "showcase_count"):
        assert k in data


def test_run_unknown_agent_returns_400(server):
    """An unsupported agent returns 400 (distinct from omitting it)."""
    with pytest.raises(HTTPError) as e:
        _post_sse({"prompt": "build x", "agent": "no-such-agent"})
    assert e.value.code == 400


def test_run_without_agent_falls_back(server):
    """Omitting agent falls back (Mock), not 400."""
    events = _post_sse({"prompt": "build x"})
    types = [e["type"] for e in events]
    assert types[-1] in ("done", "error")
    assert "message" in types


def test_forced_mock_ignores_explicit_agent(server):
    """With forced_mock (DX_AGENT_ADAPTER=mock) an explicit agent is ignored and Mock is always used.

    Even an API call with agent='copilot' (installed) must not reach the real CLI; the Mock-specific
    sequence ('dx-suite-builder') must come out. The UI hides the dropdown when forced, but the server
    must still defend.
    """
    events = _post_sse({"prompt": "build x", "agent": "copilot"})
    texts = [e.get("text", "") for e in events]
    assert any("dx-suite-builder" in t for t in texts), texts
    assert events[-1]["type"] in ("done", "error")

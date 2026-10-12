"""DX Agent Dev degraded (unavailable) endpoint, end to end.

With DX_AGENT_ADAPTER unset the server degrades naturally (offline: no .deepx harness).
Contract: /api/agent/run returns 200 SSE with one degraded frame and ends (the runner is not entered), not 404.
Port 18097 avoids other test servers; kept apart from test_server.py to isolate env changes.
"""
import json
import os
import sys
import threading
import time

import pytest
from pathlib import Path
from urllib.request import urlopen, Request

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))

TEST_PORT = 18097
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


@pytest.fixture(scope="module")
def degraded_server():
    os.environ.pop("DX_AGENT_ADAPTER", None)  # disable the mock override
    from core import environment
    from server import create_server
    # Force degradation deterministically: pin detect_environment so an agent CLI (opencode etc.)
    # or a .deepx harness on the machine cannot break the degraded assumption.
    _orig_detect = environment.detect_environment
    environment.detect_environment = lambda: {
        "available": False, "forced_mock": False, "cli": None,
        "harness_dirs": [], "reason": "cli_missing",
    }
    httpd = create_server(port=TEST_PORT)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)
    yield httpd
    httpd.shutdown()
    environment.detect_environment = _orig_detect


def test_status_reports_unavailable(degraded_server):
    data = json.loads(urlopen(f"{BASE_URL}/api/agent/status", timeout=5).read())
    assert data["available"] is False


def test_run_degraded_returns_200_sse_not_404(degraded_server):
    """When degraded: 200 SSE with a single degraded frame (not 404, runner not entered)."""
    req = Request(f"{BASE_URL}/api/agent/run",
                  data=json.dumps({"prompt": "build something"}).encode(),
                  headers={"Content-Type": "application/json"}, method="POST")
    resp = urlopen(req, timeout=5)
    assert resp.status == 200  # not 404
    frames = [json.loads(l[6:]) for l in resp.read().decode().splitlines()
              if l.startswith("data: ")]
    # a single degraded frame shows the runner was not entered (it would emit message/done events)
    assert len(frames) == 1
    assert frames[0]["type"] == "degraded"

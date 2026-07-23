"""DX Agent Dev 강등(unavailable) 엔드포인트 e2e — MED-8/§10 #8.

DX_AGENT_ADAPTER 미설정 → 자연 강등(폐쇄망: .deepx 하니스 부재).
계약: /api/agent/run 은 404가 아니라 200 SSE로 degraded 1프레임 후 종료(러너 미진입).
포트 18097 — 다른 테스트 서버와 충돌 방지. env 오염 격리를 위해 test_server.py와 분리한다.
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
    os.environ.pop("DX_AGENT_ADAPTER", None)  # mock 우선분기 차단
    from core import environment
    from server import create_server
    # 강등을 결정적으로 강제: 실제 머신에 에이전트 CLI(opencode 등)나 .deepx 하니스가
    # 있어도(일반망) 자연 강등 가정이 깨지지 않도록 detect_environment를 고정한다.
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
    """강등 시 200 SSE + degraded 단일 프레임(404 아님, 러너 미진입)."""
    req = Request(f"{BASE_URL}/api/agent/run",
                  data=json.dumps({"prompt": "build something"}).encode(),
                  headers={"Content-Type": "application/json"}, method="POST")
    resp = urlopen(req, timeout=5)
    assert resp.status == 200  # 404가 아님
    frames = [json.loads(l[6:]) for l in resp.read().decode().splitlines()
              if l.startswith("data: ")]
    # 단일 degraded 프레임 = 러너가 진입하지 않았음을 간접 보장(진입 시 message/done 다수)
    assert len(frames) == 1
    assert frames[0]["type"] == "degraded"

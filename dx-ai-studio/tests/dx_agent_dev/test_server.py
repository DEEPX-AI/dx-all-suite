"""DX Agent Dev server.py 통합 테스트.

테스트 포트 18099 사용 — 실제 서버 포트(8099)와 충돌 방지.
"""
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

TEST_PORT = 18099
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


@pytest.fixture(scope="module")
def monkeypatch_module():
    """모듈 전체에서 Mock 어댑터 강제(폐쇄망 계약 검증)."""
    os.environ["DX_AGENT_ADAPTER"] = "mock"
    yield
    os.environ.pop("DX_AGENT_ADAPTER", None)


@pytest.fixture(scope="module")
def server(monkeypatch_module):
    from server import create_server
    httpd = create_server(port=TEST_PORT)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)
    yield httpd
    httpd.shutdown()


def _get_json(path):
    return json.loads(urlopen(f"{BASE_URL}{path}", timeout=5).read())


def _post_sse(path, payload):
    """POST → data: 프레임 파싱 → 이벤트 리스트."""
    req = Request(f"{BASE_URL}{path}", data=json.dumps(payload).encode(),
                  headers={"Content-Type": "application/json"}, method="POST")
    raw = urlopen(req, timeout=10).read().decode()
    events = []
    for line in raw.splitlines():
        if line.startswith("data: "):
            frag = line[6:]
            if frag == "[DONE]":
                continue
            try:
                events.append(json.loads(frag))
            except json.JSONDecodeError:
                pass
    return events




def test_root_returns_html(server):
    body = urlopen(f"{BASE_URL}/", timeout=5).read().decode()
    assert "agent-console" in body


def test_status_endpoint(server):
    data = _get_json("/api/agent/status")
    assert "available" in data


def test_showcases_endpoint(server):
    data = _get_json("/api/agent/showcases")
    assert "showcases" in data
    assert isinstance(data["showcases"], list)


def test_unknown_api_404(server):
    with pytest.raises(HTTPError) as e:
        urlopen(f"{BASE_URL}/api/nope", timeout=5)
    assert e.value.code == 404




def test_run_sse_emits_done(server):
    events = _post_sse("/api/agent/run", {"prompt": "build a demo", "lang": "en"})
    types = [e["type"] for e in events]
    assert types[-1] in ("done", "error")
    assert "message" in types
    done = next(e for e in events if e.get("type") == "done")
    assert done.get("conversation_id")


def test_run_followup_reuses_conversation_id(server):
    first = _post_sse("/api/agent/run", {"prompt": "hello"})
    cid = next(e["conversation_id"] for e in first if e.get("type") == "done")
    second = _post_sse("/api/agent/run", {"prompt": "1", "conversation_id": cid})
    done = next(e for e in second if e.get("type") == "done")
    assert done.get("conversation_id") == cid


def test_run_empty_prompt_400(server):
    with pytest.raises(HTTPError) as e:
        _post_sse("/api/agent/run", {"prompt": "   "})
    assert e.value.code == 400


def test_run_oversize_prompt_400(server):
    with pytest.raises(HTTPError) as e:
        _post_sse("/api/agent/run", {"prompt": "x" * 9000})
    assert e.value.code == 400


_LANGS = {"en", "ko", "ja", "zh-CN", "zh-TW", "es"}


def test_degraded_payload_contract():
    """available=false 시 run 분기가 만드는 페이로드(404 아님, MED-8/§10 #8).

    reason(raw code) + text(short EN summary, backward-compat) + localized title/detail +
    installOptions(cli_missing only, per-CLI install/login status).
    """
    from server import _degraded_payload
    payload = _degraded_payload({"reason": "cli_missing"})
    assert payload["type"] == "degraded"
    assert payload["reason"] == "cli_missing"
    assert isinstance(payload["text"], str) and payload["text"]
    assert set(payload["title"]) == _LANGS
    assert set(payload["detail"]) == _LANGS
    assert isinstance(payload["installOptions"], list) and payload["installOptions"]
    for opt in payload["installOptions"]:
        assert opt["agent"] and opt["displayName"]
        assert isinstance(opt["installed"], bool)


def test_degraded_payload_harness_missing_no_install_options():
    from server import _degraded_payload
    payload = _degraded_payload({"reason": "harness_missing"})
    assert payload["reason"] == "harness_missing"
    assert set(payload["title"]) == _LANGS
    assert set(payload["detail"]) == _LANGS
    assert "installOptions" not in payload


def test_degraded_payload_fallback_text():
    from server import _degraded_payload
    payload = _degraded_payload({})
    assert payload["reason"] == "unavailable"
    assert isinstance(payload["text"], str) and payload["text"]
    assert set(payload["title"]) == _LANGS
    assert "installOptions" not in payload

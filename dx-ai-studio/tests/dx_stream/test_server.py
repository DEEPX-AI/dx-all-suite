"""DX Stream server.py 통합 테스트.

테스트 포트 18093 사용 — 실제 서버 포트(8093)와 충돌 방지.
"""
import json
import http.client
import sys
import threading
import time

import pytest
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))

TEST_PORT = 18093
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


@pytest.fixture(scope="module")
def server():
    from server import create_server
    httpd = create_server(port=TEST_PORT)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)
    yield httpd
    httpd.shutdown()
    httpd.server_close()


def _get(path: str) -> bytes:
    """GET 요청 헬퍼."""
    return urlopen(f"{BASE_URL}{path}", timeout=5).read()


def _get_json(path: str):
    """GET 요청 → JSON 파싱."""
    return json.loads(_get(path))


def _post_json(path: str, body: dict):
    """POST JSON body → 응답 dict"""
    import urllib.request
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{path}", data=data,
        headers={"Content-Type": "application/json"},
        method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=5).read())


# ── 테스트 ────────────────────────────────────────────────────


def test_get_root_returns_html(server):
    """GET / 는 200 + HTML을 반환해야 한다."""
    resp = urlopen(f"{BASE_URL}/", timeout=5)
    assert resp.status == 200
    body = resp.read().decode()
    assert "<html>" in body.lower() or "<!doctype html>" in body.lower()


def test_index_html_returns_html(server):
    resp = urlopen(f"{BASE_URL}/index.html", timeout=5)
    assert resp.status == 200
    body = resp.read().decode()
    assert "<html>" in body.lower() or "<!doctype html>" in body.lower()
    assert "DX Stream" in body


def test_api_status_returns_json(server):
    """GET /api/status 는 npu, gstreamer, models 키를 포함해야 한다."""
    data = _get_json("/api/status")
    assert "npu" in data
    assert "gstreamer" in data
    assert "models" in data


def test_api_demos_returns_list(server):
    """GET /api/demos 는 dev-backed 11개 데모 목록을 반환해야 한다."""
    data = _get_json("/api/demos")
    assert isinstance(data, list)
    assert len(data) == 11


def test_api_models_returns_catalog_object(server):
    """GET /api/models 는 카탈로그 객체를 반환해야 한다."""
    data = _get_json("/api/models")
    assert isinstance(data, dict)
    assert data["catalog_source"] in {"manifest", "fallback"}
    assert isinstance(data["models"], list)
    assert len(data["models"]) >= 1


def test_api_elements_returns_list(server):
    """GET /api/elements 는 13개 이상 엘리먼트를 반환해야 한다."""
    data = _get_json("/api/elements")
    assert isinstance(data, list)
    assert len(data) >= 13


def test_unknown_api_returns_404(server):
    """GET /api/nonexistent 는 404를 반환해야 한다."""
    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"{BASE_URL}/api/nonexistent", timeout=5)
    assert exc_info.value.code == 404


def test_static_css_served(server):
    """GET /static/css/stream.css 는 200 + Stream CSS를 반환해야 한다."""
    resp = urlopen(f"{BASE_URL}/static/css/stream.css", timeout=5)
    css = resp.read().decode()
    assert resp.status == 200
    assert "text/css" in resp.headers.get("Content-Type", "")
    assert "--stream-color" in css
    assert ".stream-badge" in css


def test_pipeline_iso_css_served(server):
    resp = urlopen(f"{BASE_URL}/static/css/pipeline-iso.css", timeout=5)
    css = resp.read().decode()
    assert resp.status == 200
    assert "text/css" in resp.headers.get("Content-Type", "")
    assert ".pipeline-builder" in css
    assert ".palette-panel" in css


def test_shared_foundation_css_served(server):
    css = _get("/static/shared/dx-fonts.css").decode()
    assert "/static/shared/fonts/inter-v20-latin-regular.woff2" in css


def test_shared_font_served(server):
    data = _get("/static/shared/fonts/inter-v20-latin-regular.woff2")
    assert data
    assert data[:4] == b"wOF2"


def test_api_setup_log_returns_json(server):
    data = _get_json("/api/setup/log")
    assert "log" in data
    assert "done" in data


def test_api_setup_status_returns_dict(server):
    data = _get_json("/api/setup/status")
    assert isinstance(data, dict)
    assert "build" in data


def test_tutorial_tags_in_html(server):
    """index.html에 tutorial 관련 3개 태그가 존재하는지 확인."""
    resp = urlopen(f"{BASE_URL}/", timeout=5)
    html = resp.read().decode()
    assert 'tutorial-engine.js' in html, "tutorial-engine.js 태그 누락"
    assert 'tutorial.js' in html, "tutorial.js 태그 누락"
    assert 'tutorial.css' in html, "tutorial.css 태그 누락"


def test_api_pipeline_status(server):
    """GET /api/pipeline/status 는 running 필드를 반환해야 한다."""
    data = _get_json("/api/pipeline/status")
    assert "running" in data
    assert data["running"] is False


def test_post_without_body_handler_drains_keepalive_body(server):
    """body를 쓰지 않는 POST 핸들러도 keep-alive 요청 본문을 소비해야 한다."""
    conn = http.client.HTTPConnection("127.0.0.1", TEST_PORT, timeout=5)
    try:
        conn.request(
            "POST",
            "/api/setup/stop",
            body=b"{}",
            headers={"Content-Type": "application/json", "Content-Length": "2"},
        )
        first = conn.getresponse()
        first.read()
        assert first.status == 200

        conn.request("GET", "/api/pipeline/status")
        second = conn.getresponse()
        body = second.read().decode()
    finally:
        conn.close()

    assert second.status == 200
    assert json.loads(body)["running"] is False


def test_api_pipeline_elements_wrapped(server):
    """API 응답이 categories + connection_rules를 포함하는지 확인"""
    data = _get_json("/api/pipeline/elements")
    assert "categories" in data
    assert "connection_rules" in data
    assert "element_overrides" in data
    assert "semantic_warnings" in data
    assert "auto_converter_rules" in data
    assert isinstance(data["categories"], dict)
    assert "source" in data["categories"]

def test_api_pipeline_validate_connection(server):
    """서버사이드 연결 검증"""
    data = _post_json("/api/pipeline/validate-connection",
                      {"from_elem": "urisourcebin", "to_elem": "DxPreprocess"})
    assert data["result"] == "allow"

def test_api_pipeline_validate_connection_block(server):
    data = _post_json("/api/pipeline/validate-connection",
                      {"from_elem": "fpsdisplaysink", "to_elem": "DxInfer"})
    assert data["result"] == "block"


def test_api_models_returns_catalog_source(server):
    data = _get_json("/api/models")
    assert isinstance(data, dict)
    assert data["catalog_source"] in {"manifest", "fallback"}
    assert isinstance(data["models"], list)

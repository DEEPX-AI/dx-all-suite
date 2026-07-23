"""DX Monitor server.py 통합 테스트.

테스트 포트 18098 사용 — 실제 서버 포트(8098)와 충돌 방지.
"""
import json
import sys
import threading
import time

import pytest
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_monitor"))

TEST_PORT = 18098
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


def _get(path: str) -> bytes:
    """GET 요청 헬퍼."""
    return urlopen(f"{BASE_URL}{path}", timeout=5).read()


def _get_json(path: str):
    """GET 요청 → JSON 파싱."""
    return json.loads(_get(path))




def test_get_root_returns_html(server):
    """GET / 는 200 + HTML을 반환해야 한다."""
    resp = urlopen(f"{BASE_URL}/", timeout=5)
    assert resp.status == 200
    body = resp.read().decode()
    assert "<html>" in body.lower() or "<!doctype html>" in body.lower()


def test_api_hw_status_returns_json(server):
    """GET /api/hw_status 는 npus 키를 포함해야 한다."""
    data = _get_json("/api/hw_status")
    assert "npus" in data
    assert isinstance(data["npus"], list)
    assert "ts" in data


def test_api_system_info_returns_json(server):
    """GET /api/system_info 는 OS, hostname 등을 포함해야 한다."""
    data = _get_json("/api/system_info")
    assert "os" in data
    assert "hostname" in data
    assert "arch" in data
    assert "python" in data


def test_api_hb_returns_ok(server):
    """GET /api/hb 는 {ok: true}를 반환해야 한다."""
    data = _get_json("/api/hb")
    assert data == {"ok": True}


def test_unknown_api_returns_404(server):
    """GET /api/nonexistent 는 404를 반환해야 한다."""
    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"{BASE_URL}/api/nonexistent", timeout=5)
    assert exc_info.value.code == 404


def test_static_css_served(server):
    """GET /static/css/style.css 는 200 + CSS를 반환해야 한다."""
    resp = urlopen(f"{BASE_URL}/static/css/style.css", timeout=5)
    assert resp.status == 200
    content_type = resp.headers.get("Content-Type", "")
    assert "text/css" in content_type


def test_static_js_served(server):
    """GET /static/js/dashboard.js 는 200을 반환해야 한다."""
    resp = urlopen(f"{BASE_URL}/static/js/dashboard.js", timeout=5)
    assert resp.status == 200


def test_hw_status_has_system_metrics(server):
    """hw_status 응답에 CPU, 메모리, 디스크 정보가 포함되어야 한다."""
    data = _get_json("/api/hw_status")
    assert "cpu_load" in data
    assert "mem_total_mb" in data
    assert "mem_pct" in data
    assert "disk_total_gb" in data


def test_system_info_has_npu_count(server):
    """system_info에 npu_count 필드가 있어야 한다."""
    data = _get_json("/api/system_info")
    assert "npu_count" in data
    assert isinstance(data["npu_count"], int)


def test_chat_config_endpoint(server):
    """GET /api/chat/config 가 동작해야 한다."""
    data = _get_json("/api/chat/config")
    assert isinstance(data, dict)


def test_tutorial_tags_in_html(server):
    """index.html에 tutorial 관련 태그가 존재하는지 확인."""
    resp = urlopen(f"{BASE_URL}/", timeout=5)
    html = resp.read().decode()
    assert 'tutorial.js' in html, "tutorial.js 태그 누락"


def test_api_events_returns_list(server):
    """GET /api/events 는 리스트를 반환해야 한다."""
    data = _get_json("/api/events")
    assert isinstance(data, list)


def test_api_events_with_since_param(server):
    """GET /api/events?since=0 이 동작해야 한다."""
    data = _get_json("/api/events?since=0")
    assert isinstance(data, list)


def test_hw_status_has_swap(server):
    """hw_status 응답에 swap 관련 필드가 포함되어야 한다."""
    data = _get_json("/api/hw_status")
    assert "swap_total_mb" in data
    assert "swap_used_mb" in data
    assert "swap_pct" in data
    assert isinstance(data["swap_pct"], (int, float))


def test_hw_status_has_cpu_cores_pct(server):
    """hw_status 응답에 cpu_cores_pct 필드가 포함되어야 한다."""
    data = _get_json("/api/hw_status")
    assert "cpu_cores_pct" in data
    assert isinstance(data["cpu_cores_pct"], list)


def test_system_info_has_versions(server):
    """system_info 응답에 SDK/드라이버 버전 및 업타임이 포함되어야 한다."""
    data = _get_json("/api/system_info")
    assert "sdk_version" in data
    assert "driver_version" in data
    assert "pcie_driver_version" in data
    assert "uptime" in data


def test_index_html_has_status_bar(server):
    """index.html에 status-bar 요소가 존재해야 한다."""
    html = _get("/").decode()
    assert 'id="status-bar"' in html


def test_index_html_has_event_log(server):
    """index.html에 이벤트 로그 카드가 존재해야 한다."""
    html = _get("/").decode()
    assert 'id="event-log"' in html


def test_index_html_has_chart_mode_buttons(server):
    """index.html에 차트 모드 버튼이 존재해야 한다."""
    html = _get("/").decode()
    assert 'cm-temp' in html
    assert 'cm-all' in html
    assert 'cm-cpu' in html


def test_system_info_has_thresholds(server):
    """system_info 응답에 thresholds 필드가 포함되어야 한다."""
    data = _get_json("/api/system_info")
    assert "thresholds" in data
    th = data["thresholds"]
    assert isinstance(th, dict)
    assert "npu_temp" in th
    assert "cpu_load" in th
    cpu_th = th["cpu_load"]
    assert "warn" in cpu_th and "crit" in cpu_th
    assert isinstance(cpu_th["warn"], (int, float))
    assert cpu_th["warn"] < cpu_th["crit"]


def test_sse_loop_not_capped_at_600(server):
    """SSE loop must not use range(600); should use a long-lived or condition-based loop."""
    import inspect
    from server import MonitorHandler
    source = inspect.getsource(MonitorHandler._sse)
    assert "range(600)" not in source, (
        "SSE loop still uses range(600) — causes hard disconnect after 15 min"
    )


def test_root_html_includes_shared_framework_assets(server):
    """Root HTML must expose shared i18n, toolbar, tutorial, chat, and monitor assets."""
    html = _get("/").decode()
    expected = [
        "/static/js/i18n.js",
        "/static/shared/i18n.js",
        "/static/shared/toolbar.js",
        "DXToolbar.init({ container: '.toolbar' });",
        "/static/js/utils.js",
        "/static/js/charts.js",
        "/static/js/dashboard.js",
        "/static/shared/tutorial-engine.js",
        "/static/shared/tutorial-init.js",
        "/static/js/tutorial.js",
        "/static/shared/chat-widget.css",
        "/static/shared/chat-widget.js",
        "DXChat.init({ appName: 'dx_monitor' });",
    ]
    missing = [token for token in expected if token not in html]
    assert not missing, missing

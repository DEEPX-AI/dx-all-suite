"""DX Monitor server.py 통합 테스트.

테스트 포트 18098 사용 — 실제 서버 포트(8098)와 충돌 방지.
"""
import importlib
import json
import signal
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


@pytest.fixture
def server():
    from server import create_server
    httpd = create_server(port=TEST_PORT)
    t = threading.Thread(
        target=httpd.serve_forever,
        kwargs={"poll_interval": 0.01},
        daemon=True,
    )
    t.start()
    time.sleep(0.05)
    yield httpd
    httpd.shutdown()
    httpd.server_close()
    t.join(timeout=2)


def _get(path: str) -> bytes:
    """GET 요청 헬퍼."""
    return urlopen(f"{BASE_URL}{path}", timeout=5).read()


def _get_json(path: str):
    """GET 요청 → JSON 파싱."""
    return json.loads(_get(path))


def _get_json_from(port, path):
    """GET a JSON response from an ephemeral test server."""
    return json.loads(
        urlopen("http://127.0.0.1:{0}{1}".format(port, path), timeout=5).read()
    )



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


@pytest.mark.parametrize("since", ["abc", "x" * 4097, "nan", "inf"])
def test_api_events_rejects_invalid_since_without_server_error(server, since):
    """Malformed, oversized, and non-finite event cursors return an empty list."""
    response = urlopen(f"{BASE_URL}/api/events?since={since}", timeout=5)

    assert response.status == 200
    assert json.loads(response.read()) == []


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


def test_create_server_reports_bind_conflict_as_os_error():
    """A failed bind must not call lifecycle cleanup before its fields exist."""
    import server as monitor_server

    first = monitor_server.create_server(port=0)
    try:
        with pytest.raises(OSError):
            monitor_server.create_server(port=first.server_address[1])
    finally:
        first.server_close()


def _hardware_free_monitor_server(monkeypatch):
    """Prepare unavailable hardware state without reloading a live server module."""
    import server as monitor_server
    from shared import hardware as shared_hardware

    for name in (
        "_DS", "_dx_ok", "_NPU_STATS_BIN", "_APP_ROOT", "_TELEMETRY",
        "_TELEMETRY_EPOCH", "_TELEMETRY_ACTIVE", "_EXPLICIT_MOCK", "_prev_cpu",
    ):
        monkeypatch.setattr(shared_hardware, name, getattr(shared_hardware, name))
    monkeypatch.setattr(shared_hardware, "_hw_cache", dict(shared_hardware._hw_cache))
    monkeypatch.setattr(monitor_server, "_telemetry_supervisor", None)
    monkeypatch.setattr(monitor_server, "_lifecycle_owners", set())
    monkeypatch.setattr(monitor_server, "_lifecycle_shutdown", False)
    shared_hardware.init_hw(ds=None, dx_ok=False, app_root=monitor_server.DX_APP_ROOT)
    return monitor_server


def _serve_httpd(httpd):
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return thread


def test_hw_status_unavailable_payload_keeps_telemetry_shape(monkeypatch):
    """Hardware-free Monitor startup keeps the dashboard payload schema."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    httpd = monitor_server.create_server(port=0)
    thread = _serve_httpd(httpd)

    try:
        data = _get_json_from(httpd.server_address[1], "/api/hw_status")
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)

    assert data["available"] is False
    assert data["npus"] == []
    assert isinstance(data["ts"], (int, float))
    assert data["telemetry"]["available"] is False
    assert data["telemetry"]["source_mode"] == "unavailable"
    assert isinstance(data["telemetry"]["diagnostics"], list)


def test_system_info_unavailable_payload_keeps_npu_and_version_fields(monkeypatch):
    """Hardware-free Monitor startup exposes stable system-info defaults."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    httpd = monitor_server.create_server(port=0)
    thread = _serve_httpd(httpd)

    try:
        data = _get_json_from(httpd.server_address[1], "/api/system_info")
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)

    assert data["dx_engine_available"] is False
    assert data["npu_count"] == 0
    assert isinstance(data["npu_count"], int)
    assert data["sdk_version"] == "N/A"
    assert data["driver_version"] == "N/A"
    assert data["pcie_driver_version"] == "N/A"


def test_system_info_bound_unstarted_supervisor_keeps_unavailable_versions(monkeypatch):
    """A bound but unstarted supervisor preserves N/A endpoint version values."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    from shared import hardware as shared_hardware

    supervisor = monitor_server.hardware_init.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    shared_hardware.init_hw(telemetry=supervisor, app_root=monitor_server.DX_APP_ROOT)
    httpd = monitor_server.create_server(port=0)
    thread = _serve_httpd(httpd)
    port = httpd.server_address[1]

    try:
        data = json.loads(
            urlopen("http://127.0.0.1:{0}/api/system_info".format(port), timeout=5)
            .read()
        )
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)
        shared_hardware.detach_telemetry_if(supervisor)

    assert data["dx_engine_available"] is False
    assert data["npu_count"] == 0
    assert data["sdk_version"] == "N/A"
    assert data["driver_version"] == "N/A"
    assert data["pcie_driver_version"] == "N/A"


def test_api_events_returns_cached_provider_events(server, monkeypatch):
    """The events endpoint delegates to the telemetry cache provider."""
    import server as monitor_server

    expected = [{"ts": 12.5, "level": "warning", "message": "cached event"}]
    observed = []

    def _get_events(since=0.0):
        observed.append(since)
        return expected

    monkeypatch.setattr(monitor_server.events, "get_events", _get_events)

    assert _get_json("/api/events?since=10") == expected
    assert observed == ["10"]


def test_skip_startup_initializes_unavailable_shared_hardware(monkeypatch):
    """The test flag avoids telemetry worker startup and binds an unavailable cache."""
    import server as monitor_server
    from shared import hardware as shared_hardware

    calls = []
    monkeypatch.setenv("DX_MONITOR_SKIP_HARDWARE_INIT", "1")
    monkeypatch.setattr(
        monitor_server.hardware_init,
        "init",
        lambda: pytest.fail("hardware_init.init must not run when startup is skipped"),
    )
    monkeypatch.setattr(
        shared_hardware,
        "init_hw",
        lambda **kwargs: calls.append(kwargs),
    )

    monitor_server = importlib.reload(monitor_server)

    assert monitor_server._telemetry_supervisor is None
    assert calls == [{"ds": None, "dx_ok": False, "app_root": monitor_server.DX_APP_ROOT}]


def test_normal_module_startup_retains_single_hardware_supervisor(monkeypatch):
    """A normal server import initializes once and retains the lifecycle singleton."""
    import server as monitor_server

    sentinel = object()
    calls = []
    monkeypatch.delenv("DX_MONITOR_SKIP_HARDWARE_INIT", raising=False)
    monkeypatch.setattr(
        monitor_server.hardware_init,
        "init",
        lambda: calls.append("init") or sentinel,
    )

    monitor_server = importlib.reload(monitor_server)

    assert calls == ["init"]
    assert monitor_server._telemetry_supervisor is sentinel

    _hardware_free_monitor_server(monkeypatch)


def test_server_shutdown_and_close_stop_hardware_once(monkeypatch):
    """One server owns one idempotent hardware lifecycle shutdown callback."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    calls = []
    monkeypatch.setattr(
        monitor_server.hardware_init,
        "shutdown",
        lambda: calls.append("shutdown"),
    )
    httpd = monitor_server.create_server(port=0)
    thread = _serve_httpd(httpd)

    httpd.shutdown()
    httpd.server_close()
    thread.join(timeout=2)

    assert calls == ["shutdown"]


def test_multiple_servers_do_not_stop_global_hardware_lifecycle_twice(monkeypatch):
    """Separate test servers share one process-level hardware shutdown."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    calls = []
    monkeypatch.setattr(
        monitor_server.hardware_init,
        "shutdown",
        lambda: calls.append("shutdown"),
    )
    servers = [monitor_server.create_server(port=0) for _ in range(2)]
    threads = [_serve_httpd(httpd) for httpd in servers]

    for httpd in servers:
        httpd.shutdown()
        httpd.server_close()
    for thread in threads:
        thread.join(timeout=2)

    assert calls == ["shutdown"]


def test_hardware_shutdown_waits_for_final_server_owner(monkeypatch):
    """Global telemetry remains active until every owning server is released."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    calls = []
    monkeypatch.setattr(
        monitor_server.hardware_init,
        "shutdown",
        lambda: calls.append("shutdown"),
    )
    first = monitor_server.create_server(port=0)
    second = monitor_server.create_server(port=0)
    first_thread = _serve_httpd(first)
    second_thread = _serve_httpd(second)

    first.shutdown()
    first.server_close()
    assert calls == []

    first.shutdown()
    first.server_close()
    assert calls == []

    second.shutdown()
    second.server_close()
    assert calls == ["shutdown"]

    second.shutdown()
    second.server_close()
    assert calls == ["shutdown"]

    first_thread.join(timeout=2)
    second_thread.join(timeout=2)


def test_production_runner_uses_monitor_http_server(monkeypatch):
    """The production bind path constructs the lifecycle-aware HTTP server."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    monkeypatch.setattr(monitor_server, "_resolve_bind_host", lambda: "127.0.0.1")

    runner = monitor_server._MonitorServerRunner(
        monitor_server.MonitorHandler,
        monitor_server.SERVER_NAME,
        monitor_server.PORT,
    )
    httpd = runner._create_server(0)

    try:
        assert isinstance(httpd, monitor_server._MonitorHTTPServer)
    finally:
        httpd.server_close()


def test_production_entry_closes_monitor_server_in_finally(monkeypatch):
    """The production entry serves then releases its server lifecycle once."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    calls = []

    class FakeHTTPServer:
        def serve_forever(self):
            calls.append("serve_forever")

        def shutdown(self):
            calls.append("shutdown")

        def server_close(self):
            calls.append("server_close")

    class FakeRunner:
        def __init__(self, *_):
            self._server = FakeHTTPServer()

        def start(self):
            self._server.serve_forever()

    monkeypatch.setattr(monitor_server, "_MonitorServerRunner", FakeRunner)

    monitor_server.run_server()

    assert calls == ["serve_forever", "shutdown", "server_close"]


def test_runner_signal_shutdown_runs_outside_signal_thread(monkeypatch):
    """Signal shutdown is delegated so it cannot block ``serve_forever``'s thread."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    registered_handlers = {}
    shutdown_started = threading.Event()
    shutdown_finished = threading.Event()
    permit_shutdown_return = threading.Event()
    shutdown_threads = []

    class FakeHTTPServer:
        def shutdown(self):
            shutdown_threads.append(threading.current_thread())
            shutdown_started.set()
            permit_shutdown_return.wait(timeout=1)
            shutdown_finished.set()

    runner = monitor_server._MonitorServerRunner(
        monitor_server.MonitorHandler,
        monitor_server.SERVER_NAME,
        monitor_server.PORT,
    )
    runner._server = FakeHTTPServer()
    monkeypatch.setattr(
        monitor_server.signal,
        "signal",
        lambda sig, handler: registered_handlers.setdefault(sig, handler),
    )

    runner._register_signals()

    signal_thread = threading.current_thread()
    start = time.monotonic()
    try:
        registered_handlers[signal.SIGTERM](signal.SIGTERM, None)
    finally:
        elapsed = time.monotonic() - start
        permit_shutdown_return.set()

    assert elapsed < 0.1
    assert shutdown_started.wait(timeout=1)
    assert shutdown_threads[0] is not signal_thread
    assert shutdown_finished.wait(timeout=1)


def test_runner_start_serves_then_entry_finally_closes_server(monkeypatch):
    """Once serving returns, the entrypoint closes and releases the owned server."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    calls = []

    class FakeHTTPServer:
        server_address = ("127.0.0.1", 18098)

        def serve_forever(self):
            calls.append("serve_forever")

        def shutdown(self):
            calls.append("shutdown")

        def server_close(self):
            calls.extend(("server_close", "lifecycle_release"))

    fake_server = FakeHTTPServer()

    class FakeRunner(monitor_server._MonitorServerRunner):
        def _create_server(self, _port):
            return fake_server

        def _report_port(self):
            calls.append("report_port")

        def _register_signals(self):
            calls.append("register_signals")

        def _print_banner(self, _port):
            calls.append("print_banner")

    monkeypatch.setattr(monitor_server, "_MonitorServerRunner", FakeRunner)
    monkeypatch.setattr(monitor_server.sys, "argv", ["monitor", "--port", "0", "--no-browser"])
    monkeypatch.setattr(
        monitor_server.DXServer,
        "_parse_args",
        lambda _self: pytest.fail("Monitor runner must not reuse DXServer.start internals"),
    )

    monitor_server.run_server()

    assert calls == [
        "report_port",
        "register_signals",
        "print_banner",
        "serve_forever",
        "shutdown",
        "server_close",
        "lifecycle_release",
    ]


def test_sse_sends_unavailable_telemetry_payload(monkeypatch):
    """SSE sends unavailable and telemetry-error payloads instead of dropping them."""
    monitor_server = _hardware_free_monitor_server(monkeypatch)
    payload = {
        "available": False,
        "source_mode": "unavailable",
        "npus": [],
        "ts": 42.0,
        "telemetry": {
            "available": False,
            "source_mode": "unavailable",
            "diagnostics": ["Telemetry snapshot failed"],
            "error": "Telemetry snapshot failed",
        },
    }
    stale_payload = {
        "available": True,
        "source_mode": "stale",
        "npus": [{"id": 0}],
        "ts": 43.5,
        "telemetry": {
            "available": True,
            "source_mode": "stale",
            "diagnostics": ["Telemetry cache is stale"],
        },
    }
    sent = []
    sleeps = []
    samples = iter([payload, stale_payload])

    monkeypatch.setattr(monitor_server, "get_hw", lambda: next(samples))
    monkeypatch.setattr(monitor_server.time, "sleep", sleeps.append)
    monkeypatch.setattr(monitor_server.MonitorHandler, "start_sse", lambda self: None)
    monkeypatch.setattr(monitor_server.MonitorHandler, "end_sse", lambda self: None)
    monkeypatch.setattr(
        monitor_server.MonitorHandler,
        "send_sse_data",
        lambda self, data: sent.append(data) or len(sent) == 1,
    )

    handler = object.__new__(monitor_server.MonitorHandler)
    handler._sse()

    assert sent == [payload, stale_payload]
    assert sleeps == [1.5]

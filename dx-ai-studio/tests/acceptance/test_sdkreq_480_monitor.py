"""SDKREQ-480 [Monitor] NPU and system monitoring — DX Monitor inside a real ./launcher.sh studio.

On a board with a DX-M1 the telemetry is real (no mock banner). The no-NPU and degraded-connection
states are shown by answering the monitor's own API calls from the test.
"""
from __future__ import annotations

import json

from tests.acceptance.conftest import http_get, module_frame, wait_home
from tests.acceptance.hardware import need

RANGES = ["tr-rt", "tr-5m", "tr-15m", "tr-30m", "tr-1h", "tr-all"]
MODES = ["cm-temp", "cm-volt", "cm-clock", "cm-dram", "cm-util", "cm-ctemp", "cm-cpu", "cm-mem", "cm-cpucores", "cm-all"]


def _monitor(pages, page=None):
    page = page or pages.new("/")
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('dx_monitor')")
    return page, module_frame(page, "dx_monitor", ready="#chart-mode-btns")


def test_six_time_ranges_switch_the_chart_window(pages):
    page, frame = _monitor(pages)
    ids = frame.locator("#time-range-btns button").evaluate_all("els => els.map(e => e.id)")
    assert ids == RANGES, ids
    for rid in RANGES[1:] + RANGES[:1]:
        frame.locator(f"#{rid}").click()
        frame.wait_for_function("(id) => document.getElementById(id).classList.contains('active')", arg=rid)
        assert frame.locator("#time-range-btns button.active").count() == 1


def test_chart_modes_for_npu_cpu_and_view_all_update_live(pages):
    page, frame = _monitor(pages)
    ids = frame.locator("#chart-mode-btns button").evaluate_all("els => els.map(e => e.id)")
    assert ids == MODES, ids
    for mid in ("cm-cpu", "cm-mem", "cm-cpucores", "cm-temp", "cm-all"):
        frame.locator(f"#{mid}").click()
        frame.wait_for_function("(id) => document.getElementById(id).classList.contains('active')", arg=mid)
        frame.locator("#chart-area canvas").first.wait_for(state="attached", timeout=15000)
    n0 = frame.evaluate("() => S.rtData.length")
    frame.wait_for_function("(n) => S.rtData.length > n + 1", arg=n0, timeout=20000)


def test_npu_topology_system_info_and_runtime_event_log(pages):
    page, frame = _monitor(pages)
    frame.locator("#npu-topo").wait_for(state="attached", timeout=15000)
    frame.wait_for_function("() => document.querySelectorAll('#sysinfo-table tbody tr').length >= 10", timeout=30000)
    assert frame.locator("#event-log").count() == 1 and frame.locator("#event-count").count() == 1
    assert frame.locator("#npu-status-label").inner_text().strip()


def test_real_npu_telemetry_streams_over_sse_without_a_mock_banner(pages, studio):
    need("npu")
    status, headers, body = http_get(studio.base + "/dx_monitor/api/hw_status", headers={"Sec-Fetch-Dest": "empty"})
    hw = json.loads(body)
    assert hw.get("npus"), hw
    assert (hw.get("telemetry") or {}).get("source_mode") == "real", hw.get("telemetry")
    assert not hw.get("mock")
    page, frame = _monitor(pages)
    frame.wait_for_function("() => /\\d+\\s*NPU/.test(document.getElementById('npu-status-label').textContent)",
                            timeout=30000)
    assert not frame.locator("#mock-banner").is_visible()
    assert not frame.locator("#sse-status").is_visible(), "the connection indicator shows only when degraded"
    assert not frame.locator("#telemetry-status").is_visible()


def test_a_broken_live_connection_falls_back_to_polling_and_says_so(pages):
    page = pages.new(None)
    page.route("**/api/hw_stream*", lambda route: route.abort())
    page.goto(pages.studio.base + "/", wait_until="domcontentloaded")
    page, frame = _monitor(pages, page)
    frame.locator("#sse-status").wait_for(state="visible", timeout=30000)
    assert "Polling" in frame.locator("#sse-status").inner_text()


def test_without_npu_telemetry_the_page_says_so_and_mock_mode_is_labelled(pages):
    page = pages.new(None)
    state = {"mode": "unavailable"}

    def hw_status(route):
        resp = route.fetch()
        body = resp.json()
        body["npus"] = []
        if state["mode"] == "mock":
            body["mock"] = True
            body["telemetry"] = {**(body.get("telemetry") or {}), "source_mode": "mock", "status": "mock"}
        else:
            body["mock"] = False
            body["telemetry"] = {"source_mode": "unavailable", "status": "unavailable",
                                 "diagnostic": "no /dev/dxrt* device"}
        route.fulfill(response=resp, body=json.dumps(body))

    page.route("**/api/hw_stream*", lambda route: route.abort())
    page.route("**/api/hw_status*", hw_status)
    page.goto(pages.studio.base + "/", wait_until="domcontentloaded")
    page, frame = _monitor(pages, page)
    frame.wait_for_function(
        "() => { const t = document.getElementById('telemetry-status'); return t && t.offsetParent && "
        "/NPU telemetry unavailable/.test(t.textContent); }", timeout=30000)
    assert not frame.locator("#mock-banner").is_visible()
    state["mode"] = "mock"
    frame.locator("#mock-banner").wait_for(state="visible", timeout=30000)

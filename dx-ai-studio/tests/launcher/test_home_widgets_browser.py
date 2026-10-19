"""The widgets render from real data.

Device and catalog are pinned with fixtures: the test harness starts only the launcher, so there is no
monitor or zoo, and left to the environment a check meant for 'device present' would check 'absent'.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_SEEN = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}")
_QUIET = """() => {
  const t = window._dxTutorial;
  if (t) { try { t.hideTOC && t.hideTOC(); t.stop && t.stop(); } catch (e) {} }
  document.querySelectorAll('.dxt-toc,.dxt-overlay,.dxt-tooltip,.dxt-toc-backdrop').forEach(e => e.remove());
}"""

HW_LIVE = {"available": True, "count": 1, "npus": [{
    "id": 0, "cores": 3, "temperatures": [40.0, 41.0, 42.0], "temp_avg": 41.0,
    "clock_avg": 1000.0, "power_est_mW": 375.0, "utilization": [10.0, 55.0, 90.0]}]}
HW_OFF = {"available": False, "count": 0, "npus": []}


def _m(mid, task, fps):
    return {"id": mid, "name": mid, "display": {"task": task},
            "performance": {"fps": fps} if fps is not None else {}}


CATALOG = {"models": [
    _m("ssd_mobilenet", "object_detection", 1847),     # faster, but not the headline
    _m("yolo26n", "object_detection", 321),
    _m("yolo26s", "object_detection", 203),
    _m("yolo26n_seg", "instance_segmentation", 240),
    # no pose model: must be skipped
    _m("yolo26n_cls", "classification", 3695),
    _m("yolo26n_obb", "obb_detection", 104),
    _m("yolo26_depth_n", "depth_estimation", None),     # no fps: skipped
]}


@pytest.fixture(scope="module")
def server():
    srv, port = start_module_server("launcher")
    yield port
    srv.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _open(browser, port, hw):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script(_SEEN)
    page = ctx.new_page()
    page.route("**/dx_monitor/api/hw_stream", lambda route, *_: route.abort())
    page.route("**/dx_monitor/api/hw_status", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(hw)))
    page.route("**/zoo/api/catalog", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(CATALOG)))
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.wait_for_selector("#studioGrid .orbital-card", state="visible")
    page.evaluate(_QUIET)
    return ctx, page


@pytest.fixture()
def live(browser, server):
    ctx, page = _open(browser, server, HW_LIVE)
    page.wait_for_function("() => document.querySelectorAll('#homeCores .dev-core').length === 3", timeout=8000)
    yield page
    ctx.close()


def test_one_bar_per_core_and_their_heights_follow_utilisation(live):
    heights = live.evaluate("""() => [...document.querySelectorAll('#homeCores .dev-core i')]
      .map(e => e.getBoundingClientRect().height)""")
    assert heights[0] < heights[1] < heights[2], heights
    assert abs(heights[2] / heights[1] - 90 / 55) < 0.15, heights


def test_the_line_reads_temperature_clock_and_power(live):
    line = live.inner_text("#homeDeviceLine")
    assert "41°C" in line and "1,000 MHz" in line and "375 mW" in line, line


def test_a_live_device_is_quiet(live):
    assert not live.evaluate("() => document.getElementById('homeDevice').classList.contains('is-off')")


def test_a_missing_device_turns_the_widget_off(browser, server):
    ctx, page = _open(browser, server, HW_OFF)
    try:
        page.wait_for_function("() => document.getElementById('homeDevice').classList.contains('is-off')", timeout=8000)
        assert page.inner_text("#heroDeviceChip").strip() == "No DX-M1 connected"
        assert page.locator("#homeCores .dev-core").count() == 0
    finally:
        ctx.close()


def _headline(page):
    return page.evaluate("() => [document.getElementById('homeProofFps').textContent.trim(),"
                         " document.getElementById('homeProofModel').textContent.trim()]")


def test_the_headline_is_yolo26n_not_the_fastest_model(live):
    live.wait_for_function("() => document.getElementById('homeProofFps').textContent.trim() !== ''", timeout=8000)
    fps, model = _headline(live)
    assert fps == "321", (fps, model)
    assert "YOLO26n" in model and "Object Detection" in model, model


def test_the_headline_moves_on_and_skips_what_is_not_measured(live):
    live.wait_for_function("() => document.getElementById('homeProofFps').textContent.trim() !== ''", timeout=8000)
    seen = [_headline(live)[0]]
    for _ in range(4):
        live.evaluate("() => window.DXLauncher._rotateHeadline()")
        seen.append(_headline(live)[0])
    # object 321 → seg 240 → (no pose) cls 3,695 → obb 104 → (depth has no fps) back to the start
    assert seen == ["321", "240", "3,695", "104", "321"], seen
    dots = live.locator("#homeProofDots > *").count()
    assert dots == 4, "점은 실제로 보여줄 task 수만큼"


def test_the_count_links_to_benchmark(live):
    live.wait_for_function("() => document.getElementById('measuredCount').textContent.trim() !== ''", timeout=8000)
    live.evaluate("() => { window.DXLauncher.launch = (app) => { window.__launched = app; }; }")
    live.click("#measuredCount")
    assert live.evaluate("() => window.__launched") == "benchmark"


def test_the_device_widget_opens_monitor(live):
    live.evaluate("() => { window.DXLauncher.launch = (app) => { window.__launched = app; }; }")
    live.click("#homeDevice")
    assert live.evaluate("() => window.__launched") == "dx_monitor"
    live.evaluate("() => { window.__launched = null; }")
    live.focus("#homeDevice")
    live.keyboard.press("Enter")
    assert live.evaluate("() => window.__launched") == "dx_monitor"

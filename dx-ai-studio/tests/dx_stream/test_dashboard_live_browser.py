"""Stream Dashboard — names the running demo and fills in FPS and NPU usage.

The table must not wait on perf fields the server never sends, and the Pipeline Status card must follow the run.
Server responses are fixed by route (demo 4 running over MJPEG, ~25 frames per second, NPU 40%).
"""
from __future__ import annotations

import json
import time

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

DEMOS = {"demos": [{"id": 4, "name_en": "Pose Estimation", "name_ko": "포즈 추정", "category": "pose_estimation"}]}
T0 = time.time()


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_stream")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');")
    pg = ctx.new_page()

    def _json(route, body):
        route.fulfill(status=200, content_type="application/json", body=json.dumps(body))

    pg.route("**/api/pipeline/status", lambda r, *_: _json(r, {"running": True, "pipeline_id": "mjpeg-demo-4",
                                                               "output_mode": "mjpeg", "demo_id": 4}))
    pg.route("**/api/stream/stats", lambda r, *_: _json(r, {"mode": "mjpeg", "streaming": True,
                                                            "frames": int((time.time() - T0) * 25)}))
    pg.route("**/dx_monitor/api/hw_status", lambda r, *_: _json(r, {"npus": [{"utilization": [40.0, 40.0, 40.0]}]}))
    pg.route("**/api/demos", lambda r, *_: _json(r, DEMOS))
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.evaluate("() => DXStream.nav('dashboard')")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def test_the_running_demo_is_named(page):
    page.wait_for_function("() => (document.querySelector('#pipeline-overview .pipe-live-name')||{}).textContent === 'Pose Estimation'",
                           timeout=10000)
    assert "MJPEG" in page.inner_text("#pipeline-overview")
    assert page.inner_text("#pipeline-status").strip() == "Running"


def test_fps_and_npu_fill_in(page):
    page.wait_for_function("() => /^\\d+$/.test(document.getElementById('perf-fps-current').textContent.trim())", timeout=10000)
    fps = int(page.inner_text("#perf-fps-current"))
    assert 15 <= fps <= 35, fps
    page.wait_for_function("() => document.getElementById('perf-npu-current').textContent.trim() === '40%'", timeout=10000)


def test_rows_without_a_source_are_gone(page):
    assert page.locator("#perf-latency-current").count() == 0
    assert page.locator("#perf-e2e-current").count() == 0


def test_the_name_follows_the_language(page):
    page.evaluate("() => DXI18n.setLang('ko')")
    try:
        page.wait_for_function("() => (document.querySelector('#pipeline-overview .pipe-live-name')||{}).textContent === '포즈 추정'",
                               timeout=10000)
    finally:
        page.evaluate("() => DXI18n.setLang('en')")

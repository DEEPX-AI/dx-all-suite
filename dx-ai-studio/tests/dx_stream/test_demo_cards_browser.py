"""dx_stream Demo Launcher — a result stage plus cards to pick from.

The stage is shared with App Run Demo: the chosen demo (Playback · RTSP · Start) opens at the top, the video plays in
the same place so no scrolling is needed, and the figures sit in the right panel.

/api/demos and the start and video APIs are fixed by fixtures.
"""
from __future__ import annotations

import base64
import json

import pytest

pytest.importorskip("playwright.sync_api")
from tests.server_helpers import start_module_server  # noqa: E402

DEMOS = [
    {"id": 0, "name_en": "Object Detection", "category": "object_detection", "model": "yolo26n.dxnn",
     "description_en": "Basic object detection with YOLOv26n", "pipeline_type": "standard", "available": True,
     "runtime_script": "run_detection.sh", "availability": {"available": True}},
    {"id": 1, "name_en": "Multi-Stream", "category": "multi_stream", "model": "YoloV5S_PPU.dxnn",
     "description_en": "Four channels at once", "pipeline_type": "multi", "available": False,
     "availability": {"available": False, "reason_items": [{"code": "missing_model", "path": "YoloV5S_PPU.dxnn"}]}},
    {"id": 2, "name_en": "RTSP Detection", "category": "object_detection", "model": "yolo26n.dxnn",
     "description_en": "Detection on an RTSP camera", "pipeline_type": "rtsp", "available": True,
     "availability": {"available": True}},
]
# 4×2 png — only checks that a frame lands in the MJPEG slot and its resolution reaches the panel
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAQAAAACCAYAAAB/qH1jAAAAEUlEQVR42mNk+M9QzwAEjDAGACCDAv8cI7IoAAAAAElFTkSuQmCC")


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_stream")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dxStreamPlaybackMode','remote');")
    pg = ctx.new_page()
    pg.starts = []
    frames = {"n": 0}
    playing = {"id": None}      # what the fake server plays — the page's shared poll asks for it

    def _start(route, request):
        pg.starts.append((request.url.split("/api/demos/")[1], json.loads(request.post_data or "{}")))
        playing["id"] = int(request.url.split("/api/demos/")[1].split("/")[0])
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True, "output_mode": "mjpeg"}))

    def _stop(route, *_):
        playing["id"] = None
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True}))

    def _status(route, *_):
        pid = playing["id"]
        route.fulfill(status=200, content_type="application/json", body=json.dumps(
            {"running": pid is not None, "pipeline_id": None if pid is None else f"mjpeg-demo-{pid}",
             "output_mode": None if pid is None else "mjpeg", "demo_id": pid}))

    def _stats(route, *_):
        frames["n"] += 30
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"frames": frames["n"]}))

    pg.route("**/api/demos", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(DEMOS)))
    pg.route("**/api/demos/*/start", _start)
    pg.route("**/api/demos/*/stop", _stop)
    pg.route("**/api/pipeline/status", _status)
    pg.route("**/api/stream/mjpeg*", lambda route, *_: route.fulfill(status=200, content_type="image/png", body=PNG))
    pg.route("**/api/stream/stats", _stats)
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.click('.dx-tab[data-page="demo"]')
    pg.wait_for_selector('#demo-root .dds-card[data-id="2"]', timeout=10000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def test_cards_show_the_task_symbol_and_the_first_ready_demo_is_open(page):
    icons = page.evaluate("""() => [...document.querySelectorAll('#demo-root .dds-card')].map(c =>
      c.querySelector('.dds-task use').getAttribute('href').split('#')[1])""")
    assert icons == ["task-object_detection", "dashboard", "task-object_detection"], icons
    assert page.inner_text("#demo-root .dds-stage .dds-title").strip() == "Object Detection"
    assert page.locator("#demo-root .dds-card button:not(.dds-setup):not(.dds-cpick)").count() == 0


def test_filters_come_from_the_demos(page):
    keys = page.evaluate("[...document.querySelectorAll('#demo-root .dds-filter button')].map(b => b.dataset.key)")
    assert keys == ["all", "object_detection", "multi_stream"], keys


def test_playback_is_a_stage_option_and_rtsp_only_for_rtsp_demos(page):
    on = page.evaluate("document.querySelector('.dds-stage [data-axis-row=\"playback\"] button.is-on').dataset.mode")
    assert on == "remote"
    assert page.locator(".dds-stage input.demo-rtsp-input").count() == 0
    page.click(".dds-card[data-id='2']")
    assert page.locator(".dds-stage #rtsp-url-2").count() == 1
    page.click(".dds-card[data-id='0']")
    assert "run_detection.sh" in page.text_content(".dds-stage #demo-perf-cmd")


def test_a_not_ready_card_gives_one_short_reason(page):
    reason = page.locator(".dds-card[data-id='1'] .dds-reason")
    assert reason.inner_text().strip() == "Model not installed"
    assert "YoloV5S_PPU.dxnn" in reason.get_attribute("title")
    assert page.inner_text(".dds-card[data-id='1'] .dds-setup").strip() == "Set up"


def test_start_plays_on_the_stage_and_stop_returns_to_the_preview(page):
    page.starts.clear()
    page.click(".dds-card[data-id='0']")
    page.click(".dds-stage #start-demo-0")
    page.wait_for_selector(".dds-stage .dds-media #demo-video-section #mjpeg-stream", timeout=10000)
    assert page.starts[0][0].startswith("0/start") and page.starts[0][1].get("forceMjpeg") is True
    assert page.evaluate("document.querySelector('.dds-state').dataset.kind") == "running"
    assert page.evaluate("document.querySelector('.dds-card[data-id=\"0\"]').classList.contains('is-running')")
    page.wait_for_function("() => document.getElementById('demo-resolution-info')?.textContent === '4×2'", timeout=6000)
    page.wait_for_function("() => /\\d/.test(document.getElementById('demo-fps-info')?.textContent || '')", timeout=6000)
    assert page.inner_text("#demo-model-info") == "yolo26n"
    # Viewing another card parks the video box out of sight — it stays in the document (webrtc-client finds it by id)
    page.click(".dds-card[data-id='2']")
    assert page.evaluate("document.getElementById('demo-video-section').parentNode.id") == "demo-video-park"
    page.click(".dds-card[data-id='0']")
    assert page.evaluate("document.getElementById('demo-video-section').closest('.dds-media') !== null")
    page.click(".dds-stage #btn-demo-stop")
    page.wait_for_function("() => document.querySelector('.dds-state').dataset.kind === 'ready'", timeout=6000)
    assert page.evaluate("document.getElementById('demo-video-section').parentNode.id") == "demo-video-park"
    assert page.locator(".dds-card.is-running").count() == 0

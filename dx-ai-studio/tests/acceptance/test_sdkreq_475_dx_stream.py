"""SDKREQ-475 [DX Stream] pipelines and demos — Studio's Stream module inside a real ./launcher.sh studio.

The live demo runs on the NPU through GStreamer and needs DX Stream's own sample models; when Stream setup
has not installed them the AC is NOT RUN with the count it reports. Starting a pipeline is answered by the
test (its UI and request are what the AC is about); the demo AC covers a real run.
"""
from __future__ import annotations

import json
import time

import pytest

from tests.acceptance.conftest import http_get, module_frame, wait_home
from tests.acceptance.hardware import need

TABS = ["setup", "dashboard", "demo", "pipeline", "models", "elements", "custom", "reference"]
TABS_KO = ["설치", "대시보드", "데모 실행", "파이프라인 빌더", "모델 카탈로그", "요소 레퍼런스", "커스텀 라이브러리", "레퍼런스"]


def _stream(pages, lang="en"):
    page = pages.new("/", lang=lang)
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('stream')")
    return page, module_frame(page, "stream", ready=".dx-tab[data-page]")


def _nav(frame, page_id):
    frame.evaluate("(p) => DXStream.nav(p)", page_id)
    frame.locator(f"#page-{page_id}.active").wait_for(timeout=15000)


def _api(studio, path):
    return json.loads(http_get(studio.base + "/stream" + path, timeout=60, headers={"Sec-Fetch-Dest": "empty"})[2])


def test_eight_tabs_open_on_the_dashboard_and_switch_pages(pages):
    page, frame = _stream(pages, lang="ko")
    tabs = frame.locator(".dx-tab[data-page]")
    assert tabs.evaluate_all("els => els.map(e => e.dataset.page)") == TABS
    assert [t.strip() for t in tabs.evaluate_all("els => els.map(e => e.textContent)")] == TABS_KO
    frame.locator("#page-dashboard.active").wait_for(timeout=15000)
    for pid in TABS:
        _nav(frame, pid)


def test_setup_steps_environment_check_and_dashboard_cards(pages):
    page, frame = _stream(pages)
    _nav(frame, "setup")
    frame.locator("#setup-steps [data-step]").first.wait_for(timeout=30000)
    assert frame.locator("#setup-steps [data-step]").evaluate_all("els => els.map(e => e.dataset.step)") == [
        "stream-deps", "runtime-deps", "driver", "build", "download-models", "webrtc-deps"]
    frame.locator("#setup-env-tbody tr").nth(5).wait_for(state="attached", timeout=30000)
    assert frame.locator("#stream-diag-run-btn").count() == 1
    _nav(frame, "dashboard")
    for card in ("npu", "gstreamer", "models", "videos", "build"):
        frame.locator(f"#stat-{card}").wait_for(state="attached", timeout=15000)
    frame.wait_for_function("() => !/^\\s*(--|…)?\\s*$/.test(document.querySelector('#stat-npu').innerText)",
                            timeout=30000)
    assert frame.locator("#quick-launch-grid .quick-card").count() == 3
    assert frame.locator("#perf-table tbody tr").count() == 2


def test_demo_cards_filter_by_category(pages):
    page, frame = _stream(pages)
    _nav(frame, "demo")
    frame.locator(".dds-card").first.wait_for(timeout=30000)
    keys = frame.locator(".dds-filter .dds-fbtn").evaluate_all("els => els.map(e => e.dataset.key)")
    assert len(keys) >= 2 and len(set(keys)) == len(keys), keys
    total = frame.locator(".dds-card").count()
    key = keys[-1]
    frame.locator(f'.dds-filter .dds-fbtn[data-key="{key}"]').click()
    frame.wait_for_function("(n) => [...document.querySelectorAll('.dds-card')].filter(c => c.offsetParent).length < n",
                            arg=total, timeout=10000)
    shown = frame.locator(".dds-card:visible").count()
    assert 0 < shown < total
    frame.locator(f'.dds-filter .dds-fbtn[data-key="{keys[0]}"]').click()
    frame.wait_for_function("(n) => [...document.querySelectorAll('.dds-card')].filter(c => c.offsetParent).length === n",
                            arg=total, timeout=10000)


def test_a_demo_runs_live_on_the_npu_and_stops(pages, studio):
    need("npu")
    demos = _api(studio, "/api/demos")
    ready = [d for d in demos if d.get("available")]
    if not ready:
        st = _api(studio, "/api/status")
        models = st.get("models", {})
        pytest.skip(f"NOT RUN: no DX Stream demo is ready on this board (Stream sample models "
                    f"{models.get('installed')}/{models.get('total')} installed; DX Stream > Setup > download-models)")
    page, frame = _stream(pages)
    _nav(frame, "demo")
    demo = ready[0]
    frame.locator(f'.dds-card[data-id="{demo["id"]}"]').click()
    frame.locator(f'#start-demo-{demo["id"]}').click()
    frame.wait_for_function(
        "() => { const v = document.getElementById('webrtc-video'); const m = document.getElementById('mjpeg-stream');"
        " return (v && v.offsetParent && v.readyState >= 2) || (m && m.offsetParent && m.naturalWidth > 0); }",
        timeout=120000)
    frame.wait_for_function("() => /\\d/.test(document.getElementById('demo-fps-info')?.textContent || '')",
                            timeout=60000)
    frame.locator("#btn-demo-stop").click()
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and _api(studio, "/api/pipeline/status").get("running"):
        time.sleep(1)


def test_pipeline_builder_adds_and_connects_elements_and_runs(pages):
    page, frame = _stream(pages)
    sent = {}

    def run(route):
        sent["body"] = json.loads(route.request.post_data or "{}")
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True, "status": "running"}))

    page.route("**/api/pipeline/run", run)
    _nav(frame, "pipeline")
    frame.locator("#palette-list .palette-item").first.wait_for(timeout=30000)
    frame.evaluate("() => DXStream._pipeState.nodes.length && DXStream.clearPipeline && DXStream.clearPipeline(true)")
    target = frame.locator(".canvas-container")
    for name, x in (("urisourcebin", 200), ("decodebin", 520)):
        frame.locator(f'#palette-list .palette-item[data-element="{name}"]').drag_to(
            target, target_position={"x": x, "y": 200})
    frame.wait_for_function("() => DXStream._pipeState.nodes.length === 2", timeout=10000)
    ports = frame.evaluate("""() => { const st = DXStream._pipeState; const c = document.getElementById('pipeline-canvas');
        const r = c.getBoundingClientRect(); const [a, b] = st.nodes;
        return { ox: r.left + st.offsetX + (a.x + _NODE_W) * st.zoom, oy: r.top + st.offsetY + (a.y + _NODE_H / 2) * st.zoom,
                 ix: r.left + st.offsetX + b.x * st.zoom, iy: r.top + st.offsetY + (b.y + _NODE_H / 2) * st.zoom }; }""")
    box = page.locator('iframe.module-iframe[data-app="stream"]').bounding_box()
    page.mouse.move(box["x"] + ports["ox"], box["y"] + ports["oy"])
    page.mouse.down()
    page.mouse.move(box["x"] + ports["ix"], box["y"] + ports["iy"], steps=12)
    page.mouse.up()
    frame.wait_for_function("() => DXStream._pipeState.edges.length >= 1", timeout=10000)
    frame.wait_for_function("() => /urisourcebin.*!.*decodebin/.test(document.getElementById('pipeline-command-output').textContent)",
                            timeout=10000)
    frame.locator("#btn-pipeline-run").click()
    for _ in range(40):
        if sent:
            break
        page.wait_for_timeout(250)
    assert len(sent.get("body", {}).get("nodes", [])) == 2 and sent["body"].get("edges"), sent


def test_catalog_element_reference_custom_library_and_reference_pages_load(pages):
    page, frame = _stream(pages)
    _nav(frame, "models")
    card = frame.locator("#models-grid .card").first
    card.wait_for(timeout=30000)
    card.click()
    frame.locator("#model-detail-modal[open]").wait_for(timeout=15000)
    frame.locator("#model-detail-modal[open]").press("Escape")
    _nav(frame, "elements")
    frame.locator(".element-card").first.wait_for(timeout=30000)
    total = frame.locator(".element-card").count()
    frame.locator("#elements-search").fill("dx")
    frame.wait_for_function("(n) => document.querySelectorAll('.element-card').length < n", arg=total, timeout=10000)
    frame.locator(".element-card").first.click()
    frame.locator("#element-detail").wait_for(state="visible", timeout=10000)
    _nav(frame, "custom")
    frame.locator("#custom-lib-grid").wait_for(state="attached", timeout=15000)
    _nav(frame, "reference")
    topic = frame.locator(".ref-topic-card[data-ref-id]").first
    topic.wait_for(timeout=15000)
    assert frame.locator(".ref-topic-card[data-ref-id]").count() >= 10
    topic.click()
    frame.wait_for_function("() => (document.getElementById('ref-expand')?.innerText || '').trim().length > 50",
                            timeout=10000)

"""DX Stream — controls that did nothing or threw (real-hardware audit 2026-10-10).

- Pipeline Builder palette search: the box was there (and the tutorial points at it) but no code
  listened to it.
- Canvas context menu "Clear All" called DXStream.pipelineClear, which does not exist: TypeError.
- Element Reference detail: the long description, key features, pipeline hint, example config and
  related elements are rendered into #element-detail-extra — an element the page never had.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_stream")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');"
                        "localStorage.removeItem('dxStreamPipelineDraft');")
    pg = ctx.new_page()
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _visible_palette(page):
    return page.evaluate("[...document.querySelectorAll('#palette-list .palette-item')]"
                         ".filter(e => e.offsetParent !== null).map(e => e.dataset.element)")


def test_palette_search_narrows_the_elements(page):
    page.evaluate("() => DXStream.nav('pipeline')")
    page.wait_for_selector("#palette-list .palette-item", timeout=10000)
    everything = _visible_palette(page)
    page.fill("#palette-search", "DXINFER")
    found = _visible_palette(page)
    assert "DxInfer" in found, found                     # matched by name (or by description)
    assert len(found) < len(everything) and "urisourcebin" not in found
    page.fill("#palette-search", "")
    assert _visible_palette(page) == everything


def test_context_menu_clear_all_empties_the_canvas(page):
    page.evaluate("() => DXStream.nav('pipeline')")
    page.wait_for_selector("#pipeline-canvas", timeout=10000)
    page.evaluate("""() => { const st = DXStream._pipeState;
        st.nodes = [{id: 'n1', type: 'queue', name: 'queue', category: 'utility', x: 40, y: 40, properties: {}}];
        st.edges = []; }""")
    box = page.locator("#pipeline-canvas").bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, button="right")
    page.locator(".ctx-menu-item", has_text="Clear All").click()
    page.click("#confirm-modal-ok")
    page.wait_for_timeout(300)
    assert page.evaluate("DXStream._pipeState.nodes.length") == 0
    assert not [e for e in page.errors if "pipelineClear" in e], page.errors


def test_element_detail_shows_the_long_description_and_features(page):
    page.evaluate("() => DXStream.nav('elements')")
    page.wait_for_selector("#elements-grid .element-card", timeout=10000)
    name = page.evaluate("""() => (DXStream._allElements.find(e => (e.key_features || []).length
                               && (e.long_description_en || e.long_description_ko)) || {}).name""")
    assert name, "the element catalog has rich details to show"
    page.evaluate(f"() => DXStream.showElementDetail({name!r})")
    extra = page.locator("#element-detail-extra")
    assert extra.count() == 1
    assert extra.locator(".element-feature-list li").count() >= 1


def test_element_detail_headings_follow_the_language(page):
    page.evaluate("() => DXI18n.setLang('ja')")
    try:
        page.evaluate("() => DXStream.nav('elements')")
        page.wait_for_selector("#elements-grid .element-card", timeout=10000)
        page.evaluate("() => DXStream.showElementDetail('DxInfer')")
        text = page.inner_text("#element-detail-extra")
        assert "Key Features" not in text and "Related Elements" not in text, text[:200]
        # the body too: long description, features (data has six languages) and property descriptions
        assert "Runs a compiled .dxnn model" not in text, text[:200]
        assert "Executes inference from a .dxnn" not in text, text[:300]
        assert "Preprocess identifier" not in page.inner_text("#element-detail-props-tbody")
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


# ── Custom Library ────────────────────────────────────────────────────────────

def _json_route(page, pattern, status, body):
    import json
    page.route(pattern, lambda r, *_: r.fulfill(status=status, content_type="application/json", body=json.dumps(body)))


def test_library_names_are_text_not_markup(page):
    _json_route(page, "**/api/custom-library", 200,
                [{"name": "<img src=x onerror=window.__xss=1>", "built": False, "has_meson": True}])
    try:
        page.evaluate("() => DXStream.nav('custom')")
        page.wait_for_selector("#custom-lib-grid .card-title", timeout=10000)
        assert page.inner_text("#custom-lib-grid .card-title") == "<img src=x onerror=window.__xss=1>"
        assert page.evaluate("window.__xss") is None
        assert page.locator("#custom-lib-grid button[data-lib]").count() == 1
    finally:
        page.unroute("**/api/custom-library")


def test_a_refused_upload_does_not_start_a_build(page):
    builds = []
    page.route("**/api/custom-library/*/build", lambda r, *_: builds.append(r.request.url) or r.fulfill(status=200, body="{}"))
    _json_route(page, "**/api/custom-library/upload", 400,
                {"error": "bad_request", "message": "Custom library files must be text source (.c/.cpp/.h), not a binary file."})
    try:
        page.evaluate("() => DXStream.nav('custom')")
        page.fill("#custom-lib-name", "mylib")
        page.set_input_files("#custom-lib-files", files=[{"name": "a.cpp", "mimeType": "text/plain", "buffer": b"int x;"}])
        page.evaluate("() => DXStream.custom.upload()")
        page.wait_for_function("() => /not a binary file/.test(document.body.innerText)", timeout=5000)
        assert builds == []
    finally:
        page.unroute("**/api/custom-library/*/build")
        page.unroute("**/api/custom-library/upload")


def test_a_build_that_needs_sudo_asks_for_the_password(page):
    _json_route(page, "**/api/custom-library/*/build", 401,
                {"error": "need_sudo", "message": "Administrator (sudo) password is required to install the library."})
    try:
        page.evaluate("() => DXStream.nav('custom')")
        page.evaluate("() => { DXStream.custom.build('mylib'); }")
        page.wait_for_selector("#dx-input-modal-field[type=password]", state="visible", timeout=5000)
        page.keyboard.press("Escape")
    finally:
        page.unroute("**/api/custom-library/*/build")


def test_a_refused_model_upload_says_why(page):
    _json_route(page, "**/api/models/upload", 409,
                {"error": "conflict", "message": "A model named yolo.dxnn already exists"})
    try:
        page.evaluate("() => DXStream.nav('custom')")
        page.set_input_files("#model-upload-file", files=[{"name": "yolo.dxnn", "mimeType": "application/octet-stream", "buffer": b"DXNN"}])
        page.evaluate("() => DXStream.uploadModel()")
        page.wait_for_function("() => /already exists/.test(document.getElementById('model-upload-status').textContent)", timeout=5000)
        assert "conflict" not in page.inner_text("#model-upload-status")
    finally:
        page.unroute("**/api/models/upload")


# ── Setup survives leaving the tab / changing language ────────────────────────

def test_coming_back_to_setup_resumes_the_running_step(page):
    import json
    page.route("**/api/setup/status", lambda r, *_: r.fulfill(status=200, content_type="application/json", body=json.dumps(
        {"build": {"ok": True, "path": "/x/libgstdxstream.so"}, "download-models": {"ok": False, "total": 17, "installed": 3},
         "running": "download-models"})))
    page.route("**/api/setup/log*", lambda r, *_: r.fulfill(status=200, content_type="application/json", body=json.dumps(
        {"log": "Downloading model 3/17 ...\n", "done": False, "exit_code": None})))
    try:
        page.evaluate("() => DXStream.nav('dashboard')")
        page.evaluate("() => DXStream.nav('setup')")
        page.wait_for_function("() => /Downloading model 3\\/17/.test(document.body.innerText)", timeout=8000)
        assert page.locator("#setup-stop-btn").is_visible()
        assert page.evaluate("DXStream._setupRunning") is True
    finally:
        page.unroute("**/api/setup/status")
        page.unroute("**/api/setup/log*")
        page.evaluate("() => { if (DXStream._setupPollTimer) clearInterval(DXStream._setupPollTimer); DXStream._setupRunning = false; DXStream.nav('dashboard'); }")


def test_a_language_change_reloads_the_page_once(page):
    page.evaluate("() => DXStream.nav('models')")
    page.evaluate("""() => { window.__navs = 0; const real = DXStream.nav;
        DXStream.nav = function (p) { window.__navs++; return real.apply(this, arguments); }; }""")
    page.evaluate("() => DXI18n.setLang('ko')")
    page.wait_for_timeout(400)
    try:
        assert page.evaluate("window.__navs") == 1
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


# ── Demo start errors · quick launch · MJPEG fallback ─────────────────────────

def _demo(i, available):
    return {"id": i, "name_en": f"Demo {i}", "name_ko": f"데모 {i}", "category": "object_detection", "model": "m.dxnn",
            "available": available, "thumbnail": "",
            "availability": {"available": available, "reason": "" if available else "Missing model: m.dxnn",
                             "reason_items": [] if available else [{"code": "missing_model", "path": "m.dxnn"}]}}


def test_a_refused_demo_start_says_why_in_the_page_language(page):
    import json
    _json_route(page, "**/api/demos", 200, [_demo(0, True)])
    _json_route(page, "**/api/demos/0/start", 424, {"error": "contract_failed",
                "message": "Runtime contract failed: gst.selected_pipeline", "detail": "could not link rtpvp8pay0"})
    page.evaluate("() => DXI18n.setLang('ko')")
    try:
        page.evaluate("() => DXStream.nav('demo')")
        page.wait_for_function("() => DXStream._allDemos && DXStream._allDemos.length", timeout=8000)
        page.evaluate("() => DXStream._startDemo(0)")
        page.wait_for_function("() => /런타임 점검을 통과하지 못했습니다/.test(document.body.innerText)", timeout=5000)
        assert "could not link rtpvp8pay0" in page.inner_text("body")
    finally:
        page.unroute("**/api/demos/0/start")
        page.unroute("**/api/demos")
        page.evaluate("() => DXI18n.setLang('en')")


def test_quick_launch_does_not_start_a_demo_that_needs_setup(page):
    starts = []
    _json_route(page, "**/api/demos", 200, [_demo(0, False)])
    page.route("**/api/demos/0/start", lambda r, *_: starts.append(1) or r.fulfill(status=200, body="{}"))
    try:
        page.evaluate("() => DXStream.nav('dashboard')")
        page.evaluate("() => DXStream.quickLaunchDemo(0)")
        page.wait_for_function("() => /m\\.dxnn/.test(document.body.innerText)", timeout=8000)
        page.wait_for_timeout(600)
        assert starts == []
    finally:
        page.unroute("**/api/demos/0/start")
        page.unroute("**/api/demos")


def test_the_mjpeg_retry_keeps_the_rtsp_source(page):
    import json
    bodies = []
    page.route("**/api/demos/9/start", lambda r, *_: bodies.append(json.loads(r.request.post_data or "{}"))
               or r.fulfill(status=200, content_type="application/json", body='{"started": true, "output_mode": "mjpeg"}'))
    try:
        page.evaluate("() => { DXStream._runningDemoId = 9; DXStream._mjpegFallbackFor = null;"
                      " DXStream._demoStartBody = {9: {video: 'rtsp://cam.local/live'}}; }")
        page.evaluate("() => DXStream._fallbackToMjpeg(9)")
        page.wait_for_timeout(500)
        assert bodies and bodies[0].get("forceMjpeg") is True and bodies[0].get("video") == "rtsp://cam.local/live"
    finally:
        page.unroute("**/api/demos/9/start")
        page.evaluate("() => { DXStream._runningDemoId = null; }")


# ── What is playing: header pill and the Demo page follow the server ──────────

def test_the_header_pill_follows_playback_on_any_page(page):
    _json_route(page, "**/api/pipeline/status", 200,
                {"running": True, "pipeline_id": "mjpeg-pipeline", "output_mode": "mjpeg", "demo_id": None})
    try:
        page.evaluate("() => DXStream.nav('models')")
        page.wait_for_function("() => /Running/.test(document.getElementById('pipeline-status').textContent)",
                               timeout=7000)
    finally:
        page.unroute("**/api/pipeline/status")


def test_the_demo_page_lets_go_of_a_demo_the_server_replaced(page):
    """Running a Pipeline Builder graph stops any demo on the server; the Demo page kept showing it
    as running (and its Stop then stopped the builder pipeline)."""
    _json_route(page, "**/api/pipeline/status", 200,
                {"running": True, "pipeline_id": "mjpeg-pipeline", "output_mode": "mjpeg", "demo_id": None})
    try:
        page.evaluate("() => { DXStream.nav('demo'); DXStream._runningDemoId = 0; }")
        page.wait_for_function("() => DXStream._runningDemoId === null", timeout=7000)
    finally:
        page.unroute("**/api/pipeline/status")


def test_a_failed_stop_is_not_reported_as_stopped(page):
    _json_route(page, "**/api/demos/0/stop", 500, {"error": "pipeline_error", "message": "Stop failed on the server"})
    _json_route(page, "**/api/pipeline/status", 200,
                {"running": True, "pipeline_id": "mjpeg-demo-0", "output_mode": "mjpeg", "demo_id": 0})
    try:
        page.evaluate("() => { DXStream.nav('demo'); DXStream._runningDemoId = 0; }")
        page.evaluate("() => DXStream._stopDemo(0)")
        page.wait_for_function("() => /Stop failed on the server/.test(document.body.innerText)", timeout=5000)
        assert page.evaluate("DXStream._runningDemoId") == 0
    finally:
        page.unroute("**/api/demos/0/stop")
        page.unroute("**/api/pipeline/status")
        page.evaluate("() => { DXStream._runningDemoId = null; }")


def test_a_loaded_preset_is_the_draft_and_an_undo_point(page):
    """loadPreset never pushed history: leaving the tab and coming back restored the OLD draft over
    the preset, and Undo skipped past it."""
    _json_route(page, "**/api/demos", 200, [_demo(0, True)])
    try:
        page.evaluate("() => DXStream.nav('pipeline')")
        page.wait_for_selector("#palette-list .palette-item", timeout=10000)
        page.evaluate("() => DXStream.loadPreset(0)")
        page.wait_for_function("() => DXStream._pipeState.nodes.length > 0", timeout=5000)
        n = page.evaluate("DXStream._pipeState.nodes.length")
        page.wait_for_timeout(500)
        draft = page.evaluate("JSON.parse(localStorage.getItem('dx-pipeline-draft') || '{}')")
        assert len(draft.get("nodes", [])) == n
        idx = page.evaluate("DXStream._pipeState._historyIdx")
        assert page.evaluate("JSON.parse(DXStream._pipeState._history[DXStream._pipeState._historyIdx]).nodes.length") == n, idx
    finally:
        page.unroute("**/api/demos")


# ── Model Catalog downloads ───────────────────────────────────────────────────

_CAT = [{"name": "yolo26n", "file": "yolo26-n_640x640.dxnn", "category": "object_detection", "installed": False,
         "description_en": "d", "description_ko": "d"}]


def test_a_refused_card_download_gives_the_button_back_and_says_why(page):
    _json_route(page, "**/api/models", 200, _CAT)
    _json_route(page, "**/api/setup/download-model", 409, {"error": "conflict", "message": "Another process is already running"})
    try:
        page.evaluate("() => DXStream.nav('models')")
        page.wait_for_selector(".download-model-btn", timeout=8000)
        page.click(".download-model-btn")
        page.wait_for_function("() => /Another process is already running/.test(document.body.innerText)", timeout=5000)
        assert page.locator(".download-model-btn").is_enabled()
    finally:
        page.unroute("**/api/setup/download-model")
        page.unroute("**/api/models")


def test_a_card_download_follows_its_own_log_and_reports_the_end(page):
    import json
    asked = []

    def log(route, *_):
        asked.append(route.request.url)
        route.fulfill(status=200, content_type="application/json",
                      body=json.dumps({"log": "x", "done": True, "exit_code": 1}))

    _json_route(page, "**/api/models", 200, _CAT)
    _json_route(page, "**/api/setup/download-model", 200, {"started": True, "model": "yolo26-n_640x640.dxnn"})
    page.route("**/api/setup/log*", log)
    try:
        page.evaluate("() => DXStream.nav('models')")
        page.wait_for_selector(".download-model-btn", timeout=8000)
        page.click(".download-model-btn")
        page.wait_for_function("() => /exit 1/.test(document.body.innerText)", timeout=8000)
        assert asked and all("step=model-yolo26-n_640x640.dxnn" in u for u in asked), asked
    finally:
        page.unroute("**/api/setup/log*")
        page.unroute("**/api/setup/download-model")
        page.unroute("**/api/models")


def test_stop_is_offered_only_for_steps_that_can_stop(page):
    _json_route(page, "**/api/setup/log*", 200, {"log": "working\n", "done": False, "exit_code": None})
    try:
        page.evaluate("() => DXStream.nav('setup')")
        page.evaluate("() => _resumeRunningStep('runtime-deps')")
        assert not page.locator("#setup-stop-btn").is_visible()
        page.evaluate("() => { clearInterval(DXStream._setupPollTimer); DXStream._setupPollTimer = null; _resumeRunningStep('download-models'); }")
        assert page.locator("#setup-stop-btn").is_visible()
    finally:
        page.evaluate("() => { clearInterval(DXStream._setupPollTimer); DXStream._setupPollTimer = null; DXStream._setupRunning = false; }")
        page.unroute("**/api/setup/log*")


def test_a_failed_diagnostics_call_says_why(page):
    _json_route(page, "**/api/diagnostics", 500, {"error": "server_error", "message": "Diagnostics are unavailable"})
    try:
        page.evaluate("() => DXStream.nav('setup')")
        before = len(page.errors)
        page.evaluate("() => DXStream.runDiagnostics()")
        page.wait_for_function("() => /Diagnostics are unavailable/.test(document.getElementById('stream-diag-results').innerText)", timeout=5000)
        assert len(page.errors) == before
        assert page.locator("#stream-diag-run-btn").is_enabled()
    finally:
        page.unroute("**/api/diagnostics")


def test_element_category_and_search_narrow_together(page):
    page.evaluate("() => DXStream.nav('elements')")
    page.wait_for_selector("#elements-grid .element-card", timeout=10000)
    page.evaluate("() => DXStream.filterElements('postprocess', null)")
    page.fill("#elements-search", "dx")
    cats = page.evaluate("() => [...new Set(DXStream._allElements.filter(e => [...document.querySelectorAll('#elements-grid .element-card-name')].map(n => n.textContent).includes(e.name)).map(e => e.category))]")
    try:
        assert cats == ["postprocess"], cats
    finally:
        page.fill("#elements-search", "")
        page.evaluate("() => DXStream.filterElements('all', null)")


def test_node_messages_are_translated_beyond_english_and_korean(page):
    """Copy / paste / delete messages passed a built sentence to T(en, ko): every other language
    showed English. They are dictionary keys with a placeholder now."""
    page.evaluate("() => DXI18n.setLang('ja')")
    try:
        page.evaluate("() => DXStream.nav('pipeline')")
        page.wait_for_selector("#pipeline-canvas", timeout=10000)
        page.evaluate("""() => { const st = DXStream._pipeState;
            st.nodes = [{id: 'n1', type: 'queue', name: 'queue', category: 'utility', x: 40, y: 40, properties: {}}];
            st.edges = []; st.selectedNodes = ['n1']; st.selectedNode = 'n1'; DXStream._copyNodes(); }""")
        page.wait_for_function("() => /個のノードをコピーしました/.test(document.body.innerText)", timeout=4000)
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_setup_intro_keeps_its_width_on_a_phone(page):
    """390 px · es: "Instalar el resto" took the row and the intro folded one word per line (matrix 2026-10-11)."""
    page.set_viewport_size({"width": 390, "height": 844})
    try:
        page.evaluate("() => { DXI18n.setLang('es'); DXStream.nav('setup'); }")
        page.wait_for_selector("#page-setup .dx-steps-lede", timeout=10000)
        page.wait_for_timeout(300)
        lede = page.evaluate("document.querySelector('#page-setup .dx-steps-lede').getBoundingClientRect().width")
        btn = page.evaluate("document.querySelector('#setup-run-all').getBoundingClientRect().right")
        assert lede > 250, lede
        assert btn <= 390, btn
    finally:
        page.evaluate("() => DXI18n.setLang('en')")
        page.set_viewport_size({"width": 1440, "height": 900})


def test_the_reference_names_the_setup_button_as_the_button_reads():
    """Reference said '나머지 설정' / 'Configurar el resto' for a button labelled '나머지 설치' / 'Instalar el resto'."""
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    i18n = (root / "dx_stream/static/js/stream-i18n.js").read_text(encoding="utf-8")
    ref = (root / "dx_stream/static/js/stream-reference.js").read_text(encoding="utf-8")
    entry = re.search(r"'Set up the rest': \{([^}]*)\}", i18n).group(1)
    line = next(l for l in ref.splitlines() if "finish the six steps" in l)
    for lang, label in re.findall(r"(ko|ja|'zh-CN'|'zh-TW'|es): '([^']*)'", entry):
        assert f"<b>{label}</b>" in line, (lang, label)

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

"""dx_app Outputs: chips, the empty list and icon-button names follow the chosen language.

Chip names (_TYPE_LABEL) must be translated at render time, not once when the script loads; 'No files' and
' Compare' must be translated; download and delete buttons need accessible names. /api/outputs is a fixture.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

FILES = [{"name": "dog_result.jpg", "type": "image", "size": 1234, "mtime": 1790000000, "url": "/api/output/dog_result.jpg",
          "src_image": "sample/img/sample_dog.jpg"}]


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');")
    pg = ctx.new_page()
    pg.route("**/api/outputs", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(FILES)))
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.evaluate("() => nav('outputs')")
    pg.wait_for_selector("#out-filters .out-filter-chip", timeout=10000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _chips(page):
    return page.evaluate("[...document.querySelectorAll('#out-filters .out-filter-chip')]"
                         ".map(c => c.textContent.replace(/\\d+/g, '').trim())")


def test_filter_chips_follow_the_language(page):
    assert _chips(page)[:3] == ["All", "Images", "Videos"]
    page.evaluate("() => DXI18n.setLang('es')")
    try:
        page.wait_for_function("() => document.querySelector('#out-filters .out-filter-chip').textContent.includes('Todo')",
                               timeout=5000)
        assert _chips(page)[:2] == ["Todo", "Imágenes"]
        assert "Comparar" in page.inner_text("#out-gallery")
        names = page.evaluate("[...document.querySelectorAll('#out-gallery .gal-actions a, #out-gallery .gal-actions .txt-err')]"
                              ".map(b => b.getAttribute('aria-label'))")
        assert names == ["Descargar", "Eliminar"], names
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_an_empty_filter_says_so_in_the_language(page):
    page.evaluate("() => { DXI18n.setLang('ko'); setOutFilter('archive'); }")
    try:
        page.wait_for_timeout(300)
        assert page.inner_text("#out-gallery").strip() == "이 필터에 맞는 파일이 없습니다."
    finally:
        page.evaluate("() => { setOutFilter('all'); DXI18n.setLang('en'); }")

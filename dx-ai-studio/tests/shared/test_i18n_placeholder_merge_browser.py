"""Translations kept in _DX_I18N_PLACEHOLDERS reach T() and data-i18n too.

dx_app's i18n.js closes _DX_I18N_DICT early; ~370 ordinary strings ("Waiting…", "Elapsed", "All Tasks" …) sit in
_DX_I18N_PLACEHOLDERS. If only the placeholder pass read them, they would stay English in every language, and the
`[data-i18n-placeholder]` pass must not write the English key back over a placeholder the first pass translated.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

ROOT = Path(__file__).resolve().parents[2]
I18N = (ROOT / "shared" / "static" / "i18n.js").read_text(encoding="utf-8")

PAGE = """<!doctype html><html><head><meta charset="utf-8"><script>
window._DX_I18N_DICT = { 'Run': { ko: '실행' } };
window._DX_I18N_PLACEHOLDERS = {
  'Waiting…': { ko: '대기 중…', ja: '待機中…' },
  'Search models...': { ko: '모델 검색...' }
};
try { localStorage.setItem('dx-lang', 'ko'); } catch (e) {}
</script><script src="/i18n.js"></script></head><body>
<span id="a" data-i18n="Waiting…">Waiting…</span>
<span id="b" data-i18n="Run">Run</span>
<input id="c" placeholder="Search models...">
<input id="d" data-i18n-placeholder="Search models..." placeholder="Search models...">
</body></html>"""


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright
    from tests.browser_support import resolve_chromium_executable

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
    pg = br.new_page()

    def serve(route):
        url = route.request.url
        if url.endswith("/i18n.js"):
            route.fulfill(status=200, content_type="application/javascript", body=I18N)
        else:
            route.fulfill(status=200, content_type="text/html", body=PAGE)

    pg.route("http://dx.test/**", serve)
    pg.goto("http://dx.test/", wait_until="load")
    pg.evaluate("DXI18n.applyLang && DXI18n.applyLang()")
    yield pg
    br.close()
    pw.stop()


def test_a_string_kept_with_the_placeholders_is_translated_everywhere(page):
    assert page.evaluate("T('Waiting…')") == "대기 중…"
    assert page.inner_text("#a") == "대기 중…"
    assert page.inner_text("#b") == "실행", "the ordinary dictionary still wins"


def test_the_placeholder_attribute_pass_does_not_undo_the_translation(page):
    assert page.get_attribute("#c", "placeholder") == "모델 검색..."
    assert page.get_attribute("#d", "placeholder") == "모델 검색..."


def test_switching_language_moves_them_too(page):
    page.evaluate("DXI18n.setLang('ja')")
    assert page.inner_text("#a") == "待機中…"

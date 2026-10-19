"""Shared toolbar: button names follow the chosen language, and the language menu works from the keyboard.

'Language', 'Theme: …', 'Tutorial', 'Settings' and the shell rail's 'Modules' come from the shared chrome dictionary
in shared/static/i18n.js, so they are translated in every language without a copy per module dictionary. Language
items must be reachable with Tab and the arrow keys.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.wait_for_selector("#dxToolbar .dx-lang-btn", timeout=10000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _names(page):
    return page.evaluate("""() => ({
      lang: document.querySelector('#dxToolbar .dx-lang-btn').getAttribute('aria-label'),
      theme: document.getElementById('dxToolbarTheme').getAttribute('aria-label'),
      tutorial: document.getElementById('dxToolbarTutorial')?.getAttribute('aria-label'),
      settings: document.getElementById('dxToolbarSettings')?.getAttribute('aria-label'),
      rail: document.querySelector('.dx-shell-rail')?.getAttribute('aria-label'),
    })""")


def test_toolbar_names_follow_the_language(page):
    assert _names(page)["lang"] == "Language"
    page.evaluate("() => DXI18n.setLang('ko')")
    try:
        n = _names(page)
        assert n["lang"] == "언어"
        assert n["theme"].startswith("테마: ")
        assert n["tutorial"] in (None, "튜토리얼")
        assert n["settings"] in (None, "설정")
        assert n["rail"] in (None, "모듈")
        title = page.get_attribute("#dxToolbar .dx-lang-btn", "title")
        assert title == "언어"
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_the_language_menu_works_from_the_keyboard(page):
    btn = page.locator("#dxToolbar .dx-lang-btn")
    btn.focus()
    page.keyboard.press("Enter")
    assert btn.get_attribute("aria-expanded") == "true"
    assert page.evaluate("document.activeElement.dataset.lang") == "en", "고른 언어에 focus"
    page.keyboard.press("ArrowDown")
    nxt = page.evaluate("document.activeElement.dataset.lang")
    assert nxt and nxt != "en"
    page.keyboard.press("Enter")
    try:
        assert page.evaluate("DXI18n.lang") == nxt
        assert btn.get_attribute("aria-expanded") == "false"
        assert page.evaluate("document.activeElement.classList.contains('dx-lang-btn')"), "단추로 focus 가 돌아온다"
        assert page.evaluate(f"document.querySelector('.dx-lang-item[data-lang=\"{nxt}\"]').getAttribute('aria-checked')") == "true"
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_escape_closes_the_menu_and_returns_focus(page):
    btn = page.locator("#dxToolbar .dx-lang-btn")
    btn.focus()
    page.keyboard.press("ArrowDown")
    assert btn.get_attribute("aria-expanded") == "true"
    page.keyboard.press("Escape")
    assert btn.get_attribute("aria-expanded") == "false"
    assert page.evaluate("document.activeElement.classList.contains('dx-lang-btn')")
    assert not page.is_visible(".dx-lang-menu")

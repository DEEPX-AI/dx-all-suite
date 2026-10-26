"""A first visit opens in the browser's language.

Studio speaks six languages; a Korean, Japanese, Chinese or Spanish browser must not open it in English and leave the
user to find the language menu. With no saved choice, the browser's languages pick the first supported one, and
the pick is saved so every script that reads dx-lang agrees. A saved choice still wins.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_QUIET = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
          "localStorage.setItem('dx-tutorial-launcher-autostarted','1');localStorage.setItem('dx-tutorial-mode','off');}"
          "catch(e){}")


@pytest.fixture(scope="module")
def servers():
    launcher, lport = start_module_server("launcher")
    app, aport = start_module_server("dx_app")
    yield {"launcher": lport, "dx_app": aport}
    launcher.shutdown()
    app.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _lang(browser, port, locale, saved=None):
    ctx = browser.new_context(locale=locale, viewport={"width": 1280, "height": 800})
    ctx.add_init_script(_QUIET + (f"try{{localStorage.setItem('dx-lang','{saved}')}}catch(e){{}}" if saved else ""))
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
        page.wait_for_function("!!window.DXI18n", timeout=30000)
        return page.evaluate("[DXI18n.lang, localStorage.getItem('dx-lang'), document.documentElement.lang]")
    finally:
        ctx.close()


@pytest.mark.parametrize(("locale", "want"), [
    ("ko-KR", "ko"), ("ja-JP", "ja"), ("es-MX", "es"), ("zh-CN", "zh-CN"), ("zh-TW", "zh-TW"),
    ("zh-HK", "zh-TW"), ("fr-FR", "en"), ("en-US", "en"),
])
def test_a_first_visit_follows_the_browser(browser, servers, locale, want):
    lang, saved, html_lang = _lang(browser, servers["launcher"], locale)
    assert lang == want and saved == want, (locale, lang, saved)
    assert html_lang == want


def test_a_saved_choice_wins_over_the_browser(browser, servers):
    lang, saved, _ = _lang(browser, servers["launcher"], "ko-KR", saved="ja")
    assert lang == "ja" and saved == "ja"


def test_a_module_opened_alone_follows_the_browser_too(browser, servers):
    lang, saved, _ = _lang(browser, servers["dx_app"], "ko-KR")
    assert lang == "ko" and saved == "ko"

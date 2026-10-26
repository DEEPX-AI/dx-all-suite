"""About DEEPX nav tabs never show an i18n key, not even for one frame.

The tabs carried data-i18n="aboutDeveloper" and so on. Those are identifier keys, not English source text, and the
shared i18n.js writes the key itself as the text in English (`el.textContent = key`) and leaves the HTML text in
other languages. about-deepx.js only wrote the real labels after about-data.json arrived, so until then the tabs read
'aboutDeveloper' / 'aboutCompany' … — for good when the data failed to load.

Here about-data.json is held back, and every animation frame from the first one records the tab texts.
"""
from __future__ import annotations

import re

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

LABELS = {
    "en": ["Developer", "Company", "Technology", "Products", "Partners", "Awards", "News"],
    "ko": ["개발자", "회사", "기술", "제품", "파트너", "수상", "뉴스"],
    "ja": ["開発者", "企業", "技術", "製品", "パートナー", "受賞", "ニュース"],
}

# Samples the nav on every frame from the very first, before any script of the page runs.
_SAMPLER = """
(() => {
  window.__aboutNavSeen = [];
  const tick = () => {
    document.querySelectorAll('#aboutNav .about-nav-tab').forEach(t => {
      const s = t.textContent.trim();
      if (!window.__aboutNavSeen.includes(s)) window.__aboutNavSeen.push(s);
    });
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
})();
"""


@pytest.fixture(scope="module")
def port():
    server, port = start_module_server("launcher")
    yield port
    server.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    from tests.browser_support import resolve_chromium_executable

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
    yield br
    br.close()
    pw.stop()


def _open(browser, port, lang, hold_data=True):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script(
        "try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');localStorage.setItem('dx-tutorial-mode','off');"
        f"localStorage.setItem('dx-lang','{lang}');}}catch(e){{}}")
    ctx.add_init_script(_SAMPLER)
    held = []
    if hold_data:
        # Never answered while the test looks: the state a slow or failed about-data.json leaves the page in.
        ctx.route("**/static/about-data.json", lambda route, *_: held.append(route))
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/about", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function("!!(window.DXLauncher && DXLauncher.currentApp === 'about')", timeout=30000)
    return ctx, page, held


def _close(ctx, held):
    for route in held:
        try:
            route.abort()
        except Exception:   # the page may have given up on it already
            pass
    ctx.close()


def _tabs(page):
    return page.evaluate("[...document.querySelectorAll('#aboutNav .about-nav-tab')].map(t => t.textContent.trim())")


def _keys_seen(page):
    return [s for s in page.evaluate("window.__aboutNavSeen") if re.fullmatch(r"about[A-Z]\w*", s)]


@pytest.mark.parametrize("lang", ["en", "ko"])
def test_tabs_are_translated_while_the_about_data_is_still_loading(port, browser, lang):
    ctx, page, held = _open(browser, port, lang)
    try:
        page.wait_for_timeout(800)
        assert _tabs(page) == LABELS[lang]
        assert not _keys_seen(page), _keys_seen(page)
    finally:
        _close(ctx, held)


def test_a_language_change_before_the_data_arrives_relabels_the_tabs(port, browser):
    ctx, page, held = _open(browser, port, "en")
    try:
        for lang in ("ja", "en", "ko"):
            page.evaluate("l => DXI18n.setLang(l)", lang)
            page.wait_for_timeout(200)
            assert _tabs(page) == LABELS[lang], lang
        assert not _keys_seen(page), _keys_seen(page)
    finally:
        _close(ctx, held)


def test_no_key_shows_from_first_paint_to_the_loaded_page(port, browser):
    ctx, page, held = _open(browser, port, "en", hold_data=False)
    try:
        page.wait_for_selector("#aboutScroll .about-hero", timeout=30000)
        page.wait_for_timeout(300)
        assert _tabs(page) == LABELS["en"]
        assert not _keys_seen(page), _keys_seen(page)
    finally:
        _close(ctx, held)

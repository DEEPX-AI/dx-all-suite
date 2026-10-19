"""Home's effects actually run on screen, and stop under reduced motion."""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_SEEN = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "localStorage.setItem('dx-tutorial-launcher-autostarted','1');"
         "localStorage.setItem('dx-tutorial-mode','off');}catch(e){}")
# Count calls to the transition, then hand off to the real API.
_COUNT_FADES = """() => {
  window.__fades = [];
  const real = document.startViewTransition && document.startViewTransition.bind(document);
  document.startViewTransition = (arg) => {
    window.__fades.push(document.documentElement.dataset.dxFading || '');
    return real ? real(arg) : (typeof arg === 'function' ? arg() : arg.update());
  };
}"""


@pytest.fixture(scope="module")
def server():
    srv, port = start_module_server("launcher")
    yield port
    srv.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _open(browser, port, *, still=False):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                              reduced_motion="reduce" if still else "no-preference")
    ctx.add_init_script(_SEEN)
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.wait_for_selector("#studioGrid .orbital-card", state="visible")
    return ctx, page


def _glow(page):
    return float(page.evaluate("() => getComputedStyle(document.querySelector('#homeAskForm .ask-box'), '::after').opacity"))


def _glow_animating(page):
    """Count only the ripples JS starts; focus CSS transitions also show up in getAnimations()."""
    return page.evaluate("""() => document.getAnimations().some(a => a.effect
      && !(a instanceof CSSTransition) && !(a instanceof CSSAnimation)
      && a.effect.pseudoElement === '::after' && a.effect.target
      && a.effect.target.classList.contains('ask-box'))""")


def test_the_stage_light_is_on_only_at_home(browser, server):
    ctx, page = _open(browser, server)
    try:
        assert page.evaluate("() => document.body.classList.contains('home-visible')")
        bg = page.evaluate("() => getComputedStyle(document.body).backgroundImage")
        assert "radial-gradient" in bg, bg
        page.click(".about-book-card:not(.sdk-card)")
        page.wait_for_function("() => !document.body.classList.contains('home-visible')", timeout=5000)
    finally:
        ctx.close()


def test_the_input_edge_lights_on_focus_and_ripples_per_key(browser, server):
    ctx, page = _open(browser, server)
    try:
        assert _glow(page) == 0
        page.focus("#homeAsk")
        page.wait_for_function("""() => parseFloat(getComputedStyle(
          document.querySelector('#homeAskForm .ask-box'), '::after').opacity) > 0.4""", timeout=3000)
        page.keyboard.type("a")
        assert _glow_animating(page), "키 입력에 빛이 일렁이지 않았다"
        page.wait_for_timeout(400)
        assert not _glow_animating(page), "빛이 240ms 뒤에도 가라앉지 않았다"
    finally:
        ctx.close()


def test_reduced_motion_keeps_the_input_still(browser, server):
    ctx, page = _open(browser, server, still=True)
    try:
        page.focus("#homeAsk")
        page.keyboard.type("a")
        assert not _glow_animating(page)
    finally:
        ctx.close()


def test_a_book_tilts_when_pointed_at(browser, server):
    ctx, page = _open(browser, server)
    try:
        cover = ".about-book-card.sdk-card .orbital-icon"
        assert page.evaluate(f"() => getComputedStyle(document.querySelector('{cover}')).transform") == "none"
        page.hover(".about-book-card.sdk-card")
        page.wait_for_timeout(450)
        t = page.evaluate(f"() => getComputedStyle(document.querySelector('{cover}')).transform")
        assert t.startswith("matrix3d"), t
    finally:
        ctx.close()


def test_a_poster_thumbnail_grows_when_pointed_at(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.hover("#landingPoster")
        page.wait_for_timeout(400)
        t = page.evaluate("() => getComputedStyle(document.querySelector('#landingPoster img')).transform")
        assert t.startswith("matrix(1.06"), t
    finally:
        ctx.close()


def test_the_theme_crossfades_and_still_switches(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.evaluate(_COUNT_FADES)
        before = page.evaluate("() => DXTheme.getTheme()")
        page.click("#dxToolbarTheme")
        page.wait_for_function(f"() => DXTheme.getTheme() !== '{before}'", timeout=3000)
        assert page.evaluate("() => window.__fades") == ["theme"]
        page.wait_for_function("() => !document.documentElement.dataset.dxFading", timeout=3000)
    finally:
        ctx.close()


def test_the_language_crossfades_and_still_switches(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.evaluate(_COUNT_FADES)
        page.evaluate("() => DXI18n.setLang('ko')")
        page.wait_for_function("() => document.documentElement.lang === 'ko'", timeout=3000)
        assert page.evaluate("() => window.__fades") == ["lang"]
        title = page.inner_text("#homeStage .stage-title")
        assert "DX-M1" in title and "Describe" not in title
    finally:
        ctx.close()


def test_reduced_motion_switches_without_a_crossfade(browser, server):
    ctx, page = _open(browser, server, still=True)
    try:
        page.evaluate(_COUNT_FADES)
        before = page.evaluate("() => DXTheme.getTheme()")
        page.click("#dxToolbarTheme")
        page.evaluate("() => DXI18n.setLang('ja')")
        assert page.evaluate("() => DXTheme.getTheme()") != before
        assert page.evaluate("() => document.documentElement.lang") == "ja"
        assert page.evaluate("() => window.__fades") == []
    finally:
        ctx.close()

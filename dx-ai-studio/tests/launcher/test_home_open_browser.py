"""Modules open from their icon and close back to it, and the document stays the same whichever way they open.

No module server runs: the transition starts before the health response, so none is needed. Whether the document
was reloaded is read from a marker left on window (a new document loses it).
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_SEEN = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "localStorage.setItem('dx-tutorial-launcher-autostarted','1');"
         "localStorage.setItem('dx-tutorial-mode','off');sessionStorage.setItem('dx-home-entered','1');}catch(e){}")
_MARK = "() => { window.__sameDocument = true; }"


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
    page.evaluate(_MARK)
    return ctx, page


def _anim(page, name):
    return f"() => document.getAnimations().some(a => a.id === '{name}')"


def _same_document(page):
    return page.evaluate("() => window.__sameDocument === true")


def test_an_icon_opens_its_module_from_where_it_sits(browser, server):
    ctx, page = _open(browser, server)
    try:
        tile = page.evaluate("""() => { const r = document.querySelector('.orbital-card[data-app="zoo"] .mod-tile')
          .getBoundingClientRect(); return [r.left, r.top, r.width]; }""")
        page.click('.orbital-card[data-app="zoo"]')
        page.wait_for_function(_anim(page, "open"), timeout=5000)
        start = page.evaluate("""() => { const a = document.getAnimations().find(a => a.id === 'open');
          return a.effect.getKeyframes()[0].transform; }""")
        assert start and "scale" in start, start
        assert page.evaluate("() => DXLauncher.currentApp") == "zoo"
        assert _same_document(page)
        assert page.evaluate("() => document.getElementById('appFrame').style.display") == "block"
        assert tile[2] > 0
    finally:
        ctx.close()


def test_going_home_shrinks_the_module_back_into_its_icon(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.click('.orbital-card[data-app="zoo"]')
        page.wait_for_function(_anim(page, "open"), timeout=5000)
        page.wait_for_function(f"() => !({_anim(page, 'open')[6:]})", timeout=3000)
        page.evaluate("() => goHome()")
        page.wait_for_function(_anim(page, "close"), timeout=5000)
        end = page.evaluate("""() => { const a = document.getAnimations().find(a => a.id === 'close');
          const k = a.effect.getKeyframes(); return k[k.length - 1].transform; }""")
        assert end and "scale" in end, end
        assert page.evaluate("() => document.body.classList.contains('home-visible')")
        assert _same_document(page)
    finally:
        ctx.close()


def test_a_route_card_opens_inside_the_same_shell(browser, server):
    """Opening must not reload the document. A string passed to loadAppIframeIfNeeded throws, and a catch that
    falls back to location.href would lose the typed sentence and state."""
    ctx, page = _open(browser, server)
    try:
        page.fill("#homeAsk", "compile yolo26n to DXNN")
        page.press("#homeAsk", "Enter")
        page.wait_for_selector('#answerRoutes .route-card[data-module="compiler"]', state="visible", timeout=5000)
        page.click('#answerRoutes .route-card[data-module="compiler"]')
        page.wait_for_function("() => DXLauncher.currentApp === 'compiler'", timeout=5000)
        page.wait_for_timeout(500)
        assert _same_document(page), "문서를 새로 불렀다"
        assert page.evaluate("() => location.pathname").startswith("/compiler")
    finally:
        ctx.close()


def test_a_hash_reaches_the_module(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.evaluate("() => DXLauncher.launch('stream', { hash: '#demo=3' })")
        page.wait_for_function("() => DXLauncher.currentApp === 'stream'", timeout=5000)
        page.wait_for_timeout(300)
        assert page.evaluate("() => location.hash") == "#demo=3"
        assert _same_document(page)
    finally:
        ctx.close()


def test_reduced_motion_opens_without_the_transition(browser, server):
    ctx, page = _open(browser, server, still=True)
    try:
        page.click('.orbital-card[data-app="zoo"]')
        page.wait_for_function("() => DXLauncher.currentApp === 'zoo'", timeout=5000)
        page.wait_for_timeout(200)
        assert not page.evaluate(_anim(page, "open"))
        assert not page.evaluate("() => !!document.querySelector('.open-veil')")
    finally:
        ctx.close()

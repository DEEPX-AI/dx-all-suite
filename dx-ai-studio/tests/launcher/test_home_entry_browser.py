"""Home's motion: first entry, the send sweep, Dock magnification, and the running light.

The effects JS names its animations (entry · sweep · orb · lit); the tests find them by those ids.
"""
from __future__ import annotations

import re

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_SEEN = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "localStorage.setItem('dx-tutorial-launcher-autostarted','1');"
         "localStorage.setItem('dx-tutorial-mode','off');}catch(e){}")
_ENTERED = "try{sessionStorage.setItem('dx-home-entered','1');}catch(e){}"


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


def _open(browser, port, *, still=False, entered=True):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                              reduced_motion="reduce" if still else "no-preference")
    ctx.add_init_script(_SEEN + (_ENTERED if entered else ""))
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.wait_for_selector("#studioGrid .orbital-card", state="visible")
    return ctx, page


def _ids(page, name):
    return page.evaluate(f"() => document.getAnimations().filter(a => a.id === '{name}').length")


# ── first entry ───────────────────────────────────────────────────────────

def test_the_first_entry_rises_in_order_and_sweeps_once(browser, server):
    ctx, page = _open(browser, server, entered=False)
    try:
        page.wait_for_function("() => document.getAnimations().some(a => a.id === 'entry')", timeout=6000)
        delays = page.evaluate("""() => document.getAnimations().filter(a => a.id === 'entry')
          .map(a => [a.effect.target, a.effect.getTiming().delay])
          .sort((x, y) => x[0].compareDocumentPosition(y[0]) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1)
          .map(x => x[1])""")
        assert len(delays) >= 12, delays
        assert delays == sorted(delays), f"화면 순서대로 떠오르지 않는다: {delays}"
        assert delays[-1] <= 700, "1.2s 안에 끝나야 한다 (지연 + 500ms)"
        assert _ids(page, "sweep") >= 1, "제목을 훑는 빛이 없다"
        page.wait_for_function("() => !document.getAnimations().some(a => a.id === 'entry' || a.id === 'sweep')",
                               timeout=4000)
        assert page.evaluate("() => sessionStorage.getItem('dx-home-entered')") == "1"
        page.reload(wait_until="load")
        page.wait_for_selector("#studioGrid .orbital-card", state="visible")
        page.wait_for_timeout(1500)
        assert _ids(page, "entry") == 0, "세션에 한 번이어야 한다"
    finally:
        ctx.close()


def test_reduced_motion_skips_the_entry(browser, server):
    ctx, page = _open(browser, server, still=True, entered=False)
    try:
        page.wait_for_timeout(2000)
        assert _ids(page, "entry") == 0 and _ids(page, "sweep") == 0
    finally:
        ctx.close()


# ── send ──────────────────────────────────────────────────────────────────

def test_sending_flies_a_light_to_the_routed_module(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.fill("#homeAsk", "compile yolo26n to DXNN")
        page.press("#homeAsk", "Enter")
        page.wait_for_function("() => document.getAnimations().some(a => a.id === 'orb')", timeout=5000)
        page.wait_for_function("""() => document.getAnimations().some(a => a.id === 'lit'
          && a.effect.target.closest('.orbital-card[data-app="compiler"]'))""", timeout=3000)
    finally:
        ctx.close()


# ── Dock magnification ────────────────────────────────────────────────────

def _scale(page, app):
    t = page.evaluate(f"""() => getComputedStyle(document.querySelector(
      '.orbital-card[data-app="{app}"] .mod-tile')).transform""")
    if t == "none":
        return 1.0
    return float(re.match(r"matrix\(([-\d.e]+)", t).group(1))


def _centre(page, app):
    return page.evaluate(f"""() => {{ const r = document.querySelector(
      '.orbital-card[data-app="{app}"] .mod-tile').getBoundingClientRect();
      return [r.left + r.width / 2, r.top + r.height / 2]; }}""")


def test_icons_near_the_cursor_grow_like_a_dock(browser, server):
    ctx, page = _open(browser, server)
    try:
        x, y = _centre(page, "app")
        page.mouse.move(x - 60, y)
        page.mouse.move(x, y, steps=4)
        page.wait_for_timeout(250)
        near, far = _scale(page, "app"), _scale(page, "agent")
        assert abs(near - 1.18) < 0.02, near
        assert far == 1.0, far
        # Between two icons (distance measured from the cursor): both grow, the nearer one more.
        page.mouse.move(x + 45, y, steps=2)
        page.wait_for_timeout(250)
        a, b = _scale(page, "app"), _scale(page, "stream")
        assert 1.0 < b < a < 1.18, (a, b)
        page.mouse.move(x, y, steps=2)
        page.wait_for_timeout(200)
        page.mouse.down()
        page.wait_for_timeout(150)
        assert abs(_scale(page, "app") - 1.18 * 0.96) < 0.02
        page.mouse.up()
        page.mouse.move(700, 120, steps=4)
        page.wait_for_timeout(300)
        assert _scale(page, "app") == 1.0
    finally:
        ctx.close()


def test_reduced_motion_keeps_the_icons_still(browser, server):
    ctx, page = _open(browser, server, still=True)
    try:
        x, y = _centre(page, "app")
        page.mouse.move(x, y, steps=3)
        page.wait_for_timeout(200)
        assert _scale(page, "app") == 1.0
    finally:
        ctx.close()


# ── running ───────────────────────────────────────────────────────────────

def test_a_running_module_lights_its_glyph(browser, server):
    ctx, page = _open(browser, server)
    try:
        sel = '.orbital-card[data-app="zoo"] .mod-glyph'
        read = f"() => parseFloat(getComputedStyle(document.querySelector('{sel}')).getPropertyValue('--ico-fill-o'))"
        before = page.evaluate(read)
        assert before < 0.6, f"켜지기 전부터 밝다: {before}"
        page.evaluate("""() => { const c = document.querySelector('.orbital-card[data-app="zoo"]');
          c.classList.remove('is-down'); c.classList.add('is-up'); }""")
        page.wait_for_timeout(600)
        assert page.evaluate(read) == 1
    finally:
        ctx.close()

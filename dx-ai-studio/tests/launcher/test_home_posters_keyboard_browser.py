"""Home's two film pills open from the keyboard (2026-10-12 release audit).

`tools/release_audit.py` keyboard smoke "landing_poster_enter" failed: #landingPoster and #ecosystemPoster are
<a role="button" tabindex="0"> with only an onclick, so Enter and Space did nothing. The keyboard handler sat on the
inner image, which never takes focus.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_QUIET = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
          "localStorage.setItem('dx-tutorial-launcher-autostarted','1');localStorage.setItem('dx-tutorial-mode','off');}"
          "catch(e){}")


@pytest.fixture(scope="module")
def port():
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


@pytest.mark.parametrize(("pill", "overlay"), [("landingPoster", "platformInfoOverlay"),
                                               ("ecosystemPoster", "ecosystemOverlay")])
@pytest.mark.parametrize("key", ["Enter", " "])
def test_a_film_pill_opens_from_the_keyboard(browser, port, pill, overlay, key):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(_QUIET)
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
        page.wait_for_function("!document.documentElement.classList.contains('launcher-boot-pending')", timeout=30000)
        page.wait_for_function(f"document.getElementById('{pill}').dataset.keyboardBound === '1'", timeout=15000)
        page.wait_for_timeout(800)                 # Home focuses its ask box on load; let that settle first
        page.locator(f"#{pill}").press(key)        # focus + key, as a keyboard user tabbing to it would
        page.wait_for_function(f"document.getElementById('{overlay}').classList.contains('open')", timeout=5000)
    finally:
        ctx.close()

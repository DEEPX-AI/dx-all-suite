"""The shared chrome icons are drawn on screen from the sprite.

Checks the launcher and one module (dx_app); the toolbar, chat and tutorial list are the same code in both.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_SEEN = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "localStorage.setItem('dx-tutorial-launcher-autostarted','1');localStorage.setItem('dx-tutorial-mode','off');"
         "sessionStorage.setItem('dx-home-entered','1');localStorage.setItem('dx-theme','dark');}catch(e){}")


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


@pytest.fixture(scope="module", params=["launcher", "dx_app"])
def page(browser, request):
    srv, port = start_module_server(request.param)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script(_SEEN)
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.wait_for_selector("#dxToolbarTheme", state="attached", timeout=15000)
    yield pg
    ctx.close()
    srv.shutdown()


def _icon(page, sel):
    return page.evaluate(f"""() => {{ const u = document.querySelector('{sel} svg.dx-ico use');
      return u ? u.getAttribute('href').split('#')[1] : null; }}""")


def test_the_sprite_is_served(page):
    ok = page.evaluate("() => fetch('/static/shared/dx-icons.svg').then(r => r.ok && r.headers.get('content-type'))")
    assert ok and "svg" in ok, ok


def test_toolbar_buttons_are_sprite_icons(page):
    assert _icon(page, "#langToggle .dx-lang-icon") == "globe"
    assert _icon(page, "#langToggle .dx-lang-arrow") == "chevd"
    assert _icon(page, "#dxToolbarTheme") == "moon"


def test_the_theme_icon_follows_the_state(page):
    seen = []
    for _ in range(3):
        page.click("#dxToolbarTheme")
        page.wait_for_timeout(150)
        seen.append(_icon(page, "#dxToolbarTheme"))
    assert seen == ["sun", "theme", "moon"], seen
    assert page.get_attribute("#dxToolbarTheme", "aria-label") == "Theme: dark"


def test_the_icons_are_drawn(page):
    """Without the sprite a <use> stays an empty box rather than 0×0, so check that strokes were painted."""
    box = page.evaluate("""() => { const s = document.querySelector('#dxToolbarTheme svg.dx-ico');
      const r = s.getBoundingClientRect(); return [r.width, r.height]; }""")
    assert box[0] >= 12 and box[1] >= 12, box


def test_the_chat_button_is_a_sprite_icon(page):
    page.wait_for_selector(".dx-chat-fab", state="attached", timeout=10000)
    assert _icon(page, ".dx-chat-fab") == "chat"
    page.evaluate("() => document.querySelector('.dx-chat-fab').click()")
    assert _icon(page, ".dx-chat-fab") == "x", "열린 챗의 버튼은 닫기 표시다"
    for action, name in (("settings", "gear"), ("clear", "trash"), ("close", "x")):
        assert _icon(page, f'.dx-chat-header-btn[data-action="{action}"]') == name, action


def test_the_tutorial_list_marks_are_sprite_icons(page):
    page.evaluate("() => { const t = window._dxTutorial; if (t) t.showTOC(); }")
    page.wait_for_selector(".dxt-toc-check svg.dx-ico", state="attached", timeout=5000)
    names = page.evaluate("""() => [...document.querySelectorAll('.dxt-toc-check use')]
      .map(u => u.getAttribute('href').split('#')[1])""")
    assert names and set(names) <= {"check", "lock", "circle"}, names
    assert _icon(page, ".dxt-toc-title") == "graduation"

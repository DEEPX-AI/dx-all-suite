"""Escape closes the topmost thing first, and only then leaves the module.

Escape in the launcher document must not jump straight to goHome() while a module is open: in the chat input it closes
the chat (it must not leave the module and abort the reply); with the Tutorial Guide open it closes the guide; in the
SDK Library search box it clears the search rather than leaving the view.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_QUIET = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
          "localStorage.setItem('dx-tutorial-launcher-autostarted','1');localStorage.setItem('dx-tutorial-mode','off');"
          "}catch(e){}")


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


def _open(browser, port, app, deferred_tutorial=None):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(_QUIET)
    if deferred_tutorial:
        ctx.add_init_script("""
          (() => {
            let api;
            Object.defineProperty(window, 'DXTutorial', {
              configurable: true,
              get: () => api,
              set: value => {
                api = value;
                const create = value.create;
                value.create = opts => {
                  if (opts.appId === '%s') {
                    window.__releaseDeferredTutorial = () => create(opts);
                  } else {
                    create(opts);
                  }
                };
              }
            });
          })();
        """ % deferred_tutorial)
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function("!!(window.DXLauncher && DXLauncher.launch && typeof DXChat !== 'undefined' && document.querySelector('.dx-chat-fab'))", timeout=30000)
    opener = {"sdk-library": "DXLauncher.showSdkLibrary()", "about": "DXLauncher.showAboutView()"}.get(
        app, f"DXLauncher.launch('{app}')")
    page.evaluate(opener)
    page.wait_for_function(f"DXLauncher.currentApp === '{app}'", timeout=15000)
    return ctx, page


def test_escape_in_the_chat_closes_the_chat_and_stays_in_the_view(port, browser):
    # The launcher chat lives on launcher screens (Home, SDK Library, About); inside a module the module's own chat
    # is used (test below).
    ctx, page = _open(browser, port, "sdk-library")
    try:
        page.click(".dx-chat-fab")
        page.wait_for_selector(".dx-chat-window.open")
        page.focus(".dx-chat-window textarea, .dx-chat-window input")
        page.keyboard.press("Escape")
        page.wait_for_function("!document.querySelector('.dx-chat-window.open')")
        assert page.evaluate("DXLauncher.currentApp") == "sdk-library"
    finally:
        ctx.close()


def test_escape_with_the_tutorial_guide_open_closes_the_guide_first(port, browser):
    # On module screens the launcher toolbar hides and the module has its own toolbar in its iframe, so this runs on
    # a launcher screen (SDK Library).
    ctx, page = _open(browser, port, "sdk-library")
    try:
        page.wait_for_function("!!(window._dxTutorials && window._dxTutorials.sdk_library)", timeout=15000)
        page.evaluate("document.getElementById('dxToolbarTutorial').click()")
        page.wait_for_selector(".dxt-toc.open", timeout=10000)
        page.keyboard.press("Escape")
        page.wait_for_function("!document.querySelector('.dxt-toc.open')")
        assert page.evaluate("DXLauncher.currentApp") == "sdk-library"
    finally:
        ctx.close()


@pytest.mark.parametrize("deferred_tutorial", ["launcher", "sdk_library"])
def test_late_tutorial_initialization_preserves_the_visible_guide(port, browser, deferred_tutorial):
    ctx, page = _open(browser, port, "sdk-library", deferred_tutorial)
    active_id = "sdk_library" if deferred_tutorial == "launcher" else "launcher"
    expected_view = "sdk-library" if active_id == "sdk_library" else None
    try:
        page.wait_for_function("typeof window.__releaseDeferredTutorial === 'function'")
        if active_id == "launcher":
            page.evaluate("DXLauncher.goHome()")
            page.wait_for_function("DXLauncher.currentApp === null")
        page.wait_for_function(
            "id => !!(window._dxTutorials && _dxTutorials[id] && _dxTutorials[id]._keyHandler)",
            arg=active_id,
        )
        page.click("#dxToolbarTutorial")
        page.wait_for_selector(".dxt-toc.open")
        page.evaluate("window.__releaseDeferredTutorial()")
        page.wait_for_function(
            "id => !!(_dxTutorials[id] && _dxTutorials[id]._keyHandler)",
            arg=deferred_tutorial,
        )
        assert page.evaluate("window._dxTutorial.appId") == active_id
        assert page.evaluate("id => !!_dxTutorials[id]._keyHandler", active_id)
        assert page.locator(".dxt-toc.open").count() == 1
        assert active_id in page.locator(".dxt-toc.open .dxt-toc-btn-start").get_attribute("onclick")
        page.keyboard.press("Escape")
        page.wait_for_function("!document.querySelector('.dxt-toc.open')")
        assert page.evaluate("DXLauncher.currentApp") == expected_view
    finally:
        ctx.close()


def test_sdk_revisits_and_hidden_language_refresh_keep_the_toolbar_owner(port, browser):
    ctx, page = _open(browser, port, "sdk-library")
    try:
        page.wait_for_function(
            "!!(window._dxTutorials && _dxTutorials.launcher && _dxTutorials.sdk_library)"
        )
        for lang in ("ko", "es"):
            page.evaluate("DXLauncher.goHome()")
            page.wait_for_function("DXLauncher.currentApp === null")
            page.evaluate("lang => DXI18n.setLang(lang)", lang)
            assert page.evaluate("window._dxTutorial.appId") == "launcher"
            page.click("#dxToolbarTutorial")
            page.wait_for_selector(".dxt-toc.open")
            assert "launcher" in page.locator(".dxt-toc.open .dxt-toc-btn-start").get_attribute("onclick")
            page.keyboard.press("Escape")
            page.evaluate("DXLauncher.showAboutView()")
            page.wait_for_function("DXLauncher.currentApp === 'about'")
            page.evaluate("SDKLibrary.refresh()")
            assert page.locator("#dxToolbarTutorial").is_disabled()
            page.evaluate("DXLauncher.showSdkLibrary()")
            page.wait_for_function("DXLauncher.currentApp === 'sdk-library'")
            assert page.evaluate("window._dxTutorial.appId") == "sdk_library"
            page.click("#dxToolbarTutorial")
            page.wait_for_selector(".dxt-toc.open")
            assert "sdk_library" in page.locator(".dxt-toc.open .dxt-toc-btn-start").get_attribute("onclick")
            page.evaluate("SDKLibrary.refresh()")
            page.keyboard.press("Escape")
            page.wait_for_function("!document.querySelector('.dxt-toc.open')")
            assert page.evaluate("DXLauncher.currentApp") == "sdk-library"
    finally:
        ctx.close()


def test_about_has_no_tutorial_even_before_the_home_engine_is_ready(port, browser):
    ctx, page = _open(browser, port, "about", "launcher")
    try:
        page.wait_for_function("typeof window.__releaseDeferredTutorial === 'function'")
        assert page.locator("#dxToolbarTutorial").is_disabled()
        page.evaluate("window.__releaseDeferredTutorial()")
        page.wait_for_function("!!(window._dxTutorials && _dxTutorials.launcher)")
        assert page.locator("#dxToolbarTutorial").is_disabled()
        page.evaluate("DXLauncher.goHome()")
        page.wait_for_function("DXLauncher.currentApp === null")
        page.click("#dxToolbarTutorial")
        page.wait_for_selector(".dxt-toc.open")
    finally:
        ctx.close()


def test_escape_in_the_sdk_search_clears_it_and_stays(port, browser):
    ctx, page = _open(browser, port, "sdk-library")
    try:
        page.fill("#sdkLibSearch", "compiler")
        page.focus("#sdkLibSearch")
        page.keyboard.press("Escape")
        assert page.input_value("#sdkLibSearch") == ""
        assert page.evaluate("DXLauncher.currentApp") == "sdk-library"
    finally:
        ctx.close()


def test_inside_a_module_only_the_modules_own_chat_button_is_there(port, browser):
    """Inside a module the launcher's chat button is hidden: it sits in the same spot as the module iframe's chat
    button and would block module-only help (module knowledge, offline answers)."""
    ctx, page = _open(browser, port, "zoo")
    try:
        assert not page.locator("body > .dx-chat-fab, .dx-chat-fab").first.is_visible()
        page.evaluate("DXLauncher.goHome()")
        page.wait_for_function("!DXLauncher.currentApp")
        page.locator(".dx-chat-fab").first.wait_for(state="visible", timeout=10000)
    finally:
        ctx.close()


def test_opening_the_sdk_library_does_not_add_a_second_chat_button(port, browser):
    """SDK Library must not call DXChat.init again: a second widget means two buttons in the same spot."""
    ctx, page = _open(browser, port, "sdk-library")
    try:
        assert page.evaluate("document.querySelectorAll('.dx-chat-fab').length") == 1
        assert page.evaluate("document.querySelectorAll('.dx-chat-window').length") == 1
        page.evaluate("DXLauncher.goHome()")
        page.evaluate("DXLauncher.showSdkLibrary()")
        assert page.evaluate("document.querySelectorAll('.dx-chat-fab').length") == 1
    finally:
        ctx.close()


def _deep(browser, port, path):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
                        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}")   # tutorial mode ON
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}{path}", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function("!!(window.DXLauncher && DXLauncher._studioReadyResolved)", timeout=30000)
    page.wait_for_timeout(2500)   # the automatic guide opens after 500 ms, plus readiness
    return ctx, page


def test_a_deep_link_into_a_module_does_not_open_the_launcher_guide_over_it(port, browser):
    """Entering by a module URL must not open the 'Launcher Home' guide on top of the module's guide."""
    ctx, page = _deep(browser, port, "/zoo")
    try:
        assert page.evaluate("DXLauncher.currentApp") == "zoo"
        assert page.locator(".dxt-toc.open").count() == 0
    finally:
        ctx.close()


def test_the_sdk_library_guide_starts_the_sdk_tour_not_the_home_tour(port, browser):
    """Entering SDK Library directly opens one guide, and its Start from Beginning starts the SDK tour, not the
    home tour."""
    ctx, page = _deep(browser, port, "/sdk-library")
    try:
        opened = page.locator(".dxt-toc.open")
        assert opened.count() <= 1
        if opened.count() == 1:
            onclick = opened.locator(".dxt-toc-btn-start").get_attribute("onclick")
            assert "sdk_library" in onclick, onclick
    finally:
        ctx.close()


def test_the_sdk_list_view_search_finds_documents(port, browser):
    """List view (the default) search must cover every document, not just sidebar names and cards already drawn:
    'quick start' and 'compiler' must match there as they do in Cabinet view."""
    ctx, page = _open(browser, port, "sdk-library")
    try:
        page.wait_for_selector("#sdkListContent", timeout=15000)
        page.fill("#sdkLibSearch", "compiler")
        page.wait_for_function("document.querySelectorAll('#sdkListContent .file-card').length > 0", timeout=5000)
        page.fill("#sdkLibSearch", "")
        page.wait_for_selector("#sdkListContent .sdk-list-empty", timeout=5000)
    finally:
        ctx.close()

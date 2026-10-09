"""Escape closes the topmost thing first, and only then leaves the module (2026-10-02 release audit X-1 / A-1 / L-5).

Escape anywhere in the launcher document called goHome() while a module was open: pressed in the chat input it
left the module (and aborted the reply) with the chat still open; pressed with the Tutorial Guide open it left the
module too; in the SDK Library search box it left the view instead of clearing the search.
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
    # launcher 채팅은 launcher 의 화면 (홈 · SDK Library · About) 에 있다 — 모듈 안에서는 모듈 자신의 채팅 (아래 시험)
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
    # 모듈 화면에서는 launcher toolbar 가 숨고 모듈이 iframe 안에 자기 toolbar 를 가진다 — launcher 자신의 화면
    # (SDK Library) 에서 본다
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
    """launcher 의 채팅 버튼이 모듈 iframe 의 채팅 버튼을 같은 자리에서 덮어, 모듈 전용 도움말 (모듈 지식 · 오프라인 답) 을
    열 수 없었다 (2026-10-02 release audit X-2 / A-2). 모듈 안에서는 launcher 의 것을 숨긴다."""
    ctx, page = _open(browser, port, "zoo")
    try:
        assert not page.locator("body > .dx-chat-fab, .dx-chat-fab").first.is_visible()
        page.evaluate("DXLauncher.goHome()")
        page.wait_for_function("!DXLauncher.currentApp")
        page.locator(".dx-chat-fab").first.wait_for(state="visible", timeout=10000)
    finally:
        ctx.close()


def test_opening_the_sdk_library_does_not_add_a_second_chat_button(port, browser):
    """SDK Library 가 DXChat.init 을 다시 불러 위젯이 하나 더 생겼다 — 같은 자리에 버튼 두 개 (2026-10-02)."""
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
    page.wait_for_timeout(2500)   # 자동 목차는 500 ms 뒤 + 준비 대기
    return ctx, page


def test_a_deep_link_into_a_module_does_not_open_the_launcher_guide_over_it(port, browser):
    """모듈 URL 로 바로 들어오면 'Launcher Home' 목차가 모듈 목차 위에 같이 열렸다 (release audit X-3 / A-21)."""
    ctx, page = _deep(browser, port, "/zoo")
    try:
        assert page.evaluate("DXLauncher.currentApp") == "zoo"
        assert page.locator(".dxt-toc.open").count() == 0
    finally:
        ctx.close()


def test_the_sdk_library_guide_starts_the_sdk_tour_not_the_home_tour(port, browser):
    """SDK Library 로 바로 들어오면 목차가 둘 열리고, SDK 목차의 Start from Beginning 이 홈 투어를 시작했다 (L-3)."""
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
    """List 보기 (기본) 검색이 사이드바 이름과 이미 그려진 카드만 보아 'quick start' · 'compiler' 가 0 건이었다
    (Cabinet 보기는 찾았다). 2026-10-02 release audit L-4."""
    ctx, page = _open(browser, port, "sdk-library")
    try:
        page.wait_for_selector("#sdkListContent", timeout=15000)
        page.fill("#sdkLibSearch", "compiler")
        page.wait_for_function("document.querySelectorAll('#sdkListContent .file-card').length > 0", timeout=5000)
        page.fill("#sdkLibSearch", "")
        page.wait_for_selector("#sdkListContent .sdk-list-empty", timeout=5000)
    finally:
        ctx.close()

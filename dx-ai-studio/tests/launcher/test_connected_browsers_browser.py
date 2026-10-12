"""Connected browsers — the launcher's list of paired remote browsers, in a real browser.

The server side (status addresses, sessions API) is pinned in tests/shared/test_remote_access.py.
"""
from __future__ import annotations

import sys

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_QUIET = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
          "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}")
LAPTOP_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/128.0.0.0 Safari/537.36")
PHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")
REMOTE_IP = "192.168.0.99"


@pytest.fixture(scope="module")
def studio(tmp_path_factory):
    server, port = start_module_server("launcher")
    lmod = sys.modules["launcher.launcher"]
    from shared import remote_access as ra
    saved = lmod.REMOTE_ACCESS, lmod._lan_addresses
    lmod._lan_addresses = lambda: ["192.168.0.152"]
    try:
        yield lmod, ra, port, tmp_path_factory
    finally:
        lmod.REMOTE_ACCESS, lmod._lan_addresses = saved
        server.shutdown()


@pytest.fixture()
def access(studio, tmp_path):
    lmod, ra, _, _ = studio
    acc = ra.RemoteAccess(sessions=ra.SessionStore(tmp_path / "sessions.json", days=30),
                          pairing=ra.Pairing(announce=lambda code: None))
    lmod.REMOTE_ACCESS = acc
    yield acc
    lmod.REMOTE_ACCESS = None
    if "_peer_ip" in lmod.LauncherHandler.__dict__:
        del lmod.LauncherHandler._peer_ip


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _open(browser, port, width=1440, lang=None, cookie=None):
    ctx = browser.new_context(viewport={"width": width, "height": 900})
    script = _QUIET
    if lang:
        script += f"try{{localStorage.setItem('dx-lang','{lang}');}}catch(e){{}}"
    ctx.add_init_script(script)
    if cookie:
        ctx.add_cookies([{"name": "dx_session", "value": cookie, "domain": "127.0.0.1", "path": "/"}])
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
    return ctx, page, errors


def _rows(page):
    return page.locator("#remoteAccessDialog .ra-row")


def test_the_board_sees_who_is_connected_and_can_disconnect_one(studio, access, browser):
    _, _, port, _ = studio
    _, laptop = access.sessions.create(user_agent=LAPTOP_UA, ip=REMOTE_IP)
    access.sessions.create(user_agent=PHONE_UA, ip="192.168.0.77")
    ctx, page, errors = _open(browser, port)
    try:
        btn = page.locator("#dxToolbar #dxToolbarRemote")
        btn.wait_for(state="visible", timeout=30000)
        assert btn.get_attribute("aria-label") == "Connected browsers"
        btn.click()
        dlg = page.locator("#remoteAccessDialog")
        dlg.wait_for(state="visible")
        _rows(page).nth(1).wait_for()
        assert _rows(page).count() == 2
        text = dlg.inner_text()
        assert f"http://192.168.0.152:{port}" in text, "다른 컴퓨터가 열 주소를 알려 준다"
        assert "Chrome · Windows" in text and "Safari · iOS" in text
        assert access.pairing.code not in text, "코드는 콘솔에만"
        assert "This browser" not in text, "보드 자신은 목록에 없다"
        assert page.evaluate("document.getElementById('remoteAccessDialog').contains(document.activeElement)"), \
            "목록을 불러온 뒤에도 focus 가 대화상자 안에 있다"
        page.locator(f'#remoteAccessDialog .ra-row[data-session="{laptop}"] button').focus()
        page.keyboard.press("Enter")
        page.wait_for_function("document.querySelectorAll('#remoteAccessDialog .ra-row').length === 1")
        assert page.evaluate("document.activeElement.closest('.ra-row') !== null"), \
            "끊은 줄이 사라지면 focus 는 남은 줄의 단추로 (release audit L-19)"
        left = [s["id"] for s in access.sessions.list()]
        assert laptop not in left and len(left) == 1
        page.keyboard.press("Escape")
        dlg.wait_for(state="hidden")
        assert not errors, errors
    finally:
        ctx.close()


def test_with_nobody_connected_it_says_so_in_korean(studio, access, browser):
    _, _, port, _ = studio
    ctx, page, errors = _open(browser, port, lang="ko")
    try:
        btn = page.locator("#dxToolbarRemote")
        btn.wait_for(state="visible", timeout=30000)
        page.wait_for_function("document.getElementById('dxToolbarRemote').getAttribute('aria-label') === '연결된 브라우저'")
        btn.click()
        page.locator("#remoteAccessDialog .ra-empty").wait_for()
        text = page.locator("#remoteAccessDialog").inner_text()
        assert "연결된 브라우저" in text and "연결된 다른 컴퓨터가 없습니다." in text
        assert "./launcher.sh" in text
        assert not errors, errors
    finally:
        ctx.close()


def test_a_phone_width_dialog_does_not_scroll_sideways(studio, access, browser):
    _, _, port, _ = studio
    access.sessions.create(user_agent=LAPTOP_UA, ip=REMOTE_IP)
    ctx, page, _ = _open(browser, port, width=390)
    try:
        page.locator("#dxToolbarRemote").wait_for(state="attached", timeout=30000)
        page.evaluate("DXLauncher.remoteAccess.open()")
        _rows(page).first.wait_for()
        over = page.evaluate("""() => {
            const m = document.querySelector('#remoteAccessDialog .modal');
            const r = m.getBoundingClientRect();
            return {sw: m.scrollWidth, cw: m.clientWidth, right: r.right, vw: window.innerWidth};
        }""")
        assert over["sw"] <= over["cw"] + 1 and over["right"] <= over["vw"], over
    finally:
        ctx.close()


def test_a_remote_browser_sees_itself_and_disconnecting_returns_it_to_pairing(studio, access, browser):
    lmod, _, port, _ = studio
    token, _ = access.sessions.create(user_agent=LAPTOP_UA, ip=REMOTE_IP)
    lmod.LauncherHandler._peer_ip = lambda self: REMOTE_IP
    ctx, page, errors = _open(browser, port, cookie=token)
    try:
        page.locator("#dxToolbarRemote").wait_for(state="visible", timeout=30000)
        page.locator("#dxToolbarRemote").click()
        row = _rows(page).first
        row.wait_for()
        text = page.locator("#remoteAccessDialog").inner_text()
        assert "This browser" in text and "192.168.0.152" not in text, "주소 안내는 보드에만"
        with page.expect_navigation():
            row.locator("button").click()
        page.locator("#dx-pair").wait_for(timeout=15000)
        assert access.sessions.valid(token) is None
        assert not errors, errors
    finally:
        ctx.close()


def test_a_launcher_nobody_else_can_reach_has_no_button(studio, browser):
    lmod, _, port, _ = studio
    lmod.REMOTE_ACCESS = None
    ctx, page, _ = _open(browser, port)
    try:
        page.wait_for_function("!!document.getElementById('dxToolbarTutorial')", timeout=30000)
        page.wait_for_timeout(2000)  # wait for the status response (the health poll keeps networkidle from arriving)
        assert page.locator("#dxToolbarRemote").count() == 0
    finally:
        ctx.close()

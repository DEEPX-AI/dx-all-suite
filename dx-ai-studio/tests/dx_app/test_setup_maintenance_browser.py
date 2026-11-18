"""Setup page on screen: backend command lines, Maintenance (typed RESET → sudo → run → Quick Start), NPU sanity row.

Backend answers are routed fixtures, so nothing is installed or removed on this machine."""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

STEPS = ["dx-app-deps", "dx-rt-deps", "dx-rt-build", "dx-driver", "dx-app-build", "dx-app-setup"]
STATUS = {sid: {"ok": True, "detail": "ok"} for sid in STEPS}
STATUS.update({
    "versions": {"dx_app": "3.0.0"},
    "commands": {sid: f"cmd-for-{sid} --arch aarch64" for sid in STEPS},
    "runtime-reset": {"confirm": "RESET"},
    "disk": {"free_gb": 50.0, "min_gb": 5.0},
})
DIAG = {"checks": [
    {"id": "pcie_link", "label": {"en": "PCIe Link (DeepX)"}, "ok": True, "detail": "ok"},
    {"id": "npu_sanity", "label": {"en": "NPU sanity check", "ko": "NPU sanity check"}, "ok": False,
     "pending": True, "detail": "Needs administrator password"},
], "passed": 1, "total": 1, "all_ok": True}


@pytest.fixture(scope="module")
def server():
    srv, port = start_module_server("dx_app")
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


def _open(browser, port, lang="en"):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script(f"localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','{lang}');")
    page = ctx.new_page()
    calls = {"run": [], "sanity": []}
    page.route("**/api/setup/status", lambda r, *_: r.fulfill(json=STATUS))
    page.route("**/api/setup/diagnostics", lambda r, *_: r.fulfill(json=json.loads(json.dumps(DIAG))))

    def run(route, *_):
        calls["run"].append(route.request.post_data_json)
        route.fulfill(json={"ok": True, "started": True})

    def sanity(route, *_):
        calls["sanity"].append(route.request.post_data_json)
        route.fulfill(json={"state": "passed", "detail": "", "log": "** Sanity check PASSED!"})

    page.route("**/api/setup/run", run)
    page.route("**/api/setup/sanity", sanity)
    page.route("**/api/setup/log", lambda r, *_: r.fulfill(json={"log": "done", "done": True, "exit_code": 0}))
    page.route("**/api/setup/quick-start-plan", lambda r, *_: r.fulfill(json={"plan": []}))
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.click('.dx-tab[data-page="setup"]')
    page.wait_for_function("() => document.querySelector('#setup-steps [data-step=\"dx-app-build\"] .dx-step-cmd code')"
                           ".textContent.indexOf('cmd-for-dx-app-build')===0", timeout=10000)
    return ctx, page, calls


def _sudo(page, password="pw"):
    page.wait_for_selector("#setup-sudo-password")
    page.fill("#setup-sudo-password", password)
    page.click("#setup-sudo-ok")


def test_card_command_lines_come_from_the_backend(browser, server):
    ctx, page, _ = _open(browser, server)
    try:
        text = page.locator('#setup-steps [data-step="dx-app-build"] .dx-step-cmd code').inner_text()
        assert text == "cmd-for-dx-app-build --arch aarch64"
    finally:
        ctx.close()


def test_reset_needs_the_typed_word_then_sudo_then_runs_and_starts_quick_start(browser, server):
    ctx, page, calls = _open(browser, server)
    try:
        page.click("#setup-maint > summary")
        page.click("#setup-reset-btn")
        ok = page.locator("#setup-reset-ok")
        assert ok.is_disabled()
        page.fill("#setup-reset-word", "RESE")
        assert ok.is_disabled()
        page.fill("#setup-reset-word", "RESET")
        assert ok.is_enabled()
        ok.click()
        _sudo(page)
        page.wait_for_function("() => document.getElementById('setup-try-demo').style.display === ''", timeout=15000)
        body = calls["run"][0]
        assert body["step"] == "runtime-reset" and body["confirm"] == "RESET" and body["password"] == "pw"
    finally:
        ctx.close()


def test_reset_cancel_closes_without_running(browser, server):
    ctx, page, calls = _open(browser, server)
    try:
        page.click("#setup-maint > summary")
        page.click("#setup-reset-btn")
        page.click("#setup-reset-cancel")
        assert page.locator("#setup-reset-modal").count() == 0 and not calls["run"]
    finally:
        ctx.close()


def test_pending_sanity_row_runs_with_the_password_and_updates_the_totals(browser, server):
    ctx, page, calls = _open(browser, server)
    try:
        page.click("#diag-run-btn")
        btn = page.locator("#diag-results .diag-card-pending button")
        btn.wait_for()
        btn.click()
        _sudo(page, "secret")
        page.wait_for_function("() => !document.querySelector('#diag-results .diag-card-pending')"
                               " && document.querySelectorAll('#diag-results .diag-card-ok').length === 2")
        assert calls["sanity"] == [{"password": "secret"}]
        assert "2/2" in page.locator("#diag-summary").inner_text()
    finally:
        ctx.close()


@pytest.mark.parametrize("lang,words", [("ko", ("유지보수", "관리자 비밀번호 필요", "초기화 후 재설치")),
                                        ("ja", ("メンテナンス", "管理者パスワードが必要", "リセットして再インストール"))])
def test_new_ui_speaks_the_page_language(browser, server, lang, words):
    ctx, page, _ = _open(browser, server, lang)
    try:
        page.click("#diag-run-btn")
        page.locator("#diag-results .diag-card-pending").wait_for()
        page.click("#setup-maint > summary")
        text = page.locator("#page-setup").inner_text()
        for w in words:
            assert w in text, (lang, w)
        for english in ("Reset and reinstall", "Needs administrator password", "Clean C++ build"):
            assert english not in text, (lang, english)
    finally:
        ctx.close()


def test_failed_sanity_shows_the_fix_in_the_page_language(browser, server):
    """Fix texts use the standard 'zh-CN' key (the i18n audit reads those); older rows use 'zhCN' — both render."""
    from dx_app.core.setup_steps import _COLD_BOOT
    ctx, page, _ = _open(browser, server, "zh-CN")
    try:
        page.route("**/api/setup/sanity", lambda r, *_: r.fulfill(json={
            "state": "failed", "detail": "[ERROR] Fail to initialize device", "fix": _COLD_BOOT, "log": "x"}))
        page.click("#diag-run-btn")
        page.locator("#diag-results .diag-card-pending button").click()
        _sudo(page)
        page.locator("#diag-results .diag-card-fail .diag-card-fix").wait_for()
        assert _COLD_BOOT["zh-CN"] in page.locator("#diag-results").inner_text()
    finally:
        ctx.close()

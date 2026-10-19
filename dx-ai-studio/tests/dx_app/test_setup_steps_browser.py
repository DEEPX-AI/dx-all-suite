"""dx_app Setup's step list behaves as promised on screen.

Status is a fixture (route /api/setup/status) so results do not depend on what is installed on this machine.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

STEPS = ["dx-app-deps", "dx-rt-deps", "dx-rt-build", "dx-driver", "dx-app-build", "dx-app-setup"]
DETAIL = {"dx-app-deps": "cmake · gcc · ninja", "dx-rt-deps": "v3.4.2", "dx-rt-build": "dx_engine v3.4.2 (venv-dx-runtime)",
          "dx-driver": "dxrt0", "dx-app-build": "build_x86_64/ found", "dx-app-setup": "11 model(s), 0 video(s)"}


def _status(not_done=("dx-app-setup",)):
    st = {sid: {"ok": sid not in not_done, "detail": DETAIL[sid]} for sid in STEPS}
    st["versions"] = {"dx_app": "3.0.0", "dx_runtime": "3.4.2"}
    return st


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


def _open(browser, port, status, width=1440, height=900):
    ctx = browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');")
    page = ctx.new_page()
    page.route("**/api/setup/status", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(status)))
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.click('.dx-tab[data-page="setup"]')
    page.wait_for_function("() => document.getElementById('setup-steps').dataset.ready !== undefined"
                           " && document.querySelector('#setup-steps .dx-step[data-state=\"done\"]')", timeout=8000)
    return ctx, page


def test_the_header_counts_what_is_ready(browser, server):
    ctx, page = _open(browser, server, _status())
    try:
        assert page.inner_text("#setup-steps [data-steps-count]").strip() == "5 of 6 ready"
        bar = page.evaluate("() => [...document.querySelectorAll('#setup-steps .dx-steps-bar > i')].map(i => i.className)")
        assert bar == ["is-done"] * 5 + ["is-next"], bar
        assert page.inner_text("#setup-run-all [data-steps-left]").strip() == "(1)"
    finally:
        ctx.close()


def test_only_the_next_step_is_open(browser, server):
    ctx, page = _open(browser, server, _status())
    try:
        open_ = page.evaluate("() => [...document.querySelectorAll('#setup-steps .dx-step.is-open')].map(li => li.dataset.step)")
        assert open_ == ["dx-app-setup"], open_
        heights = page.evaluate("""() => [...document.querySelectorAll('#setup-steps .dx-step')]
          .map(li => li.querySelector('button').getBoundingClientRect().height)""")
        assert heights[:5] == [0] * 5 and heights[5] > 0, heights
        badge = page.inner_text("#setup-badge-dx-app-deps").strip()
        assert badge == "Ready", badge
        facts = page.evaluate("() => [...document.querySelectorAll('[data-step=\"dx-app-deps\"] .dx-step-facts span')].map(s => s.textContent)")
        assert facts == ["cmake", "gcc", "ninja"], facts
    finally:
        ctx.close()


def test_a_collapsed_row_opens_when_clicked(browser, server):
    ctx, page = _open(browser, server, _status())
    try:
        page.click('[data-step="dx-driver"] .dx-step-title')
        assert page.evaluate("() => document.querySelector('[data-step=\"dx-driver\"]').classList.contains('is-open')")
        assert page.is_visible("button[onclick*=\"dx-driver\"]")
    finally:
        ctx.close()


def test_when_everything_is_ready_there_is_nothing_to_run(browser, server):
    ctx, page = _open(browser, server, _status(not_done=()))
    try:
        assert page.inner_text("#setup-steps [data-steps-count]").strip() == "6 of 6 ready"
        assert page.is_hidden("#setup-run-all")
        assert page.evaluate("() => document.querySelectorAll('#setup-steps .dx-step.is-open').length") == 0
    finally:
        ctx.close()


def test_the_list_fits_one_screen(browser, server):
    """The step list fits on one screen at 1280×800 (two columns of six cards would fold from the third row)."""
    ctx, page = _open(browser, server, _status(), width=1280, height=800)
    try:
        bottom = page.evaluate("() => document.querySelector('#setup-steps .dx-steps-list').getBoundingClientRect().bottom")
        assert bottom <= 800, bottom
    finally:
        ctx.close()


DIAG = {"all_ok": False, "passed": 1, "total": 2, "checks": [
    {"id": "kmod_dxrt", "ok": True, "detail": "Loaded",
     "label": {"ko": "커널 모듈 (dxrt_driver)", "en": "Kernel Module (dxrt_driver)", "ja": "カーネルモジュール (dxrt_driver)",
               "zhCN": "内核模块 (dxrt_driver)", "zhTW": "核心模組 (dxrt_driver)", "es": "Módulo del kernel (dxrt_driver)"}},
    {"id": "disk", "ok": False, "detail": "3.2 GB free / 512 GB total",
     "label": {"en": "Disk Space (≥5GB free)", "es": "Espacio en disco (≥5 GB libres)"},
     "fix": {"en": "Free up disk space (clear build artifacts, logs, etc.)",
             "es": "Libere espacio en disco (artefactos de compilación, registros, etc.)"}}]}


def test_server_facts_and_diagnostics_speak_the_language(browser, server):
    """Setup's fact chips ("11 model(s), 0 video(s)") and diagnostics (label · detail · fix) follow the chosen
    language, Spanish included, and diagnostics re-render when the language changes."""
    ctx, page = _open(browser, server, _status())
    page.route("**/api/setup/diagnostics", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(DIAG)))
    try:
        page.evaluate("() => DXI18n.setLang('es')")
        page.wait_for_function("() => document.getElementById('setup-steps').innerText.includes('11 modelos, 0 videos')",
                               timeout=8000)
        assert "build_x86_64/ encontrado" in page.inner_text("#setup-steps")
        page.evaluate("() => runDiagnostics()")
        page.wait_for_selector("#diag-results .diag-card", timeout=8000)
        txt = page.inner_text("#diag-results")
        assert "Módulo del kernel (dxrt_driver)" in txt and "Cargado" in txt
        assert "3.2 GB libres / 512 GB en total" in txt and "Libere espacio en disco" in txt
        assert "comprobaciones superadas" in page.inner_text("#diag-summary")
        page.evaluate("() => DXI18n.setLang('ja')")
        page.wait_for_function("() => document.getElementById('diag-results').innerText.includes('ロード済み')", timeout=5000)
        assert "カーネルモジュール (dxrt_driver)" in page.inner_text("#diag-results")
    finally:
        page.evaluate("() => DXI18n.setLang('en')")
        ctx.close()

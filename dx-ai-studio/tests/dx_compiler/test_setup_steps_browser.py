"""The dx_compiler Setup panel behaves on screen as promised.

State is pinned by fixtures (routes /setup/status and /feature-check), whether or not the SDK is on this PC.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

MODELS = ("yolov5s", "resnet50", "mobilenetv2", "deeplabv3")


def _status(sdk=True, samples=True):
    return {
        "dx_com_installed": sdk, "dx_com_version": "2.1.0" if sdk else None,
        "venv_path": None, "venv_python": None, "install_requires_sudo": False,
        "sample_models": {m: {"downloaded": samples, "onnx_path": f"/tmp/{m}.onnx" if samples else None,
                              "config_path": f"/tmp/{m}.json" if samples else None} for m in MODELS},
        "calibration_data": {"downloaded": samples},
    }


@pytest.fixture(scope="module")
def server():
    srv, port = start_module_server("dx_compiler")
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


def _open(browser, port, status, compile_ok=True):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');")
    page = ctx.new_page()
    page.route("**/setup/status", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(status)))
    feature = {"compile": compile_ok, "setup_available": True, "capabilities": {"node_selection": compile_ok}, "warnings": []}
    page.route("**/feature-check", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(feature)))
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.wait_for_function("() => !document.getElementById('setup-panel').hasAttribute('aria-busy')", timeout=8000)
    page.wait_for_timeout(200)
    return ctx, page


def test_when_everything_is_set_the_panel_is_one_line(browser, server):
    ctx, page = _open(browser, server, _status())
    try:
        assert page.is_visible("#setup-summary")
        assert page.is_hidden("#setup-header") and page.is_hidden("#setup-install-btn")
        text = page.inner_text("#setup-summary")
        assert "Setup ready" in text and "SDK v2.1.0" in text and "4 sample models" in text, text
        h = page.evaluate("() => document.getElementById('setup-panel').getBoundingClientRect().height")
        assert h < 80, h
        assert page.is_enabled("#compile-main-btn")
        assert page.is_hidden("#compile-gate-reason")
    finally:
        ctx.close()


def test_the_one_line_opens_and_folds_back(browser, server):
    ctx, page = _open(browser, server, _status())
    try:
        page.click("#setup-summary")
        assert page.is_visible("#setup-header")
        page.click('#setup-samples .dx-step-title')
        assert page.is_visible("#setup-download-btn")
        assert page.inner_text("#setup-download-btn").strip() == "Re-download"
        page.click("#setup-toggle")
        assert page.is_visible("#setup-summary") and page.is_hidden("#setup-header")
    finally:
        ctx.close()


def test_without_the_sdk_the_next_step_is_open_and_compile_says_why(browser, server):
    ctx, page = _open(browser, server, _status(sdk=False, samples=False))
    try:
        assert page.is_hidden("#setup-summary")
        assert page.inner_text("#setup-panel [data-steps-count]").strip() == "0 of 2 ready"
        assert page.is_visible("#setup-install-btn")
        assert page.inner_text("#setup-install-btn").strip() == "Install"
        assert page.inner_text("#setup-sdk-icon").strip() == "Needs setup"
        assert page.is_disabled("#compile-main-btn")
        assert page.inner_text("#compile-gate-reason").strip() == "Install the SDK first"
        assert page.get_attribute("#compile-main-btn", "aria-describedby") == "compile-gate-reason"
    finally:
        ctx.close()


def test_a_server_without_compile_locks_even_when_the_sdk_looks_installed(browser, server):
    ctx, page = _open(browser, server, _status(), compile_ok=False)
    try:
        page.wait_for_function("() => document.getElementById('compile-main-btn').disabled", timeout=5000)
        assert "dx_com not installed on server" in page.inner_text("#compile-gate-reason")
    finally:
        ctx.close()


def test_the_tour_can_point_into_the_folded_panel(browser, server):
    ctx, page = _open(browser, server, _status())
    try:
        page.evaluate("() => setupPanel.revealForTour()")
        assert page.is_visible("#setup-toggle") and page.is_visible("#setup-install-btn")
        assert page.is_visible("#setup-download-btn")
    finally:
        ctx.close()

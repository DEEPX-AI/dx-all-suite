"""dx_stream Setup's step list behaves as promised on screen.

Status is fixed by fixtures (route /api/setup/status · /api/status), independent of this PC's install state.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

STEPS = ["stream-deps", "runtime-deps", "driver", "build", "download-models", "webrtc-deps"]


def _status(webrtc=False, models=True):
    setup = {"build": {"ok": True, "path": "/usr/local/lib/gstreamer-1.0/libgstdxstream.so"},
             "download-models": {"ok": models, "total": 12, "installed": 12 if models else 3}}
    system = {
        "npu": {"ok": True, "devices": ["/dev/dxrt0"]},
        "gstreamer": {"ok": True, "installed": True, "plugin": True},
        "build": setup["build"],
        "models": {"ok": models, "total": 12, "installed": setup["download-models"]["installed"]},
        "videos": {"ok": True, "count": 5},
        "webrtc": {"ok": webrtc, "nice_plugin": webrtc},
        "system_info": {"os": "Ubuntu 24.04", "gstreamer_version": "1.24.2", "npu_driver_version": "1.8.0",
                        "python_version": "3.12.3"},
    }
    return setup, system


@pytest.fixture(scope="module")
def server():
    srv, port = start_module_server("dx_stream")
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
    setup, system = status
    ctx = browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');")
    page = ctx.new_page()
    page.route("**/api/setup/status", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(setup)))
    page.route("**/api/status", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(system)))
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.click('.dx-tab[data-page="setup"]')
    page.wait_for_function("() => document.querySelectorAll('#setup-steps .dx-step[data-state=\"done\"]').length >= 4",
                           timeout=8000)
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


def test_only_the_next_step_is_open_and_done_rows_carry_facts(browser, server):
    ctx, page = _open(browser, server, _status())
    try:
        open_ = page.evaluate("() => [...document.querySelectorAll('#setup-steps .dx-step.is-open')].map(li => li.dataset.step)")
        assert open_ == ["webrtc-deps"], open_
        assert page.inner_text("#setup-badge-driver").strip() == "Ready"
        facts = page.evaluate("""() => Object.fromEntries([...document.querySelectorAll('#setup-steps .dx-step')]
          .map(li => [li.dataset.step, [...li.querySelectorAll('.dx-step-facts span')].map(s => s.textContent)]))""")
        assert facts["driver"] == ["dxrt0", "1.8.0"], facts
        assert facts["build"] == ["libgstdxstream.so"], facts
        assert facts["download-models"] == ["12/12 files"], facts
        assert facts["webrtc-deps"] == [], "끝나지 않은 단계에는 사실을 붙이지 않는다"
        logs = page.evaluate("() => [...document.querySelectorAll('#setup-steps pre.log-output')].map(p => p.offsetHeight)")
        assert logs == [0] * 6, "빈 로그 상자가 보인다"
    finally:
        ctx.close()


def test_a_collapsed_row_opens_when_clicked(browser, server):
    ctx, page = _open(browser, server, _status())
    try:
        assert not page.is_visible("#setup-opt-clean")
        page.click('[data-step="build"] .dx-step-title')
        assert page.is_visible("#setup-opt-clean")
        assert page.is_visible("button[onclick*=\"runSetup('build')\"]")
    finally:
        ctx.close()


def test_when_everything_is_ready_there_is_nothing_to_run(browser, server):
    ctx, page = _open(browser, server, _status(webrtc=True))
    try:
        page.wait_for_function("() => document.getElementById('setup-steps').dataset.ready === '6'", timeout=5000)
        assert page.inner_text("#setup-steps [data-steps-count]").strip() == "6 of 6 ready"
        assert page.is_hidden("#setup-run-all")
    finally:
        ctx.close()


def test_the_environment_table_uses_icons_and_words(browser, server):
    ctx, page = _open(browser, server, _status())
    try:
        page.wait_for_function("() => document.querySelector('#env-webrtc-status svg.dx-ico')", timeout=5000)
        assert page.inner_text("#env-gst-status").strip() == "Ready"
        assert page.inner_text("#env-webrtc-status").strip() == "Needs setup"
    finally:
        ctx.close()


def test_the_list_fits_one_screen(browser, server):
    ctx, page = _open(browser, server, _status(), width=1280, height=800)
    try:
        bottom = page.evaluate("() => document.querySelector('#setup-steps .dx-steps-list').getBoundingClientRect().bottom")
        assert bottom <= 800, bottom
    finally:
        ctx.close()

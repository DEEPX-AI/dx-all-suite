"""A Korean config wizard shows the server's preprocessing refusals in Korean (B3 / SR-758).

The wizard appends ``data.error`` through ``_srvErr`` (shared/static/server-error-i18n.js). The
arithmetic-transform messages validation.py added must be matched there too, or a Korean user
reads a Korean prefix followed by an English sentence.
"""
from __future__ import annotations

import re

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

MESSAGES = {
    "Invalid preprocessings[0].div.x: 'not-a-number' — expected a finite number "
    "or a non-empty list of finite numbers":
        "preprocessings[0].div.x의 'not-a-number'을(를) 쓸 수 없습니다",
    "Invalid preprocessings[0].div.x: contains 0 — division by zero":
        "preprocessings[0].div.x에 0이 있습니다 — 0으로 나눌 수 없습니다",
}


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_compiler")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','ko');")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


@pytest.mark.parametrize("message", list(MESSAGES))
def test_the_wizard_shows_the_arithmetic_refusals_in_korean(page, message):
    shown = page.evaluate("m => _srvErr(m)", message)
    assert MESSAGES[message] in shown, shown
    assert not re.search(r"expected a finite|division by zero", shown), shown

"""Agent Dev's console starts on the Studio agent and saves a change, like Home (spec 2026-10-11 chat settings §3.5)."""
from __future__ import annotations

import json
import os

import pytest

pytest.importorskip("playwright.sync_api")

from shared import agent_cli  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture(scope="module")
def port():
    saved = os.environ.get("DX_AGENT_DEV_PIN_AGENTS")
    os.environ["DX_AGENT_DEV_PIN_AGENTS"] = "copilot,claude"
    srv, port = start_module_server("dx_agent_dev")
    yield port
    srv.shutdown()
    agent_cli._studio_path().unlink(missing_ok=True)
    if saved is None:
        os.environ.pop("DX_AGENT_DEV_PIN_AGENTS", None)
    else:
        os.environ["DX_AGENT_DEV_PIN_AGENTS"] = saved


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _console(browser, port):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','en')}catch(e){}")
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    page.wait_for_selector("#agent-controls:not([hidden])", state="attached", timeout=20000)
    return ctx, page


def test_the_console_starts_on_the_studio_agent(browser, port):
    agent_cli.set_studio_agent("claude", None)
    ctx, page = _console(browser, port)
    try:
        assert page.evaluate("document.getElementById('agent-select').value") == "claude"
    finally:
        ctx.close()


def test_changing_the_agent_in_the_console_saves_it(browser, port):
    agent_cli.set_studio_agent("claude", None)
    ctx, page = _console(browser, port)
    try:
        page.select_option("#agent-select", "copilot")
        page.wait_for_function("1")
        for _ in range(30):
            got = agent_cli.studio_agent()
            if got and got["agent"] == "copilot":
                break
            page.wait_for_timeout(100)
        assert agent_cli.studio_agent()["agent"] == "copilot"
    finally:
        ctx.close()

"""Agent Dev takes over and renders a run that home started.

`attachIfRunning()` must open a conversation turn (`beginTurn`) as well as attach to the stream; otherwise the
message and command renderers drop everything (`if (!_turn) return`) and "Go to agent dev" shows no live output.
"""
from __future__ import annotations

import json
import os
import threading
import urllib.request

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

REPLY = "## Plan\n1. read\n2. build"


@pytest.fixture()
def agent(monkeypatch):
    monkeypatch.setenv("DX_AGENT_ADAPTER", "mock")
    monkeypatch.setenv("DX_AGENT_MOCK_DELAY", "0.5")
    monkeypatch.setenv("DX_AGENT_MOCK_REPLY", REPLY)
    server, port = start_module_server("dx_agent_dev")
    try:
        yield port
    finally:
        server.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _start_run_elsewhere(port, prompt):
    """A run home started and left: read only the first line, then disconnect (the server keeps the run)."""
    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/agent/run",
                                 data=json.dumps({"prompt": prompt, "mode": "interactive"}).encode(),
                                 headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=30)
    resp.readline()
    resp.close()


def test_the_module_draws_a_run_it_did_not_start(agent, browser):
    _start_run_elsewhere(agent, "make a pose demo")
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off')}catch(e){}")
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{agent}/#ask=make%20a%20pose%20demo", wait_until="domcontentloaded")
        page.wait_for_selector("#console-output .chat-turn", timeout=10000)
        assert page.inner_text("#console-output .chat-turn .user-line") == "make a pose demo"
        page.wait_for_function("document.querySelector('#console-output .assistant-body')"
                               " && /read/.test(document.querySelector('#console-output .assistant-body').textContent)",
                               timeout=15000)
        assert page.locator("#console-output .chat-turn").count() == 1
    finally:
        ctx.close()


def test_an_open_console_picks_up_a_run_when_it_is_shown_again(agent, browser):
    """The launcher keeps module iframes alive, so Agent Dev opened earlier is not loaded again.

    Opened before a run started on home (or in Auto Compile), it read the status once, found nothing, and
    showed nothing when the user came back to it. Being shown again (`dx-module-shown` from the launcher)
    must attach to the run that is going.
    """
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off')}catch(e){}")
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{agent}/", wait_until="domcontentloaded")
        page.wait_for_function("document.querySelector('#console-badge, .status-badge') !== null", timeout=10000)
        page.wait_for_timeout(1500)
        assert page.locator("#console-output .chat-turn").count() == 0

        _start_run_elsewhere(agent, "make a squat game")
        page.evaluate("window.postMessage({type: 'dx-module-shown'}, '*')")
        page.wait_for_selector("#console-output .chat-turn", timeout=10000)
        assert page.inner_text("#console-output .chat-turn .user-line") == "make a squat game"

        # Shown again while it is already drawing that run: no second copy.
        page.evaluate("window.postMessage({type: 'dx-module-shown'}, '*')")
        page.wait_for_timeout(1500)
        assert page.locator("#console-output .chat-turn").count() == 1
    finally:
        ctx.close()

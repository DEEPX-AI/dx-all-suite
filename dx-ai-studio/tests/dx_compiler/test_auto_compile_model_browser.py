"""Agentic Auto Compile model picker (2026-10-11 real-use audit).

- The CLI's live default was ignored: the static default ("auto" for copilot) was already selected
  when the live list arrived and the refresh kept it, so the page opened on "auto" with the
  "Current model may reduce instruction following quality" warning although copilot itself
  defaults to claude-sonnet-5.5. Agent Dev had the same bug and fixed it; the Compiler copy was not.
- Picking a model by hand never re-checked the warning: it stayed after choosing Sonnet, and
  choosing auto did not show it.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

COPILOT = {"name": "copilot", "authenticated": True, "models": ["auto", "claude-sonnet-5.5", "gpt-5-mini"],
           "default_model": "auto", "reasoning_efforts": ["low", "medium"], "default_effort": "medium"}
LIVE = {"agent": "copilot", "models": ["auto", "claude-sonnet-5.5", "claude-opus-5.5", "gpt-5-mini"],
        "default_model": "claude-sonnet-5.5"}


@pytest.fixture()
def page():
    from playwright.sync_api import sync_playwright

    server, port = start_module_server("dx_compiler")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','en')}catch(e){}")
    pg = ctx.new_page()
    pg.route("**/agent/api/agent/status", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps({"available": True, "agents": [COPILOT]})))
    pg.route("**/agent/api/agent/models?agent=copilot", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps(LIVE)))
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    server.shutdown()


def _hint_visible(page):
    return page.locator("#agentic-model-quality-hint").is_visible()


def test_the_cli_default_model_wins_over_the_static_one(page):
    page.wait_for_function("document.querySelectorAll('#agentic-model-select option').length === 4", timeout=5000)
    assert page.input_value("#agentic-model-select") == "claude-sonnet-5.5"
    assert not _hint_visible(page)


def test_picking_a_model_rechecks_the_warning(page):
    page.wait_for_function("document.querySelectorAll('#agentic-model-select option').length === 4", timeout=5000)
    page.select_option("#agentic-model-select", "auto")
    assert _hint_visible(page)
    page.select_option("#agentic-model-select", "claude-opus-5.5")
    assert not _hint_visible(page)
    page.select_option("#agentic-model-select", "gpt-5-mini")
    assert _hint_visible(page)


def test_a_late_live_list_keeps_the_users_pick(page):
    """The live list can land after the user already chose; it must not snap back to the default."""
    held = []
    page.unroute("**/agent/api/agent/models?agent=copilot")
    page.route("**/agent/api/agent/models?agent=copilot", lambda r: held.append(r))
    page.evaluate("document.getElementById('agentic-agent-select').dispatchEvent(new Event('change'))")
    page.wait_for_function("document.querySelectorAll('#agentic-model-select option').length === 3", timeout=5000)
    page.select_option("#agentic-model-select", "gpt-5-mini")
    for _ in range(50):
        if held:
            break
        page.wait_for_timeout(100)
    held[0].fulfill(status=200, content_type="application/json", body=json.dumps(LIVE))
    page.wait_for_function("document.querySelectorAll('#agentic-model-select option').length === 4", timeout=5000)
    assert page.input_value("#agentic-model-select") == "gpt-5-mini"

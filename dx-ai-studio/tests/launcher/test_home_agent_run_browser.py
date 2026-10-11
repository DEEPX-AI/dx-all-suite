"""home 에서 agent 를 돌리는 길 (spec 2026-09-30 home agent run).

사용자가 본 것: model 선택이 떴다 안 떴다 한다 · 계획 글에 줄바꿈이 없다 · 늘 auto 같다 (답할 곳이
없다). 각각의 원인은 spec 의 표 — 여기서는 고쳐진 행동을 실제 browser 에서 본다. agent 는 mock 이다
(tests/conftest.py 가 진짜 CLI 실행을 막는다).
"""
from __future__ import annotations

import json
import os
import sys

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

REPLY = "## Plan\n1. read the model\n2. build the app\n\nShall I proceed?"
_ENV = {
    "DX_AGENT_ADAPTER": "mock",
    "DX_AGENT_MOCK_DELAY": "0.12",
    "DX_AGENT_MOCK_REPLY": REPLY,
    "DX_AGENT_DEV_PIN_AGENTS": "copilot,claude",
}
_QUIET = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
          "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}")


@pytest.fixture(scope="module")
def port():
    """launcher + 진짜 agent dev server (mock adapter). test 용 launcher 는 module 을 띄우지 않으므로
    agent dev 를 따로 띄우고 launcher 의 proxy 표에 그 port 를 적는다 — SSE 까지 실제 경로로 간다."""
    saved = {k: os.environ.get(k) for k in _ENV}
    os.environ.update(_ENV)
    # These tests are about copilot's model list. Home now starts on the Studio agent, then the first signed-in in
    # Studio order (claude before copilot) — so pick copilot as the Studio agent, as a user who chose it would.
    from shared import agent_cli
    agent_cli.set_studio_agent("copilot", None)
    agent, agent_port = start_module_server("dx_agent_dev")
    server, port = start_module_server("launcher")
    sys.modules["launcher.launcher"]._LAUNCHER_PROXY_PORTS["dx_agent_dev"] = agent_port
    try:
        yield port
    finally:
        agent_cli._studio_path().unlink(missing_ok=True)
        server.shutdown()
        agent.shutdown()
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _home(browser, port, route=None):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(_QUIET)
    if route:
        ctx.route(*route)
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function("!!(window.DXLauncher && window.DXLauncher.homeAgentStart)", timeout=30000)
    # The home is visibility:hidden until boot ends (html.launcher-boot-pending); innerText of a hidden badge is ''.
    page.wait_for_function("!document.documentElement.classList.contains('launcher-boot-pending')", timeout=30000)
    return ctx, page


def _runs(page):
    bodies = []
    page.on("request", lambda r: bodies.append(json.loads(r.post_data or "{}"))
            if r.url.endswith("/agent/api/agent/run") and r.method == "POST" else None)
    return bodies


def _wait_done(page, n=1):
    page.wait_for_function(f"document.querySelectorAll('#workNarration .work-turn').length >= {n} && "
                           "!document.getElementById('homeWork').classList.contains('is-running')",
                           timeout=30000)


def test_the_setup_waits_for_a_module_that_is_not_up_yet(browser, port):
    calls = {"n": 0}

    def flaky(route):
        calls["n"] += 1
        if calls["n"] <= 2:
            route.fulfill(status=502, body="Proxy error")
        else:
            route.continue_()

    ctx, page = _home(browser, port, route=("**/agent/api/agent/status", flaky))
    try:
        page.wait_for_selector("#setupForm:not([hidden])", state="attached", timeout=15000)
        assert calls["n"] >= 3, "다시 묻지 않고 보였다면 502 를 맞지 않은 것"
        assert page.evaluate("document.querySelectorAll('#setupAgent option').length") >= 1
    finally:
        ctx.close()


def test_the_answer_reads_as_formatted_text(browser, port):
    ctx, page = _home(browser, port)
    try:
        page.wait_for_selector("#setupForm:not([hidden])", state="attached", timeout=15000)
        page.evaluate("DXLauncher.homeAgentStart('make a demo')")
        _wait_done(page)
        narr = page.locator("#workNarration")
        assert narr.locator(":is(h2, h3, h4)").count() >= 1, narr.inner_html()[:300]   # renderer 는 ## 를 한 단 낮춘다 (Agent Dev 와 같다)
        assert narr.locator("ol li").count() == 2
        assert page.locator("#workNarration .work-turn").count() == 1, "한 턴의 글은 한 덩어리"
    finally:
        ctx.close()


def test_interactive_opens_a_reply_that_continues_the_conversation(browser, port):
    ctx, page = _home(browser, port)
    bodies = _runs(page)
    try:
        page.wait_for_selector("#setupForm:not([hidden])", state="attached", timeout=15000)
        assert page.evaluate("document.getElementById('setupMode').value") == "interactive"
        page.evaluate("DXLauncher.homeAgentStart('make a demo')")
        _wait_done(page)
        page.wait_for_selector("#workReply:not([hidden])", timeout=5000)
        page.fill("#workReplyInput", "1")
        page.click("#workReplySend")
        _wait_done(page, 2)
        assert len(bodies) == 2, bodies
        assert bodies[0]["mode"] == "interactive" and not bodies[0].get("conversation_id")
        assert bodies[1]["conversation_id"], "답장은 같은 대화로 간다"
        assert bodies[1]["prompt"] == "1"
        assert page.locator("#workNarration .work-you").count() == 1, "보낸 답장이 왼쪽에 남는다"
    finally:
        ctx.close()


def test_autopilot_sends_its_mode_and_asks_nothing(browser, port):
    ctx, page = _home(browser, port)
    bodies = _runs(page)
    try:
        page.wait_for_selector("#setupForm:not([hidden])", state="attached", timeout=15000)
        page.click("#setupFold > summary")        # 설정은 접혀 있다 — 사람처럼 펼치고 고른다
        page.select_option("#setupMode", "autopilot")
        page.evaluate("DXLauncher.homeAgentStart('make a demo')")
        _wait_done(page)
        assert bodies[0]["mode"] == "autopilot"
        assert page.locator("#workReply").is_hidden()
    finally:
        ctx.close()


CATALOG = {
    "agent": "copilot", "models": ["auto", "claude-sonnet-5", "claude-opus-5.5"], "default_model": "claude-sonnet-5",
    "catalog": [
        {"id": "auto", "name": "Auto", "usage": None, "enabled": True},
        {"id": "claude-sonnet-5", "name": "Claude Sonnet 5", "usage": "1x", "enabled": True},
        {"id": "claude-opus-5.5", "name": "Claude Opus 5.5", "usage": "15x", "enabled": True},
        {"id": "claude-fable-5", "name": "claude-fable-5", "usage": None, "enabled": False},
    ],
}


def test_copilot_shows_every_model_but_only_the_accounts_are_pickable(browser, port):
    route = ("**/agent/api/agent/models?agent=copilot*",
             lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(CATALOG)))
    ctx, page = _home(browser, port, route=route)
    try:
        page.wait_for_selector("#setupForm:not([hidden])", state="attached", timeout=15000)
        page.click("#setupFold > summary")
        page.select_option("#setupAgent", "copilot")
        page.wait_for_function("document.querySelector('#setupModel option[value=\"claude-fable-5\"]')", timeout=8000)
        got = page.evaluate("""() => [...document.querySelectorAll('#setupModel option')]
          .map(o => ({v: o.value, t: o.textContent, d: o.disabled}))""")
        by = {o["v"]: o for o in got}
        assert by["claude-fable-5"]["d"], "계정에서 쓸 수 없는 model 은 고를 수 없다"
        assert not by["claude-opus-5.5"]["d"] and "15x" in by["claude-opus-5.5"]["t"]
        assert page.evaluate("document.getElementById('setupModel').value") == "claude-sonnet-5"
    finally:
        ctx.close()


def test_the_terminal_wraps_long_lines(browser, port):
    ctx, page = _home(browser, port)
    try:
        ws = page.evaluate("getComputedStyle(document.getElementById('workTerminalOut')).whiteSpace")
        assert ws == "pre-wrap", ws
    finally:
        ctx.close()


def test_a_run_that_failed_is_not_shown_as_completed(browser, port):
    """The server closes every run with `done`, also after `error` (a CLI that exits 1 — e.g. an
    account usage limit). The badge read "Completed" and the reply box opened for a dead run."""
    sse = "".join("data: " + json.dumps(e) + "\n\n" for e in (
        {"type": "message", "text": "usage limit reached"},
        {"type": "error", "text": "exit 1"},
        {"type": "done", "text": "ok", "conversation_id": "c1"}))
    ctx, page = _home(browser, port, route=("**/agent/api/agent/run",
                                            lambda r: r.fulfill(status=200, content_type="text/event-stream", body=sse)))
    try:
        page.wait_for_selector("#setupForm:not([hidden])", state="attached", timeout=15000)
        page.evaluate("DXLauncher.homeAgentStart('make a demo')")
        page.wait_for_function("!document.getElementById('homeWork').classList.contains('is-running')"
                               " && document.getElementById('workBadge').textContent.trim() !== ''", timeout=15000)
        assert page.inner_text("#workBadge") == "Failed"
        assert page.locator("#workReply").is_hidden()
    finally:
        ctx.close()


def test_the_folded_summary_names_the_model_a_run_will_use(browser, port):
    """2026-10-11: the folded setup read "copilot · auto" while the live list had already selected copilot's own
    default (claude-sonnet-5) — the summary was painted before the list arrived and the list changes the select
    without a change event, so the line under the prompt named a model the run would not use."""
    route = ("**/agent/api/agent/models?agent=copilot*",
             lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(CATALOG)))
    ctx, page = _home(browser, port, route=route)
    try:
        page.wait_for_selector("#setupForm:not([hidden])", state="attached", timeout=15000)
        page.evaluate("document.getElementById('setupAgent').value")  # copilot is first (DX_AGENT_DEV_PIN_AGENTS)
        page.wait_for_function("document.querySelector('#setupModel option[value=\"claude-fable-5\"][disabled]')", timeout=8000)
        assert page.evaluate("document.getElementById('setupModel').value") == "claude-sonnet-5"
        assert page.text_content("#setupFoldValue") == "copilot · claude-sonnet-5"
    finally:
        ctx.close()


def test_a_model_picked_before_the_live_list_arrives_is_kept(browser, port):
    """The CLI's list can take seconds (cursor asks for 200+ models). A model picked meanwhile was replaced by the
    agent's default when the list landed, and the summary kept naming the picked one."""
    held = []
    ctx, page = _home(browser, port, route=("**/agent/api/agent/models?agent=copilot*", lambda r: held.append(r)))
    try:
        page.wait_for_selector("#setupForm:not([hidden])", state="attached", timeout=15000)
        page.click("#setupFold > summary")
        page.wait_for_function("document.querySelectorAll('#setupModel option').length > 1", timeout=8000)
        page.select_option("#setupModel", "claude-opus-5.5")
        for _ in range(80):
            if held:
                break
            page.wait_for_timeout(100)
        held[0].fulfill(status=200, content_type="application/json", body=json.dumps(CATALOG))
        page.wait_for_function("document.querySelector('#setupModel option[value=\"claude-fable-5\"][disabled]')", timeout=8000)
        assert page.evaluate("document.getElementById('setupModel').value") == "claude-opus-5.5"
        assert page.text_content("#setupFoldValue") == "copilot · claude-opus-5.5"
    finally:
        ctx.close()

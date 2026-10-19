"""Chat says who answers and asks one question in settings. API answers are routed, so no CLI runs."""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

AGENTS = [{"name": "claude", "installed": True, "authenticated": True, "login_hint": "claude"},
          {"name": "copilot", "installed": True, "authenticated": False, "login_hint": "copilot login"},
          {"name": "cursor", "installed": False, "authenticated": None, "login_hint": "cursor-agent login"},
          {"name": "codex", "installed": False, "authenticated": None, "login_hint": "codex login"},
          {"name": "opencode", "installed": False, "authenticated": None, "login_hint": "opencode auth login"}]
AUTO = {"configured": False, "agents": AGENTS,
        "source": {"kind": "auto", "provider": "agent-cli", "agent": "claude", "model": None}}
SAVED = {"configured": True, "agents": AGENTS, "provider": "anthropic", "model": "claude-sonnet-4-5",
         "api_key": "sk-••••1234", "endpoint": "", "temperature": 0.7,
         "source": {"kind": "saved", "provider": "anthropic", "agent": None, "model": "claude-sonnet-4-5"}}
NONE = {"configured": False, "agents": [dict(a, installed=False) for a in AGENTS],
        "source": {"kind": "none", "provider": None, "agent": None, "model": None}}


@pytest.fixture(scope="module")
def port():
    srv, port = start_module_server("dx_planner")
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


def _page(browser, port, status, lang="en", width=1280):
    ctx = browser.new_context(viewport={"width": width, "height": 860})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');"
                        f"localStorage.setItem('dx-lang','{lang}')}}catch(e){{}}")
    posts = []
    state = {"status": status}

    def config(route):
        req = route.request
        if req.method == "GET":
            return route.fulfill(status=200, content_type="application/json", body=json.dumps(state["status"]))
        posts.append((req.method, json.loads(req.post_data or "{}")))
        if req.method == "DELETE":
            return route.fulfill(status=200, content_type="application/json", body='{"ok": true}')
        body = json.loads(req.post_data or "{}")
        ok = body.get("force") or body.get("model") != "bad-model"
        reply = {"ok": True, "tested": not body.get("force"), "response": "OK"} if ok else \
            {"ok": False, "tested": True, "error": "HTTP 404: model not found", "error_type": "api_error"}
        return route.fulfill(status=200, content_type="application/json", body=json.dumps(reply))
    ctx.route("**/api/chat/config", config)
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    page.evaluate("DXChat.toggle ? DXChat.toggle() : document.querySelector('.dx-chat-fab').click()")
    page.wait_for_selector(".dx-chat-source", state="visible")
    return ctx, page, posts, state


def test_the_status_line_names_who_answers(browser, port):
    for status, want in ((AUTO, "claude"), (SAVED, "Anthropic"), (NONE, "Basic guidance only")):
        ctx, page, _, _ = _page(browser, port, status)
        try:
            text = page.inner_text(".dx-chat-source")
            assert want in text, text
            assert "API key" not in text
        finally:
            ctx.close()


def test_settings_ask_one_question_and_show_the_right_fields(browser, port):
    ctx, page, _, _ = _page(browser, port, AUTO)
    try:
        page.click(".dx-chat-source button")
        page.wait_for_selector(".dx-chat-settings-panel.open")
        assert page.is_checked("input[name=dx-chat-kind][value=agent]")
        opts = page.eval_on_selector_all(".dx-chat-settings-agent option", "os => os.map(o => o.textContent)")
        assert any("claude" in o and "signed in" in o for o in opts)
        assert any("copilot" in o and "copilot login" in o for o in opts)
        assert not any("cursor" in o for o in opts)                 # not installed → not offered
        assert not page.is_visible(".dx-chat-settings-api-key")
        page.check("input[name=dx-chat-kind][value=cloud]")
        assert page.is_visible(".dx-chat-settings-api-key")
        cloud = page.eval_on_selector_all(".dx-chat-settings-provider option:not([hidden])", "os => os.map(o => o.value)")
        assert cloud == ["openai", "anthropic", "google", "github", "custom"]
        page.check("input[name=dx-chat-kind][value=local]")
        assert page.is_visible(".dx-chat-settings-endpoint") and not page.is_visible(".dx-chat-settings-api-key")
        assert not page.is_visible(".dx-chat-settings-temp")         # folded under Advanced
        page.click(".dx-chat-settings-advanced > summary")
        assert page.is_visible(".dx-chat-settings-temp")
    finally:
        ctx.close()


def test_save_tests_first_then_offers_save_anyway(browser, port):
    ctx, page, posts, _ = _page(browser, port, SAVED)
    try:
        page.click(".dx-chat-source button")
        page.wait_for_selector(".dx-chat-settings-panel.open")
        assert page.is_checked("input[name=dx-chat-kind][value=cloud]")
        page.select_option(".dx-chat-settings-model-select", "__custom__")
        page.fill(".dx-chat-settings-model", "bad-model")
        page.click(".dx-chat-settings-save")
        page.wait_for_selector(".dx-chat-settings-force", state="visible")
        assert "model not found" in page.inner_text(".dx-chat-settings-status")
        assert posts[-1][1]["api_key"] == ""                         # blank = keep the saved key
        page.click(".dx-chat-settings-force")
        page.wait_for_function("document.querySelector('.dx-chat-settings-status').textContent.length > 0")
        assert posts[-1][1]["force"] is True
    finally:
        ctx.close()


def test_reset_to_automatic(browser, port):
    ctx, page, posts, state = _page(browser, port, SAVED)
    try:
        page.click(".dx-chat-source button")
        page.wait_for_selector(".dx-chat-settings-reset", state="visible")
        state["status"] = AUTO
        page.click(".dx-chat-settings-reset")
        page.wait_for_function("document.querySelector('.dx-chat-source').textContent.includes('claude')")
        assert posts[-1][0] == "DELETE"
    finally:
        ctx.close()


@pytest.mark.parametrize("lang", ["ko", "ja", "es", "zh-CN", "zh-TW"])
def test_every_language_and_a_phone(browser, port, lang):
    ctx, page, _, _ = _page(browser, port, AUTO, lang=lang, width=390)
    try:
        page.click(".dx-chat-source button")
        page.wait_for_selector(".dx-chat-settings-panel.open")
        legend = page.inner_text(".dx-chat-settings-kind legend")
        assert legend and "Which AI" not in legend
        assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
    finally:
        ctx.close()


def test_opening_chat_rereads_who_answers(browser, port):
    """When Home switches the Studio agent to copilot, the chat line must not keep saying claude, as it would if the
    widget read the status only once at page load. Opening the chat reads it again."""
    ctx, page, _, state = _page(browser, port, AUTO)
    try:
        assert "claude" in page.inner_text(".dx-chat-source")
        state["status"] = dict(AUTO, source={"kind": "studio", "provider": "agent-cli", "agent": "copilot", "model": None})
        page.evaluate("DXChat.toggle()")          # close
        page.evaluate("DXChat.toggle()")          # open again
        page.wait_for_function("document.querySelector('.dx-chat-source').textContent.includes('copilot')", timeout=5000)
    finally:
        ctx.close()


def test_a_late_model_list_for_another_agent_is_ignored(browser, port):
    """Picking cursor must not save copilot's model (claude-sonnet-5.5), which happens when copilot's model list,
    asked first, arrives after cursor's and replaces it. A list for an agent that is no longer picked is dropped."""
    status = dict(AUTO, agents=[dict(a, installed=True, authenticated=True) for a in AGENTS[:3]],
                  source={"kind": "studio", "provider": "agent-cli", "agent": "copilot", "model": None})
    ctx, page, posts, _ = _page(browser, port, status)
    held = []
    lists = {"copilot": {"models": ["auto", "claude-sonnet-5.5"], "default_model": "claude-sonnet-5.5"},
             "cursor": {"models": ["auto", "composer-2.5"], "default_model": "auto"}}

    def models(route):
        agent = route.request.url.split("agent=")[1].split("&")[0]
        if agent == "copilot":
            held.append(route)
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(lists[agent]))
    page.route("**/agent/api/agent/models*", models)
    try:
        page.click(".dx-chat-source button")
        page.wait_for_selector(".dx-chat-settings-panel.open")
        page.wait_for_function("1")
        page.select_option(".dx-chat-settings-agent", "cursor")
        page.wait_for_function("[...document.querySelectorAll('.dx-chat-settings-agentmodel-select option')]"
                               ".some(o => o.value === 'composer-2.5')", timeout=5000)
        for r in held:
            r.fulfill(status=200, content_type="application/json", body=json.dumps(lists["copilot"]))
        page.wait_for_timeout(500)
        opts = page.eval_on_selector_all(".dx-chat-settings-agentmodel-select option", "os => os.map(o => o.value)")
        assert opts == ["auto", "composer-2.5"], opts
        page.click(".dx-chat-settings-save")
        page.wait_for_function("document.querySelector('.dx-chat-settings-status').textContent.length > 0")
        assert posts[-1][1]["model"] in ("cursor", "cursor::auto"), posts[-1]
    finally:
        ctx.close()


def test_on_a_phone_the_send_button_is_not_under_the_chat_button(browser, port):
    """At 390 px the open chat fills the width, so the round chat/close button would sit on top of Send. The
    header already has a close button, so the round one steps aside while the chat is open."""
    ctx, page, _, _ = _page(browser, port, AUTO, width=390)
    try:
        hit = page.evaluate("""() => { const b = document.querySelector('.dx-chat-send-btn').getBoundingClientRect();
          const el = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2);
          return el && el.closest('.dx-chat-send-btn') ? 'send' : (el ? el.className : 'none'); }""")
        assert hit == "send", hit
        assert page.is_visible(".dx-chat-header-btn[data-action=close]")
    finally:
        ctx.close()

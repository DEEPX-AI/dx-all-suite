"""Chat settings — Local / Self-hosted finds the models of the endpoint the user types (2026-10-11 real-use audit).

Models were looked up only when the provider changed, with whatever endpoint was there then (empty → the Ollama
default localhost:11434). Typing another endpoint (LM Studio :1234, llama.cpp :8080, Ollama on another host) found
nothing, the model box stayed an empty text field and Save said "Please enter a model".
"""
from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture()
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');")
    pg = ctx.new_page()
    asked = []

    def models(route):
        base = parse_qs(urlparse(route.request.url).query).get("base", [""])[0]
        asked.append(base)
        found = ["qwen-local:7b", "llama-local:8b"] if base == "http://127.0.0.1:1234" else []
        route.fulfill(status=200, content_type="application/json",
                      body=json.dumps({"models": found, "available": bool(found)}))

    pg.route("**/api/chat/local/models*", models)
    pg.route("**/api/chat/config", lambda r: r.fulfill(status=200, content_type="application/json",
                                                       body=json.dumps({"configured": False})))
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.wait_for_selector(".dx-chat-fab", timeout=10000)
    pg.click(".dx-chat-fab")
    pg.click('.dx-chat-header-btn[data-action="settings"]')
    pg.wait_for_selector(".dx-chat-settings-panel.open")
    pg.asked = asked
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def test_typing_the_endpoint_looks_up_its_models(page):
    page.check("input[name=dx-chat-kind][value=local]")   # settings ask one question (2026-10-11)
    page.fill(".dx-chat-settings-endpoint", "http://127.0.0.1:1234")
    page.locator(".dx-chat-settings-endpoint").blur()
    page.wait_for_function("() => !document.querySelector('.dx-chat-settings-model-select').hidden", timeout=5000)
    opts = page.eval_on_selector_all(".dx-chat-settings-model-select option", "els => els.map(e => e.value)")
    assert opts == ["qwen-local:7b", "llama-local:8b"]
    assert page.asked[-1] == "http://127.0.0.1:1234"
    assert not page.is_visible(".dx-chat-settings-model")


def test_typing_pauses_look_up_once_not_per_key(page):
    page.check("input[name=dx-chat-kind][value=local]")   # settings ask one question (2026-10-11)
    before = len(page.asked)
    page.locator(".dx-chat-settings-endpoint").press_sequentially("http://127.0.0.1:1234", delay=20)
    page.wait_for_function("() => !document.querySelector('.dx-chat-settings-model-select').hidden", timeout=5000)
    assert len(page.asked) - before <= 2

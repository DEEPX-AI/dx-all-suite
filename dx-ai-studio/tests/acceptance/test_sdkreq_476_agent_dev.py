"""SDKREQ-476 [Agent Dev] agent console — DX Agent Dev inside a real ./launcher.sh studio.

Tests never run a real coding-agent CLI (DX_AGENT_NO_REAL_RUN). The studio here uses the mock adapter
with two pinned agents, so the console behaves as on a machine with Claude and Copilot installed; the
run request itself is answered by the test, which checks what the console sends.
"""
from __future__ import annotations

import json

from tests.acceptance.conftest import module_frame, wait_home

LAUNCHER_ENV = {"DX_AGENT_ADAPTER": "mock", "DX_AGENT_DEV_PIN_AGENTS": "claude,copilot"}
TARGETS = ["suite", "dx-runtime", "dx_app", "dx_stream", "dx-compiler"]


def _agent(pages):
    page = pages.new(None)
    page.route("**/api/agent/models*", lambda route: route.fulfill(
        status=200, content_type="application/json",
        body=json.dumps({"models": [{"id": "default", "label": "Default"}, {"id": "fast", "label": "Fast"}]})))
    page.goto(pages.studio.base + "/", wait_until="domcontentloaded")
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('agent')")
    return page, module_frame(page, "agent", ready="#agent-console")


def test_three_column_layout_with_showcases_beside_the_console(pages):
    page, frame = _agent(pages)
    frame.locator("#examples-left .example-card").first.wait_for(timeout=30000)
    boxes = [frame.locator(s).bounding_box() for s in ("#examples-left", "#agent-console", "#examples-right")]
    assert boxes[0]["x"] < boxes[1]["x"] < boxes[2]["x"], boxes
    left, right = frame.locator("#examples-left .example-card").count(), frame.locator("#examples-right .example-card").count()
    assert left >= 1 and right >= 1, (left, right)


def test_agent_model_and_effort_pickers_follow_the_chosen_agent(pages):
    page, frame = _agent(pages)
    frame.locator("#agent-controls").wait_for(state="visible", timeout=30000)
    agents = frame.locator("#agent-select option").evaluate_all("els => els.map(e => e.value)")
    assert {"claude", "copilot"} <= set(agents), agents
    assert frame.locator("#model-select option").count() >= 1
    effort = {}
    for agent in ("claude", "copilot"):
        frame.select_option("#agent-select", agent)
        frame.locator("#effort-control").wait_for(state="visible", timeout=10000)
        effort[agent] = frame.locator("#effort-select option").evaluate_all("els => els.map(e => e.value)")
    assert "max" in effort["claude"] and "low" in effort["claude"], effort
    assert effort["claude"] != effort["copilot"], effort


def test_target_and_mode_are_sent_with_the_request(pages):
    page, frame = _agent(pages)
    sent = []

    def run(route):
        sent.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="text/event-stream",
                      body='data: {"type": "done", "exit_code": 0}\n\n')

    page.route("**/api/agent/run", run)
    frame.locator("#agent-controls").wait_for(state="visible", timeout=30000)
    assert frame.locator("#target-select option").evaluate_all("els => els.map(e => e.value)") == TARGETS
    assert frame.locator("#mode-select option").evaluate_all("els => els.map(e => e.value)") == ["interactive", "autopilot"]
    frame.select_option("#target-select", "dx_app")
    frame.select_option("#mode-select", "autopilot")
    frame.locator("#console-input").fill("Build a YOLO26n detection app")
    frame.locator("#console-send").click()
    for _ in range(40):
        if sent:
            break
        page.wait_for_timeout(250)
    assert sent and sent[0].get("target") == "dx_app" and sent[0].get("mode") == "autopilot", sent


def test_a_showcase_card_shows_a_preview_and_opens_its_readme(pages):
    page, frame = _agent(pages)
    card = frame.locator("a.example-card").first
    card.wait_for(timeout=30000)
    assert (card.get_attribute("href") or "").endswith("README.md")
    assert card.get_attribute("target") == "_blank"
    frame.wait_for_function("() => { const i = document.querySelector('a.example-card img.example-thumb');"
                            " return i && i.complete && i.naturalWidth > 0; }", timeout=30000)


def test_the_sdk_chat_answers_without_touching_the_console(pages):
    page, frame = _agent(pages)
    chats = []
    page.on("request", lambda r: chats.append(r.url) if r.url.endswith("/api/chat") and r.method == "POST" else None)
    frame.locator(".dx-chat-fab").click()
    frame.locator(".dx-chat-window.open").wait_for(timeout=10000)
    before = frame.locator("#console-output").inner_text()
    frame.locator(".dx-chat-input").fill("What is DX-M1?")
    frame.locator(".dx-chat-send-btn").click()
    frame.locator(".dx-chat-msg.ai").last.wait_for(timeout=30000)
    assert chats, "the chat goes to /api/chat"
    assert frame.locator("#console-output").inner_text() == before

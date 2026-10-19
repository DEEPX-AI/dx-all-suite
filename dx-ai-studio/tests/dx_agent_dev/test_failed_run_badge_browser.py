"""A failed agent run stays "Failed" — the closing `done` event must not paint it "Completed".

The server ends every run with `done`, also after `error` (a CLI that exits 1, e.g. an account
usage limit). The badge went Failed → Completed in the same tick, so the user read a failed run
as finished.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


def _sse(*events):
    return "".join("data: " + json.dumps(e) + "\n\n" for e in events)


@pytest.fixture()
def page(monkeypatch):
    from playwright.sync_api import sync_playwright

    monkeypatch.setenv("DX_AGENT_ADAPTER", "mock")
    server, port = start_module_server("dx_agent_dev")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','en')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    server.shutdown()


def _run(page, *events):
    page.route("**/api/agent/run", lambda r: r.fulfill(status=200, content_type="text/event-stream",
                                                         body=_sse(*events)))
    page.fill("#console-input", "build a demo")
    page.click("#console-send")
    page.wait_for_function("() => !document.querySelector('#status-badge').classList.contains('running')",
                           timeout=10000)
    page.unroute("**/api/agent/run")
    return page.locator("#status-badge")


def test_a_run_that_errored_stays_failed_after_done(page):
    badge = _run(page, {"type": "message", "text": "usage limit reached"},
                 {"type": "error", "text": "exit 1"},
                 {"type": "done", "text": "ok", "session_dir": "/tmp/s"})
    assert badge.inner_text() == "Failed"
    assert "failed" in badge.get_attribute("class")


def test_a_clean_run_is_completed_and_the_next_run_starts_fresh(page):
    _run(page, {"type": "error", "text": "exit 1"}, {"type": "done", "text": "ok"})
    badge = _run(page, {"type": "message", "text": "done", "final": True}, {"type": "done", "text": "ok"})
    assert badge.inner_text() == "Completed"


_CONTROLLED_FETCH = """() => {
  const real = window.fetch;
  window.__cancelled = 0;
  window.fetch = function (url, opts) {
    if (String(url).endsWith('/api/agent/cancel')) {
      window.__cancelled += 1;
      return Promise.resolve(new Response('{}', {status: 200}));
    }
    if (String(url).endsWith('/api/agent/run')) {
      const enc = new TextEncoder();
      const body = new ReadableStream({start(c) {
        window.__push = ev => c.enqueue(enc.encode('data: ' + JSON.stringify(ev) + '\\n\\n'));
        window.__end = () => c.close();
      }});
      return Promise.resolve(new Response(body, {status: 200, headers: {'Content-Type': 'text/event-stream'}}));
    }
    return real.apply(this, arguments);
  };
}"""


def _start_controlled(page):
    page.evaluate(_CONTROLLED_FETCH)
    page.fill("#console-input", "build a demo")
    page.click("#console-send")
    page.wait_for_function("() => typeof window.__push === 'function'", timeout=5000)
    page.evaluate("() => window.__push({type: 'message', text: 'working'})")


def test_stop_cancels_the_run_and_says_stopped(page):
    """The Agent Dev console must offer Stop, so a mistaken multi-minute build can be stopped here."""
    _start_controlled(page)
    stop = page.locator("#console-stop")
    assert stop.is_visible()
    stop.click()
    assert page.evaluate("window.__cancelled") == 1
    page.evaluate("() => { window.__push({type: 'error', text: 'exit -15'}); window.__push({type: 'done', text: 'ok'}); window.__end(); }")
    page.wait_for_function("() => !document.querySelector('#status-badge').classList.contains('running')", timeout=5000)
    assert page.locator("#status-badge").inner_text() == "Stopped"
    assert "exit -15" not in page.locator("#console-output").inner_text()
    assert not stop.is_visible()
    assert page.locator("#console-input").is_enabled()


def test_a_stream_that_ends_without_done_does_not_stay_running(page):
    """Server gone mid-run: the badge said "Running..." forever and nothing explained it."""
    _start_controlled(page)
    page.evaluate("() => window.__end()")
    page.wait_for_function("() => !document.querySelector('#status-badge').classList.contains('running')", timeout=5000)
    assert page.locator("#status-badge").inner_text() == "Failed"
    assert "connection to the agent ended" in page.locator("#console-output").inner_text()


def test_the_status_line_names_the_folder_the_app_was_written_to(page):
    _run(page, {"type": "message", "text": "built", "final": True},
         {"type": "done", "text": "ok", "session_dir": "/studio/var/dx_agent_dev/sessions/x"},
         {"type": "artifacts", "dirs": ["/suite/dx-runtime/dx_app/dx-agent-dev/20261011_demo"]})
    page.wait_for_timeout(200)
    bar = page.inner_text("#console-status-bar")
    assert "dx-agent-dev/20261011_demo" in bar and "var/dx_agent_dev" not in bar

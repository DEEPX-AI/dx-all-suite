"""Home and Agent Dev attach to the same run.

`test_live_run.py` guards the buffer and `test_server_reattach.py` the HTTP wiring. This file checks that
the screen actually uses them: even with a correct server, a console that does not attach still looks to
the user like the work vanished.

Pressing `Open in DX Agent Dev` while an agent runs on home must show that run in Agent Dev, and coming
back to home must still show the work.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_QUIET = """() => {
  const t = window._dxTutorial;
  if (t) { try { t.stop && t.stop(); } catch (e) {} }
  document.querySelectorAll('.dxt-toc,.dxt-overlay,.dxt-tooltip,.dxt-toc-backdrop')
    .forEach(e => e.remove());
}"""

RUNNING = {
    "available": True, "busy": True, "agents": [{"name": "mock"}],
    "showcase_count": 0, "run_id": "abc123", "event_count": 3, "run_done": False,
}
IDLE = {
    "available": True, "busy": False, "agents": [{"name": "mock"}],
    "showcase_count": 0, "run_id": None, "event_count": 0, "run_done": True,
}
EVENTS = (
    'data: {"type":"status","text":"thinking"}\n\n'
    'data: {"type":"message","text":"building the baseball game"}\n\n'
    'data: {"type":"done"}\n\n'
)


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _open(browser, status):
    server, port = start_module_server("launcher")
    ctx = browser.new_context(viewport={"width": 1512, "height": 900})
    ctx.add_init_script(
        "try{sessionStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}"
    )
    page = ctx.new_page()
    page.route("**/agent/api/agent/status", lambda r, *_: r.fulfill(
        status=200, content_type="application/json", body=json.dumps(status)))
    page.route("**/agent/api/agent/run/events**", lambda r, *_: r.fulfill(
        status=200, content_type="text/event-stream", body=EVENTS))
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
    page.wait_for_timeout(3500)
    page.evaluate(_QUIET)
    page.wait_for_timeout(800)
    return server, ctx, page


def test_home_picks_up_a_run_that_is_already_going(browser):
    """The path by which a window that left and came back takes the run over again."""
    server, ctx, page = _open(browser, RUNNING)
    try:
        shown = page.evaluate(
            "() => { const v = document.getElementById('homeWork');"
            " return !!(v && v.offsetParent !== null); }")
        assert shown, "실행 중인데 작업 뷰가 열리지 않았다"
        text = page.evaluate(
            "() => (document.getElementById('workNarration') || {}).textContent || ''")
        assert "baseball" in text, f"붙었는데 내용이 없다: {text[:120]!r}"
    finally:
        page.close(); ctx.close(); server.shutdown()


def test_home_stays_quiet_when_nothing_is_running(browser):
    """A work view opening when nothing runs is a ghost."""
    server, ctx, page = _open(browser, IDLE)
    try:
        shown = page.evaluate(
            "() => { const v = document.getElementById('homeWork');"
            " return !!(v && v.offsetParent !== null); }")
        assert not shown, "도는 게 없는데 작업 뷰가 열렸다"
    finally:
        page.close(); ctx.close(); server.shutdown()


def test_the_move_button_does_not_leave_the_shell(browser):
    """A full navigation drops the stream, and that must not kill the run."""
    src = (__import__("pathlib").Path(__file__).resolve().parents[2]
           / "launcher" / "static" / "home-console.js").read_text(encoding="utf-8")
    body = src[src.index("workOpenModule"):]
    body = body[: body.index("\n    }")]
    assert "location.href" not in body, (
        "이동 버튼이 여전히 전체 페이지 이동을 쓴다"
    )

"""Home's module rows each carry their own number, and stay quiet when everything is normal.

The eight modules are not started: requests to the launcher proxy are intercepted and answered with fakes. The
contract is how this screen reads each module API's response, so real servers are not needed, nor the cost of eight
processes.

A string-only check of `home-sections.js` cannot see whether the numbers render, so this file drives the page.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

CATALOG = {"ok": True, "models": [
    {"id": f"m{i}", "display": {"task": f"task{i % 3}"}} for i in range(12)
]}
APP_DEMOS = {"demos": [{"idx": i, "group": f"g{i % 4}"} for i in range(9)]}
STREAM_DEMOS = [{"id": i} for i in range(5)]
SHOWCASES = {"showcases": [{"id": f"s{i}"} for i in range(3)]}
BENCH = [{"hw_id": "A", "runs": [{"run_id": "1"}, {"run_id": "2"}]},
         {"hw_id": "B", "runs": [{"run_id": "3"}]}]
HW = {"available": True, "npus": [{"id": 0, "cores": 3, "temperatures": [40.0, 39.0, 39.0]}]}

ROUTES = {
    "**/zoo/api/catalog": CATALOG,
    "**/app/api/demos": APP_DEMOS,
    "**/stream/api/demos": STREAM_DEMOS,
    "**/agent/api/agent/showcases": SHOWCASES,
    "**/benchmark/api/results": BENCH,
    "**/dx_monitor/api/hw_status": HW,
}


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _open(browser, port, *, serve=None, health=None):
    ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
    ctx.add_init_script(
        "try{sessionStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}"
    )
    page = ctx.new_page()
    # Playwright calls handlers as (route, request). Passing the payload as a default argument would let the
    # Request overwrite it in the second slot, so close over it with a factory.
    def _fulfil(payload):
        def handler(route, *_):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(payload))
        return handler

    for pattern, payload in (serve or ROUTES).items():
        page.route(pattern, _fulfil(payload))
    if health is not None:
        page.route("**/api/health", _fulfil(health))
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
    page.wait_for_timeout(4000)
    page.evaluate(
        "() => { const t=window._dxTutorial; if(t){try{t.stop&&t.stop();}catch(e){}}"
        " document.querySelectorAll('.dxt-toc,.dxt-overlay,.dxt-tooltip,.dxt-toc-backdrop')"
        ".forEach(e=>e.remove()); }"
    )
    page.wait_for_timeout(400)
    return ctx, page


def _desc(page, app):
    return page.evaluate(
        "(a) => { const e=document.querySelector('.orbital-card[data-app=\"'+a+'\"] .card-desc');"
        " return e ? e.textContent.trim() : null; }", app)


@pytest.fixture()
def home(browser):
    server, port = start_module_server("launcher")
    ctx, page = _open(browser, port)
    try:
        yield page
    finally:
        page.close(); ctx.close(); server.shutdown()


def test_each_module_carries_its_own_number(home):
    assert "12" in _desc(home, "zoo"), _desc(home, "zoo")
    assert "3" in _desc(home, "zoo"), "task 수도 들어야 한다"
    assert "9" in _desc(home, "app"), _desc(home, "app")
    assert "5" in _desc(home, "stream"), _desc(home, "stream")
    assert "3" in _desc(home, "agent"), _desc(home, "agent")
    assert "2" in _desc(home, "benchmark"), _desc(home, "benchmark")
    assert "40" in _desc(home, "dx_monitor"), _desc(home, "dx_monitor")


def test_modules_with_nothing_to_count_keep_their_prose(home):
    for app in ("compiler", "planner"):
        d = _desc(home, app)
        assert d, f"{app} 설명이 비었다"
        assert not any(ch.isdigit() for ch in d), f"{app} 에 숫자가 붙었다: {d!r}"


def test_a_module_that_is_down_does_not_block_the_others(browser):
    """One module's failed response must not block the other rows."""
    server, port = start_module_server("launcher")
    broken = dict(ROUTES)
    broken.pop("**/app/api/demos")
    ctx, page = _open(browser, port, serve=broken)
    try:
        page.route("**/app/api/demos", lambda route: route.abort())
        page.wait_for_timeout(500)
        assert "12" in _desc(page, "zoo"), "다른 모듈이 실패에 휩쓸렸다"
        assert "3" in _desc(page, "agent")
    finally:
        page.close(); ctx.close(); server.shutdown()


# ── quiet when normal ─────────────────────────────────────────
#
# When every module runs (the usual case) the screen must not state the same fact several times: no
# "8 of 8 running" count, no "Running" on every row. Running is told by the icon's light. What this file
# protects is "show the exception, stay silent otherwise": eight calls to action are no call to action.

# Health keys differ from the cards' data-app (dx_monitor → monitor). A hand-written list would drift
# silently when the mapping changes, so take the mapping the page actually uses.
_KEYS_FROM_PAGE = """() => {
  const map = (window.DXLauncher && window.DXLauncher._HEALTH_KEY) || null;
  return [...document.querySelectorAll('.orbital-card[data-app]')]
    .map(c => (map && map[c.dataset.app]) || c.dataset.app);
}"""


def _page_health_keys(page):
    keys = page.evaluate(_KEYS_FROM_PAGE)
    assert keys, "모듈 카드를 못 찾았다"
    return keys


def _health(alive_keys, all_keys):
    return {k: {"alive": k in alive_keys} for k in all_keys}


def _set_health(page, health):
    """Swap the health the page holds and make it repaint.

    Done this way rather than by intercepting /api/health because polling has already cached a result, so a route
    would only take effect on the next cycle.
    """
    page.evaluate(
        "(h) => { window.DXLauncher._healthStatus = h;"
        " window.DXLauncher.refreshModuleState(); }", health)


def _state_labels(page):
    return page.evaluate(
        "() => [...document.querySelectorAll('.orbital-card [data-role=\"state\"]')]"
        ".map(e => e.textContent.trim()).filter(Boolean)")


def test_when_everything_runs_the_screen_stops_repeating_itself(browser):
    server, port = start_module_server("launcher")
    ctx, page = _open(browser, port)
    try:
        keys = _page_health_keys(page)
        _set_health(page, _health(keys, keys))
        page.wait_for_timeout(1200)
        assert not _state_labels(page), (
            f"전부 도는데 행마다 상태 라벨이 있다: {_state_labels(page)}"
        )
    finally:
        page.close(); ctx.close(); server.shutdown()


def test_when_one_is_down_the_screen_says_so(browser):
    server, port = start_module_server("launcher")
    ctx, page = _open(browser, port)
    try:
        keys = _page_health_keys(page)
        alive = [k for k in keys if k != "benchmark"]
        _set_health(page, _health(alive, keys))
        page.wait_for_timeout(1200)
        assert _state_labels(page), "예외 상태일 때는 행 라벨이 정보가 된다"
    finally:
        page.close(); ctx.close(); server.shutdown()

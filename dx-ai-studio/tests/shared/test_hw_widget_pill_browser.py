"""The floating pill (pages without the module rail, i.e. the launcher's SDK Library) is easy to miss.

Folded, it carries the same NPU state dot as the rail button (grey without data, no motion). On the first visit of
a browser, at desktop width, it starts open once; after that the remembered choice applies. Pages with the rail keep
starting folded (test_hw_widget_rail_browser) because an open panel there covers module controls.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

WIDGET = (Path(__file__).resolve().parents[2] / "shared" / "hw_widget" / "widget.html").read_text(encoding="utf-8")
# Studio pages size .dx-ico through the shared CSS; this bare page needs the same rule, or each icon renders at the
# SVG default 300x150 and the open panel overflows the viewport.
PAGE = ("<html><head><style>.dx-ico{width:14px;height:14px}</style></head><body><p>no rail here</p>"
        + WIDGET + "</body></html>")
URL = "http://studio.test/"
PAYLOAD = """window.postMessage({type: 'dx-hw-data', payload: {npus: [{id: 0, temp_avg: 47.3, utilization: [10],
    clock_avg: 1000, voltage_avg: 750, dram_pct: 20}], cpu_load: 1, mem_pct: 30, disk_pct: 50}}, '*')"""


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _page(browser, width=1440):
    ctx = browser.new_context(viewport={"width": width, "height": 900})
    pg = ctx.new_page()
    pg.route("http://studio.test/**", lambda route: route.fulfill(status=200, content_type="text/html", body=PAGE))
    pg.goto(URL, wait_until="load")
    return ctx, pg


def _folded(pg):
    return "minimized" in (pg.locator("#hw-float").get_attribute("class") or "")


def test_first_visit_opens_once_then_the_pill_starts_folded(browser):
    ctx, pg = _page(browser)
    try:
        assert not _folded(pg)
        pg.reload(wait_until="load")
        assert _folded(pg)
    finally:
        ctx.close()


def test_a_remembered_choice_wins_over_the_first_visit(browser):
    ctx, pg = _page(browser)
    try:
        pg.click("#hw-float .hw-float-toggle")
        assert _folded(pg)
        assert pg.evaluate("localStorage.getItem('hw-float-open')") == "0"
        pg.click("#hw-float .hw-float-toggle")
        pg.reload(wait_until="load")
        assert not _folded(pg)
    finally:
        ctx.close()


def test_narrow_screens_do_not_open_on_the_first_visit(browser):
    ctx, pg = _page(browser, width=390)
    try:
        assert _folded(pg)
    finally:
        ctx.close()


def test_folded_pill_shows_the_npu_state_dot(browser):
    ctx, pg = _page(browser)
    try:
        pg.evaluate("localStorage.setItem('hw-float-open','0')")
        pg.reload(wait_until="load")
        dot = pg.locator("#hw-float .hw-float-dot")
        assert dot.is_visible()
        assert pg.locator("#hw-float").get_attribute("data-state") == "offline"
        pg.evaluate(PAYLOAD)
        pg.wait_for_function("document.getElementById('hw-float').dataset.state === 'ok'", timeout=3000)
        assert dot.evaluate("el => getComputedStyle(el).animationName") == "none"
    finally:
        ctx.close()

"""The NPU Monitor float, folded, docks into the module rail (2026-10-11 real-use audit).

Folded, it sat over the bottom-left of every module page: measured at 1440 and 390 px with each page
scrolled to its end, it still covered the Model Zoo category checkbox, the Compiler's Nodes/Edges/Zoom
status, EdgeGuide's channel slider and task buttons, an Agent Dev example card and the DX App model table,
so those could not be reached without dragging it away. On a page with the module rail the folded widget
is now a rail button above Hub; opening it shows the panel beside the rail. A page without the rail
(the launcher's SDK Library) keeps the floating pill.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

WIDGET = (Path(__file__).resolve().parents[2] / "shared" / "hw_widget" / "widget.html").read_text(encoding="utf-8")

# what the module pages would leave under a floating pill at the bottom-left once scrolled to the end
COVERED = """() => {
  const pill = document.getElementById('hw-float');
  const p = pill.getBoundingClientRect();
  if (!pill.checkVisibility() || p.width < 2) return [];
  const out = [];
  for (const el of document.querySelectorAll('a,button,input,select,textarea,label,span,td,h2,h3,p')) {
    if (pill.contains(el) || !el.checkVisibility()) continue;
    const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
    if (r.right <= p.left || r.left >= p.right || r.bottom <= p.top || r.top >= p.bottom) continue;
    out.push(el.tagName + ' ' + (el.innerText || el.value || '').trim().slice(0, 30));
  }
  return out;
}"""


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _open(browser, module, width):
    srv, port = start_module_server(module)
    ctx = browser.new_context(viewport={"width": width, "height": 900 if width > 600 else 844})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','en')}catch(e){}")
    pg = ctx.new_page()

    # the launcher proxy injects the widget before </body>; do the same here
    def inject(route):
        resp = route.fetch()
        body = resp.text().replace("</body>", WIDGET + "</body>", 1)
        route.fulfill(response=resp, body=body)

    pg.route(f"http://127.0.0.1:{port}/", inject)
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    return srv, ctx, pg


@pytest.mark.parametrize("width", [1440, 390])
@pytest.mark.parametrize("module", ["dx_planner", "dx_compiler", "dx_modelzoo"])
def test_folded_widget_is_a_rail_button_and_covers_nothing(browser, module, width):
    srv, ctx, pg = _open(browser, module, width)
    try:
        btn = pg.locator(".dx-shell-rail-foot .hw-rail-btn")
        btn.wait_for(timeout=5000)
        assert btn.get_attribute("aria-expanded") == "false"
        assert not pg.locator("#hw-float").is_visible()
        assert pg.evaluate(COVERED) == []
        # the rail button stays inside the rail, above Hub
        rail = pg.locator(".dx-shell-rail").bounding_box()
        b = btn.bounding_box()
        hub = pg.locator('.dx-shell-rail-foot a[href="/"]').bounding_box()
        assert rail["x"] <= b["x"] and b["x"] + b["width"] <= rail["x"] + rail["width"]
        assert b["y"] + b["height"] <= hub["y"]

        btn.click()
        panel = pg.locator("#hw-float")
        assert panel.is_visible() and "minimized" not in (panel.get_attribute("class") or "")
        assert btn.get_attribute("aria-expanded") == "true"
        assert panel.bounding_box()["x"] >= rail["x"] + rail["width"]
        assert pg.evaluate("localStorage.getItem('hw-float-open')") == "1"

        pg.click("#hw-float .hw-float-toggle")
        assert not panel.is_visible()
        assert btn.get_attribute("aria-expanded") == "false"
        assert pg.evaluate("localStorage.getItem('hw-float-open')") == "0"
    finally:
        ctx.close()
        srv.shutdown()


def test_rail_button_shows_the_npu_temperature_state(browser):
    srv, ctx, pg = _open(browser, "dx_planner", 1440)
    try:
        btn = pg.locator(".dx-shell-rail-foot .hw-rail-btn")
        btn.wait_for(timeout=5000)
        assert btn.get_attribute("data-state") == "offline"
        pg.evaluate("""window.postMessage({type: 'dx-hw-data', payload: {npus: [{id: 0, temp_avg: 47.3,
            utilization: [10], clock_avg: 1000, voltage_avg: 750, dram_pct: 20}], cpu_load: 1, mem_pct: 30, disk_pct: 50}}, '*')""")
        pg.wait_for_function("document.querySelector('.hw-rail-btn').dataset.state === 'ok'", timeout=3000)
        assert "47.3°C" in (btn.get_attribute("title") or "")
    finally:
        ctx.close()
        srv.shutdown()


def test_page_without_the_rail_keeps_the_floating_pill(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    pg = ctx.new_page()
    try:
        pg.set_content("<html><body><p>no rail here</p>" + WIDGET + "</body></html>")
        assert pg.locator("#hw-float").is_visible()
        assert pg.locator(".hw-rail-btn").count() == 0
    finally:
        ctx.close()

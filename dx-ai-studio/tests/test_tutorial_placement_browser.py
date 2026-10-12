"""A tutorial tooltip never covers the target it points at — on narrow screens too.

- A tooltip clamped into the viewport must not end up on top of its target; checking only
  "is it clipped" would leave it covering the target on a phone width.
- A zero-height strip is not a visible target; the spotlight must not land on an empty line.
- A beforeStep that throws must not stall the tour on the previous step.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture(scope="module")
def server():
    srv, port = start_module_server("dx_modelzoo")
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


def _open(browser, port, width, height=844):
    ctx = browser.new_context(viewport={"width": width, "height": height})
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_function("() => window._dxTutorial", timeout=20000)
    return ctx, pg


START = """(steps) => {
  const e = window._dxTutorial;
  for (const s of steps) if (s.throws) s.beforeStep = () => { throw new Error('boom'); };
  const probe = { id: 'probe', title: { en: 'Probe' }, steps };
  e.sections = [probe]; e._sections = [probe];
  return e.startSection('probe');
}"""

OVERLAP = """(sel) => {
  const t = document.querySelector(sel).getBoundingClientRect();
  const p = document.querySelector('.dxt-tooltip').getBoundingClientRect();
  const w = Math.max(0, Math.min(t.right, p.right) - Math.max(t.left, p.left));
  const h = Math.max(0, Math.min(t.bottom, p.bottom) - Math.max(t.top, p.top));
  return { area: w * h, target: t.width * t.height, inView: p.left >= 0 && p.right <= innerWidth && p.top >= 0 && p.bottom <= innerHeight };
}"""


@pytest.mark.parametrize("width", [390, 1440])
@pytest.mark.parametrize("position", ["left", "right", "auto"])
def test_the_tooltip_does_not_cover_its_target(browser, server, width, position):
    ctx, pg = _open(browser, server, width)
    try:
        pg.evaluate("""() => { const b = document.createElement('button'); b.id = 'probe-target';
          b.textContent = 'target'; b.style.cssText = 'position:fixed;left:40%;top:40%;width:120px;height:40px;z-index:1';
          document.body.appendChild(b); }""")
        pg.evaluate(START, [{"target": "#probe-target", "position": position,
                             "title": {"en": "t"}, "content": {"en": "A fairly long explanation " * 4}}])
        pg.wait_for_timeout(400)
        o = pg.evaluate(OVERLAP, "#probe-target")
        assert o["area"] == 0, f"{width}px {position}: the tooltip covers {o['area']:.0f}px² of the target"
        assert o["inView"]
    finally:
        ctx.close()


def test_a_zero_height_target_is_not_spotlighted(browser, server):
    ctx, pg = _open(browser, server, 1440, 900)
    try:
        pg.evaluate("""() => { const d = document.createElement('div'); d.id = 'probe-empty';
          d.style.cssText = 'width:400px;height:0'; document.body.prepend(d); }""")
        pg.evaluate(START, [{"target": "#probe-empty", "title": {"en": "t"}, "content": {"en": "empty strip"}}])
        pg.wait_for_timeout(2600)   # after the engine's polling (2 s)
        assert pg.evaluate("() => !!document.querySelector('.dxt-tooltip').getAttribute('data-dxt-floating')")
        assert not pg.evaluate("() => document.querySelector('.dxt-spotlight').classList.contains('active')")
    finally:
        ctx.close()


def test_a_failing_before_step_does_not_freeze_the_tour(browser, server):
    ctx, pg = _open(browser, server, 1440, 900)
    try:
        pg.evaluate(START, [{"target": "#dxToolbar", "title": {"en": "one"}, "content": {"en": "first step"}},
                            {"target": "#dxToolbar", "title": {"en": "two"}, "content": {"en": "second step"}, "throws": True}])
        pg.wait_for_timeout(300)
        pg.evaluate("() => window._dxTutorial.next()")
        pg.wait_for_timeout(500)
        assert "second step" in pg.inner_text(".dxt-tooltip")
    finally:
        ctx.close()

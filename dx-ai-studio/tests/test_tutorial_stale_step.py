"""When the step changes, nothing from the previous step may stay on screen.

`_showStep()` polls for up to 2 s (20×100ms) when the target is not visible. If the user
presses Next meanwhile, the `_stepToken` guard returns without rendering. Unless the old
visuals are cleared, **the previous step's spotlight and tooltip** stay on screen — the user
looks at a box from a step already passed, with that step's tooltip text.

The tutorial e2e gate reports that state as `TARGET_MISSING` even though the selector is
fine: the engine is simply still looking for it.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


@pytest.fixture()
def page(browser):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    try:
        yield pg
    finally:
        pg.close()
        ctx.close()

TARGETLESS_STEP = """() => {
  const e = window._dxTutorial;
  const probe = {
    id: 'probe',
    title: { en: 'Probe' },
    steps: [
      { target: '#dxToolbar', title: { en: 'one' }, content: { en: 'anchored step' } },
      { target: '#definitely-not-here-xyz', title: { en: 'two' }, content: { en: 'missing target' } },
    ],
  };
  // startSection() 이 _buildDOM() 을 부르므로 정식 경로로 들어간다.
  e.sections = [probe];
  e._sections = [probe];
  return e.startSection('probe');
}"""


def _state(page):
    return page.evaluate(
        """() => {
      const sp = document.querySelector('.dxt-spotlight');
      const tip = document.querySelector('.dxt-tooltip');
      return {
        spotlightActive: !!(sp && sp.classList.contains('active')),
        tooltipText: tip ? tip.innerText : '',
        floating: !!(tip && tip.getAttribute('data-dxt-floating')),
      };
    }"""
    )


def test_no_stale_spotlight_while_polling_for_a_missing_target(page):
    server, port = start_module_server("dx_modelzoo")
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_function("() => window._dxTutorial", timeout=20000)
        page.evaluate(TARGETLESS_STEP)
        page.wait_for_timeout(400)

        first = _state(page)
        assert first["spotlightActive"], "앵커된 첫 스텝이 스포트라이트를 걸어야 한다"
        assert "anchored step" in first["tooltipText"]

        # Move to the next step, which has no target — the engine starts polling.
        page.evaluate("() => window._dxTutorial.next()")
        page.wait_for_timeout(300)  # well before polling (2 s) ends

        during = _state(page)
        assert not during["spotlightActive"], (
            "폴링 중 이전 스텝의 스포트라이트가 남아 있다 — 사용자는 지나간 스텝의 상자를 본다"
        )
        assert "anchored step" not in during["tooltipText"], (
            "폴링 중 툴팁이 아직 이전 스텝 내용이다"
        )
        assert "missing target" in during["tooltipText"], (
            "새 스텝의 내용이 즉시 보여야 한다"
        )
    finally:
        server.shutdown()


def test_anchored_steps_are_unaffected(page):
    """A step whose target is found on the first lookup keeps the direct path (no tooltip flicker)."""
    server, port = start_module_server("dx_modelzoo")
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_function("() => window._dxTutorial", timeout=20000)
        page.evaluate(TARGETLESS_STEP)
        page.wait_for_timeout(400)
        st = _state(page)
        assert st["spotlightActive"]
        assert not st["floating"], "타깃이 있는 스텝이 floating 으로 떨어졌다"
    finally:
        server.shutdown()

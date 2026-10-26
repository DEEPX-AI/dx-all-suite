"""EdgeGuide: summary chips, facts table, benchmark table and platform summary follow the chosen language.

Chip names (Task · Model · Channels …) must be translated and values must show task names, not slugs
(pose_estimation). 'Benchmark system' and 'Host' are data-i18n spans and must stay translated across redraws.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_planner")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');"
                        "localStorage.removeItem('dxPlanner.state.v1');")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.click('.task-btn[data-task="pose_estimation"]')
    pg.click("#btnSetupNext")
    pg.wait_for_selector("#btnRecommend:not([disabled])", timeout=10000)
    pg.click("#btnRecommend")
    pg.wait_for_selector("#conditionSummary .summary-chip", timeout=10000)
    pg.evaluate("() => { const r = PlannerRuntime.getLastResults(); openDetail(r[0].platform.id); }")
    pg.wait_for_selector("#recommendation-facts .fact-grid", timeout=10000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _text(page, sel):
    return page.inner_text(sel)


def test_english_shows_task_names_not_slugs(page):
    chips = _text(page, "#conditionSummary")
    assert "Pose Estimation" in chips and "pose_estimation" not in chips
    assert "pose_estimation" not in _text(page, "#recommendation-facts")


def test_switching_language_translates_chips_facts_and_platform_summary(page):
    page.evaluate("() => DXI18n.setLang('ja')")
    try:
        page.wait_for_function("() => document.querySelector('#conditionSummary').textContent.includes('タスク')",
                               timeout=5000)
        chips = _text(page, "#conditionSummary")
        assert "姿勢推定" in chips and "Task" not in chips and "Channels" not in chips
        assert "充足" in _text(page, "#recommendSummary")
        assert "姿勢推定" in _text(page, "#recommendation-facts")
        summary = _text(page, "#platform-summary")
        assert "Host" not in summary and "Benchmark system" not in summary
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_task_names_are_not_clipped_in_the_results_sidebar(page):
    """At 1440 px the sidebar must not clip task names ("Object Detectic", "Segmen") by splitting task · size into columns."""
    clipped = page.evaluate("""() => [...document.querySelectorAll('.task-btn .task-name')]
        .filter(e => e.offsetParent !== null && e.scrollWidth > e.clientWidth + 1).map(e => e.textContent.trim())""")
    widths = page.evaluate("[...document.querySelectorAll('.task-btn')].map(b => Math.round(b.getBoundingClientRect().width))")
    assert not clipped, (clipped, widths)
    assert min(widths) >= 120, widths

"""DX Benchmark on a phone (390 px, 2026-10-11 matrix).

Settings: a 220 px input beside each label folded the label one syllable per line and the
inputs ran off-screen. Results: the 1fr column kept its min-content width, so the hardware
list was cut at the right edge.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_benchmark")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 390, "height": 844})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','ko')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _overflowing(page, sel):
    return page.evaluate("""s => { const vw = document.documentElement.clientWidth;
        return [...document.querySelectorAll(s)].filter(e => e.offsetParent && e.getBoundingClientRect().right > vw + 1)
                 .map(e => e.id || e.className); }""", sel)


def test_settings_labels_sit_above_their_inputs(page):
    page.evaluate("BenchApp.switchTab('settings')")
    page.wait_for_timeout(300)
    assert not _overflowing(page, "#tab-settings .setting-input"), _overflowing(page, "#tab-settings .setting-input")
    heights = page.evaluate("[...document.querySelectorAll('#tab-settings .setting-row label')].filter(l => l.offsetParent).map(l => l.getBoundingClientRect().height)")
    assert heights and max(heights) < 48, heights          # one line, not a column of syllables


def test_results_rail_fits_the_screen(page):
    page.evaluate("BenchApp.switchTab('results')")
    page.wait_for_timeout(600)
    assert not _overflowing(page, "#tab-results .results-rail-section, #tab-results .results-detail")

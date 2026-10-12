"""Task icons are drawn on screen from the sprite.

Model Zoo (cards, list filter, detail), the Planner task buttons and the dx_app result hints all use the same
`task-<key>` table.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_QUIET = ("try{localStorage.setItem('dx-tutorial-mode','off');sessionStorage.setItem('dx-splash-seen','1');"
          "localStorage.setItem('dx-splash-seen','1');}catch(e){}")


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _page(browser, module):
    srv, port = start_module_server(module)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script(_QUIET)
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    return srv, ctx, page


def _hrefs(page, sel):
    return page.evaluate(f"""() => [...document.querySelectorAll('{sel} use')].map(u => u.getAttribute('href').split('#')[1])""")


def test_model_zoo_cards_filters_and_detail_use_task_symbols(browser):
    srv, ctx, page = _page(browser, "dx_modelzoo")
    try:
        page.wait_for_selector(".mz-card .mz-card-cat svg.dx-ico", timeout=15000)
        cats = _hrefs(page, ".mz-card .mz-card-cat")
        assert cats and all(n.startswith("task-") for n in cats), cats[:5]
        filters = _hrefs(page, ".mz-category-label")
        assert filters and all(n.startswith("task-") for n in filters), filters
        box = page.evaluate("() => { const r = document.querySelector('.mz-card .mz-card-cat svg').getBoundingClientRect(); return [r.width, r.height]; }")
        assert 12 <= box[0] <= 24 and 12 <= box[1] <= 24, box
        mid = page.evaluate("() => document.querySelector('.mz-card').dataset.modelId")
        page.evaluate(f"() => {{ location.hash = 'model=' + encodeURIComponent('{mid}'); }}")
        page.wait_for_selector(".mz-detail-hero .mz-card-cat svg.dx-ico", timeout=10000)
        assert _hrefs(page, ".mz-detail-hero .mz-card-cat")[0].startswith("task-")
    finally:
        ctx.close()
        srv.shutdown()


def test_planner_task_buttons_draw_task_symbols(browser):
    srv, ctx, page = _page(browser, "dx_planner")
    try:
        page.wait_for_selector(".task-btn svg.task-icon", state="attached", timeout=10000)
        names = _hrefs(page, ".task-grid")
        assert names == ["task-object_detection", "task-pose_estimation", "task-semantic_segmentation",
                         "task-obb_detection", "task-classification"], names
    finally:
        ctx.close()
        srv.shutdown()


def test_dx_app_result_hint_leads_with_the_task_symbol(browser):
    srv, ctx, page = _page(browser, "dx_app")
    try:
        page.wait_for_function("() => typeof window.renderInferenceResult === 'function'", timeout=10000)
        out = page.evaluate("""() => { const el = document.createElement('div'); document.body.appendChild(el);
          window.renderInferenceResult(el, { _cat: 'depth_estimation', results: [] });
          const hint = el.querySelector('.res-hint');
          return hint ? [hint.querySelector('use').getAttribute('href').split('#')[1], hint.textContent.trim()] : null; }""")
        assert out, "결과 안내가 그려지지 않았다"
        assert out[0] == "task-depth_estimation"
        assert out[1].startswith("Depth Result"), out[1]
    finally:
        ctx.close()
        srv.shutdown()

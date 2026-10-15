"""The Graph Composer tutorial in a browser: the page's tour hooks (GraphComposer.tutorial, GraphRun.preview,
GraphPalette.reveal) and the graph section of dx_app/static/js/tutorial.js.

/api/graph/* is answered by test_graph_logic_browser's FakeApi (the recorded catalog with the nine templates). The
tutorial's recorded result (dx_app/static/img/graph-tutorial/preview.json) is answered with a two-source fixture
whose pictures are the 16x12 layer fixtures, so these tests do not depend on the recorded files.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

from tests.dx_app.test_graph_logic_browser import FakeApi  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402

LAYERS = Path(__file__).resolve().parent / "fixtures" / "graph" / "layers"


def _cell(s):
    return {"url": f"/fake/tut/{s}.png", "kind": "image", "name": f"result_{s}.jpg", "stream": s,
            "layers": {"base": f"/fake/tut/{s}_base.png", "width": 16, "height": 12, "layers": [
                {"node": "od", "model": "yolov8-n_640x640", "url": f"/fake/tut/{s}_od.png"},
                {"node": "count", "op": "count", "url": f"/fake/tut/{s}_count.png"}]}}


PREVIEW = {"ok": True, "exit_code": 0, "run_id": None, "preview": True, "frames": 2, "error_frames": 0, "fps": None,
           "avg_fps": None, "elapsed": 0.9, "node_ms": {"od": 12.5, "count": 0.1, "crowded": 0.1},
           "nodes": {"od": {"shape": "boxes", "frames": 2, "items_total": 17, "crops_total": 0}}, "errors": [],
           "events": [{"seq": 1, "frame": 0, "time": 0, "stream": "cam2", "node": "crowded", "event": "crowded",
                       "track_id": -1, "data": {"value": 15, "threshold": 5}}],
           "event_total": 1, "event_counts": {"crowded": {"crowded": 1}}, "events_truncated": False,
           "events_url": None, "events_partial": False, "outputs": [_cell("cam1"), _cell("cam2")]}


def _picture(route):
    name = route.request.url.rsplit("/", 1)[1]
    plain = name.endswith("_base.png") or name.count("_") == 0
    route.fulfill(status=200, content_type="image/png",
                  body=(LAYERS / ("base.png" if plain else "layer.png")).read_bytes())


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    srv, port = start_module_server("dx_app")
    from dx_app.core import config
    mp = pytest.MonkeyPatch()
    mp.setattr(config, "OUTPUTS_DIR", tmp_path_factory.mktemp("outputs"))
    yield port
    mp.undo()
    srv.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _page(browser, server, lang="en"):
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    ctx.add_init_script("try { localStorage.setItem('dx-tutorial-mode', 'off'); localStorage.setItem('dx-lang', '%s');"
                        " localStorage.removeItem('dx-graph-draft'); window.confirm = () => true; } catch (e) {}" % lang)
    ctx.route("**/api/graph/**", FakeApi().handle)
    ctx.route("**/static/img/graph-tutorial/preview.json",
              lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(PREVIEW)))
    ctx.route("**/fake/tut/*.png", _picture)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"http://127.0.0.1:{server}/", wait_until="domcontentloaded")
    page.wait_for_function("() => typeof nav === 'function' && window.GraphComposer && window._dxTutorial")
    page.evaluate("nav('graph')")
    page.wait_for_selector("[data-group='logic'] .gc-item", timeout=20000)
    return ctx, page, errors


@pytest.fixture
def ui(browser, server):
    ctx, page, errors = _page(browser, server)
    yield page
    assert not errors, errors
    ctx.close()


def test_the_preview_shows_a_recorded_run_and_takes_nothing_away(ui):
    page = ui
    assert page.evaluate("GraphComposer.tutorial.showResults()") is True
    page.wait_for_selector("#gc-run-results .gc-res-grid[data-n='2']")
    assert page.locator("#gc-run-results .gc-res-stack img.gc-res-layer").count() == 4
    assert page.locator("[data-dxt-tutorial-mock]").count() == 2, "the result and the event list are marked"
    assert "crowded" in page.inner_text("#gc-run-events")
    assert page.evaluate("GraphComposer.state().run") is None, "a preview is not the page's run"
    page.evaluate("GraphComposer.tutorial.hideResults()")
    assert page.locator("[data-dxt-tutorial-mock]").count() == 0
    assert page.locator("#gc-run-results").count() == 0 and page.is_hidden("#gc-run-events")


def test_after_the_preview_the_page_shows_its_own_run_again(ui):
    page = ui
    page.evaluate("""() => { GraphComposer.state().run = {ok: true, exit_code: 0, run_id: null, frames: 1,
        elapsed: 0.5, nodes: {}, node_ms: {}, errors: [], events: [], event_total: 0,
        outputs: [{url: '/fake/tut/mine.png', kind: 'image', name: 'result_mine.jpg', stream: 'mine'}]}; }""")
    page.evaluate("GraphComposer.tutorial.showResults()")
    page.wait_for_selector("#gc-run-results .gc-res-grid[data-n='2']")
    page.evaluate("GraphComposer.tutorial.hideResults()")
    page.wait_for_selector("#gc-run-results .gc-res-grid[data-n='1']")
    assert "mine" in page.inner_text("#gc-run-results")


def test_the_preview_follows_a_language_change(ui):
    page = ui
    page.evaluate("GraphComposer.tutorial.showResults()")
    page.wait_for_selector("#gc-run-results .gc-res-grid[data-n='2']")
    page.evaluate("DXI18n.setLang('ko')")
    page.wait_for_function("() => document.querySelector('#gc-run-results .gc-checks-title') && "
                           "document.querySelector('#gc-run-results .gc-checks-title').textContent === '레이어'")
    assert page.locator("[data-dxt-tutorial-mock]").count() == 2
    page.evaluate("GraphComposer.tutorial.hideResults()")
    assert page.locator("[data-dxt-tutorial-mock]").count() == 0


def test_a_template_goes_on_the_canvas_only_when_no_work_is_lost(ui):
    page = ui
    assert page.evaluate("GraphComposer.tutorial.useExample('zone_intrusion')") is True
    assert page.evaluate("GraphComposer.state().name") == "zone-intrusion"
    assert page.evaluate("GraphComposer.tutorial.select('zone')") is True
    page.wait_for_selector("#gc-inspector .gc-zone-edit")
    page.evaluate("GraphComposer.loadExample('line_counting')")
    page.evaluate("GraphComposer.state().dirty = true")
    assert page.evaluate("GraphComposer.tutorial.useExample('zone_intrusion')") is False
    assert page.evaluate("GraphComposer.state().name") == "line-counting"
    assert page.evaluate("GraphComposer.tutorial.select('zone')") is False


def test_the_run_tab_comes_back_as_it_was(ui):
    page = ui
    page.evaluate("GraphComposer.tutorial.runTab('live')")
    assert page.is_visible("#gc-live-body") and page.is_hidden("#gc-run-body")
    page.evaluate("GraphComposer.tutorial.runTab('once')")
    page.evaluate("GraphComposer.tutorial.restoreRunTab()")
    assert page.evaluate("GraphComposer.state().runTab") == "once"


def test_reveal_opens_a_palette_group(ui):
    page = ui
    page.click("[data-group='templates'] .gc-group-head")
    assert page.is_hidden("[data-group='templates'] .gc-group-body")
    page.evaluate("GraphPalette.reveal('templates')")
    assert page.is_visible("[data-group='templates'] .gc-group-body")

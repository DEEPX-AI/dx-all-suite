"""DX Compiler — real-use audit (2026-10-11).

Config Builder: "Dataset Path *" is required.

Leaving it empty walked straight through to "Use This Config" and produced a config
with no dataset_path; the user found out only when dxcom failed. An empty path now
stops at step 3 and says why. A path that does not exist still only warns (the
server decides), and Dummy Loader skips the step.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture()
def page():
    from playwright.sync_api import sync_playwright

    server, port = start_module_server("dx_compiler")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','en')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    pg.evaluate("() => { document.getElementById('config-wizard').style.display = 'flex'; }")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    server.shutdown()


def _step(page):
    return page.evaluate("document.querySelector('.wizard-step.active').dataset.step")


def test_an_empty_dataset_path_stops_at_step_three(page):
    page.click("#wiz-next")
    page.click("#wiz-next")
    assert _step(page) == "3"
    page.click("#wiz-next")
    assert _step(page) == "3"
    warning = page.locator("#wiz-dataset-warning")
    assert warning.is_visible() and "Dummy Loader" in warning.inner_text()
    page.fill("#wiz-dataset-path", "/tmp/calib-images")
    page.click("#wiz-next")
    assert _step(page) == "4"


def test_dummy_loader_does_not_ask_for_a_dataset(page):
    page.click("#wiz-next")
    page.click("label.mode-card:has(input[value='dummy'])")
    page.click("#wiz-next")
    assert _step(page) == "4"


def test_a_long_graph_opens_readable_at_its_input(page):
    """A 300-node model was fitted to the viewer at 2 % — a pale column nobody could read (2026-10-11 audit).
    It now opens at a readable zoom with the input node in view; Fit still shows the whole graph."""
    page.evaluate("() => { document.getElementById('config-wizard').style.display = 'none'; }")
    got = page.evaluate("""() => {
        const svg = document.querySelector('svg #graph-content').ownerSVGElement;
        const nodes = [], edges = [];
        for (let i = 0; i < 300; i++) {
            nodes.push({id: 'n' + i, op_type: i % 2 ? 'Conv' : 'Sigmoid', name: 'n' + i});
            if (i) edges.push({from_node: 'n' + (i - 1), to_node: 'n' + i});
        }
        GraphRenderer.renderGraph(svg, {nodes, edges});
        const zp = GraphRenderer.setupZoomPan(svg);
        zp.initialView();
        const first = zp.getTransform();
        const box = svg.getBoundingClientRect();
        const input = svg.querySelector('g.node-group[data-node-id="n0"]').getBoundingClientRect();
        zp.fitToView();
        return {first: first.scale, fit: zp.getTransform().scale,
                inputVisible: input.top >= box.top && input.bottom <= box.bottom
                              && input.left >= box.left && input.right <= box.right};
    }""")
    assert got["fit"] < 0.5, got            # the case that used to open unreadable
    assert got["first"] >= 0.5 and got["inputVisible"], got


def test_picking_a_sample_model_loads_its_graph(page):
    """The sample menu filled the path but sent no change event, so the graph never drew (2026-10-11 audit)."""
    page.evaluate("() => { document.getElementById('config-wizard').style.display = 'none'; }")
    fired = page.evaluate("""() => {
        const got = [];
        document.getElementById('model_path').addEventListener('change', e => got.push('model:' + e.target.value));
        document.getElementById('config_path').addEventListener('change', e => got.push('config:' + e.target.value));
        setupPanel.status = Object.assign({}, setupPanel.status || {}, {sample_models: {
            S: {downloaded: true, onnx_path: '/samples/S.onnx', config_path: '/samples/S.json'}}});
        setupPanel.selectSample('S');
        return got;
    }""")
    assert "model:/samples/S.onnx" in fired and "config:/samples/S.json" in fired, fired

"""E2E tutorial journey — real UI clicks through Start → Next → Continue."""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402
from tests.tutorial_e2e_runner import run_ui_journey, summarize  # noqa: E402

JOURNEY_MODULES = [
    {
        "id": "dx_modelzoo",
        "server": "dx_modelzoo",
        "setup": "() => {}",
        "wait": "#dxToolbar",
        "ready": "() => window._dxTutorial && document.querySelector('.mz-card')",
        "ready_timeout": 60000,
    },
    {
        "id": "dx_app",
        "server": "dx_app",
        "setup": "() => {}",
        "wait": "#dxToolbar",
        "ready": "() => typeof nav==='function' && window._dxTutorial",
    },
    {
        "id": "dx_stream",
        "server": "dx_stream",
        "setup": "() => { const d = document.getElementById('dx-input-modal'); if (d && d.open) d.close(); }",
        "wait": "#dxToolbar",
        "ready": "() => typeof DXStream!=='undefined' && window._dxTutorial",
    },
    {
        "id": "dx_planner",
        "server": "dx_planner",
        "setup": "() => {}",
        "wait": "#plannerWorkspace",
        "ready": "() => window._dxTutorial",
    },
    {
        "id": "dx_benchmark",
        "server": "dx_benchmark",
        "setup": "() => {}",
        "wait": "#dxToolbar",
        "ready": "() => typeof BenchApp!=='undefined' && window._dxTutorial",
    },
    {
        "id": "dx_monitor",
        "server": "dx_monitor",
        "setup": "() => {}",
        "wait": ".monitor-main",
        "ready": "() => window._dxTutorial",
    },
    {
        "id": "dx_agent_dev",
        "server": "dx_agent_dev",
        "setup": "() => {}",
        "wait": ".agent-layout",
        "ready": "() => window._dxTutorial",
    },
]


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


@pytest.fixture()
def page(browser):
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    pg = ctx.new_page()
    try:
        yield pg
    finally:
        pg.close()
        ctx.close()


@pytest.mark.parametrize("mod", JOURNEY_MODULES, ids=[m["id"] for m in JOURNEY_MODULES])
def test_tutorial_ui_journey_no_visual_defects(page, mod):
    server, port = start_module_server(mod["server"])
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
        results = run_ui_journey(
            page,
            lang="en",
            module_setup=mod["setup"],
            wait_selector=mod["wait"],
            ready_script=mod["ready"],
            ready_timeout=mod.get("ready_timeout", 20000),
        )
        failures = summarize(results)
        assert results, f"{mod['id']}: journey produced no step checks"
        assert not failures, f"{mod['id']} UI journey defects:\n" + "\n".join(failures[:30])
    finally:
        server.shutdown()

"""E2E tutorial journey — real UI clicks through Start → Next → Continue."""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402
from tests.tutorial_e2e_runner import mock_left_over, run_ui_journey, summarize  # noqa: E402

JOURNEY_MODULES = [
    {
        # Driving the launcher tour catches steps that point at elements a home redesign
        # removed (users see such steps skipped). The splash must be skipped first: the
        # tutorial engine will not open while its overlay is in the DOM (the shell block
        # in tutorial-init.js), and the intro lasts 12 seconds.
        "id": "launcher",
        "server": "launcher",
        "setup": "() => {}",
        "wait": "#studioGrid",
        "ready": "() => window._dxTutorial && document.getElementById('studioGrid')",
        "ready_timeout": 60000,
    },
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
        # Every module with a tutorial needs a journey here, Compiler included.
        "id": "dx_compiler",
        "server": "dx_compiler",
        "setup": "() => {}",
        "wait": "#dxToolbar",
        "ready": "() => window._dxTutorial && document.getElementById('compile-main-btn')",
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
        "id": "dx_edge",
        "server": "dx_edge",
        "setup": "() => {}",
        "wait": ".edge-main",
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
    # Only matters for the launcher: the tutorial engine will not open while the 12-second
    # intro is in the DOM (tutorial-init.js), and an auto walkthrough would fight the tour
    # the journey drives. Other modules have neither, so this is harmless there.
    ctx.add_init_script(
        "try {"
        " sessionStorage.setItem('dx-splash-seen', '1');"
        " localStorage.setItem('dx-splash-seen', '1');"
        " localStorage.setItem('dx-tutorial-launcher-autostarted', '1');"
        "} catch (e) {}"
    )
    pg = ctx.new_page()
    try:
        yield pg
    finally:
        pg.close()
        ctx.close()


# The tour aims at elements by **pixel coordinates.** Translations differ in length — when
# `Re-download` becomes a longer phrase the button grows and its neighbors wrap or shift —
# so a tour can be right in English and off in another language (one wider table column
# can shift the whole table).
#
# Why Japanese: labels tend to run longer than Korean or Chinese (katakana loanwords), and
# its line-break rules differ from Spanish, so it shakes the layout more. One language
# costs ~8 minutes for 8 modules, so not every language runs — the goal is to find the
# kinds of breakage, not to verify every language.
JOURNEY_LANGS = ["en", "ja"]

_JOURNEY_AXES = [(m, lang) for m in JOURNEY_MODULES for lang in JOURNEY_LANGS]


@pytest.mark.parametrize(
    ("mod", "lang"), _JOURNEY_AXES,
    ids=[f"{m['id']}-{lang}" for m, lang in _JOURNEY_AXES],
)
def test_tutorial_ui_journey_no_visual_defects(page, mod, lang):
    server, port = start_module_server(mod["server"])
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
        results = run_ui_journey(
            page,
            lang=lang,
            module_setup=mod["setup"],
            wait_selector=mod["wait"],
            ready_script=mod["ready"],
            ready_timeout=mod.get("ready_timeout", 20000),
        )
        failures = summarize(results)
        assert results, f"{mod['id']}[{lang}]: journey produced no step checks"
        assert not failures, (
            f"{mod['id']} UI journey defects [{lang}]:\n" + "\n".join(failures[:30]))

        # Injected previews must be gone once the tour ends. They are expected while their
        # step is live, so they are counted here rather than in analyze_step.
        left = mock_left_over(page)
        assert not left, f"{mod['id']}[{lang}]: 투어 종료 후에도 남은 튜토리얼 주입 요소: {left}"
    finally:
        server.shutdown()

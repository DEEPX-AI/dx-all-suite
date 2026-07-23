"""Full-matrix browser zoom audit for all 10 launcher modules."""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from playwright.sync_api import sync_playwright

from tests.server_helpers import start_module_server

ZOOMS = (0.67, 1.0, 1.25, 1.5, 2.0)
VIEWPORTS = ((1440, 900), (1280, 800), (1024, 768))

DOC_OVERFLOW_JS = """(zoom) => {
  document.body.style.zoom = String(zoom);
  const el = document.documentElement;
  return Math.max(0, el.scrollWidth - el.clientWidth);
}"""


# module, label, setup_js, wait_selector
AUDIT_SCENARIOS: list[tuple[str, str, str, str]] = [
    # 1 DX App — all nav pages
    *[
        ("dx_app", f"page:{p}", f"() => nav('{p}')", f"#page-{p}.active")
        for p in ("setup", "models", "run", "bench", "compare", "modelzoo", "lab", "outputs", "reference")
    ],
    # 2 DX Stream
    *[
        ("dx_stream", f"page:{p}", f"() => DXStream.nav('{p}')", f"#page-{p}.active")
        for p in ("setup", "dashboard", "demo", "pipeline", "models", "elements", "custom", "reference")
    ],
    # 3 Model Zoo
    ("dx_modelzoo", "entry", "() => {}", "body"),
    # 4 Compiler
    ("dx_compiler", "entry", "() => {}", "main"),
    ("dx_compiler", "explorer", "() => document.getElementById('explorer-toggle')?.click()", "#explorer-panel"),
    # 5 EdgeGuide
    ("dx_planner", "entry", "() => {}", "#plannerWorkspace"),
    ("dx_planner", "methodology", "() => document.querySelector('[data-open-methodology]')?.click()", "#methodologyDialog[open]"),
    ("dx_planner", "priority-step2", "() => document.getElementById('btnSetupNext')?.click()", "#requirementsStep2"),
    # 6 Benchmark
    *[
        ("dx_benchmark", f"tab:{t}", f"() => BenchApp.switchTab('{t}')", f"#tab-{t}.active")
        for t in ("dashboard", "results", "settings")
    ],
    # 7 Monitor
    ("dx_monitor", "entry", "() => {}", ".monitor-main"),
    # 8 Agent Dev
    ("dx_agent_dev", "entry", "() => {}", ".agent-layout"),
    # 9 SDK Library (launcher)
    ("launcher", "sdk-library", "() => { sessionStorage.setItem('dx-splash-seen','1'); showSdkLibrary(); }", "#sdk-library-view.visible"),
    ("launcher", "sdk-cabinet", "() => { sessionStorage.setItem('dx-splash-seen','1'); showSdkLibrary(); setTimeout(()=>document.querySelector('.sdk-toggle-btn[data-mode=\"cabinet\"]')?.click(),400); }", ".cabinet-drawers"),
    # 10 About DEEPX (launcher)
    ("launcher", "about-deepx", "() => { sessionStorage.setItem('dx-splash-seen','1'); showAboutView(); }", "#about-view.visible"),
    ("launcher", "platform-modal", "() => { sessionStorage.setItem('dx-splash-seen','1'); openPlatformInfo(); }", "#platformInfoOverlay.open"),
    ("launcher", "home", "() => sessionStorage.setItem('dx-splash-seen','1')", "body"),
]


@pytest.mark.parametrize("module,label,setup_js,wait_sel", AUDIT_SCENARIOS)
@pytest.mark.parametrize("viewport", VIEWPORTS, ids=lambda v: f"{v[0]}x{v[1]}")
@pytest.mark.parametrize("zoom", ZOOMS)
def test_module_state_has_no_document_overflow(module: str, label: str, setup_js: str, wait_sel: str, viewport: tuple[int, int], zoom: float):
    server, port = start_module_server(module)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
            page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(500)
            # start_module_server launches only the launcher (no child module servers), so the
            # boot gate never clears headless and gated views stay hidden. Clear it for the audit.
            if module == "launcher":
                page.evaluate("() => document.documentElement.classList.remove('launcher-boot-pending')")
            if module == "dx_app":
                page.wait_for_function("() => typeof nav === 'function'", timeout=20000)
                page.wait_for_function("() => typeof S !== 'undefined' && Array.isArray(S.models)", timeout=20000)
            elif module == "dx_stream":
                page.wait_for_function("() => typeof DXStream !== 'undefined' && typeof DXStream.nav === 'function'", timeout=20000)
            elif module == "dx_benchmark":
                page.wait_for_function("() => typeof BenchApp !== 'undefined' && typeof BenchApp.switchTab === 'function'", timeout=20000)
            elif module == "launcher":
                page.wait_for_function(
                    "() => typeof showSdkLibrary === 'function' && typeof showAboutView === 'function'",
                    timeout=20000,
                )
            if setup_js.strip() != "() => {}" and setup_js.strip() != "() => sessionStorage.setItem('dx-splash-seen','1')":
                page.evaluate(setup_js)
                page.wait_for_timeout(700)
            page.wait_for_selector(wait_sel, timeout=20000)
            overflow = page.evaluate(DOC_OVERFLOW_JS, zoom)
            assert overflow == 0, (
                f"{module}/{label} @ {viewport[0]}x{viewport[1]} zoom={zoom}: document overflow {overflow}px"
            )
            browser.close()
    finally:
        server.shutdown()

"""CSS + browser contracts for Ctrl+scroll / browser zoom resilience."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

ZOOM_SAFE_MODULES = {
    "dx_app": ROOT / "dx_app/static/css/style.css",
    "dx_stream": ROOT / "dx_stream/static/css/stream.css",
    "dx_compiler": ROOT / "dx_compiler/static/css/style.css",
    "dx_benchmark": ROOT / "dx_benchmark/static/css/style.css",
}

PIPELINE_ISO = ROOT / "dx_stream/static/css/pipeline-iso.css"
TOOLBAR_CSS = ROOT / "shared/static/toolbar.css"
LAUNCHER_CSS = ROOT / "launcher/static/style.css"
SDK_LIBRARY_CSS = ROOT / "launcher/static/sdk-library.css"

_OVERFLOW_JS = """(zoom) => {
    document.body.style.zoom = String(zoom);
    const el = document.documentElement;
    return Math.max(0, el.scrollWidth - el.clientWidth);
}"""


def _doc_overflow(page, zoom: float) -> int:
    return page.evaluate(_OVERFLOW_JS, zoom)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("module,css_path", list(ZOOM_SAFE_MODULES.items()))
def test_body_allows_horizontal_scroll_on_zoom(module: str, css_path: Path):
    css = _read(css_path)
    assert "overflow-x:auto" in css.replace(" ", "") or "overflow-x: auto" in css, module
    assert "overflow:hidden" not in css.replace(" ", "").split("overflow-x")[0] or "overflow-y:hidden" in css.replace(" ", "")


@pytest.mark.parametrize("module,css_path", [("dx_app", ZOOM_SAFE_MODULES["dx_app"]), ("dx_stream", ZOOM_SAFE_MODULES["dx_stream"])])
def test_app_shell_uses_percent_width_not_viewport(module: str, css_path: Path):
    css = _read(css_path)
    app_rule = re.search(r"\.app\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    assert app_rule is not None, f"{module} .app rule missing"
    body = app_rule.group("body").replace(" ", "")
    assert "width:100vw" not in body, f"{module} .app must not pin shell to 100vw"
    assert "width:100%" in body


@pytest.mark.parametrize("module,css_path", [("dx_app", ZOOM_SAFE_MODULES["dx_app"]), ("dx_stream", ZOOM_SAFE_MODULES["dx_stream"])])
def test_modal_overlay_uses_percent_not_viewport(module: str, css_path: Path):
    css = _read(css_path)
    overlay = re.search(r"\.modal-overlay\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    assert overlay is not None, f"{module} .modal-overlay rule missing"
    body = overlay.group("body").replace(" ", "")
    assert "width:100vw" not in body, f"{module} modal overlay must not use 100vw"
    assert "height:100vh" not in body, f"{module} modal overlay must not use 100vh"
    assert "width:100%" in body


def test_pipeline_builder_scrolls_when_rails_overflow():
    css = _read(PIPELINE_ISO)
    builder = re.search(r"\.pipeline-builder\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    assert builder is not None
    body = builder.group("body")
    assert "overflow-x: auto" in body or "overflow-x:auto" in body.replace(" ", "")
    assert "min-width: 0" in body or "min-width:0" in body.replace(" ", "")


def test_pipeline_property_panel_can_shrink():
    css = _read(PIPELINE_ISO)
    panel = re.search(r"\.property-panel\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    assert panel is not None
    body = panel.group("body")
    assert "flex: 0 1" in body or "flex:0 1" in body.replace(" ", "")
    assert "min-width: 280px" not in body


def test_compiler_form_panel_uses_min_width():
    css = _read(ZOOM_SAFE_MODULES["dx_compiler"])
    assert "width: min(550px" in css or "width:min(550px" in css.replace(" ", "")


def test_toolbar_scrolls_on_narrow_header():
    css = _read(TOOLBAR_CSS)
    toolbar = re.search(r"\.dx-toolbar\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    assert toolbar is not None
    body = toolbar.group("body")
    assert "overflow-x: auto" in body


def test_platform_values_grid_wraps_on_narrow_width():
    css = _read(LAUNCHER_CSS)
    values = re.search(r"\.platform-values\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    panel = re.search(r"\.platform-info-panel\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    assert values is not None
    assert panel is not None
    assert "auto-fit" in values.group("body")
    assert "overflow-x: auto" in panel.group("body")


def test_sdk_list_sidebar_can_shrink():
    css = _read(SDK_LIBRARY_CSS)
    sidebar = re.search(r"\.sdk-list-sidebar\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    layout = re.search(r"\.sdk-list-layout\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    assert sidebar is not None
    assert layout is not None
    body = sidebar.group("body")
    assert "flex: 0 1" in body or "flex:0 1" in body.replace(" ", "")
    assert "min-width: 240px" not in body
    assert "overflow-x: auto" in layout.group("body")


@pytest.mark.parametrize(
    "module",
    ["dx_app", "dx_stream", "dx_compiler", "dx_benchmark", "dx_planner", "dx_modelzoo", "dx_monitor", "dx_agent_dev"],
)
def test_entry_page_no_horizontal_overflow_at_browser_zoom(module: str):
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    from tests.server_helpers import start_module_server

    server, port = start_module_server(module)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(500)
            for zoom in (0.67, 1.0, 1.25, 1.5):
                overflow = _doc_overflow(page, zoom)
                assert overflow == 0, f"{module} overflow {overflow}px at zoom {zoom}"
            browser.close()
    finally:
        server.shutdown()


@pytest.mark.parametrize("zoom", [0.67, 1.0, 1.25, 1.5])
def test_launcher_platform_modal_no_horizontal_overflow(zoom: float):
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    from tests.server_helpers import start_module_server

    server, port = start_module_server("launcher")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=30000)
            page.evaluate(
                """() => {
                    sessionStorage.setItem('dx-splash-seen', '1');
                    if (typeof openPlatformInfo === 'function') openPlatformInfo();
                }"""
            )
            page.wait_for_selector("#platformInfoOverlay.open", timeout=10000)
            overflow = _doc_overflow(page, zoom)
            assert overflow == 0, f"launcher platform modal overflow {overflow}px at zoom {zoom}"
            browser.close()
    finally:
        server.shutdown()


@pytest.mark.parametrize("zoom", [0.67, 1.0, 1.25, 1.5])
def test_launcher_sdk_library_no_horizontal_overflow(zoom: float):
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    from tests.server_helpers import start_module_server

    server, port = start_module_server("launcher")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=30000)
            page.evaluate(
                """() => {
                    sessionStorage.setItem('dx-splash-seen', '1');
                    // Only the launcher server runs headless, so its boot gate never clears — drop it.
                    document.documentElement.classList.remove('launcher-boot-pending');
                    if (typeof showSdkLibrary === 'function') showSdkLibrary();
                }"""
            )
            page.wait_for_selector("#sdk-library-view.visible", timeout=10000)
            page.wait_for_selector(".sdk-list-sidebar, .cabinet-drawers", timeout=30000)
            overflow = _doc_overflow(page, zoom)
            assert overflow == 0, f"launcher sdk library overflow {overflow}px at zoom {zoom}"
            browser.close()
    finally:
        server.shutdown()


@pytest.mark.parametrize("zoom", [0.67, 1.0, 1.25, 1.5])
def test_dx_stream_pipeline_page_no_horizontal_overflow(zoom: float):
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    from tests.server_helpers import start_module_server

    server, port = start_module_server("dx_stream")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_function("() => typeof DXStream !== 'undefined' && typeof DXStream.nav === 'function'")
            page.evaluate("() => DXStream.nav('pipeline')")
            page.wait_for_selector("#page-pipeline.active", timeout=10000)
            page.wait_for_selector(".pipeline-builder", timeout=10000)
            overflow = _doc_overflow(page, zoom)
            assert overflow == 0, f"dx_stream pipeline overflow {overflow}px at zoom {zoom}"
            browser.close()
    finally:
        server.shutdown()

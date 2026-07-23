"""Browser zoom audit for modal, dialog, and dropdown open states."""
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

# module, label, pre_js, open_js, wait_js
MODAL_SCENARIOS: list[tuple[str, str, str, str, str]] = [
    (
        "dx_modelzoo",
        "detail-view",
        "() => {}",
        """async () => {
          const resp = await fetch('/api/catalog');
          const data = await resp.json();
          const id = (data.models && data.models[0] && data.models[0].id) || '';
          if (!id) throw new Error('no catalog model');
          location.hash = 'model=' + encodeURIComponent(id);
        }""",
        """() => {
          const el = document.getElementById('detailView');
          return el && el.style.display !== 'none' && el.innerHTML.trim().length > 40;
        }""",
    ),
    (
        "dx_stream",
        "model-detail-modal",
        "() => DXStream.nav('models')",
        """() => {
          const m = DXStream._allModels && DXStream._allModels[0];
          if (!m) throw new Error('no stream models');
          DXStream.showModelDetail(m.name);
        }""",
        "() => document.getElementById('model-detail-modal')?.open === true",
    ),
    (
        "dx_stream",
        "model-detail-metadata",
        "() => DXStream.nav('models')",
        """() => {
          const m = DXStream._allModels && DXStream._allModels[0];
          if (!m) throw new Error('no stream models');
          DXStream.showModelDetail(m.name);
          document.querySelector('.modal-tab[data-tab=\"metadata\"]')?.click();
        }""",
        "() => document.querySelector('.modal-tab[data-tab=\"metadata\"]')?.classList.contains('active')",
    ),
    (
        "dx_stream",
        "input-modal",
        "() => {}",
        """() => {
          const dlg = document.getElementById('dx-input-modal');
          const titleEl = document.getElementById('dx-input-modal-title');
          if (titleEl) titleEl.textContent = 'Zoom audit test';
          if (dlg && dlg.showModal) dlg.showModal();
        }""",
        "() => document.getElementById('dx-input-modal')?.open === true",
    ),
    (
        "dx_compiler",
        "sample-dropdown",
        "() => {}",
        """() => {
          const container = document.getElementById('sample-select-container');
          if (container) container.style.display = 'block';
          const dd = document.getElementById('sample-dropdown');
          if (dd) {
            dd.innerHTML = '<div class=\"sample-dropdown-item\">Sample A</div>'
              + '<div class=\"sample-dropdown-item\">Sample B</div>';
            dd.classList.add('open');
            dd.style.top = '120px';
            dd.style.left = '16px';
          }
        }""",
        "() => document.getElementById('sample-dropdown')?.classList.contains('open')",
    ),
    (
        "dx_app",
        "modal-detail",
        "() => nav('bench')",
        "() => openModal('modal-detail')",
        "() => document.getElementById('modal-detail')?.open === true",
    ),
    (
        "dx_app",
        "modal-fb",
        "() => nav('run')",
        "() => openModal('modal-fb')",
        "() => document.getElementById('modal-fb')?.open === true",
    ),
    (
        "dx_app",
        "modal-imgpreview",
        "() => {}",
        "() => openModal('modal-imgpreview')",
        "() => document.getElementById('modal-imgpreview')?.open === true",
    ),
    (
        "dx_planner",
        "detail-panel",
        "() => {}",
        """() => {
          if (typeof PlannerWorkspace === 'undefined') throw new Error('PlannerWorkspace missing');
          PlannerWorkspace.showRecommendations();
          PlannerWorkspace.showDetail('dx-m1');
        }""",
        "() => { const p = document.getElementById('detailPanel'); return p && !p.hidden; }",
    ),
    (
        "launcher",
        "sdk-book-viewer",
        "() => { sessionStorage.setItem('dx-splash-seen','1'); showSdkLibrary(); }",
        """async () => {
          const resp = await fetch('/static/sdk-library-data.json');
          const data = await resp.json();
          const drawer = data.drawers && data.drawers[0];
          const file = drawer && drawer.sections && drawer.sections[0] && drawer.sections[0].files[0];
          if (!file || !window._sdkLib) throw new Error('sdk book unavailable');
          window._sdkLib.openBookViewer(file, drawer.color);
        }""",
        "() => document.getElementById('sdkBookViewer')?.classList.contains('open')",
    ),
    (
        "launcher",
        "sdk-arch-overlay",
        "() => { sessionStorage.setItem('dx-splash-seen','1'); showSdkLibrary(); }",
        "() => document.getElementById('sdkArchBtn')?.click()",
        "() => document.getElementById('sdkArchOverlay')?.classList.contains('open')",
    ),
    (
        "launcher",
        "platform-modal",
        "() => sessionStorage.setItem('dx-splash-seen','1')",
        "() => openPlatformInfo()",
        "() => document.getElementById('platformInfoOverlay')?.classList.contains('open')",
    ),
]


def _wait_module_ready(page, module: str) -> None:
    if module == "dx_app":
        page.wait_for_function("() => typeof nav === 'function'", timeout=20000)
        page.wait_for_function("() => typeof openModal === 'function'", timeout=20000)
    elif module == "dx_stream":
        page.wait_for_function(
            "() => typeof DXStream !== 'undefined' && typeof DXStream.nav === 'function'",
            timeout=20000,
        )
    elif module == "dx_planner":
        page.wait_for_function("() => typeof PlannerWorkspace !== 'undefined'", timeout=20000)
    elif module == "launcher":
        page.wait_for_function(
            "() => typeof showSdkLibrary === 'function' && typeof openPlatformInfo === 'function'",
            timeout=20000,
        )
    elif module == "dx_modelzoo":
        page.wait_for_function("() => typeof renderDetailPage === 'function'", timeout=20000)


@pytest.mark.parametrize("module,label,pre_js,open_js,wait_js", MODAL_SCENARIOS)
@pytest.mark.parametrize("viewport", VIEWPORTS, ids=lambda v: f"{v[0]}x{v[1]}")
@pytest.mark.parametrize("zoom", ZOOMS)
def test_modal_state_has_no_document_overflow(
    module: str,
    label: str,
    pre_js: str,
    open_js: str,
    wait_js: str,
    viewport: tuple[int, int],
    zoom: float,
):
    server, port = start_module_server(module)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
            page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(500)
            # Launcher boot gate never clears headless (only the launcher server runs) — clear it.
            if module == "launcher":
                page.evaluate("() => document.documentElement.classList.remove('launcher-boot-pending')")
            _wait_module_ready(page, module)

            if pre_js.strip() not in ("() => {}", "() => sessionStorage.setItem('dx-splash-seen','1')"):
                page.evaluate(pre_js)
                page.wait_for_timeout(700)

            if module == "dx_stream" and "models" in pre_js:
                page.wait_for_function(
                    "() => Array.isArray(DXStream._allModels) && DXStream._allModels.length > 0",
                    timeout=20000,
                )
            if module == "launcher" and "showSdkLibrary" in pre_js:
                page.wait_for_selector("#sdk-library-view.visible", timeout=20000)
                page.wait_for_function("() => window._sdkLib && typeof window._sdkLib.openBookViewer === 'function'", timeout=20000)

            page.evaluate(open_js)
            page.wait_for_function(wait_js, timeout=20000)
            page.wait_for_timeout(300)

            overflow = page.evaluate(DOC_OVERFLOW_JS, zoom)
            assert overflow == 0, (
                f"{module}/{label} modal @ {viewport[0]}x{viewport[1]} zoom={zoom}: document overflow {overflow}px"
            )
            browser.close()
    finally:
        server.shutdown()

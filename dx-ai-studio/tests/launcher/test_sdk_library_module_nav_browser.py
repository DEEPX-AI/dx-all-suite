"""Browser E2E: SDK Library → top nav module tab must reveal module iframe."""
from __future__ import annotations

import os
import sys

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

MODULE_TABS = (
    ("app", "dx_app", "DX_APP_PORT", "#dxToolbar"),
    ("benchmark", "dx_benchmark", "DX_BENCHMARK_PORT", "#tab-dashboard"),
    ("dx_monitor", "dx_monitor", "DX_MONITOR_PORT", ".monitor-main"),
)


def _purge_launcher_modules() -> None:
    for name in list(sys.modules):
        if name == "launcher" or name.startswith("launcher."):
            del sys.modules[name]


WAIT_IFRAME_READY = """(readySel) => new Promise((resolve, reject) => {
  let n = 0;
  const tick = () => {
    const sdk = document.getElementById('sdk-library-view');
    const frame = document.getElementById('appFrame');
    const iframe = document.getElementById('appIframe');
    const backdrop = document.querySelector('.dxt-toc-backdrop.open');
    if (backdrop) {
      if (++n > 120) reject(new Error('tutorial backdrop still open'));
      else setTimeout(tick, 100);
      return;
    }
    if (!sdk || sdk.classList.contains('visible')) {
      if (++n > 120) reject(new Error('sdk-library-view still visible'));
      else setTimeout(tick, 100);
      return;
    }
    if (!frame || frame.style.display === 'none') {
      if (++n > 120) reject(new Error('appFrame hidden'));
      else setTimeout(tick, 100);
      return;
    }
    if (!iframe || iframe.hidden || !iframe.classList.contains('active')) {
      if (++n > 120) reject(new Error('module iframe not active'));
      else setTimeout(tick, 100);
      return;
    }
    try {
      const doc = iframe.contentDocument;
      if (doc && doc.body && doc.body.childElementCount > 0 &&
          doc.querySelector(readySel)) {
        resolve(true);
        return;
      }
    } catch (e) {}
    if (++n > 160) reject(new Error('iframe content timeout'));
    else setTimeout(tick, 250);
  };
  tick();
})"""


@pytest.fixture()
def page():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        try:
            yield pg
        finally:
            pg.close()
            ctx.close()
            browser.close()


@pytest.mark.parametrize("launch_key,module,env_key,ready_sel", MODULE_TABS)
def test_sdk_library_nav_tab_shows_module(page, launch_key, module, env_key, ready_sel):
    mod_server, mod_port = start_module_server(module)
    prev = os.environ.get(env_key)
    os.environ[env_key] = str(mod_port)
    _purge_launcher_modules()
    launch_server, launch_port = start_module_server("launcher")
    try:
        page.goto(f"http://127.0.0.1:{launch_port}/", wait_until="domcontentloaded", timeout=60000)
        page.evaluate("() => sessionStorage.setItem('dx-splash-seen','1')")
        page.wait_for_function(
            "() => window.LauncherRouter && typeof window.LauncherRouter._showSdk === 'function'",
            timeout=30000,
        )
        page.evaluate("() => window.LauncherRouter._showSdk({ push: false })")
        page.wait_for_selector("#sdk-library-view.visible", timeout=30000)
        page.click(f'.nav-tab[data-app="{launch_key}"]')
        page.wait_for_function(WAIT_IFRAME_READY, arg=ready_sel, timeout=90000)
        has_content = page.evaluate(
            f"""() => {{
              const iframe = document.getElementById('appIframe');
              if (!iframe || !iframe.contentDocument) return false;
              return !!iframe.contentDocument.querySelector({ready_sel!r});
            }}"""
        )
        assert has_content, f"module selector {ready_sel!r} not found after SDK → {launch_key} nav"
    finally:
        launch_server.shutdown()
        mod_server.shutdown()
        if prev is None:
            os.environ.pop(env_key, None)
        else:
            os.environ[env_key] = prev


@pytest.mark.parametrize("launch_key,module,env_key,ready_sel", MODULE_TABS[:1])
def test_sdk_library_nav_tab_with_tutorial_toc_open(page, launch_key, module, env_key, ready_sel):
    """Regression: active SDK tutorial TOC must not block module view after tab switch."""
    mod_server, mod_port = start_module_server(module)
    prev = os.environ.get(env_key)
    os.environ[env_key] = str(mod_port)
    _purge_launcher_modules()
    launch_server, launch_port = start_module_server("launcher")
    try:
        page.goto(f"http://127.0.0.1:{launch_port}/", wait_until="domcontentloaded", timeout=60000)
        page.evaluate("() => sessionStorage.setItem('dx-splash-seen','1')")
        page.wait_for_function(
            "() => window.LauncherRouter && window._dxTutorial",
            timeout=45000,
        )
        page.evaluate("() => window.LauncherRouter._showSdk({ push: false })")
        page.wait_for_selector("#sdk-library-view.visible", timeout=30000)
        page.wait_for_function(
            "() => window._dxTutorial && typeof window._dxTutorial.showTOC === 'function'",
            timeout=30000,
        )
        page.evaluate("() => window._dxTutorial.showTOC()")
        page.wait_for_selector(".dxt-toc-backdrop.open", timeout=10000)
        page.click(f'.nav-tab[data-app="{launch_key}"]')
        page.wait_for_function(WAIT_IFRAME_READY, arg=ready_sel, timeout=90000)
    finally:
        launch_server.shutdown()
        mod_server.shutdown()
        if prev is None:
            os.environ.pop(env_key, None)
        else:
            os.environ[env_key] = prev

"""Browser audit: launcher ↔ module iframe language synchronization."""
from __future__ import annotations

import os
import sys

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

LANGS = ("ko", "ja", "zh-CN", "es")
IFRAME_MODULES = (
    ("app", "dx_app", "DX_APP_PORT", "#dxToolbar"),
    ("stream", "dx_stream", "DX_STREAM_PORT", "#dxToolbar"),
    ("zoo", "dx_modelzoo", "DX_ZOO_PORT", ".mz-card"),
)


def _purge_launcher_modules() -> None:
    for name in list(sys.modules):
        if name == "launcher" or name.startswith("launcher."):
            del sys.modules[name]

WAIT_IFRAME_LOADED = """() => new Promise((resolve, reject) => {
  let n = 0;
  const tick = () => {
    const f = document.getElementById('appIframe');
    if (f && f.dataset.loadState === 'loaded') {
      try {
        const doc = f.contentDocument;
        if (doc && doc.body) {
          resolve(true);
          return;
        }
      } catch (e) {}
    }
    if (++n > 120) reject(new Error('iframe load timeout'));
    else setTimeout(tick, 250);
  };
  tick();
})"""

READ_IFRAME_LANG = """() => {
  const f = document.getElementById('appIframe');
  if (!f || !f.contentDocument) return { ok: false, reason: 'no iframe doc' };
  const win = f.contentWindow;
  const body = f.contentDocument.body;
  return {
    ok: true,
    dxi18n: win.DXI18n ? win.DXI18n.lang : null,
    htmlLang: f.contentDocument.documentElement.lang || '',
    bodyClasses: Array.from(body.classList).filter(c => c.startsWith('lang-')),
    storage: localStorage.getItem('dx-lang'),
  };
}"""


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


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("launch_key,module,env_key,ready_sel", IFRAME_MODULES)
def test_launcher_lang_propagates_to_iframe(page, lang, launch_key, module, env_key, ready_sel):
    mod_server, mod_port = start_module_server(module)
    prev = os.environ.get(env_key)
    os.environ[env_key] = str(mod_port)
    _purge_launcher_modules()
    launch_server, launch_port = start_module_server("launcher")
    try:
        page.goto(f"http://127.0.0.1:{launch_port}/", wait_until="domcontentloaded", timeout=60000)
        page.evaluate("() => sessionStorage.setItem('dx-splash-seen','1')")
        page.wait_for_function("() => window.DXLauncher && window.LauncherRouter", timeout=20000)
        page.evaluate("(lang) => window.DXLauncher.selectLang(lang)", lang)
        page.evaluate(
            "(key) => window.LauncherRouter._showApp(key, { push: false, forceReload: true })",
            launch_key,
        )
        page.wait_for_function(WAIT_IFRAME_LOADED, timeout=90000)
        page.wait_for_function(
            f"""() => {{
              const f = document.getElementById('appIframe');
              return !!(f && f.contentDocument && f.contentDocument.querySelector({ready_sel!r}));
            }}""",
            timeout=30000,
        )
        snap = page.evaluate(READ_IFRAME_LANG)
        assert snap.get("ok"), snap.get("reason", "iframe lang read failed")
        assert snap["storage"] == lang
        assert snap["dxi18n"] == lang, f"DXI18n.lang={snap['dxi18n']!r} expected {lang!r}"
        assert f"lang-{lang}" in snap["bodyClasses"], snap["bodyClasses"]
    finally:
        launch_server.shutdown()
        mod_server.shutdown()
        if prev is None:
            os.environ.pop(env_key, None)
        else:
            os.environ[env_key] = prev


def test_iframe_lang_change_syncs_launcher_on_go_home(page):
    mod_server, mod_port = start_module_server("dx_app")
    prev = os.environ.get("DX_APP_PORT")
    os.environ["DX_APP_PORT"] = str(mod_port)
    _purge_launcher_modules()
    launch_server, launch_port = start_module_server("launcher")
    try:
        page.goto(f"http://127.0.0.1:{launch_port}/", wait_until="domcontentloaded", timeout=60000)
        page.evaluate("() => sessionStorage.setItem('dx-splash-seen','1')")
        page.wait_for_function("() => window.DXLauncher && window.LauncherRouter", timeout=20000)
        page.evaluate(
            "() => window.LauncherRouter._showApp('app', { push: false, forceReload: true })"
        )
        page.wait_for_function(WAIT_IFRAME_LOADED, timeout=90000)
        page.evaluate(
            """() => {
              const f = document.getElementById('appIframe');
              f.contentWindow.DXI18n.setLang('ja');
            }"""
        )
        page.wait_for_timeout(400)
        page.evaluate("() => window.DXLauncher.goHome()")
        page.wait_for_timeout(400)
        parent = page.evaluate(
            """() => ({
              lang: window.DXLauncher._lang,
              bodyClass: Array.from(document.body.classList).filter(c => c.startsWith('lang-')),
              storage: localStorage.getItem('dx-lang'),
            })"""
        )
        assert parent["storage"] == "ja"
        assert parent["lang"] == "ja"
        assert "lang-ja" in parent["bodyClass"]
    finally:
        launch_server.shutdown()
        mod_server.shutdown()
        if prev is None:
            os.environ.pop("DX_APP_PORT", None)
        else:
            os.environ["DX_APP_PORT"] = prev


@pytest.mark.parametrize("lang", ("ko", "ja"))
def test_tutorial_step_text_updates_on_lang_switch(page, lang):
    server, port = start_module_server("dx_app")
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_function(
            "() => window._dxTutorial && typeof window._dxTutorial.startSection === 'function'",
            timeout=30000,
        )
        page.evaluate("() => { localStorage.setItem('dx-lang','en'); window.DXI18n.setLang('en'); }")
        page.evaluate("() => window._dxTutorial.startSection('setup')")
        page.wait_for_selector(".dxt-tooltip.active", timeout=15000)
        en_title = page.eval_on_selector(".dxt-tip-title", "el => el.textContent.trim()")
        page.evaluate("(lang) => window.DXI18n.setLang(lang)", lang)
        page.wait_for_timeout(400)
        new_title = page.eval_on_selector(".dxt-tip-title", "el => el.textContent.trim()")
        assert new_title, "tutorial title empty after lang switch"
        assert new_title != en_title or lang == "en", (
            f"tutorial title unchanged after switch to {lang}: {new_title!r}"
        )
    finally:
        server.shutdown()

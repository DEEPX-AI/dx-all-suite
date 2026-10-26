"""An icon + label keeps its icon when the language changes.

DXIcon.label(el, name, text) inserts an icon svg and a text node. For elements matched by a module dictionary's
_DX_I18N_SELECTORS (h3, buttons …), replacing the whole textContent in shared/i18n.js _translateEl on a language
change would drop the icon, so when the only element child is the icon, only the text node is replaced.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


def test_an_icon_label_keeps_its_icon_across_a_language_switch():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_compiler")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    try:
        ctx = br.new_context(viewport={"width": 1280, "height": 800}, reduced_motion="reduce")
        ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');")
        page = ctx.new_page()
        page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
        page.wait_for_function("() => window.DXIcon && DXIcon.label && window.DXI18n", timeout=10000)
        out = page.evaluate("""async () => {
          const h = document.createElement('h3'); document.body.appendChild(h);
          DXIcon.label(h, 'check', T('Compilation Complete'));
          const before = [h.querySelector('svg.dx-ico use').getAttribute('href').split('#')[1], h.textContent.trim()];
          DXI18n.setLang('ko'); await new Promise(r => setTimeout(r, 200));
          const ko = [h.querySelectorAll('svg.dx-ico').length, h.textContent.trim()];
          DXI18n.setLang('en'); await new Promise(r => setTimeout(r, 200));
          return { before, ko, en: [h.querySelectorAll('svg.dx-ico').length, h.textContent.trim()] };
        }""")
        assert out["before"] == ["check", "Compilation Complete"], out
        assert out["ko"] == [1, "컴파일 완료"], out
        assert out["en"] == [1, "Compilation Complete"], out
        ctx.close()
    finally:
        br.close()
        pw.stop()
        srv.shutdown()

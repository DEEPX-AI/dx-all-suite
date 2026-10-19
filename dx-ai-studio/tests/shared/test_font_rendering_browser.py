"""Fonts render the way they are declared, not just declared.

A Regular-only file declared as `font-weight:100 900` makes the browser believe every weight exists, so it does not
even synthesise bold, and all bold Latin text renders as Regular. A real weight changes the text width.
"""
from __future__ import annotations

import re

import pytest

pytest.importorskip("playwright.sync_api")

from tests.browser_support import launch_browser  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402

PROBE = """async ([lang, text]) => {
  document.documentElement.lang = lang;
  await document.fonts.ready;
  const el = document.createElement('span');
  el.textContent = text; el.style.fontSize = '56px';
  el.style.fontFamily = getComputedStyle(document.body).fontFamily;
  document.body.appendChild(el);
  const widths = {};
  for (const w of [400, 700]) {
    el.style.fontWeight = String(w);
    await document.fonts.load(`${w} 56px ${el.style.fontFamily}`, text);
    widths[w] = el.getBoundingClientRect().width;
  }
  el.remove();
  return widths;
}"""


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    server, port = start_module_server("dx_app")
    try:
        with sync_playwright() as p:
            browser = launch_browser(p, "chromium")
            pg = browser.new_page()
            pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
            yield pg
            browser.close()
    finally:
        server.shutdown()


@pytest.mark.parametrize("lang,text", [
    ("en", "Describe anything. Run it on DX-M1."),
    ("es", "Describe cualquier cosa. Ejecútalo en DX-M1."),
])
def test_latin_bold_is_a_real_weight(page, lang, text):
    """Width only tells weights apart for Latin. A CJK glyph is 1em wide at any weight, so a real weight
    gives the same width there."""
    w = page.evaluate(PROBE, [lang, text])
    assert w["700"] > w["400"] * 1.02, w


@pytest.mark.parametrize("family", ["DX CJK KR", "DX CJK JP", "DX CJK SC", "DX CJK TC"])
def test_cjk_faces_cover_400_to_700_so_the_browser_never_synthesises_bold(page, family):
    """The face's font-weight range must cover 400–700 so weights in between render as asked.
    With only 400 and 700 files, a request for 600 renders as 700."""
    weight = page.evaluate(
        "(fam) => [...document.fonts].filter(f => f.family.replace(/\"/g, '') === fam)"
        ".map(f => f.weight)", family)
    assert len(weight) == 1, weight
    lo, hi = (float(x) for x in weight[0].split())
    assert lo <= 400 and hi >= 700, weight


# Match exactly: a "Pretendard" prefix match would pass even if the ja face "Pretendard JP" were used for ko.
# Noto's " Thin" is only the name of the variable font's default instance, not the rendered weight.
@pytest.mark.parametrize("lang,text,family", [
    ("ko", "무엇이든", r"Pretendard Variable"),
    ("ja", "説明", r"Pretendard JP Variable"),
    ("zh-CN", "描述", r"Noto Sans SC( Thin)?"),
    ("zh-TW", "描述", r"Noto Sans TC( Thin)?"),
])
def test_each_language_renders_with_its_own_cjk_font(page, lang, text, family):
    page.evaluate("""async ([lang, text]) => {
      document.documentElement.lang = lang;
      const el = document.createElement('div'); el.id = 'fp'; el.textContent = text;
      el.style.fontFamily = getComputedStyle(document.body).fontFamily;
      document.body.appendChild(el);
      await document.fonts.load(`400 16px ${el.style.fontFamily}`, text);
    }""", [lang, text])
    cdp = page.context.new_cdp_session(page)
    cdp.send("DOM.enable")
    cdp.send("CSS.enable")
    root = cdp.send("DOM.getDocument")["root"]["nodeId"]
    node = cdp.send("DOM.querySelector", {"nodeId": root, "selector": "#fp"})["nodeId"]
    fonts = [f["familyName"] for f in cdp.send("CSS.getPlatformFontsForNode", {"nodeId": node})["fonts"]]
    page.evaluate("() => document.getElementById('fp').remove()")
    assert fonts and re.fullmatch(family, fonts[0]), fonts

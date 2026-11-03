"""Canvas chart colours follow the page theme.

The palette used to be dark-only: near-white label text with a black 3 px halo (strokeText). On the light theme the
halo smeared over the version-trend value labels and the past-version numbers were hard to read. Light theme: dark
text with a light halo; dark theme: unchanged.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_benchmark")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','en')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _palette(page, theme):
    page.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
    return page.evaluate("Dashboard.palette()")


def _luma(colour):
    """Relative brightness 0-255 of '#rrggbb' or 'rgba(r,g,b,a)'."""
    c = colour.strip()
    if c.startswith("#"):
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
    else:
        r, g, b = (float(x) for x in c[c.index("(") + 1:c.index(")")].split(",")[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def test_light_theme_uses_dark_text_on_a_light_halo(page):
    cc = _palette(page, "light")
    assert _luma(cc["emph"]) < 80
    assert _luma(cc["outline"]) > 200


def test_dark_theme_keeps_light_text_on_a_dark_halo(page):
    cc = _palette(page, "dark")
    assert _luma(cc["emph"]) > 200
    assert _luma(cc["outline"]) < 50

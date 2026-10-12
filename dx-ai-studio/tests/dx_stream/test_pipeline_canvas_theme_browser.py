"""Pipeline Builder canvas — node names, grid and links stay visible in the light theme.

They follow the current theme colors: white text (#f5f5f7) and translucent white lines cannot be read on a light
background, and the canvas must repaint when the theme changes.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_stream")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-theme','dark');")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.evaluate("() => DXStream.nav('pipeline')")
    pg.wait_for_function("() => DXStream._pipeState && DXStream._pipeState.elementFlat && DXStream._pipeState.elementFlat.length",
                         timeout=15000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _luma(page):
    """[background brightness, mean node-name text brightness] (0–255); text = name-area pixels >40 off the background."""
    return page.evaluate("""() => {
      const st = DXStream._pipeState;
      if (!st.nodes.length) _addNode(st.elementFlat[0].name, 300, 200);
      _refreshCanvas();
      const c = document.getElementById('pipeline-canvas'), g = c.getContext('2d');
      const L = (d, i) => 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
      const bg = L(g.getImageData(3, 3, 1, 1).data, 0);
      const n = st.nodes[0];
      const x = Math.round(st.offsetX + (n.x + 26) * st.zoom), y = Math.round(st.offsetY + (n.y + 56 / 2 - 14) * st.zoom);
      const d = g.getImageData(x, y, Math.round(90 * st.zoom), Math.round(12 * st.zoom)).data;
      let sum = 0, cnt = 0;
      for (let i = 0; i < d.length; i += 4) { const l = L(d, i); if (Math.abs(l - bg) > 40) { sum += l; cnt++; } }
      return [bg, cnt ? sum / cnt : bg];
    }""")


def test_node_names_are_readable_in_both_themes(page):
    bg, text = _luma(page)
    assert bg < 80 and text > bg + 100, f"어두운 테마: 어두운 바탕 · 밝은 글자 (바탕 {bg:.0f}, 글자 {text:.0f})"
    page.evaluate("() => DXTheme.setTheme('light')")
    try:
        page.wait_for_timeout(300)
        bg, text = _luma(page)
        assert bg > 200, f"밝은 테마로 바꾸면 캔버스 바탕도 밝다 — 테마 색을 다시 읽는다 (바탕 {bg:.0f})"
        assert text < bg - 100, f"밝은 바탕 위의 이름은 어두운 글자 (바탕 {bg:.0f}, 글자 {text:.0f})"
    finally:
        page.evaluate("() => DXTheme.setTheme('dark')")

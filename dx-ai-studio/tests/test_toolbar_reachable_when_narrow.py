"""Toolbar buttons must stay **reachable** on a narrow screen (= high browser zoom).

The zoom audit only looks at document-wide horizontal overflow
(`documentElement.scrollWidth - clientWidth`), so it cannot see this:

    vw=512
      .dx-shell-header       505/456  <- overflows by 49px
      .dx-shell-body         overflow-x: hidden   <- clips it
      => document overflow is 0, so that gate passes.
      => .dx-toolbar sits at l=366 r=561, pushed past the screen (512),
         and the theme and settings buttons disappear.

`.dx-toolbar` has `overflow-x: auto` of its own, but that scrolls **inside** the toolbar.
When the content is as wide as the toolbar there is nothing to scroll, and what gets clipped
is the **whole** toolbar. Inner scrolling cannot rescue outer clipping.

Widths are measured with a narrow viewport, not `body.style.zoom`: style.zoom fires no
resize, so the tab overflow calculation is not refreshed and the result is misleading.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.browser_support import launch_browser  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402

# 1024 = default, 683 ≈ 150% zoom, 512 ≈ 200% zoom (the CSS width shrinks on the same physical screen)
WIDTHS = (1024, 683, 512)

_UNREACHABLE_JS = """() => {
  const de = document.documentElement, vw = de.clientWidth;
  const out = [];
  for (const el of document.querySelectorAll('.dx-toolbar-btn, .dx-tab, .dx-tab-overflow')) {
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    if ((r.width === 0 && r.height === 0) || cs.display === 'none' || cs.visibility === 'hidden') continue;
    if (r.right <= vw + 2 && r.left >= -2) continue;
    // 스크롤 가능한 조상이 있으면 사용자가 스크롤해서 닿을 수 있다 — 결함이 아니다.
    let p = el.parentElement, reachable = false;
    while (p && p !== document.body) {
      const pcs = getComputedStyle(p);
      if (/(auto|scroll)/.test(pcs.overflowX) && p.scrollWidth > p.clientWidth + 2) { reachable = true; break; }
      p = p.parentElement;
    }
    if (!reachable) out.push(((el.textContent || '').trim().slice(0, 12)) + ' @' + Math.round(r.right));
  }
  return out;
}"""


# All eight modules share the shell (dx-shell.css), so a fix in shared styles is checked in
# every module, not only the one where a problem shows up first.
MODULES = ("dx_app", "dx_compiler", "dx_modelzoo", "dx_benchmark",
           "dx_stream", "dx_planner", "dx_monitor", "dx_agent_dev")


@pytest.mark.parametrize("width", WIDTHS)
def test_no_toolbar_control_is_pushed_out_of_reach(width: int):
    server, port = start_module_server("dx_app")
    try:
        with sync_playwright() as p:
            browser = launch_browser(p, "chromium")
            ctx = browser.new_context(viewport={"width": width, "height": 768})
            page = ctx.new_page()
            page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
            page.wait_for_timeout(2500)
            unreachable = page.evaluate(_UNREACHABLE_JS)
            ctx.close()
            browser.close()
    finally:
        server.shutdown()
    assert not unreachable, (
        f"{width}px 에서 스크롤로도 닿을 수 없는 컨트롤: {unreachable}\n"
        "문서 가로 넘침은 0 이라 줌 감사는 이것을 보지 못한다 — "
        "조상의 overflow-x:hidden 이 잘라내기 때문이다."
    )


@pytest.mark.parametrize("module", MODULES)
def test_every_module_shell_survives_the_narrowest_width(module: str):
    """Checks only the narrowest width — passing there means wider widths pass too.

    Eight modules × three widths would mean 24 browser launches, which is slow. The test
    above covers the widths with dx_app; this one checks only **differences between modules**.
    """
    server, port = start_module_server(module)
    try:
        with sync_playwright() as p:
            browser = launch_browser(p, "chromium")
            ctx = browser.new_context(viewport={"width": min(WIDTHS), "height": 768})
            page = ctx.new_page()
            page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
            page.wait_for_timeout(2500)
            unreachable = page.evaluate(_UNREACHABLE_JS)
            ctx.close()
            browser.close()
    finally:
        server.shutdown()
    assert not unreachable, f"{module} @ {min(WIDTHS)}px: 닿을 수 없는 컨트롤 {unreachable}"


@pytest.mark.parametrize("width", (390, 360))
def test_the_launcher_top_bar_fits_a_phone(width: int):
    """On a phone width, the launcher top bar's theme, connected-browser and tutorial buttons must
    stay on screen and clickable."""
    server, port = start_module_server("launcher")
    try:
        with sync_playwright() as p:
            browser = launch_browser(p, "chromium")
            ctx = browser.new_context(viewport={"width": width, "height": 844})
            ctx.add_init_script("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
                                "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}")
            page = ctx.new_page()
            page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
            page.wait_for_timeout(2500)
            unreachable = page.evaluate(_UNREACHABLE_JS)
            ctx.close()
            browser.close()
    finally:
        server.shutdown()
    assert not unreachable, f"{width}px 에서 닿을 수 없는 launcher 컨트롤: {unreachable}"

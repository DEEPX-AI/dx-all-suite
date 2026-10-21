"""The stage really fits one screen, and turns into the Dock after input.

One screen is easy to lose as content is added, so it is measured. 1280×800 is the visual suite's
reference window.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_QUIET = """() => {
  const t = window._dxTutorial;
  if (t) { try { t.hideTOC && t.hideTOC(); t.stop && t.stop(); } catch (e) {} }
  document.querySelectorAll('.dxt-toc,.dxt-overlay,.dxt-tooltip,.dxt-toc-backdrop').forEach(e => e.remove());
}"""
_SEEN = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}")



@pytest.fixture(scope="module")
def server():
    srv, port = start_module_server("launcher")
    yield port
    srv.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _open(browser, port, w, h, lang="en"):
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    ctx.add_init_script(_SEEN + f"try{{localStorage.setItem('dx-lang','{lang}');}}catch(e){{}}")
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.wait_for_selector("#studioGrid .orbital-card", state="visible")
    page.evaluate(_QUIET)
    page.wait_for_timeout(300)
    return ctx, page


@pytest.mark.parametrize("w,h", [(1280, 800), (1440, 900)])
@pytest.mark.parametrize("lang", ["en", "es"])
def test_the_home_is_one_screen(browser, server, w, h, lang):
    ctx, page = _open(browser, server, w, h, lang)
    try:
        over = page.evaluate("() => document.documentElement.scrollHeight - innerHeight")
        assert over <= 0, f"{w}×{h} {lang}: {over}px 넘친다"
    finally:
        ctx.close()


def test_every_role_is_in_the_fold(browser, server):
    ctx, page = _open(browser, server, 1280, 800)
    try:
        bottoms = page.evaluate("""() => ['#homeAsk', '#studioGrid', '#homeDevice', '#homeMeasured', '#homeBar']
          .map(s => [s, document.querySelector(s).getBoundingClientRect().bottom])""")
        for sel, bottom in bottoms:
            assert bottom <= 800, (sel, bottom)
        assert page.locator("#studioGrid .orbital-card[data-app]").count() == 9
        assert page.locator("#studioGrid .about-book-card").count() == 2
    finally:
        ctx.close()




def _rows(page, cells="#studioGrid > *"):
    return page.evaluate("""(sel) => {
      const tops = [...document.querySelectorAll(sel)].map(e => Math.round(e.getBoundingClientRect().top));
      return [...new Set(tops)].length; }""", cells)


_MODULES = "#studioGrid > .orbital-card"


def test_the_modules_are_three_by_three_when_wide(browser, server):
    """Nine modules in three rows; the two books sit beside them, centred across the rows (not a row of their own)."""
    ctx, page = _open(browser, server, 1440, 900)
    try:
        assert _rows(page, _MODULES) == 3
    finally:
        ctx.close()


def test_the_grid_reflows_when_narrow(browser, server):
    ctx, page = _open(browser, server, 700, 900)
    try:
        assert _rows(page) >= 3
    finally:
        ctx.close()


def test_the_widgets_sit_either_side_of_the_grid_when_wide(browser, server):
    ctx, page = _open(browser, server, 1440, 900)
    try:
        dev, grid, meas = page.evaluate("""() => ['#homeDevice', '#studioGrid', '#homeMeasured']
          .map(s => document.querySelector(s).getBoundingClientRect()).map(r => [r.left, r.right])""")
        assert dev[1] <= grid[0] and grid[1] <= meas[0]
    finally:
        ctx.close()


_SHOW_ANSWER = "() => { document.getElementById('homeAnswer').hidden = false; }"


def _docked(browser, server):
    ctx, page = _open(browser, server, 1280, 800)
    page.evaluate(_SHOW_ANSWER)
    page.wait_for_timeout(100)
    r = page.evaluate("""() => Object.fromEntries(['#homeAnswer', '#studioGrid', '#homeDevice', '#homeMeasured']
      .map(s => [s, document.querySelector(s).getBoundingClientRect()]).map(([s, r]) => [s, [r.top, r.bottom]]))""")
    return ctx, page, r


def test_an_answer_docks_the_tools_below_it(browser, server):
    ctx, page, r = _docked(browser, server)
    try:
        assert r["#studioGrid"][0] >= r["#homeAnswer"][1], "아이콘이 답 아래로 내려가지 않았다"
        assert _rows(page) == 1, "Dock 은 한 줄이다"
        width = page.evaluate("() => document.getElementById('homeAskForm').getBoundingClientRect().width")
        assert width <= 760, f"Dock 에서 입력창이 {width}px 로 늘어났다"
    finally:
        ctx.close()


def test_docked_widgets_stay_above_the_answer_on_one_screen(browser, server):
    ctx, page, r = _docked(browser, server)
    try:
        assert r["#homeDevice"][1] <= r["#homeAnswer"][0], "위젯이 답 위에 남지 않았다"
        assert page.evaluate("() => document.documentElement.scrollHeight - innerHeight") <= 0
    finally:
        ctx.close()


def test_a_real_answer_scrolls_inside_its_row_instead_of_spilling(browser, server):
    """A real answer with a path card (227px) must stay inside its 123px cell and off the Dock icons. With
    .landing's align-items: center the grid item is centred rather than stretched and overflows above and below."""
    ctx, page = _open(browser, server, 1280, 800)
    try:
        page.fill("#homeAsk", "compile yolo26n to DXNN")
        page.press("#homeAsk", "Enter")
        page.wait_for_function("() => !document.getElementById('homeAnswer').hidden", timeout=5000)
        page.wait_for_timeout(200)
        r = page.evaluate("""() => Object.fromEntries(['#homeStageWork', '#studioGrid', '#homeDevice']
          .map(s => [s, document.querySelector(s).getBoundingClientRect()]).map(([s, r]) => [s, [r.top, r.bottom]]))""")
        assert r["#homeStageWork"][1] <= r["#studioGrid"][0] + 1, f"답이 Dock 을 덮는다: {r}"
        assert r["#homeStageWork"][0] >= r["#homeDevice"][1] - 1, f"답이 위젯을 덮는다: {r}"
        assert page.evaluate("() => document.documentElement.scrollHeight - innerHeight") <= 0
        # Even at 1280×800 the answer must fit through the path card: in the Dock the chips and poster that help you
        # start give up their space. Overflow scrolls inside the cell, but one route must fit.
        fit = page.evaluate("""() => { const w = document.getElementById('homeStageWork');
          return [w.scrollHeight, w.clientHeight]; }""")
        assert fit[0] <= fit[1] + 1, f"답이 칸 안에서 잘린다: {fit}"
        hidden = page.evaluate("""() => ['#homeAskChips', '#homeStage .stage-films']
          .map(s => getComputedStyle(document.querySelector(s)).display)""")
        assert hidden == ["none", "none"], hidden
    finally:
        ctx.close()


def test_escape_closes_the_answer_and_undocks(browser, server):
    ctx, page = _open(browser, server, 1280, 800)
    try:
        page.evaluate(_SHOW_ANSWER)
        page.keyboard.press("Escape")
        page.wait_for_timeout(100)
        assert page.evaluate("() => document.getElementById('homeAnswer').hidden")
        assert _rows(page, _MODULES) == 3 or page.viewport_size["width"] < 1200
    finally:
        ctx.close()


def test_the_close_button_closes_the_answer(browser, server):
    ctx, page = _open(browser, server, 1280, 800)
    try:
        page.evaluate(_SHOW_ANSWER)
        page.click("#answerClose")
        assert page.evaluate("() => document.getElementById('homeAnswer').hidden")
    finally:
        ctx.close()


def test_a_running_console_cannot_be_closed_by_accident(browser, server):
    ctx, page = _open(browser, server, 1280, 800)
    try:
        page.evaluate("""() => { const w = document.getElementById('homeWork');
          w.hidden = false; window.DXLauncher._homeWorkSetBusy(true); }""")
        # The ✕ visible from the start hides while running. It must show on a finished run restored by reconnect, so
        # the HTML does not start it hidden.
        assert page.locator("#workClose").is_hidden()
        page.keyboard.press("Escape")
        assert page.evaluate("() => !document.getElementById('homeWork').hidden"), "도는 중에 Esc 로 닫혔다"
        page.evaluate("() => window.DXLauncher._homeWorkSetBusy(false)")
        assert page.locator("#workClose").is_visible()
        page.keyboard.press("Escape")
        assert page.evaluate("() => document.getElementById('homeWork').hidden")
    finally:
        ctx.close()

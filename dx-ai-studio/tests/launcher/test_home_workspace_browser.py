"""Home's Build must be a place to start work, not a search box.

A block taking 217px of a 900px screen can still read as "one search box". This file protects two
things: that block is the largest thing on the first screen, and it takes several lines, not a one-line
question.

Module layout (5×2, collapsing when narrow) is checked by test_home_stage_browser.py.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_QUIET = """() => {
  const t = window._dxTutorial;
  if (t) { try { t.stop && t.stop(); } catch (e) {} }
  document.querySelectorAll('.dxt-toc,.dxt-overlay,.dxt-tooltip,.dxt-toc-backdrop')
    .forEach(e => e.remove());
}"""


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _open(browser, width=1512, height=900):
    server, port = start_module_server("launcher")
    ctx = browser.new_context(viewport={"width": width, "height": height})
    ctx.add_init_script(
        "try{sessionStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}"
    )
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
    page.wait_for_timeout(3500)
    page.evaluate(_QUIET)
    page.wait_for_timeout(400)
    return server, ctx, page


@pytest.fixture()
def home(browser):
    server, ctx, page = _open(browser)
    try:
        yield page
    finally:
        page.close(); ctx.close(); server.shutdown()


def _h(page, sel):
    return page.evaluate(
        "(s) => { const e = document.querySelector(s);"
        " return e ? Math.round(e.getBoundingClientRect().height) : 0; }", sel)


def test_the_build_block_is_the_largest_thing_on_the_first_screen(home):
    """The hero must be larger than the side widgets; the product's claim must not take less room than status."""
    build = _h(home, "#homeStage")
    for widget in ("#homeDevice", "#homeMeasured"):
        other = _h(home, widget)
        assert other > 0, f"{widget} 가 그려지지 않았다 — 비교가 공짜로 참이 된다"
        assert build > other, f"Build {build}px 가 {widget} {other}px 보다 작다"


def test_you_can_write_more_than_one_line(home):
    tag = home.evaluate(
        "() => { const e = document.getElementById('homeAsk');"
        " return e ? e.tagName.toLowerCase() : null; }")
    assert tag == "textarea", (
        f"입력이 <{tag}> 다 — 한 줄짜리 질문만 받는 자리로 읽힌다"
    )


def test_the_input_reads_at_least_as_large_as_the_subtitle(home):
    """On the stage the largest text is the 56px title, so what this contract keeps is that the input is not
    smaller than the subtitle."""
    ask = home.evaluate(
        "() => parseFloat(getComputedStyle(document.getElementById('homeAsk')).fontSize)")
    note = home.evaluate(
        "() => { const e = document.querySelector('#homeStage .stage-sub');"
        " return e ? parseFloat(getComputedStyle(e).fontSize) : 0; }")
    # Without a description this would compare against 0 and pass for free.
    assert note > 0, "hero 부제가 없다"
    assert ask >= note, f"입력 {ask}px 가 부제 {note}px 보다 작다"
    assert ask >= 21, f"입력 글자가 {ask}px — 작업 공간으로 읽히기에 작다"


def test_the_examples_belong_to_the_input_not_the_page(home):
    """Chips floating outside the input do not say what they are examples of."""
    inside = home.evaluate(
        """() => {
          const chips = document.getElementById('homeAskChips');
          const form = document.getElementById('homeAskForm');
          return !!(chips && form && form.contains(chips));
        }"""
    )
    assert inside, "예시 칩이 입력 덩어리 밖에 있다"

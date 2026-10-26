"""The hero looks and behaves as specified on screen."""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_SEEN = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}")
_QUIET = """() => {
  const t = window._dxTutorial;
  if (t) { try { t.hideTOC && t.hideTOC(); t.stop && t.stop(); } catch (e) {} }
  document.querySelectorAll('.dxt-toc,.dxt-overlay,.dxt-tooltip,.dxt-toc-backdrop').forEach(e => e.remove());
}"""


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


def _open(browser, port, lang="en"):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script(_SEEN + f"try{{localStorage.setItem('dx-lang','{lang}');}}catch(e){{}}")
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.wait_for_selector("#studioGrid .orbital-card", state="visible")
    page.evaluate(_QUIET)
    return ctx, page


def _px(page, sel, prop="fontSize"):
    return page.evaluate("([s, p]) => parseFloat(getComputedStyle(document.querySelector(s))[p])", [sel, prop])


def test_the_title_leads_at_56_and_the_subtitle_follows_at_21(browser, server):
    ctx, page = _open(browser, server)
    try:
        assert _px(page, "#homeStage .stage-title") == 56
        assert _px(page, "#homeStage .stage-title", "fontWeight") == 600
        assert _px(page, "#homeStage .stage-sub") == 21
    finally:
        ctx.close()


def test_a_chip_fills_the_english_prompt_and_waits(browser, server):
    """Even with a Korean UI the verified English original is filled in, and it runs only when the user presses."""
    ctx, page = _open(browser, server, "ko")
    try:
        page.click('#homeAskChips .ask-chip[data-prompt="mini-game-squat-fitness"]')
        value = page.input_value("#homeAsk")
        assert value.startswith("Build a squat-counting fitness mini-game using yolo26n-pose"), value
        assert page.evaluate("() => document.activeElement.id") == "homeAsk"
        page.wait_for_timeout(300)
        assert page.evaluate("() => document.getElementById('homeAnswer').hidden"), "chip 이 곧바로 실행했다"
    finally:
        ctx.close()


def test_more_shows_the_other_five(browser, server):
    ctx, page = _open(browser, server)
    try:
        visible = lambda: page.locator("#homeAskChips .ask-chip:visible").count()  # noqa: E731
        assert visible() == 4
        page.click("#homeAskMore")
        assert visible() == 9
        assert page.locator("#homeAskMore").is_hidden()
    finally:
        ctx.close()


def test_the_agent_line_and_build_sit_inside_the_input_box(browser, server):
    ctx, page = _open(browser, server)
    try:
        inside = page.evaluate("""() => { const box = document.querySelector('#homeAskForm .ask-box');
          return !!box && box.contains(document.getElementById('setupFold'))
            && box.contains(document.querySelector('#homeAskForm .ask-go'))
            && !box.contains(document.getElementById('homeAskChips')); }""")
        assert inside
    finally:
        ctx.close()


def test_korean_breaks_between_words_not_inside_them(browser, server):
    """The Korean subtitle must not break in the middle of a word: by default Korean wraps between any two characters."""
    ctx, page = _open(browser, server, "ko")
    try:
        rule = page.evaluate("() => ['.stage-sub', '.stage-title', '#homeAsk']"
                             ".map(s => getComputedStyle(document.querySelector(s)).wordBreak)")
        assert rule == ["keep-all"] * 3, rule
    finally:
        ctx.close()

"""ModelZoo catalog virtualization actually follows the scroll.

The source-level contract (`tests/test_modelzoo_virtualized_performance.py`) only greps
catalog.js for names like `renderViewport`, so it passes even when virtualization is dead.

The failure this catches: with the filter on All, only the first 40 of 347 cards render and
scrolling to the end adds none. That happens when the virtualizer assumes the scroller is "its
own container or window" while the overflow sits on an ancestor (`main.dx-shell-main`): neither
fires scroll events, so `_getEffectiveScrollTop()` stays 0.

So this test does **not find the scroller by name.** It scrolls the ancestor that actually
overflows in the DOM, so it keeps working if the shell changes.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

# Walk up from the container to the first ancestor that actually scrolls.
_FIND_SCROLLER = """() => {
  let node = document.getElementById('catalogContainer');
  while (node && node !== document.documentElement) {
    const st = getComputedStyle(node);
    if (/auto|scroll|overlay/.test(st.overflowY) && node.scrollHeight > node.clientHeight + 30) {
      return node.tagName.toLowerCase() + (node.className ? '.' + node.className.trim().split(/\\s+/).join('.') : '');
    }
    node = node.parentElement;
  }
  return null;
}"""

_CARD_IDS = """() => [...document.querySelectorAll('[data-model-id]')]
    .map(e => e.dataset.modelId).filter(Boolean)"""


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


@pytest.fixture()
def zoo(browser):
    server, port = start_module_server("dx_modelzoo")
    ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
        page.wait_for_selector("[data-model-id]", timeout=30000)
        page.wait_for_timeout(2500)
        yield page
    finally:
        page.close()
        ctx.close()
        server.shutdown()


def _scroller(page):
    sel = page.evaluate(_FIND_SCROLLER)
    assert sel, "카탈로그를 담은 스크롤 컨테이너를 못 찾았다"
    return sel


def _scroll_to(page, sel, ratio):
    page.evaluate(
        """([sel, r]) => { const e = document.querySelector(sel);
             e.scrollTop = (e.scrollHeight - e.clientHeight) * r; }""",
        [sel, ratio],
    )
    page.wait_for_timeout(700)


def _total_models(page):
    return page.evaluate(
        "async () => { const r = await fetch('/api/catalog'); const j = await r.json(); return (j.models||[]).length; }"
    )


def test_scrolling_moves_the_rendered_window(zoo):
    sel = _scroller(zoo)
    first_before = _CARD_IDS and zoo.evaluate(_CARD_IDS)[0]
    _scroll_to(zoo, sel, 0.5)
    first_after = zoo.evaluate(_CARD_IDS)[0]
    assert first_after != first_before, (
        f"절반까지 스크롤했는데 첫 카드가 그대로다 ({first_before!r}) — "
        "가상화가 스크롤을 못 보고 있다"
    )


def test_scrolling_to_the_end_shows_models_the_top_never_showed(zoo):
    """Scrolling to the end must show models not seen at the top.

    API order and render order are not assumed equal — the catalog sorts on its own, so a
    comparison with the 'first 40 from the API' would be trivially true. Only checks that the
    view actually moved.
    """
    sel = _scroller(zoo)
    _scroll_to(zoo, sel, 0.0)
    top_ids = set(zoo.evaluate(_CARD_IDS))
    assert top_ids, "맨 위에서 렌더된 카드가 없다"

    _scroll_to(zoo, sel, 1.0)
    end_ids = set(zoo.evaluate(_CARD_IDS))
    assert end_ids, "끝까지 내렸는데 렌더된 카드가 없다"
    assert end_ids - top_ids, (
        f"끝까지 내렸는데 맨 위와 같은 모델만 보인다 ({len(end_ids)}장) — 화면이 이동하지 않았다"
    )


def test_virtualization_still_windows(zoo):
    """Rendering everything is not a fix — drawing 347 cards at once makes the page slow."""
    sel = _scroller(zoo)
    total = _total_models(zoo)
    for ratio in (0.0, 0.3, 0.6, 1.0):
        _scroll_to(zoo, sel, ratio)
        n = zoo.evaluate("() => document.querySelectorAll('[data-model-id]').length")
        assert n < total / 2, f"ratio={ratio} 에서 {n}장 렌더 — 가상화가 사라졌다 (총 {total})"


def test_list_view_scrolls_too(zoo):
    zoo.evaluate("() => { if (typeof setViewMode === 'function') setViewMode('list'); }")
    zoo.wait_for_timeout(1500)
    sel = _scroller(zoo)
    first_before = zoo.evaluate(_CARD_IDS)[0]
    _scroll_to(zoo, sel, 0.5)
    first_after = zoo.evaluate(_CARD_IDS)[0]
    assert first_after != first_before, (
        f"리스트 뷰에서 첫 행이 그대로다 ({first_before!r})"
    )

"""The glass bar under the stage looks and behaves as specified.

External sites are pinned with routes: if the probe result depended on this PC's network, a check meant for
'unreachable' would end up checking 'reachable'.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_SEEN = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "localStorage.setItem('dx-tutorial-launcher-autostarted','1');"
         "localStorage.setItem('dx-tutorial-mode','off');}catch(e){}")
_QUIET = """() => {
  const t = window._dxTutorial;
  if (t) { try { t.hideTOC && t.hideTOC(); t.stop && t.stop(); } catch (e) {} }
  document.querySelectorAll('.dxt-toc,.dxt-overlay,.dxt-tooltip,.dxt-toc-backdrop').forEach(e => e.remove());
}"""
DEV = "https://developer.deepx.ai/"


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


def _open(browser, port, *, reachable=True, width=1440, height=900, lang="en"):
    ctx = browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
    ctx.add_init_script(_SEEN + f"try{{localStorage.setItem('dx-lang','{lang}');}}catch(e){{}}")
    probes = []

    def _dev(route, request):
        probes.append(request.method)
        if reachable:
            route.fulfill(status=200, body="")
        else:
            route.abort()

    ctx.route(DEV, _dev)
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.wait_for_selector("#studioGrid .orbital-card", state="visible")
    page.evaluate(_QUIET)
    return ctx, page, probes


def _offline(page):
    return page.evaluate("() => document.getElementById('homeBar').classList.contains('is-offline')")


_ROWS = """() => {
  const top = e => Math.round(e.getBoundingClientRect().top);
  const bar = document.getElementById('homeBar').getBoundingClientRect();
  const legal = document.querySelector('#homeBar .stage-legal').getBoundingClientRect();
  return {links: [...document.querySelectorAll('#homeBar .bar-title, #homeBar .deepx-link')].map(top),
          legal: Math.round(legal.top), legalGap: Math.round(bar.right - legal.right)};
}"""


@pytest.mark.parametrize("size", [(1440, 900), (1280, 800)])
@pytest.mark.parametrize("lang", ["en", "es", "ko", "ja", "zh-CN", "zh-TW"])
def test_the_links_are_one_line_and_the_legal_keeps_the_right_edge(browser, server, size, lang):
    ctx, page, _ = _open(browser, server, width=size[0], height=size[1], lang=lang)
    try:
        rows = page.evaluate(_ROWS)
        links = rows["links"]
        assert len(links) == 8, links
        assert max(links) - min(links) <= 12, f"링크가 두 줄로 접혔다: {links}"
        assert rows["legalGap"] <= 24, f"법적 고지가 오른쪽 끝을 떠났다: {rows}"
        # At 1280 and below the chat button's 64px slot is kept clear, so the legal notice wraps to a second row.
        if lang == "en" and size[0] == 1440:
            assert rows["legal"] - min(links) <= 12, f"en 은 1440 에서 한 줄이어야 한다: {rows}"
    finally:
        ctx.close()


@pytest.mark.parametrize("width", [1280, 1100])
def test_the_chat_button_does_not_cover_the_bar(browser, server, width):
    ctx, page, _ = _open(browser, server, width=width, height=800)
    try:
        gap = page.evaluate("""() => document.querySelector('.dx-chat-fab').getBoundingClientRect().left
          - document.getElementById('homeBar').getBoundingClientRect().right""")
        assert gap >= 0, f"챗 버튼이 막대를 {-gap}px 덮는다"
    finally:
        ctx.close()


def test_the_bar_is_glass(browser, server):
    ctx, page, _ = _open(browser, server)
    try:
        blur = page.evaluate("() => getComputedStyle(document.getElementById('homeBar')).backdropFilter")
        assert blur and blur != "none", blur
    finally:
        ctx.close()


def test_hover_shows_the_one_line_description(browser, server):
    ctx, page, _ = _open(browser, server)
    try:
        link = page.locator('#homeBar .deepx-link[href$="/sw-download/"]')
        desc = link.locator(".bar-desc")
        assert float(desc.evaluate("e => getComputedStyle(e).opacity")) == 0
        link.hover()
        page.wait_for_function("""() => getComputedStyle(document.querySelector(
          '#homeBar .deepx-link[href$="/sw-download/"] .bar-desc')).opacity === '1'""", timeout=3000)
        assert "DX-RT" in desc.inner_text()
    finally:
        ctx.close()


def test_no_probe_leaves_at_load(browser, server):
    ctx, page, probes = _open(browser, server)
    try:
        page.wait_for_timeout(500)
        assert probes == [], "로드 때 외부로 나갔다"
        page.hover("#homeBar .bar-title")
        page.wait_for_timeout(500)
        page.hover('#homeBar .deepx-link[href$="/tech-docs/"]')
        page.wait_for_timeout(300)
        assert probes == ["HEAD"], probes
        assert not _offline(page)
    finally:
        ctx.close()


def test_an_unreachable_site_turns_the_links_off_after_the_first_hover(browser, server):
    ctx, page, _ = _open(browser, server, reachable=False)
    try:
        assert not _offline(page)
        page.hover("#homeBar .bar-title")
        page.wait_for_function("() => document.getElementById('homeBar').classList.contains('is-offline')",
                               timeout=5000)
        assert page.is_visible("#homeBarOffline")
        assert page.inner_text("#homeBarOffline").strip() == "Offline"
        disabled = page.evaluate("""() => [...document.querySelectorAll('#homeBar a[href^="http"]')]
          .every(a => a.getAttribute('aria-disabled') === 'true')""")
        assert disabled
    finally:
        ctx.close()


def test_going_offline_disables_the_links_and_they_do_not_open(browser, server):
    ctx, page, _ = _open(browser, server)
    try:
        ctx.set_offline(True)
        page.wait_for_function("() => document.getElementById('homeBar').classList.contains('is-offline')",
                               timeout=5000)
        popups = []
        ctx.on("page", lambda p: popups.append(p))
        page.click('#homeBar .deepx-link[href$="/tech-docs/"]', force=True)
        page.wait_for_timeout(500)
        assert popups == [], "꺼진 링크가 새 탭을 열었다"
        ctx.set_offline(False)
        page.wait_for_function("() => !document.getElementById('homeBar').classList.contains('is-offline')",
                               timeout=5000)
        assert page.is_hidden("#homeBarOffline")
    finally:
        ctx.close()


def test_the_chat_offers_the_web_agent(browser, server):
    ctx, page, _ = _open(browser, server)
    try:
        page.click(".dx-chat-fab")
        link = page.locator('.dx-chat-window a[href="https://deepx.rapidflare.ai/"]')
        link.wait_for(state="visible", timeout=3000)
        assert link.get_attribute("target") == "_blank"
    finally:
        ctx.close()

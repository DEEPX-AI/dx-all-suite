"""A sentence typed on home must survive a trip to a module and back.

Home has two ways out:

* a module card: pushState inside the shell. The document stays, so the input stays.
* the answer panel's route / agent hand-off: `window.location.href` would leave the SPA, so coming
  back would be a new document.

Both must go through one in-shell path, and separately the typed sentence is kept as a draft.
Surviving a real reload (F5, or entering by a direct link) needs storage: losing a half-written
sentence is losing work.
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


@pytest.fixture()
def launcher(browser):
    server, port = start_module_server("launcher")
    ctx = browser.new_context(viewport={"width": 1512, "height": 900})
    ctx.add_init_script(
        "try{sessionStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}"
    )
    page = ctx.new_page()
    try:
        yield page, port
    finally:
        page.close(); ctx.close(); server.shutdown()


def _home(page, port):
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
    page.wait_for_timeout(3000)
    page.evaluate(_QUIET)
    page.wait_for_timeout(300)


def _ask(page):
    return page.evaluate(
        "() => { const e = document.getElementById('homeAsk'); return e ? e.value : null; }")


def test_the_sentence_survives_a_real_reload(launcher):
    """Same situation as leaving with a full navigation and coming back."""
    page, port = launcher
    _home(page, port)
    page.evaluate(
        """() => { const e = document.getElementById('homeAsk');
             e.value = 'make baseball game';
             e.dispatchEvent(new Event('input', { bubbles: true })); }""")
    page.wait_for_timeout(400)

    _home(page, port)          # new document
    assert _ask(page) == "make baseball game", (
        f"새로 열었더니 쓰던 문장이 사라졌다: {_ask(page)!r}"
    )


def test_sending_it_clears_the_draft(launcher):
    """A sent sentence showing up again is not a kept draft, it is a bug."""
    page, port = launcher
    _home(page, port)
    page.evaluate(
        """() => { const e = document.getElementById('homeAsk');
             e.value = 'pose estimation on webcam';
             e.dispatchEvent(new Event('input', { bubbles: true })); }""")
    page.wait_for_timeout(300)
    page.evaluate(
        "() => { if (window.DXLauncher && DXLauncher.homeAsk)"
        " DXLauncher.homeAsk('pose estimation on webcam'); }")
    page.wait_for_timeout(1500)

    _home(page, port)
    assert not _ask(page), f"보낸 뒤에도 초안이 남았다: {_ask(page)!r}"


def test_leaving_home_keeps_the_shell(launcher):
    """Leaving from the answer panel must also stay inside the shell, the same as a module card."""
    src = (__import__("pathlib").Path(__file__).resolve().parents[2]
           / "launcher" / "static" / "home-answer.js").read_text(encoding="utf-8")
    assert "_leaveHome" in src, "나가는 길이 한 곳으로 모이지 않았다"
    # Any remaining direct location.href exit would leak out that way.
    body = src[src.index("function _leaveHome"):]
    body = body[: body.index("\n  }")]
    # Checking only that loadAppIframeIfNeeded or pushState appears is not enough: a call that passes a string
    # as the iframe throws, and its catch falls back to location.href.
    assert "ns2.launch(" in body, "모듈 카드와 같은 launch 로 나가지 않는다"
    assert "loadAppIframeIfNeeded" not in body

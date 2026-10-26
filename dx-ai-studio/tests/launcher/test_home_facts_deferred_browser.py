"""Home's module numbers are fetched when home shows, not on every screen.

The launcher shell keeps home in the document on every route. Fetching the module facts (/zoo/api/catalog, 2.5 MB)
at boot would cost that even when the user opens /app/ or /compiler/ and never sees home, and Model Zoo would pay for
the catalog twice. The facts load the first time home becomes visible.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_SEEN = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "localStorage.setItem('dx-tutorial-launcher-autostarted','1');"
         "localStorage.setItem('dx-tutorial-mode','off');sessionStorage.setItem('dx-home-entered','1');}catch(e){}")
_CATALOG = '{"ok": true, "models": [{"name": "a", "display": {"task": "object_detection"}}]}'


@pytest.fixture(scope="module")
def port():
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


def _open(browser, port, path):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(_SEEN)
    asked = []
    ctx.route("**/zoo/api/catalog", lambda r: (asked.append(r.request.url),
                                               r.fulfill(status=200, content_type="application/json", body=_CATALOG)))
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}{path}", wait_until="load")
    return ctx, page, asked


def test_a_module_route_does_not_fetch_home_numbers(browser, port):
    ctx, page, asked = _open(browser, port, "/compiler/")
    try:
        page.wait_for_function("!!(window.DXLauncher && window.DXLauncher.goHome)", timeout=30000)
        page.wait_for_timeout(2500)
        assert not page.evaluate("document.body.classList.contains('home-visible')")
        assert asked == []
        page.evaluate("DXLauncher.goHome()")
        page.wait_for_function("document.body.classList.contains('home-visible')", timeout=15000)
        page.wait_for_function("document.querySelector('.orbital-card[data-app=\"zoo\"] .card-desc')"
                               ".textContent.includes('1')", timeout=15000)
        assert len(asked) == 1
    finally:
        ctx.close()


def test_home_fetches_its_numbers_once(browser, port):
    ctx, page, asked = _open(browser, port, "/")
    try:
        page.wait_for_function("document.querySelector('.orbital-card[data-app=\"zoo\"] .card-desc')"
                               ".textContent.includes('1')", timeout=30000)
        page.wait_for_timeout(500)
        assert len(asked) == 1
    finally:
        ctx.close()


def test_mermaid_loads_only_when_a_doc_has_a_diagram(browser, port):
    """mermaid.min.js (800 KB) was a <script> on every launcher screen; only SDK Library docs draw diagrams."""
    ctx, page, _ = _open(browser, port, "/")
    libs = []
    page.on("request", lambda r: libs.append(r.url) if "mermaid.min.js" in r.url else None)
    try:
        page.wait_for_function("!!(window.SDKLibrary && window.SDKLibrary._renderMermaid)", timeout=30000)
        page.wait_for_timeout(1500)
        assert libs == [] and page.evaluate("typeof window.mermaid") == "undefined"
        page.evaluate("""() => { const d = document.createElement('div'); d.id = 'mm-probe';
          d.innerHTML = '<pre class="mermaid-source"><code>graph TD; A-->B</code></pre>';
          document.body.appendChild(d); SDKLibrary._renderMermaid(d); }""")
        page.wait_for_selector("#mm-probe svg", state="attached", timeout=20000)
        assert len(libs) == 1
    finally:
        ctx.close()

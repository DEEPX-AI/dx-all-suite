"""Clicking Save as HTML in Korean downloads the new card in Korean, under the server's file name; the button
is disabled while the request runs, and a failed label fetch shows an error instead of an English card."""
import json

import pytest

pytest.importorskip("playwright.sync_api")

from shared.chromium import resolve_chromium_executable  # noqa: E402
from shared.paths import DX_APP_ROOT  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402

pytestmark = pytest.mark.skipif(not (DX_APP_ROOT / "config" / "model_registry.json").is_file(),
                                reason="needs the dx_app checkout")

BUTTON = 'button[onclick^="exportModelCardHtml"]'
# Records the button's disabled state at each fetch the export makes.
WATCH_FETCH = """() => {
  window.__cardFetches = [];
  const orig = window.fetch;
  window.fetch = function (url, opts) {
    if (String(url).includes('/api/model_card/')) {
      window.__cardFetches.push({ url: String(url), method: (opts && opts.method) || 'GET',
                                  disabled: document.querySelector('%s').disabled });
    }
    return orig.apply(this, arguments);
  };
}""" % BUTTON


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_modelzoo")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
    try:
        yield br, port
    finally:
        br.close()
        pw.stop()
        srv.shutdown()
        srv.server_close()


def _open(browser, port):
    ctx = browser.new_context(accept_downloads=True)
    ctx.add_init_script("localStorage.setItem('dx-lang','ko');localStorage.setItem('dx-tutorial-mode','off');")
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/#model=yolo26n", wait_until="load")
    button = page.locator(BUTTON)
    button.wait_for(timeout=20000)
    page.evaluate(WATCH_FETCH)
    return ctx, page, button


def test_save_as_html_in_korean(browser, tmp_path):
    br, port = browser
    ctx, page, button = _open(br, port)
    try:
        with page.expect_response(lambda r: r.request.method == "POST" and "/api/model_card/yolo26n" in r.url) as resp:
            with page.expect_download(timeout=30000) as info:
                button.click()
        disposition = resp.value.headers.get("content-disposition", "")
        assert info.value.suggested_filename and f'filename="{info.value.suggested_filename}"' in disposition
        path = tmp_path / "card.html"
        info.value.save_as(path)
        html = path.read_text(encoding="utf-8")
        assert '<html lang="ko">' in html and "빠른 시작" in html and "data:image/webp;base64," in html
        # The task label comes from the page's Korean category name, not the English one.
        assert "Object Detection" not in html
        fetches = page.evaluate("window.__cardFetches")
        assert [f["method"] for f in fetches] == ["GET", "POST"] and all(f["disabled"] for f in fetches), fetches
        page.wait_for_function(f"!document.querySelector('{BUTTON}').disabled", timeout=5000)
    finally:
        ctx.close()


def test_failed_label_fetch_sends_no_card_and_the_button_recovers(browser):
    br, port = browser
    ctx, page, button = _open(br, port)
    try:
        original = button.inner_html()
        current = f"document.querySelector('{BUTTON}').innerHTML"
        page.route("**/api/model_card/labels", lambda route: route.fulfill(status=500, body="{}"))
        button.click()
        page.wait_for_function(f"{current} !== {json.dumps(original)}", timeout=5000)
        page.wait_for_function(f"!document.querySelector('{BUTTON}').disabled", timeout=5000)
        button.click()                                    # a second click while the error text shows
        page.wait_for_function(f"{current} === {json.dumps(original)}", timeout=8000)
        page.wait_for_timeout(3000)                       # the second click's restore must not bring the error back
        assert button.inner_html() == original
        assert [f["method"] for f in page.evaluate("window.__cardFetches")] == ["GET", "GET"]
    finally:
        ctx.close()

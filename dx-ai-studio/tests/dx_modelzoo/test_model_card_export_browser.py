"""Clicking Save as HTML in Korean downloads the new card in Korean."""
import pytest

pytest.importorskip("playwright.sync_api")

from shared.chromium import resolve_chromium_executable  # noqa: E402
from shared.paths import DX_APP_ROOT  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402

pytestmark = pytest.mark.skipif(not (DX_APP_ROOT / "config" / "model_registry.json").is_file(),
                                reason="needs the dx_app checkout")


def test_save_as_html_in_korean(tmp_path):
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_modelzoo")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
    try:
        ctx = br.new_context(accept_downloads=True)
        ctx.add_init_script("localStorage.setItem('dx-lang','ko');localStorage.setItem('dx-tutorial-mode','off');")
        page = ctx.new_page()
        page.goto(f"http://127.0.0.1:{port}/#model=yolo26n", wait_until="load")
        button = page.locator("[data-detail-action-bar] button", has_text="HTML")
        button.wait_for(timeout=20000)
        with page.expect_download(timeout=30000) as info:
            button.click()
        path = tmp_path / "card.html"
        info.value.save_as(path)
        html = path.read_text(encoding="utf-8")
        assert '<html lang="ko">' in html and "빠른 시작" in html and "data:image/webp;base64," in html
        # The task label comes from the page's Korean category name, not the English one.
        assert "Object Detection" not in html
    finally:
        br.close()
        pw.stop()
        srv.shutdown()
        srv.server_close()

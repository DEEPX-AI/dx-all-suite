"""Model Zoo: an already-downloaded model without a Studio record is not "not downloaded".

It shows as downloaded-but-unverified with a cart checkbox; downloading it again verifies the
file by size (shared/atomic_download.download_file) and keeps a matching file in place.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


def _tier(state):
    return {"accuracy": "", "dxnn_url": f"https://example/{state}.dxnn", "json_url": None,
            "exists": state != "missing", "install_state": state}


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def test_unverified_download_is_marked_and_can_be_verified_but_verified_is_plain(page):
    models = [{"name": state, "task": "Object Detection", "qlite": _tier(state)}
              for state in ("verified", "unverified", "missing")]
    page.evaluate("""(models) => { nav('modelzoo'); MZ.loading = false; MZ.models = models;
                    MZ.cart = {}; mzRenderTable(); }""", models)
    rows = {state: page.locator("#mz-tbody tr").nth(i) for i, state in enumerate(("verified", "unverified", "missing"))}
    assert rows["verified"].locator(".mz-col-ql .badge.b-ok").count() == 1
    assert rows["verified"].locator(".mz-col-ql .mz-chk-wrap").count() == 0
    unverified = rows["unverified"]
    assert unverified.locator(".mz-unverified").count() == 1
    assert "Unverified" in unverified.locator(".mz-unverified").get_attribute("title")
    assert unverified.locator(".mz-col-ql .mz-chk-wrap").count() == 1, "verify = select and download again"
    assert rows["missing"].locator(".mz-col-ql .mz-unverified, .mz-col-ql .badge.b-ok").count() == 0
    assert rows["missing"].locator(".mz-col-ql .mz-chk-wrap").count() == 1
    page.evaluate("mzToggleCart('unverified')")
    assert page.evaluate("MZ.cart['unverified'].qlite") is True

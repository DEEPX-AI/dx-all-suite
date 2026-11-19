"""Model Zoo detail → Specification → "Supported hardware", on screen.

DX-M1 and DX-H1 Quattro always (Quattro = 4 × M1). DX-M1M per model from dx-modelzoo YAML `target_hardware`
(next release): until then the row says it is not confirmed yet (no date promised); once present it is listed, or
"Not supported on DX-M1M (reason)".
The real catalog answer is used and only `processor` is swapped, so the page is the real one."""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from shared.chromium import resolve_chromium_executable  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402

MODEL = "alexnet"
PENDING = None
SUPPORTED = {"supported_devices": ["dx_m1", "dx_m1m", "dx_h1_quattro"], "status": "provided",
             "m1m": {"status": "supported", "reason": None}}
UNSUPPORTED = {"supported_devices": ["dx_m1", "dx_h1_quattro"], "status": "provided",
               "m1m": {"status": "unsupported", "reason": "NPU memory"}}


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


def _row(browser, processor=PENDING, lang="en"):
    br, port = browser
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script(f"localStorage.setItem('dx-lang','{lang}');localStorage.setItem('dx-tutorial-mode','off');")
    page = ctx.new_page()

    def catalog(route, *_):
        resp = route.fetch()
        data = resp.json()
        if processor is not None:
            data["model"]["processor"] = processor
        route.fulfill(response=resp, json=data)

    page.route(f"**/api/catalog/{MODEL}", catalog)
    page.goto(f"http://127.0.0.1:{port}/#model={MODEL}", wait_until="load")
    row = page.locator(".mz-spec-table tr").filter(has=page.locator(".mz-hw-list"))
    row.wait_for(timeout=20000)
    text = row.inner_text()
    ctx.close()
    return text


def test_today_m1_and_quattro_with_the_m1m_notice(browser):
    """No processor swap: the real served catalog (committed generated catalog, no YAML field yet)."""
    text = _row(browser)
    assert "Supported hardware" in text
    assert "DX-M1 · DX-H1 Quattro" in text
    assert "DX-M1M: support for this model is not confirmed yet." in text


def test_m1m_listed_when_the_yaml_says_so(browser):
    text = _row(browser, SUPPORTED)
    assert "DX-M1 · DX-M1M · DX-H1 Quattro" in text
    assert "not confirmed yet" not in text and "Not supported" not in text


def test_unsupported_shows_the_reason(browser):
    text = _row(browser, UNSUPPORTED)
    assert "DX-M1 · DX-H1 Quattro" in text
    assert "Not supported on DX-M1M (NPU memory)" in text


@pytest.mark.parametrize("lang,label,notice", [
    ("ko", "지원 하드웨어", "DX-M1M: 이 모델의 지원 여부는 아직 확인되지 않았습니다."),
    ("ja", "対応ハードウェア", "DX-M1M: このモデルの対応可否はまだ確認されていません。"),
])
def test_row_speaks_the_page_language(browser, lang, label, notice):
    text = _row(browser, lang=lang)
    assert label in text and notice in text
    assert "Supported hardware" not in text and "not confirmed yet" not in text

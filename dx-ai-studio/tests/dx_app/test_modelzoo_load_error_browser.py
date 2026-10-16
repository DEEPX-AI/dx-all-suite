"""DX App model store: when the Public list cannot be loaded, the toast speaks the user's language.

The toast showed the server's developer message as is — "ModelZoo payload unreadable: window.__MODEL_ZOO_DATA__
…" with a Korean tail whatever the UI language (DETAIL below), or a raw "<urlopen error …>". The toast now says, in the UI
language, that the public model list could not be loaded and what to do; the technical detail goes to the console
only. /api/modelzoo/list is a fixture with the server's real error.
"""
from __future__ import annotations

import json
import re

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

DETAIL = ("ModelZoo payload unreadable: window.__MODEL_ZOO_DATA__ 을 찾을 수 없다 — 페이지 구조가 또 바뀌었거나 "
          "응답이 우리가 기대한 문서가 아니다. 부분 카탈로그를 만들지 않는다.")

# A word of the message in each language, and that it points at the network and at Internal.
EXPECT = {
    "en": ("public model list", "network", "Internal"),
    "ko": ("공개 모델 목록", "네트워크", "Internal"),
    "ja": ("公開モデル一覧", "ネットワーク", "Internal"),
    "es": ("lista pública de modelos", "red", "Internal"),
    "zh-CN": ("公开模型列表", "网络", "Internal"),
    "zh-TW": ("公開模型清單", "網路", "Internal"),
}
HANGUL = re.compile(r"[가-힣]")
CONSOLE: list[str] = []


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');")
    pg = ctx.new_page()
    pg.on("console", lambda m: CONSOLE.append(m.text))

    def _list(route, *_):
        if "source=public" in route.request.url:
            body = {"ok": False, "error": DETAIL, "models": []}
        else:
            body = {"ok": False, "error": "<urlopen error [Errno -2] Name or service not known>", "models": []}
        route.fulfill(status=200, content_type="application/json", body=json.dumps(body))

    pg.route("**/api/modelzoo/list*", _list)
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _load(page, source="public"):
    """Load the list again and return the text of the error toast it raises."""
    page.evaluate("() => document.querySelectorAll('#toast-wrap .toast').forEach(t => t.remove())")
    page.evaluate("s => { const sel = document.getElementById('mz-source'); sel.value = s; }", source)
    page.evaluate("() => { MZ.source = document.getElementById('mz-source').value; MZ.models = []; nav('modelzoo'); }")
    page.wait_for_selector("#toast-wrap .toast-err .toast-msg", timeout=10000)
    return page.inner_text("#toast-wrap .toast-err .toast-msg")


@pytest.mark.parametrize("lang", list(EXPECT))
def test_a_public_load_failure_says_what_to_do_in_the_ui_language(page, lang):
    page.evaluate("l => DXI18n.setLang(l)", lang)
    try:
        msg = _load(page)
        for word in EXPECT[lang]:
            assert word in msg, (lang, msg)
        for raw in ("__MODEL_ZOO_DATA__", "unreadable", "payload", "urlopen"):
            assert raw not in msg, (lang, msg)
        if lang != "ko":
            assert not HANGUL.search(msg), (lang, msg)
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_the_technical_detail_goes_to_the_console(page):
    CONSOLE.clear()
    _load(page)
    assert any("__MODEL_ZOO_DATA__" in m for m in CONSOLE), CONSOLE


def test_an_internal_load_failure_does_not_show_the_raw_error_either(page):
    msg = _load(page, "internal")
    assert "urlopen" not in msg and "Errno" not in msg, msg
    assert msg.strip()

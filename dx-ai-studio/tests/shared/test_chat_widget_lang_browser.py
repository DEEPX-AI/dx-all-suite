"""Shared chat widget: every label and button name follows the chosen language.

'API Key', 'Model', 'Endpoint', 'Custom endpoint', Send and Chat must not be fixed in English, and the rest must not
stay in the language the widget was first drawn in (placeholders, titles and aria-labels all follow a language switch).
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


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
    pg.wait_for_selector(".dx-chat-fab", timeout=10000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _snapshot(page):
    return page.evaluate("""() => {
      const w = document.querySelector('.dx-chat-window');
      const spans = [...w.querySelectorAll('.dx-chat-settings-field > span')].map(s => s.textContent.trim());
      return {
        fab: document.querySelector('.dx-chat-fab').getAttribute('aria-label'),
        send: w.querySelector('.dx-chat-send-btn').getAttribute('aria-label'),
        settingsAria: w.querySelector('[data-action=settings]').getAttribute('aria-label'),
        fields: spans,
        custom: w.querySelector('.dx-chat-settings-provider option[value=custom]').textContent,
        input: w.querySelector('.dx-chat-input').placeholder,
        save: w.querySelector('.dx-chat-settings-save').textContent,
        legend: w.querySelector('.dx-chat-settings-kind legend').textContent,
        web: w.querySelector('.dx-chat-header-link').getAttribute('aria-label'),
      };
    }""")


def test_the_widget_speaks_english_first(page):
    s = _snapshot(page)
    assert s["fab"] == "Chat" and s["send"] == "Send"
    # settings ask one question first; the Agent field leads
    assert s["fields"][:5] == ["Agent", "Provider", "API Key", "Model", "Endpoint"]
    assert s["custom"] == "Custom endpoint" and s["save"] == "Save"


def test_every_label_follows_a_language_change(page):
    page.evaluate("() => DXI18n.setLang('ja')")
    try:
        s = _snapshot(page)
        assert s["fab"] == "チャット" and s["send"] == "送信"
        assert s["settingsAria"] == "AI設定"
        assert s["fields"][:5] == ["エージェント", "プロバイダー", "API キー", "モデル", "エンドポイント"]
        assert s["fields"][5].startswith("温度")
        assert s["legend"] == "どの AI で回答しますか?"
        assert s["custom"] == "カスタムエンドポイント"
        assert s["input"] == "質問を入力..."
        assert s["save"] == "保存"
        assert s["web"] == "Web で DEEPX Agent を開く"
    finally:
        page.evaluate("() => DXI18n.setLang('en')")
    assert _snapshot(page)["fields"][2] == "API Key", "다시 영어로"


def test_the_page_translator_leaves_the_widgets_own_labels_alone(page):
    """The widget translates its labels itself (data-chat-t). DX App's page translator also walks every `option`
    and every select option; a label not in the page dictionary went back to English when it ran after the
    widget (on a slower board, after every language change)."""
    page.evaluate("() => DXI18n.setLang('ja')")
    try:
        page.evaluate("() => { DXI18n.applyLang(); if (typeof _i18nOptions === 'function') _i18nOptions(); }")
        assert _snapshot(page)["custom"] == "カスタムエンドポイント"
    finally:
        page.evaluate("() => DXI18n.setLang('en')")

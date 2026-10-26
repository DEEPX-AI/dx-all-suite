"""DX App Reference: every topic opens in all six languages and states facts that match the screen.

The facts (settings cards, APIs, RTSP input, defaults) are checked against the code, and Spanish must be present.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

LANGS = ["en", "ko", "ja", "zh-CN", "zh-TW", "es"]


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');")
    pg = ctx.new_page()
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.evaluate("() => nav('reference')")
    pg.wait_for_selector("#ref-content .ref-topic-card", timeout=10000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _open_all(page):
    """Open every topic and collect the text of every tab."""
    return page.evaluate("""() => {
      const out = [];
      const ids = [...document.querySelectorAll('.ref-topic-card')].map(c => c.dataset.refId);
      for (const id of ids) {
        const card = document.querySelector('.ref-topic-card[data-ref-id="' + id + '"]');
        if (card.classList.contains('active')) card.click();
        card.click();
        const panel = document.getElementById('ref-expand');
        out.push([id, panel ? panel.textContent : '']);
      }
      return out;
    }""")


@pytest.mark.parametrize("lang", LANGS)
def test_every_topic_opens_in_every_language(page, lang):
    page.evaluate(f"() => DXI18n.setLang('{lang}')")
    try:
        topics = _open_all(page)
        assert len(topics) == 16, [t[0] for t in topics]
        empty = [i for i, text in topics if len(text.strip()) < 40]
        assert not empty, f"{lang}: empty topics {empty}"
        assert not page.errors, page.errors
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_spanish_is_spanish(page):
    page.evaluate("() => DXI18n.setLang('es')")
    try:
        text = "\n".join(t for _, t in _open_all(page))
        assert "Configurar el resto" in text and "Descripción general" in text
        assert "Six steps get" not in text and "Click a model card" not in text
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_the_facts_match_the_screens(page):
    text = "\n".join(t for _, t in _open_all(page))
    for gone in ("/api/inference/single", "/api/npu/status", "/api/system", "Username", "Five cards", "KO / EN"):
        assert gone not in text, gone
    for fact in ("6. Sample Assets Setup", "/api/run_async", "stream1 – stream16", "Q-Master", "0.25", "Set up the rest"):
        assert fact in text, fact

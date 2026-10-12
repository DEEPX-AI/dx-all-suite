"""DX Stream Reference — 15 topics open in six languages and state facts that match the screen.

Step counts, demo / preset / model / element counts, the default playback mode, shortcuts and API paths must match
what the app actually has.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

LANGS = ["en", "ko", "ja", "zh-CN", "zh-TW", "es"]


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_stream")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');")
    pg = ctx.new_page()
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.evaluate("() => DXStream.nav('reference')")
    pg.wait_for_selector("#ref-content .ref-topic-card", timeout=10000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _open_all(page):
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
        assert len(topics) == 15, [t[0] for t in topics]
        assert not [i for i, text in topics if len(text.strip()) < 40]
        assert not page.errors, page.errors
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_spanish_is_spanish(page):
    page.evaluate("() => DXI18n.setLang('es')")
    try:
        text = "\n".join(t for _, t in _open_all(page))
        assert "Orden recomendado" in text and "Reglas de conexión" in text
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_the_facts_match_the_screens(page):
    text = "\n".join(t for _, t in _open_all(page))
    for gone in ("Ctrl+K", "Backspace", "/api/stream/webrtc/offer", "/api/demo/run", "7-step", "Languages (5)"):
        assert gone not in text, gone
    for fact in ("Local (WebRTC)", "Depth Estimation", "/api/demos/:id/start", "/api/webrtc/offer", "29 GStreamer elements"):
        assert fact in text, fact

"""Shared chat widget runtime language refresh contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_chat_widget_header_refresh_on_lang_change():
    src = (ROOT / "shared/chat/static/chat-widget.js").read_text(encoding="utf-8")
    assert "DXI18n.onLangChange" in src
    assert "_headerTitle" in src
    assert "titleEl.textContent" in src

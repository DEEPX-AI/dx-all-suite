"""DX Stream runtime language refresh contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_stream_lang_refresh_orchestrator_exists():
    src = (ROOT / "dx_stream/static/js/stream-lang-refresh.js").read_text(encoding="utf-8")
    assert "registerStreamLangRefresher" in src
    assert "DXI18n.onLangChange" in src
    assert "refreshStreamModuleLanguage" in src


def test_stream_setup_registers_refresher():
    src = (ROOT / "dx_stream/static/js/stream-setup.js").read_text(encoding="utf-8")
    assert "registerStreamLangRefresher" in src

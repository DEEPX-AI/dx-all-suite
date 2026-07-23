"""DX App runtime language refresh contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_lang_refresh_orchestrator_registers_on_lang_change():
    src = (ROOT / "dx_app/static/js/lang-refresh.js").read_text(encoding="utf-8")
    assert "registerLangRefresher" in src
    assert "refreshDxAppModuleLanguage" in src
    assert "DXI18n.onLangChange" in src


def test_i18n_callbacks_not_duplicating_page_refresh():
    src = (ROOT / "dx_app/static/js/i18n.js").read_text(encoding="utf-8")
    assert "window._DX_I18N_CALLBACKS = [];" in src


def test_inference_registers_lang_refresher():
    src = (ROOT / "dx_app/static/js/inference.js").read_text(encoding="utf-8")
    assert "registerLangRefresher" in src

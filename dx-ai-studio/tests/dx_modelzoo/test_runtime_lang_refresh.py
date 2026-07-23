"""DX Model Zoo runtime language refresh contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_modelzoo_lang_registry_and_hook():
    src = (ROOT / "dx_modelzoo/static/js/i18n.js").read_text(encoding="utf-8")
    assert "registerModelZooLangRefresher" in src
    assert "DXI18n.onLangChange" in src
    assert "refreshModelZooLanguage" in src


def test_catalog_registers_refresher():
    src = (ROOT / "dx_modelzoo/static/js/catalog.js").read_text(encoding="utf-8")
    assert "registerModelZooLangRefresher" in src

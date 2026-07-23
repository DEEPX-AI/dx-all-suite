"""DX Compiler runtime language refresh contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_compiler_lang_refresher_registry():
    src = (ROOT / "dx_compiler/static/js/compiler-i18n.js").read_text(encoding="utf-8")
    assert "registerCompilerLangRefresher" in src
    assert "__compilerLangRefreshers" in src


def test_config_wizard_registers_refresher():
    src = (ROOT / "dx_compiler/static/js/config_wizard.js").read_text(encoding="utf-8")
    assert "registerCompilerLangRefresher" in src

"""Shared lang-refresh helper contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_lang_refresh_helper_exists():
    src = (ROOT / "shared/static/lang-refresh.js").read_text(encoding="utf-8")
    assert "window.LangRefresh" in src
    assert "relocalizeSelectOptions" in src
    assert "snapshotSelect" in src


def test_i18n_core_dispatches_dx_lang_applied():
    src = (ROOT / "shared/static/i18n.js").read_text(encoding="utf-8")
    assert "dx-lang-applied" in src
    assert "CustomEvent" in src

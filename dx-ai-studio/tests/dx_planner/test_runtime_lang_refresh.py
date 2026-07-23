"""DX Planner and DX Sandbox runtime language refresh contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_planner_lang_refresher_registry():
    src = (ROOT / "dx_planner/static/js/i18n.js").read_text(encoding="utf-8")
    assert "registerPlannerLangRefresher" in src
    assert "refreshPlannerLanguage" in src


def test_planner_explorer_registers_refresher():
    src = (ROOT / "dx_planner/static/js/explorer.js").read_text(encoding="utf-8")
    assert "registerPlannerLangRefresher" in src
    assert "_lastOpen" in src
    assert "ExplorerView.open(snapshot.platformId" in src


def test_edgeguide_methodology_yellow_glow_css():
    css = (ROOT / "dx_planner/static/css/style.css").read_text(encoding="utf-8")
    assert "methodology-glow" in css
    assert "250, 204, 21" in css
    assert "prefers-reduced-motion" in css



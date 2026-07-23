"""Runtime lang-hook inventory gate tests."""

from pathlib import Path

from tools.i18n_audit.runtime_refresh import (
    check_runtime_gaps_gate,
    classify_runtime_gaps,
    extract_runtime_inventory,
)

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_inventory_has_no_missing_lang_hooks():
    records = extract_runtime_inventory(ROOT)
    findings = classify_runtime_gaps(records)
    msg = check_runtime_gaps_gate(findings)
    assert msg is None, msg


def test_launcher_has_refresh_launcher_chrome():
    src = (ROOT / "launcher/static/launcher-app-frame.js").read_text(encoding="utf-8")
    assert "function refreshLauncherChrome" in src
    assert "DXI18n.onLangChange" in src


def test_agent_dev_applylang_relocalizes_models():
    src = (ROOT / "dx_agent_dev/static/js/console.js").read_text(encoding="utf-8")
    assert "function applyLang" in src
    assert "fillModels(agent)" in src
    assert "relocalizeOpenTurns" in src

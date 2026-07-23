"""Contracts verifying Task 7 AI-frontend removal for DX Compiler."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2] / "dx_compiler"


def test_no_autopilot_or_suggest_dom():
    h = (ROOT / "templates" / "index.html").read_text()
    for m in ("autopilot-fieldset", "ai-context-btn", "ai-suggest-panel", "CompilerAiAssist"):
        assert m not in h, m


def test_suggest_fix_js_deleted():
    assert not (ROOT / "static" / "js" / "suggest_fix.js").exists()


def test_config_patch_route_removed():
    s = (ROOT / "server.py").read_text()
    assert "/config/patch" not in s and "_config_patch" not in s


def test_tutorial_no_dangling_ai_targets():
    t = (ROOT / "static" / "js" / "tutorial.js").read_text()
    for tid in ("help-autopilot", "help-ai-suggest-panel", "help-ai-log", "help-ai-hint"):
        assert tid not in t

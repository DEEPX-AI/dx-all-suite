"""Static spotlight / overlay contracts for shared tutorial engine."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "shared" / "static" / "tutorial-engine.js"


def test_tutorial_engine_exposes_spotlight_overlay_dom():
    src = ENGINE.read_text(encoding="utf-8")
    assert "dxt-overlay" in src
    assert "dxt-spotlight" in src
    assert "_highlightElement" in src
    assert "_refreshHighlight" in src


def test_tutorial_engine_polls_for_targets():
    src = ENGINE.read_text(encoding="utf-8")
    assert re.search(r"for\s*\(\s*var\s+_pw\s*=\s*0;\s*_pw\s*<\s*20", src)


def test_tutorial_engine_iframe_target_fallback():
    src = ENGINE.read_text(encoding="utf-8")
    assert "_queryTarget" in src
    assert "appIframePool" in src

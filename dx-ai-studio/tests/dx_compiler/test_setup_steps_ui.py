"""The dx_compiler Setup panel uses the compact form of the shared step list (DXSteps).

A two-step list that collapses to one line ("Setup ready · SDK v… · N samples") once both steps are done, so it
does not push the compile form down. Without the SDK, Compile is locked and the reason is shown beside the button.
Only setup_panel.js decides the lock.
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPILER = ROOT / "dx_compiler"
PANEL = (COMPILER / "templates" / "partials" / "setup_panel.html").read_text(encoding="utf-8")
JS = (COMPILER / "static" / "js" / "setup_panel.js").read_text(encoding="utf-8")
INDEX = (COMPILER / "templates" / "index.html").read_text(encoding="utf-8")
BASE = (COMPILER / "templates" / "base.html").read_text(encoding="utf-8")
TUTORIAL = (COMPILER / "static" / "js" / "tutorial.js").read_text(encoding="utf-8")
gate = importlib.import_module("scripts.emoji_gate")


def test_the_panel_is_a_compact_step_list():
    assert re.search(r'<section id="setup-panel" class="[^"]*\bdx-steps dx-steps--compact\b[^"]*" data-steps', PANEL)
    assert re.findall(r'<li class="dx-step" data-step="([^"]+)"', PANEL) == ["sdk", "samples"]
    assert "data-steps-summary" in PANEL and 'id="setup-summary-facts"' in PANEL
    assert BASE.index("/static/shared/dx-steps.js") < BASE.index("/static/js/setup_panel.js")


def test_ids_the_tutorial_and_js_use_are_kept():
    for kept in ("setup-panel", "setup-toggle", "setup-body", "setup-install-btn", "setup-download-btn",
                 "setup-sdk-icon", "setup-sdk-version", "setup-install-progress", "setup-install-bar",
                 "setup-install-text", "setup-install-log", "setup-download-progress", "setup-download-bar",
                 "setup-download-text"):
        assert f'id="{kept}"' in PANEL, kept


def test_no_emoji_left():
    for name, src in (("setup_panel.html", PANEL), ("setup_panel.js", JS)):
        assert gate.count(src) == 0, (name, sorted({c for c in src if gate.count(c)}))


def test_state_goes_through_dxsteps():
    assert "DXSteps.set(" in JS
    assert "sdkIcon.textContent" not in JS and "samplesIcon.textContent" not in JS


def test_one_place_decides_the_compile_lock():
    """If feature-check and setup status each set the button, whichever finishes last wins."""
    start = INDEX.index("fetch('/feature-check')")
    feature = INDEX[start:INDEX.index("}).catch", start)]
    assert "setupPanel.setFeatureCompile(" in feature
    assert "btn.disabled = true" not in feature
    assert 'id="compile-gate-reason"' in INDEX
    assert "'Install the SDK first'" in JS
    body = JS[JS.index("  _disableCompileForm(disabled, reason) {"):]
    body = body[:body.index("\n  }\n")]
    assert "compile-gate-reason" in body and "aria-describedby" in body


def test_the_tutorial_reveals_the_folded_panel_first():
    for sel in ("#setup-toggle", "#setup-install-btn", "#setup-download-btn"):
        line = next(l for l in TUTORIAL.splitlines() if f"target: '{sel}'" in l)
        assert "revealForTour" in line, sel

"""Setup step list: the contract of the shared component.

The app and stream Setup pages and the compiler's Setup pane use the same component. Module JS only reports state
(DXSteps.set); the component works out the next step, the bar, the button labels and collapsing.
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = (ROOT / "shared" / "static" / "dx-steps.js").read_text(encoding="utf-8")
CSS = (ROOT / "shared" / "static" / "dx-components.css").read_text(encoding="utf-8")
gate = importlib.import_module("scripts.emoji_gate")


def test_the_states_are_the_agreed_five():
    assert re.search(r"STATES = \['done', 'todo', 'running', 'failed', 'blocked'\]", JS)


def test_state_is_shape_colour_and_words():
    """States are not told apart by colour alone: each has an icon and words."""
    icons = re.search(r"STATE_ICON = \{([^}]*)\}", JS).group(1)
    for state, icon in (("done", "check"), ("todo", "alert"), ("running", "spinner"), ("failed", "x")):
        assert f"{state}: '{icon}'" in icons, state
    for key in ("Ready", "Needs setup", "Running", "Failed", "After step {n}", "{n} of {m} ready", "Set up the rest ({n})"):
        assert re.search(r"'" + re.escape(key) + r"': \{ ko: '[^']+', ja: '[^']+', 'zh-CN': '[^']+', 'zh-TW': '[^']+', es: '[^']+' \}", JS), key


def test_only_the_next_step_is_open_by_default():
    body = JS[JS.index("function refresh("):JS.index("function set(")]
    assert "li === next" in body and "is-open" in body
    assert ".dx-step.is-open .dx-step-more { display: block; }" in CSS
    assert re.search(r"\.dx-step-more \{ display: none;", CSS)


def test_compact_collapses_to_one_line_when_complete():
    assert ".dx-steps--compact.is-complete:not(.is-expanded) .dx-steps-summary { display: flex; }" in CSS


def test_no_emoji_in_the_component():
    assert gate.count(JS) == 0
    part = CSS[CSS.index("Setup step list"):]
    assert gate.count(part) == 0

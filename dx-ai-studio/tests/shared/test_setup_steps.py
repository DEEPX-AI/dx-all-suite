"""Setup 단계 목록 — 공용 부품의 계약 (spec 2026-09-29 아이콘 체계 단계 2).

app · stream 의 Setup 과 compiler 의 Setup 칸이 같은 부품을 쓴다. 모듈 JS 는 상태만 알리고
(DXSteps.set), 다음 단계 · 막대 · 버튼 글자 · 접기는 부품이 계산한다.
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
    """색만으로 가르지 않는다 — 각 상태에 아이콘과 말이 있다."""
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

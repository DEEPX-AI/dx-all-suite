"""launcher 튜토리얼이 새 무대를 따라가는지 (spec 2026-09-23 §9, §8.2)."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TUTORIAL = (ROOT / "launcher" / "static" / "tutorial.js").read_text(encoding="utf-8")
HTML = (ROOT / "launcher" / "static" / "index.html").read_text(encoding="utf-8")

ORDER = [
    "#homeAskForm .ask-box",
    "#homeAskChips",
    "#homeStage .stage-films",
    "#studioGrid",
    ".about-book-card.sdk-card",
    ".about-book-card:not(.sdk-card)",
    "#homeDevice",
    "#homeMeasured",
    "#homeBar",
    "#homeTour",
    ".dx-chat-fab",
    ".dx-chat-settings-kind",          # 2026-10-11: settings ask one question (chat settings redesign)
    ".dx-chat-window.open",
]
GONE = [".top-bar", "#launcherToolbar", "#deepxLinks", "#dxt-tutorial-card", "#replayBtn"]


def _steps() -> str:
    start = TUTORIAL.index("steps: [")
    return TUTORIAL[start:TUTORIAL.index("\n      ] }", start)]


def test_the_steps_follow_the_stage():
    targets = re.findall(r"\{ target: '([^']+)'", _steps())
    assert targets == ORDER, targets


def test_the_step_list_has_no_holes():
    """`},,` 는 배열에 빈 칸을 만든다 — 엔진은 steps[i] 가 undefined 인 곳에서 투어를 멈춘다. 처음 판이
    SDK Library 다음에서 멈췄다 (정규식으로 대상만 보던 위 테스트는 통과했다)."""
    assert not re.search(r"\}\s*,\s*,", _steps())


def test_the_old_furniture_is_not_a_step():
    targets = re.findall(r"\{ target: '([^']+)'", _steps())
    for gone in GONE:
        assert gone not in targets, gone


def _pictographs(text: str) -> list[str]:
    return sorted({ch for ch in text if unicodedata.category(ch) == "So" and ord(ch) > 0x2600})


def test_no_emoji_in_the_launcher_steps():
    """아이콘은 이모지 작업이 SVG 로 바꾼다 — 설명이 이모지를 가리키면 그때 거짓이 된다."""
    body = re.sub(r"//[^\n]*", "", _steps())
    assert _pictographs(body) == [], _pictographs(body)


def test_tutorial_mode_is_translated():
    m = re.search(r"'Tutorial Mode':\s*\{([^}]*)\}", HTML)
    values = dict(re.findall(r"['\"]?([\w-]+)['\"]?\s*:\s*'([^']*)'", m.group(1)))
    for lang in ("ko", "ja", "zh-CN", "zh-TW", "es"):
        assert values.get(lang) and values[lang] != "Tutorial Mode", (lang, values.get(lang))

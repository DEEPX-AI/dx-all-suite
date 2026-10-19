"""The launcher tutorial follows the stage layout."""
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
    ".dx-chat-settings-kind",          # settings ask one question
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
    """`},,` makes a hole in the array, and the engine stops the tour where steps[i] is undefined. A regex that
    reads only targets (the test above) does not see it."""
    assert not re.search(r"\}\s*,\s*,", _steps())


def test_the_old_furniture_is_not_a_step():
    targets = re.findall(r"\{ target: '([^']+)'", _steps())
    for gone in GONE:
        assert gone not in targets, gone


def _pictographs(text: str) -> list[str]:
    return sorted({ch for ch in text if unicodedata.category(ch) == "So" and ord(ch) > 0x2600})


def test_no_emoji_in_the_launcher_steps():
    """Icons are SVG; a description that points at an emoji would be false."""
    body = re.sub(r"//[^\n]*", "", _steps())
    assert _pictographs(body) == [], _pictographs(body)


def test_tutorial_mode_is_translated():
    m = re.search(r"'Tutorial Mode':\s*\{([^}]*)\}", HTML)
    values = dict(re.findall(r"['\"]?([\w-]+)['\"]?\s*:\s*'([^']*)'", m.group(1)))
    for lang in ("ko", "ja", "zh-CN", "zh-TW", "es"):
        assert values.get(lang) and values[lang] != "Tutorial Mode", (lang, values.get(lang))

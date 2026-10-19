"""Tutorial icons come from the same sprite.

- a section icon is a sprite name (drawn by tutorial-engine.js _dxtSectionIcon),
- titles and descriptions are plain text,
- body text that points at a mark on screen uses {{i:name}} (the engine swaps in that icon), and steps are digits.
Migrated modules are listed in MIGRATED below, so emoji cannot come back once a module is moved.
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ENGINE = (ROOT / "shared" / "static" / "tutorial-engine.js").read_text(encoding="utf-8")
SPRITE = (ROOT / "shared" / "static" / "dx-icons.svg").read_text(encoding="utf-8")
gate = importlib.import_module("scripts.emoji_gate")
SYMBOLS = set(re.findall(r'<symbol id="([^"]+)"', SPRITE))

MIGRATED = [
    "dx_planner/static/js/tutorial.js",
    "dx_agent_dev/static/js/tutorial.js",
    "dx_benchmark/static/js/tutorial.js",
    "dx_compiler/static/js/tutorial.js",
    "dx_modelzoo/static/js/tutorial.js",
    "dx_monitor/static/js/tutorial.js",
    "dx_stream/static/js/tutorial.js",
    "dx_app/static/js/tutorial.js",
    "launcher/static/tutorial.js",
    "launcher/static/sdk-tutorial.js",
]


def test_the_engine_turns_icon_tokens_into_sprite_icons():
    assert "function _dxtExpandIcons(" in ENGINE
    assert ENGINE.count("_dxtExpandIcons(this._t(step.content))") == 2
    assert "/^[a-z0-9_-]+$/" in ENGINE, "task-object_detection 같은 이름도 구역 아이콘이 되어야 한다"


@pytest.mark.parametrize("rel", MIGRATED)
def test_a_migrated_tutorial_has_no_emoji_left(rel):
    src = (ROOT / rel).read_text(encoding="utf-8")
    assert gate.count(src) == 0, sorted({c for c in src if gate.count(c)})


@pytest.mark.parametrize("rel", MIGRATED)
def test_its_section_icons_and_tokens_are_real_symbols(rel):
    src = (ROOT / rel).read_text(encoding="utf-8")
    names = re.findall(r"\bicon\s*:\s*'([^']+)'", src) + re.findall(r"\{\{i:([a-z0-9_-]+)\}\}", src)
    missing = sorted({n for n in names if n not in SYMBOLS})
    assert not missing, missing

"""Launcher tutorial six-language contract."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TUTORIAL = ROOT / "launcher" / "static" / "tutorial.js"
TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")


def test_launcher_tutorial_covers_six_languages():
    source = TUTORIAL.read_text(encoding="utf-8")
    ko_count = len(re.findall(r"(?<![A-Za-z0-9_'\"-])ko\s*:", source))
    assert ko_count >= 8
    deficits = {}
    for lang in TARGET_LANGS:
        count = len(re.findall(rf"['\"]?{re.escape(lang)}['\"]?\s*:", source))
        if count < ko_count:
            deficits[lang] = (count, ko_count)
    assert not deficits, f"language coverage deficits: {deficits}"


def test_launcher_tutorial_labels_include_es():
    source = TUTORIAL.read_text(encoding="utf-8")
    assert "Modo tutorial" in source
    assert re.search(r"es:\s*['\"]Modo tutorial['\"]", source)


def test_sdk_tutorial_covers_six_languages():
    source = (ROOT / "launcher" / "static" / "sdk-tutorial.js").read_text(encoding="utf-8")
    ko_count = len(re.findall(r"(?<![A-Za-z0-9_'\"-])ko\s*:", source))
    assert ko_count >= 8
    deficits = {}
    for lang in TARGET_LANGS:
        count = len(re.findall(rf"['\"]?{re.escape(lang)}['\"]?\s*:", source))
        if count < ko_count:
            deficits[lang] = (count, ko_count)
    assert not deficits, f"sdk-tutorial language coverage deficits: {deficits}"

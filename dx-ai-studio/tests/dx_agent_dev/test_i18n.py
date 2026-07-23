"""dx_agent_dev 정적 i18n 계약(범위 축소판 — 콘솔 동적 키만).

dx_monitor/test_i18n.py 구조를 따르되 콘솔이 사용하는 T() 키만 검증한다.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENT = ROOT / "dx_agent_dev"
I18N = AGENT / "static" / "js" / "i18n.js"
SOURCE_FILES = [AGENT / "static" / "js" / "console.js"]
TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def dict_keys() -> set:
    return set(re.findall(r"'((?:\\.|[^'\\])+)':\s*\{", read_text(I18N)))


def dict_entry(key: str) -> str:
    match = re.search(rf"'{re.escape(key)}':\s*\{{(.*?)\n\s*\}}\s*(?:,|\n)",
                      read_text(I18N), re.S)
    return match.group(1) if match else ""


def t_keys(path: Path) -> set:
    source = read_text(path)
    single = re.findall(r"\bT\('((?:\\.|[^'\\])+)'", source)
    double = re.findall(r'\bT\("((?:\\.|[^"\\])+)"', source)
    return set(single + double)


def test_dictionary_nonempty():
    assert len(dict_keys()) >= 8


def test_console_t_keys_are_in_dictionary():
    keys = dict_keys()
    missing = {}
    for path in SOURCE_FILES:
        unresolved = sorted(k for k in t_keys(path) if k not in keys)
        if unresolved:
            missing[path.name] = unresolved
    assert not missing, missing


def test_dictionary_entries_cover_target_languages():
    incomplete = {}
    for key in dict_keys():
        entry = dict_entry(key)
        missing_langs = [
            lang for lang in TARGET_LANGS
            if f"{lang}:" not in entry and f"'{lang}':" not in entry and f'"{lang}":' not in entry
        ]
        if missing_langs:
            incomplete[key] = missing_langs
    assert not incomplete, incomplete

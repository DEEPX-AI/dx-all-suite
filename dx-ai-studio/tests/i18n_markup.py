"""One place to decide "does this control's label show in all 6 languages".

A label is a single `data-i18n="English key"` and its translations live in the module
dictionary, so the check is that every key resolves in the dictionary for the 5 other languages.
"""
from __future__ import annotations

import html as _html
import re

from scripts.migrate_i18n_spans import _load_dict

LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")

_ATTR = re.compile(r'data-i18n(?:-html)?="([^"]*)"')
_SPAN = re.compile(r'class="(ko|ja|zh-CN|zh-TW|en|es)"')


def i18n_keys(fragment: str) -> list[str]:
    """Keys in the fragment that need a translation."""
    return [_html.unescape(k) for k in _ATTR.findall(fragment)]


def assert_translatable(fragment: str, dict_rel: str, label: str) -> None:
    """Assert the fragment's labels show in all 6 languages.

    Markup that still carries one span per language is accepted as is — some blocks hold two
    phrases under one key and cannot move to data-i18n.
    """
    keys = i18n_keys(fragment)
    if not keys:
        found = set(_SPAN.findall(fragment))
        assert found >= {"en", *LANGS}, (
            f"{label}: 번역 경로가 없다 — data-i18n 도, 언어 span 도 없음 "
            f"(span: {sorted(found)})"
        )
        return

    dictionary = _load_dict(dict_rel)
    incomplete = {}
    for key in keys:
        entry = dictionary.get(key)
        if not isinstance(entry, dict):
            incomplete[key] = list(LANGS)
            continue
        gaps = [lang for lang in LANGS if not entry.get(lang)]
        if gaps:
            incomplete[key] = gaps
    assert not incomplete, f"{label}: 사전이 못 채우는 언어가 있다 — {incomplete}"

#!/usr/bin/env python3
"""Backfill es (and missing ja/zh) into dx_app/static/js/tutorial.js."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "dx_app" / "static" / "js" / "tutorial.js"
TRANS_FILE = Path(__file__).resolve().parent / "data" / "dx_app_tutorial_es.json"
INCOMPLETE_FILE = Path(__file__).resolve().parent / "data" / "dx_app_tutorial_incomplete.json"

LANG_ORDER = ("ko", "en", "ja", "zh-CN", "zh-TW", "es")

_JS_LANG_RE = re.compile(
    r"['\"]?(en|ja|ko|es|zh-CN|zh-TW)['\"]?\s*:\s*"
    r"(?:'(?P<value_s>(?:\\.|[^'\\])*)'|\"(?P<value_d>(?:\\.|[^\"\\])*)\")"
)


def js_quote(key: str, value: str) -> str:
    qkey = f"'{key}'" if "-" in key else key
    normalized = value.replace("\\'", "'")
    escaped = normalized.replace("'", "\\'")
    return f"{qkey}: '{escaped}'"


def _lookup(mapping: dict[str, str], key: str) -> str | None:
    if key in mapping:
        return mapping[key]
    alt = key.replace("\\'", "'")
    if alt in mapping:
        return mapping[alt]
    return None


def render_map(texts: dict[str, str]) -> str:
    parts = [js_quote(lang, texts[lang]) for lang in LANG_ORDER if lang in texts]
    return ", ".join(parts)


def extract_maps(source: str) -> list[tuple[int, int, dict[str, str]]]:
    maps: list[tuple[int, int, dict[str, str]]] = []
    i = 0
    while i < len(source):
        m = _JS_LANG_RE.search(source, i)
        if not m:
            break
        start = m.start()
        texts: dict[str, str] = {}
        pos = start
        while True:
            m2 = _JS_LANG_RE.match(source, pos)
            if not m2:
                break
            lang = m2.group(1)
            val = m2.group("value_s") or m2.group("value_d") or ""
            texts[lang] = val
            pos = m2.end()
            while pos < len(source) and source[pos] in " \t\n,":
                pos += 1
        if "ko" in texts and len(texts) >= 2:
            maps.append((start, pos, texts))
        i = pos if pos > start else m.end() + 1
    return maps


def main() -> int:
    es_map: dict[str, str] = json.loads(TRANS_FILE.read_text(encoding="utf-8"))
    incomplete: dict[str, dict[str, str]] = json.loads(
        INCOMPLETE_FILE.read_text(encoding="utf-8")
    )

    source = TUTORIAL.read_text(encoding="utf-8")
    maps = extract_maps(source)

    missing_es = 0
    fixed_incomplete = 0
    for start, end, texts in reversed(maps):
        en = texts.get("en", "")
        changed = False

        inc = _lookup(incomplete, en)
        if inc:
            for lang, val in inc.items():
                if lang not in texts:
                    texts[lang] = val
                    changed = True
            fixed_incomplete += 1

        if "es" not in texts:
            es_val = _lookup(es_map, en)
            if es_val is None:
                print(f"MISSING ES TRANSLATION: {en[:80]!r}", file=sys.stderr)
                return 1
            texts["es"] = es_val
            missing_es += 1
            changed = True

        if changed:
            source = source[:start] + render_map(texts) + source[end:]

    source = source.replace(
        "12 sections, ~115 steps — bilingual (ko/en)",
        "12 sections, ~115 steps — 6-language (ko/en/ja/zh-CN/zh-TW/es)",
        1,
    )

    TUTORIAL.write_text(source, encoding="utf-8")
    print(f"Applied es to {missing_es} maps; fixed {fixed_incomplete} incomplete maps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

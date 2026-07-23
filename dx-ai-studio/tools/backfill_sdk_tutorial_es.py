#!/usr/bin/env python3
"""Backfill missing es keys in launcher/static/sdk-tutorial.js (copy from en)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "launcher" / "static" / "sdk-tutorial.js"
LANG_ORDER = ("ko", "en", "ja", "zh-CN", "zh-TW", "es")

_JS_LANG_RE = re.compile(
    r"['\"]?(en|ja|ko|es|zh-CN|zh-TW)['\"]?\s*:\s*"
    r"(?:'(?P<value_s>(?:\\.|[^'\\])*)'|\"(?P<value_d>(?:\\.|[^\"\\])*)\")"
)


def js_quote(key: str, value: str) -> str:
    qkey = f"'{key}'" if "-" in key else key
    escaped = value.replace("\\'", "'").replace("'", "\\'")
    return f"{qkey}: '{escaped}'"


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
    source = TUTORIAL.read_text(encoding="utf-8")
    maps = extract_maps(source)
    missing_es = 0
    for start, end, texts in reversed(maps):
        if "es" in texts:
            continue
        en = texts.get("en")
        if not en:
            print("SKIP map without en", file=sys.stderr)
            continue
        texts["es"] = en
        missing_es += 1
        source = source[:start] + render_map(texts) + source[end:]
    TUTORIAL.write_text(source, encoding="utf-8")
    print(f"Applied es (from en) to {missing_es} maps in sdk-tutorial.js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

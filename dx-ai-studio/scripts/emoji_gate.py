#!/usr/bin/env python3
"""Ratchet that keeps the number of emoji icons in the UI going down.

The studio's icons are the single set in `shared/static/dx-icons.svg`, but many places still use
emoji: toolbar 🌏 ◒◓◑ 🎓, Setup ①–⑥ ✅ ⏳, task 🎯🏷️, page titles, tutorial sections. Emoji render
differently per OS and font (headless capture drew ◒ as "-"), and the theme cannot set their colour
or weight.

There are too many to remove at once, so this works like css_token_gate and spacing_scale_gate:
**the current count is a per-file ceiling and only increases are blocked.** Lower it with `--update`
after removing some.

Counted: pictographs (U+1F000–1FAFF), misc symbols and dingbats (2600–27BF), misc technical
(2300–23FF — ⏳ ⌨ ⏹), enclosed numbers (2460–24FF — ①), geometric shapes (25A0–25FF — ▶ ◒ ■),
misc symbols and arrows (2B00–2BFF — ⬇ ⭐), and ℹ.
Not counted: arrows (2190–21FF — → ↗), punctuation (— · ›), variation selectors (FE0F).
Literal characters are counted, and so are JS escapes (\\uD83C\\uDF93 · \\u2705) and HTML numeric
entities (&#9662;).

Scope: .js · .html · .css · .json under each module's and the shared `static/` and `templates/`
(plus shared/hw_widget, which is injected into every module). Tutorials, translation dictionaries,
references and data count too; their icons move to the icon set as well (body text stays text).

Contract: tests/shared/test_emoji_gate.py
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "config" / "emoji_baseline.json"

_RANGES = (
    (0x1F000, 0x1FAFF),
    (0x2600, 0x27BF),
    (0x2300, 0x23FF),
    (0x2460, 0x24FF),
    (0x25A0, 0x25FF),
    (0x2B00, 0x2BFF),
    (0x2139, 0x2139),
)
_SUFFIXES = (".js", ".html", ".css", ".json")
_SKIP = (".venv", "node_modules", "/var/", "/tests/", "/docs/", "/outputs/", "/data/models/", ".min.")


_JS_ESCAPE = re.compile(r"\\u([dD][89abAB][0-9a-fA-F]{2})\\u([dD][c-fC-F][0-9a-fA-F]{2})|\\u([0-9a-fA-F]{4})")
_ENTITY = re.compile(r"&#(?:x([0-9a-fA-F]+)|(\d+));")


def _pictographic(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in _RANGES)


def _decoded(text: str):
    """Code points written literally, plus those written as JS escapes ('\\uD83C\\uDF93', '\\u2705')
    or HTML numeric entities ('&#9662;'), so an escaped emoji still counts."""
    for ch in text:
        yield ord(ch)
    for m in _JS_ESCAPE.finditer(text):
        if m.group(1):
            hi, lo = int(m.group(1), 16), int(m.group(2), 16)
            yield 0x10000 + ((hi - 0xD800) << 10) + (lo - 0xDC00)
        else:
            yield int(m.group(3), 16)
    for m in _ENTITY.finditer(text):
        yield int(m.group(1), 16) if m.group(1) else int(m.group(2))


def count(text: str) -> int:
    return sum(1 for cp in _decoded(text) if _pictographic(cp))


def _iter_files():
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in _SUFFIXES or not path.is_file():
            continue
        rel = "/" + str(path.relative_to(ROOT))
        if any(s in rel for s in _SKIP):
            continue
        parts = path.relative_to(ROOT).parts
        # hw_widget lives outside static/ but is a shared view injected into every module.
        if "static" not in parts and "templates" not in parts and "hw_widget" not in parts:
            continue
        yield rel[1:], path


def count_tree() -> dict[str, int]:
    counts: dict[str, int] = {}
    for rel, path in _iter_files():
        n = count(path.read_text(encoding="utf-8", errors="ignore"))
        if n:
            counts[rel] = n
    return counts


def regressions(counts: dict[str, int], baseline: dict[str, int]) -> list[str]:
    """Files over their ceiling (a new file has a ceiling of 0)."""
    return [rel for rel, n in sorted(counts.items()) if n > baseline.get(rel, 0)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--update", action="store_true",
                    help="현재 값으로 baseline 을 다시 쓴다 (걷어낸 뒤 내릴 때)")
    args = ap.parse_args(argv)

    counts = count_tree()
    total = sum(counts.values())

    if args.update:
        BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_PATH.write_text(
            json.dumps(dict(sorted(counts.items())), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"baseline 갱신: 파일 {len(counts)}개 · 이모지 {total}개")
        return 0

    if not BASELINE_PATH.is_file():
        print(f"baseline 이 없다: {BASELINE_PATH} (--update 로 만든다)")
        return 1

    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    over = regressions(counts, baseline)
    print(f"UI 이모지 {total}개 · 파일 {len(counts)}개 (상한 합 {sum(baseline.values())})")
    for rel in over:
        print(f"  {rel}: 이모지가 {baseline.get(rel, 0)} → {counts[rel]} 로 늘었다. "
              f"DXIcon('<name>') 과 shared/static/dx-icons.svg 를 쓰세요")
    return 1 if over else 0


if __name__ == "__main__":
    raise SystemExit(main())

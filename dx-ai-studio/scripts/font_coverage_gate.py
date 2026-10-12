"""Check that every CJK glyph in the translation dictionaries is in that language's font subset.

A missing glyph falls back to another font on screen, mixing letterforms within one sentence.
On failure: .venv/bin/python -m scripts.build_font_subsets
"""
from __future__ import annotations

import json
import sys

try:
    from fontTools.ttLib import TTFont
except ImportError:  # run_ci.sh does not pip install (air-gapped); give the same hint.
    sys.exit("fonttools not found — install test deps first: "
             "<python> -m pip install -r requirements-ci.txt")

from scripts.font_glyphs import ROOT, dictionary_glyphs

SOURCES = ROOT / "config" / "font_sources.json"
FONTS = ROOT / "shared" / "static" / "fonts"

# Same order as --font-cjk in the :root:lang(...) rules of dx-tokens.css. A glyph missing from the
# first font is drawn by the next, so the gate checks the whole chain (checking one font alone would
# fail on glyphs that render fine).
CHAIN = {"ko": ("ko", "zh-CN"), "ja": ("ja", "zh-CN"), "zh-CN": ("zh-CN",), "zh-TW": ("zh-TW", "zh-CN")}


def missing_glyphs() -> dict[str, list[str]]:
    specs = json.loads(SOURCES.read_text(encoding="utf-8"))
    cmaps = {s["lang"]: TTFont(FONTS / s["output"]).getBestCmap()
             for s in specs.values() if s["lang"] != "latin"}
    missing: dict[str, list[str]] = {}
    for lang, cps in dictionary_glyphs().items():
        lacking = sorted(chr(cp) for cp in cps
                         if not any(cp in cmaps[f] for f in CHAIN[lang]))
        if lacking:
            missing[lang] = lacking
    return missing


def main() -> int:
    missing = missing_glyphs()
    if not missing:
        print("font coverage: 사전의 한중일 글자가 모두 subset 에 있다")
        return 0
    for lang, chars in missing.items():
        print(f"font coverage: {lang} 글꼴에 없는 글자 {len(chars)}개: {''.join(chars[:40])}")
    print("→ .venv/bin/python -m scripts.build_font_subsets")
    return 1


if __name__ == "__main__":
    sys.exit(main())

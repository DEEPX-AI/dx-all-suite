#!/usr/bin/env python3
"""Count literal colours and compare them with the baseline.

The palette lives only in three files under shared/static (dx-tokens / dx-semantic /
dx-theme-light). A literal colour anywhere else silently breaks theme switching, because
it does not follow the tokens. The baseline can only go down; a new literal fails at once.

Both hex and rgb()/rgba() are counted (the same colour often appears in either form), in
CSS, JS and HTML, since charts and widgets carry inline colours too. Component files under
shared/static are scanned like any module; only the palette files are exempt.

Neutral rgb (black/white with alpha) is a legitimate scrim or hairline and is not counted.
Only chromatic colours are, since inlining those is what breaks the theme.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "config" / "css_token_baseline.json"

# Files scanned for literal colours. The palette files in shared/static are skipped
# via PALETTE_FILES below (dx-tokens.css is the source of truth).
SCAN_GLOBS = (
    "launcher/static/*.css",
    "launcher/static/*.js",
    "dx_*/static/css/*.css",
    "dx_*/static/js/*.js",
    "shared/static/*.css",
    "shared/static/*.js",
    "shared/chat/static/*.css",
    "shared/hw_widget/*.html",
)

# Where the palette is defined; literals belong here.
PALETTE_FILES = frozenset({
    "shared/static/dx-tokens.css",
    "shared/static/dx-semantic.css",
    "shared/static/dx-theme-light.css",
})

_HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
_RGB = re.compile(r"\brgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)")
# Custom property definitions (--x: #fff) are token declarations and are not counted.
_VAR_DEF = re.compile(r"--[\w-]+\s*:[^;}]*")


def count_raw_hex(css: str) -> int:
    """Number of literal colours: every hex plus chromatic rgb()/rgba().

    Neutral colours (r==g==b) are legitimate scrims and hairlines. Only inlined
    chromatic colours break the theme, so only those are counted.
    """
    body = _VAR_DEF.sub("", css)
    n = len(_HEX.findall(body))
    for m in _RGB.finditer(body):
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        if not (r == g == b):
            n += 1
    return n


def scan_modules(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for pattern in SCAN_GLOBS:
        for path in sorted(root.glob(pattern)):
            rel = path.relative_to(root).as_posix()
            if rel in PALETTE_FILES:
                continue
            counts[rel] = count_raw_hex(path.read_text(encoding="utf-8"))
    return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="현재 값으로 baseline을 다시 쓴다")
    args = ap.parse_args(argv)

    counts = scan_modules(ROOT)
    if args.write:
        BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_PATH.write_text(
            json.dumps(counts, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"wrote {BASELINE_PATH.relative_to(ROOT)} ({sum(counts.values())} raw hex)")
        return 0

    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    failed = False
    for rel, n in sorted(counts.items()):
        allowed = baseline.get(rel, 0)
        if n > allowed:
            print(f"FAIL {rel}: {n} raw hex > baseline {allowed}")
            failed = True
    print(f"total raw hex: {sum(counts.values())}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

"""Download the variable source fonts and build woff2 subsets with only the glyphs the studio uses.

    .venv/bin/python -m scripts.build_font_subsets

Sources are pinned by URL and sha256 in config/font_sources.json and cached in var/font-src/
(git-ignored). Only the subsets and licenses are committed. Re-run this when a translation adds
new glyphs and scripts/font_coverage_gate.py fails.
"""
from __future__ import annotations

import hashlib
import io
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

from scripts.font_glyphs import ROOT, all_glyphs

SOURCES = ROOT / "config" / "font_sources.json"
CACHE = ROOT / "var" / "font-src"
OUT = ROOT / "shared" / "static" / "fonts"
LAUNCHER_OUT = ROOT / "launcher" / "static" / "fonts"

# Ranges kept in the Latin fonts: Basic Latin + extensions (covers es), combining marks, general
# punctuation, currency, letterlike symbols (™), arrows (→ ↗), math, shapes (▶ ●), checks (✓ ✕).
LATIN = [
    *range(0x20, 0x7F), *range(0xA0, 0x250), *range(0x300, 0x370),
    *range(0x2000, 0x2070), *range(0x20A0, 0x20D0), *range(0x2100, 0x2150),
    *range(0x2190, 0x2200), *range(0x2200, 0x2300), *range(0x25A0, 0x2600),
    0x2713, 0x2715,
]


def _fetch(label: str, file: str, url: str, sha256: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / file
    if not dest.exists():
        print(f"  받는 중 {label}: {url}")
        with urllib.request.urlopen(url, timeout=300) as resp:
            dest.write_bytes(resp.read())
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    if digest != sha256:
        raise SystemExit(f"{label}: sha256 {digest} != {sha256} — 원본이 바뀌었다. "
                         f"config/font_sources.json 을 확인하라")
    return dest


def _read(path: Path, member: str | None) -> bytes:
    if member is None:
        return path.read_bytes()
    with zipfile.ZipFile(path) as zf:
        return zf.read(member)


def _subset(font_bytes: bytes, unicodes, out: Path) -> None:
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]   # tnum (fixed digit width for count-ups), kern, liga …
    opts.name_IDs = ["*"]
    opts.hinting = False
    opts.notdef_outline = True
    # recalcTimestamp=False keeps the source head.modified. Otherwise the save time is written in
    # and the same input gives a different file each run (tests/shared/test_font_subsets.py).
    font = TTFont(io.BytesIO(font_bytes), recalcTimestamp=False)
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=sorted(unicodes))
    sub.subset(font)
    font.flavor = "woff2"
    font.save(out)


def main() -> int:
    specs = json.loads(SOURCES.read_text(encoding="utf-8"))
    glyphs = all_glyphs()
    for name, spec in specs.items():
        src = _fetch(name, spec["file"], spec["url"], spec["sha256"])
        unicodes = LATIN if spec["lang"] == "latin" else glyphs[spec["lang"]]
        out = OUT / spec["output"]
        _subset(_read(src, spec["member"]), unicodes, out)

        lic = spec["license"]
        lic_src = (_fetch(f"{name} license", lic["file"], lic["url"], lic["sha256"])
                   if "url" in lic else src)
        (OUT / spec["license_output"]).write_bytes(_read(lic_src, lic["member"]))
        print(f"  {spec['output']:34} {len(unicodes):5} 글자  {out.stat().st_size // 1024:4} KB")

    inter = specs["inter"]["output"]
    shutil.copyfile(OUT / inter, LAUNCHER_OUT / inter)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Ratchet: Korean text in source comments may only go down.

Comments and docstrings ship with the studio, and readers of the code should not need Korean to follow it. This
gate keeps them in English. UI text (i18n dictionary values, strings shown to users) is not a comment and is not
counted.

Counts lines of comment text that contain Hangul, per tracked file (py, js, css, html, sh; vendor and minified files
are skipped). `--update` rewrites config/comment_language_baseline.json; a file may never exceed its baseline.

Contract: tests/shared/test_comment_tools.py
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from scripts.comment_lexer import KINDS, comments

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "config" / "comment_language_baseline.json"
_HANGUL = re.compile(r"[가-힣ᄀ-ᇿ㄰-㆏]")


def tracked_sources() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    return [f for f in out if Path(f).suffix in KINDS and "/vendor/" not in f and not f.endswith(".min.js")]


def hangul_comment_lines(text: str, kind: str) -> int:
    return sum(1 for c in comments(text, kind) for line in c.splitlines() if _HANGUL.search(line))


def count() -> dict[str, int]:
    counts: dict[str, int] = {}
    for rel in tracked_sources():
        try:
            text = (ROOT / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        n = hangul_comment_lines(text, KINDS[Path(rel).suffix])
        if n:
            counts[rel] = n
    return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--update", action="store_true", help="rewrite the baseline with the current counts")
    args = ap.parse_args(argv)
    counts = count()
    total = sum(counts.values())
    if args.update:
        BASELINE_PATH.write_text(json.dumps(dict(sorted(counts.items())), indent=2) + "\n", encoding="utf-8")
        print(f"baseline updated: {len(counts)} files · {total} Korean comment lines")
        return 0
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8")) if BASELINE_PATH.is_file() else {}
    problems = [f"  {rel}: Korean comment lines {baseline.get(rel, 0)} → {n}. Write comments in English."
                for rel, n in sorted(counts.items()) if n > baseline.get(rel, 0)]
    print(f"Korean comment lines: {total} in {len(counts)} files")
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

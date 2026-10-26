#!/usr/bin/env python3
"""Prove that a change touched comments only: same Python AST (docstrings aside), same code tokens elsewhere.

Usage: python -m scripts.comment_only_diff [REF] [PATH ...]   (REF defaults to HEAD; paths default to every modified
tracked file of a supported kind). Exits 1 and names each file whose code changed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.comment_lexer import KINDS, code_tokens, python_equivalent

ROOT = Path(__file__).resolve().parent.parent


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def same_code(before: str, after: str, kind: str) -> bool:
    if kind == "py":
        return python_equivalent(before, after)
    return code_tokens(before, kind) == code_tokens(after, kind)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ref = argv.pop(0) if argv and not Path(ROOT / argv[0]).exists() else "HEAD"
    paths = argv or [p for p in _git("diff", "--name-only", ref, "--", ".").split() if Path(p).suffix in KINDS]
    bad = []
    for rel in paths:
        rel = rel[len("dx-ai-studio/"):] if rel.startswith("dx-ai-studio/") else rel
        kind = KINDS.get(Path(rel).suffix)
        if not kind or not (ROOT / rel).is_file():
            continue
        try:
            before = _git("show", f"{ref}:./{rel}")
        except subprocess.CalledProcessError:
            bad.append(f"{rel}: new file (not a comment-only change)")
            continue
        after = (ROOT / rel).read_text(encoding="utf-8")
        try:
            if not same_code(before, after, kind):
                bad.append(f"{rel}: code changed")
        except SyntaxError as exc:
            bad.append(f"{rel}: does not parse ({exc})")
    print(f"comment-only check: {len(paths)} files, {len(bad)} with code changes")
    for line in bad:
        print("  " + line)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

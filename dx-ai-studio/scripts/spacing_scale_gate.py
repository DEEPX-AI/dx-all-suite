#!/usr/bin/env python3
"""Ratchet that keeps spacing values off the 4px scale going down.

The tokens define seven steps: `--sp-1..7` = 4·8·12·16·24·32·48px. Yet raw px values in
padding/margin/gap were spread over dozens of sizes, about half of them off the scale; the most
common, 6px, has no token at all.

A 2px difference is invisible in one place. The problem shows when values **stack**: a card at
6px, a list inside it at 10px and a badge at 14px never line up with each other. Fixing that late
shakes the whole visual baseline.

Same approach as colours (css_token_gate) and breakpoints (breakpoint_gate): **the current count is
a per-file ceiling and only increases are blocked.** Reducing is always fine; lower the ceiling with
`--update`.

The scale is read from `shared/static/dx-tokens.css` rather than written here, so it cannot drift
silently when the tokens change.

Not counted:
  - declarations that use `var(--sp-*)`: they already do the right thing
  - 0, 1px, 2px: border and hairline sizes, not spacing
  - values inside `auto`, `%`, `em`, `rem`, `calc()`: the px scale does not apply

Contract: tests/shared/test_spacing_scale_gate.py
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "shared" / "static" / "dx-tokens.css"
BASELINE_PATH = ROOT / "config" / "spacing_scale_baseline.json"

_PROPS = ("padding", "margin", "gap")
# Borders and hairlines are not on the spacing scale.
_IGNORE_BELOW = 3
_SKIP_DIRS = (".venv", "node_modules", "/data/", "docs/.venv-docs", "/outputs/")


def scale() -> set[int]:
    """Read the scale from the `--sp-N: Xpx` declarations."""
    text = TOKENS.read_text(encoding="utf-8")
    return {int(v) for v in re.findall(r"--sp-\d+\s*:\s*(\d+)px", text)}


def _iter_css():
    for path in sorted(ROOT.rglob("*.css")):
        rel = str(path.relative_to(ROOT))
        if any(s.strip("/") in rel for s in _SKIP_DIRS):
            continue
        yield rel, path


def count_off_scale(allowed: set[int]) -> dict[str, int]:
    """Count, per file, how many spacing values are off the scale."""
    counts: dict[str, int] = {}
    for rel, path in _iter_css():
        n = 0
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            for prop in _PROPS:
                for m in re.finditer(rf"\b{prop}[^:]*:\s*([^;}}]+)", line):
                    value = m.group(1)
                    if "var(--" in value or "calc(" in value:
                        continue
                    for raw in re.findall(r"(\d+)px", value):
                        px = int(raw)
                        if px < _IGNORE_BELOW or px in allowed:
                            continue
                        n += 1
        if n:
            counts[rel] = n
    return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--update", action="store_true",
                    help="현재 값으로 baseline 을 다시 쓴다 (줄었을 때만 의미가 있다)")
    args = ap.parse_args(argv)

    allowed = scale()
    if not allowed:
        print(f"스케일을 읽지 못했다: {TOKENS}")
        return 1
    counts = count_off_scale(allowed)
    total = sum(counts.values())

    if args.update:
        BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_PATH.write_text(
            json.dumps(dict(sorted(counts.items())), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
        print(f"baseline 갱신: {len(counts)}개 파일 · 스케일 밖 {total}개")
        return 0

    if not BASELINE_PATH.is_file():
        print(f"baseline 이 없다: {BASELINE_PATH} (--update 로 만든다)")
        return 1

    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    problems = []
    for rel, n in sorted(counts.items()):
        cap = baseline.get(rel, 0)
        if n > cap:
            problems.append(
                f"  {rel}: 스케일 밖 간격이 {cap} → {n} 로 늘었다. "
                f"{sorted(allowed)} 중에서 고르거나 var(--sp-*) 를 쓰세요")

    print(f"간격 스케일 밖 {total}개 · 파일 {len(counts)}개 "
          f"(스케일 {sorted(allowed)})")
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

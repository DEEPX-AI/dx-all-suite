#!/usr/bin/env python3
"""Ratchet that keeps the number of distinct CSS breakpoints going down.

Responsive layouts used to break at many different widths for no reason: one screen
folded at 900 and the next at 960 because each file copied whatever value it found.
New rules pick from SCALE; values outside the scale may only disappear.

Values still outside the scale, and why:

    480   chat-widget    full-screen mobile chat    (no baseline covers 480-600 yet)
    768   five files     mobile -> tablet           (kept on purpose, see below)
    1600  dx_planner     detailed workspace, 2 cols (outside the visual baselines)
    1979  about-deepx    side rail vs 1680 column   (derived, not copied)

480 cannot move until a visual baseline covers the 480-600 range; a move that
cannot be checked does not follow the procedure below.

768 is a shared mobile -> tablet convention across five files. Moving it to 900
swaps one distinct value for another, so the ratchet gains nothing while five
modules change behaviour.

1979 is computed, not copied: it is the narrowest width at which the rail fits in
the gutter next to the 1680 content column (see the comment in about-deepx.css).
Snapping it to the scale makes the rail cover the content between 1440 and 1979.

Before moving a value, ask whether the rule needs a breakpoint at all; a grid such
as `repeat(auto-fit, minmax(280px, 1fr))` folds on its own.

To move a value: change one value at a time, check the render by eye at the
baseline width that covers it (tests/visual shoots 650, 860, 1150 and 1320), then
tighten the baseline with --write.

    python -m scripts.breakpoint_gate            # check
    python -m scripts.breakpoint_gate --write    # tighten the baseline
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "config" / "breakpoint_baseline.json"

# Target scale. New responsive rules pick from these.
SCALE = (600, 900, 1200, 1440)

_MEDIA = re.compile(r"@media([^{]*)\{")
_WIDTH = re.compile(r"(?:max|min)-width:\s*(\d+)px")


def _css_files(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*.css")
        if ".venv" not in p.parts
        and "node_modules" not in p.parts
        and "docs" not in p.parts
    )


def scan(root: Path = ROOT) -> dict[str, list[int]]:
    """File -> the breakpoint values it uses (sorted, deduplicated)."""
    out: dict[str, list[int]] = {}
    for path in _css_files(root):
        found: set[int] = set()
        for query in _MEDIA.findall(path.read_text(encoding="utf-8")):
            found.update(int(v) for v in _WIDTH.findall(query))
        if found:
            out[path.relative_to(root).as_posix()] = sorted(found)
    return dict(sorted(out.items()))


def distinct(counts: dict[str, list[int]]) -> list[int]:
    return sorted({v for vals in counts.values() for v in vals})


def new_values(counts: dict[str, list[int]], baseline: dict[str, list[int]]) -> dict[str, list[int]]:
    """Per file, breakpoints that are neither on the scale nor in that file's baseline.

    Scale values do not add fragmentation, so any file may use them without a
    baseline entry. Contract: tests/test_breakpoint_gate.py
    """
    out: dict[str, list[int]] = {}
    for rel, values in counts.items():
        allowed = set(baseline.get(rel, [])) | set(SCALE)
        new = [v for v in values if v not in allowed]
        if new:
            out[rel] = new
    return out


def main() -> int:
    counts = scan()
    if "--write" in sys.argv:
        BASELINE_PATH.write_text(
            json.dumps(counts, indent=2) + "\n", encoding="utf-8"
        )
        print(
            f"baseline 갱신: 고유 {len(distinct(counts))}개 / {len(counts)} 파일"
        )
        return 0

    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    problems = [
        f"  {rel}: 새 breakpoint {new} — {SCALE} 중에서 고르거나 "
        f"이 파일이 이미 쓰는 값 {sorted(baseline.get(rel, []))} 을 쓰세요"
        for rel, new in new_values(counts, baseline).items()
    ]
    per_file = collections.Counter(len(v) for v in counts.values())
    print(
        f"breakpoint 고유값 {len(distinct(counts))}개 · "
        f"파일당 분포 {dict(sorted(per_file.items()))}"
    )
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

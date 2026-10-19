#!/usr/bin/env python3
"""Ratchet that keeps the number of per-language sibling span groups going down.

Markup that lists one phrase as six language spans keeps the dictionary and the translations in
two places. `scripts/migrate_i18n_spans.py` moved most of them to data-i18n; the rest have two
phrases for one key and need a human decision. The gate only has to stop new ones.

    python -m scripts.i18n_span_gate            # check
    python -m scripts.i18n_span_gate --write    # tighten the baseline
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts.migrate_i18n_spans import _GROUP, _markup_files

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "config" / "i18n_span_baseline.json"

SCAN_ROOTS = (
    "dx_agent_dev",
    "dx_app",
    "dx_benchmark",
    "dx_compiler",
    "dx_edge",
    "dx_modelzoo",
    "dx_monitor",
    "dx_planner",
    "dx_stream",
    "launcher",
    "shared",
)


def count_groups(text: str) -> int:
    return sum(1 for _ in _GROUP.finditer(text))


def scan(root: Path = ROOT) -> dict[str, int]:
    """File with at least one lang-span group -> number of groups."""
    out: dict[str, int] = {}
    for name in SCAN_ROOTS:
        for path in _markup_files(name):
            n = count_groups(path.read_text())
            if n:
                out[path.relative_to(root).as_posix()] = n
    return dict(sorted(out.items()))


def main() -> int:
    counts = scan()
    if "--write" in sys.argv:
        BASELINE_PATH.write_text(
            json.dumps(counts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"baseline 갱신: {sum(counts.values())} groups / {len(counts)} files")
        return 0

    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    over = {r: (n, baseline.get(r, 0)) for r, n in counts.items() if n > baseline.get(r, 0)}
    for rel, (now, allowed) in over.items():
        print(f"OVER  {rel}: {now} > {allowed}")
    print(f"total lang-span groups: {sum(counts.values())}")
    return 1 if over else 0


if __name__ == "__main__":
    raise SystemExit(main())

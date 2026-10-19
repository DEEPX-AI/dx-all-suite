#!/usr/bin/env python3
"""Compare measured coverage against the committed baseline.

Report-only by default (staged rollout): it prints the per-module delta and exits
0 even on a drop. Set DX_COVERAGE_ENFORCE=1 to make a regression fail the build
once the numbers have settled.

Baseline lives in config/coverage_baseline.json and is refreshed with:
    python scripts/coverage_gate.py --update
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "config" / "coverage_baseline.json"
COVERAGE_DATA = ROOT / ".coverage"

# A module may dip this far below baseline without being called a regression —
# branch coverage moves a little with unrelated refactors, and a hair-trigger
# gate teaches people to ignore it.
TOLERANCE_PCT = 0.5


def measured() -> dict[str, float]:
    """Per-module coverage percentages, keyed by top-level package.

    Reads `coverage json`, NOT coverage.xml: .coveragerc declares ten separate
    `source` roots, so every filename in the XML is relative to whichever root it
    came from ("core/models.py" — which module?). The JSON report keeps the full
    repo-relative path, so the module is unambiguous.
    """
    if not COVERAGE_DATA.is_file():
        sys.exit(f"{COVERAGE_DATA.name} not found — run `bash scripts/run_ci.sh --coverage` first")
    proc = subprocess.run(
        [sys.executable, "-m", "coverage", "json", "-o", "-", "-q"],
        cwd=str(ROOT), capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        sys.exit(f"coverage json failed:\n{proc.stderr}")
    data = json.loads(proc.stdout)

    hits: dict[str, list[int]] = {}
    for filename, entry in data["files"].items():
        module = filename.split("/", 1)[0]
        if not module or module.endswith(".py"):
            continue
        summary = entry["summary"]
        acc = hits.setdefault(module, [0, 0])
        acc[0] += summary["covered_lines"]
        acc[1] += summary["num_statements"]
    return {m: (c * 100.0 / t if t else 0.0) for m, (c, t) in sorted(hits.items())}


def main() -> int:
    current = measured()
    if "--update" in sys.argv:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(
            json.dumps({k: round(v, 1) for k, v in current.items()}, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"baseline written: {BASELINE.relative_to(ROOT)}")
        return 0

    if not BASELINE.is_file():
        print(f"no baseline at {BASELINE.relative_to(ROOT)} — create it with --update")
        return 0

    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    regressions = []
    print(f"{'module':<16}{'baseline':>10}{'current':>10}{'delta':>9}")
    for module in sorted(set(base) | set(current)):
        b = base.get(module)
        c = current.get(module)
        if b is None:
            print(f"{module:<16}{'—':>10}{c:>9.1f}%{'  new':>9}")
            continue
        if c is None:
            print(f"{module:<16}{b:>9.1f}%{'—':>10}{'  gone':>9}")
            continue
        delta = c - b
        flag = ""
        if delta < -TOLERANCE_PCT:
            flag = "  DROP"
            regressions.append((module, b, c, delta))
        print(f"{module:<16}{b:>9.1f}%{c:>9.1f}%{delta:>+8.1f}%{flag}")

    if not regressions:
        print("\ncoverage: no regression beyond tolerance")
        return 0

    print(f"\ncoverage REGRESSION in {len(regressions)} module(s):")
    for module, b, c, delta in regressions:
        print(f"  {module}: {b:.1f}% -> {c:.1f}% ({delta:+.1f}%)")
    if os.environ.get("DX_COVERAGE_ENFORCE") == "1":
        print("DX_COVERAGE_ENFORCE=1 — failing the build.")
        return 1
    print("Report-only (set DX_COVERAGE_ENFORCE=1 to enforce).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

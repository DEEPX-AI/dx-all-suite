#!/usr/bin/env python3
"""
migrate_results_to_run_id.py — Migrate legacy flat results/ layout to run-id-keyed.

Before:
    dx-agent-dev/e2e-tests/results/
        20260521_000935_911a91_copilot-cli-autopilot/manifest.json
        20260521_015901_f5c6cd_claude-code-autopilot/manifest.json
        ...   (all runs mixed together)

After:
    dx-agent-dev/e2e-tests/results/
        20260521_135734/                                       ← run_id from state.json
            20260521_174857_e25076_claude-code-autopilot/
        20260520_193327/
            20260520_193327_xxxxxx_claude-code-autopilot/
        legacy/                                                ← unmatched flat sessions
            20260511_194755_d31c86_cursor-cli-autopilot/

Mapping source:
    .deepx/tests/runner_state/<run_id>/state.json
        → tool_states[*].completed[*].result_dir_name

Usage:
    python .deepx/tests/migrate_results_to_run_id.py             # dry-run (default)
    python .deepx/tests/migrate_results_to_run_id.py --apply     # actually move
    python .deepx/tests/migrate_results_to_run_id.py --apply --skip-legacy
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = (SCRIPT_DIR / "../..").resolve()
RESULTS_ROOT = REPO_ROOT / "dx-agent-dev/e2e-tests/results"
RUNNER_STATE_DIR = SCRIPT_DIR / "runner_state"


def build_session_to_run_id_map() -> Dict[str, str]:
    """Read every runner_state/<run_id>/state.json and return {result_dir_name: run_id}."""
    mapping: Dict[str, str] = {}
    if not RUNNER_STATE_DIR.is_dir():
        return mapping
    for state_path in RUNNER_STATE_DIR.glob("*/state.json"):
        if state_path.parent.name == "latest":
            continue
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"WARN: cannot parse {state_path}: {e}", file=sys.stderr)
            continue
        run_id = data.get("run_id") or state_path.parent.name
        for tool_state in (data.get("tool_states") or {}).values():
            for entry in tool_state.get("completed", []):
                rdn = entry.get("result_dir_name")
                if rdn:
                    mapping[rdn] = run_id
    return mapping


def plan_moves(
    mapping: Dict[str, str],
    include_legacy: bool,
) -> Tuple[List[Tuple[Path, Path]], List[Tuple[Path, Path]], List[Path]]:
    """Return (matched_moves, legacy_moves, skipped_existing)."""
    matched: List[Tuple[Path, Path]] = []
    legacy: List[Tuple[Path, Path]] = []
    skipped: List[Path] = []

    if not RESULTS_ROOT.is_dir():
        return matched, legacy, skipped

    for entry in sorted(RESULTS_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        # Skip already-migrated subdirs (run_id directories): they do NOT match
        # the session-id regex (which has "_<tool>-autopilot" suffix).
        if "-autopilot" not in entry.name:
            continue

        run_id = mapping.get(entry.name)
        if run_id:
            dest = RESULTS_ROOT / run_id / entry.name
        elif include_legacy:
            dest = RESULTS_ROOT / "legacy" / entry.name
        else:
            skipped.append(entry)
            continue

        if dest.exists():
            skipped.append(entry)
            continue

        if run_id:
            matched.append((entry, dest))
        else:
            legacy.append((entry, dest))

    return matched, legacy, skipped


def execute_moves(moves: List[Tuple[Path, Path]], dry_run: bool) -> int:
    moved = 0
    for src, dest in moves:
        if dry_run:
            print(f"  WOULD MOVE: {src.name} → {dest.relative_to(RESULTS_ROOT)}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src), str(dest))
                print(f"  MOVED: {src.name} → {dest.relative_to(RESULTS_ROOT)}")
                moved += 1
            except Exception as e:
                print(f"  ERROR moving {src.name}: {e}", file=sys.stderr)
    return moved


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Migrate flat results/ → results/<run_id>/<session>/ layout."
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually move directories (default: dry-run preview only).",
    )
    parser.add_argument(
        "--skip-legacy", action="store_true",
        help="Do not move unmatched sessions into legacy/. They remain flat.",
    )
    args = parser.parse_args(argv)

    if not RESULTS_ROOT.exists():
        print(f"Nothing to do — results/ not found at {RESULTS_ROOT}")
        return 0

    print(f"Results root: {RESULTS_ROOT}")
    print(f"State source: {RUNNER_STATE_DIR}")

    mapping = build_session_to_run_id_map()
    print(f"Loaded {len(mapping)} session→run_id mappings from runner_state/.\n")

    matched, legacy, skipped = plan_moves(mapping, include_legacy=not args.skip_legacy)

    # Group matched moves by run_id for readable preview
    by_run: Dict[str, List[Tuple[Path, Path]]] = defaultdict(list)
    for src, dest in matched:
        by_run[dest.parent.name].append((src, dest))

    print(f"== Matched ({len(matched)} sessions across {len(by_run)} run_ids) ==")
    for run_id in sorted(by_run):
        print(f"  [{run_id}]  {len(by_run[run_id])} session(s)")
    print()

    if legacy:
        print(f"== Legacy / unmatched ({len(legacy)} sessions → results/legacy/) ==")
        for src, _ in legacy[:5]:
            print(f"  {src.name}")
        if len(legacy) > 5:
            print(f"  ... and {len(legacy) - 5} more")
        print()

    if skipped:
        print(f"== Skipped ({len(skipped)} — destination exists or --skip-legacy) ==")
        for s in skipped[:5]:
            print(f"  {s.name}")
        if len(skipped) > 5:
            print(f"  ... and {len(skipped) - 5} more")
        print()

    dry_run = not args.apply
    if dry_run:
        print("(dry-run) Re-run with --apply to execute these moves.\n")
    else:
        print(">>> APPLYING MOVES <<<\n")

    total = execute_moves(matched + legacy, dry_run=dry_run)

    if not dry_run:
        print(f"\nDone. Moved {total} session director{'y' if total == 1 else 'ies'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

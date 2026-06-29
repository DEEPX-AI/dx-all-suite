#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""move_round.py — Transplant a fully-valid completed round across run_ids.

SYNOPSIS
--------
    python move_round.py \\
        --from-run-id   20260615_070604 \\
        --from-round-dir 20260615_082857_d640d1_claude-code-autopilot \\
        --to-run-id     20260612_194959 \\
        [--replace-round-dir 20260612_215242_43cb91_claude-code-autopilot] \\
        [--tool claude-code] \\
        [--no-require-valid] \\
        [--dry-run]

DESIGN NOTES
------------
* Validity precondition (require_valid=True):
    All ``{prefix}__*`` scenario subdirs inside the round dir must classify as
    "valid" (DONE sentinel found) via ``e2e_runner._classify_round_scenario``.
    Any envfail / incomplete / skip verdict causes the move to be refused.

* Analyzer round numbering:
    The analyzer assigns round numbers by AUTOPILOT-DIR TIMESTAMP ORDER (i.e.
    directory names sorted lexicographically), NOT by the ``round`` field in
    state.json.  A transplanted round therefore sorts by its own timestamp —
    which is typically earlier than any round in the destination run.  This is
    expected and documented here; the round number shown in reports will differ
    from the ``round`` field preserved in state.

* Symlinks inside the round dir:
    ``shutil.move`` is used, which preserves symlinks.  The actual artifact
    dirs pointed to by those symlinks are NOT moved — only the round dir shell
    (manifest, SUMMARY.md, scenario subdirs + their internal symlinks) is
    relocated.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path constants (mirrors e2e_runner.py convention)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = (SCRIPT_DIR / "../..").resolve()
DEFAULT_RESULTS_ROOT = REPO_ROOT / "dx-agent-dev/e2e-tests/results"
DEFAULT_STATE_ROOT = SCRIPT_DIR / "runner_state"

# ---------------------------------------------------------------------------
# Tool → scenario-prefix mapping  (mirrors e2e_runner's naming)
# ---------------------------------------------------------------------------
_TOOL_PREFIX: dict[str, str] = {
    "claude-code": "claude_code",
    "copilot-cli": "copilot_cli",
    "cursor-cli": "cursor_cli",
    "opencode-cli": "opencode_cli",
    "codex-cli": "codex_cli",
}


def _tool_prefix(tool: str) -> str:
    """Return the scenario-subdir prefix for *tool* (e.g. 'claude_code')."""
    return _TOOL_PREFIX.get(tool, tool.replace("-", "_"))


# ---------------------------------------------------------------------------
# Import e2e_runner via importlib (avoids sys.path pollution at module level)
# ---------------------------------------------------------------------------
def _load_er():
    """Lazy-import e2e_runner from the same directory as this script."""
    spec = importlib.util.spec_from_file_location(
        "e2e_runner", SCRIPT_DIR / "e2e_runner.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError("Cannot locate e2e_runner.py next to move_round.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


# ---------------------------------------------------------------------------
# Public pure functions
# ---------------------------------------------------------------------------

def round_is_fully_valid(round_dir: Path, prefix: str) -> tuple[bool, dict]:
    """Classify every ``{prefix}__*`` scenario subdir in *round_dir*.

    Parameters
    ----------
    round_dir:
        The round result directory (contains manifest.json + scenario subdirs).
    prefix:
        Tool prefix string, e.g. ``"claude_code"`` for tool ``"claude-code"``.

    Returns
    -------
    (all_valid, verdicts)
        ``all_valid`` is True only if every matched scenario subdir has
        verdict == "valid".  ``verdicts`` is a ``{scenario_name: verdict}``
        dict for every matched subdir (excluding unmatched dirs).
    """
    er = _load_er()
    classify = er._classify_round_scenario

    verdicts: dict[str, str] = {}
    matched = [
        d for d in sorted(round_dir.iterdir())
        if d.is_dir() and d.name.startswith(f"{prefix}__")
    ]
    if not matched:
        return (False, {})

    for scen_dir in matched:
        verdict, _sigs = classify(scen_dir)
        verdicts[scen_dir.name] = verdict

    all_valid = all(v == "valid" for v in verdicts.values())
    return (all_valid, verdicts)


def rewrite_manifest_run_id(round_dir: Path, new_run_id: str) -> None:
    """Overwrite the ``run_id`` field in *round_dir*/manifest.json.

    All other fields and the ``artifacts`` map are preserved verbatim.
    File is written with ``indent=2, ensure_ascii=False``.
    """
    manifest_path = round_dir / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["run_id"] = new_run_id
    manifest_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def state_remove_round(
    state_path: Path, tool: str, result_dir_name: str
) -> Optional[dict]:
    """Remove a completed-round entry from *state_path* and return it.

    Looks for an entry in ``tool_states[tool]["completed"]`` whose
    ``result_dir_name`` field exactly matches *result_dir_name*.  If no exact
    match, falls back to startswith.  Returns the removed entry, or ``None``
    if not found (state is still saved unchanged).
    """
    data = json.loads(state_path.read_text(encoding="utf-8"))
    ts = data.setdefault("tool_states", {}).setdefault(tool, {})
    completed: list[dict] = ts.setdefault("completed", [])

    # Exact match first
    idx = next(
        (i for i, e in enumerate(completed) if e.get("result_dir_name") == result_dir_name),
        None,
    )
    # Fallback: startswith
    if idx is None:
        idx = next(
            (i for i, e in enumerate(completed)
             if e.get("result_dir_name", "").startswith(result_dir_name)),
            None,
        )

    removed: Optional[dict] = None
    if idx is not None:
        removed = completed.pop(idx)

    state_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return removed


def state_add_round(state_path: Path, tool: str, entry: dict) -> None:
    """Append *entry* to ``tool_states[tool]["completed"]`` in *state_path*.

    Creates the ``tool_states[tool]["completed"]`` structure if missing.
    """
    if state_path.exists():
        data = json.loads(state_path.read_text(encoding="utf-8"))
    else:
        data = {}
    ts = data.setdefault("tool_states", {}).setdefault(tool, {})
    ts.setdefault("completed", []).append(entry)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def move_round(
    from_run_id: str,
    from_round_dir: str,
    to_run_id: str,
    *,
    tool: str = "claude-code",
    replace_round_dir: Optional[str] = None,
    results_root: Path = DEFAULT_RESULTS_ROOT,
    state_root: Path = DEFAULT_STATE_ROOT,
    require_valid: bool = True,
) -> dict:
    """Transplant a completed round from one run_id to another.

    Parameters
    ----------
    from_run_id:
        Source run_id (directory name under *results_root*).
    from_round_dir:
        Round directory name (e.g. ``"20260615_082857_d640d1_claude-code-autopilot"``).
    to_run_id:
        Destination run_id.
    tool:
        Tool identifier (default ``"claude-code"``).
    replace_round_dir:
        If given, this round dir under *to_run_id* is removed from the
        filesystem and its state entry is deleted before the move.
    results_root:
        Base directory containing ``<run_id>/<round_dir>/`` trees.
    state_root:
        Base directory containing ``<run_id>/state.json`` files.
    require_valid:
        If True (default), the move is refused when the source round is not
        fully valid (any scenario != "valid").

    Returns
    -------
    A summary dict with keys:
        moved_to, replaced, removed_from_source, scenarios
    On refusal (require_valid=True and round not fully valid):
        Raises ``ValueError`` with a descriptive message.
    """
    prefix = _tool_prefix(tool)

    # -- Resolve source round dir -------------------------------------------
    src_dir = results_root / from_run_id / from_round_dir
    if not src_dir.is_dir():
        raise FileNotFoundError(f"Source round dir not found: {src_dir}")

    # -- Validity check -------------------------------------------------------
    all_valid, verdicts = round_is_fully_valid(src_dir, prefix)
    if require_valid and not all_valid:
        invalid = {k: v for k, v in verdicts.items() if v != "valid"}
        raise ValueError(
            f"Round {from_round_dir!r} is NOT fully valid. "
            f"Refusing move.\nInvalid scenarios: {invalid}"
        )

    # -- State paths ----------------------------------------------------------
    from_state = state_root / from_run_id / "state.json"
    to_state = state_root / to_run_id / "state.json"

    # -- Replace target round (if requested) ----------------------------------
    replaced_info: Optional[str] = None
    if replace_round_dir is not None:
        repl_dir = results_root / to_run_id / replace_round_dir
        # Remove state entry first (so state stays consistent even if rmtree fails)
        if to_state.exists():
            state_remove_round(to_state, tool, replace_round_dir)
        if repl_dir.is_dir():
            shutil.rmtree(repl_dir)
        replaced_info = replace_round_dir

    # -- Move source round dir → destination run_id --------------------------
    dest_run_dir = results_root / to_run_id
    dest_run_dir.mkdir(parents=True, exist_ok=True)
    dest_dir = dest_run_dir / from_round_dir

    shutil.move(str(src_dir), str(dest_dir))

    # -- Rewrite manifest run_id --------------------------------------------
    rewrite_manifest_run_id(dest_dir, to_run_id)

    # -- Update source state -------------------------------------------------
    removed_entry: Optional[dict] = None
    if from_state.exists():
        removed_entry = state_remove_round(from_state, tool, from_round_dir)

    # -- Build new completed entry for destination ---------------------------
    new_entry = dict(removed_entry) if removed_entry else {}
    new_entry["result_dir_name"] = from_round_dir
    # Keep the original round number — the analyzer re-derives by timestamp.

    state_add_round(to_state, tool, new_entry)

    return {
        "moved_to": str(dest_dir),
        "replaced": replaced_info,
        "removed_from_source": str(src_dir),
        "scenarios": verdicts,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="move_round.py",
        description=(
            "Transplant a fully-valid completed round from one run_id to another.\n\n"
            "Results live at:\n"
            "  <results_root>/<run_id>/<round_dir>/\n\n"
            "State files live at:\n"
            "  <state_root>/<run_id>/state.json\n\n"
            "NOTE: The analyzer orders rounds by AUTOPILOT-DIR TIMESTAMP (lexicographic\n"
            "directory order), NOT by the 'round' field in state.json.  A transplanted\n"
            "round will therefore appear at the position determined by its own timestamp."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--from-run-id", required=True, metavar="RUN_ID",
                   help="Source run_id (directory under results_root)")
    p.add_argument("--from-round-dir", required=True, metavar="ROUND_DIR",
                   help="Round directory name to transplant")
    p.add_argument("--to-run-id", required=True, metavar="RUN_ID",
                   help="Destination run_id")
    p.add_argument("--tool", default="claude-code", metavar="TOOL",
                   help="Tool identifier (default: claude-code)")
    p.add_argument("--replace-round-dir", default=None, metavar="ROUND_DIR",
                   help="Round dir under to_run_id to remove before transplanting")
    p.add_argument("--require-valid", dest="require_valid",
                   action="store_true", default=True,
                   help="Refuse move if source round is not fully valid (default ON)")
    p.add_argument("--no-require-valid", dest="require_valid",
                   action="store_false",
                   help="Skip validity check (allow moving incomplete rounds)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print intended actions; change nothing")
    p.add_argument("--results-root", default=None, metavar="PATH",
                   help=f"Override results root (default: {DEFAULT_RESULTS_ROOT})")
    p.add_argument("--state-root", default=None, metavar="PATH",
                   help=f"Override runner_state root (default: {DEFAULT_STATE_ROOT})")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    results_root = Path(args.results_root) if args.results_root else DEFAULT_RESULTS_ROOT
    state_root = Path(args.state_root) if args.state_root else DEFAULT_STATE_ROOT

    prefix = _tool_prefix(args.tool)
    src_dir = results_root / args.from_run_id / args.from_round_dir
    dest_dir = results_root / args.to_run_id / args.from_round_dir
    from_state = state_root / args.from_run_id / "state.json"
    to_state = state_root / args.to_run_id / "state.json"

    print(f"move_round.py — cross-run-id round transplant")
    print(f"  tool         : {args.tool}  (prefix: {prefix})")
    print(f"  from_run_id  : {args.from_run_id}")
    print(f"  from_round   : {args.from_round_dir}")
    print(f"  to_run_id    : {args.to_run_id}")
    if args.replace_round_dir:
        print(f"  replace      : {args.replace_round_dir}")
    print(f"  require_valid: {args.require_valid}")
    print(f"  dry_run      : {args.dry_run}")
    print()

    # -- Source dir check ----------------------------------------------------
    if not src_dir.is_dir():
        print(f"[ERROR] Source round dir not found:\n  {src_dir}", file=sys.stderr)
        return 1

    # -- Validity check -------------------------------------------------------
    print("[CHECK] Classifying source round scenarios …")
    all_valid, verdicts = round_is_fully_valid(src_dir, prefix)
    if verdicts:
        for scen, v in sorted(verdicts.items()):
            mark = "OK" if v == "valid" else "!!"
            print(f"  [{mark}]  {scen}: {v}")
    else:
        print(f"  (no '{prefix}__*' scenario subdirs found in {src_dir.name})")
    print(f"  → all_valid={all_valid}")
    print()

    if args.require_valid and not all_valid:
        invalid = {k: v for k, v in verdicts.items() if v != "valid"}
        sys.stdout.flush()
        print("[BLOCKED] Source round is NOT fully valid.", file=sys.stderr)
        print(f"  Invalid scenarios: {invalid}", file=sys.stderr)
        print("  Use --no-require-valid to force (not recommended).", file=sys.stderr)
        sys.stderr.flush()
        return 2

    if args.dry_run:
        print("[DRY-RUN] The following actions WOULD be performed (nothing changed):")
        if args.replace_round_dir:
            repl_dir = results_root / args.to_run_id / args.replace_round_dir
            print(f"  1. state_remove_round({to_state}, {args.tool!r}, {args.replace_round_dir!r})")
            print(f"  2. shutil.rmtree({repl_dir})")
        else:
            print("  1. (no replacement round)")
        print(f"  3. shutil.move({src_dir}, {dest_dir})")
        print(f"  4. rewrite_manifest_run_id({dest_dir}/manifest.json, {args.to_run_id!r})")
        print(f"  5. state_remove_round({from_state}, {args.tool!r}, {args.from_round_dir!r})")
        print(f"  6. state_add_round({to_state}, {args.tool!r}, <entry with round kept, result_dir_name={args.from_round_dir!r}>)")
        print()
        print("[DRY-RUN] No files modified. Exiting.")
        return 0

    # -- Execute --------------------------------------------------------------
    try:
        summary = move_round(
            from_run_id=args.from_run_id,
            from_round_dir=args.from_round_dir,
            to_run_id=args.to_run_id,
            tool=args.tool,
            replace_round_dir=args.replace_round_dir,
            results_root=results_root,
            state_root=state_root,
            require_valid=args.require_valid,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print("[DONE] Round transplant complete.")
    print(f"  moved_to            : {summary['moved_to']}")
    print(f"  replaced            : {summary['replaced']}")
    print(f"  removed_from_source : {summary['removed_from_source']}")
    print(f"  scenarios           : {summary['scenarios']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

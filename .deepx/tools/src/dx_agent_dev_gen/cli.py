"""CLI entry point for dx-agent-gen."""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

from . import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dx-agent-gen",
        description="DEEPX Agent-Driven Development Platform Generator",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    # generate
    gen_parser = sub.add_parser("generate", help="Generate platform files from .deepx/ canonical source")
    gen_parser.add_argument(
        "--platform",
        choices=["copilot", "claude", "opencode", "cursor", "instructions", "all"],
        default="all",
        help="Platform to generate (default: all)",
    )
    gen_parser.add_argument(
        "--repo",
        type=Path,
        default=Path("."),
        help="Repository root path (default: current directory)",
    )
    gen_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing files",
    )
    gen_parser.add_argument(
        "--prune",
        action="store_true",
        help="After generating, remove stale orphan outputs (renamed/removed sources). "
        "Hand-authored files are never touched. Honors --dry-run.",
    )

    # prune
    prune_parser = sub.add_parser(
        "prune",
        help="Remove stale generator outputs (orphans) with no current .deepx/ source",
    )
    prune_parser.add_argument(
        "--platform",
        choices=["copilot", "claude", "opencode", "cursor", "instructions", "all"],
        default="all",
    )
    prune_parser.add_argument(
        "--repo",
        type=Path,
        default=Path("."),
    )
    prune_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be pruned without deleting",
    )

    # check
    chk_parser = sub.add_parser("check", help="Check if generated files are up-to-date")
    chk_parser.add_argument(
        "--platform",
        choices=["copilot", "claude", "opencode", "cursor", "instructions", "all"],
        default="all",
    )
    chk_parser.add_argument(
        "--repo",
        type=Path,
        default=Path("."),
    )

    # lint
    lint_parser = sub.add_parser(
        "lint",
        help="Check EN/KO fragment parity (pair existence + structural marker sync)",
    )
    lint_parser.add_argument(
        "--repo",
        type=Path,
        default=Path("."),
        help="Repository root path (default: current directory)",
    )

    args = parser.parse_args(argv)
    repo = args.repo.resolve()

    if not (repo / ".deepx").is_dir():
        # lint can still run if fragments are found in a parent; use cwd
        if args.command != "lint":
            print(f"ERROR: {repo} does not contain .deepx/ directory", file=sys.stderr)
            return 1

    try:
        return _dispatch(args, repo)
    except Exception as e:  # noqa: BLE001
        # Anything outside the documented RuntimeError contract (drift = 1,
        # `error: <msg>` = 1) is a TOOL failure — e.g. an import-time TypeError
        # on an old interpreter. Exit 2 so callers (subrepo_check.sh, run_all.sh)
        # never mistake it for drift; keep the traceback for debugging.
        print(f"error: internal failure ({type(e).__name__}): {e}", file=sys.stderr)
        traceback.print_exc()
        return 2


def _dispatch(args: argparse.Namespace, repo: Path) -> int:
    from .generator import Generator

    gen = Generator(repo)

    if args.command == "generate":
        try:
            results = gen.generate(platform=args.platform, dry_run=args.dry_run)
        except RuntimeError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        if args.dry_run:
            for path, action in results.items():
                print(f"  {action}: {path}")
            print(f"\n{len(results)} files would be generated.")
        else:
            print(f"Generated {len(results)} files.")
        if getattr(args, "prune", False):
            removed, report = gen.prune(platform=args.platform, dry_run=args.dry_run)
            for line in report:
                print(f"  {line}")
            verb = "would be pruned" if args.dry_run else "pruned"
            print(f"{len(removed)} orphan file(s)/dir(s) {verb}.")
        return 0

    elif args.command == "prune":
        removed, report = gen.prune(platform=args.platform, dry_run=args.dry_run)
        for line in report:
            print(line)
        verb = "would be pruned" if args.dry_run else "pruned"
        print(f"{len(removed)} orphan file(s)/dir(s) {verb}.")
        return 0

    elif args.command == "check":
        try:
            clean, report = gen.check(platform=args.platform)
        except RuntimeError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        for line in report:
            print(line)
        return 0 if clean else 1

    elif args.command == "lint":
        clean, report = gen.lint()
        for line in report:
            print(line)
        return 0 if clean else 1

    return 0

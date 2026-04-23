"""CLI entry point for dx-agentic-gen."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dx-agentic-gen",
        description="DEEPX Agentic Development Platform Generator",
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

    args = parser.parse_args(argv)
    repo = args.repo.resolve()

    if not (repo / ".deepx").is_dir():
        print(f"ERROR: {repo} does not contain .deepx/ directory", file=sys.stderr)
        return 1

    from .generator import Generator

    gen = Generator(repo)

    if args.command == "generate":
        results = gen.generate(platform=args.platform, dry_run=args.dry_run)
        if args.dry_run:
            for path, action in results.items():
                print(f"  {action}: {path}")
            print(f"\n{len(results)} files would be generated.")
        else:
            print(f"Generated {len(results)} files.")
        return 0

    elif args.command == "check":
        clean, report = gen.check(platform=args.platform)
        for line in report:
            print(line)
        return 0 if clean else 1

    return 0

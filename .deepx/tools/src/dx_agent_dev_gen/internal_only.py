# SPDX-License-Identifier: Apache-2.0
"""Internal-only (hand-authored, release-excluded) platform files.

Internal repos carry hand-authored `.github/agents/*.md` (e.g. copilot-pr-review.md,
dx_stream's dxr-* review agents) that are listed in `.github/release-excluded` and
never reach the public github.com export. They have no `.deepx/agents/` source and
no AUTO-GENERATED header, so generator-parity checks must skip them.
"""

from __future__ import annotations

from pathlib import Path

AUTO_GENERATED_MARK = "<!-- AUTO-GENERATED"


def release_excluded_paths(repo: Path) -> set[str]:
    """Repo-relative paths listed in .github/release-excluded (empty set if absent)."""
    f = repo / ".github" / "release-excluded"
    if not f.is_file():
        return set()
    out: set[str] = set()
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(line.rstrip("/"))
    return out


def is_internal_only_agent(repo: Path, path: Path) -> bool:
    """True for a .github/agents file that is release-excluded OR hand-authored
    (no AUTO-GENERATED header and no .deepx/agents/<stem>.md source)."""
    rel = path.relative_to(repo).as_posix()
    if rel in release_excluded_paths(repo):
        return True
    stem = path.name
    if stem.endswith(".agent.md"):
        stem = stem[: -len(".agent.md")]
    elif stem.endswith(".md"):
        stem = stem[: -len(".md")]
    has_source = (repo / ".deepx" / "agents" / f"{stem}.md").is_file()
    try:
        has_header = AUTO_GENERATED_MARK in path.read_text(encoding="utf-8")[:4000]
    except OSError:
        has_header = False
    return not has_source and not has_header

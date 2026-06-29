# SPDX-License-Identifier: Apache-2.0
"""Output-Isolation guard for showcase reproducibility runs.

The Output-Isolation HARD GATE requires every agent-generated file to live under a
``dx-agent-dev/<session_id>/`` directory. A run that writes anywhere else in the
tracked source tree (e.g. straight into ``dx-agent-dev-showcase/<name>/``) is a
violation — it pollutes / overwrites committed ground truth.

These pure helpers diff two ``git status --porcelain`` snapshots (before vs after a
run) and report violating paths, so the driver can mark the cell FAILED and revert.
They take plain strings so they unit-test without a git repo.
"""
from __future__ import annotations

from typing import List, Set, Tuple

# submodule pointer churn we never treat as agent pollution
_IGNORE_EXACT = {"dx-compiler", "dx-runtime"}


def parse_status(porcelain: str) -> Set[Tuple[str, str]]:
    """Parse ``git status --porcelain`` into a set of (code, path).

    Porcelain line = 2-char status + space + path. Handles untracked ('??').
    Rename ('R  old -> new') keeps the new path.
    """
    out: Set[Tuple[str, str]] = set()
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        code, path = line[:2], line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        out.add((code, path))
    return out


def is_sanctioned(path: str) -> bool:
    """A path is sanctioned iff it lives under a ``dx-agent-dev/`` output dir.

    Note ``dx-agent-dev-showcase/`` is NOT sanctioned — it is a committed source dir,
    and its path component is ``dx-agent-dev-showcase`` (no ``/dx-agent-dev/`` segment).
    """
    if path in _IGNORE_EXACT:
        return True
    return "/dx-agent-dev/" in ("/" + path)


def isolation_violations(before_porcelain: str, after_porcelain: str) -> List[str]:
    """Paths newly changed by a run that are NOT under a dx-agent-dev/ output dir."""
    before_paths = {p for _, p in parse_status(before_porcelain)}
    after = parse_status(after_porcelain)
    violations = []
    for _code, path in sorted(after):
        if path in before_paths:
            continue  # pre-existing change (e.g. operator edits) — not this run's doing
        if is_sanctioned(path):
            continue
        violations.append(path)
    return violations

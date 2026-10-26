# SPDX-License-Identifier: Apache-2.0
"""Filesystem integrity of documentation trees scanned by conformance tests.

Root cause (2026-09-04): dx_stream shipped docs/source/docs/RELEASE_NOTES.md as a
*symlink whose target is the literal string* `--8<-- "RELEASE_NOTES.md"` (a
pymdownx.snippets directive mistaken for a link target). Every test that
rglob()s docs and read_text()s crashed with FileNotFoundError. This test names
the offending path instead of letting 3 unrelated tests explode.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import PROJECT_ROOTS

DOC_DIRS = ("docs", "source", ".deepx")


def _broken_symlinks(root: Path) -> list[str]:
    out: list[str] = []
    for sub in DOC_DIRS:
        base = root / sub
        if base.is_symlink() and not base.exists():
            out.append(f"{sub} -> {str(base.readlink())!r}")
            continue
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_symlink() and not p.exists():
                out.append(f"{p.relative_to(root)} -> {str(p.readlink())!r}")
    return sorted(out)


@pytest.mark.parametrize("project,root", list(PROJECT_ROOTS.items()), ids=list(PROJECT_ROOTS))
def test_no_broken_symlinks_in_docs(project: str, root: Path):
    broken = _broken_symlinks(root)
    assert not broken, (
        f"{project}: broken symlink(s) in documentation tree — replace with a regular "
        f"file (for a mkdocs snippet include, the FILE CONTENT should be the "
        f"`--8<-- \"...\"` line):\n  " + "\n  ".join(broken)
    )

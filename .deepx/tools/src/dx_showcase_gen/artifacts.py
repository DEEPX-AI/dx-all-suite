"""Copy a build session's generated files into the showcase dir + portability scan.

Skips heavy binaries / environments (venv, *.pt, *.onnx, *.dxnn, __pycache__) that
should not be committed, and flags absolute / session-specific path references the
agent must make portable before the showcase can run standalone.
``scan_nonportable`` scans .py, .sh, and .json files — the ppe regression showed that
absolute build-session paths can leak into committed data files (*.json) too.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Dict, List

# Files/dirs never copied into a showcase (binaries, envs, caches).
SKIP_NAMES = {"venv", "__pycache__", ".git"}
SKIP_SUFFIXES = {".pt", ".onnx", ".dxnn", ".engine", ".mp4", ".mkv", ".pyc"}

# Path patterns that break portability if they appear in a copied script.
NONPORTABLE = [
    re.compile(r"/tmp/"),
    re.compile(r"/data/home/"),
    re.compile(r"/home/\w+/"),
    re.compile(r"dx-agent-dev/\d{8}-\d{6}_"),   # a specific session dir
]

# Strict set for the verify GATE: only the unambiguous relocatability killers — a build
# session dir (points into a vanished build worktree) and /tmp paths. Dataset / current-
# worktree absolute paths in committed result files are recorded metadata, not load-bearing,
# so the gate does not flag them (the broad NONPORTABLE set still does, at copy time).
NONPORTABLE_STRICT = [
    re.compile(r"dx-agent-dev/\d{8}-\d{6}_"),
    re.compile(r"/tmp/"),
]

# Directory components that are run artifacts / envs — never scanned for portability.
_EPHEMERAL_DIR_PARTS = {"venv", ".venv", "__pycache__", ".git", "node_modules"}


def _skip(p: Path) -> bool:
    return p.name in SKIP_NAMES or p.suffix in SKIP_SUFFIXES


def copy_session_artifacts(session_dir: str, showcase_dir: str,
                           include: List[str] | None = None) -> Dict[str, list]:
    """Copy session files → showcase dir. Returns {'copied':[...], 'skipped':[...]}."""
    src = Path(session_dir)
    dst = Path(showcase_dir)
    dst.mkdir(parents=True, exist_ok=True)
    copied, skipped = [], []
    names = include or [c.name for c in src.iterdir()]
    for name in names:
        sp = src / name
        if not sp.exists() or _skip(sp):
            skipped.append(name)
            continue
        dp = dst / name
        if sp.is_dir():
            # copy a dir but prune skip-listed children
            shutil.copytree(sp, dp, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(*SKIP_NAMES,
                                                          *(f"*{s}" for s in SKIP_SUFFIXES)))
        else:
            shutil.copy2(sp, dp)
        copied.append(name)
    return {"copied": copied, "skipped": skipped}


def scan_nonportable(showcase_dir: str, strict: bool = False) -> List[Dict[str, str]]:
    """Flag absolute / session-specific path refs in scripts for the agent to fix.

    ``strict=True`` (used by the verify GATE) checks only the unambiguous
    relocatability killers: build-session dir paths and ``/tmp/`` refs.  Dataset
    paths and current-worktree absolute paths recorded in committed result files
    are recorded metadata, not load-bearing — the gate ignores them.

    ``strict=False`` (default, used at copy time) applies the broader
    ``NONPORTABLE`` set including ``/data/home/`` and ``/home/<user>/`` patterns.

    Either mode silently skips files inside ephemeral directory components
    (``venv``, ``.venv``, ``__pycache__``, ``.git``, ``node_modules``).
    """
    patterns = NONPORTABLE_STRICT if strict else NONPORTABLE
    flags: List[Dict[str, str]] = []
    for p in Path(showcase_dir).rglob("*"):
        if p.is_dir() or p.suffix not in {".py", ".sh", ".json"}:
            continue
        if any(part in _EPHEMERAL_DIR_PARTS for part in p.parts):
            continue
        try:
            text = p.read_text(errors="replace")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for pat in patterns:
                if pat.search(line):
                    flags.append({"file": str(p), "line": str(i),
                                  "text": line.strip()[:120]})
                    break
    return flags

# SPDX-License-Identifier: Apache-2.0
"""Each sub-repo's `.deepx/scripts/validate_framework.py` must treat a `.deepx/...`
reference that contains glob characters (e.g. `.deepx/skills/*/SKILL.md` in the
`.deepx/README*.md` directory descriptions) as a pattern — PASS when it matches
at least one file — not as a literal path that "does not exist".

Before 2026-09-08 this false positive made the dx_app validator exit 1 (2 FAIL)
and the dx-runtime validator report `routing_paths` FAIL, which surfaced as a
`WARNING: validate_framework.py reported failures` in every green subrepo-gate run.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import COMPILER_ROOT, RUNTIME_ROOT, APP_ROOT, STREAM_ROOT

CASES = [
    ("compiler", COMPILER_ROOT, True),
    ("runtime", RUNTIME_ROOT, False),   # pre-existing model_consistency content mismatch — rc not asserted
    ("app", APP_ROOT, True),
    ("stream", STREAM_ROOT, True),
]
GLOB_FAILURE = re.compile(r"(does not exist|FAIL|Broken reference|matches no files).*\*")


def _run_validator(root: Path) -> subprocess.CompletedProcess:
    script = root / ".deepx" / "scripts" / "validate_framework.py"
    if not script.is_file():
        pytest.skip(f"{script} absent")
    # -v prints per-check lines on validators that support it; fall back silently otherwise
    r = subprocess.run([sys.executable, str(script), "-v"], cwd=root, text=True, capture_output=True, timeout=300)
    if r.returncode == 2 and "unrecognized arguments" in (r.stderr + r.stdout):
        r = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True, timeout=300)
    return r


@pytest.mark.parametrize("label,root,expect_rc0", CASES, ids=[c[0] for c in CASES])
def test_validator_does_not_flag_glob_references(label, root, expect_rc0):
    if not (root / ".deepx").is_dir():
        pytest.skip(f"{label}: .deepx absent")
    r = _run_validator(root)
    out = r.stdout + r.stderr
    hits = [l.strip() for l in out.splitlines() if GLOB_FAILURE.search(l)]
    assert not hits, f"{label}: validator reports glob reference(s) as missing:\n" + "\n".join(hits)
    if expect_rc0:
        assert r.returncode == 0, f"{label}: validate_framework.py exit {r.returncode}\n{out[-1500:]}"

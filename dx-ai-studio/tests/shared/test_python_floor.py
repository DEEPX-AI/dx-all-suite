"""pyproject says requires-python >= 3.8, so runtime code must not use the 3.9+ string APIs.

vermin (stdlib and syntax check) passes for 3.8 but misses `str.removesuffix` on a variable, since it cannot know
the type. Those two methods are blocked separately. Ubuntu 20.04 ships Python 3.8."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = {".venv", "var", "tests", "scripts", "tools", "node_modules"}


def test_runtime_code_runs_on_the_declared_python_floor():
    assert 'requires-python = ">=3.8"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    offenders = []
    for p in ROOT.rglob("*.py"):
        if SKIP & set(p.relative_to(ROOT).parts):
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\.remove(suffix|prefix)\(", line):
                offenders.append(f"{p.relative_to(ROOT)}:{i}")
    assert offenders == [], "Python 3.9+ API: " + ", ".join(offenders)

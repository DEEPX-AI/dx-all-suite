# SPDX-License-Identifier: Apache-2.0
"""
Python 3.8 floor guards for the dx-agent-dev gates.

GHES self-hosted runners in the ASIC pool run Ubuntu 20.04 whose system
`python3` is 3.8. Run 982 (dx-compiler `subrepo-gate`, 2026-09-10) died at
import time with ``TypeError: 'type' object is not subscriptable`` because
`constants.py` — the only generator module without
``from __future__ import annotations`` — evaluates ``dict[str, list[str]]``
at module level. These tests keep the generator (and the test code the suite
gate runs) importable/runnable on 3.8:

* every generator module defers annotation evaluation (PEP 563);
* no 3.9-only str/Path APIs in the generator;
* `pyproject.toml` declares the real floor (3.8);
* gate test code does not use ``dict | dict`` (3.9+);
* when a `python3.8` interpreter with jinja2/pyyaml is on PATH, the generator
  actually imports under it.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest


def _suite_root(start: Path) -> Path:
    cur = start.resolve()
    marker = Path(".deepx") / "tools" / "src" / "dx_agent_dev_gen" / "cli.py"
    for _ in range(10):
        if (cur / marker).is_file():
            return cur
        cur = cur.parent
    raise RuntimeError("suite root not found")


SUITE = _suite_root(Path(__file__))
SRC = SUITE / ".deepx" / "tools" / "src"
PKG = SRC / "dx_agent_dev_gen"
FUTURE_IMPORT = "from __future__ import annotations"
MODULES = sorted(p for p in PKG.glob("*.py") if p.name != "__init__.py")

# str.removeprefix/removesuffix and Path.is_relative_to are 3.9+.
PY39_ONLY_API = re.compile(r"\.(is_relative_to|removeprefix|removesuffix)\(")

# `{...} | {...}` dict union is 3.9+. Opt out per line with `# py38-ok`.
# ... on one line, or as a continuation line `    | {...}` under a dict literal.
DICT_UNION = re.compile(r"\}\s*\|\s*\{|^\s*\|\s*\{")  # py38-ok
GATE_TEST_DIRS = (".deepx/tests", ".deepx/tools/tests", ".deepx/e2e/tests")


@pytest.mark.parametrize("mod", MODULES, ids=lambda p: p.name)
def test_every_generator_module_defers_annotations(mod: Path):
    assert FUTURE_IMPORT in mod.read_text(encoding="utf-8"), (
        f"{mod.relative_to(SUITE)} lacks `{FUTURE_IMPORT}` — module/class-level "
        "PEP 585/604 annotations are evaluated at import on Python 3.8"
    )


def test_no_py39_only_apis_in_generator():
    hits = []
    for p in PKG.glob("*.py"):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if PY39_ONLY_API.search(line):
                hits.append(f"{p.relative_to(SUITE)}:{i}: {line.strip()}")
    assert hits == [], "3.9-only APIs in the generator:\n" + "\n".join(hits)


def test_pyproject_requires_python_floor_is_3_8():
    text = (SUITE / ".deepx" / "tools" / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'requires-python\s*=\s*">=\s*3\.(\d+)"', text)
    assert m, "pyproject.toml must declare requires-python = \">=3.X\""
    assert int(m.group(1)) == 8, f"requires-python floor is 3.{m.group(1)}, expected 3.8"


def test_no_dict_union_operator_in_gate_test_code():
    hits = []
    for d in GATE_TEST_DIRS:
        for p in (SUITE / d).rglob("*.py"):
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if DICT_UNION.search(line) and "py38-ok" not in line:
                    hits.append(f"{p.relative_to(SUITE)}:{i}: {line.strip()}")
    assert hits == [], (
        "`dict | dict` is Python 3.9+; use {**a, **b} (or mark the line `# py38-ok` "
        "if it is not a dict union):\n" + "\n".join(hits)
    )


# GHES self-hosted runners: Ubuntu 20.04 = git 2.25 (no initial-branch option on init) and
# Python 3.8.10 (no tarfile `filter=` — backported only to 3.8.17+; a newer local 3.8 hides it).
OLD_RUNNER_HAZARDS = (
    (re.compile(r'"init",\s*(?:"-q",\s*)?"(?:-b|--initial-branch)"|git init[^\n]*\s(?:-b|--initial-branch)\b'),
     "`git init -b/--initial-branch` needs git >= 2.28 — use `git init` + `git symbolic-ref HEAD refs/heads/<b>`"),  # py38-ok
    (re.compile(r"extractall\([^)\n]*filter="),
     "tarfile.extractall(filter=...) needs 3.12 / 3.8.17+ — guard with `if hasattr(tarfile, 'data_filter')`"),  # py38-ok
)


def test_no_constructs_that_break_on_the_old_runner_image():
    hits = []
    for d in GATE_TEST_DIRS:
        for p in (SUITE / d).rglob("*.py"):
            text = p.read_text(encoding="utf-8")
            for i, line in enumerate(text.splitlines(), 1):
                if "py38-ok" in line:
                    continue
                for rx, why in OLD_RUNNER_HAZARDS:
                    if rx.search(line):
                        # an extractall guarded in the same file by hasattr(tarfile, "data_filter") is fine
                        if "extractall" in line and 'hasattr(tarfile, "data_filter")' in text:
                            continue
                        hits.append(f"{p.relative_to(SUITE)}:{i}: {line.strip()}  <- {why}")
    assert hits == [], "constructs that fail on the GHES runner image (git 2.25 / python 3.8.10):\n" + "\n".join(hits)


def _python38_with_deps() -> str | None:
    py = shutil.which("python3.8")
    if not py:
        return None
    r = subprocess.run([py, "-c", "import jinja2, yaml"], capture_output=True, text=True)
    return py if r.returncode == 0 else None


PY38 = _python38_with_deps()


@pytest.mark.skipif(PY38 is None, reason="no python3.8 with jinja2/pyyaml on PATH")
def test_generator_imports_and_checks_under_python38(tmp_path):
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    r = subprocess.run(
        [PY38, "-c", "import dx_agent_dev_gen.cli, dx_agent_dev_gen.generator, dx_agent_dev_gen.counts"],
        env=env, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"generator does not import under {PY38}:\n{r.stderr}"
    r = subprocess.run(
        [PY38, "-c", "import sys; from dx_agent_dev_gen.cli import main; sys.exit(main(sys.argv[1:]))",
         "check", "--repo", str(SUITE / "dx-compiler")],
        env=env, capture_output=True, text=True, cwd=SUITE,
    )
    assert "Traceback" not in r.stderr, r.stderr
    assert r.returncode in (0, 1), f"check crashed under {PY38} (rc={r.returncode}):\n{r.stderr}"

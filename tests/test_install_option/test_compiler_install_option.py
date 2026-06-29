"""
dx-compiler install.sh --pypi option tests.

Runs install.sh directly on the host (no Docker) and verifies that
--pypi=false is accepted and succeeds. --pypi=true requires public PyPI
access and is intentionally not exercised in offline/CI runs.
"""

import subprocess
from pathlib import Path

import pytest

pytestmark = [pytest.mark.install_option, pytest.mark.compiler]

COMPILER_DIR = Path(__file__).resolve().parents[2] / "dx-compiler"
TIMEOUT = 3600

CASES = [
    ("pypi-false", ["--pypi=false"]),
]


@pytest.mark.parametrize("case_id,args", CASES, ids=[c[0] for c in CASES])
def test_compiler_install_option(case_id, args):
    """Run dx-compiler/install.sh with the given option and expect success."""
    result = subprocess.run(
        ["./install.sh", *args],
        cwd=str(COMPILER_DIR),
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, (
        f"install.sh {' '.join(args)} failed (exit {result.returncode})\n{output}"
    )

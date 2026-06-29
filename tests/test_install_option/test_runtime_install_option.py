"""
dx-runtime install.sh option tests.

Runs install.sh directly on the host (no Docker) and verifies that each
option combination succeeds and produces expected output.

The --exclude-* tests additionally assert that the corresponding "SKIP"
line appears in stdout so we know the flag was actually honoured.
"""

import subprocess
from pathlib import Path

import pytest

pytestmark = [pytest.mark.install_option, pytest.mark.runtime]

RUNTIME_DIR = Path(__file__).resolve().parents[2] / "dx-runtime"
TIMEOUT = 3600

# (case_id, args, expected_skip_pattern_or_None)
CASES = [
    ("runtime-only",
     ["--runtime-only"],
     None),
    ("all-exclude-all",
     ["--all", "--exclude-driver", "--exclude-fw", "--exclude-app", "--exclude-stream"],
     None),
    ("target-fw-app-exclude-app",
     ["--target=dx_fw,dx_app", "--exclude-app"],
     "Skipping dx_app"),
    ("target-fw-stream-exclude-stream",
     ["--target=dx_fw,dx_stream", "--exclude-stream"],
     "Skipping dx_stream"),
    ("target-rt-stream-exclude-rt",
     ["--target=dx_rt,dx_stream", "--exclude-rt"],
     "Skipping dx_rt"),
]


@pytest.mark.parametrize(
    "case_id,args,skip_pattern",
    CASES,
    ids=[c[0] for c in CASES],
)
def test_runtime_install_option(case_id, args, skip_pattern):
    """Run dx-runtime/install.sh with the given option and expect success."""
    result = subprocess.run(
        ["./install.sh", *args],
        cwd=str(RUNTIME_DIR),
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, (
        f"install.sh {' '.join(args)} failed (exit {result.returncode})\n{output}"
    )
    if skip_pattern:
        assert skip_pattern in output, (
            f"Expected '{skip_pattern}' in output but not found.\n{output}"
        )

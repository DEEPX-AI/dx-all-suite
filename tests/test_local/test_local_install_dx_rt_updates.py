"""
Local Install dx-rt driver/runtime Update Tests for dx-all-suite

Runs dx-runtime install targets on the host after local install build.
"""

import pytest
import subprocess
import sys
from pathlib import Path

pytestmark = pytest.mark.local

PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
TEST_TIMEOUT = 1800  # 30 minutes per install


def _run_install(cmd, label):
    banner = (
        f"\n{'=' * 80}\n"
        f"🚀 {label}\n"
        f"{'=' * 80}\n"
    )
    print(banner, file=sys.stdout, flush=True)
    print(banner, file=sys.stderr, flush=True)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=PROJECT_ROOT,
    )

    output_lines = []
    for line in process.stdout:
        print(line, end="", file=sys.stdout, flush=True)
        print(line, end="", file=sys.stderr, flush=True)
        output_lines.append(line.rstrip())

    process.wait(timeout=TEST_TIMEOUT)

    summary = f"\n{'=' * 80}\n"
    if process.returncode == 0:
        summary += f"✅ {label} succeeded\n"
    else:
        summary += f"❌ {label} failed (exit code: {process.returncode})\n"
    summary += f"{'=' * 80}\n"
    print(summary, file=sys.stdout, flush=True)
    print(summary, file=sys.stderr, flush=True)

    return subprocess.CompletedProcess(
        args=cmd,
        returncode=process.returncode,
        stdout="\n".join(output_lines),
        stderr=None,
    )


class TestLocalInstallDxRtUpdates:
    """Install driver/runtime on host after build."""

    def test_install_1_dx_rt_npu_linux_driver(self):
        cmd = ["./dx-runtime/install.sh", "--target=dx_rt_npu_linux_driver"]
        result = _run_install(cmd, "Installing dx_rt_npu_linux_driver")
        if result.returncode != 0:
            pytest.fail(
                "\n".join(
                    [
                        "",
                        "=" * 80,
                        "DX-RT DRIVER INSTALL FAILED",
                        "=" * 80,
                        f"Exit Code: {result.returncode}",
                        f"Command: {' '.join(cmd)}",
                        "",
                        "STDOUT:",
                        "-" * 80,
                        result.stdout or "(no stdout)",
                        "-" * 80,
                        "",
                    ]
                )
            )

    def test_install_2_dx_rt(self):
        cmd = ["./dx-runtime/install.sh", "--target=dx_rt"]
        result = _run_install(cmd, "Installing dx_rt")
        if result.returncode != 0:
            pytest.fail(
                "\n".join(
                    [
                        "",
                        "=" * 80,
                        "DX-RT INSTALL FAILED",
                        "=" * 80,
                        f"Exit Code: {result.returncode}",
                        f"Command: {' '.join(cmd)}",
                        "",
                        "STDOUT:",
                        "-" * 80,
                        result.stdout or "(no stdout)",
                        "-" * 80,
                        "",
                    ]
                )
            )

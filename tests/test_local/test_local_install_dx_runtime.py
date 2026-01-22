"""
Local Install dx-runtime Test Suite for dx-all-suite

This test suite runs dx-runtime install inside the local-install container
created by test_docker_run_local_install.py.
"""

import os
import pytest
import subprocess
import sys
from pathlib import Path

pytestmark = pytest.mark.local

# Get project root (dx-all-suite directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
VERBOSE_OUTPUT = os.getenv("DX_TEST_VERBOSE", "0").lower() in {"1", "true", "yes", "y"}

# Test configuration
TEST_TIMEOUT = 7200  # 2 hours for runtime install


def _container_name(version: str) -> str:
    return f"dx-local-install-test-{version}"


def _is_container_running(container_name: str) -> bool:
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def _path_exists_in_container(container_name: str, path: str) -> bool:
    result = subprocess.run(
        ["docker", "exec", "-i", container_name, "bash", "-lc", f"test -f {path}"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _ensure_repo_in_container(container_name: str) -> None:
    repo_root_path = "/deepx/workspace"
    nested_repo_path = "/deepx/workspace/dx-all-suite"
    install_path = f"{repo_root_path}/dx-runtime/install.sh"
    nested_install_path = f"{nested_repo_path}/dx-runtime/install.sh"

    if _path_exists_in_container(container_name, install_path):
        return
    if _path_exists_in_container(container_name, nested_install_path):
        return

    raise RuntimeError(
        "dx-all-suite is not mounted in the container. "
        "Re-run test_docker_run_local_install.py with LOCAL_VOLUME_PATH set to the repo root."
    )


def _run_in_container(container_name: str, cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            container_name,
            "bash",
            "-lc",
            cmd,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        timeout=TEST_TIMEOUT,
    )


class TestLocalInstallDxRuntime:
    """Run dx-runtime install in the local-install container"""

    @pytest.mark.parametrize(
        "os_type,version",
        [
            ("ubuntu", "24.04"),
            ("ubuntu", "22.04"),
            ("ubuntu", "20.04"),
            ("ubuntu", "18.04"),
            ("debian", "12"),
            ("debian", "13"),
        ],
    )
    def test_install_dx_runtime_in_container(self, os_type, version, capsys):
        container = _container_name(version)

        if not _is_container_running(container):
            pytest.fail(
                "Required container is not running: "
                f"{container}. Run test_docker_run_local_install.py first."
            )

        try:
            _ensure_repo_in_container(container)
        except Exception as exc:
            pytest.fail(str(exc))

        install_cmd = (
            "set -e; "
            "if [ -f /deepx/workspace/dx-runtime/install.sh ]; then "
            "cd /deepx/workspace; "
            "elif [ -f /deepx/workspace/dx-all-suite/dx-runtime/install.sh ]; then "
            "cd /deepx/workspace/dx-all-suite; "
            "elif [ -f /deepx/dx-runtime/install.sh ]; then "
            "cd /deepx; "
            "else echo 'dx-runtime install.sh not found in container'; exit 2; fi; "
            "./dx-runtime/install.sh --all --exclude-driver --exclude-fw"
        )

        result = self._run_with_live_output(container, install_cmd, capsys)

        if result.returncode != 0:
            error_msg = [
                "",
                "=" * 80,
                f"DX-RUNTIME INSTALL FAILED: {os_type}:{version}",
                "=" * 80,
                f"Exit Code: {result.returncode}",
                f"Container: {container}",
                "",
                "STDOUT:",
                "-" * 80,
                result.stdout or "(no stdout)",
                "-" * 80,
                "",
                "STDERR:",
                "-" * 80,
                result.stderr or "(no stderr)",
                "-" * 80,
                "",
            ]
            pytest.fail("\n".join(error_msg))

    def _run_with_live_output(
        self,
        container: str,
        cmd: str,
        capsys,
    ) -> subprocess.CompletedProcess:
        if VERBOSE_OUTPUT and capsys is not None:
            capsys.disabled()
        banner = (
            f"\n{'=' * 80}\n"
            f"🚀 Installing dx-runtime in container: {container}\n"
            f"{'=' * 80}\n"
        )
        print(banner, file=sys.stdout, flush=True)
        print(banner, file=sys.stderr, flush=True)

        process = subprocess.Popen(
            [
                "docker",
                "exec",
                "-i",
                container,
                "bash",
                "-lc",
                cmd,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=PROJECT_ROOT,
        )

        output_lines = []
        for line in process.stdout:
            if VERBOSE_OUTPUT and capsys is not None:
                with capsys.disabled():
                    print(line, end="", file=sys.stdout, flush=True)
                    print(line, end="", file=sys.stderr, flush=True)
            else:
                print(line, end="", file=sys.stdout, flush=True)
                print(line, end="", file=sys.stderr, flush=True)
            output_lines.append(line.rstrip())

        process.wait(timeout=TEST_TIMEOUT)

        summary = f"\n{'=' * 80}\n"
        if process.returncode == 0:
            summary += f"✅ dx-runtime install succeeded in {container}\n"
        else:
            summary += f"❌ dx-runtime install failed in {container} (exit code: {process.returncode})\n"
        summary += f"{'=' * 80}\n"
        print(summary, file=sys.stdout, flush=True)
        print(summary, file=sys.stderr, flush=True)

        return subprocess.CompletedProcess(
            args=["docker", "exec", "-i", container, "bash", "-lc", cmd],
            returncode=process.returncode,
            stdout="\n".join(output_lines),
            stderr=None,
        )

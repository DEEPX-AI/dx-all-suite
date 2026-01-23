"""
Local Install dx-compiler Test Suite for dx-all-suite

This test suite runs dx-compiler install inside the local-install container
created by test_docker_run_local_install.py.
"""

import pytest
from conftest import (
    container_name,
    is_container_running,
    ensure_repo_in_container,
    run_in_container,
)

pytestmark = pytest.mark.local

# Test configuration
TEST_TIMEOUT = 1800  # 30 minutes for compiler install


class TestLocalInstallDxCompiler:
    """Run dx-compiler install in the local-install container"""

    @pytest.mark.parametrize(
        "os_type,version",
        [
            ("ubuntu", "24.04"),
            ("ubuntu", "22.04"),
            ("ubuntu", "20.04"),
        ],
    )
    def test_install_dx_compiler_in_container(self, os_type, version, capsys):
        container = container_name(version)

        if not is_container_running(container):
            pytest.fail(
                "Required container is not running: "
                f"{container}. Run test_docker_run_local_install.py first."
            )

        try:
            ensure_repo_in_container(container, "dx-compiler")
        except Exception as exc:
            pytest.fail(str(exc))

        install_cmd = (
            "set -e; "
            "if [ -f /deepx/workspace/dx-compiler/install.sh ]; then "
            "cd /deepx/workspace; "
            "elif [ -f /deepx/workspace/dx-all-suite/dx-compiler/install.sh ]; then "
            "cd /deepx/workspace/dx-all-suite; "
            "elif [ -f /deepx/dx-compiler/install.sh ]; then "
            "cd /deepx; "
            "else echo 'dx-compiler install.sh not found in container'; exit 2; fi; "
            "./dx-compiler/install.sh"
        )

        result = run_in_container(
            container,
            install_cmd,
            "Installing dx-compiler",
            timeout=TEST_TIMEOUT,
            capsys=capsys,
        )

        if result.returncode != 0:
            error_msg = [
                "",
                "=" * 80,
                f"DX-COMPILER INSTALL FAILED: {os_type}:{version}",
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

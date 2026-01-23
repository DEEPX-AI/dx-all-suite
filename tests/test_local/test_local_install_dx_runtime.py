"""
Local Install dx-runtime Test Suite for dx-all-suite

This test suite runs dx-runtime install inside the local-install container
created by test_docker_run_local_install.py.
"""

import os
import pytest
from conftest import (
    container_name,
    is_container_running,
    ensure_repo_in_container,
    run_in_container,
)

pytestmark = pytest.mark.local

# Test configuration
TEST_TIMEOUT = 7200  # 2 hours for runtime install


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
        container = container_name(version)

        if not is_container_running(container):
            pytest.fail(
                "Required container is not running: "
                f"{container}. Run test_docker_run_local_install.py first."
            )

        try:
            ensure_repo_in_container(container, "dx-runtime")
        except Exception as exc:
            pytest.fail(str(exc))

        # Build install command with conditional --exclude-fw flag
        exclude_fw_flag = ""
        if os.getenv("DX_EXCLUDE_FW", "0") == "1":
            exclude_fw_flag = " --exclude-fw"
        
        install_cmd = (
            "set -e; "
            "if [ -f /deepx/workspace/dx-runtime/install.sh ]; then "
            "cd /deepx/workspace; "
            "elif [ -f /deepx/workspace/dx-all-suite/dx-runtime/install.sh ]; then "
            "cd /deepx/workspace/dx-all-suite; "
            "elif [ -f /deepx/dx-runtime/install.sh ]; then "
            "cd /deepx; "
            "else echo 'dx-runtime install.sh not found in container'; exit 2; fi; "
            f"./dx-runtime/install.sh --all --exclude-driver{exclude_fw_flag}"
        )

        result = run_in_container(
            container,
            install_cmd,
            "Installing dx-runtime",
            timeout=TEST_TIMEOUT,
            capsys=capsys,
        )

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


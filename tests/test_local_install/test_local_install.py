"""
Local Install Test Suite for dx-all-suite

This test suite validates local installation for:
- dx-compiler (Ubuntu 24.04, 22.04, 20.04)
- dx-modelzoo (Ubuntu 24.04, 22.04, 20.04, Debian 12, 13)
- dx-runtime (Ubuntu 24.04, 22.04, 20.04, Debian 12, 13)

Test workflow:
1. Build docker image (session fixture)
2. Start container (session fixture)
3. Install component in container
4. (Optional) Install driver/runtime on host
"""

import os
import pytest
import subprocess
import sys
from pathlib import Path

pytestmark = pytest.mark.local_install

# Get project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Import from conftest
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import (
    run_in_container,
    check_docker_image_exists,
    container_name,
    is_container_running,
    run_command,
)

# Test configuration
INSTALL_TIMEOUT = 10800  # 3 hours for installs

# ============================================================================
# Sanity Tests
# ============================================================================

class TestLocalInstallSanity:
    """Sanity checks before running actual installations"""

    @pytest.mark.sanity
    def test_docker_command_available(self):
        """Verify docker command is available"""
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "docker command not found"

    @pytest.mark.sanity
    def test_docker_compose_command_available(self):
        """Verify docker compose command is available"""
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "docker compose command not found"

    @pytest.mark.sanity
    def test_project_structure(self):
        """Verify essential project directories exist"""
        essential_dirs = [
            PROJECT_ROOT / "dx-compiler",
            PROJECT_ROOT / "dx-runtime",
            PROJECT_ROOT / "dx-modelzoo",
            PROJECT_ROOT / "docker",
        ]

        for dir_path in essential_dirs:
            assert dir_path.exists(), f"Essential directory not found: {dir_path}"


# ============================================================================
# Docker Image Build Tests
# ============================================================================

class TestLocalInstallDockerBuild:
    """Test docker image builds for local install"""

    @pytest.mark.parametrize(
        "component,os_type,version",
        [
            ("dx-compiler", "ubuntu", "24.04"),
            ("dx-compiler", "ubuntu", "22.04"),
            ("dx-compiler", "ubuntu", "20.04"),
            ("dx-modelzoo", "ubuntu", "24.04"),
            ("dx-modelzoo", "ubuntu", "22.04"),
            ("dx-modelzoo", "ubuntu", "20.04"),
            ("dx-modelzoo", "ubuntu", "18.04"),
            ("dx-modelzoo", "debian", "12"),
            ("dx-modelzoo", "debian", "13"),
            ("dx-runtime", "ubuntu", "24.04"),
            ("dx-runtime", "ubuntu", "22.04"),
            ("dx-runtime", "ubuntu", "20.04"),
            ("dx-runtime", "ubuntu", "18.04"),
            ("dx-runtime", "debian", "12"),
            ("dx-runtime", "debian", "13"),
        ],
        ids=[
            "dx-compiler-ubuntu-24.04",
            "dx-compiler-ubuntu-22.04",
            "dx-compiler-ubuntu-20.04",
            "dx-modelzoo-ubuntu-24.04",
            "dx-modelzoo-ubuntu-22.04",
            "dx-modelzoo-ubuntu-20.04",
            "dx-modelzoo-ubuntu-18.04",
            "dx-modelzoo-debian-12",
            "dx-modelzoo-debian-13",
            "dx-runtime-ubuntu-24.04",
            "dx-runtime-ubuntu-22.04",
            "dx-runtime-ubuntu-20.04",
            "dx-runtime-ubuntu-18.04",
            "dx-runtime-debian-12",
            "dx-runtime-debian-13",
        ],
    )
    def test_docker_build(self, component, os_type, version):
        """
        Test Docker image build for local install.

        Builds the docker image using docker compose if it doesn't exist.
        """
        # Check if image already exists
        if check_docker_image_exists(os_type, version):
            return

        # Image doesn't exist, build it
        env = os.environ.copy()
        env["COMPOSE_BAKE"] = "true"
        env["HOST_UID"] = str(os.getuid())
        env["HOST_GID"] = str(os.getgid())
        env["TARGET_USER"] = "deepx"
        env["TARGET_HOME"] = "/deepx"
        env["OS_TYPE"] = os_type
        env["VERSION"] = version
        env["VERSION_DASH"] = version.replace(".", "-")

        if not env.get("XAUTHORITY"):
            from pathlib import Path
            dummy_xauth = "/tmp/dummy"
            Path(dummy_xauth).touch(exist_ok=True)
            env["XAUTHORITY"] = dummy_xauth
            env["XAUTHORITY_TARGET"] = dummy_xauth
        else:
            env["XAUTHORITY_TARGET"] = "/tmp/.docker.xauth"

        # Set environment variables to prevent docker-compose warnings
        if not env.get("USE_INTRANET"):
            env["USE_INTRANET"] = ""
        if not env.get("CA_FILE_NAME"):
            env["CA_FILE_NAME"] = ""
        if not env.get("DISPLAY"):
            env["DISPLAY"] = ""
        if not env.get("COMPONENT"):
            env["COMPONENT"] = component
        if not env.get("LOCAL_VOLUME_PATH"):
            env["LOCAL_VOLUME_PATH"] = str(PROJECT_ROOT)

        config_file_args = ["-f", "tests/docker/docker-compose.local.install.test.yml"]
        if env.get("DX_TEST_NVIDIA_GPU", "0").lower() in {"1", "true", "yes", "y"}:
            config_file_args.extend(["-f", "docker/docker-compose.nvidia_gpu.yml"])
        if env.get("DX_TEST_INTERNAL", "0").lower() in {"1", "true", "yes", "y"}:
            config_file_args.extend(["-f", "docker/docker-compose.internal.yml"])

        no_cache_arg = []
        if env.get("DX_TEST_NO_CACHE", "0").lower() in {"1", "true", "yes", "y"}:
            no_cache_arg = ["--no-cache"]

        cmd = [
            "docker",
            "compose",
            *config_file_args,
            "build",
            *no_cache_arg,
            "dx-local-install-test",
        ]

        # Build the image
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=env,
            timeout=1800,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Failed to build docker image for {os_type}:{version}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

        # Verify the image was created
        assert check_docker_image_exists(os_type, version), \
            f"Docker image not found for {os_type}:{version}"


# ============================================================================
# Docker Container Run Tests
# ============================================================================

class TestLocalInstallDockerRun:
    """Test docker container startup for local install"""

    @pytest.mark.parametrize(
        "component,os_type,version",
        [
            ("dx-compiler", "ubuntu", "24.04"),
            ("dx-compiler", "ubuntu", "22.04"),
            ("dx-compiler", "ubuntu", "20.04"),
            ("dx-modelzoo", "ubuntu", "24.04"),
            ("dx-modelzoo", "ubuntu", "22.04"),
            ("dx-modelzoo", "ubuntu", "20.04"),
            ("dx-modelzoo", "ubuntu", "18.04"),
            ("dx-modelzoo", "debian", "12"),
            ("dx-modelzoo", "debian", "13"),
            ("dx-runtime", "ubuntu", "24.04"),
            ("dx-runtime", "ubuntu", "22.04"),
            ("dx-runtime", "ubuntu", "20.04"),
            ("dx-runtime", "ubuntu", "18.04"),
            ("dx-runtime", "debian", "12"),
            ("dx-runtime", "debian", "13"),
        ],
        ids=[
            "dx-compiler-ubuntu-24.04",
            "dx-compiler-ubuntu-22.04",
            "dx-compiler-ubuntu-20.04",
            "dx-modelzoo-ubuntu-24.04",
            "dx-modelzoo-ubuntu-22.04",
            "dx-modelzoo-ubuntu-20.04",
            "dx-modelzoo-ubuntu-18.04",
            "dx-modelzoo-debian-12",
            "dx-modelzoo-debian-13",
            "dx-runtime-ubuntu-24.04",
            "dx-runtime-ubuntu-22.04",
            "dx-runtime-ubuntu-20.04",
            "dx-runtime-ubuntu-18.04",
            "dx-runtime-debian-12",
            "dx-runtime-debian-13",
        ],
    )
    def test_docker_run(self, component, os_type, version):
        """
        Test Docker container startup.

        Starts the container using docker run with volume mounting.
        If container exists, removes it and recreates.
        """
        container_name_str = container_name(os_type, version)

        # Check if container exists (running or stopped)
        check_result = subprocess.run(
            ["docker", "inspect", container_name_str],
            capture_output=True,
            text=True,
        )

        # If container exists, remove it
        if check_result.returncode == 0:
            remove_result = subprocess.run(
                ["docker", "rm", "-f", container_name_str],
                capture_output=True,
                text=True,
            )
            if remove_result.returncode != 0:
                pytest.fail(
                    f"Failed to remove existing container {container_name_str}\n"
                    f"STDOUT:\n{remove_result.stdout}\n"
                    f"STDERR:\n{remove_result.stderr}"
                )

        # Get LOCAL_VOLUME_PATH from environment
        local_volume_path = os.getenv("LOCAL_VOLUME_PATH", str(PROJECT_ROOT))
        docker_volume_path = os.getenv("DOCKER_VOLUME_PATH", "/deepx/workspace")

        # Build image name
        image_name = f"dx-local-install-test-{os_type}:{version}"

        # Ensure the image exists
        if not check_docker_image_exists(os_type, version):
            pytest.fail(f"Docker image {image_name} does not exist. Run docker build test first.")

        # Start the container
        cmd = [
            "docker", "run",
            "-d",
            "--name", container_name_str,
            "-e", f"DOCKER_VOLUME_PATH={docker_volume_path}",
            "-e", f"LOCAL_VOLUME_PATH={local_volume_path}",
            "-v", f"{local_volume_path}:{docker_volume_path}"
        ]

        cmd.extend([
            image_name,
            "tail", "-f", "/dev/null"
        ])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Failed to start container {container_name_str}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

        # Verify the container is running
        assert is_container_running(container_name_str), \
            f"Container {container_name_str} is not running"

class TestLocalInstallation:
    """
    Test component installations
    1. For dx-runtime, installs driver and runtime on host first
    2. Installs component in container
    3. Verifies installation success
    """

    @pytest.mark.parametrize(
        "component,os_type,version",
        [
            ("dx-compiler", "ubuntu", "24.04"),
            ("dx-compiler", "ubuntu", "22.04"),
            ("dx-compiler", "ubuntu", "20.04"),
            ("dx-modelzoo", "ubuntu", "24.04"),
            ("dx-modelzoo", "ubuntu", "22.04"),
            ("dx-modelzoo", "ubuntu", "20.04"),
            ("dx-modelzoo", "ubuntu", "18.04"),
            ("dx-modelzoo", "debian", "12"),
            ("dx-modelzoo", "debian", "13"),
            ("dx-runtime", "ubuntu", "24.04"),
            ("dx-runtime", "ubuntu", "22.04"),
            ("dx-runtime", "ubuntu", "20.04"),
            ("dx-runtime", "ubuntu", "18.04"),
            ("dx-runtime", "debian", "12"),
            ("dx-runtime", "debian", "13"),
        ],
        ids=[
            "dx-compiler-ubuntu-24.04",
            "dx-compiler-ubuntu-22.04",
            "dx-compiler-ubuntu-20.04",
            "dx-modelzoo-ubuntu-24.04",
            "dx-modelzoo-ubuntu-22.04",
            "dx-modelzoo-ubuntu-20.04",
            "dx-modelzoo-ubuntu-18.04",
            "dx-modelzoo-debian-12",
            "dx-modelzoo-debian-13",
            "dx-runtime-ubuntu-24.04",
            "dx-runtime-ubuntu-22.04",
            "dx-runtime-ubuntu-20.04",
            "dx-runtime-ubuntu-18.04",
            "dx-runtime-debian-12",
            "dx-runtime-debian-13",
        ],
    )
    def test_install_component(self, component, os_type, version, capsys):
        """
        Test component installation in container.
        For dx-runtime, also installs driver and runtime on host first.

        Args:
            component: Component name (dx-compiler, dx-modelzoo, dx-runtime)
            os_type: OS type (ubuntu, debian)
            version: OS version (24.04, 22.04, etc.)
            capsys: Pytest fixture for capturing output
        """
        container_name_str = container_name(os_type, version)

        # Ensure container is running
        if not is_container_running(container_name_str):
            pytest.fail(f"Container {container_name_str} is not running. Run docker run test first.")

        # For dx-runtime, install driver and runtime on host first
        if component == "dx-runtime":
            print("\n" + "=" * 80)
            print("Installing dx-runtime dependencies on host")
            print("=" * 80 + "\n")

            # Step 1: Install dx_rt_npu_linux_driver on host
            cmd = ["./dx-runtime/install.sh", "--target=dx_rt_npu_linux_driver"]
            result = run_command(cmd, "Installing dx_rt_npu_linux_driver", cwd=PROJECT_ROOT, capsys=capsys)
            if result.returncode != 0:
                pytest.fail(
                    "\n".join([
                        "",
                        "=" * 80,
                        "DX_RT_NPU_LINUX_DRIVER INSTALL FAILED",
                        "=" * 80,
                        f"Exit Code: {result.returncode}",
                        f"Command: {' '.join(cmd)}",
                        "",
                        "STDOUT:",
                        "-" * 80,
                        result.stdout or "(no stdout)",
                        "-" * 80,
                        "",
                    ])
                )

            # Step 2: Install dx-runtime on host
            cmd = ["./dx-runtime/install.sh", "--target=dx_rt"]
            result = run_command(cmd, "Installing dx_rt", cwd=PROJECT_ROOT, capsys=capsys)

            if result.returncode != 0:
                pytest.fail(
                    "\n".join([
                        "",
                        "=" * 80,
                        "DX_RT INSTALL FAILED",
                        "=" * 80,
                        f"Exit Code: {result.returncode}",
                        f"Command: {' '.join(cmd)}",
                        "",
                        "STDOUT:",
                        "-" * 80,
                        result.stdout or "(no stdout)",
                        "-" * 80,
                        "",
                    ])
                )

        # Build install command based on component
        if component == "dx-runtime":
            # Build dx_rt install command with optional --exclude-fw flag
            exclude_fw_flag = " --exclude-fw" if os.getenv("DX_EXCLUDE_FW", "0") == "1" else ""
            install_cmd = (
                "set -e; "
                "if [ -f /deepx/workspace/dx-runtime/install.sh ]; then "
                "cd /deepx/workspace; "
                "else echo 'dx-runtime install.sh not found in container'; exit 2; fi; "
                f"./dx-runtime/install.sh --all --sanity-check=n --exclude-driver{exclude_fw_flag}"
            )
        elif component == "dx-compiler":
            # dx-compiler standard install
            install_cmd = (
                "set -e; "
                f"if [ -f /deepx/workspace/{component}/install.sh ]; then "
                "cd /deepx/workspace; "
                f"else echo '{component} install.sh not found in container'; exit 2; fi; "
                "sudo apt update && sudo DEBIAN_FRONTEND=noninteractive apt install -y keyboard-configuration; " # make sure keyboard-configuration is installed to avoid install.sh prompt
                f"DEBIAN_FRONTEND=noninteractive ./{component}/install.sh"
            )
        elif component == "dx-modelzoo":
            # dx-modelzoo standard install
            install_cmd = (
                "set -e; "
                f"if [ -f /deepx/workspace/{component}/install.sh ]; then "
                "cd /deepx/workspace; "
                f"else echo '{component} install.sh not found in container'; exit 2; fi; "
                f"./{component}/install.sh"
            )

        # Run installation
        result = run_in_container(
            container_name_str,
            install_cmd,
            f"Installing {component}",
            timeout=INSTALL_TIMEOUT,
            capsys=capsys,
        )

        # Check result
        if result.returncode != 0:
            error_msg = [
                "",
                "=" * 80,
                f"{component.upper()} INSTALL FAILED",
                "=" * 80,
                f"Exit Code: {result.returncode}",
                f"Container: {container_name_str}",
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

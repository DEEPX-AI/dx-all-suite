"""
Local Install Test Suite for dx-all-suite

This test suite validates local installation for:
- dx-compiler (Ubuntu 26.04, 24.04, 22.04, 20.04, Fedora 42-45, RHEL 9-10, CentOS Stream 9-10)
- dx-modelzoo (Ubuntu 26.04, 24.04, 22.04, 20.04, Debian 12, 13)
- dx-runtime (Ubuntu 26.04, 24.04, 22.04, 20.04, Debian 12, 13)

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
    compose_project_name,
    remove_container_and_wait,
    is_container_running,
    run_command,
    get_base_image,
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
            ("dx-compiler", "ubuntu", "26.04"),
            ("dx-compiler", "ubuntu", "24.04"),
            ("dx-compiler", "ubuntu", "22.04"),
            ("dx-compiler", "ubuntu", "20.04"),
            ("dx-compiler", "fedora", "42"),
            ("dx-compiler", "fedora", "43"),
            ("dx-compiler", "fedora", "44"),
            ("dx-compiler", "fedora", "45"),
            ("dx-compiler", "rhel", "9"),
            ("dx-compiler", "rhel", "10"),
            ("dx-compiler", "centos", "stream9"),
            ("dx-compiler", "centos", "stream10"),
            ("dx-modelzoo", "ubuntu", "26.04"),
            ("dx-modelzoo", "ubuntu", "24.04"),
            ("dx-modelzoo", "ubuntu", "22.04"),
            ("dx-modelzoo", "ubuntu", "20.04"),
            ("dx-modelzoo", "debian", "12"),
            ("dx-modelzoo", "debian", "13"),
            ("dx-runtime", "ubuntu", "26.04"),
            ("dx-runtime", "ubuntu", "24.04"),
            ("dx-runtime", "ubuntu", "22.04"),
            ("dx-runtime", "ubuntu", "20.04"),
            ("dx-runtime", "debian", "12"),
            ("dx-runtime", "debian", "13"),
        ],
        ids=[
            "dx-compiler-ubuntu-26.04",
            "dx-compiler-ubuntu-24.04",
            "dx-compiler-ubuntu-22.04",
            "dx-compiler-ubuntu-20.04",
            "dx-compiler-fedora-42",
            "dx-compiler-fedora-43",
            "dx-compiler-fedora-44",
            "dx-compiler-fedora-45",
            "dx-compiler-rhel-9",
            "dx-compiler-rhel-10",
            "dx-compiler-centos-stream9",
            "dx-compiler-centos-stream10",
            "dx-modelzoo-ubuntu-26.04",
            "dx-modelzoo-ubuntu-24.04",
            "dx-modelzoo-ubuntu-22.04",
            "dx-modelzoo-ubuntu-20.04",
            "dx-modelzoo-debian-12",
            "dx-modelzoo-debian-13",
            "dx-runtime-ubuntu-26.04",
            "dx-runtime-ubuntu-24.04",
            "dx-runtime-ubuntu-22.04",
            "dx-runtime-ubuntu-20.04",
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
        env["BASE_IMAGE"] = get_base_image(os_type, version)
        env["COMPOSE_PROJECT_NAME"] = compose_project_name(component, os_type, version)

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
            ("dx-compiler", "ubuntu", "26.04"),
            ("dx-compiler", "ubuntu", "24.04"),
            ("dx-compiler", "ubuntu", "22.04"),
            ("dx-compiler", "ubuntu", "20.04"),
            ("dx-compiler", "fedora", "42"),
            ("dx-compiler", "fedora", "43"),
            ("dx-compiler", "fedora", "44"),
            ("dx-compiler", "fedora", "45"),
            ("dx-compiler", "rhel", "9"),
            ("dx-compiler", "rhel", "10"),
            ("dx-compiler", "centos", "stream9"),
            ("dx-compiler", "centos", "stream10"),
            ("dx-modelzoo", "ubuntu", "26.04"),
            ("dx-modelzoo", "ubuntu", "24.04"),
            ("dx-modelzoo", "ubuntu", "22.04"),
            ("dx-modelzoo", "ubuntu", "20.04"),
            ("dx-modelzoo", "debian", "12"),
            ("dx-modelzoo", "debian", "13"),
            ("dx-runtime", "ubuntu", "26.04"),
            ("dx-runtime", "ubuntu", "24.04"),
            ("dx-runtime", "ubuntu", "22.04"),
            ("dx-runtime", "ubuntu", "20.04"),
            ("dx-runtime", "debian", "12"),
            ("dx-runtime", "debian", "13"),
        ],
        ids=[
            "dx-compiler-ubuntu-26.04",
            "dx-compiler-ubuntu-24.04",
            "dx-compiler-ubuntu-22.04",
            "dx-compiler-ubuntu-20.04",
            "dx-compiler-fedora-42",
            "dx-compiler-fedora-43",
            "dx-compiler-fedora-44",
            "dx-compiler-fedora-45",
            "dx-compiler-rhel-9",
            "dx-compiler-rhel-10",
            "dx-compiler-centos-stream9",
            "dx-compiler-centos-stream10",
            "dx-modelzoo-ubuntu-26.04",
            "dx-modelzoo-ubuntu-24.04",
            "dx-modelzoo-ubuntu-22.04",
            "dx-modelzoo-ubuntu-20.04",
            "dx-modelzoo-debian-12",
            "dx-modelzoo-debian-13",
            "dx-runtime-ubuntu-26.04",
            "dx-runtime-ubuntu-24.04",
            "dx-runtime-ubuntu-22.04",
            "dx-runtime-ubuntu-20.04",
            "dx-runtime-debian-12",
            "dx-runtime-debian-13",
        ],
    )
    def test_docker_run(self, component, os_type, version):
        """
        Test Docker container startup.

        Starts the container using docker compose up with volume mounting.
        If container exists, removes it and recreates.
        """
        container_name_str = container_name(os_type, version, component)

        # Remove any existing container with this name and wait until the name
        # is free, so the recreate below does not race the teardown.
        remove_container_and_wait(container_name_str)

        # Build image name
        image_name = f"dx-local-install-test-{os_type}:{version}"

        # Ensure the image exists
        if not check_docker_image_exists(os_type, version):
            pytest.fail(f"Docker image {image_name} does not exist. Run docker build test first.")

        # Prepare environment for docker compose
        env = os.environ.copy()
        env["HOST_UID"] = str(os.getuid())
        env["HOST_GID"] = str(os.getgid())
        env["OS_TYPE"] = os_type
        env["VERSION"] = version
        env["VERSION_DASH"] = version.replace(".", "-")
        env["COMPONENT"] = component
        env["LOCAL_VOLUME_PATH"] = os.getenv("LOCAL_VOLUME_PATH", str(PROJECT_ROOT))
        env["DOCKER_VOLUME_PATH"] = os.getenv("DOCKER_VOLUME_PATH", "/deepx/workspace")
        env["BASE_IMAGE"] = get_base_image(os_type, version)
        env["COMPOSE_PROJECT_NAME"] = compose_project_name(component, os_type, version)

        if not env.get("XAUTHORITY"):
            dummy_xauth = "/tmp/dummy"
            Path(dummy_xauth).touch(exist_ok=True)
            env["XAUTHORITY"] = dummy_xauth
            env["XAUTHORITY_TARGET"] = dummy_xauth
        else:
            env["XAUTHORITY_TARGET"] = "/tmp/.docker.xauth"

        if not env.get("USE_INTRANET"):
            env["USE_INTRANET"] = ""
        if not env.get("CA_FILE_NAME"):
            env["CA_FILE_NAME"] = ""
        if not env.get("DISPLAY"):
            env["DISPLAY"] = ""

        config_file_args = ["-f", "tests/docker/docker-compose.local.install.test.yml"]
        if env.get("DX_TEST_NVIDIA_GPU", "0").lower() in {"1", "true", "yes", "y"}:
            config_file_args.extend(["-f", "docker/docker-compose.nvidia_gpu.yml"])
        if env.get("DX_TEST_INTERNAL", "0").lower() in {"1", "true", "yes", "y"}:
            config_file_args.extend(["-f", "docker/docker-compose.internal.yml"])

        # Start the container using docker compose
        cmd = [
            "docker", "compose",
            *config_file_args,
            "up", "-d",
            "--force-recreate",
            "dx-local-install-test",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=env,
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
            ("dx-compiler", "ubuntu", "26.04"),
            ("dx-compiler", "ubuntu", "24.04"),
            ("dx-compiler", "ubuntu", "22.04"),
            ("dx-compiler", "ubuntu", "20.04"),
            ("dx-compiler", "fedora", "42"),
            ("dx-compiler", "fedora", "43"),
            ("dx-compiler", "fedora", "44"),
            ("dx-compiler", "fedora", "45"),
            ("dx-compiler", "rhel", "9"),
            ("dx-compiler", "rhel", "10"),
            ("dx-compiler", "centos", "stream9"),
            ("dx-compiler", "centos", "stream10"),
            ("dx-modelzoo", "ubuntu", "26.04"),
            ("dx-modelzoo", "ubuntu", "24.04"),
            ("dx-modelzoo", "ubuntu", "22.04"),
            ("dx-modelzoo", "ubuntu", "20.04"),
            ("dx-modelzoo", "debian", "12"),
            ("dx-modelzoo", "debian", "13"),
            ("dx-runtime", "ubuntu", "26.04"),
            ("dx-runtime", "ubuntu", "24.04"),
            ("dx-runtime", "ubuntu", "22.04"),
            ("dx-runtime", "ubuntu", "20.04"),
            ("dx-runtime", "debian", "12"),
            ("dx-runtime", "debian", "13"),
        ],
        ids=[
            "dx-compiler-ubuntu-26.04",
            "dx-compiler-ubuntu-24.04",
            "dx-compiler-ubuntu-22.04",
            "dx-compiler-ubuntu-20.04",
            "dx-compiler-fedora-42",
            "dx-compiler-fedora-43",
            "dx-compiler-fedora-44",
            "dx-compiler-fedora-45",
            "dx-compiler-rhel-9",
            "dx-compiler-rhel-10",
            "dx-compiler-centos-stream9",
            "dx-compiler-centos-stream10",
            "dx-modelzoo-ubuntu-26.04",
            "dx-modelzoo-ubuntu-24.04",
            "dx-modelzoo-ubuntu-22.04",
            "dx-modelzoo-ubuntu-20.04",
            "dx-modelzoo-debian-12",
            "dx-modelzoo-debian-13",
            "dx-runtime-ubuntu-26.04",
            "dx-runtime-ubuntu-24.04",
            "dx-runtime-ubuntu-22.04",
            "dx-runtime-ubuntu-20.04",
            "dx-runtime-debian-12",
            "dx-runtime-debian-13",
        ],
    )
    def test_install_component(self, component, os_type, version, capsys,
                               install_host_npu_stack):
        """
        Test component installation in container.
        For dx-runtime, the host NPU driver (and firmware unless excluded) is ensured
        once via the install_host_npu_stack fixture (version-gated, lock-serialized),
        so this per-OS test only validates the in-container dx_rt install.

        Args:
            component: Component name (dx-compiler, dx-modelzoo, dx-runtime)
            os_type: OS type (ubuntu, debian)
            version: OS version (24.04, 22.04, etc.)
            capsys: Pytest fixture for capturing output
            install_host_npu_stack: session prerequisite ensuring host driver/fw once
        """
        container_name_str = container_name(os_type, version, component)

        # Ensure container is running
        if not is_container_running(container_name_str):
            pytest.fail(f"Container {container_name_str} is not running. Run docker run test first.")

        # For dx-runtime, ensure the host NPU stack (driver/fw) exactly once.
        # Driver is a host kernel-module singleton (orthogonal to the container OS),
        # so it is installed a single time and version-gated rather than per-OS.
        if component == "dx-runtime":
            print("\n" + "=" * 80)
            print("Ensuring host NPU stack (driver/fw) once")
            print("=" * 80 + "\n")
            install_host_npu_stack(capsys=capsys)

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
            pre_install = (
                "sudo apt update && sudo DEBIAN_FRONTEND=noninteractive apt install -y keyboard-configuration; "
                if os_type in ("ubuntu", "debian") else ""
            )
            install_cmd = (
                "set -e; "
                f"if [ -f /deepx/workspace/{component}/install.sh ]; then "
                "cd /deepx/workspace; "
                f"else echo '{component} install.sh not found in container'; exit 2; fi; "
                f"{pre_install}"
                f"./{component}/install.sh --pypi=false"
            )
        elif component == "dx-modelzoo":
            # dx-modelzoo install (no install.sh; install via pip)
            install_cmd = (
                "set -e; "
                "cd /deepx/workspace/dx-modelzoo; "
                "sudo apt update && sudo apt install -y python3 python3-dev python3-venv build-essential; "
                "python3 -m venv venv-dx-modelzoo; "
                "source venv-dx-modelzoo/bin/activate && pip install '.[cpu]'"
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

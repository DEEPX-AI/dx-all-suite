"""
Docker Build Test Suite for dx-all-suite

This test suite builds Docker images for local install testing.
The images are built once per session and reused by other tests.

This test suite validates Docker image builds for:
- Ubuntu 24.04, 22.04, 20.04, 18.04

Note: This test builds images as session fixtures. Other tests that need
the images (like test_docker_run_local_install.py) will automatically
trigger the build if the images don't exist.
"""

import pytest
import subprocess
from pathlib import Path

pytestmark = pytest.mark.local

# Define PROJECT_ROOT locally to avoid import issues
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # dx-all-suite directory


def check_docker_image_exists(os_type: str, version: str) -> bool:
    """Check if a local install docker image exists."""
    image_name = f"dx-local-install-test-{os_type.replace('.', '-')}-{version.replace('.', '-')}"
    result = subprocess.run(
        ["docker", "images", "-q", image_name],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


class TestLocalInstallDockerBuildSanity:
    """Sanity checks before running actual Docker builds"""

    def test_docker_command_available(self):
        """Verify docker command is available"""
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "docker command not found"
    
    def test_docker_compose_command_available(self):
        """Verify docker compose command is available"""
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "docker compose command not found"
    
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


class TestLocalInstallDockerBuild:
    """Docker image build local install tests"""
    
    @pytest.mark.parametrize("os_type,version", [
        # docker build local install tests (4 configurations)
        ("ubuntu", "24.04"),
        ("ubuntu", "22.04"),
        ("ubuntu", "20.04"),
        ("ubuntu", "18.04"),
    ])
    def test_docker_build_local_install(self, os_type, version, ensure_local_install_image):
        """
        Test Docker image build for local install.
        
        This test uses the ensure_local_install_image fixture which builds
        the image if it doesn't exist. The fixture is session-scoped, so
        the image is built only once even with pytest -n auto.
        
        Args:
            os_type: OS type (ubuntu)
            version: OS version (24.04, 22.04, 20.04, 18.04)
            ensure_local_install_image: Fixture that ensures image exists
        """
        # The fixture already built the image, just verify it exists
        assert check_docker_image_exists(os_type, version), f"Docker image not found for {os_type}:{version}"


# Apply sanity marker to test class
TestLocalInstallDockerBuildSanity = pytest.mark.sanity(TestLocalInstallDockerBuildSanity)

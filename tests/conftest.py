"""
Shared utilities and configuration for all test suites.

This conftest provides:
1. Common helper functions for test_local (container operations)
2. Common helper functions for test_getting-started (script execution)
3. Pytest hooks for test collection and execution control
"""

import os
import subprocess
import sys
from pathlib import Path
import pytest

# ============================================================================
# Common Configuration
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = REPO_ROOT  # Alias for compatibility
GETTING_STARTED_DIR = REPO_ROOT / "getting-started"
DEFAULT_TIMEOUT = int(os.getenv("DX_TEST_GETTING_STARTED_TIMEOUT", "3600"))


def is_verbose() -> bool:
    """Check if verbose/debug mode is enabled."""
    return os.getenv("DX_TEST_VERBOSE", "0").lower() in {"1", "true", "yes", "y"}


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_collection_modifyitems(items):
    """
    Force all getting-started tests to run sequentially (disable pytest-xdist parallelization).
    
    This hook assigns all tests in the getting-started directory to the same xdist_group,
    which ensures they run on the same worker in sequential order, even when using pytest -n.
    
    How it works:
    - pytest-xdist's xdist_group marker groups tests to run on the same worker
    - By assigning all getting-started tests to the same group ("getting_started_sequential"),
      they will never be distributed across multiple workers
    - Tests within the same group run sequentially in their collection order
    
    This is necessary for getting-started tests because they have dependencies:
    - compiler-0 must install before compiler-1 can download
    - compiler-1 must download before compiler-2 can setup calibration
    - etc.
    """
    for item in items:
        # Check if this test is in the test_getting-started directory
        if "test_getting-started" in str(item.fspath):
            # Add xdist_group marker to force sequential execution on same worker
            item.add_marker(pytest.mark.xdist_group("getting_started_sequential"))


# ============================================================================
# Test Local Container Utilities
# ============================================================================

def container_name(version: str) -> str:
    """Generate container name from version string."""
    return f"dx-local-install-test-{version.replace('.', '-')}"


def is_container_running(container_name: str) -> bool:
    """Check if a docker container is running."""
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def path_exists_in_container(container_name: str, path: str) -> bool:
    """Check if a file or directory exists inside a container."""
    result = subprocess.run(
        ["docker", "exec", "-i", container_name, "bash", "-lc", f"test -f {path}"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def ensure_repo_in_container(container_name: str, component: str) -> None:
    """
    Verify that the dx-all-suite repository is mounted in the container.
    
    Args:
        container_name: Name of the container to check
        component: Component name (e.g., 'dx-runtime', 'dx-compiler', 'dx-modelzoo')
        
    Raises:
        RuntimeError: If the repository is not found in the container
    """
    repo_root_path = "/deepx/workspace"
    nested_repo_path = "/deepx/workspace/dx-all-suite"
    install_path = f"{repo_root_path}/{component}/install.sh"
    nested_install_path = f"{nested_repo_path}/{component}/install.sh"

    if path_exists_in_container(container_name, install_path):
        return
    if path_exists_in_container(container_name, nested_install_path):
        return

    raise RuntimeError(
        "dx-all-suite is not mounted in the container. "
        "Re-run test_docker_run_local_install.py with LOCAL_VOLUME_PATH set to the repo root."
    )


def run_in_container(
    container_name: str,
    cmd: str,
    banner_msg: str = "",
    timeout: int = 7200,
    capsys=None,
) -> subprocess.CompletedProcess:
    """
    Execute a command inside a container with optional live output streaming.
    
    When DX_TEST_VERBOSE=1 (set by ./test.sh --debug), this function will stream
    output in real-time, making it easy to debug container commands.
    
    Args:
        container_name: Name of the container
        cmd: Command to execute
        banner_msg: Optional message to display in banner (e.g., "Installing dx-runtime")
        timeout: Timeout in seconds (default: 7200 = 2 hours)
        capsys: pytest capsys fixture for output control
        
    Returns:
        CompletedProcess object with the result
    """
    # Use banner_msg if provided, otherwise don't show banner
    if is_verbose():
        if capsys is not None:
            capsys.disabled()
        
        if banner_msg:
            banner = (
                f"\n{'=' * 80}\n"
                f"🚀 {banner_msg} in container: {container_name}\n"
                f"{'=' * 80}\n"
            )
            print(banner, file=sys.stdout, flush=True)
            print(banner, file=sys.stderr, flush=True)

    if is_verbose():
        # Live output mode - stream output in real-time
        process = subprocess.Popen(
            [
                "docker",
                "exec",
                "-i",
                container_name,
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
            if capsys is not None:
                with capsys.disabled():
                    print(line, end="", file=sys.stdout, flush=True)
                    print(line, end="", file=sys.stderr, flush=True)
            else:
                print(line, end="", file=sys.stdout, flush=True)
                print(line, end="", file=sys.stderr, flush=True)
            output_lines.append(line.rstrip())

        process.wait(timeout=timeout)

        # Show summary if banner_msg was provided
        if banner_msg:
            summary = f"\n{'=' * 80}\n"
            if process.returncode == 0:
                summary += f"✅ {banner_msg} succeeded in {container_name}\n"
            else:
                summary += f"❌ {banner_msg} failed in {container_name} (exit code: {process.returncode})\n"
            summary += f"{'=' * 80}\n"
            print(summary, file=sys.stdout, flush=True)
            print(summary, file=sys.stderr, flush=True)

        return subprocess.CompletedProcess(
            args=["docker", "exec", "-i", container_name, "bash", "-lc", cmd],
            returncode=process.returncode,
            stdout="\n".join(output_lines),
            stderr=None,
        )
    else:
        # Quiet mode - capture output and return
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
            timeout=timeout,
        )


# ============================================================================
# Docker Image Fixtures for Local Install Tests
# ============================================================================

def check_docker_image_exists(os_type: str, version: str) -> bool:
    """
    Check if a local install docker image exists.
    
    Args:
        os_type: OS type (ubuntu or debian)
        version: OS version (24.04, 22.04, etc.)
        
    Returns:
        True if image exists, False otherwise
    """
    image_name = f"dx-local-install-test-{os_type.replace('.', '-')}-{version.replace('.', '-')}"
    result = subprocess.run(
        ["docker", "images", "-q", image_name],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


@pytest.fixture(scope="session")
def ensure_local_install_image(request):
    """
    Session-scoped fixture to ensure local install docker image exists.
    
    This fixture builds the docker image once per session if it doesn't exist.
    Tests that need the image should use this fixture as a dependency.
    
    The fixture is parameterized with os_type and version from the test via
    indirect=["ensure_local_install_image"] in the parametrize decorator.
    """
    # Get parameters from the test using indirect parametrization
    # Extract os_type and version from the test node
    test_node = request.node
    callspec = test_node.callspec
    os_type = callspec.params.get("os_type", "ubuntu")
    version = callspec.params.get("version", "22.04")
    
    # Check if image already exists
    if check_docker_image_exists(os_type, version):
        return (os_type, version)
    
    # Image doesn't exist, build it
    env = os.environ.copy()
    env["COMPOSE_BAKE"] = "true"
    env["HOST_UID"] = str(os.getuid())
    env["HOST_GID"] = str(os.getgid())
    env["TARGET_USER"] = "deepx"
    env["TARGET_HOME"] = "/deepx"
    
    if os_type == "ubuntu":
        env["UBUNTU_VERSION"] = version
    elif os_type == "debian":
        env["DEBIAN_VERSION"] = version
    
    if not env.get("XAUTHORITY"):
        dummy_xauth = "/tmp/dummy"
        Path(dummy_xauth).touch(exist_ok=True)
        env["XAUTHORITY"] = dummy_xauth
        env["XAUTHORITY_TARGET"] = dummy_xauth
    else:
        env["XAUTHORITY_TARGET"] = "/tmp/.docker.xauth"
    
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
    
    # Build the image with progress output
    banner_msg = f"Building local install docker image for {os_type}:{version}"
    if is_verbose():
        print(f"\n{'=' * 80}\n🚀 {banner_msg}\n{'=' * 80}\n", file=sys.stdout, flush=True)
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=str(PROJECT_ROOT),
        env=env,
    )
    
    output_lines = []
    for line in process.stdout:
        if is_verbose():
            print(line, end="", file=sys.stdout, flush=True)
        output_lines.append(line.rstrip())
    
    process.wait(timeout=1800)
    
    if is_verbose():
        status = "✅ succeeded" if process.returncode == 0 else f"❌ failed (exit code: {process.returncode})"
        print(f"\n{'=' * 80}\n{banner_msg} {status}\n{'=' * 80}\n", file=sys.stdout, flush=True)
    
    if process.returncode != 0:
        pytest.fail(f"Failed to build docker image for {os_type}:{version}\n" + "\n".join(output_lines[-50:]))
    
    return (os_type, version)


# ============================================================================
# Getting-Started Test Utilities
# ============================================================================

def run_script(script_name: str, extra_env: dict | None = None, timeout: int | None = None) -> None:
    """
    Execute a getting-started script with live output when debug mode is enabled.
    
    When DX_TEST_VERBOSE=1 (set by ./test.sh --debug), this function will stream
    output in real-time, making it easy to debug script execution.
    
    This is a specialized wrapper around run_command for getting-started scripts.
    
    Args:
        script_name: Name of the script in getting-started directory
        extra_env: Optional environment variables to add
        timeout: Optional timeout in seconds (default: DEFAULT_TIMEOUT)
        
    Raises:
        pytest.fail: If script doesn't exist or returns non-zero exit code
    """
    script_path = GETTING_STARTED_DIR / script_name
    if not script_path.exists():
        pytest.fail(f"Script not found: {script_path}")

    # Set up environment variables if provided
    if extra_env:
        original_env = {}
        for key, value in extra_env.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value

    cmd = ["bash", str(script_path)]
    use_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
    banner_msg = f"Running script: {script_name}"

    try:
        # Use run_command for execution
        result = run_command(cmd, banner_msg=banner_msg, timeout=use_timeout, cwd=GETTING_STARTED_DIR)
        
        # Fail test if script failed
        if result.returncode != 0:
            pytest.fail(result.stdout or f"Script failed: {script_name}")
    finally:
        # Restore original environment variables
        if extra_env:
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


# ============================================================================
# Test Local Container Utilities
# ============================================================================

def container_name(version: str) -> str:
    """Generate container name from version string."""
    return f"dx-local-install-test-{version.replace('.', '-')}"


def is_container_running(container_name: str) -> bool:
    """Check if a docker container is running."""
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def path_exists_in_container(container_name: str, path: str) -> bool:
    """Check if a file or directory exists inside a container."""
    result = subprocess.run(
        ["docker", "exec", "-i", container_name, "bash", "-lc", f"test -f {path}"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def ensure_repo_in_container(container_name: str, component: str) -> None:
    """
    Verify that the dx-all-suite repository is mounted in the container.
    
    Args:
        container_name: Name of the container to check
        component: Component name (e.g., 'dx-runtime', 'dx-compiler', 'dx-modelzoo')
        
    Raises:
        RuntimeError: If the repository is not found in the container
    """
    repo_root_path = "/deepx/workspace"
    nested_repo_path = "/deepx/workspace/dx-all-suite"
    install_path = f"{repo_root_path}/{component}/install.sh"
    nested_install_path = f"{nested_repo_path}/{component}/install.sh"

    if path_exists_in_container(container_name, install_path):
        return
    if path_exists_in_container(container_name, nested_install_path):
        return

    raise RuntimeError(
        "dx-all-suite is not mounted in the container. "
        "Re-run test_docker_run_local_install.py with LOCAL_VOLUME_PATH set to the repo root."
    )


def run_in_container(
    container_name: str,
    cmd: str,
    banner_msg: str = "",
    timeout: int = 7200,
    capsys=None,
) -> subprocess.CompletedProcess:
    """
    Execute a command inside a container with optional live output streaming.
    
    When DX_TEST_VERBOSE=1 (set by ./test.sh --debug), this function will stream
    output in real-time, making it easy to debug container commands.
    
    Args:
        container_name: Name of the container
        cmd: Command to execute
        banner_msg: Optional message to display in banner (e.g., "Installing dx-runtime")
        timeout: Timeout in seconds (default: 7200 = 2 hours)
        capsys: pytest capsys fixture for output control
        
    Returns:
        CompletedProcess object with the result
    """
    # Use banner_msg if provided, otherwise don't show banner
    if is_verbose():
        if capsys is not None:
            capsys.disabled()
        
        if banner_msg:
            banner = (
                f"\n{'=' * 80}\n"
                f"🚀 {banner_msg} in container: {container_name}\n"
                f"{'=' * 80}\n"
            )
            print(banner, file=sys.stdout, flush=True)
            print(banner, file=sys.stderr, flush=True)

    if is_verbose():
        # Live output mode - stream output in real-time
        process = subprocess.Popen(
            [
                "docker",
                "exec",
                "-i",
                container_name,
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
            if capsys is not None:
                with capsys.disabled():
                    print(line, end="", file=sys.stdout, flush=True)
                    print(line, end="", file=sys.stderr, flush=True)
            else:
                print(line, end="", file=sys.stdout, flush=True)
                print(line, end="", file=sys.stderr, flush=True)
            output_lines.append(line.rstrip())

        process.wait(timeout=timeout)

        # Show summary if banner_msg was provided
        if banner_msg:
            summary = f"\n{'=' * 80}\n"
            if process.returncode == 0:
                summary += f"✅ {banner_msg} succeeded in {container_name}\n"
            else:
                summary += f"❌ {banner_msg} failed in {container_name} (exit code: {process.returncode})\n"
            summary += f"{'=' * 80}\n"
            print(summary, file=sys.stdout, flush=True)
            print(summary, file=sys.stderr, flush=True)

        return subprocess.CompletedProcess(
            args=["docker", "exec", "-i", container_name, "bash", "-lc", cmd],
            returncode=process.returncode,
            stdout="\n".join(output_lines),
            stderr=None,
        )
    else:
        # Quiet mode - capture output and return
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
            timeout=timeout,
        )


def run_command(
    cmd: list[str],
    banner_msg: str = "",
    timeout: int = 1800,
    cwd: str | Path | None = None,
) -> subprocess.CompletedProcess:
    """
    Execute a command with optional live output streaming.
    
    When DX_TEST_VERBOSE=1 (set by ./test.sh --debug), this function will stream
    output in real-time. Otherwise, it runs in quiet mode and only shows output on failure.
    
    Args:
        cmd: Command list to execute
        banner_msg: Optional message to display in banner (e.g., "Building dx-runtime")
        timeout: Timeout in seconds (default: 1800 = 30 minutes)
        cwd: Working directory for command execution (default: PROJECT_ROOT)
        
    Returns:
        CompletedProcess object with the result
    """
    use_cwd = str(cwd) if cwd is not None else str(PROJECT_ROOT)
    
    # Show banner when in verbose mode and banner_msg is provided
    if is_verbose() and banner_msg:
        banner = (
            f"\n{'=' * 80}\n"
            f"🚀 {banner_msg}\n"
            f"{'=' * 80}\n"
        )
        print(banner, file=sys.stdout, flush=True)
        print(banner, file=sys.stderr, flush=True)

    if is_verbose():
        # Live output mode - stream output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=use_cwd,
        )

        output_lines = []
        for line in process.stdout:
            print(line, end="", file=sys.stdout, flush=True)
            print(line, end="", file=sys.stderr, flush=True)
            output_lines.append(line.rstrip())

        process.wait(timeout=timeout)

        # Show summary if banner_msg was provided
        if banner_msg:
            summary = f"\n{'=' * 80}\n"
            if process.returncode == 0:
                summary += f"✅ {banner_msg} succeeded\n"
            else:
                summary += f"❌ {banner_msg} failed (exit code: {process.returncode})\n"
            summary += f"{'=' * 80}\n"
            print(summary, file=sys.stdout, flush=True)
            print(summary, file=sys.stderr, flush=True)

        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout="\n".join(output_lines),
            stderr=None,
        )
    else:
        # Quiet mode - capture output and return
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=use_cwd,
            timeout=timeout,
        )

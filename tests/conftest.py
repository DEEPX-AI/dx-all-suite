"""
Shared utilities and configuration for all test suites.
"""

import os
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = REPO_ROOT  # Alias for compatibility
GETTING_STARTED_DIR = REPO_ROOT / "getting-started"
DEFAULT_TIMEOUT = int(os.getenv("DX_TEST_GETTING_STARTED_TIMEOUT", "3600"))


def is_verbose() -> bool:
    """Check if verbose/debug mode is enabled."""
    return os.getenv("DX_TEST_VERBOSE", "0").lower() in {"1", "true", "yes", "y"}

def container_name(os_type: str, version: str) -> str:
    """Generate container name from os_type and version string."""
    return f"dx-local-install-test-{os_type}-{version.replace('.', '-')}"


def is_container_running(container_name_str: str) -> bool:
    """Check if a docker container is running."""
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container_name_str],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def path_exists_in_container(container_name_str: str, path: str) -> bool:
    """Check if a file or directory exists inside a container."""
    result = subprocess.run(
        ["docker", "exec", "-i", container_name_str, "bash", "-lc", f"test -f {path}"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0

def check_docker_image_exists(os_type: str, version: str) -> bool:
    """
    Check if a local install docker image exists.

    Args:
        os_type: OS type (ubuntu or debian)
        version: OS version (24.04, 22.04, etc.)

    Returns:
        True if image exists, False otherwise
    """
    image_name = f"dx-local-install-test-{os_type}:{version}"
    result = subprocess.run(
        ["docker", "images", "-q", image_name],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())

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
            else:
                print(line, end="", file=sys.stdout, flush=True)
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
    capsys=None,
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

    # Prepare environment with DX_USERNAME and DX_PASSWORD
    env = os.environ.copy()
    if os.getenv("DX_USERNAME"):
        env["DX_USERNAME"] = os.getenv("DX_USERNAME")
    if os.getenv("DX_PASSWORD"):
        env["DX_PASSWORD"] = os.getenv("DX_PASSWORD")

    # Show banner when in verbose mode and banner_msg is provided
    if is_verbose() and banner_msg:
        banner = (
            f"\n{'=' * 80}\n"
            f"🚀 {banner_msg}\n"
            f"{'=' * 80}\n"
        )
        print(banner, file=sys.stdout, flush=True)

    if is_verbose():
        # Live output mode - stream output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=use_cwd,
            env=env,
        )

        output_lines = []
        for line in process.stdout:
            if capsys is not None:
                with capsys.disabled():
                    print(line, end="", file=sys.stdout, flush=True)
            else:
                print(line, end="", file=sys.stdout, flush=True)
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

        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout="\n".join(output_lines),
            stderr=None,
        )
    else:
        # Quiet mode - capture both stdout and stderr separately
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=use_cwd,
            timeout=timeout,
            env=env,
        )

        # Combine stdout and stderr for complete output
        combined_output = ""
        if result.stdout:
            combined_output += result.stdout
        if result.stderr:
            if combined_output:
                combined_output += "\n" + "=" * 80 + "\nSTDERR:\n" + "=" * 80 + "\n"
            combined_output += result.stderr

        # Return with combined output in stdout field for consistent access
        return subprocess.CompletedProcess(
            args=result.args,
            returncode=result.returncode,
            stdout=combined_output,
            stderr=result.stderr,
        )

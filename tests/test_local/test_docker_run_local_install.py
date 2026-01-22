"""
Docker Run Local Install Test Suite for dx-all-suite

This test suite validates local install docker run for:
- Ubuntu 24.04, 22.04, 20.04, 18.04
"""

import pytest
import subprocess
import sys
from pathlib import Path

pytestmark = pytest.mark.local

# Get project root (dx-all-suite directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
DOCKER_RUN_SCRIPT = PROJECT_ROOT / "tests/test_local/local_install_test_docker_run.sh"

# Test configuration
TEST_TIMEOUT = 1800  # 30 minutes per run


class TestLocalInstallDockerRunSanity:
    """Sanity checks before running actual Docker runs"""

    def test_docker_run_script_exists(self):
        """Verify local_install_test_docker_run.sh script exists"""
        assert DOCKER_RUN_SCRIPT.exists(), (
            f"local_install_test_docker_run.sh not found at {DOCKER_RUN_SCRIPT}"
        )

    def test_docker_command_available(self):
        """Verify docker command is available"""
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "docker command not found"

    def test_docker_compose_command_available(self):
        """Verify docker compose command is available"""
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "docker compose command not found"

    def test_project_structure(self):
        """Verify essential project directories exist"""
        essential_dirs = [
            PROJECT_ROOT / "dx-compiler",
            PROJECT_ROOT / "dx-runtime",
            PROJECT_ROOT / "dx-modelzoo",
            PROJECT_ROOT / "docker",
            PROJECT_ROOT / "internal",
        ]

        for dir_path in essential_dirs:
            assert dir_path.exists(), f"Essential directory not found: {dir_path}"


class TestLocalInstallDockerRun:
    """Local install docker run tests"""

    @pytest.mark.parametrize(
        "version",
        [
            "24.04",
            "22.04",
            "20.04",
            "18.04",
        ],
    )
    def test_docker_run_local_install(self, version):
        """
        Test Docker run for specific Ubuntu version

        Args:
            version: OS version (24.04, 22.04, 20.04, 18.04)
        """
        # Run command
        cmd = [
            str(DOCKER_RUN_SCRIPT),
            f"--ubuntu_version={version}",
        ]

        # Execute run (output handled in run_docker_run_local_install)
        result = self.run_docker_run_local_install(cmd, version)

        # Assert run succeeded with detailed error message
        if result.returncode != 0:
            # Extract last 50 lines of output for error context
            output_lines = result.stdout.split("\n") if result.stdout else []

            # Find error indicators in the output
            error_indicators = [
                "ERROR",
                "FAILED",
                "Error",
                "error:",
                "failed:",
                "cannot",
                "Cannot",
            ]
            error_lines = []
            for i, line in enumerate(output_lines):
                if any(indicator in line for indicator in error_indicators):
                    # Get context: 2 lines before and after
                    start = max(0, i - 2)
                    end = min(len(output_lines), i + 3)
                    error_lines.extend(output_lines[start:end])
                    error_lines.append("..." if end < len(output_lines) else "")

            # If no specific errors found, show last 50 lines
            if not error_lines:
                error_lines = output_lines[-50:] if len(output_lines) > 50 else output_lines
            else:
                # Deduplicate while preserving order
                seen = set()
                error_lines = [x for x in error_lines if not (x in seen or seen.add(x))]

            error_msg = [
                "",
                "=" * 80,
                f"DOCKER RUN LOCAL INSTALL FAILED: ubuntu:{version}",
                "=" * 80,
                f"Exit Code: {result.returncode}",
                f"Command: {' '.join(cmd)}",
                "",
                "Error Context (key error lines with context):",
                "-" * 80,
            ]
            error_msg.extend(error_lines)
            error_msg.append("-" * 80)
            error_msg.append("")
            error_msg.append("💡 Tip: Scroll up to see the full docker run output for more context")
            error_msg.append("")

            pytest.fail("\n".join(error_msg))

    def run_docker_run_local_install(self, cmd, version):
        """
        Execute docker run local install command with real-time output

        Args:
            cmd: Command list to execute
            version: OS version

        Returns:
            CompletedProcess object
        """
        try:
            banner = (
                f"\n{'=' * 80}\n🚀 Running: local install docker on ubuntu:{version}\n{'=' * 80}\n"
            )
            # Write to both stdout and stderr to ensure visibility in HTML report
            print(banner, file=sys.stdout, flush=True)
            print(banner, file=sys.stderr, flush=True)

            # Run command with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=PROJECT_ROOT,
            )

            # Print output in real-time with line numbers for easier debugging
            output_lines = []
            line_count = 0
            for line in process.stdout:
                line_count += 1
                # Write to both stdout and stderr for maximum visibility
                print(line, end="", file=sys.stdout, flush=True)
                print(line, end="", file=sys.stderr, flush=True)
                # Store clean line for error reporting
                output_lines.append(line.rstrip())

            # Wait for completion
            process.wait(timeout=TEST_TIMEOUT)

            # Print summary
            summary = f"\n{'=' * 80}\n"
            if process.returncode == 0:
                summary += f"✅ Run succeeded: ubuntu:{version}\n"
            else:
                summary += (
                    f"❌ Run failed: ubuntu:{version} (exit code: {process.returncode})\n"
                )
            summary += f"{'=' * 80}\n"

            # Write to both stdout and stderr
            print(summary, file=sys.stdout, flush=True)
            print(summary, file=sys.stderr, flush=True)

            # Create result object
            result = subprocess.CompletedProcess(
                args=cmd,
                returncode=process.returncode,
                stdout="\n".join(output_lines),
                stderr=None,
            )

            return result

        except subprocess.TimeoutExpired:
            process.kill()
            error_msg = [
                "",
                "=" * 80,
                f"RUN TIMEOUT: ubuntu:{version}",
                "=" * 80,
                f"Timeout: {TEST_TIMEOUT} seconds exceeded",
                f"Command: {' '.join(cmd)}",
                "=" * 80,
            ]
            pytest.fail("\n".join(error_msg))
        except Exception as e:
            error_msg = [
                "",
                "=" * 80,
                f"RUN EXCEPTION: ubuntu:{version}",
                "=" * 80,
                f"Exception: {type(e).__name__}",
                f"Error: {e}",
                f"Command: {' '.join(cmd)}",
                "=" * 80,
            ]
            pytest.fail("\n".join(error_msg))

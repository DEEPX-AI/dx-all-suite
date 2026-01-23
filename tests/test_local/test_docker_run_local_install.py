"""
Docker Run Local Install Test Suite for dx-all-suite

This test suite validates local install docker run for:
- Ubuntu 24.04, 22.04, 20.04, 18.04
"""

import os
import pytest
import subprocess
import sys
from pathlib import Path

pytestmark = pytest.mark.local

# Get project root (dx-all-suite directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
# Test configuration
TEST_TIMEOUT = 1800  # 30 minutes per run


class TestLocalInstallDockerRunSanity:
    """Sanity checks before running actual Docker runs"""

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
            PROJECT_ROOT / "tests",
        ]

        for dir_path in essential_dirs:
            assert dir_path.exists(), f"Essential directory not found: {dir_path}"


class TestLocalInstallDockerRun:
    """Local install docker run tests"""

    @pytest.mark.parametrize(
        "os_type,version",
        [
            ("ubuntu", "24.04"),
            ("ubuntu", "22.04"),
            ("ubuntu", "20.04"),
            ("ubuntu", "18.04"),
        ],
    )
    def test_docker_run_local_install(self, os_type, version, ensure_local_install_image):
        """
        Test Docker run for specific Ubuntu version.
        
        This test depends on ensure_local_install_image fixture which ensures
        the docker image exists before running the container.

        Args:
            os_type: OS type (ubuntu)
            version: OS version (24.04, 22.04, 20.04, 18.04)
            ensure_local_install_image: Fixture that ensures image is built
        """
        # Image is guaranteed to exist via fixture
        # Execute run (output handled in run_docker_run_local_install)
        result = self.run_docker_run_local_install(os_type, version)

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
                f"DOCKER RUN LOCAL INSTALL FAILED: {os_type}:{version}",
                "=" * 80,
                f"Exit Code: {result.returncode}",
                f"Command: docker compose up dx-local-install-test",
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

    def run_docker_run_local_install(self, os_type, version):
        """
        Execute docker run local install command with real-time output

        Args:
            os_type: OS type
            version: OS version

        Returns:
            CompletedProcess object
        """
        try:
            banner = (
                f"\n{'=' * 80}\n🚀 Running: local install docker on {os_type}:{version}\n{'=' * 80}\n"
            )
            # Write to both stdout and stderr to ensure visibility in HTML report
            print(banner, file=sys.stdout, flush=True)
            print(banner, file=sys.stderr, flush=True)

            env = os.environ.copy()
            env.setdefault("LOCAL_VOLUME_PATH", str(PROJECT_ROOT))
            env["COMPOSE_BAKE"] = "true"
            if os_type == "ubuntu":
                env["UBUNTU_VERSION"] = version

            dummy_xauthority = None
            if not env.get("XAUTHORITY"):
                dummy_xauthority = str(PROJECT_ROOT / "dummy_xauthority")
                Path(dummy_xauthority).unlink(missing_ok=True)
                Path(dummy_xauthority).touch()
                env["XAUTHORITY"] = dummy_xauthority
                env["XAUTHORITY_TARGET"] = dummy_xauthority
            else:
                env["XAUTHORITY_TARGET"] = "/tmp/.docker.xauth"

            compose_files = [
                str(PROJECT_ROOT / "tests/docker/docker-compose.local.install.test.yml")
            ]
            if env.get("DX_TEST_NVIDIA_GPU", "0").lower() in {"1", "true", "yes", "y"}:
                compose_files.append(str(PROJECT_ROOT / "tests/docker/docker-compose.nvidia_gpu.yml"))
            if env.get("DX_TEST_DEV", "0").lower() in {"1", "true", "yes", "y"}:
                compose_files.append(str(PROJECT_ROOT / "tests/docker/docker-compose.dev.yml"))
            if env.get("DX_TEST_INTEL_GPU_HW_ACC", "0").lower() in {"1", "true", "yes", "y"}:
                compose_files.append(str(PROJECT_ROOT / "tests/docker/docker-compose.intel_gpu_hw_acc.yml"))

            compose_project = f"dx-local-install-test-{version.replace('.', '-')}"
            cmd = ["docker", "compose"]
            for compose_file in compose_files:
                cmd.extend(["-f", compose_file])
            cmd.extend(["-p", compose_project, "up", "-d", "--remove-orphans", "dx-local-install-test"])

            # Run command with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=PROJECT_ROOT,
                env=env,
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

            # Post-run adjustments (tty flag / xauth)
            container_name = f"dx-local-install-test-{version}"
            session_type = env.get("XDG_SESSION_TYPE", "")

            if process.returncode == 0 and session_type == "tty":
                tty_cmd = ["docker", "exec", "-i", container_name, "touch", "/deepx/tty_flag"]
                output_lines.append("[INFO] Detected tty session; creating /deepx/tty_flag")
                tty_result = subprocess.run(
                    tty_cmd,
                    cwd=PROJECT_ROOT,
                    text=True,
                    capture_output=True,
                )
                output_lines.extend((tty_result.stdout or "").splitlines())
                output_lines.extend((tty_result.stderr or "").splitlines())

            if process.returncode == 0 and dummy_xauthority:
                display = env.get("DISPLAY", "")
                if display.lower().startswith("localhost:"):
                    display = display.split(":", 1)[1]
                if display.lower().startswith("localhost"):
                    display = display.split(":", 1)[-1]
                display = display or env.get("DISPLAY", "")

                try:
                    xauth_list = subprocess.run(
                        ["xauth", "list", display],
                        cwd=PROJECT_ROOT,
                        text=True,
                        capture_output=True,
                    )
                    if xauth_list.returncode == 0 and xauth_list.stdout.strip():
                        xauth_entry = xauth_list.stdout.strip().splitlines()[0]
                        output_lines.append("[INFO] Adding xauth into container")
                        touch_cmd = ["docker", "exec", "-i", container_name, "touch", "/tmp/.docker.xauth"]
                        add_cmd = ["docker", "exec", "-i", container_name, "xauth", "add"] + xauth_entry.split()
                        subprocess.run(touch_cmd, cwd=PROJECT_ROOT, text=True, capture_output=True)
                        add_result = subprocess.run(add_cmd, cwd=PROJECT_ROOT, text=True, capture_output=True)
                        output_lines.extend((add_result.stdout or "").splitlines())
                        output_lines.extend((add_result.stderr or "").splitlines())
                    else:
                        output_lines.append("[WARN] xauth list returned no entries; skipping xauth add")
                except FileNotFoundError:
                    output_lines.append("[WARN] xauth not available; skipping xauth add")

            # Print summary
            summary = f"\n{'=' * 80}\n"
            if process.returncode == 0:
                summary += f"✅ Run succeeded: {os_type}:{version}\n"
            else:
                summary += (
                    f"❌ Run failed: {os_type}:{version} (exit code: {process.returncode})\n"
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
                f"RUN TIMEOUT: {os_type}:{version}",
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
                f"RUN EXCEPTION: {os_type}:{version}",
                "=" * 80,
                f"Exception: {type(e).__name__}",
                f"Error: {e}",
                f"Command: {' '.join(cmd)}",
                "=" * 80,
            ]
            pytest.fail("\n".join(error_msg))

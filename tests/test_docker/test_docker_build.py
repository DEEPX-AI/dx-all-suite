"""
Docker Build Test Suite for dx-all-suite

This test suite validates Docker image builds for:
- dx-runtime (Ubuntu 24.04, 22.04, 20.04, 18.04, Debian 12, Debian 13)
- dx-modelzoo (Ubuntu 24.04, 22.04, 20.04, 18.04, Debian 12, Debian 13)
- dx-compiler (Ubuntu 24.04, 22.04, 20.04)

Total: 15 test cases
"""

import pytest
import subprocess
import os
import sys
from pathlib import Path

pytestmark = pytest.mark.docker

# Get project root (dx-all-suite directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
DOCKER_BUILD_SCRIPT = PROJECT_ROOT / "docker_build.sh"

# Test configuration
TEST_TIMEOUT = 1800  # 30 minutes per build


class TestDockerBuildSanity:
    """Sanity checks before running actual Docker builds"""
    
    def test_docker_build_script_exists(self):
        """Verify docker_build.sh script exists"""
        assert DOCKER_BUILD_SCRIPT.exists(), f"docker_build.sh not found at {DOCKER_BUILD_SCRIPT}"
    
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


class TestDockerBuild:
    """Docker image build tests"""
    
    @pytest.mark.parametrize("target,os_type,version", [
        # dx-runtime tests (6 configurations)
        ("dx-runtime", "ubuntu", "24.04"),
        ("dx-runtime", "ubuntu", "22.04"),
        ("dx-runtime", "ubuntu", "20.04"),
        ("dx-runtime", "ubuntu", "18.04"),
        ("dx-runtime", "debian", "12"),
        ("dx-runtime", "debian", "13"),
        
        # dx-modelzoo tests (6 configurations)
        ("dx-modelzoo", "ubuntu", "24.04"),
        ("dx-modelzoo", "ubuntu", "22.04"),
        ("dx-modelzoo", "ubuntu", "20.04"),
        ("dx-modelzoo", "ubuntu", "18.04"),
        ("dx-modelzoo", "debian", "12"),
        ("dx-modelzoo", "debian", "13"),
        
        # dx-compiler tests (3 configurations - Ubuntu only)
        ("dx-compiler", "ubuntu", "24.04"),
        ("dx-compiler", "ubuntu", "22.04"),
        ("dx-compiler", "ubuntu", "20.04"),
    ])
    def test_docker_build(self, target, os_type, version):
        """
        Test Docker image build for specific target and OS version
        
        Args:
            target: Docker build target (dx-runtime, dx-modelzoo, dx-compiler)
            os_type: OS type (ubuntu or debian)
            version: OS version (24.04, 22.04, 20.04, 18.04, 12, 13)
        """
        # Build command
        cmd = [
            str(DOCKER_BUILD_SCRIPT),
            f"--target={target}",
            f"--{os_type}_version={version}",
            # "--skip-archive",  # Skip archiving to speed up tests
        ]
        
        # Run build (output handled in run_docker_build)
        result = self.run_docker_build(cmd, target, os_type, version)
        
        # Assert build succeeded with detailed error message
        if result.returncode != 0:
            # Extract last 50 lines of output for error context
            output_lines = result.stdout.split('\n') if result.stdout else []
            
            # Find error indicators in the output
            error_indicators = ['ERROR', 'FAILED', 'Error', 'error:', 'failed:', 'cannot', 'Cannot']
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
                f"DOCKER BUILD FAILED: {target} on {os_type}:{version}",
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
            error_msg.append("💡 Tip: Scroll up to see the full build output for more context")
            error_msg.append("")
            
            pytest.fail("\n".join(error_msg))
    
    def run_docker_build(self, cmd, target, os_type, version):
        """
        Execute docker build command with real-time output
        
        Args:
            cmd: Command list to execute
            target: Build target name
            os_type: OS type
            version: OS version
            
        Returns:
            CompletedProcess object
        """
        try:
            banner = f"\n{'='*80}\n🚀 Building: {target} on {os_type}:{version}\n{'='*80}\n"
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
                cwd=PROJECT_ROOT
            )
            
            # Print output in real-time with line numbers for easier debugging
            output_lines = []
            line_count = 0
            for line in process.stdout:
                line_count += 1
                # Write to both stdout and stderr for maximum visibility
                print(line, end='', file=sys.stdout, flush=True)
                print(line, end='', file=sys.stderr, flush=True)
                # Store clean line for error reporting
                output_lines.append(line.rstrip())
            
            # Wait for completion
            process.wait(timeout=TEST_TIMEOUT)
            
            # Print summary
            summary = f"\n{'='*80}\n"
            if process.returncode == 0:
                summary += f"✅ Build succeeded: {target} on {os_type}:{version}\n"
            else:
                summary += f"❌ Build failed: {target} on {os_type}:{version} (exit code: {process.returncode})\n"
            summary += f"{'='*80}\n"
            
            # Write to both stdout and stderr
            print(summary, file=sys.stdout, flush=True)
            print(summary, file=sys.stderr, flush=True)
            
            # Create result object
            result = subprocess.CompletedProcess(
                args=cmd,
                returncode=process.returncode,
                stdout='\n'.join(output_lines),
                stderr=None
            )
            
            return result
            
        except subprocess.TimeoutExpired:
            process.kill()
            error_msg = [
                "",
                "=" * 80,
                f"BUILD TIMEOUT: {target} on {os_type}:{version}",
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
                f"BUILD EXCEPTION: {target} on {os_type}:{version}",
                "=" * 80,
                f"Exception: {type(e).__name__}",
                f"Message: {str(e)}",
                f"Command: {' '.join(cmd)}",
                "=" * 80,
            ]
            pytest.fail("\n".join(error_msg))


# Apply sanity marker to test class
TestDockerBuildSanity = pytest.mark.sanity(TestDockerBuildSanity)

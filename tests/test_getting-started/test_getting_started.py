"""
Getting Started Test Suite for dx-all-suite

This test suite validates the getting-started workflow:
- Compiler tests (install, download, setup, compile, clean)
- Runtime tests (install, setup, run, clean)

All tests run sequentially to maintain proper workflow order.
"""

import os
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_command, GETTING_STARTED_DIR, DEFAULT_TIMEOUT

pytestmark = pytest.mark.getting_started

# ============================================================================
# Compiler Tests
# ============================================================================

@pytest.mark.compiler
def test_compiler_0_install_dx_compiler():
    result = run_command(
        ["bash", str(GETTING_STARTED_DIR / "compiler-0_install_dx-compiler.sh")],
        banner_msg="Running script: compiler-0_install_dx-compiler.sh",
        timeout=DEFAULT_TIMEOUT,
        cwd=GETTING_STARTED_DIR
    )
    if result.returncode != 0:
        pytest.fail(result.stdout or "Script failed: compiler-0_install_dx-compiler.sh")

@pytest.mark.compiler
def test_compiler_1_download_onnx():
    result = run_command(
        ["bash", str(GETTING_STARTED_DIR / "compiler-1_download_onnx.sh")],
        banner_msg="Running script: compiler-1_download_onnx.sh",
        timeout=DEFAULT_TIMEOUT,
        cwd=GETTING_STARTED_DIR
    )
    if result.returncode != 0:
        pytest.fail(result.stdout or "Script failed: compiler-1_download_onnx.sh")

@pytest.mark.compiler
def test_compiler_2_setup_calibration_dataset():
    result = run_command(
        ["bash", str(GETTING_STARTED_DIR / "compiler-2_setup_calibration_dataset.sh")],
        banner_msg="Running script: compiler-2_setup_calibration_dataset.sh",
        timeout=DEFAULT_TIMEOUT,
        cwd=GETTING_STARTED_DIR
    )
    if result.returncode != 0:
        pytest.fail(result.stdout or "Script failed: compiler-2_setup_calibration_dataset.sh")

@pytest.mark.compiler
def test_compiler_3_setup_output_path():
    result = run_command(
        ["bash", str(GETTING_STARTED_DIR / "compiler-3_setup_output_path.sh")],
        banner_msg="Running script: compiler-3_setup_output_path.sh",
        timeout=DEFAULT_TIMEOUT,
        cwd=GETTING_STARTED_DIR
    )
    if result.returncode != 0:
        pytest.fail(result.stdout or "Script failed: compiler-3_setup_output_path.sh")

@pytest.mark.compiler
def test_compiler_4_model_compile():
    result = run_command(
        ["bash", str(GETTING_STARTED_DIR / "compiler-4_model_compile.sh")],
        banner_msg="Running script: compiler-4_model_compile.sh",
        timeout=DEFAULT_TIMEOUT,
        cwd=GETTING_STARTED_DIR
    )
    if result.returncode != 0:
        pytest.fail(result.stdout or "Script failed: compiler-4_model_compile.sh")

@pytest.mark.compiler
def test_compiler_clean():
    result = run_command(
        ["bash", str(GETTING_STARTED_DIR / "compiler-clean.sh")],
        banner_msg="Running script: compiler-clean.sh",
        timeout=DEFAULT_TIMEOUT,
        cwd=GETTING_STARTED_DIR
    )
    if result.returncode != 0:
        pytest.fail(result.stdout or "Script failed: compiler-clean.sh")

# ============================================================================
# Runtime Tests
# ============================================================================

@pytest.mark.runtime
def test_runtime_0_install_dx_runtime():
    script_name = "runtime-0_install_dx-runtime.sh"
    script_path = GETTING_STARTED_DIR / script_name

    if not script_path.exists():
        pytest.fail(f"Script not found: {script_path}")

    cmd = ["bash", str(script_path)]

    # Add --exclude-fw flag if environment variable is set
    if os.getenv("DX_EXCLUDE_FW", "0") == "1":
        cmd.append("--exclude-fw")

    banner_msg = f"Running script: {script_name}"
    result = run_command(cmd, banner_msg=banner_msg, cwd=GETTING_STARTED_DIR)

    if result.returncode != 0:
        pytest.fail(result.stdout or f"Script failed: {script_name}")

@pytest.mark.runtime
def test_runtime_1_setup_input_path():
    result = run_command(
        ["bash", str(GETTING_STARTED_DIR / "runtime-1_setup_input_path.sh")],
        banner_msg="Running script: runtime-1_setup_input_path.sh",
        timeout=DEFAULT_TIMEOUT,
        cwd=GETTING_STARTED_DIR
    )
    if result.returncode != 0:
        pytest.fail(result.stdout or "Script failed: runtime-1_setup_input_path.sh")

@pytest.mark.runtime
def test_runtime_2_setup_assets():
    result = run_command(
        ["bash", str(GETTING_STARTED_DIR / "runtime-2_setup_assets.sh")],
        banner_msg="Running script: runtime-2_setup_assets.sh",
        timeout=DEFAULT_TIMEOUT,
        cwd=GETTING_STARTED_DIR
    )
    if result.returncode != 0:
        pytest.fail(result.stdout or "Script failed: runtime-2_setup_assets.sh")

@pytest.mark.runtime
def test_runtime_3_run_example_using_dxrt():
    result = run_command(
        ["bash", str(GETTING_STARTED_DIR / "runtime-3_run_example_using_dxrt.sh")],
        banner_msg="Running script: runtime-3_run_example_using_dxrt.sh",
        timeout=DEFAULT_TIMEOUT,
        cwd=GETTING_STARTED_DIR
    )
    if result.returncode != 0:
        pytest.fail(result.stdout or "Script failed: runtime-3_run_example_using_dxrt.sh")

@pytest.mark.runtime
def test_runtime_clean():
    result = run_command(
        ["bash", str(GETTING_STARTED_DIR / "runtime-clean.sh")],
        banner_msg="Running script: runtime-clean.sh",
        timeout=DEFAULT_TIMEOUT,
        cwd=GETTING_STARTED_DIR
    )
    if result.returncode != 0:
        pytest.fail(result.stdout or "Script failed: runtime-clean.sh")

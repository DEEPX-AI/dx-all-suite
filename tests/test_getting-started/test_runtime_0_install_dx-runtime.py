import pytest
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_command

pytestmark = [pytest.mark.getting_started, pytest.mark.runtime]

REPO_ROOT = Path(__file__).resolve().parents[2]
GETTING_STARTED_DIR = REPO_ROOT / "getting-started"

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

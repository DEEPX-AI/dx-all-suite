import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script

pytestmark = [pytest.mark.getting_started, pytest.mark.compiler]

def test_compiler_2_setup_calibration_dataset():
    run_script("compiler-2_setup_calibration_dataset.sh")

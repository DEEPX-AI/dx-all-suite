from conftest import run_script
import pytest

pytestmark = pytest.mark.getting_started

def test_compiler_2_setup_calibration_dataset():
    run_script("compiler-2_setup_calibration_dataset.sh")

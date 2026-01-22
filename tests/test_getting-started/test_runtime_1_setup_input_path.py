from conftest import run_script
import pytest

pytestmark = pytest.mark.getting_started

def test_runtime_1_setup_input_path():
    run_script("runtime-1_setup_input_path.sh")

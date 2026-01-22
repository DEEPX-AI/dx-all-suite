from conftest import run_script
import pytest

pytestmark = pytest.mark.getting_started

def test_compiler_3_setup_output_path():
    run_script("compiler-3_setup_output_path.sh")

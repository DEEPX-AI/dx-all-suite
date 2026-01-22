from conftest import run_script
import pytest

pytestmark = pytest.mark.getting_started

def test_runtime_3_run_example_using_dxrt():
    run_script("runtime-3_run_example_using_dxrt.sh")

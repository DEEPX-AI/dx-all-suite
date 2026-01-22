from conftest import run_script
import pytest

pytestmark = pytest.mark.getting_started

def test_runtime_2_setup_assets():
    run_script("runtime-2_setup_assets.sh")

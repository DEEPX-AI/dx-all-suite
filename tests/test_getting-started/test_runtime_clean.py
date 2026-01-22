from conftest import run_script
import pytest

pytestmark = pytest.mark.getting_started

def test_runtime_clean():
    run_script("runtime-clean.sh")

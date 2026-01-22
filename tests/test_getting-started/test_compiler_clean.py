from conftest import run_script
import pytest

pytestmark = pytest.mark.getting_started

def test_compiler_clean():
    run_script("compiler-clean.sh")

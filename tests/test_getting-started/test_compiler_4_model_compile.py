from conftest import run_script
import pytest

pytestmark = pytest.mark.getting_started

def test_compiler_4_model_compile():
    run_script("compiler-4_model_compile.sh")

from conftest import run_script
import pytest

pytestmark = pytest.mark.getting_started

def test_compiler_1_download_onnx():
    run_script("compiler-1_download_onnx.sh")

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script

pytestmark = [pytest.mark.getting_started, pytest.mark.compiler]

def test_compiler_1_download_onnx():
    run_script("compiler-1_download_onnx.sh")

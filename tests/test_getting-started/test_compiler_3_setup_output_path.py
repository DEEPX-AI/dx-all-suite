import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script

pytestmark = [pytest.mark.getting_started, pytest.mark.compiler]

def test_compiler_3_setup_output_path():
    run_script("compiler-3_setup_output_path.sh")

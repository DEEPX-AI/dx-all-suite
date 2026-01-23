import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script

pytestmark = [pytest.mark.getting_started, pytest.mark.runtime]

def test_runtime_1_setup_input_path():
    run_script("runtime-1_setup_input_path.sh")

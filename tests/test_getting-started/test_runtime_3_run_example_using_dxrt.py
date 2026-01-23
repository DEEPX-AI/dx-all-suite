import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script

pytestmark = [pytest.mark.getting_started, pytest.mark.runtime]

def test_runtime_3_run_example_using_dxrt():
    run_script("runtime-3_run_example_using_dxrt.sh")

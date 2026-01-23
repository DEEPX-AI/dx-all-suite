import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script

pytestmark = [pytest.mark.getting_started, pytest.mark.getting_started_skip_install, pytest.mark.runtime]

def test_runtime_clean():
    run_script("runtime-clean.sh")

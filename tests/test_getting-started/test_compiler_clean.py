import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script

pytestmark = pytest.mark.getting_started

def test_compiler_clean():
    run_script("compiler-clean.sh")

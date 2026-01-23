import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script

pytestmark = [pytest.mark.getting_started, pytest.mark.compiler]

def test_compiler_0_install_dx_compiler():
    run_script("compiler-0_install_dx-compiler.sh")

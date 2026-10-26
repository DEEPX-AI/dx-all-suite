# SPDX-License-Identifier: Apache-2.0
"""Make the in-tree packages importable without `pip install -e` or PYTHONPATH.

`pytest .deepx/tools/tests` from the suite root failed with 8 collection errors
(ModuleNotFoundError: dx_transcripts / dx_showcase_gen) whenever the editable
install was stale or absent — the same class of breakage as a dangling
`dx-agent-gen` shim. Prefer the version-matched source next to these tests.
"""
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

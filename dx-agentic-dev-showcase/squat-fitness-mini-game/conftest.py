"""Pytest path setup: make the shared 'common' package and local packages
importable, mirroring the runtime sys.path walk done by the entry script."""
import sys
from pathlib import Path

_session_dir = Path(__file__).resolve().parent
_walk = _session_dir
for _ in range(8):
    for _cand in (_walk / "src" / "python_example",
                  _walk / "dx-runtime" / "dx_app" / "src" / "python_example"):
        if _cand.is_dir():
            if str(_cand) not in sys.path:
                sys.path.insert(0, str(_cand))
            break
    else:
        _walk = _walk.parent
        continue
    break
if str(_session_dir) not in sys.path:
    sys.path.insert(0, str(_session_dir))

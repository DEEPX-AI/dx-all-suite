"""Factory package for the YOLO26n-Pose squat game.

Self-bootstraps the dx_app package root (``src/python_example``, which holds
``common``) onto ``sys.path`` so the factory imports cleanly regardless of the
directory depth it is imported from. This matters because the app lives in the
mandated output-isolation dir (``dx-agentic-dev/<session>/``) rather than the
stock ``src/python_example/<task>/<model>`` layout — so a fixed ``parent.parent``
assumption does not hold. The walker is idempotent and a no-op when the
entrypoint has already set the path up.
"""

import sys as _sys
from pathlib import Path as _Path

_here = _Path(__file__).resolve().parent
for _p in [_here, *_here.parents]:
    _cand = _p / "src" / "python_example"
    if (_cand / "common").is_dir():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
# Also expose the session dir so sibling modules (squat_game_visualizer,
# squat_rep_counter) import as top-level modules.
_session_dir = _here.parent
if str(_session_dir) not in _sys.path:
    _sys.path.insert(0, str(_session_dir))

from .yolo26n_pose_squat_factory import Yolo26nPoseSquatFactory  # noqa: E402

__all__ = ["Yolo26nPoseSquatFactory"]

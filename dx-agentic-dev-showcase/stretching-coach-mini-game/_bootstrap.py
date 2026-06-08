#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""Resolve the dx_app ``common`` framework package onto sys.path.

Portable resolution order (NO PYTHONPATH required):
  1. A vendored ``./common`` next to this file (created by setup.sh) — lets the
     app run even when copied entirely outside the dx-all-suite tree.
  2. dx_app's ``src/python_example/common`` found by walking up — in-place dev.

The session directory itself is always added so sibling modules (pose_logic,
coach, factory) import cleanly.
"""

import sys
from pathlib import Path


def setup() -> str:
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))

    # 1) vendored ./common
    if (here / "common").is_dir():
        return str(here)

    # 2) walk up to dx_app/src/python_example/common
    d = here
    for _ in range(10):
        cand = d / "src" / "python_example"
        if (cand / "common").is_dir():
            if str(cand) not in sys.path:
                sys.path.insert(0, str(cand))
            return str(cand)
        d = d.parent

    raise ImportError(
        "Could not locate the dx_app 'common' framework package. "
        "Run setup.sh to vendor it into ./common, or run from inside dx_app.")

"""Source loader and hero chip list shared by the home-router tests.

The contracts are split across two files: static contracts that only read the source run in the blocking gate, and
contracts that run the real router in a browser run in the advisory --browser stage. Both must see the same
`source()` and `HERO_CHIPS`, so they live here once.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ROUTER = ROOT / "launcher" / "static" / "home-router.js"

# The four chips the hero ships with. If one of these resolves to nothing, the
# chip is wrong — a suggestion the product cannot honour is worse than none.
HERO_CHIPS = (
    "compile yolo26n to DXNN",
    "pose estimation on webcam",
    "16-channel CCTV object detection",
    "segment a video file",
)


def source() -> str:
    assert ROUTER.is_file(), "launcher/static/home-router.js is missing"
    return ROUTER.read_text(encoding="utf-8")

"""Example result image → webp for a dx_app example dir: ≤ 800 px, quality lowered until it fits the budget.

Contract: tests/dx_modelzoo/test_model_card_html.py
"""
from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image

MAX_SIDE = 800
BUDGET = 60_000
FLOOR = 60


def example_image(model, data_dir):
    rel = (model.get("example_images") or {}).get("result") or ""
    path = Path(data_dir) / rel
    return path if rel and path.is_file() else None


def webp_bytes(path, max_side=MAX_SIDE, budget=BUDGET, floor=FLOOR):
    """The encoded image. Cached per file version, so repeated Save as HTML clicks do not re-encode."""
    resolved = Path(path).resolve()
    return _encode(resolved, resolved.stat().st_mtime_ns, max_side, budget, floor)


@lru_cache(maxsize=64)
def _encode(path, _mtime_ns, max_side, budget, floor):
    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail((max_side, max_side))
        quality = 80
        while True:
            buf = BytesIO()
            image.save(buf, "WEBP", quality=quality, method=6)
            data = buf.getvalue()
            if len(data) <= budget or quality <= floor:
                return data
            quality -= 5

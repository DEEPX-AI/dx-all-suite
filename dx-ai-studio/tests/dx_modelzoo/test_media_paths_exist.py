"""The catalog only points at thumbnails and result images that exist.

A path to a missing file costs three 404s per model on every catalog load. A missing image is no image (the card
shows its task icon, the detail page its 'Run inference' note); BEiT-L/16 384, the same model filed as
beit_large_patch16, uses that model's file.
"""
from __future__ import annotations

import importlib


def test_every_media_path_in_the_catalog_exists():
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    from dx_modelzoo.core.config import DATA_DIR
    models = cat.get_catalog()["models"]
    missing = []
    for m in models:
        if m.get("thumbnail") and not (DATA_DIR / m["thumbnail"]).is_file():
            missing.append(("thumbnail", m["id"], m["thumbnail"]))
        res = (m.get("example_images") or {}).get("result")
        if res and not (DATA_DIR / res).is_file():
            missing.append(("result", m["id"], res))
    assert missing == [], missing[:8]
    beit = next(m for m in models if m["id"] == "beit_l_p16_384x384")
    assert beit["thumbnail"] == "thumbnails/beit_large_patch16.jpg"

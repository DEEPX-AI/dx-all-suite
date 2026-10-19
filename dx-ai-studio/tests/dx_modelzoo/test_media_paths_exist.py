"""The catalog only points at thumbnails and result images that exist.

A path to a missing file costs three 404s per model on every catalog load. A missing image is no image (the card
shows its task icon, the detail page its 'Run inference' note); BEiT-L/16 384, the same model filed as
beit_large_patch16, uses that model's file.
"""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest


def _available(data_dir, relative):
    path = Path(relative)
    optimized = data_dir / "optimized" / path.parent
    name = f"{path.stem}-{path.suffix[1:].lower()}"
    return (
        (data_dir / path).is_file()
        or (optimized / f"{name}.webp").is_file()
        or (optimized / f"{name}.jpg").is_file()
    )


def test_every_media_path_in_the_catalog_exists():
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    from dx_modelzoo.core.config import DATA_DIR
    models = cat.get_catalog()["models"]
    missing = []
    for m in models:
        if m.get("thumbnail") and not _available(DATA_DIR, m["thumbnail"]):
            missing.append(("thumbnail", m["id"], m["thumbnail"]))
        res = (m.get("example_images") or {}).get("result")
        if res and not _available(DATA_DIR, res):
            missing.append(("result", m["id"], res))
    assert missing == [], missing[:8]
    beit = next(m for m in models if m["id"] == "beit_l_p16_384x384")
    assert beit["thumbnail"] == "thumbnails/beit_large_patch16.jpg"


@pytest.mark.parametrize("extension", ("webp", "jpg"))
def test_optimized_only_media_keeps_browser_references(tmp_path, monkeypatch, extension):
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    monkeypatch.setattr(cat, "DATA_DIR", tmp_path)
    for relative in (
        f"optimized/thumbnails/model.v2-jpg.{extension}",
        f"optimized/examples/model.v2_result-jpg.{extension}",
        f"optimized/examples/model.v2_original-png.{extension}",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"image")
    model = {
        "id": "model.v2",
        "thumbnail": "thumbnails/model.v2.jpg",
        "example_images": {
            "result": "examples/model.v2_result.jpg",
            "original": "examples/model.v2_original.png",
        },
    }

    cat._settle_media(model)

    assert model["thumbnail"] == "thumbnails/model.v2.jpg"
    assert model["example_images"] == {
        "result": "examples/model.v2_result.jpg",
        "original": "examples/model.v2_original.png",
    }


def test_optimized_only_alias_uses_the_same_models_images(tmp_path, monkeypatch):
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    monkeypatch.setattr(cat, "DATA_DIR", tmp_path)
    for relative in (
        "optimized/thumbnails/beit_large_patch16-jpg.webp",
        "optimized/examples/beit_large_patch16_result-jpg.webp",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"image")
    model = {
        "id": "beit_l_p16_384x384",
        "thumbnail": "thumbnails/beit_l_p16_384x384.jpg",
        "example_images": {"result": "examples/beit_l_p16_384x384_result.jpg"},
    }

    cat._settle_media(model)

    assert model["thumbnail"] == "thumbnails/beit_large_patch16.jpg"
    assert model["example_images"]["result"] == "examples/beit_large_patch16_result.jpg"


def test_original_media_still_works_without_optimized_files(tmp_path, monkeypatch):
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    monkeypatch.setattr(cat, "DATA_DIR", tmp_path)
    path = tmp_path / "thumbnails/model.jpg"
    path.parent.mkdir()
    path.write_bytes(b"image")
    model = {"id": "model", "thumbnail": "thumbnails/model.jpg"}

    cat._settle_media(model)

    assert model["thumbnail"] == "thumbnails/model.jpg"


def test_missing_media_does_not_borrow_another_models_image(tmp_path, monkeypatch):
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    monkeypatch.setattr(cat, "DATA_DIR", tmp_path)
    path = tmp_path / "optimized/thumbnails/other-jpg.webp"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"image")
    model = {
        "id": "missing",
        "thumbnail": "thumbnails/missing.jpg",
        "example_images": {"result": "examples/missing_result.jpg"},
    }

    cat._settle_media(model)

    assert model["thumbnail"] is None
    assert model["example_images"] == {}

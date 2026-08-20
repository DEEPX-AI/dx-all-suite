"""Composer asset-grid thumbnail generation (dx_app.core.assets.sample_thumbnail).

The composer palette shows 82x54px previews; sample_thumbnail serves a small cached JPEG
instead of the full-resolution original. The `f` argument is a user-supplied query param on
/api/asset-thumb, so the path-traversal guard is security-relevant and locked here.
"""
import cv2
import pytest

from dx_app.core.assets import sample_thumbnail, _scan_sample_img
from dx_app.core.config import DX_APP_ROOT


def _a_sample_image():
    for rel in _scan_sample_img():
        if (DX_APP_ROOT / rel).is_file():
            return rel
    return None


def test_traversal_and_non_image_are_rejected():
    # escapes the app root
    assert sample_thumbnail("../../../etc/passwd") is None
    assert sample_thumbnail("/etc/passwd") is None
    # in-tree but not an image extension
    assert sample_thumbnail("server.py") is None
    # missing file
    assert sample_thumbnail("sample/img/does_not_exist_1234.png") is None


def test_downscales_and_caches():
    rel = _a_sample_image()
    if rel is None:
        pytest.skip("no sample image available in this checkout")

    tp = sample_thumbnail(rel, 160)
    assert tp is not None and tp.is_file()

    thumb = cv2.imread(str(tp))
    assert thumb is not None
    h, w = thumb.shape[:2]
    assert w <= 160  # never upscales past the requested width

    src = cv2.imread(str(DX_APP_ROOT / rel))
    if src is not None and src.shape[1] > 160:
        # a real downscale — thumbnail must be materially smaller on disk
        assert tp.stat().st_size < (DX_APP_ROOT / rel).stat().st_size

    # second call is a cache hit → identical path, no regeneration
    assert sample_thumbnail(rel, 160) == tp


def test_width_is_bounded_by_caller():
    rel = _a_sample_image()
    if rel is None:
        pytest.skip("no sample image available in this checkout")
    tp = sample_thumbnail(rel, 96)
    assert tp is not None
    thumb = cv2.imread(str(tp))
    assert thumb.shape[1] <= 96



def test_tmp_file_cleaned_on_replace_failure(monkeypatch):
    """If os.replace fails (e.g. permission error), the .<pid>.tmp file must not be
    left behind polluting the cache directory."""
    import os
    from unittest.mock import patch
    from dx_app.core import assets
    from dx_app.core.config import DX_APP_ROOT

    rel = _a_sample_image()
    if rel is None:
        pytest.skip("no sample image available in this checkout")

    # Clear any cached result and leftover tmp files so we force regeneration
    src = (DX_APP_ROOT / rel).resolve()
    import hashlib
    mtime_ns = src.stat().st_mtime_ns
    key = hashlib.sha1(f"{src}|{mtime_ns}|160".encode("utf-8")).hexdigest()
    expected_out = assets._THUMB_CACHE_DIR / (key + ".jpg")
    expected_out.unlink(missing_ok=True)
    for old_tmp in assets._THUMB_CACHE_DIR.glob(f"{key}.jpg.*.tmp"):
        old_tmp.unlink(missing_ok=True)

    original_replace = os.replace

    def failing_replace(src_path, dst_path):
        raise OSError("simulated permission denied on replace")

    monkeypatch.setattr(os, "replace", failing_replace)

    result = sample_thumbnail(rel, 160)
    # Should return None on failure
    assert result is None

    # The .<pid>.tmp file must NOT exist
    import glob
    tmp_files = list(assets._THUMB_CACHE_DIR.glob(f"{key}.jpg.*.tmp"))
    assert tmp_files == [], f"Leaked tmp files: {tmp_files}"

"""Without sources, optimize_images must fail **loudly**.

`data/thumbnails` and `data/examples` are not in git. The browser receives `data/optimized/`;
the originals are only its input.

So a fresh clone has no sources, and running optimize_images there must not **succeed silently
with zero images processed**: someone trying to rebuild the optimized set would see "success"
when nothing happened.

Rebuilding the sources needs the dx_app server, the .dxnn models and an NPU
(generate_thumbnails.py). The error message must say so.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PIL")

from dx_modelzoo.scripts.optimize_images import optimize_images  # noqa: E402


def test_a_missing_source_root_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError) as e:
        optimize_images(tmp_path / "does-not-exist", tmp_path / "out", write=True)
    assert "generate_thumbnails" in str(e.value), "되살리는 방법을 말해야 한다"


def test_an_empty_source_root_is_an_error(tmp_path):
    """The directory exists but holds no images, as in a fresh clone."""
    (tmp_path / "src").mkdir()
    with pytest.raises(FileNotFoundError):
        optimize_images(tmp_path / "src", tmp_path / "out", write=True)


def test_a_dry_run_still_reports_the_problem(tmp_path):
    """A check without --write must report the same problem."""
    (tmp_path / "src").mkdir()
    with pytest.raises(FileNotFoundError):
        optimize_images(tmp_path / "src", tmp_path / "out", write=False)


def test_sources_present_still_work(tmp_path):
    from PIL import Image

    src = tmp_path / "src" / "thumbnails"
    src.mkdir(parents=True)
    Image.new("RGB", (40, 30), (1, 2, 3)).save(src / "a.jpg")
    report = optimize_images(tmp_path / "src", tmp_path / "out", write=True)
    assert report["written"] == 1

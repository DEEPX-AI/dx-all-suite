"""scripts/build_graph_thumbs.py: a template's result picture becomes a 320x180 JPEG for the palette."""
from __future__ import annotations

import io

import pytest

from scripts import build_graph_thumbs as thumbs

Image = pytest.importorskip("PIL.Image")


def _jpeg(w, h):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (200, 30, 30)).save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.parametrize("w, h", [(640, 640), (1920, 1080), (480, 1200)])
def test_any_picture_becomes_a_small_16_by_9_jpeg(w, h):
    out = Image.open(io.BytesIO(thumbs.make_thumb(_jpeg(w, h))))
    assert out.format == "JPEG" and out.size == (320, 180)


def test_a_thumbnail_stays_small():
    assert len(thumbs.make_thumb(_jpeg(1920, 1080))) < 40 * 1024


def test_the_thumbnails_land_where_the_catalog_looks():
    from dx_app.core import graph_catalog
    assert graph_catalog.THUMBS_DIR.parts[-4:] == ("dx_app", "static", "img", "graph-examples")

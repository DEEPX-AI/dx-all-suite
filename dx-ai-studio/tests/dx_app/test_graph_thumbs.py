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


def test_every_example_whose_models_are_installed_is_run_and_the_rest_named():
    examples = [{"id": "zone_intrusion", "logic": True, "models": ["yolov8-n_640x640"]},
                {"id": "cascade_od_attr", "logic": False, "models": ["yolov8-n_640x640", "deepmar_resnet50_224x224"]},
                {"id": "dms_headpose", "logic": False, "models": ["scrfd_500m", "headpose"]}]
    run, skipped = thumbs.plan(examples, installed={"yolov8-n_640x640", "deepmar_resnet50_224x224"})
    assert [e["id"] for e in run] == ["zone_intrusion", "cascade_od_attr"]
    assert skipped == [("dms_headpose", ["headpose", "scrfd_500m"])]
    run, skipped = thumbs.plan(examples, installed={"yolov8-n_640x640"}, only=["zone_intrusion"])
    assert [e["id"] for e in run] == ["zone_intrusion"] and skipped == []


def _png(w, h, rgb):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), rgb).save(buf, format="PNG")
    return buf.getvalue()


def test_one_result_is_the_plain_thumbnail():
    one = _png(640, 360, (200, 30, 30))
    assert thumbs.tile([one]) == thumbs.make_thumb(one)


def test_two_sources_sit_side_by_side_like_the_results_view():
    out = Image.open(io.BytesIO(thumbs.tile([_png(640, 640, (200, 30, 30)), _png(1920, 1080, (30, 30, 200))])))
    assert out.format == "JPEG" and out.size == (320, 180)
    left, right = out.getpixel((40, 90)), out.getpixel((280, 90))
    assert left[0] > 150 and left[2] < 80, left
    assert right[2] > 150 and right[0] < 80, right


def test_three_or_four_sources_make_a_two_by_two_grid():
    colours = [(200, 30, 30), (30, 200, 30), (30, 30, 200)]
    out = Image.open(io.BytesIO(thumbs.tile([_png(320, 180, c) for c in colours])))
    assert out.size == (320, 180)
    assert out.getpixel((40, 40))[0] > 150       # top left: the first source
    assert out.getpixel((280, 40))[1] > 150      # top right: the second
    assert out.getpixel((40, 140))[2] > 150      # bottom left: the third
    assert max(out.getpixel((280, 140))) < 60    # bottom right: empty


def test_past_four_sources_the_first_four_are_shown():
    pics = [_png(64, 36, (200, 30, 30))] * 4 + [_png(64, 36, (30, 200, 30))]
    out = Image.open(io.BytesIO(thumbs.tile(pics)))
    assert out.getpixel((280, 140))[0] > 150

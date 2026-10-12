"""Assets for the intro Stream scene: 16 channels of real video and real detections from a DX-M1.

Frames come from DEEPX's official sample videos, and the boxes are the result of the official Model Zoo
yolov5-s 320 on a DX-M1 (`scripts/bake_intro_stream.py`). This checks that the baked outputs keep the shape the
screen relies on, with no debug traces (scores).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "launcher" / "static" / "img" / "intro" / "stream"


@pytest.fixture(scope="module")
def data():
    return json.loads((DIR / "detections.json").read_text(encoding="utf-8"))


def test_the_wall_has_sixteen_channels_and_names_its_hero(data):
    assert data["cols"] == 4 and data["rows"] == 4
    assert len(data["tiles"]) == 16
    assert 0 <= data["hero"] < 16
    assert data["stage"] == [1600, 1000]


def test_every_box_is_a_normalised_rect_with_a_class_and_no_score(data):
    total = 0
    for tile in data["tiles"]:
        assert tile["source"] and isinstance(tile["t"], (int, float))
        for box in tile["boxes"]:
            x0, y0, x1, y1 = box["b"]
            assert 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1, box
            assert isinstance(box["c"], str) and box["c"] and not box["c"].isdigit()
            assert set(box) == {"b", "c"}, "score · id 같은 debug 값은 화면에 오지 않는다"
            total += 1
    assert total >= 60, "16칸 전체에서 이보다 적으면 장면이 비어 보인다"


def test_the_pictures_stay_light_enough_for_a_boot_screen():
    assert (DIR / "wall.webp").stat().st_size <= 350_000
    assert (DIR / "hero.webp").stat().st_size <= 300_000


def test_the_source_is_recorded_so_it_can_be_baked_again():
    src = (DIR / "SOURCE.md").read_text(encoding="utf-8")
    assert "sample_videos.tar.gz" in src
    assert "yolov5-s_320x320.dxnn" in src
    assert "FPS" in src

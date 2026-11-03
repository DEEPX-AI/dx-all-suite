"""The 2026-10-30 publish page adds a Q-Master tier and USE_ORT FPS columns.

dx_app reads the table by header label, not by cell position: a position-based read put the
Q-Master accuracy (74.286) into the FPS column of DenseNet121-1 (the right value is 102).
"""
from __future__ import annotations

from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "internal_publish_v2_sample.html"


def _densenet():
    from dx_app.core.modelzoo import _parse_models

    models = _parse_models(FIXTURE.read_text(encoding="utf-8"))
    return next(m for m in models if m["name"] == "DenseNet121-1")


def test_fps_and_fps_per_watt_come_from_their_own_columns():
    m = _densenet()
    assert m["fps"] == "102"
    assert m["fps_per_watt"] == "237.32"


def test_use_ort_columns_are_parsed():
    m = _densenet()
    assert m["use_ort_fps"] == "102"
    assert m["use_ort_fps_per_watt"] == "242.58"


def test_qmaster_tier_is_parsed():
    m = _densenet()
    assert m["qmaster"]["accuracy"] == "74.286"
    assert m["qmaster"]["dxnn_url"].endswith(".dxnn")
    assert m["qmaster"]["json_url"].endswith(".json")


def test_qlite_and_qpro_are_unchanged_by_the_new_columns():
    m = _densenet()
    assert m["qlite"]["accuracy"] == "73.97"
    assert m["qpro"]["accuracy"] == "74.250"

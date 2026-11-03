"""inference.js keys its category lists by legacy names (classification, obb_detection, ...), while the server
hands the UI canonical per-model categories (image_classification, oriented_object_detection, ...).

Every list lookup must go through _taskLegacy(cat), the same normalisation the VIS_HINTS lookup already uses;
otherwise the detect/classify/pair branches silently never fire for the canonical names.
"""
from pathlib import Path

JS = Path(__file__).resolve().parents[2] / "dx_app" / "static" / "js" / "inference.js"


def _src():
    return JS.read_text(encoding="utf-8")


def _body(src, header, span=2400):
    start = src.index(header)
    return src[start:start + span]


def test_update_run_params_normalises_the_category_before_its_lists():
    body = _body(_src(), "function updateRunParams(cat){")
    assert "cat=_taskLegacy(cat)" in body
    assert body.index("cat=_taskLegacy(cat)") < body.index("noneDescMap")


def test_pair_compare_check_normalises_the_category():
    assert "pairCats.indexOf(_taskLegacy(cat))" in _src()


def test_summary_detect_and_classify_checks_normalise_the_category():
    body = _body(_src(), "function contShowSummary(){", span=3000)
    assert "DET_CATS.indexOf(_taskLegacy(cat))" in body
    assert "CLF_CATS.indexOf(_taskLegacy(cat))" in body

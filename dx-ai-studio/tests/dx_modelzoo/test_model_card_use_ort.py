"""USE_ORT FPS (ONNX Runtime ON, CPU tail included, end-to-end) is shown on the Studio card beside plain FPS.

dx_app's model.html keeps performance numbers out of the card (test_model_card_html), so it stays out there too.
"""
import copy

from dx_modelzoo.core import model_card as mc
from dx_modelzoo.core.model_card_html import render_html
from tests.dx_modelzoo.test_model_card import MODEL, ROW, app  # noqa: F401  (fixture)


def _model_with_ort():
    model = copy.deepcopy(MODEL)
    model["performance"] = {"fps": 102.0, "fps_per_watt": 237.32, "use_ort_fps": 102.0, "use_ort_fps_per_watt": 242.58}
    return model


def test_card_carries_the_use_ort_values(app):
    card = mc.build_card(_model_with_ort(), ROW, app, asof="2026-10-30")
    assert card["use_ort_fps"] == 102.0
    assert card["use_ort_fps_per_watt"] == 242.58


def test_studio_html_shows_use_ort_beside_plain_fps(app):
    card = mc.build_card(_model_with_ort(), ROW, app, asof="2026-10-30")
    card["has_image"] = True
    page = render_html(card, image_src="result.webp")
    assert "ORT FPS · DX-M1" in page
    assert "242.6" in page or "242.58" in page


def test_dx_app_page_keeps_use_ort_out_like_the_other_numbers(app):
    card = mc.build_card(_model_with_ort(), ROW, app, asof="2026-10-30")
    card["has_image"] = True
    page = render_html(card, image_src="result.webp", performance=False)
    assert "ORT FPS" not in page

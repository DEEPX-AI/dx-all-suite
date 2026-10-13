"""Self-contained HTML card (spec §4 layout rules, theme, labels)."""
import re

from PIL import Image

from dx_modelzoo.core import model_card as mc
from dx_modelzoo.core.model_card_html import render_html
from dx_modelzoo.core.model_card_image import webp_bytes
from tests.dx_modelzoo.test_model_card import MODEL, ROW, app  # noqa: F401  (fixture)


def _card(app):
    card = mc.build_card(MODEL, ROW, app, asof="2026-10-13")
    card["has_image"] = True
    return card


def test_no_external_resources_only_links(app):
    page = render_html(_card(app), image_src="result.webp")
    assert not re.search(r'<(script|link|img|iframe)[^>]+(src|href)="https?://', page)
    assert 'href="https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/yolov5-m-face_640x640.dxnn"' in page
    assert "devops.dpx.ai" not in page


def test_dark_by_default_with_a_toggle_and_light_print(app):
    page = render_html(_card(app), image_src="result.webp")
    assert "<html lang=\"en\">" in page
    assert "localStorage.getItem('dx-card-theme')" in page and "class=theme" in page
    assert ":root[data-theme=light]" in page and "@media print" in page


def test_labels_translate_and_escape(app):
    page = render_html(_card(app), lang="ko", labels={"Quick start": "빠른 시작", "Model": "<b>x</b>"})
    assert "<html lang=\"ko\">" in page and "빠른 시작" in page and "&lt;b&gt;x&lt;/b&gt;" in page


def test_dx_app_links_and_standalone(app):
    card = _card(app)
    page = render_html(card, image_src="result.webp", other_href="../../../../cpp_example/x/README.md")
    assert 'href="README.md"' in page and 'href="../../../../cpp_example/x/README.md"' in page
    card["has_cpp"] = False
    assert "cpp_example/x" not in render_html(card, image_src="result.webp", other_href="../../../../cpp_example/x/README.md")
    alone = render_html(card, image_src="data:image/webp;base64,AA==", readme_href=None, other_href=None)
    assert 'href="README.md"' not in alone and "cpp_example" not in alone


def test_long_names_break_only_after_underscores_and_slashes(app):
    page = render_html(_card(app), image_src="result.webp")
    assert ("<span class=nb>yolov5-m-face_</span><wbr><span class=nb>640x640_</span><wbr>"
            "<span class=nb>sync.py</span>") in page
    assert "<code><span class=nb>yolov5-m-face_</span><wbr><span class=nb>640x640</span></code>" in page   # crumb
    assert ".nb{white-space:nowrap}" in page
    assert not re.search(r"\.(crumb code|files [^{]*span)\{[^}]*overflow-wrap", page)


def test_license_text_zero_delta_and_empty_lists(app):
    card = _card(app)
    page = render_html(card, image_src="result.webp")
    assert "GNU GPL v3" in page
    assert '<small class="zero">±0.00</small>' in page and "small.zero{color:var(--muted)}" in page
    card["files"]["python"] = []
    card["downloads"] = {"onnx": None, "tiers": []}
    page = render_html(card, image_src="result.webp", readme_href=None)
    assert "<ul class=files>" not in page and "<ul class=dl>" not in page
    assert page.count("<p class=empty>—</p>") == 2


def test_footer_date_board_month_and_unpublished_note(app):
    card = _card(app)
    card["asof"] = None
    card["published"] = False
    card["boards"] = {"rows": [{"board": "DX-M1 · Raspberry Pi 5", "throughput_fps": 179.6, "single_fps": 46.4,
                                "latency_ms": 21.5}], "measured": "July 2026"}
    page = render_html(card, image_src="result.webp")
    assert "Generated from the DX Model Zoo publish table.\nBoard measurements: DX AI Studio Benchmark, July 2026." in page
    assert "as of" not in page and "None" not in page
    assert "Numbers from the DX AI Studio catalog; this model is not in the DX Model Zoo publish table." in page
    card["boards"]["measured"] = None
    page = render_html(card, image_src="result.webp")
    assert "DX AI Studio Benchmark, DX-RT without ORT." in page and "None" not in page


def test_webp_fits_the_budget(tmp_path):
    src = tmp_path / "x.jpg"
    Image.radial_gradient("L").resize((1600, 1200)).convert("RGB").save(src, quality=95)
    data = webp_bytes(src)
    assert data[:4] == b"RIFF" and len(data) <= 60_000
    from io import BytesIO
    assert max(Image.open(BytesIO(data)).size) <= 960
    assert data == webp_bytes(src)          # deterministic, so --check is stable

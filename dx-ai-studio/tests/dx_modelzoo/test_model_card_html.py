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
    page = render_html(card, image_src="result.webp", other_href="../../../../cpp_example/x/")
    assert 'href="README.md"' in page and 'href="../../../../cpp_example/x/"' in page
    alone = render_html(card, image_src="data:image/webp;base64,AA==", readme_href=None, other_href=None)
    assert 'href="README.md"' not in alone and "cpp_example" not in alone


def test_long_file_names_break_only_after_underscores(app):
    page = render_html(_card(app), image_src="result.webp")
    assert "yolov5-m-face_<wbr>640x640_<wbr>sync.py" in page


def test_webp_fits_the_budget(tmp_path):
    src = tmp_path / "x.jpg"
    Image.radial_gradient("L").resize((1600, 1200)).convert("RGB").save(src, quality=95)
    data = webp_bytes(src)
    assert data[:4] == b"RIFF" and len(data) <= 60_000
    from io import BytesIO
    assert max(Image.open(BytesIO(data)).size) <= 960
    assert data == webp_bytes(src)          # deterministic, so --check is stable

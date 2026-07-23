"""dx_modelzoo must expose the public ModelZoo homepage link (like dx_app)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "dx_modelzoo" / "templates" / "index.html"
DICT = ROOT / "dx_modelzoo" / "static" / "js" / "i18n-dict-catalog.js"


def test_topbar_has_public_modelzoo_link():
    html = HTML.read_text(encoding="utf-8")
    assert 'https://developer.deepx.ai/modelzoo/' in html
    assert 'data-i18n="ModelZoo Homepage"' in html


def test_homepage_i18n_key_all_langs():
    src = DICT.read_text(encoding="utf-8")
    assert "'ModelZoo Homepage'" in src
    for lang in ("ko", "ja", "'zh-CN'", "'zh-TW'", "es"):
        assert lang in src

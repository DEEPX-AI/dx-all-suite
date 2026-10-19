"""dx_modelzoo must expose the public ModelZoo homepage link (like dx_app)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "dx_modelzoo" / "templates" / "index.html"
DICT = ROOT / "dx_modelzoo" / "static" / "js" / "i18n-dict-catalog.js"


def test_topbar_has_public_modelzoo_link():
    """The link is server-rendered into the .toolbar slot of the shell header."""
    from dx_modelzoo.server import DX_MODELZOO_SHELL
    from shared.shell import apply as apply_shell

    template = HTML.read_text(encoding="utf-8")
    assert "developer.deepx.ai/modelzoo" not in template, "링크는 이제 shell 슬롯이 그린다"

    html = apply_shell(template, DX_MODELZOO_SHELL)
    assert 'https://developer.deepx.ai/modelzoo/' in html
    assert 'data-i18n="ModelZoo Homepage"' in html
    toolbar = html.split('class="dx-shell-header-right toolbar">', 1)[1].split("</header>", 1)[0]
    assert 'developer.deepx.ai/modelzoo' in toolbar, "링크가 툴바 밖으로 나갔다"


def test_homepage_i18n_key_all_langs():
    src = DICT.read_text(encoding="utf-8")
    assert "'ModelZoo Homepage'" in src
    for lang in ("ko", "ja", "'zh-CN'", "'zh-TW'", "es"):
        assert lang in src

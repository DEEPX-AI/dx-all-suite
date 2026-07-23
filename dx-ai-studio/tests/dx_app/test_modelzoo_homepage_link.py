"""dx_app ModelZoo homepage link must follow the selected source profile.

Bug: the link was hardcoded to the internal/air-gapped devops URL, so it opened the
closed-network site even when 'public' was selected. It must point to
developer.deepx.ai/modelzoo for public and the devops publish page for internal.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "dx_app" / "templates" / "index.html"
JS = ROOT / "dx_app" / "static" / "js" / "modelzoo.js"


def test_homepage_link_default_is_public_site():
    html = HTML.read_text(encoding="utf-8")
    assert 'id="mz-homepage-link"' in html
    # default href is the open-network public site, not the air-gapped devops page
    assert 'href="https://developer.deepx.ai/modelzoo/"' in html
    line = next(l for l in html.splitlines() if 'id="mz-homepage-link"' in l)
    assert "modelzoo-publish-api.devops.dpx.ai" not in line


def test_homepage_link_switches_with_source():
    js = JS.read_text(encoding="utf-8")
    assert "MZ_SITE_URLS" in js and "mzUpdateHomepageLink" in js
    assert "developer.deepx.ai/modelzoo/" in js
    assert "modelzoo-publish-api.devops.dpx.ai" in js
    # the source switch handler must refresh the link
    block = js.split("function mzSwitchSource()", 1)[1].split("}", 1)[0]
    assert "mzUpdateHomepageLink()" in block

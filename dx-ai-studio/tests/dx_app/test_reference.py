"""Reference extraction contracts for DX App."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_app"
TEMPLATES = APP / "templates"
JS_DIR = APP / "static" / "js"

EXPECTED_SECTION_IDS = [
    "quick-start",
    "setup-install",
    "deep-diagnostics",
    "models",
    "run-inference",
    "rtsp-continuous",
    "benchmark",
    "compare",
    "modelzoo",
    "compiler",
    "outputs",
    "pipeline",
    "shortcuts",
    "themes-i18n",
    "global-features",
    "api-endpoints",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_app_reference_template_uses_external_renderer():
    html = read_text(TEMPLATES / "index.html")
    assert 'src="/static/js/reference.js' in html
    assert "buildRefCategories" not in html
    assert "buildRefSections" not in html
    assert "refT5(" not in html
    assert "window._refData" not in html
    assert 'onclick="window._ref' not in html


def test_app_reference_js_uses_event_delegation_and_ref_t5():
    source = read_text(JS_DIR / "reference.js")
    assert "function refT5(en, ko, ja, zhCN, zhTW, es)" in source
    assert "buildRefCategories" in source
    assert "buildRefSections" in source
    assert "addEventListener('click'" in source or "addEventListener(\"click\"" in source
    assert 'onclick="window._ref' not in source
    assert 'data-ref-cat-filter' in source
    assert 'data-ref-id' in source
    assert 'data-ref-tab' in source


def test_app_reference_preserves_section_ids():
    source = read_text(JS_DIR / "reference.js")
    for section_id in EXPECTED_SECTION_IDS:
        assert section_id in source, f"section {section_id!r} missing"


def test_app_reference_ref_t5_order_is_locked():
    source = read_text(JS_DIR / "reference.js")
    assert "function refT5(en, ko, ja, zhCN, zhTW, es)" in source
    body = _extract_braced_body(source, "function refT5")
    assert "|| en" in body
    assert "|| ko" not in body
    assert "refT5('Getting Started','시작하기'" in source or "refT5('Getting Started', '시작하기'" in source
    assert "refT5('Reference','레퍼런스'" in source or "refT5('Reference', '레퍼런스'" in source


def test_app_reference_rebuilds_on_language_change():
    source = read_text(JS_DIR / "reference.js")
    assert "DXI18n.onLangChange" in source
    assert "buildRefCategories" in source
    assert "buildRefSections" in source
    assert "renderRef" in source


def test_app_reference_template_no_orphan_script_after_mount():
    """Template must not have an orphaned <script> between the reference mount and </main>."""
    html = read_text(TEMPLATES / "index.html")
    ref_page_end = html.find('</div>\n<script>\n</main>')
    assert ref_page_end == -1, (
        "Orphaned <script> tag found between reference page close and </main>; "
        "it will swallow subsequent DOM"
    )
    # More generally: all <script> and </script> tags must be balanced
    opens = len(re.findall(r"<script[\s>]", html))
    closes = len(re.findall(r"</script>", html))
    assert opens == closes, f"Unbalanced script tags: {opens} opens vs {closes} closes"


def test_app_reference_js_translates_search_placeholder():
    """reference.js must set #ref-search placeholder via refT5()."""
    source = read_text(JS_DIR / "reference.js")
    assert "ref-search" in source
    # The placeholder must be set through refT5 — look for the pattern
    assert re.search(
        r"""\.placeholder\s*=\s*refT5\(""", source
    ), "ref-search placeholder must be set via refT5()"


def test_app_reference_tab_delegation_uses_last_hyphen():
    """Tab parsing must split on the *last* hyphen, not the first."""
    source = read_text(JS_DIR / "reference.js")
    assert ".split('-')" not in source, (
        "data-ref-tab must not be parsed with .split('-'); "
        "use lastIndexOf('-') to separate secId from tabKey"
    )
    assert "lastIndexOf('-')" in source, (
        "data-ref-tab parsing must use lastIndexOf('-') "
        "so section IDs with hyphens (e.g. 'quick-start') work correctly"
    )


def test_app_reference_detail_nav_label_uses_ref_t5():
    """Detail navigation button must not hardcode Korean page label."""
    source = read_text(JS_DIR / "reference.js")
    assert "s.name+' 페이지로" not in source and "s.name + ' 페이지로" not in source, (
        "Navigation button must not concatenate raw Korean '페이지로'; use refT5()"
    )
    assert re.search(r"refT5\([^)]*페이지로", source), (
        "Navigation label must use refT5() with Korean '페이지로' as one of the variants"
    )


def test_app_reference_js_no_hardcoded_localhost_api_base():
    """Reference copy must not advertise a fixed localhost API origin."""
    source = read_text(JS_DIR / "reference.js")
    assert "localhost:8080" not in source


def test_app_reference_js_api_base_uses_dynamic_origin():
    """Reference API tips must build their base URL from the current browser origin."""
    source = read_text(JS_DIR / "reference.js")
    assert "window.location.origin" in source
    assert "/api/" in source


def test_app_reference_ref_t5_supports_spanish():
    """Reference renderer must not silently fall back to English for Spanish."""
    source = read_text(JS_DIR / "reference.js")
    assert "function refT5(en, ko, ja, zhCN, zhTW, es)" in source
    body = _extract_braced_body(source, "function refT5")
    assert "if(lang==='es') return es || en;" in body


def _extract_braced_body(source: str, anchor: str) -> str:
    start = source.find(anchor)
    assert start != -1, f"anchor {anchor!r} not found"
    open_pos = source.find("{", start)
    assert open_pos != -1, f"no opening brace after {anchor!r}"
    depth = 0
    for i in range(open_pos, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[open_pos + 1 : i]
    raise AssertionError(f"unmatched braces after {anchor!r}")

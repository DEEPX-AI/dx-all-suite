import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CSS_PATH = ROOT / "launcher" / "static" / "sdk-library.css"


def read_css() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


def css_rule(css: str, selector: str) -> str:
    pattern = re.escape(selector) + r"\s*\{([^}]*)\}"
    match = re.search(pattern, css, re.S)
    assert match, f"{selector} rule is missing"
    return match.group(1)


def normalize(rule: str) -> str:
    return re.sub(r"\s+", "", rule)


def test_sdk_list_sidebar_matches_module_sidebar_width_and_tone():
    css = read_css()
    rule = normalize(css_rule(css, ".sdk-list-sidebar"))
    assert "width:240px" in rule
    assert "min-width:min(180px,36vw)" in rule or "min-width:60px" in rule
    assert "background:linear-gradient(180deg,var(--bg-0)0%,var(--bg-1)100%)" in rule
    assert "border-right:1pxsolidvar(--border)" in rule
    assert "display:flex" in rule
    assert "flex-direction:column" in rule
    assert "transition:width.25s" in rule
    assert "z-index:50" in rule


def test_sdk_sidebar_group_headers_match_module_nav_item_spacing():
    css = read_css()
    group = normalize(css_rule(css, ".sdk-sidebar-group-head"))
    icon = normalize(css_rule(css, ".sdk-sidebar-icon"))
    label = normalize(css_rule(css, ".sdk-sidebar-label"))

    assert "gap:12px" in group
    assert "padding:10px20px" in group
    assert "font-size:13px" in group
    assert "border-left:3pxsolidtransparent" in group
    assert "border-radius:06px6px0" in group
    assert "margin-right:8px" in group
    assert "font-size:17px" in icon
    assert "width:22px" in icon
    assert "text-align:center" in icon
    assert "font-size:13px" in label


def test_sdk_sidebar_sections_match_module_nav_active_and_hover_states():
    css = read_css()
    base = normalize(css_rule(css, ".sdk-sidebar-section"))
    hover = normalize(css_rule(css, ".sdk-sidebar-section:hover"))
    selected = normalize(css_rule(css, ".sdk-sidebar-section.selected"))

    assert "gap:12px" in base
    assert "padding:10px20px" in base
    assert "font-size:13px" in base
    assert "transition:var(--transition)" in base
    assert "border-left:3pxsolidtransparent" in base
    assert "border-top:none" in base
    assert "border-right:none" in base
    assert "border-bottom:none" in base
    assert "background:none" in base
    assert "width:100%" in base
    assert "text-align:left" in base
    assert "border-radius:06px6px0" in base
    assert "margin-right:8px" in base
    assert "border-left-color:rgba(99,140,255,.3)" in hover
    assert "font-weight:600" in selected
    assert "box-shadow:inset0012pxrgba(99,140,255,.06)" in selected


def test_sdk_sidebar_section_icon_and_label_match_module_nav_metrics():
    css = read_css()
    icon = normalize(css_rule(css, ".sdk-sidebar-sec-icon"))
    label = normalize(css_rule(css, ".sdk-sidebar-sec-label"))

    assert "font-size:17px" in icon
    assert "width:22px" in icon
    assert "text-align:center" in icon
    assert "flex-shrink:0" in icon
    assert "white-space:nowrap" in label


def test_sdk_sidebar_count_badges_use_design_tokens():
    css = read_css()
    group_count = normalize(css_rule(css, ".sdk-sidebar-count"))
    section_count = normalize(css_rule(css, ".sdk-sidebar-sec-count"))
    assert "color:var(--text-4)" in group_count
    assert "color:var(--text-4)" in section_count

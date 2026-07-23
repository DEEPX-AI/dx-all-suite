"""Static contracts for DX Stream Reference v2 UI."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STREAM = ROOT / "dx_stream"
APP = ROOT / "dx_app"

REFERENCE_TOPIC_IDS = {
    "quick-start",
    "setup-install",
    "dashboard-overview",
    "demo-launcher",
    "streaming-modes",
    "demo-catalog",
    "visual-editor",
    "connection-rules",
    "preset-export",
    "model-catalog",
    "element-reference",
    "custom-library",
    "keyboard-shortcuts",
    "api-endpoints",
    "theme-language",
}

CATEGORY_IDS = {
    "getting-started",
    "demo-streaming",
    "pipeline",
    "models-elements",
    "system",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def template_source() -> str:
    return read_text(STREAM / "templates" / "index.html")


def reference_js_source() -> str:
    return read_text(STREAM / "static" / "js" / "stream-reference.js")


def stream_css_source() -> str:
    return read_text(STREAM / "static" / "css" / "stream.css")


def stream_demo_js_source() -> str:
    return read_text(STREAM / "static" / "js" / "stream-demo.js")


def app_css_source() -> str:
    return read_text(APP / "static" / "css" / "style.css")


def normalized_rule(css: str, selector: str) -> str:
    pattern = re.escape(selector) + r"\s*\{([^}]*)\}"
    match = re.search(pattern, css, re.S)
    assert match, f"missing CSS rule: {selector}"
    return re.sub(r"\s+", "", match.group(1))


def test_stream_reference_template_uses_v2_layout():
    html = template_source()
    assert '<div class="ref-layout" id="ref-layout">' in html
    assert '<div class="ref-toolbar card">' in html
    assert 'class="ref-search-icon"' in html
    assert 'class="ref-search"' in html
    assert 'id="ref-filter-bar"' in html
    assert 'id="ref-content"' in html
    assert 'class="ref-grid"' in html
    assert 'id="ref-grid"' not in html
    assert "DXStream.refFilterCat(" not in html


def test_stream_reference_js_uses_v2_renderer_contract():
    js = reference_js_source()
    assert "function _T5(en, ko, ja, zhCN, zhTW)" in js
    assert "DXStream._L(" not in js
    assert "var _L = S._L" not in js
    assert "ref-grid" not in js
    assert "ref-content" in js
    assert "ref-tabs" in js
    assert "ref-tab-content" in js
    assert "data-ref-cat-filter" in js
    assert "data-ref-id" in js
    assert "addEventListener('click'" in js or 'addEventListener("click"' in js
    assert "S.referenceInit" in js


def test_stream_reference_preserves_categories_and_topics():
    js = reference_js_source()
    missing_categories = sorted(cid for cid in CATEGORY_IDS if cid not in js)
    missing_topics = sorted(tid for tid in REFERENCE_TOPIC_IDS if tid not in js)
    assert not missing_categories, missing_categories
    assert not missing_topics, missing_topics


def test_stream_reference_categories_have_v2_descriptions():
    js = reference_js_source()
    for expected in (
        "Setup, dashboard, and first demo flow",
        "Preset demos, MJPEG/WebRTC",
        "Pipeline builder, validation, presets, and export",
        "Model catalog, GStreamer elements, and custom libraries",
        "Monitoring, APIs, keyboard shortcuts, and troubleshooting",
    ):
        assert expected in js


def test_stream_reference_css_defines_v2_components():
    css = stream_css_source()
    required_selectors = [
        ".chip-bar",
        ".chip",
        "#page-reference.active",
        ".ref-layout",
        ".ref-toolbar",
        ".ref-search-icon",
        ".ref-grid",
        ".ref-cat",
        ".ref-topic-card",
        ".ref-section-icon",
        ".ref-expand",
        ".ref-detail-hd",
        ".ref-tabs",
        ".ref-tab-content",
        ".ref-flow",
        ".ref-box",
        ".ref-tbl",
    ]
    missing = [selector for selector in required_selectors if selector not in css]
    assert not missing, missing


def test_demo_video_header_stacks_above_video_container():
    css = stream_css_source()

    section_rule = normalized_rule(css, ".video-section")
    header_rule = normalized_rule(css, ".video-header")
    controls_rule = normalized_rule(css, ".video-controls")
    info_rule = normalized_rule(css, ".video-info-bar")

    assert "display:flex" in section_rule
    assert "flex-direction:column" in section_rule
    assert "position:relative" in header_rule
    assert "z-index:1" in header_rule
    assert "display:flex" in controls_rule
    assert "display:flex" in info_rule


def test_demo_fullscreen_target_keeps_stop_controls_inside():
    js = stream_demo_js_source()
    body = re.search(
        r"DXStream\.toggleFullscreen\s*=\s*function\s*\(\)\s*\{([\s\S]+?)\n\};",
        js,
    )
    assert body, "missing DXStream.toggleFullscreen implementation"
    src = body.group(1)

    assert "var target = DXStream.$('demo-video-section')" in src
    assert "requestFullscreen()" in src


def test_demo_stop_exits_fullscreen_before_hiding_video_section():
    js = stream_demo_js_source()
    body = re.search(
        r"DXStream\._stopDemo\s*=\s*async\s+function\s*\([^)]*\)\s*\{([\s\S]+?)\n\};",
        js,
    )
    assert body, "missing DXStream._stopDemo implementation"
    src = body.group(1)

    assert "document.fullscreenElement" in src
    assert "document.exitFullscreen()" in src
    assert src.index("document.exitFullscreen()") < src.index("videoSection.style.display = 'none'")


def test_stream_reference_uses_event_delegation_not_inline_handlers():
    js = reference_js_source()
    html = template_source()
    assert 'onclick="DXStream.refFilterCat' not in html
    assert 'onclick="DXStream._ref' not in html
    assert 'onclick="DXStream.refFilterCat' not in js
    assert 'onclick="DXStream._ref' not in js
    assert re.search(
        r"document\.getElementById\(['\"]ref-filter-bar['\"]\)[\s\S]+?\.addEventListener\(['\"]click['\"]",
        js,
    ) or re.search(
        r"var\s+\w+\s*=\s*document\.getElementById\(['\"]ref-filter-bar['\"]\);[\s\S]+?\w+\.addEventListener\(['\"]click['\"]",
        js,
    )
    assert re.search(
        r"document\.getElementById\(['\"]ref-content['\"]\)[\s\S]+?\.addEventListener\(['\"]click['\"]",
        js,
    ) or re.search(
        r"var\s+\w+\s*=\s*document\.getElementById\(['\"]ref-content['\"]\);[\s\S]+?\w+\.addEventListener\(['\"]click['\"]",
        js,
    )


def test_stream_reference_topics_are_built_per_render_for_language_switch():
    js = reference_js_source()
    assert "var REF_TOPICS =" not in js
    assert "function buildRefTopics()" in js
    assert re.search(r"buildRefTopics\(\)", js)


def test_stream_reference_card_click_toggles_existing_detail_closed():
    js = reference_js_source()
    assert "var wasExpanded = _expandedId" in js
    assert re.search(
        r"var\s+wasExpanded\s*=\s*_expandedId;[\s\S]+?closeDetail\(\);[\s\S]+?if\s*\(\s*wasExpanded\s*===\s*topicId\s*\)",
        js,
    )


def test_stream_reference_generated_category_headers_use_styled_classes():
    js = reference_js_source()
    assert "ref-cat-header" not in js
    assert "ref-cat-title" in js
    assert "ref-cat-desc" in js


def test_stream_reference_css_matches_dx_app_reference_visual_contract():
    app_css = app_css_source()
    stream_css = stream_css_source()
    selectors = [
        ".chip",
        ".chip.active",
        ".ref-search",
        ".ref-search:focus",
        ".ref-cat-title",
        ".ref-cat-desc",
        ".ref-topic-card",
        ".ref-topic-card:hover",
        ".ref-expand",
        ".ref-expand-arrow",
        ".ref-expand-close",
        ".ref-detail-hd h2",
        ".ref-detail-hd p",
        ".ref-tab",
        ".ref-tab:hover",
        ".ref-tab.active",
        ".ref-tab-content p",
        ".ref-tab-content ul,.ref-tab-content ol",
        ".ref-tab-content code",
        ".ref-flow-step",
        ".ref-flow-arrow",
        ".ref-box.tip",
        ".ref-box.warn",
        ".ref-tbl th",
        ".ref-tbl td",
    ]
    mismatched = [
        selector
        for selector in selectors
        if normalized_rule(stream_css, selector) != normalized_rule(app_css, selector)
    ]
    assert not mismatched, mismatched


def test_stream_reference_renderer_matches_dx_app_visual_dom_shape():
    js = reference_js_source()
    assert "header.className = 'ref-cat';" in js
    assert "grid.className = 'ref-card-row';" in js
    assert "grid.setAttribute('data-ref-cat', cat.id);" in js
    assert "document.createElement('button')" in js
    assert "container.appendChild(header);" in js
    assert "container.appendChild(grid);" in js
    assert "'<div class=\"ref-detail-hd\"><div><div class=\"ref-detail-kicker\">'" in js
    assert "'</h2><p>' + topic.desc + '</p></div></div>'" in js
    assert "'<div class=\"ref-detail-hd\">' + topic.icon" not in js


def test_stream_reference_detail_chrome_uses_localized_labels():
    js = reference_js_source()
    assert "_T5('Reference','레퍼런스','リファレンス','参考','參考')" in js
    assert "_T5('Overview','개요','概要','概述','概述')" in js
    assert "_T5('Parameters','파라미터','パラメータ','参数','參數')" in js
    assert "_T5('Workflow','워크플로우','ワークフロー','工作流','工作流程')" in js
    assert "_T5('Tips','팁','ヒント','提示','提示')" in js
    assert "overview:'📋 Overview'" not in js
    assert "ref-detail-kicker\">Reference" not in js


def test_stream_reference_tab_labels_remain_keyboard_focusable():
    js = reference_js_source()
    assert 'class="ref-tab' in js
    assert 'tabindex="0"' in js


def test_stream_reference_tab_labels_support_keyboard_activation():
    js = reference_js_source()
    assert "function activateRefTab(tab)" in js
    assert "content.addEventListener('keydown'" in js
    assert "if (e.key !== 'Enter' && e.key !== ' ') return;" in js
    assert "e.preventDefault();" in js
    assert "activateRefTab(tab);" in js


# Task 9: Reference — 제거된 데모/모델 카테고리 검증


def test_stream_reference_matches_dev_demo_surface():
    source = reference_js_source()
    assert "OBB Detection" not in source
    assert "YOLO26n_OBB" not in source
    assert "<td>Classification</td>" not in source
    assert "Secondary Inference" in source
    assert "Multi-Object Tracking" in source
    assert "Manage 16 DEEPX" in source
    assert "Object Detection(8)" in source
    assert "Depth(1)" not in source

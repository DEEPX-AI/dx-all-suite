from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parent.parent
SHARED_STATIC = ROOT / "shared" / "static"

FOUNDATION_HREFS = [
    "/static/shared/dx-fonts.css",
    "/static/shared/dx-tokens.css",
    "/static/shared/dx-base.css",
    "/static/shared/dx-utilities.css",
]

FONT_FILES = [
    "inter-v20-latin-regular.woff2",
    "jetbrains-mono-v24-latin-regular.woff2",
    "NotoSans-Regular.ttf",
    "NotoSans-Bold.ttf",
    "NotoSansMono-Regular.ttf",
    "NotoSansMono-Bold.ttf",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_ordered(html: str, hrefs: list[str]) -> None:
    positions = []
    for href in hrefs:
        token = f'href="{href}"'
        base = href.split("?")[0]
        versioned_token = f'href="{base}?'
        unversioned_token = f'href="{base}"'
        if token in html:
            positions.append(html.index(token))
        elif versioned_token in html:
            positions.append(html.index(versioned_token))
        else:
            assert unversioned_token in html, f"{href} is missing"
            positions.append(html.index(unversioned_token))
    assert positions == sorted(positions), hrefs


def assert_ordered_tokens(text: str, tokens: list[str]) -> None:
    positions = []
    for token in tokens:
        assert token in text, f"{token} is missing"
        positions.append(text.index(token))
    assert positions == sorted(positions), tokens


# Toolbar targets are unconditional top-level markup; do not reuse this parser
# for template-generated conditional DOM without rechecking assumptions.
class ToolbarContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.nodes: list[dict[str, object]] = []
        self.stack: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        classes = set(attr_map.get("class", "").split())
        node = {
            "tag": tag,
            "attrs": attr_map,
            "classes": classes,
            "parent": self.stack[-1] if self.stack else None,
            "children": [],
        }
        idx = len(self.nodes)
        self.nodes.append(node)
        if self.stack:
            self.nodes[self.stack[-1]]["children"].append(idx)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(idx)

    def handle_endtag(self, tag: str) -> None:
        for pos in range(len(self.stack) - 1, -1, -1):
            if self.nodes[self.stack[pos]]["tag"] == tag:
                del self.stack[pos:]
                return


def parse_html_nodes(html: str) -> list[dict[str, object]]:
    parser = ToolbarContractParser()
    parser.feed(html)
    return parser.nodes


def has_classes(node: dict[str, object], *classes: str) -> bool:
    node_classes = node["classes"]
    return all(cls in node_classes for cls in classes)


def has_id(node: dict[str, object], element_id: str) -> bool:
    return node["attrs"].get("id") == element_id


def descendants(nodes: list[dict[str, object]], index: int) -> list[int]:
    found: list[int] = []
    pending = list(nodes[index]["children"])
    while pending:
        child = pending.pop(0)
        found.append(child)
        pending.extend(nodes[child]["children"])
    return found


TOOLBAR_TARGETS = [
    ("dx_app", ROOT / "dx_app" / "templates" / "index.html", ("topbar-right", "toolbar")),
    ("dx_stream", ROOT / "dx_stream" / "templates" / "index.html", ("topbar-right", "toolbar")),
    ("dx_modelzoo", ROOT / "dx_modelzoo" / "templates" / "index.html", ("mz-topbar-right", "toolbar")),
    ("dx_compiler", ROOT / "dx_compiler" / "templates" / "base.html", ("header-right", "toolbar")),
    ("dx_planner", ROOT / "dx_planner" / "templates" / "index.html", ("planner-controls", "toolbar")),
    ("dx_monitor", ROOT / "dx_monitor" / "templates" / "index.html", ("toolbar",)),
    ("dx_benchmark", ROOT / "dx_benchmark" / "templates" / "index.html", ("toolbar",)),
    ("launcher", ROOT / "launcher" / "static" / "index.html", ("toolbar",)),
]


def toolbar_nodes(nodes: list[dict[str, object]]) -> list[int]:
    return [idx for idx, node in enumerate(nodes) if "toolbar" in node["classes"]]


@pytest.mark.parametrize(("app_name", "path", "required_classes"), TOOLBAR_TARGETS)
def test_surface_uses_single_toolbar_class_token_target(app_name, path, required_classes):
    html = read_text(path)
    nodes = parse_html_nodes(html)
    targets = toolbar_nodes(nodes)
    assert len(targets) == 1, f"{app_name} should expose exactly one .toolbar target"
    target = nodes[targets[0]]
    assert has_classes(target, *required_classes), app_name
    assert re.search(r"DXToolbar\.init\(\{[^}]*container:\s*['\"]\.toolbar['\"]", html, re.S), app_name


def find_one(nodes: list[dict[str, object]], predicate, label: str) -> int:
    matches = [idx for idx, node in enumerate(nodes) if predicate(node)]
    assert len(matches) == 1, label
    return matches[0]


def assert_descendant(nodes: list[dict[str, object]], ancestor: int, descendant: int, label: str) -> None:
    assert descendant in descendants(nodes, ancestor), label


def test_app_toolbar_preserves_notification_controls():
    nodes = parse_html_nodes(read_text(ROOT / "dx_app" / "templates" / "index.html"))
    toolbar = find_one(nodes, lambda node: has_classes(node, "topbar-right", "toolbar"), "app toolbar")
    bell = find_one(nodes, lambda node: has_classes(node, "notif-bell"), "notif bell")
    badge = find_one(nodes, lambda node: has_id(node, "notif-badge"), "notif badge")
    assert_descendant(nodes, toolbar, bell, "notif bell remains inside app toolbar")
    assert_descendant(nodes, toolbar, badge, "notif badge remains inside app toolbar")


def test_stream_toolbar_preserves_pipeline_status_badge():
    nodes = parse_html_nodes(read_text(ROOT / "dx_stream" / "templates" / "index.html"))
    toolbar = find_one(nodes, lambda node: has_classes(node, "topbar-right", "toolbar"), "stream toolbar")
    badge = find_one(nodes, lambda node: has_id(node, "pipeline-status"), "pipeline status")
    assert_descendant(nodes, toolbar, badge, "pipeline status remains inside stream toolbar")


def test_benchmark_toolbar_preserves_edgeguide_button():
    nodes = parse_html_nodes(read_text(ROOT / "dx_benchmark" / "templates" / "index.html"))
    toolbar = find_one(nodes, lambda node: has_classes(node, "toolbar"), "benchmark toolbar")
    button = find_one(nodes, lambda node: has_id(node, "edgeguideBtn"), "edgeguide button")
    assert_descendant(nodes, toolbar, button, "edgeguide button remains inside benchmark toolbar")



def test_launcher_toolbar_preserves_status_dots_as_sibling():
    nodes = parse_html_nodes(read_text(ROOT / "launcher" / "static" / "index.html"))
    topbar = find_one(nodes, lambda node: has_classes(node, "top-bar-right"), "launcher top-bar-right")
    toolbar = find_one(nodes, lambda node: has_id(node, "launcherToolbar") and has_classes(node, "toolbar"), "launcher toolbar")
    status = find_one(nodes, lambda node: has_classes(node, "status-dots"), "launcher status dots")
    assert nodes[toolbar]["parent"] == topbar
    assert nodes[status]["parent"] == topbar


def test_shared_foundation_css_files_exist():
    for name in ("dx-fonts.css", "dx-tokens.css", "dx-base.css", "dx-utilities.css"):
        path = SHARED_STATIC / name
        assert path.is_file(), f"{path} missing"
        assert path.stat().st_size > 0, f"{path} is empty"


def test_shared_font_css_uses_shared_font_paths():
    css = read_text(SHARED_STATIC / "dx-fonts.css")
    assert "/static/shared/fonts/inter-v20-latin-regular.woff2" in css
    assert "/static/shared/fonts/jetbrains-mono-v24-latin-regular.woff2" in css
    assert "/static/shared/fonts/NotoSans-Regular.ttf" in css
    assert "/static/fonts/" not in css
    for font_name in FONT_FILES:
        assert (SHARED_STATIC / "fonts" / font_name).is_file(), font_name


def test_shared_tokens_include_required_aliases():
    css = read_text(SHARED_STATIC / "dx-tokens.css")
    required_tokens = [
        "--bg-0",
        "--bg-1",
        "--text-1",
        "--text-2",
        "--accent",
        "--accent-rgb",
        "--success",
        "--warning",
        "--error",
        "--info",
        "--font",
        "--mono",
        "--sp-1",
        "--radius",
    ]
    for token in required_tokens:
        assert token in css


def test_shared_base_includes_safe_foundation_rules():
    css = read_text(SHARED_STATIC / "dx-base.css")
    assert "*,*::before,*::after" in css
    assert "button,select,input,textarea,optgroup" in css
    assert ":focus-visible" in css
    assert "::-webkit-scrollbar" in css
    assert "@keyframes dx-pulse" in css
    assert "@keyframes dx-fade-in" in css
    assert "@keyframes dx-spin" in css
    assert ".card{" not in css
    assert ".btn{" not in css
    assert ".top-bar" not in css


def test_monitor_template_uses_canonical_css_order():
    html = read_text(ROOT / "dx_monitor" / "templates" / "index.html")
    assert html.count('href="/static/shared/chat-widget.css"') == 1
    assert html.index('href="/static/shared/chat-widget.css"') < html.index("<body")
    assert_ordered(
        html,
        FOUNDATION_HREFS
        + [
            "/static/shared/tutorial.css",
            "/static/shared/toolbar.css",
            "/static/shared/chat-widget.css",
            "/static/css/style.css",
        ],
    )


def test_monitor_template_uses_shared_script_order_and_chat_widget():
    html = read_text(ROOT / "dx_monitor" / "templates" / "index.html")
    assert_ordered_tokens(
        html,
        [
            'src="/static/js/i18n.js',
            'src="/static/shared/i18n.js"',
            'src="/static/shared/toolbar.js"',
            "DXToolbar.init({ container: '.toolbar' });",
            'src="/static/js/utils.js',
            'src="/static/js/charts.js',
            'src="/static/js/dashboard.js',
            'src="/static/shared/tutorial-engine.js"',
            'src="/static/shared/tutorial-init.js"',
            'src="/static/js/tutorial.js',
            'src="/static/shared/chat-widget.js"',
            "DXChat.init({ appName: 'dx_monitor' });",
        ],
    )


def test_monitor_server_uses_route_common_after_chat_routes():
    source = read_text(ROOT / "dx_monitor" / "server.py")
    assert "static_dir = STATIC_DIR" in source
    assert "templates_dir = TEMPLATES_DIR" in source
    assert "if self.handle_chat_routes(_chat_engine):" in source
    assert "if self.route_common():" in source
    assert source.index("if self.handle_chat_routes(_chat_engine):") < source.index("if self.route_common():")
    assert 'path in ("/", "/index.html")' not in source
    assert "serve_shared_static" not in source
    assert "serve_static(" not in source
    assert "self.route_legacy()" in source


def test_modelzoo_template_uses_canonical_css_order():
    html = read_text(ROOT / "dx_modelzoo" / "templates" / "index.html")
    assert html.count('href="/static/shared/chat-widget.css"') == 1
    assert_ordered(
        html,
        FOUNDATION_HREFS
        + [
            "/static/shared/tutorial.css",
            "/static/shared/toolbar.css",
            "/static/shared/chat-widget.css",
            "/static/css/style.css",
        ],
    )
    assert html.index('src="/static/shared/chat-widget.js"') > html.index("<body")
    assert "DXChat.init({ appName: 'dx_modelzoo' });" in html


def test_monitor_css_no_longer_defines_shared_font_faces_or_tokens():
    monitor_css = read_text(ROOT / "dx_monitor" / "static" / "css" / "style.css")
    assert "@font-face" not in monitor_css
    assert "/static/fonts/" not in monitor_css
    assert ":root{" not in monitor_css
    assert "@keyframes dx-pulse" not in monitor_css
    assert "@keyframes dx-fade-in" not in monitor_css
    assert "@keyframes dx-spin" not in monitor_css


def test_modelzoo_css_no_longer_defines_shared_foundation():
    css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    assert_shared_foundation_removed(css)
    assert ":root{" not in css
    assert "@keyframes spin" not in css
    assert ".mz-topbar" in css
    assert ".mz-card" in css
    assert ".mz-detail-view" in css
    assert ".mz-btn" in css
    assert ".mz-logo" not in css, ".mz-logo is dead after brand migration"


def assert_local_topbar_token(css: str) -> None:
    # 로컬 topbar 변수는 반드시 --dx-module-header-h를 참조해야 한다
    has_shared_ref = "--topbar-h: var(--dx-module-header-h)" in css
    has_benchmark_ref = "--benchmark-topbar-h: var(--dx-module-header-h)" in css
    assert has_shared_ref or has_benchmark_ref, (
        "local topbar token must reference --dx-module-header-h"
    )


def assert_shared_foundation_removed(css: str) -> None:
    forbidden_fragments = [
        "@font-face",
        "/static/fonts/",
        "color-scheme: dark",
        "--bg-0:",
        "--bg-1:",
        "--font:",
        "--mono:",
        "scrollbar-color:",
        ":focus-visible",
        "::-webkit-scrollbar",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in css, fragment


def test_benchmark_template_uses_canonical_css_order():
    html = read_text(ROOT / "dx_benchmark" / "templates" / "index.html")
    assert "<body" in html
    assert html.index("</head>") < html.index("<body")
    assert html.count('href="/static/shared/chat-widget.css"') == 1
    assert_ordered(
        html,
        FOUNDATION_HREFS
        + [
            "/static/shared/tutorial.css",
            "/static/shared/toolbar.css",
            "/static/shared/chat-widget.css",
            "/static/css/style.css",
        ],
    )


def test_planner_template_uses_canonical_css_order():
    html = read_text(ROOT / "dx_planner" / "templates" / "index.html")
    assert_ordered(
        html,
        FOUNDATION_HREFS
        + [
            "/static/shared/tutorial.css",
            "/static/shared/toolbar.css",
            "/static/shared/chat-widget.css",
            "/static/css/style.css",
        ],
    )


def head_html(html: str) -> str:
    return html[: html.index("</head>")]


def test_stream_template_uses_canonical_css_order():
    html = read_text(ROOT / "dx_stream" / "templates" / "index.html")
    assert html.count('href="/static/shared/chat-widget.css"') == 1
    assert 'href="static/css/stream.css"' not in html
    assert 'href="static/css/pipeline-iso.css"' not in html
    assert_ordered(
        html,
        FOUNDATION_HREFS
        + [
            "/static/shared/tutorial.css",
            "/static/shared/toolbar.css",
            "/static/shared/chat-widget.css",
            "/static/css/stream.css",
            "/static/css/pipeline-iso.css",
        ],
    )
    assert html.index('src="/static/shared/chat-widget.js"') > html.index("<body")
    assert "DXChat.init({ appName: 'dx_stream' });" in html


def test_benchmark_css_no_longer_defines_shared_foundation():
    css = read_text(ROOT / "dx_benchmark" / "static" / "css" / "style.css")
    assert_shared_foundation_removed(css)
    assert_local_topbar_token(css)
    assert "body { overflow-x: auto; overflow-y: hidden; }" in css
    assert ".top-bar" in css
    assert ".main-tab" in css
    assert ".panel" in css
    assert "@keyframes slideIn" in css
    assert "@keyframes pulse" in css
    assert "@keyframes spin" in css


def test_planner_css_no_longer_defines_shared_foundation():
    css = read_text(ROOT / "dx_planner" / "static" / "css" / "style.css")
    assert_shared_foundation_removed(css)
    assert_local_topbar_token(css)
    assert "body { overflow-x: auto; overflow-y: hidden; }" in css
    assert ".planner-topbar" in css
    assert ".planner-main" in css
    assert ".cfg-card" in css
    assert ".task-btn" in css
    assert "animation: planner-fade-in .25s ease" in css
    assert "@keyframes planner-fade-in" in css
    assert "translateY(8px)" in css
    assert "@keyframes dx-pulse" not in css
    assert "@keyframes dx-fade-in" not in css
    assert "@keyframes dx-spin" not in css


def test_stream_css_no_longer_defines_shared_foundation():
    css = read_text(ROOT / "dx_stream" / "static" / "css" / "stream.css")
    assert_shared_foundation_removed(css)
    assert "color-scheme:dark" not in css
    assert "--stream-color:#10B981" in css
    assert "body{overflow-x:auto;overflow-y:hidden}" in css
    assert ".sidebar" in css
    assert ".topbar" in css
    assert ".stream-badge" in css
    assert ".demo-card.cat-stream" in css
    assert ".element-card" in css
    assert ".perf-chart-wrap" in css
    assert "#webrtc-stats-overlay" in css
    assert "@keyframes modalIn" in css
    assert "@keyframes sp" in css
    assert "@keyframes pulse-dot" in css
    assert "@keyframes spin" in css
    assert "@keyframes dx-pulse" not in css
    assert "@keyframes dx-fade-in" not in css
    assert "@keyframes dx-spin" not in css


def test_benchmark_server_uses_route_common_after_chat_routes():
    source = read_text(ROOT / "dx_benchmark" / "server.py")
    assert "if self.handle_chat_routes(_chat_engine):" in source
    assert "if self.route_common():" in source
    assert source.index("if self.handle_chat_routes(_chat_engine):") < source.index("if self.route_common():")
    assert 'path in ("/", "/index.html")' not in source
    assert "serve_shared_static" not in source
    assert "serve_static" not in source


def test_planner_server_uses_route_common_after_chat_routes():
    source = read_text(ROOT / "dx_planner" / "server.py")
    assert "if self.handle_chat_routes(_chat_engine):" in source
    assert "if self.route_common():" in source
    assert source.index("if self.handle_chat_routes(_chat_engine):") < source.index("if self.route_common():")
    assert 'path in ("/", "/index.html")' not in source
    assert "serve_shared_static" not in source
    assert "serve_static" not in source


def test_stream_server_uses_route_common_after_chat_routes():
    source = read_text(ROOT / "dx_stream" / "server.py")
    assert "static_dir = STATIC_DIR" in source
    assert "templates_dir = TEMPLATES_DIR" in source
    assert "if self.handle_chat_routes(_chat_engine):" in source
    assert "if self.route_common():" in source
    assert source.index("if self.handle_chat_routes(_chat_engine):") < source.index("if self.route_common():")
    assert 'path in ("/", "/index.html")' not in source
    assert "serve_shared_static" not in source
    assert "serve_static(" not in source
    assert "self.route_legacy()" in source


def test_modelzoo_server_uses_route_common_after_chat_routes_and_keeps_data_static():
    source = read_text(ROOT / "dx_modelzoo" / "server.py")
    assert "static_dir = STATIC_DIR" in source
    assert "templates_dir = TEMPLATES_DIR" in source
    assert "if self.handle_chat_routes(_chat_engine):" in source
    assert "if self.route_common():" in source
    assert source.index("if self.handle_chat_routes(_chat_engine):") < source.index("if self.route_common():")
    assert 'path == "/" or path == "/index.html"' not in source
    assert 'path in ("/", "/index.html")' not in source
    assert "serve_shared_static" not in source
    assert "serve_static(path[8:], STATIC_DIR)" not in source
    assert "serve_static(path[6:], DATA_DIR)" in source
    assert source.count("serve_static(") == 1


def test_compiler_template_uses_canonical_css_order():
    html = read_text(ROOT / "dx_compiler" / "templates" / "base.html")
    assert html.count('href="/static/shared/chat-widget.css"') == 1
    assert html.index('href="/static/shared/chat-widget.css"') < html.index("<body")
    assert_ordered(
        html,
        FOUNDATION_HREFS
        + [
            "/static/shared/tutorial.css",
            "/static/shared/toolbar.css",
            "/static/shared/chat-widget.css",
            "/static/css/graph_viewer.css?v={{ v }}",
            "/static/css/style.css?v={{ v }}",
        ],
    )


def test_compiler_dagre_js_not_interleaved_with_head_css_links():
    html = read_text(ROOT / "dx_compiler" / "templates" / "base.html")
    head = head_html(html)
    assert "dagre.min.js" not in head
    assert html.index('src="/static/js/dagre.min.js') > html.index("<body")


def test_compiler_css_no_longer_defines_shared_foundation():
    css = read_text(ROOT / "dx_compiler" / "static" / "css" / "style.css")
    forbidden_fragments = [
        "@font-face",
        "/static/fonts/",
        "color-scheme:dark",
        "color-scheme: dark",
        "--bg-0:",
        "--bg-1:",
        "--font:",
        "--mono:",
        "scrollbar-color:",
        ":focus-visible",
        "::-webkit-scrollbar{width:5px",
        "::-webkit-scrollbar { width: 5px",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in css, fragment

    for fragment in (
        "body{overflow-x:auto;overflow-y:hidden}",
        "#header",
        ".compile-form",
        ".dropzone",
        ".dxq-fieldset",
        ".progress-container",
        ".viewer-panel",
        ".viewer-tabs",
        ".viewer-sidebar",
        ".viewer-status-bar",
        ".explorer-content",
        ".search-dropdown",
        ".legend-dot-compute",
        ".ns-toolbar-btn",
        ".setup-panel",
        ".sample-dropdown",
        "body.lang-ko .en",
        "body.lang-ja .en",
        "body.lang-zh-CN .zh-TW",
        "::-webkit-scrollbar { width: 8px; height: 8px; }",
        ".log-content::-webkit-scrollbar",
        ".explorer-content::-webkit-scrollbar",
        ".search-dropdown::-webkit-scrollbar",
    ):
        assert fragment in css, fragment


def test_dx_app_template_uses_canonical_css_order():
    html = read_text(ROOT / "dx_app" / "templates" / "index.html")
    assert html.count('href="/static/shared/chat-widget.css"') == 1
    assert html.index('href="/static/shared/chat-widget.css"') < html.index("<body")
    assert_ordered_tokens(
        html,
        [
            'href="/static/shared/dx-fonts.css"',
            'href="/static/shared/dx-tokens.css"',
            'href="/static/shared/dx-base.css"',
            'href="/static/shared/dx-utilities.css"',
            'href="/static/shared/tutorial.css"',
            'href="/static/shared/toolbar.css"',
            'href="/static/shared/chat-widget.css"',
            'href="/static/css/style.css',
        ],
    )


def test_dx_app_template_uses_shared_script_order_and_chat_widget():
    html = read_text(ROOT / "dx_app" / "templates" / "index.html")
    assert '<div class="topbar-right toolbar">' in html
    assert "DXToolbar.init({ container: '.toolbar'" in html
    assert "DXToolbar.init({ container: '.topbar-right'" not in html
    assert_ordered_tokens(
        html,
        [
            'src="/static/js/i18n.js',
            'src="/static/shared/i18n.js"',
            'src="/static/shared/toolbar.js"',
            "DXToolbar.init({ container: '.toolbar'",
            'src="/static/js/utils.js',
            'src="/static/js/reference.js',
            'src="/static/shared/tutorial-engine.js"',
            'src="/static/shared/tutorial-init.js"',
            'src="/static/js/tutorial.js',
            'src="/static/shared/chat-widget.js"',
            "DXChat.init({ appName: 'dx_app' });",
        ],
    )


def test_dx_app_css_no_longer_defines_shared_foundation():
    css = read_text(ROOT / "dx_app" / "static" / "css" / "style.css")
    assert_shared_foundation_removed(css)
    assert ":root{" not in css
    assert "color-scheme" not in css
    assert "@font-face" not in css
    assert "/static/fonts/" not in css
    assert "@keyframes dx-pulse" not in css
    assert "@keyframes dx-fade-in" not in css
    assert "@keyframes dx-spin" not in css
    for selector in (
        ".app",
        ".sidebar",
        ".topbar",
        ".topbar-right",
        ".toolbar",
        ".nav-item",
        ".content-wrap",
        ".card",
        ".btn",
        ".ref-layout",
        ".ref-topic-card",
    ):
        assert selector in css, selector


def test_compiler_server_route_order():
    source = read_text(ROOT / "dx_compiler" / "server.py")
    assert "static_dir = STATIC_DIR" in source
    assert "if self.handle_chat_routes(_chat_engine):" in source
    assert "if self.route_common():" in source
    assert source.index("if self.handle_chat_routes(_chat_engine):") < source.index("if self.route_common():")
    assert source.index('path in ("/", "/index.html")') < source.index("if self.route_common():")
    assert "html = self._render(\"index.html\")" in source
    assert "self.send_error_json(404, \"Not found\")" in source
    assert "serve_shared_static" not in source
    assert "serve_static(rel, STATIC_DIR)" not in source


def test_launcher_template_uses_canonical_css_order():
    html = read_text(ROOT / "launcher" / "static" / "index.html")
    assert html.count('href="/static/shared/chat-widget.css"') == 1
    assert html.index("</head>") < html.index("<body")
    assert_ordered(
        html,
        FOUNDATION_HREFS
        + [
            "/static/shared/tutorial.css",
            "/static/shared/toolbar.css",
            "/static/shared/chat-widget.css",
            "/style.css",
            "/about-deepx.css?v=2",
            "/sdk-library.css?v=9",
        ],
    )


def test_launcher_css_no_longer_defines_shared_foundation():
    css = read_text(ROOT / "launcher" / "static" / "style.css")
    # Launcher-specific forbidden list (not the shared helper, which bans all
    # :focus-visible including component-specific focus rings launcher needs).
    for fragment in (
        "@font-face",
        "/static/fonts/",
        "color-scheme: dark",
        "--bg-0:",
        "--bg-1:",
        "--font:",
        "--mono:",
        "scrollbar-color:",
        "::-webkit-scrollbar",
        "\n:focus-visible",
    ):
        assert fragment not in css, fragment
    assert "* { margin: 0; padding: 0; box-sizing: border-box; }" not in css
    for alias in (
        "--bg-surface:",
        "--bg-card:",
        "--bg-card-hover:",
        "--text:",
        "--text-muted:",
        "--text-dim:",
        "--border-glow:",
        "--app-color:",
        "--stream-color:",
        "--sandbox-color:",
        "--zoo-color:",
    ):
        assert alias in css, alias
    for selector in (
        ".top-bar",
        ".top-bar-right",
        ".status-dots",
        ".launch-card",
        ".splash-overlay",
    ):
        assert selector in css, selector
    for selector in (
        ".settings-dialog",
        ".settings-field",
        ".settings-actions",
        ".settings-status",
        ".settings-test-btn",
        ".settings-save-btn",
    ):
        assert selector not in css, selector
    # Component-specific focus rings must be preserved.
    for selector in (
        ".about-book-card:focus-visible",
        ".orbital-card:focus-visible",
    ):
        assert selector in css, selector


def test_launcher_server_uses_guarded_shared_chat_routes():
    source = read_text(ROOT / "launcher" / "launcher.py")
    assert "from shared.chat import ChatEngine" in source
    assert '_chat_engine = ChatEngine(app_name="launcher")' in source
    assert 'headers["X-Forwarded-Host"] = handler.headers.get("Host", "")' in source
    assert "def _has_subapp_referer(" in source
    assert "def _chat_endpoint_for_path(" in source
    assert "def _is_launcher_chat_request(" in source
    assert "if self._is_launcher_chat_request(path):" in source
    assert "if self.handle_chat_routes(_chat_engine):" in source
    assert source.index("def _has_subapp_referer(") < source.index("if self.handle_chat_routes(_chat_engine):")
    assert source.index("Referer") < source.index("if self.handle_chat_routes(_chat_engine):")
    # POST config/test routes are now delegated to shared handler, not duplicated.
    assert 'path == "/api/chat/config" and self.command == "POST"' not in source
    assert 'path == "/api/chat/config/test" and self.command == "POST"' not in source
    assert "save_config(" not in source
    assert "stream_chat(" not in source
    assert '"/api/chat",' in source
    assert "route_common()" not in source


def test_shared_dx_server_owns_chat_config_routes():
    """shared/dx_server.py의 handle_chat_routes()가 POST config/test 라우트를 소유."""
    shared_source = read_text(ROOT / "shared" / "dx_server.py")
    assert 'self.url_path == "/api/chat/config"' in shared_source
    assert 'self.url_path == "/api/chat/config/test"' in shared_source
    assert "save_config(" in shared_source
    assert "stream_chat(" in shared_source


def test_shared_chat_widget_owns_settings_panel_and_config_api():
    """chat-widget.js가 설정 패널과 config save/test API 호출을 소유."""
    source = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.js")
    assert 'data-action="settings"' in source
    assert 'class="dx-chat-settings-panel"' in source
    assert 'class="dx-chat-settings-form"' in source
    assert "function _openSettingsPanel()" in source
    assert "function _saveSettings(" in source
    assert "function _testSettingsConnection()" in source
    assert "fetch(_apiUrl('/api/chat/config'))" in source
    assert "fetch(_apiUrl('/api/chat/config'), {" in source
    assert "fetch(_apiUrl('/api/chat/config/test'), {" in source
    assert "Launcher → Settings" not in source
    assert ".value = data.api_key" not in source
    assert "chatApiKey.value = ''" in source


def test_shared_chat_widget_has_provider_specific_model_hints():
    """Provider별 model placeholder가 잘못된 OpenAI 기본값으로 고정되지 않아야 한다."""
    source = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.js")
    assert "const modelHints = {" in source
    assert "anthropic: 'claude-3-5-haiku-20241022'" in source
    assert "google: 'gemini-1.5-flash'" in source
    assert "custom: 'your-model-name'" in source
    assert "provider === 'github' ? 'gpt-4o-mini' : 'gpt-4o-mini'" not in source


def test_shared_chat_widget_retranslates_banner_without_refetching_config():
    """언어 변경은 배너 문구만 갱신하고 config API를 다시 호출하지 않는다."""
    source = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.js")
    assert "function _renderConfigBanner()" in source
    start = source.index("DXI18n.onLangChange(function() {")
    end = source.index("_history.forEach(m => _renderMessage", start)
    handler = source[start:end]
    assert "_renderConfigBanner();" in handler
    assert "_checkConfig();" not in handler


def test_shared_chat_widget_styles_settings_panel():
    """chat-widget.css가 widget 내부 설정 패널 스타일을 포함."""
    css = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.css")
    for selector in (
        ".dx-chat-settings-panel",
        ".dx-chat-settings-form",
        ".dx-chat-settings-field",
        ".dx-chat-settings-actions",
        ".dx-chat-settings-status",
        ".dx-chat-banner-action",
    ):
        assert selector in css, selector


def test_launcher_no_longer_owns_chat_settings_ui():
    """상단 toolbar/launcher가 chatbot 설정 dialog와 저장 로직을 소유하지 않아야 한다."""
    html = read_text(ROOT / "launcher" / "static" / "index.html")
    launcher_js = read_text(ROOT / "launcher" / "static" / "launcher.js")
    sdk_library_js = read_text(ROOT / "launcher" / "static" / "sdk-library.js")

    for token in (
        "chatSettingsDialog",
        "chatSettingsForm",
        "AI Assistant Settings",
        "saveChatSettings(",
        "testChatConnection()",
        "onSettings:",
        "openSettings()",
    ):
        assert token not in html, token

    for token in (
        "function openSettings(",
        "function closeSettings(",
        "function saveChatSettings(",
        "function testChatConnection(",
        "chatSettingsStatus",
        "_GITHUB_MODEL_HINT",
        "fetch('/api/chat/config'",
        "fetch('/api/chat/config/test'",
    ):
        assert token not in launcher_js, token

    for token in (
        "openSettings",
        "settingsBtn",
        "Settings",
        "⚙️ settings",
    ):
        assert token not in sdk_library_js, token


def test_shared_chat_runtime_messages_reference_widget_settings():
    """fallback/error 문구는 더 이상 Launcher Settings를 안내하지 않는다."""
    fallback_source = read_text(ROOT / "shared" / "chat" / "fallback.py")
    engine_source = read_text(ROOT / "shared" / "chat" / "engine.py")
    widget_source = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.js")
    sdk_library_js = read_text(ROOT / "launcher" / "static" / "sdk-library.js")

    for source in (fallback_source, engine_source, widget_source):
        assert "Launcher Settings" not in source
        assert "Launcher → Settings" not in source

    assert "chat settings" in fallback_source
    assert "채팅 설정" in fallback_source
    assert "chat settings" in engine_source
    assert "채팅 설정" in engine_source
    assert "_t('Temperature', '온도')" in widget_source
    assert "⚙️ settings" not in sdk_library_js


def test_tutorial_auto_runs_by_default_and_opts_out_on_explicit_off():
    """Tutorial is ON by default: auto-runs unless the user explicitly turned it off.
    The launcher auto-starts the walkthrough once (first-run guard), then falls back to TOC."""
    tutorial_init = read_text(ROOT / "shared" / "static" / "tutorial-init.js")
    assert "dx-tutorial-mode" in tutorial_init
    assert "tutMode === 'off'" in tutorial_init          # opt out only on an explicit "off"
    assert "dx-tutorial-launcher-autostarted" in tutorial_init  # first-run auto-start guard
    assert "engine.startAll()" in tutorial_init          # first run → walkthrough
    assert "engine.showTOC()" in tutorial_init            # later / modules → table of contents


def test_dx_app_topbar_title_is_owned_by_navigation_not_bulk_i18n():
    """App navigation title must not be reset to the first translated value by bulk applyLang."""
    app_i18n = read_text(ROOT / "dx_app" / "static" / "js" / "i18n.js")
    app_utils = read_text(ROOT / "dx_app" / "static" / "js" / "utils.js")
    selector_block = re.search(r"window\._DX_I18N_SELECTORS\s*=\s*\[(?P<body>.*?)\]\.join", app_i18n, re.S)
    assert selector_block is not None
    assert ".topbar-title" not in selector_block.group("body")
    assert "const PAGE_TITLES" in app_utils
    for title in ("Setup & Install", "Models", "Run Inference", "Benchmark", "A/B Compare"):
        assert title in app_utils


def test_shared_brand_assets_define_component_contract():
    css = read_text(ROOT / "shared" / "static" / "brand.css")
    js = read_text(ROOT / "shared" / "static" / "brand.js")
    assert ".dx-brand" in css
    assert ".dx-brand-prefix" in css
    assert "font-size: var(--fs-2xl)" in css
    assert "font-weight: 800" in css
    assert ".dx-brand-name" in css
    assert "font-size: var(--fs-lg)" in css
    assert "font-weight: 700" in css
    assert ".dx-brand-subtitle" in css
    assert "font-size: var(--fs-2xs)" in css
    assert "letter-spacing: 1px" in css
    # topbar gap이 간격을 담당하므로 page title은 margin-left를 가지면 안 된다.
    page_title_rule = re.search(r"\.dx-brand-page-title\s*\{(?P<body>.*?)\}", css, re.S).group("body")
    assert "margin-left" not in page_title_rule, "margin-left causes double spacing with topbar gap"
    assert "padding-left: 14px" in page_title_rule
    assert "window.DXBrand" in js
    assert "function mount" in js
    assert "document.createElement(safeHref ? 'a' : 'div')" in js
    assert "DXI18n.onLangChange" in js
    assert "console.warn" in js
    assert "subtitle.en" in js
    # safe href는 /, http://, https://만 허용한다.
    assert "function isSafeHref" in js
    assert ("href.charAt(0) === '/'" in js or "href.indexOf('/') === 0" in js), "allowlist must check /"
    assert "href.indexOf('https://') === 0" in js, "allowlist must check https://"
    assert "href.indexOf('http://') === 0" in js, "allowlist must check http://"
    assert "homeHref ignored" in js
    # 같은 target에 중복 mount하면 기존 brand를 재사용한다.
    assert "target.querySelector('.dx-brand')" in js
    assert "already mounted" in js


def assert_loads_shared_brand_after_i18n(html: str, rel: str) -> None:
    assert 'href="/static/shared/brand.css' in html, rel
    assert 'src="/static/shared/brand.js' in html, rel
    assert_ordered_tokens(html, [
        'src="/static/shared/i18n.js',
        'src="/static/shared/brand.js',
    ])


def test_module_chrome_metrics_are_shared_and_loaded():
    chrome_css = read_text(ROOT / "shared" / "static" / "module-chrome.css")
    assert "--dx-module-header-h: 56px" in chrome_css
    assert "--dx-module-header-px: 24px" in chrome_css
    assert "--dx-module-header-gap: var(--sp-4)" in chrome_css
    assert "--dx-module-header-shadow: 0 1px 12px rgba(0,0,0,.3)" in chrome_css

    affected_templates = {
        "dx_compiler/templates/base.html": 'href="/static/css/style.css',
        "dx_app/templates/index.html": 'href="/static/css/style.css',
        "dx_stream/templates/index.html": 'href="/static/css/stream.css',
    }
    for rel, local_token in affected_templates.items():
        html = read_text(ROOT / rel)
        assert_ordered_tokens(html, [
            'href="/static/shared/dx-utilities.css',
            'href="/static/shared/module-chrome.css',
            'href="/static/shared/brand.css',
            'href="/static/shared/toolbar.css',
            'href="/static/shared/chat-widget.css',
            local_token,
        ])


def test_compiler_app_stream_use_module_chrome_metrics():
    compiler_css = read_text(ROOT / "dx_compiler" / "static" / "css" / "style.css")
    app_css = read_text(ROOT / "dx_app" / "static" / "css" / "style.css")
    stream_css = read_text(ROOT / "dx_stream" / "static" / "css" / "stream.css")

    compiler_header = re.search(r"#header\s*\{(?P<body>.*?)\}", compiler_css, re.S).group("body")
    compiler_left = re.search(r"\.header-left\s*\{(?P<body>.*?)\}", compiler_css, re.S).group("body")
    assert "height: var(--dx-module-header-h)" in compiler_header
    assert "padding: 0 var(--dx-module-header-px)" in compiler_header
    assert "box-shadow: var(--dx-module-header-elevation)" in compiler_header
    assert "gap: var(--dx-module-header-gap)" in compiler_left

    for css in (app_css, stream_css):
        sidebar_brand = re.search(r"\.sidebar-brand\s*\{(?P<body>.*?)\}", css, re.S).group("body")
        topbar = re.search(r"\.topbar\s*\{(?P<body>.*?)\}", css, re.S).group("body")
        assert "height: var(--dx-module-header-h)" in sidebar_brand
        assert "height: var(--dx-module-header-h)" in topbar
        assert "min-height: var(--dx-module-header-h)" in topbar
        assert "box-shadow: var(--dx-module-header-elevation)" in topbar


def test_app_stream_use_sidebar_brand_for_position_alignment():
    for rel in ("dx_app/templates/index.html", "dx_stream/templates/index.html"):
        html = read_text(ROOT / rel)
        assert_loads_shared_brand_after_i18n(html, rel)
        assert "DXBrand.mount({" in html
        sidebar_start = html.index('id="sidebar"')
        brand_pos = html.index('id="dxBrand"')
        nav_pos = html.index('class="nav-section"')
        assert sidebar_start < brand_pos < nav_pos, f"{rel} brand must be inside sidebar before nav"

        topbar_match = re.search(r'<div class="topbar-left">(?P<body>.*?)</div>', html, re.S)
        assert topbar_match is not None, rel
        assert 'id="dxBrand"' not in topbar_match.group("body"), f"{rel} brand must not sit right of sidebar"
        assert "dx-brand-page-title" not in topbar_match.group("body"), rel

        assert "sidebar-brand" in html, rel
        assert "logo-dx" not in html, rel
        assert "logo-text" not in html, rel
        assert 'class="dx-brand-slot"' in html
        # brand.js가 inline mount 호출보다 먼저 로드되어야 한다.
        assert_ordered_tokens(html, [
            'src="/static/shared/brand.js',
            'DXBrand.mount({',
        ])
        mount_match = re.search(r"DXBrand\.mount\(\{(?P<body>.*?)\}\);", html, re.S)
        assert mount_match is not None, rel
        mount_block = mount_match.group("body")
        for lang in ("ko", "en", "ja", "zh-CN", "zh-TW"):
            assert f"{lang}:" in mount_block or f"'{lang}':" in mount_block
    # 기존 sidebar logo 전용 selector는 App/Stream CSS에 남기지 않고, 새 wrapper만 사용한다.
    old_logo_patterns = (
        r"\.logo-dx\b",
        r"\.logo-text\b",
        r"\.sidebar\.collapsed\s+\.logo\b",
        r"\.sidebar\.collapsed\s+\.logo-text\b",
    )
    for css_rel in ("dx_app/static/css/style.css", "dx_stream/static/css/stream.css"):
        css_path = ROOT / css_rel
        assert css_path.is_file(), css_rel
        css_content = read_text(css_path)
        assert ".sidebar-brand" in css_content, f"missing sidebar brand wrapper in {css_rel}"
        assert "height:var(--dx-module-header-h)" in css_content.replace(" ", ""), f"{css_rel} sidebar brand must align with shared module header height"
        assert "padding:0 24px" in css_content or "padding: 0 24px" in css_content, f"{css_rel} sidebar brand should center within shared header"
        for pattern in old_logo_patterns:
            assert re.search(pattern, css_content) is None, f"old logo selector {pattern} still in {css_rel}"


def test_brand_topbars_use_unified_metrics_and_shadow():
    """Topbar형 모듈 brand 영역은 같은 높이와 shadow를 사용한다."""
    planner_css = read_text(ROOT / "dx_planner" / "static" / "css" / "style.css")
    benchmark_css = read_text(ROOT / "dx_benchmark" / "static" / "css" / "style.css")
    monitor_css = read_text(ROOT / "dx_monitor" / "static" / "css" / "style.css")
    modelzoo_css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    sdk_css = read_text(ROOT / "launcher" / "static" / "sdk-library.css")
    compiler_css = read_text(ROOT / "dx_compiler" / "static" / "css" / "style.css")

    for css in (planner_css, benchmark_css):
        has_shared = "--topbar-h: var(--dx-module-header-h)" in css
        has_benchmark = "--benchmark-topbar-h: var(--dx-module-header-h)" in css
        assert has_shared or has_benchmark
    assert "height: var(--dx-module-header-h)" in monitor_css
    assert "top: var(--dx-module-header-h)" in monitor_css
    assert "height: var(--dx-module-header-h)" in compiler_css
    for css in (planner_css, benchmark_css, monitor_css, sdk_css, compiler_css, modelzoo_css):
        assert "box-shadow: var(--dx-module-header-elevation)" in css


def test_modules_load_shared_brand_assets_and_mount_brand():
    modules = {
        "dx_modelzoo/templates/index.html": "Model Zoo",
        "dx_compiler/templates/base.html": "Compiler",
        "dx_planner/templates/index.html": "EdgeGuide",
        "dx_benchmark/templates/index.html": "Benchmark",
        "dx_monitor/templates/index.html": "Monitor",
    }
    for rel, name in modules.items():
        html = read_text(ROOT / rel)
        assert_loads_shared_brand_after_i18n(html, rel)
        assert "DXBrand.mount({" in html, rel
        assert_ordered_tokens(html, [
            'src="/static/shared/brand.js',
            'DXBrand.mount({',
        ])
        assert f"name: '{name}'" in html or f'name: "{name}"' in html
        mount_match = re.search(r"DXBrand\.mount\(\{(?P<body>.*?)\}\);", html, re.S)
        assert mount_match is not None, rel
        mount_block = mount_match.group("body")
        for lang in ("ko", "en", "ja", "zh-CN", "zh-TW"):
            assert f"{lang}:" in mount_block or f"'{lang}':" in mount_block
    modelzoo_html = read_text(ROOT / "dx_modelzoo/templates/index.html")
    assert re.search(r'<span class="logo-text">\s*Model Zoo', modelzoo_html) is None


def test_sdk_library_uses_shared_brand_without_about_deepx():
    html = read_text(ROOT / "launcher" / "static" / "index.html")
    sdk_css = read_text(ROOT / "launcher" / "static" / "sdk-library.css")
    sdk_js = read_text(ROOT / "launcher" / "static" / "sdk-library.js")
    sdk_match = re.search(r'<section id="sdk-library-view">(?P<body>.*?)</section>', html, re.S)
    about_match = re.search(r'<section id="about-view">(?P<body>.*?)</section>', html, re.S)
    assert sdk_match is not None
    assert about_match is not None
    sdk_section = sdk_match.group("body")
    about_section = about_match.group("body")
    assert_loads_shared_brand_after_i18n(html, "launcher/static/index.html")
    assert 'class="sdk-library-topbar"' not in sdk_section
    assert 'id="sdkBrand"' not in sdk_section

    # SDK는 중복 topbar 없이 기존 기능 topbar 안에서 shared brand를 mount한다.
    assert "header.className = 'sdk-topbar'" in sdk_js
    assert 'class="dx-brand-slot" id="sdkBrand"' in sdk_js
    assert "sdk-logo" not in sdk_js
    assert ".sdk-logo" not in sdk_css
    assert ".sdk-library-topbar" not in sdk_css
    assert "DXBrand.mount({" not in html
    assert "DXBrand.mount({" in sdk_js
    assert "typeof DXBrand === 'undefined'" in sdk_js or "typeof DXBrand !== 'undefined'" in sdk_js
    assert "#50dce8" not in sdk_js
    assert "accent: 'var(--accent)'" in sdk_js or 'accent: "var(--accent)"' in sdk_js

    # #sdkBrand 타겟에 앵커된 mount 블록 검증
    mount_match = re.search(
        r"DXBrand\.mount\(\{(?P<body>.*?target:\s*['\"]#sdkBrand['\"].*?)\}\);",
        sdk_js,
        re.S,
    )
    assert mount_match is not None
    mount_block = mount_match.group("body")
    for lang in ("ko", "en", "ja", "zh-CN", "zh-TW"):
        assert f"{lang}:" in mount_block or f"'{lang}':" in mount_block
    assert "homeHref:" not in mount_block
    assert "DXBrand.mount" not in about_section


def test_launcher_and_sdk_topbars_share_height_variable():
    launcher_css = read_text(ROOT / "launcher" / "static" / "style.css")
    sdk_css = read_text(ROOT / "launcher" / "static" / "sdk-library.css")
    assert "--launcher-topbar-h" in launcher_css
    assert "height: var(--launcher-topbar-h)" in launcher_css
    assert "top: var(--launcher-topbar-h)" in sdk_css


def test_about_topbar_nav_constrains_width_on_tablet():
    css = read_text(ROOT / "launcher" / "static" / "about-deepx.css")
    topbar_left = re.search(r"\.about-topbar-left\s*\{(?P<body>.*?)\}", css, re.S)
    nav = re.search(r"\.about-nav\s*\{(?P<body>.*?)\}", css, re.S)
    tab = re.search(r"\.about-nav-tab\s*\{(?P<body>.*?)\}", css, re.S)
    assert topbar_left is not None
    assert nav is not None
    assert tab is not None

    assert "flex: 0 0 auto" in topbar_left.group("body")
    nav_body = nav.group("body")
    assert "flex: 1 1 auto" in nav_body
    assert "min-width: 0" in nav_body
    assert "overflow-x: auto" in nav_body
    assert "white-space: nowrap" in nav_body
    tab_body = tab.group("body")
    assert "flex: 0 0 auto" in tab_body
    assert "white-space: nowrap" in tab_body


BRAND_SLOT_BLOCK_TEMPLATES = (
    "dx_app/templates/index.html",
    "dx_stream/templates/index.html",
    "dx_compiler/templates/base.html",
    "dx_planner/templates/index.html",
    "dx_benchmark/templates/index.html",
    "dx_monitor/templates/index.html",
)


def test_touched_modules_use_block_brand_slots():
    for rel in BRAND_SLOT_BLOCK_TEMPLATES:
        html = read_text(ROOT / rel)
        assert '<div class="dx-brand-slot"' in html, rel
        assert '<span class="dx-brand-slot"' not in html, rel


def test_modelzoo_brand_slot_semantic_cleanup_is_deferred():
    html = read_text(ROOT / "dx_modelzoo/templates/index.html")
    assert 'class="dx-brand-slot"' in html


def test_shared_brand_css_load_order_is_consistent_for_touched_modules():
    for rel in BRAND_SLOT_BLOCK_TEMPLATES + ("launcher/static/index.html",):
        html = read_text(ROOT / rel)
        assert_ordered_tokens(html, [
            'href="/static/shared/module-chrome.css',
            'href="/static/shared/brand.css',
            'href="/static/shared/tutorial.css',
            'href="/static/shared/toolbar.css',
            'href="/static/shared/chat-widget.css',
        ])


def test_sdk_library_shell_uses_deepx_tokens_not_github_palette():
    css = read_text(ROOT / "launcher" / "static" / "sdk-library.css")
    shell_blocks = "\n".join(
        block.group(0)
        for block in re.finditer(r"\.(sdk-topbar|sdk-list-sidebar|sdk-sidebar-section|sdk-topbar-search|sdk-toggle-btn|sdk-topbar-btn)[^{]*\{[^}]*\}", css, re.S)
    )
    for forbidden in ("#0d1117", "#21262d", "#30363d", "#58a6ff", "rgba(13,17,23"):
        assert forbidden not in shell_blocks
    for token in ("var(--bg-", "var(--border", "var(--accent", "var(--text-"):
        assert token in shell_blocks




def _css_rule(css: str, selector: str) -> str:
    """Return the body (content between braces) of the first rule matching *selector*."""
    # Escape special regex chars in selector, then find the block.
    escaped = re.escape(selector)
    m = re.search(escaped + r"\s*\{([^}]*)\}", css)
    assert m is not None, f"selector {selector!r} not found in CSS"
    return m.group(1)


def _css_rule_last(css: str, selector: str) -> str:
    """Return the body of the last matching rule so late overrides are covered."""
    escaped = re.escape(selector)
    matches = list(re.finditer(r"^\s*" + escaped + r"\s*\{([^}]*)\}", css, re.M | re.S))
    assert matches, f"selector {selector!r} not found in CSS"
    return matches[-1].group(1)


def test_shared_depth_tokens_define_surface_contract():
    """dx-tokens.css와 dx-utilities.css가 통합 깊이 토큰/유틸리티를 제공한다."""
    tokens_css = read_text(SHARED_STATIC / "dx-tokens.css")
    utilities_css = read_text(SHARED_STATIC / "dx-utilities.css")

    # 토큰 존재 확인
    for token in (
        "--inset-highlight:",
        "--inset-highlight-strong:",
        "--shadow-sm:",
        "--shadow-xl:",
        "--surface-raised-bg:",
        "--surface-raised-shadow:",
        "--surface-glass-shadow:",
        "--surface-active-shadow:",
        "--surface-hover-shadow:",
        "--text-glow-accent:",
    ):
        assert token in tokens_css, f"token {token} missing from dx-tokens.css"

    # 유틸리티 셀렉터 존재 확인
    for sel in (".dx-surface-raised", ".dx-surface-glass", ".dx-surface-active", ".dx-text-glow"):
        assert sel in utilities_css, f"selector {sel} missing from dx-utilities.css"

    # 유틸리티 정확한 프래그먼트 확인
    assert "background: var(--surface-raised-bg)" in utilities_css
    assert "box-shadow: var(--surface-raised-shadow)" in utilities_css


def test_module_chrome_depth_contract_is_token_only_and_loaded():
    """module-chrome.css가 깊이 토큰을 정의하고, 모든 템플릿이 올바른 순서로 로드한다."""
    chrome_css = read_text(SHARED_STATIC / "module-chrome.css")

    # 깊이 토큰 존재
    assert "--dx-module-header-glow:" in chrome_css
    assert "--dx-module-header-elevation:" in chrome_css

    # module-chrome.css는 box-shadow 선언을 직접 가지지 않음 (토큰만 정의)
    assert "box-shadow: var(--dx-module-header-elevation)" not in chrome_css

    # module-chrome.css가 bare topbar 셀렉터를 정의하지 않음
    for sel in (".top-bar", ".topbar", ".header", "#header"):
        pattern = re.escape(sel) + r"\s*\{"
        assert re.search(pattern, chrome_css) is None, (
            f"module-chrome.css must not define bare selector {sel}"
        )

    # 템플릿 로드 순서 검증
    TEMPLATE_LOAD_ORDER = {
        "launcher/static/index.html": 'href="/style.css',
        "dx_modelzoo/templates/index.html": 'href="/static/css/style.css',
        "dx_planner/templates/index.html": 'href="/static/css/style.css',
        "dx_benchmark/templates/index.html": 'href="/static/css/style.css',
        "dx_monitor/templates/index.html": 'href="/static/css/style.css',
        "dx_app/templates/index.html": 'href="/static/css/style.css',
        "dx_stream/templates/index.html": 'href="/static/css/stream.css',
        "dx_compiler/templates/base.html": 'href="/static/css/style.css',
    }
    shared_order = [
        'href="/static/shared/dx-utilities.css',
        'href="/static/shared/module-chrome.css',
        'href="/static/shared/brand.css',
        'href="/static/shared/tutorial.css',
        'href="/static/shared/toolbar.css',
        'href="/static/shared/chat-widget.css',
    ]
    for rel, local_token in TEMPLATE_LOAD_ORDER.items():
        html = read_text(ROOT / rel)
        assert_ordered_tokens(html, shared_order + [local_token])


def test_all_module_topbars_use_shared_depth_elevation():
    """모든 모듈의 topbar가 공유 깊이 토큰을 사용한다."""
    TOPBAR_SPECS = [
        ("launcher/static/style.css", ".top-bar"),
        ("launcher/static/sdk-library.css", ".sdk-topbar"),
        ("launcher/static/about-deepx.css", ".about-topbar"),
        ("dx_app/static/css/style.css", ".topbar"),
        ("dx_stream/static/css/stream.css", ".topbar"),
        ("dx_modelzoo/static/css/style.css", ".mz-topbar"),
        ("dx_compiler/static/css/style.css", "#header"),
        ("dx_planner/static/css/style.css", ".planner-topbar"),
        ("dx_benchmark/static/css/style.css", ".top-bar"),
        ("dx_monitor/static/css/style.css", ".top-bar"),
    ]
    for css_rel, selector in TOPBAR_SPECS:
        css = read_text(ROOT / css_rel)
        body = _css_rule(css, selector)
        assert "background: var(--dx-module-header-bg)" in body, (
            f"{css_rel} {selector} missing background token"
        )
        assert "border-bottom: 1px solid var(--dx-module-header-border)" in body, (
            f"{css_rel} {selector} missing border token"
        )
        assert "box-shadow: var(--dx-module-header-elevation)" in body, (
            f"{css_rel} {selector} missing elevation token"
        )


def test_flat_modules_use_shared_surface_depth_tokens():
    """카드/패널 등 평면 모듈이 공유 surface 깊이 토큰을 사용한다."""
    # 기본 raised surface 검증
    RAISED_SPECS = [
        ("dx_benchmark/static/css/style.css", [".panel", ".card", ".stat-card", ".meta-card", ".controls"]),
        ("dx_compiler/static/css/style.css", [".compile-form", ".progress-container", ".mode-card"]),
        ("dx_modelzoo/static/css/style.css", [".mz-detail-header", ".mz-detail-section", ".mz-inference-panel"]),
        ("launcher/static/about-deepx.css", [".about-value-card", ".about-quote"]),
    ]
    for css_rel, selectors in RAISED_SPECS:
        css = read_text(ROOT / css_rel)
        for sel in selectors:
            body = _css_rule(css, sel)
            assert "background: var(--surface-raised-bg)" in body, (
                f"{css_rel} {sel} missing surface-raised-bg"
            )
            assert "box-shadow: var(--surface-raised-shadow)" in body, (
                f"{css_rel} {sel} missing surface-raised-shadow"
            )

    # active state 검증
    ACTIVE_SPECS = [
        ("dx_benchmark/static/css/style.css", ".main-tab.active"),
        ("dx_app/static/css/style.css", ".nav-item.active"),
        ("dx_stream/static/css/stream.css", ".nav-item.active"),
        ("dx_planner/static/css/style.css", ".task-btn.selected"),
        ("dx_planner/static/css/style.css", ".size-btn.selected"),
    ]
    for css_rel, sel in ACTIVE_SPECS:
        css = read_text(ROOT / css_rel)
        body = _css_rule(css, sel)
        assert "box-shadow: var(--surface-active-shadow)" in body, (
            f"{css_rel} {sel} missing surface-active-shadow"
        )


def test_app_stream_sidebar_brand_uses_shared_header_depth():
    """App/Stream의 좌측 브랜드 영역도 상단 chrome과 같은 depth를 사용한다."""
    for css_rel in ("dx_app/static/css/style.css", "dx_stream/static/css/stream.css"):
        css = read_text(ROOT / css_rel)
        body = _css_rule(css, ".sidebar-brand")
        assert "background: var(--dx-module-header-bg)" in body, (
            f"{css_rel} .sidebar-brand missing shared header background"
        )
        assert "border-bottom: 1px solid var(--dx-module-header-border)" in body, (
            f"{css_rel} .sidebar-brand missing shared header border"
        )
        assert "box-shadow: var(--dx-module-header-elevation)" in body, (
            f"{css_rel} .sidebar-brand missing shared header elevation"
        )


def test_app_stream_final_card_rules_use_shared_raised_depth():
    """App/Stream의 실제 최종 카드 rule이 hard-coded gradient로 depth를 덮어쓰지 않는다."""
    SURFACE_SPECS = {
        "dx_app/static/css/style.css": [
            ".card",
            ".stat",
            ".detail-info-card",
            ".pp-card",
            ".setup-card",
            ".pcard",
            ".npu-card",
            ".plan-sc",
            ".comp-result-card",
            ".forum-item",
            ".ref-topic-card",
        ],
        "dx_stream/static/css/stream.css": [
            ".card",
            ".stat",
            ".setup-card",
            ".demo-card",
            ".ref-topic-card",
        ],
    }
    for css_rel, selectors in SURFACE_SPECS.items():
        css = read_text(ROOT / css_rel)
        for selector in selectors:
            body = _css_rule_last(css, selector)
            assert "background: var(--surface-raised-bg)" in body, (
                f"{css_rel} {selector} final rule missing surface-raised-bg"
            )
            assert "box-shadow: var(--surface-raised-shadow)" in body, (
                f"{css_rel} {selector} final rule missing surface-raised-shadow"
            )


def test_app_stream_local_css_urls_bust_pre_depth_cache():
    """App/Stream은 이전 CSS URL과 달라야 기존 브라우저 캐시가 depth 변경을 가리지 않는다."""
    app_html = read_text(ROOT / "dx_app" / "templates" / "index.html")
    stream_html = read_text(ROOT / "dx_stream" / "templates" / "index.html")

    assert 'href="/static/css/style.css?m=dx_app_mzhdr' in app_html
    assert 'href="/static/css/stream.css?m=dx_stream_depth' in stream_html

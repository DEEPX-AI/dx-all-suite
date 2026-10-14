from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re

import pytest
from tests.css_rules import css_rule as _css_rule
from tests.css_rules import defines
from tests.css_rules import css_rule_last as _css_rule_last


ROOT = Path(__file__).resolve().parent.parent
SHARED_STATIC = ROOT / "shared" / "static"

FOUNDATION_HREFS = [
    "/static/shared/dx-fonts.css",
    "/static/shared/dx-tokens.css",
    "/static/shared/dx-base.css",
    "/static/shared/dx-utilities.css",
]

FONT_FILES = [
    "inter-4.1-var-latin.woff2",
    "jetbrains-mono-v24-latin-regular.woff2",
    "NotoSans-Regular.ttf",
    "NotoSans-Bold.ttf",
    "NotoSansMono-Regular.ttf",
    "NotoSansMono-Bold.ttf",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── Modules on the shared App Shell ────────────────────────────
# For these modules, shared/shell.py injects the rail, header, tabs and toolbar
# slot at server render time, so contracts that read only the template file do
# not hold. A module listed here is checked against its rendered HTML and is
# excluded from checks that assume a sidebar/topbar of its own.
MIGRATED_SHELL_MODULES = {
    "dx_app": ("dx_app/templates/index.html", "dx_app.server", "DX_APP_SHELL"),
    "dx_stream": ("dx_stream/templates/index.html", "dx_stream.server", "DX_STREAM_SHELL"),
    "dx_benchmark": ("dx_benchmark/templates/index.html", "dx_benchmark.server", "DX_BENCHMARK_SHELL"),
    "dx_monitor": ("dx_monitor/templates/index.html", "dx_monitor.server", "DX_MONITOR_SHELL"),
    "dx_agent_dev": ("dx_agent_dev/templates/index.html", "dx_agent_dev.server", "DX_AGENT_DEV_SHELL"),
    "dx_modelzoo": ("dx_modelzoo/templates/index.html", "dx_modelzoo.server", "DX_MODELZOO_SHELL"),
    "dx_planner": ("dx_planner/templates/index.html", "dx_planner.server", "DX_PLANNER_SHELL"),
    "dx_compiler": ("dx_compiler/templates/base.html", "dx_compiler.server", "DX_COMPILER_SHELL"),
}


def rendered_index(module: str) -> str:
    """The index.html the server actually serves (after shell injection for shared-shell modules)."""
    import importlib

    template_rel, mod_path, spec_name = MIGRATED_SHELL_MODULES[module]
    from shared.shell import apply as apply_shell

    spec = getattr(importlib.import_module(mod_path), spec_name)
    return apply_shell(read_text(ROOT / template_rel), spec)


def rendered_dx_app_index() -> str:
    return rendered_index("dx_app")


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
    ("launcher", ROOT / "launcher" / "static" / "index.html", ("toolbar",)),
]


def toolbar_nodes(nodes: list[dict[str, object]]) -> list[int]:
    return [idx for idx, node in enumerate(nodes) if "toolbar" in node["classes"]]


@pytest.mark.parametrize("module", sorted(MIGRATED_SHELL_MODULES))
def test_migrated_toolbar_target_lives_in_the_shared_shell_header(module):
    """shared/shell.py draws the toolbar for shared-shell modules, so check the rendered HTML."""
    html = rendered_index(module)
    nodes = parse_html_nodes(html)
    targets = toolbar_nodes(nodes)
    assert len(targets) == 1, f"{module} should expose exactly one .toolbar target"
    assert has_classes(nodes[targets[0]], "dx-shell-header-right", "toolbar")
    assert re.search(
        r"DXToolbar\.init\(\{[^}]*container:\s*['\"]\.toolbar['\"]", html, re.S
    )


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
    nodes = parse_html_nodes(rendered_dx_app_index())
    toolbar = find_one(nodes, lambda node: has_classes(node, "dx-shell-header-right", "toolbar"), "app toolbar")
    bell = find_one(nodes, lambda node: has_classes(node, "notif-bell"), "notif bell")
    badge = find_one(nodes, lambda node: has_id(node, "notif-badge"), "notif badge")
    assert_descendant(nodes, toolbar, bell, "notif bell remains inside app toolbar")
    assert_descendant(nodes, toolbar, badge, "notif badge remains inside app toolbar")


def test_stream_toolbar_preserves_pipeline_status_badge():
    nodes = parse_html_nodes(rendered_index("dx_stream"))
    toolbar = find_one(
        nodes, lambda node: has_classes(node, "dx-shell-header-right", "toolbar"), "stream toolbar"
    )
    badge = find_one(nodes, lambda node: has_id(node, "pipeline-status"), "pipeline status")
    assert_descendant(nodes, toolbar, badge, "pipeline status remains inside stream toolbar")


def test_benchmark_toolbar_preserves_edgeguide_button():
    nodes = parse_html_nodes(rendered_index("dx_benchmark"))
    toolbar = find_one(nodes, lambda node: has_classes(node, "toolbar"), "benchmark toolbar")
    button = find_one(nodes, lambda node: has_id(node, "edgeguideBtn"), "edgeguide button")
    assert_descendant(nodes, toolbar, button, "edgeguide button remains inside benchmark toolbar")



def test_launcher_toolbar_keeps_its_place_in_the_top_bar():
    """The toolbar sits in the right of the top bar, and nothing else takes the centre.

    The contract is only the toolbar's place in the bar, not what sits beside it.
    """
    nodes = parse_html_nodes(read_text(ROOT / "launcher" / "static" / "index.html"))
    bar = find_one(nodes, lambda node: has_classes(node, "top-bar"), "launcher top-bar")
    right = find_one(nodes, lambda node: has_classes(node, "top-bar-right"), "launcher top-bar-right")
    toolbar = find_one(nodes, lambda node: has_id(node, "launcherToolbar") and has_classes(node, "toolbar"), "launcher toolbar")
    assert nodes[toolbar]["parent"] == right
    assert nodes[right]["parent"] == bar
    assert not [n for n in nodes if has_id(n, "portalNav")], "the section nav is back"

def test_shared_foundation_css_files_exist():
    for name in ("dx-fonts.css", "dx-tokens.css", "dx-base.css", "dx-utilities.css"):
        path = SHARED_STATIC / name
        assert path.is_file(), f"{path} missing"
        assert path.stat().st_size > 0, f"{path} is empty"


def test_shared_font_css_uses_shared_font_paths():
    css = read_text(SHARED_STATIC / "dx-fonts.css")
    assert "/static/shared/fonts/inter-4.1-var-latin.woff2" in css
    assert "/static/shared/fonts/jetbrains-mono-v24-latin-regular.woff2" in css
    assert "/static/shared/fonts/NotoSans-Regular.ttf" in css
    assert "/static/fonts/" not in css
    for font_name in FONT_FILES:
        assert (SHARED_STATIC / "fonts" / font_name).is_file(), font_name


def test_shared_tokens_include_required_aliases():
    css = read_text(SHARED_STATIC / "dx-tokens.css")
    required_tokens = [
        "--surface-panel-rgb",
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
    # .mz-topbar lives in shared/static/dx-shell.css (the shared App Shell).
    assert not re.search(r"^\s*" + re.escape(".mz-topbar") + r"\s*\{", css, re.M)
    assert ".mz-explorer-shell" in css, "모듈 고유 레이아웃은 계속 소유한다"
    assert ".mz-card" in css
    assert ".mz-detail-view" in css
    assert ".mz-btn" in css
    assert ".mz-logo" not in css, ".mz-logo is dead after brand migration"


def assert_local_topbar_token(css: str) -> None:
    """A local topbar variable must derive from the shared header height.

    For shared-shell modules the tab row height is added — there the variable means
    "total chrome height above the content", not just the header.
    """
    accepted = (
        "--topbar-h: var(--dx-module-header-h)",
        "--benchmark-topbar-h: var(--dx-module-header-h)",
        "--benchmark-topbar-h: calc(var(--dx-module-header-h) + var(--dx-tabs-h))",
    )
    assert any(frag in css for frag in accepted), (
        "local topbar token must derive from --dx-module-header-h"
    )


# A module must not RE-DEFINE the global focus ring (shared/static/dx-base.css
# ships `:focus-visible{...}` as a bare selector). Styling the pseudo-class on a
# module's own component — `.dxg-tbtn:focus-visible` — is normal
# CSS and must stay allowed, so match only a STANDALONE `:focus-visible`, i.e. one
# not attached to a preceding selector. A plain substring check cannot tell the two
# apart; every other fragment below is a token unique to the foundation.
_BARE_FOCUS_VISIBLE = re.compile(r"(?:^|[\s,{}])(:focus-visible)\b")


def assert_shared_foundation_removed(css: str) -> None:
    forbidden_fragments = [
        "@font-face",
        "/static/fonts/",
        "color-scheme: dark",
        "--font:",
        "--mono:",
        "scrollbar-color:",
        "::-webkit-scrollbar",
    ]
    for fragment in forbidden_fragments:
        if hasattr(fragment, "search"):
            assert not fragment.search(css), fragment.pattern
        else:
            assert fragment not in css, fragment

    bare = _BARE_FOCUS_VISIBLE.search(css)
    assert not bare, (
        "module CSS re-defines the global :focus-visible ring "
        f"(shared/static/dx-base.css owns it): ...{css[max(0, bare.start() - 40):bare.end() + 60]}..."
    )


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
    # .top-bar / .main-tab live in shared/static/dx-shell.css (the shared App Shell).
    for selector in (".top-bar", ".main-tabs", ".main-tab", ".app-title"):
        assert not re.search(r"^\s*" + re.escape(selector) + r"\s*\{", css, re.M), (
            f"{selector} 는 shared/static/dx-shell.css 로 옮겼다"
        )
    assert ".main-tab-content" in css, "탭 본문 컨테이너는 모듈이 계속 소유한다"
    assert ".panel" in css
    assert "@keyframes slideIn" in css
    assert "@keyframes pulse" in css
    assert "@keyframes spin" in css


def test_planner_css_no_longer_defines_shared_foundation():
    css = read_text(ROOT / "dx_planner" / "static" / "css" / "style.css")
    assert_shared_foundation_removed(css)
    assert_local_topbar_token(css)
    assert "body { overflow-x: auto; overflow-y: hidden; }" in css
    # .planner-topbar lives in shared/static/dx-shell.css (the shared App Shell).
    assert not re.search(r"^\s*" + re.escape(".planner-topbar") + r"\s*\{", css, re.M)
    assert ".planner-main" in css, "모듈 고유 레이아웃은 계속 소유한다"
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
    for selector in (".app", ".sidebar", ".topbar", ".topbar-right", ".nav-item", ".content-wrap"):
        assert not re.search(r"^\s*" + re.escape(selector) + r"\s*\{", css, re.M), (
            f"{selector} 는 shared/static/dx-shell.css 로 옮겼다"
        )
    assert "color-scheme:dark" not in css
    assert "--stream-color:#10B981" in css
    assert "body{overflow-x:auto;overflow-y:hidden}" in css
    # .sidebar / .topbar live in shared/static/dx-shell.css (the shared App Shell).
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
    assert "return self.serve_static(rel, DATA_DIR)" in source
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
        # A declaration, not the media feature: "@media (prefers-color-scheme:
        # dark)" contains this string and is a legitimate theme query. Matching
        # the substring made the guard fire on correct code.
        re.compile(r"(?<!prefers-)color-scheme\s*:\s*dark"),
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
        if hasattr(fragment, "search"):
            assert not fragment.search(css), fragment.pattern
        else:
            assert fragment not in css, fragment

    # #header lives in shared/static/dx-shell.css (the shared App Shell).
    assert not re.search(r"^\s*#header\s*\{", css, re.M)

    for fragment in (
        "body{overflow-x:auto;overflow-y:hidden}",
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
    # The shell header owns the toolbar container (the rendered check is the dedicated test above).
    assert '<div class="topbar-right toolbar">' not in html
    assert "DXToolbar.init({ container: '.toolbar'" in html
    assert "DXToolbar.init({ container: '.topbar-right'" not in html
    # Tab overflow initializes after toolbar.js, so it measures once the header width is final.
    assert_ordered_tokens(
        html,
        [
            "DXToolbar.init({ container: '.toolbar'",
            'src="/static/shared/dx-tabs.js"',
            "DXTabs.init(",
        ],
    )
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
    # Selectors owned by the shared App Shell must not remain in the module, or two definitions fight.
    for selector in (".app", ".sidebar", ".topbar", ".topbar-right", ".nav-item", ".content-wrap"):
        assert not re.search(r"^\s*" + re.escape(selector) + r"\s*\{", css, re.M), (
            f"{selector} 는 shared/static/dx-shell.css 로 옮겼다"
        )
    # Selectors the module still owns
    # .toolbar / .card / .btn belong to the shared layer, and .ref-* (the Reference
    # screen, shared with dx_stream) lives in shared/static/dx-components.css.
    # (List any selector the module keeps owning here.)


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
        "--bg-0:",
        "--bg-1:",
        "--font:",
        "--mono:",
        "scrollbar-color:",
        "::-webkit-scrollbar",
        "\n:focus-visible",
    ):
        assert fragment not in css, fragment
    # The declaration, not the media feature. "@media (prefers-color-scheme:
    # dark)" contains the same substring and is how a module asks the OS which
    # theme is on — the guard must not fire on that.
    assert not re.search(r"(?<!prefers-)color-scheme\s*:\s*dark", css)
    assert "* { margin: 0; padding: 0; box-sizing: border-box; }" not in css
    for alias in (
        "--text:",
        "--text-muted:",
        "--text-dim:",
        "--border-glow:",
        "--app-color:",
        # --stream-color is not required: the launcher does not use it and dx_stream
        # defines its own. Requiring an unused token would only block cleanup.
        "--sandbox-color:",
        "--zoo-color:",
    ):
        assert alias in css, alias
    for selector in (
        ".top-bar",
        ".top-bar-right",
        # Only selectors with live markup belong here; listing a dead one keeps an
        # orphan rule alive because it looks "referenced".
        ".orbital-status",
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
    """handle_chat_routes() in shared/dx_server.py owns the POST config/test routes."""
    shared_source = read_text(ROOT / "shared" / "dx_server.py")
    assert 'self.url_path == "/api/chat/config"' in shared_source
    assert 'self.url_path == "/api/chat/config/test"' in shared_source
    assert "save_config(" in shared_source
    assert "stream_chat(" in shared_source


def test_shared_chat_widget_owns_settings_panel_and_config_api():
    """chat-widget.js owns the settings panel and the config save API call. Saving checks the connection
    first, so there is no separate Test button in the widget (the /config/test server route remains)."""
    source = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.js")
    assert 'data-action="settings"' in source
    assert 'class="dx-chat-settings-panel"' in source
    assert 'class="dx-chat-settings-form"' in source
    assert "function _openSettingsPanel()" in source
    assert "function _saveSettings(" in source
    assert "function _postConfig(" in source and "force: true" in source
    assert "fetch(_apiUrl('/api/chat/config'))" in source
    assert "fetch(_apiUrl('/api/chat/config'), {" in source
    assert "method: 'DELETE'" in source          # back to automatic
    assert "Launcher → Settings" not in source
    assert ".value = data.api_key" not in source
    assert "_els.settingsApiKey.value = ''" in source


def test_shared_chat_widget_has_provider_specific_model_hints():
    """The model placeholder follows the provider instead of a fixed, wrong OpenAI default."""
    source = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.js")
    assert "const modelHints = {" in source
    assert "anthropic: 'claude-haiku-4-5-20251001'" in source
    assert "google: 'gemini-1.5-flash'" in source
    assert "custom: 'your-model-name'" in source
    assert "provider === 'github' ? 'gpt-4o-mini' : 'gpt-4o-mini'" not in source


def test_shared_chat_widget_retranslates_banner_without_refetching_config():
    """A language change redraws only the top line (who is answering, _renderSource) and does not
    call the config API again."""
    source = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.js")
    assert "function _renderSource()" in source
    start = source.index("DXI18n.onLangChange(function() {")
    end = source.index("_history.forEach(m => _renderMessage", start)
    handler = source[start:end]
    assert "_renderSource();" in handler
    assert "_checkConfig();" not in handler


def test_shared_chat_widget_styles_settings_panel():
    """chat-widget.css styles the settings panel inside the widget."""
    css = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.css")
    for selector in (
        ".dx-chat-settings-panel",
        ".dx-chat-settings-form",
        ".dx-chat-settings-field",
        ".dx-chat-settings-actions",
        ".dx-chat-settings-status",
        ".dx-chat-source-change",
    ):
        assert selector in css, selector


def test_launcher_no_longer_owns_chat_settings_ui():
    """The top toolbar/launcher does not own the chatbot settings dialog or its save logic."""
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
    """Fallback/error messages do not point users to Launcher Settings."""
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
    # Settings labels are keys translated per language (tests/shared/test_chat_widget_lang_browser.py)
    assert 'data-chat-t="Temperature"' in widget_source
    assert "'Temperature': { ko: '온도'" in widget_source
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
    # The topbar gap provides the spacing, so the page title must not have margin-left.
    page_title_rule = re.search(r"\.dx-brand-page-title\s*\{(?P<body>.*?)\}", css, re.S).group("body")
    assert "margin-left" not in page_title_rule, "margin-left causes double spacing with topbar gap"
    # Checks **what provides the spacing**, not the value: the contract is "padding, not
    # margin", not a particular pixel count, so spacing-scale changes do not break it.
    assert re.search(r"padding-left:\s*(var\(--sp-|\d+px)", page_title_rule), (
        f"page title 이 padding-left 로 간격을 주지 않는다: {page_title_rule!r}")
    assert "window.DXBrand" in js
    assert "function mount" in js
    assert "document.createElement(safeHref ? 'a' : 'div')" in js
    assert "DXI18n.onLangChange" in js
    assert "console.warn" in js
    assert "subtitle.en" in js
    # A safe href allows only /, http:// and https://.
    assert "function isSafeHref" in js
    assert ("href.charAt(0) === '/'" in js or "href.indexOf('/') === 0" in js), "allowlist must check /"
    assert "href.indexOf('https://') === 0" in js, "allowlist must check https://"
    assert "href.indexOf('http://') === 0" in js, "allowlist must check http://"
    assert "homeHref ignored" in js
    # A second mount on the same target reuses the existing brand.
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


def test_migrated_modules_leave_header_metrics_to_the_shell():
    """Header metrics left in a shared-shell module would fight the shell's definition.

    With all 8 modules on the shared shell, only module-chrome.css (definition) and
    dx-shell.css (use) may reference --dx-module-header-*.
    """
    app_css = read_text(ROOT / "dx_app" / "static" / "css" / "style.css")
    stream_css = read_text(ROOT / "dx_stream" / "static" / "css" / "stream.css")

    # dx-shell.css owns the header metrics for shared-shell modules — a local copy would fight it.
    for css, name in ((app_css, "dx_app"), (stream_css, "dx_stream")):
        assert "--dx-module-header-h" not in css, (
            f"{name} 은 shell로 이관됐다 — 헤더 치수는 dx-shell.css가 소유한다"
        )

    shell_css = read_text(SHARED_STATIC / "dx-shell.css")
    shell_header = re.search(r"\.dx-shell-header\s*\{(?P<body>.*?)\}", shell_css, re.S).group("body")
    assert "height: var(--dx-module-header-h)" in shell_header
    assert "min-height: var(--dx-module-header-h)" in shell_header
    assert "box-shadow: var(--dx-module-header-elevation)" in shell_header


@pytest.mark.parametrize("module", sorted(MIGRATED_SHELL_MODULES))
def test_migrated_brand_sits_in_the_shell_header_before_the_page_name(module):
    """With no sidebar, the brand sits at the left of the shell header."""
    template_rel = MIGRATED_SHELL_MODULES[module][0]
    template = read_text(ROOT / template_rel)
    assert_loads_shared_brand_after_i18n(template, template_rel)
    assert "DXBrand.mount({" in template
    assert "sidebar-brand" not in template

    html = rendered_index(module)
    left = re.search(r'<div class="dx-shell-header-left">(?P<body>.*?)</header>', html, re.S)
    assert left is not None
    body = left.group("body")
    assert 'id="dxBrand"' in body, "브랜드가 헤더 좌측에 없다"
    assert body.index('id="dxBrand"') < body.index('id="dxShellPage"'), (
        "브랜드는 페이지명 왼쪽에 온다"
    )


def test_unmigrated_modules_use_sidebar_brand_for_position_alignment():
    for rel in ():
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
        # brand.js must load before the inline mount call.
        assert_ordered_tokens(html, [
            'src="/static/shared/brand.js',
            'DXBrand.mount({',
        ])
        mount_match = re.search(r"DXBrand\.mount\(\{(?P<body>.*?)\}\);", html, re.S)
        assert mount_match is not None, rel
        mount_block = mount_match.group("body")
        for lang in ("ko", "en", "ja", "zh-CN", "zh-TW"):
            assert f"{lang}:" in mount_block or f"'{lang}':" in mount_block
    # Sidebar-logo-only selectors must not remain; only the brand wrapper is used.
    old_logo_patterns = (
        r"\.logo-dx\b",
        r"\.logo-text\b",
        r"\.sidebar\.collapsed\s+\.logo\b",
        r"\.sidebar\.collapsed\s+\.logo-text\b",
    )
    # No module has a sidebar of its own now. List one here if a module with a
    # sidebar is added.
    for css_rel in ():
        css_path = ROOT / css_rel
        assert css_path.is_file(), css_rel
        css_content = read_text(css_path)
        assert ".sidebar-brand" in css_content, f"missing sidebar brand wrapper in {css_rel}"
        assert "height:var(--dx-module-header-h)" in css_content.replace(" ", ""), f"{css_rel} sidebar brand must align with shared module header height"
        assert "padding:0 24px" in css_content or "padding: 0 24px" in css_content, f"{css_rel} sidebar brand should center within shared header"
        for pattern in old_logo_patterns:
            assert re.search(pattern, css_content) is None, f"old logo selector {pattern} still in {css_rel}"


def test_brand_topbars_use_unified_metrics_and_shadow():
    """Topbar-style brand areas use the same height and shadow."""
    planner_css = read_text(ROOT / "dx_planner" / "static" / "css" / "style.css")
    benchmark_css = read_text(ROOT / "dx_benchmark" / "static" / "css" / "style.css")
    monitor_css = read_text(ROOT / "dx_monitor" / "static" / "css" / "style.css")
    modelzoo_css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    sdk_css = read_text(ROOT / "launcher" / "static" / "sdk-library.css")
    compiler_css = read_text(ROOT / "dx_compiler" / "static" / "css" / "style.css")

    # dx_benchmark is on the shared shell: dx-shell.css owns the header itself, and the
    # module's --benchmark-topbar-h means "total chrome height above the content", so it
    # must add header + tab row (without the tab row the 100vh calculation overflows).
    assert (
        "--benchmark-topbar-h: calc(var(--dx-module-header-h) + var(--dx-tabs-h))"
        in benchmark_css
    ), "benchmark chrome height must include the shell tab row"

    # All 8 modules are on the shared shell, where dx-shell.css owns header height, offset
    # and elevation. The only remaining topbar surface is the SDK Library.
    assert "box-shadow: var(--dx-module-header-elevation)" in sdk_css


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

    # The SDK Library mounts the shared brand inside its own topbar, with no duplicate topbar.
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

    # The mount block anchored to the #sdkBrand target
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
        # For shared-shell modules the shell header draws the slot, so check the rendered HTML.
        migrated = {v[0]: k for k, v in MIGRATED_SHELL_MODULES.items()}
        html = (
            rendered_index(migrated[rel]) if rel in migrated else read_text(ROOT / rel)
        )
        assert '<div class="dx-brand-slot"' in html, rel
        assert '<span class="dx-brand-slot"' not in html, rel


def test_modelzoo_brand_slot_is_a_block_element_after_the_shell_migration():
    """The brand slot is a block element: the shell header draws it as a <div>, never a <span>."""
    html = rendered_index("dx_modelzoo")
    assert '<div class="dx-brand-slot"' in html
    assert '<span class="dx-brand-slot"' not in html


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
    for token in ("var(--surface-", "var(--border", "var(--accent", "var(--text-"):
        assert token in shell_blocks






def test_shared_depth_tokens_define_surface_contract():
    """dx-tokens.css and dx-utilities.css provide the shared depth tokens/utilities."""
    tokens_css = read_text(SHARED_STATIC / "dx-tokens.css")
    utilities_css = read_text(SHARED_STATIC / "dx-utilities.css")

    # Tokens exist
    for token in (
        "--inset-highlight:",
        "--inset-highlight-strong:",
        "--shadow-sm:",
        "--shadow-xl:",
        "--surface-raised-shadow:",
        "--surface-glass-shadow:",
        "--surface-active-shadow:",
        "--surface-hover-shadow:",
        "--text-glow-accent:",
    ):
        assert token in tokens_css, f"token {token} missing from dx-tokens.css"

    # Utility selectors exist
    for sel in (".dx-surface-raised", ".dx-surface-glass", ".dx-surface-active", ".dx-text-glow"):
        assert sel in utilities_css, f"selector {sel} missing from dx-utilities.css"

    # Exact utility fragments
    assert "background: var(--surface-raised)" in utilities_css
    assert "box-shadow: var(--surface-raised-shadow)" in utilities_css


def test_module_chrome_depth_contract_is_token_only_and_loaded():
    """module-chrome.css defines the depth tokens and every template loads it in the right order."""
    chrome_css = read_text(SHARED_STATIC / "module-chrome.css")

    # Depth tokens exist
    assert "--dx-module-header-glow:" in chrome_css
    assert "--dx-module-header-elevation:" in chrome_css

    # module-chrome.css has no box-shadow declarations of its own (it only defines tokens)
    assert "box-shadow: var(--dx-module-header-elevation)" not in chrome_css

    # module-chrome.css defines no bare topbar selectors
    for sel in (".top-bar", ".topbar", ".header", "#header"):
        pattern = re.escape(sel) + r"\s*\{"
        assert re.search(pattern, chrome_css) is None, (
            f"module-chrome.css must not define bare selector {sel}"
        )

    # Template load order
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
    """Every module topbar uses the shared depth tokens."""
    TOPBAR_SPECS = [
        ("launcher/static/style.css", ".top-bar"),
        ("launcher/static/sdk-library.css", ".sdk-topbar"),
        ("launcher/static/about-deepx.css", ".about-topbar"),
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
    """Flat surfaces such as cards/panels use the shared surface depth tokens."""
    # Default raised surface
    RAISED_SPECS = [
        ("dx_benchmark/static/css/style.css", [".panel", ".stat-card", ".meta-card", ".controls"]),
        ("dx_compiler/static/css/style.css", [".compile-form", ".progress-container", ".mode-card"]),
        ("dx_modelzoo/static/css/style.css", [".mz-detail-header", ".mz-detail-section", ".mz-inference-panel"]),
        ("launcher/static/about-deepx.css", [".about-value-card", ".about-quote"]),
    ]
    for css_rel, selectors in RAISED_SPECS:
        css = read_text(ROOT / css_rel)
        for sel in selectors:
            body = _css_rule(css, sel)
            assert "background: var(--surface-raised)" in body, (
                f"{css_rel} {sel} missing surface-raised"
            )
            assert "box-shadow: var(--surface-raised-shadow)" in body, (
                f"{css_rel} {sel} missing surface-raised-shadow"
            )

    # Active state
    ACTIVE_SPECS = [
        ("dx_planner/static/css/style.css", ".task-btn.selected"),
        ("dx_planner/static/css/style.css", ".size-btn.selected"),
    ]
    for css_rel, sel in ACTIVE_SPECS:
        css = read_text(ROOT / css_rel)
        body = _css_rule(css, sel)
        assert "box-shadow: var(--surface-active-shadow)" in body, (
            f"{css_rel} {sel} missing surface-active-shadow"
        )


def test_unmigrated_sidebar_brand_uses_shared_header_depth():
    """A module that has its own sidebar uses the same depth as the top chrome.

    No module has one now (all are on the shared shell); the list is empty."""
    for css_rel in ():
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
    """The final card rule in App/Stream does not override the depth with a hard-coded gradient."""
    SURFACE_SPECS = {
        "dx_app/static/css/style.css": [
            ".detail-info-card",
            ".pp-card",
            ".pcard",
            ".npu-card",
            ".plan-sc",
            ".comp-result-card",
            ".ref-topic-card",
        ],
        "dx_stream/static/css/stream.css": [
            ".demo-card",
            ".ref-topic-card",
        ],
    }
    shared_rel = "shared/static/dx-components.css"
    shared_css = read_text(ROOT / shared_rel)
    for css_rel, selectors in SURFACE_SPECS.items():
        css = read_text(ROOT / css_rel)
        for selector in selectors:
            # For a card owned by the shared layer, the shared rule is the final one. It stays
            # in the contract, or depth regressions there would go uncaught.
            owner_rel, body = (
                (css_rel, _css_rule_last(css, selector))
                if _defines_selector(css, selector)
                else (shared_rel, _css_rule_last(shared_css, selector))
            )
            assert "background: var(--surface-raised)" in body, (
                f"{owner_rel} {selector} final rule missing surface-raised"
            )
            assert "box-shadow: var(--surface-raised-shadow)" in body, (
                f"{owner_rel} {selector} final rule missing surface-raised-shadow"
            )


def test_app_stream_local_css_urls_bust_pre_depth_cache():
    """App/Stream CSS URLs differ from the earlier ones, so a stale browser cache cannot hide depth changes."""
    app_html = read_text(ROOT / "dx_app" / "templates" / "index.html")
    stream_html = read_text(ROOT / "dx_stream" / "templates" / "index.html")

    assert 'href="/static/css/style.css?m=dx_app_shell_a' in app_html
    assert 'href="/static/css/stream.css?m=dx_stream_shell_a' in stream_html


# ── Single owner for shared components ──────────────────────────
# Shared components are defined in one place only: shared/static/dx-components.css.
# A module that redefines one overrides the shared definition and drifts from it.
# Allowlist entries are removed once a file no longer redefines the selector — the
# stale-entry test enforces that.

COMPONENT_OWNER = "shared/static/dx-components.css"

# Selectors owned by the utilities/shell rather than the components file.
ALT_OWNERS = {
    ".flex": "shared/static/dx-utilities.css",
    ".hidden": "shared/static/dx-utilities.css",
    ".txt-dim": "shared/static/dx-utilities.css",
    ".b-ok": "shared/static/dx-utilities.css",
    ".b-warn": "shared/static/dx-utilities.css",
    ".b-red": "shared/static/dx-utilities.css",
    ".toolbar": "shared/static/dx-shell.css",
    ".page": "shared/static/dx-shell.css",
}

# Selectors that have a shared owner, with the modules allowed to override them.
OWNED_COMPONENT_OVERRIDES = {
    ".btn": set(),
    ".btn-ghost": set(),
    ".btn-danger": set(),
    # An empty set means no module may redefine the component; any new redefinition fails.
    ".card": set(),
    ".btn-primary": set(),
    ".btn-acc": set(),
    ".btn-sm": set(),
    ".btn-neutral": set(),
    ".toast": set(),
    ".toast-wrap": set(),
    ".modal": set(),
    ".modal-overlay": set(),
    ".stat": set(),
    ".toolbar": set(),
    ".page": set(),
    ".flex": set(),
    ".hidden": set(),
    ".txt-dim": set(),
    ".b-ok": set(),
    ".b-warn": set(),
    ".b-red": set(),
}

# Selectors with no shared owner yet, each module defining its own.
# Once one moves to dx-components.css, move it to OWNED_COMPONENT_OVERRIDES.
UNOWNED_COMPONENTS = {}

MODULE_CSS_GLOBS = ("launcher/static/*.css", "dx_*/static/css/*.css")


def _module_css_paths() -> list[Path]:
    paths: list[Path] = []
    for pattern in MODULE_CSS_GLOBS:
        paths.extend(sorted(ROOT.glob(pattern)))
    return paths


def _defines_selector(css: str, selector: str) -> bool:
    """Whether a rule defines the selector — robust to grouped selectors, comments and media queries."""
    return defines(css, selector)


def _redefining_files(selector: str) -> set[str]:
    return {
        path.relative_to(ROOT).as_posix()
        for path in _module_css_paths()
        if _defines_selector(read_text(path), selector)
    }


@pytest.mark.parametrize("selector", sorted(OWNED_COMPONENT_OVERRIDES))
def test_owned_component_is_defined_by_the_shared_owner(selector):
    owner = ALT_OWNERS.get(selector, COMPONENT_OWNER)
    assert _defines_selector(read_text(ROOT / owner), selector), (
        f"{owner} 가 {selector} 를 정의하지 않는다"
    )


@pytest.mark.parametrize("selector", sorted(UNOWNED_COMPONENTS))
def test_unowned_component_is_tracked_until_it_gets_an_owner(selector):
    """Fails once the selector gets an owner — the signal to move it to OWNED_COMPONENT_OVERRIDES."""
    assert not _defines_selector(read_text(ROOT / COMPONENT_OWNER), selector), (
        f"{selector} 가 {COMPONENT_OWNER} 로 올라갔다. "
        "UNOWNED_COMPONENTS에서 OWNED_COMPONENT_OVERRIDES로 옮겨라"
    )


@pytest.mark.parametrize(
    "selector,allowed",
    sorted({**OWNED_COMPONENT_OVERRIDES, **UNOWNED_COMPONENTS}.items()),
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_no_new_module_redefines_a_shared_component(selector, allowed):
    offenders = _redefining_files(selector) - allowed
    assert not offenders, (
        f"{selector} 를 새로 재정의한 모듈: {sorted(offenders)}. "
        f"{COMPONENT_OWNER} 의 정의를 쓰세요"
    )


@pytest.mark.parametrize(
    "selector,allowed",
    sorted({**OWNED_COMPONENT_OVERRIDES, **UNOWNED_COMPONENTS}.items()),
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_component_allowlist_has_no_stale_entries(selector, allowed):
    """An allowlist entry the module no longer needs would hide the next regression."""
    stale = allowed - _redefining_files(selector)
    assert not stale, f"{selector} allowlist에서 지울 것: {sorted(stale)}"


# ── Semantic token layer ────────────────────────────────────────
# Two layers: primitive (dx-tokens.css) → semantic (dx-semantic.css).
# Module CSS references only semantic tokens, so themes can be swapped.
SEMANTIC_TOKENS = (
    "--surface-page",
    "--surface-panel",
    "--surface-raised",
    "--surface-sunken",
    "--surface-overlay",
    "--text-primary",
    "--text-secondary",
    "--text-muted",
    "--text-faint",
    "--text-on-accent",
    "--border-subtle",
    "--border-strong",
    "--control-bg",
    "--control-border",
    "--control-border-focus",
    "--control-ring",
    "--status-ok",
    "--status-warn",
    "--status-error",
    "--status-info",
    "--surface-hover",
    "--surface-hover-strong",
)

# Retired names. Nothing may define or use them.
RETIRED_NAMES = (
    "--bg-0", "--bg-1", "--bg-2", "--bg-3", "--bg-4", "--bg-input",
    "--text-1", "--text-2", "--text-3", "--text-4",
    "--border", "--border-hover",
    "--success", "--warning", "--error", "--info",
    "--surface-raised-bg", "--glass-bg",
)

SEMANTIC_SURFACES = {
    "dx_app": "dx_app/templates/index.html",
    "dx_stream": "dx_stream/templates/index.html",
    "dx_benchmark": "dx_benchmark/templates/index.html",
    "dx_monitor": "dx_monitor/templates/index.html",
    "dx_modelzoo": "dx_modelzoo/templates/index.html",
    "dx_planner": "dx_planner/templates/index.html",
    "dx_compiler": "dx_compiler/templates/base.html",
    "dx_agent_dev": "dx_agent_dev/templates/index.html",
    "launcher": "launcher/static/index.html",
}


def test_semantic_layer_defines_every_role_token():
    css = read_text(SHARED_STATIC / "dx-semantic.css")
    missing = [t for t in SEMANTIC_TOKENS if f"{t}:" not in css]
    assert not missing, f"dx-semantic.css에 없는 semantic 토큰: {missing}"


def test_no_legacy_alias_layer_remains():
    """Only one set of role names exists.

    A second set of alias names (--bg-0 / --text-1 / --border ...) defined in both
    dx-tokens.css and dx-semantic.css, with no light value on the primitive side, would
    fall back to a dark literal in the light theme whenever one alias is missing. One set
    of names removes that trap.
    """
    tokens = read_text(SHARED_STATIC / "dx-tokens.css")
    semantic = read_text(SHARED_STATIC / "dx-semantic.css")
    for legacy in RETIRED_NAMES:
        pattern = re.compile(r"(?m)^\s*" + re.escape(legacy) + r"\s*:")
        assert not pattern.search(semantic), (
            f"{legacy} 가 semantic 계층에 되살아났다 — 역할 이름을 쓰세요"
        )
        assert not pattern.search(tokens), (
            f"{legacy} 가 primitive 계층에 되살아났다 — light 값이 없어 "
            "그 자리가 light 테마에서 dark 로 떨어진다"
        )


def test_no_module_still_calls_a_retired_name():
    used = {}
    for path in _module_css_paths():
        css = read_text(path)
        hit = sorted({n for n in RETIRED_NAMES if f"var({n})" in css})
        if hit:
            used[path.relative_to(ROOT).as_posix()] = hit
    assert not used, f"은퇴한 토큰 이름을 아직 부른다: {used}"


@pytest.mark.parametrize("name,rel", sorted(SEMANTIC_SURFACES.items()))
def test_semantic_css_loads_between_tokens_and_base(name, rel):
    html = head_html(read_text(ROOT / rel))
    assert_ordered(
        html,
        [
            "/static/shared/dx-tokens.css",
            "/static/shared/dx-semantic.css",
            "/static/shared/dx-base.css",
        ],
    )


# ── Light theme ─────────────────────────────────────────────────
def test_light_theme_redefines_every_semantic_token():
    """One missing token gives dark text on a dark background in the light theme."""
    css = read_text(SHARED_STATIC / "dx-theme-light.css")
    missing = [t for t in SEMANTIC_TOKENS if f"{t}:" not in css]
    assert not missing, f"light 테마에 빠진 semantic 토큰: {missing}"


def test_light_theme_covers_all_three_viewer_states():
    """All three states are handled: explicit light / explicit dark / unstamped (system)."""
    css = read_text(SHARED_STATIC / "dx-theme-light.css")
    assert ':root[data-theme="light"]' in css, "명시적 light 선택 규칙이 없다"
    assert "@media (prefers-color-scheme: light)" in css, "system light 규칙이 없다"
    assert ':root:not([data-theme="dark"])' in css, (
        "system light 규칙이 명시적 dark 선택을 이기지 못하게 가드해야 한다"
    )


def test_light_theme_defines_the_same_tokens_in_both_blocks():
    """A token in only one block becomes a hard-to-find bug that breaks only for system-light viewers."""
    css = read_text(SHARED_STATIC / "dx-theme-light.css")
    explicit, _, system = css.partition("@media (prefers-color-scheme: light)")
    names = lambda blob: set(re.findall(r"(--[\w-]+)\s*:", blob))
    only_explicit = names(explicit) - names(system)
    only_system = names(system) - names(explicit)
    assert not only_explicit, f"명시 블록에만 있는 토큰: {sorted(only_explicit)}"
    assert not only_system, f"system 블록에만 있는 토큰: {sorted(only_system)}"


def test_light_theme_does_not_redefine_legacy_aliases():
    """The light theme must not bring retired names back.

    Defining one here would revive it in light only, and module CSS that uses a name with
    no value in dark would go unnoticed."""
    css = read_text(SHARED_STATIC / "dx-theme-light.css")
    for legacy in RETIRED_NAMES:
        assert re.search(re.escape(legacy) + r"\s*:", css) is None, (
            f"{legacy} 를 light 테마가 재정의했다 — dx-semantic.css의 alias만 유지하라"
        )


@pytest.mark.parametrize("name,rel", sorted(SEMANTIC_SURFACES.items()))
def test_light_theme_loads_right_after_the_semantic_layer(name, rel):
    html = head_html(read_text(ROOT / rel))
    assert_ordered(
        html,
        [
            "/static/shared/dx-semantic.css",
            "/static/shared/dx-theme-light.css",
            "/static/shared/dx-base.css",
        ],
    )



# ── Button system contract ──────────────────────────────────────
def test_button_size_modifier_carries_no_appearance():
    """.btn-sm changes size only.

    If a size variant also set background or border color, every element combining it with
    .btn-ghost would stop rendering as ghost (module CSS loads after shared CSS). A size
    variant that touches appearance silently breaks every such combination.
    """
    body = _css_rule_last(read_text(SHARED_STATIC / "dx-components.css"), ".btn-sm")
    flat = body.replace(" ", "")
    for prop in ("background:", "border-color:", "color:"):
        assert prop not in flat, f".btn-sm 이 외형을 건드린다: {prop}"


def test_button_base_reserves_a_transparent_border():
    """No 1px size jump between variants with and without a border."""
    body = _css_rule_last(read_text(SHARED_STATIC / "dx-components.css"), ".btn")
    assert "border:1pxsolidtransparent" in body.replace(" ", "")


def test_no_module_ships_a_standalone_button_outside_the_shared_system():
    """Standalone button names (used without `.btn`) are retired in favor of the shared system.

    A class named `.btn-…` outside the `.btn` system builds the same thing twice
    (e.g. .btn-small / .btn-secondary).
    """
    retired = (".btn-small", ".btn-secondary", ".btn-acc-standalone")
    for path in _module_css_paths():
        css = read_text(path)
        for selector in retired:
            assert not _defines_selector(css, selector), (
                f"{path.relative_to(ROOT)} 가 은퇴한 {selector} 를 다시 정의한다"
            )



# ── Reach of the shared component CSS ──────────────────────────
COMPONENT_CSS_HREF = "/static/shared/dx-components.css"

ALL_SURFACES = {
    **SEMANTIC_SURFACES,
    "dx_agent_dev": "dx_agent_dev/templates/index.html",
}


@pytest.mark.parametrize("name,rel", sorted(ALL_SURFACES.items()))
def test_every_surface_loads_the_shared_component_layer(name, rel):
    """A surface that does not load the shared component CSS misses every shared component.

    Its buttons and cards fall back to browser defaults once .card / .btn are defined only
    in the shared layer — so the foundation contract requires components too, not just
    tokens/base/utilities.
    """
    html = head_html(read_text(ROOT / rel))
    assert COMPONENT_CSS_HREF.split("?")[0] in html, f"{name} 이 공유 컴포넌트 CSS를 로드하지 않는다"


@pytest.mark.parametrize("name,rel", sorted(ALL_SURFACES.items()))
def test_component_css_loads_after_the_foundation_and_before_module_css(name, rel):
    """Modules can still override it, and the foundation tokens are already loaded."""
    html = head_html(read_text(ROOT / rel))
    assert html.index("/static/shared/dx-utilities.css") < html.index(COMPONENT_CSS_HREF), name


# ── Name collision boundary ─────────────────────────────────────
# Unrelated modules use these class names with different meanings. They are not
# merge candidates — merging breaks one side. The danger is the moment one of them
# moves into the shared layer: e.g. a `.page` that is a page switcher (display:none)
# in one module and a content container in another would hide the latter's content.
#
# This test fails at that moment. If a name really must be shared, rename one side first.
KNOWN_NAME_COLLISIONS = {
    ".bench-table": ("dx_benchmark", "dx_planner"),
    ".card-grid": ("dx_stream", "launcher"),
    ".empty-state": ("dx_benchmark", "dx_planner", "dx_stream"),
    ".form-group": ("dx_benchmark", "dx_compiler"),
    ".form-row": ("dx_benchmark", "dx_compiler"),
    ".hero": ("dx_benchmark", "launcher"),
    ".info-row": ("dx_benchmark", "dx_compiler"),
    ".loading-overlay": ("dx_app", "launcher"),
    ".mb-4": ("dx_app", "dx_benchmark"),
    ".mz-spinner": ("dx_app", "dx_modelzoo"),
    ".progress-bar": ("dx_compiler", "dx_stream"),
    ".spinner": ("dx_benchmark", "launcher"),
    ".status-badge": ("dx_agent_dev", "dx_benchmark"),
}

SHARED_CSS_FILES = ("dx-components.css", "dx-utilities.css", "dx-shell.css", "dx-base.css")


@pytest.mark.parametrize("selector", sorted(KNOWN_NAME_COLLISIONS))
def test_colliding_name_is_not_promoted_to_the_shared_layer(selector):
    for name in SHARED_CSS_FILES:
        css = read_text(SHARED_STATIC / name)
        assert not _defines_selector(css, selector), (
            f"{name} 이 {selector} 를 정의한다. 이 이름은 "
            f"{KNOWN_NAME_COLLISIONS[selector]} 에서 서로 다른 뜻으로 쓰인다 — "
            "공유로 올리기 전에 한쪽 이름을 바꿔야 한다"
        )


@pytest.mark.parametrize("selector", sorted(KNOWN_NAME_COLLISIONS))
def test_collision_registry_has_no_stale_entries(selector):
    """A resolved collision left in the list would hide the next one."""
    users = {
        path.relative_to(ROOT).as_posix().split("/")[0]
        for path in _module_css_paths()
        if _defines_selector(read_text(path), selector)
    }
    assert len(users) > 1, (
        f"{selector} 는 더 이상 충돌하지 않는다 ({sorted(users)}) — 목록에서 지워라"
    )

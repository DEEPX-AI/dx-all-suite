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


# ── 통합 App Shell(Option A)로 이관된 모듈 ─────────────────────
# 이관된 모듈은 레일·헤더·탭·툴바 슬롯이 shared/shell.py 에서 서버 렌더
# 시점에 주입되므로, 템플릿 파일만 읽는 계약이 성립하지 않는다. 아래 목록에
# 한 줄 추가하면 이 파일의 계약들이 알아서 렌더된 HTML을 보고, 구 사이드바/
# topbar 를 전제한 검사에서 그 모듈을 빼준다.
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
    """서버가 실제로 내보내는 index.html (이관 모듈은 shell 주입 후)."""
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
    """이관 모듈의 툴바는 shared/shell.py 가 그리므로 렌더된 HTML로 검증한다."""
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

    This used to pin the toolbar beside the section nav (and before that, beside
    the eight-module dot strip). The nav went with the one-screen stage (spec
    2026-09-23 §5.1) — an anchor on a page that does not scroll points at nothing.
    What the contract protects is unchanged: the toolbar keeps its place in the bar.
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
    # .mz-topbar 는 shared/static/dx-shell.css 로 옮겼다 (Option A 이관).
    assert not re.search(r"^\s*" + re.escape(".mz-topbar") + r"\s*\{", css, re.M)
    assert ".mz-explorer-shell" in css, "모듈 고유 레이아웃은 계속 소유한다"
    assert ".mz-card" in css
    assert ".mz-detail-view" in css
    assert ".mz-btn" in css
    assert ".mz-logo" not in css, ".mz-logo is dead after brand migration"


def assert_local_topbar_token(css: str) -> None:
    """로컬 topbar 변수는 반드시 공유 헤더 높이에서 파생돼야 한다.

    통합 shell로 이관된 모듈은 여기에 탭 행 높이가 더해진다 — 그 변수는
    헤더가 아니라 "콘텐츠 위 chrome 총높이"를 뜻하기 때문이다.
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
# module's own component — `.lab-composer-palette-item:focus-visible` — is normal
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
    # .top-bar / .main-tab 은 shared/static/dx-shell.css 로 옮겼다 (Option A 이관).
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
    # .planner-topbar 는 shared/static/dx-shell.css 로 옮겼다 (Option A 이관).
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
    # .sidebar / .topbar 는 shared/static/dx-shell.css 로 옮겼다 (Option A 이관).
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

    # #header 는 shared/static/dx-shell.css 로 옮겼다 (Option A 이관).
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
    # 툴바 컨테이너는 shell 헤더가 소유한다 (렌더 검증은 위 전용 테스트).
    assert '<div class="topbar-right toolbar">' not in html
    assert "DXToolbar.init({ container: '.toolbar'" in html
    assert "DXToolbar.init({ container: '.topbar-right'" not in html
    # 탭 오버플로는 toolbar.js 이후에 초기화되어야 헤더 폭이 확정된 뒤 잰다.
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
    # shell(Option A)로 옮긴 셀렉터는 모듈에 남으면 두 정의가 싸운다.
    for selector in (".app", ".sidebar", ".topbar", ".topbar-right", ".nav-item", ".content-wrap"):
        assert not re.search(r"^\s*" + re.escape(selector) + r"\s*\{", css, re.M), (
            f"{selector} 는 shared/static/dx-shell.css 로 옮겼다"
        )
    # 모듈이 계속 소유하는 셀렉터
    # .toolbar / .card / .btn 은 공유 계층으로 올라갔다.
    # .ref-* 는 dx_stream 과 함께 shared/static/dx-components.css 로 올라갔다 —
    # 두 모듈이 Reference 화면 전체를 복제하고 있었기 때문이다.
    # (모듈이 계속 소유하는 셀렉터가 생기면 여기에 채운다)


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
    # theme is on — the guard used to fire on correct code.
    assert not re.search(r"(?<!prefers-)color-scheme\s*:\s*dark", css)
    assert "* { margin: 0; padding: 0; box-sizing: border-box; }" not in css
    for alias in (
        "--text:",
        "--text-muted:",
        "--text-dim:",
        "--border-glow:",
        "--app-color:",
        # --stream-color 는 뺐다. 런처에서 쓰던 마지막 자리(모듈별 활성 탭 색)가
        # 통일 강조색으로 바뀌면서 참조가 사라졌고, dx_stream 은 자기 파일에서
        # 따로 정의한다. 쓰이지 않는 토큰의 존재를 요구하면 정리를 막을 뿐이다.
        "--sandbox-color:",
        "--zoo-color:",
    ):
        assert alias in css, alias
    for selector in (
        ".top-bar",
        ".top-bar-right",
        # .status-dots 는 마크업이 사라졌다(홈 재설계). 이 목록이 그 스타일을
        # 붙잡고 있었고, 그 덕에 "어딘가 참조된다"는 이유로 고아 규칙이 남았다.
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
    """shared/dx_server.py의 handle_chat_routes()가 POST config/test 라우트를 소유."""
    shared_source = read_text(ROOT / "shared" / "dx_server.py")
    assert 'self.url_path == "/api/chat/config"' in shared_source
    assert 'self.url_path == "/api/chat/config/test"' in shared_source
    assert "save_config(" in shared_source
    assert "stream_chat(" in shared_source


def test_shared_chat_widget_owns_settings_panel_and_config_api():
    """chat-widget.js가 설정 패널과 config save API 호출을 소유. 저장이 먼저 연결을 확인한다 (2026-10-11 재설계 —
    따로 있던 Test 버튼 · /config/test 호출은 저장에 합쳐졌다; server route 는 남아 있다)."""
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
    """Provider별 model placeholder가 잘못된 OpenAI 기본값으로 고정되지 않아야 한다."""
    source = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.js")
    assert "const modelHints = {" in source
    assert "anthropic: 'claude-haiku-4-5-20251001'" in source
    assert "google: 'gemini-1.5-flash'" in source
    assert "custom: 'your-model-name'" in source
    assert "provider === 'github' ? 'gpt-4o-mini' : 'gpt-4o-mini'" not in source


def test_shared_chat_widget_retranslates_banner_without_refetching_config():
    """언어 변경은 상단 한 줄 (누가 답하는지) 만 다시 그리고 config API 를 다시 호출하지 않는다.
    배너는 2026-10-11 chat settings 재설계에서 그 한 줄 (_renderSource) 이 됐다."""
    source = read_text(ROOT / "shared" / "chat" / "static" / "chat-widget.js")
    assert "function _renderSource()" in source
    start = source.index("DXI18n.onLangChange(function() {")
    end = source.index("_history.forEach(m => _renderMessage", start)
    handler = source[start:end]
    assert "_renderSource();" in handler
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
        ".dx-chat-source-change",
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
    # 설정 글자는 key 로 달고 언어마다 번역한다 (tests/shared/test_chat_widget_lang_browser.py)
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
    # topbar gap이 간격을 담당하므로 page title은 margin-left를 가지면 안 된다.
    page_title_rule = re.search(r"\.dx-brand-page-title\s*\{(?P<body>.*?)\}", css, re.S).group("body")
    assert "margin-left" not in page_title_rule, "margin-left causes double spacing with topbar gap"
    # 값이 아니라 **무엇으로 간격을 주는지** 를 본다. 예전에는 `padding-left: 14px`
    # 를 글자 그대로 못박아서, 간격을 4px 스케일로 당기는 작업(2026-09-22)이 이
    # 계약과 부딪혔다. 이 테스트가 지키려는 것은 "margin 이 아니라 padding" 이지
    # 특정 픽셀이 아니다.
    assert re.search(r"padding-left:\s*(var\(--sp-|\d+px)", page_title_rule), (
        f"page title 이 padding-left 로 간격을 주지 않는다: {page_title_rule!r}")
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


def test_migrated_modules_leave_header_metrics_to_the_shell():
    """이관된 모듈에 헤더 치수가 남아 있으면 shell 정의와 싸운다.

    8개 모듈이 전부 이관된 지금 --dx-module-header-* 를 참조하는 곳은
    module-chrome.css(정의)와 dx-shell.css(사용) 둘뿐이어야 한다.
    """
    app_css = read_text(ROOT / "dx_app" / "static" / "css" / "style.css")
    stream_css = read_text(ROOT / "dx_stream" / "static" / "css" / "stream.css")

    # 이관 모듈은 dx-shell.css 가 헤더 치수를 소유한다 — 로컬에 남아 있으면 두 정의가 싸운다.
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
    """사이드바가 사라졌으므로 브랜드 자리는 헤더 좌측이 물려받는다."""
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
    # dx_app / dx_stream 이관 후 사이드바를 가진 모듈은 남아 있지 않다.
    # 다음 모듈이 이관 전 상태로 여기 들어오면 다시 채운다.
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
    """Topbar형 모듈 brand 영역은 같은 높이와 shadow를 사용한다."""
    planner_css = read_text(ROOT / "dx_planner" / "static" / "css" / "style.css")
    benchmark_css = read_text(ROOT / "dx_benchmark" / "static" / "css" / "style.css")
    monitor_css = read_text(ROOT / "dx_monitor" / "static" / "css" / "style.css")
    modelzoo_css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    sdk_css = read_text(ROOT / "launcher" / "static" / "sdk-library.css")
    compiler_css = read_text(ROOT / "dx_compiler" / "static" / "css" / "style.css")

    # dx_benchmark 는 통합 shell로 이관됐다. 헤더 자체는 dx-shell.css 가 소유하고,
    # 모듈에 남은 --benchmark-topbar-h 는 "콘텐츠 위 chrome 총높이"라서
    # 헤더 + 탭 행을 합산해야 한다 (탭 행을 빼먹으면 100vh 계산이 넘친다).
    assert (
        "--benchmark-topbar-h: calc(var(--dx-module-header-h) + var(--dx-tabs-h))"
        in benchmark_css
    ), "benchmark chrome height must include the shell tab row"

    # planner 도 이관됐다 — 남은 미이관 topbar 모듈이 없다.
    # 다음 모듈이 이관 전 상태로 들어오면 여기에 다시 추가한다.
    # dx_monitor 는 이관됐다 — 헤더 높이/오프셋은 dx-shell.css 가 소유한다.
    # dx_benchmark 는 이관됐다 — 헤더 elevation 은 dx-shell.css 가 소유한다.
    # 8개 모듈이 모두 이관돼 남은 topbar 서피스는 SDK Library 뿐이다.
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
        # dx_app 은 shell 헤더가 슬롯을 그리므로 렌더된 HTML로 본다.
        migrated = {v[0]: k for k, v in MIGRATED_SHELL_MODULES.items()}
        html = (
            rendered_index(migrated[rel]) if rel in migrated else read_text(ROOT / rel)
        )
        assert '<div class="dx-brand-slot"' in html, rel
        assert '<span class="dx-brand-slot"' not in html, rel


def test_modelzoo_brand_slot_is_a_block_element_after_the_shell_migration():
    """구 템플릿은 브랜드 슬롯을 <span> 으로 갖고 있었고 정리가 미뤄져 있었다.

    shell 헤더가 <div> 로 그리면서 그 부채가 자동으로 해소됐다.
    """
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
    """dx-tokens.css와 dx-utilities.css가 통합 깊이 토큰/유틸리티를 제공한다."""
    tokens_css = read_text(SHARED_STATIC / "dx-tokens.css")
    utilities_css = read_text(SHARED_STATIC / "dx-utilities.css")

    # 토큰 존재 확인
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

    # 유틸리티 셀렉터 존재 확인
    for sel in (".dx-surface-raised", ".dx-surface-glass", ".dx-surface-active", ".dx-text-glow"):
        assert sel in utilities_css, f"selector {sel} missing from dx-utilities.css"

    # 유틸리티 정확한 프래그먼트 확인
    assert "background: var(--surface-raised)" in utilities_css
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

    # active state 검증
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
    """아직 사이드바를 가진 모듈은 상단 chrome과 같은 depth를 쓴다.

    dx_app / dx_stream 은 통합 shell로 이관되어 사이드바가 없다."""
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
    """App/Stream의 실제 최종 카드 rule이 hard-coded gradient로 depth를 덮어쓰지 않는다."""
    SURFACE_SPECS = {
        "dx_app/static/css/style.css": [
            ".detail-info-card",
            ".pp-card",
            ".pcard",
            ".npu-card",
            ".plan-sc",
            ".comp-result-card",
            ".forum-item",
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
            # 공유 계층으로 승격된 카드는 그쪽이 최종 rule 이다. 승격됐다고
            # 계약에서 빼버리면 depth 회귀를 잡을 곳이 사라진다.
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
    """App/Stream은 이전 CSS URL과 달라야 기존 브라우저 캐시가 depth 변경을 가리지 않는다."""
    app_html = read_text(ROOT / "dx_app" / "templates" / "index.html")
    stream_html = read_text(ROOT / "dx_stream" / "templates" / "index.html")

    assert 'href="/static/css/style.css?m=dx_app_shell_a' in app_html
    assert 'href="/static/css/stream.css?m=dx_stream_shell_a' in stream_html


# ── 공통 컴포넌트 단일 소유 계약 ────────────────────────────────
# 목표: 공통 컴포넌트는 shared/static/dx-components.css 한 곳만 정의한다.
# 실측(2026-08-31): dx-components.css가 소유한 것은 .btn/.btn-ghost/.btn-sm/.fg/.badge뿐.
#   .btn  → dx_benchmark, dx_planner가 각자 다시 정의해 공유 정의를 덮는다.
#   .card → 소유자가 아예 없고 4개 모듈이 제각각 정의한다
#           (padding 20px vs var(--sp-4)=16px, dx_monitor는 shadow를 토큰 대신 하드코딩).
# 이관이 끝난 파일부터 allowlist에서 지운다 — stale 테스트가 그걸 강제한다.

COMPONENT_OWNER = "shared/static/dx-components.css"

# 컴포넌트가 아니라 유틸리티/셸이 소유하는 것들.
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

# 이미 shared 소유자가 있는데 모듈이 덮어쓰는 셀렉터.
OWNED_COMPONENT_OVERRIDES = {
    ".btn": set(),
    ".btn-ghost": set(),
    ".btn-danger": set(),
    # .card 는 dx-components.css 로 올라갔고 네 모듈의 사본은 전부 제거됐다.
    # 빈 집합이 곧 "이 컴포넌트는 끝났다"는 뜻이고, 새 재정의가 생기면 실패한다.
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

# shared 소유자가 아직 없어 모듈마다 재발명 중인 셀렉터.
# dx-components.css 로 올린 뒤 OWNED_COMPONENT_OVERRIDES 로 옮긴다.
UNOWNED_COMPONENTS = {}

MODULE_CSS_GLOBS = ("launcher/static/*.css", "dx_*/static/css/*.css")


def _module_css_paths() -> list[Path]:
    paths: list[Path] = []
    for pattern in MODULE_CSS_GLOBS:
        paths.extend(sorted(ROOT.glob(pattern)))
    return paths


def _defines_selector(css: str, selector: str) -> bool:
    """그 셀렉터를 정의하는 rule 이 있는가 — 그룹 셀렉터·주석·미디어쿼리를 견딘다."""
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
    """소유자가 생기면 이 테스트가 실패한다 — OWNED_COMPONENT_OVERRIDES로 옮기라는 신호."""
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
    """이관이 끝났는데 allowlist에 남아 있으면 다음 회귀를 못 잡는다."""
    stale = allowed - _redefining_files(selector)
    assert not stale, f"{selector} allowlist에서 지울 것: {sorted(stale)}"


# ── semantic 토큰 계층 ──────────────────────────────────────────
# primitive(dx-tokens.css) → semantic(dx-semantic.css) 2층 분리.
# 모듈 CSS는 semantic만 참조해야 재테마가 가능하다.
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

# 모듈 CSS 14,300줄이 아직 쓰는 물리적 이름. semantic 위 alias여야 한다.
# --bg-3 / --bg-4 는 대응하는 역할이 없어 dx-tokens.css의 리터럴을 그대로 둔다
# (semantic이 재정의하지 않으므로 primitive 값이 살아남는다).
# 은퇴한 이름들. 정의도 호출도 없어야 한다.
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
    """역할 이름 하나만 남는다.

    --bg-0 / --text-1 / --border 같은 옛 이름은 dx-tokens.css 와
    dx-semantic.css 두 곳에서 정의되고, 그중 primitive 쪽에는 light 값이
    없었다. 그래서 alias 가 하나라도 빠지면 그 자리가 light 테마에서 dark
    리터럴로 떨어졌다 — 실제로 --bg-3/--bg-4/--bg-1-rgb 가 그렇게 새고
    있었다. 이름을 한 벌로 줄여 그 함정을 없앤다.
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


# ── light 테마 ──────────────────────────────────────────────────
def test_light_theme_redefines_every_semantic_token():
    """빠진 토큰 하나가 light에서 dark 글자 위 dark 배경을 만든다."""
    css = read_text(SHARED_STATIC / "dx-theme-light.css")
    missing = [t for t in SEMANTIC_TOKENS if f"{t}:" not in css]
    assert not missing, f"light 테마에 빠진 semantic 토큰: {missing}"


def test_light_theme_covers_all_three_viewer_states():
    """명시 light / 명시 dark / 미스탬프(system) 세 상태를 모두 다뤄야 한다."""
    css = read_text(SHARED_STATIC / "dx-theme-light.css")
    assert ':root[data-theme="light"]' in css, "명시적 light 선택 규칙이 없다"
    assert "@media (prefers-color-scheme: light)" in css, "system light 규칙이 없다"
    assert ':root:not([data-theme="dark"])' in css, (
        "system light 규칙이 명시적 dark 선택을 이기지 못하게 가드해야 한다"
    )


def test_light_theme_defines_the_same_tokens_in_both_blocks():
    """한쪽에만 있는 토큰은 system-light 뷰어에서만 깨지는, 찾기 어려운 버그가 된다."""
    css = read_text(SHARED_STATIC / "dx-theme-light.css")
    explicit, _, system = css.partition("@media (prefers-color-scheme: light)")
    names = lambda blob: set(re.findall(r"(--[\w-]+)\s*:", blob))
    only_explicit = names(explicit) - names(system)
    only_system = names(system) - names(explicit)
    assert not only_explicit, f"명시 블록에만 있는 토큰: {sorted(only_explicit)}"
    assert not only_system, f"system 블록에만 있는 토큰: {sorted(only_system)}"


def test_light_theme_does_not_redefine_legacy_aliases():
    """은퇴한 이름을 light 테마가 되살리면 안 된다.

    여기 정의를 두면 그 이름이 light 에서만 살아나, dark 에서 값 없는
    이름을 부르는 모듈 CSS 가 생겨도 아무도 눈치채지 못한다."""
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



# ── 버튼 체계 계약 ──────────────────────────────────────────────
def test_button_size_modifier_carries_no_appearance():
    """.btn-sm 은 크기만 바꾼다.

    dx_app 사본이 여기에 background 와 border 색까지 넣는 바람에, 같은 요소에
    붙은 .btn-ghost 41개가 ghost 로 렌더되지 않았다 — 모듈 CSS가 공유 CSS보다
    뒤에 로드되기 때문이다. 크기 변형이 외형을 건드리면 그 조합은 전부 조용히 깨진다.
    """
    body = _css_rule_last(read_text(SHARED_STATIC / "dx-components.css"), ".btn-sm")
    flat = body.replace(" ", "")
    for prop in ("background:", "border-color:", "color:"):
        assert prop not in flat, f".btn-sm 이 외형을 건드린다: {prop}"


def test_button_base_reserves_a_transparent_border():
    """테두리 있는 변형과 없는 변형 사이에서 1px 크기 점프가 생기지 않아야 한다."""
    body = _css_rule_last(read_text(SHARED_STATIC / "dx-components.css"), ".btn")
    assert "border:1pxsolidtransparent" in body.replace(" ", "")


def test_no_module_ships_a_standalone_button_outside_the_shared_system():
    """`.btn` 없이 홀로 쓰이던 버튼 이름들은 공유 체계로 흡수됐다.

    이름이 `.btn-` 으로 시작하면서 `.btn` 체계 밖에 있는 클래스는 같은 것을
    두 번 만들게 만든다 — dx_compiler 의 .btn-small / .btn-secondary 가 그랬다.
    """
    retired = (".btn-small", ".btn-secondary", ".btn-acc-standalone")
    for path in _module_css_paths():
        css = read_text(path)
        for selector in retired:
            assert not _defines_selector(css, selector), (
                f"{path.relative_to(ROOT)} 가 은퇴한 {selector} 를 다시 정의한다"
            )



# ── 공유 컴포넌트 CSS 도달 범위 ─────────────────────────────────
COMPONENT_CSS_HREF = "/static/shared/dx-components.css"

ALL_SURFACES = {
    **SEMANTIC_SURFACES,
    "dx_agent_dev": "dx_agent_dev/templates/index.html",
}


@pytest.mark.parametrize("name,rel", sorted(ALL_SURFACES.items()))
def test_every_surface_loads_the_shared_component_layer(name, rel):
    """공유 컴포넌트 CSS 를 로드하지 않는 서피스가 있으면 통합이 그 모듈만 비켜간다.

    실측(2026-08-31): 9개 서피스 중 5개가 이 파일을 로드하지 않고 있었고,
    그 상태에서 .card / .btn 을 공유로 올리자 그 다섯 곳의 버튼이 브라우저
    기본 스타일로 돌아갔다 — 파운데이션 계약이 tokens/base/utilities 만 강제하고
    components 는 강제하지 않아 아무도 눈치채지 못했다.
    """
    html = head_html(read_text(ROOT / rel))
    assert COMPONENT_CSS_HREF.split("?")[0] in html, f"{name} 이 공유 컴포넌트 CSS를 로드하지 않는다"


@pytest.mark.parametrize("name,rel", sorted(ALL_SURFACES.items()))
def test_component_css_loads_after_the_foundation_and_before_module_css(name, rel):
    """모듈이 여전히 덮을 수 있어야 하고, 파운데이션 토큰은 이미 있어야 한다."""
    html = head_html(read_text(ROOT / rel))
    assert html.index("/static/shared/dx-utilities.css") < html.index(COMPONENT_CSS_HREF), name


# ── 이름 충돌 경계 ──────────────────────────────────────────────
# 서로 무관한 모듈이 같은 클래스 이름을 다른 뜻으로 쓰고 있는 것들이다.
# 병합 대상이 아니다 — 병합하면 한쪽이 깨진다. 위험한 건 이 이름 중 하나가
# 공유 계층으로 올라가는 순간이다. 실제로 `.page` 가 그랬다: dx_app 은
# 페이지 전환자(display:none), dx_benchmark 는 콘텐츠 컨테이너였고, 전환자를
# 셸로 올리자 benchmark 대시보드가 사라질 뻔했다.
#
# 이 테스트는 그 순간에 실패한다. 정말 공유해야 한다면 먼저 한쪽 이름을 바꿔라.
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
    """충돌이 해소됐는데 목록에 남아 있으면 다음 충돌을 못 잡는다."""
    users = {
        path.relative_to(ROOT).as_posix().split("/")[0]
        for path in _module_css_paths()
        if _defines_selector(read_text(path), selector)
    }
    assert len(users) > 1, (
        f"{selector} 는 더 이상 충돌하지 않는다 ({sorted(users)}) — 목록에서 지워라"
    )

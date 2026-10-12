from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def _js_block(source: str, name: str) -> str:
    match = re.search(rf"{name}\s*=\s*(\{{.*?\}}|\[.*?\]);", source, re.DOTALL)
    assert match, f"{name} block not found"
    return match.group(1)


def test_launcher_runtime_does_not_register_sandbox():
    src = read("launcher/launcher.py")
    assert "SANDBOX_PORT" not in src
    assert "SANDBOX_DIR" not in src
    assert 'start_sub_server("DX Sandbox"' not in src
    assert "start_sub_server('DX Sandbox'" not in src
    assert '"DX Sandbox":' not in src
    assert "'DX Sandbox':" not in src
    referer_targets = re.search(r"_SUBAPP_REFERER_TARGETS\s*=\s*[\(\[](.*?)[\)\]]", src, re.DOTALL)
    assert referer_targets
    assert "/sandbox" not in referer_targets.group(1)
    assert "SANDBOX_PORT" not in referer_targets.group(1)
    route_body = re.search(r"def route\(self\):(?P<body>.*?)(?=\n    def |\nclass |\Z)", src, re.DOTALL)
    assert route_body
    assert "/sandbox" not in route_body.group("body")


def test_launcher_state_registers_exact_eight_release_modules():
    """Eight modules, no sandbox — checked where the app actually routes.

    APP_PATHS is the one register. The names themselves are asserted where
    they are shown: the home's list.
    """
    src = read("launcher/static/launcher-state.js")
    app_paths = _js_block(src, "window.DXLauncher.APP_PATHS")
    assert "sandbox" not in app_paths
    assert app_paths.count(":") == 8

    html = read("launcher/static/index.html")
    for name in ("App", "Stream", "Model Zoo", "Compiler",
                 "EdgeGuide", "Benchmark", "Monitor", "Agent Dev"):
        assert ">" + name + "<" in html, f"{name} is missing from the home's list"
    assert "DX Sandbox" not in html


def test_launcher_navigation_shortcuts_are_compact_eight_modules():
    src = read("launcher/static/launcher.js")
    assert "launch('sandbox')" not in src
    expected = {
        "1": "app",
        "2": "stream",
        "3": "zoo",
        "4": "compiler",
        "5": "planner",
        "6": "benchmark",
        "7": "dx_monitor",
        "8": "agent",
    }
    for key, app in expected.items():
        pattern = rf"e\.altKey\s*&&\s*e\.key\s*===\s*['\"]{key}['\"][\s\S]{{0,220}}?ns\.launch\(['\"]{app}['\"]\)"
        assert re.search(pattern, src), f"Alt+{key} should launch {app}"
    # Shortcuts are compact/contiguous: Alt+1..Alt+8, no gap and no 9th key.
    assert "e.key === '9'" not in src


def test_launcher_app_frame_has_no_sandbox_nav_or_health_binding():
    src = read("launcher/static/launcher-app-frame.js")
    assert "launch('sandbox')" not in src
    assert "active-sandbox" not in src
    assert "dotSandbox" not in src
    assert "orbStatusSandbox" not in src
    assert "DX Sandbox" not in src
    nav = re.search(r"NAV_TAB_CONFIG\s*=\s*\[(.*?)\];", src, re.DOTALL)
    assert nav
    assert "sandbox" not in nav.group(1)


def test_launcher_home_copy_and_cards_are_eight_module_release():
    html = read("launcher/static/index.html")
    assert 'data-app="sandbox"' not in html
    assert "pm-dx-sandbox" not in html
    assert "dotSandbox" not in html
    assert "DX Sandbox" not in html
    assert "7 Modules" not in html
    assert "7개 모듈" not in html
    assert "8 Modules" in html
    assert "8개 모듈" in html
    assert "8 specialized modules" in html
    assert "8 モジュール" in html
    assert "8 módulos" in html
    assert "8 个模块" in html
    assert "8 個模組" in html
    # Eight modules, in the home grid's order, with no ninth and no sandbox. The two
    # books (SDK Library, About) are not modules and are not counted here. Update this
    # list together with the grid order.
    cards = re.findall(r'class="orbital-card"[^>]*\sdata-app="([^"]+)"', html)
    assert cards == [
        "app", "stream", "zoo", "compiler",
        "benchmark", "planner", "dx_monitor", "agent",
    ]


def test_the_intro_carries_no_module_list():
    """The intro does not name the modules, so it carries no module data either.

    The Gargantua sequence has one subject and it is not a menu. A module list
    (_SPLASH_MODULES) or icon table nobody reads is how a ninth module ends up
    with invented values for a layout that does not exist.
    """
    state = read("launcher/static/launcher-state.js")
    splash = read("launcher/static/launcher-splash.js")
    assert "_SPLASH_MODULES" not in state, "the intro's module list outlived its only reader"
    assert "_SPLASH_MODULES" not in splash
    assert "_MODULE_ICONS" not in splash, "the intro's icon table has no consumer"
    # The home's own list is where the eight modules are named, and it stays.
    html = read("launcher/static/index.html")
    assert html.count('class="orbital-card"') == 8


def test_the_offline_assistant_does_not_offer_the_excluded_sandbox():
    """The no-API-key assistant (FallbackEngine) must not mention DX Sandbox, which the release excludes, or a stale model count (340+)."""
    src = (ROOT / "shared" / "chat" / "fallback.py").read_text(encoding="utf-8")
    assert "Sandbox" not in src
    assert "340" not in src
    from shared.chat.fallback import COMMON_RULES
    help_rule = COMMON_RULES[1][1]
    for lang, text in help_rule.items():
        for module in ("DX App", "DX Stream", "DX Model Zoo", "DX Compiler", "DX Benchmark", "DX Monitor",
                       "DX EdgeGuide", "DX Agent Dev"):
            assert module in text, f"{lang}: {module} 이 도움말에 없다"

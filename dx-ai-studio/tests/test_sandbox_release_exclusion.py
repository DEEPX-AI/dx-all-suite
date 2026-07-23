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
    src = read("launcher/static/launcher-state.js")
    app_paths = _js_block(src, "window.DXLauncher.APP_PATHS")
    assert "sandbox" not in app_paths
    assert app_paths.count(":") == 8

    splash = _js_block(src, "window.DXLauncher._SPLASH_MODULES")
    assert "DX Sandbox" not in splash
    assert "sandbox" not in splash
    expected_names = [
        "DX App",
        "DX Stream",
        "DX Model Zoo",
        "DX Compiler",
        "DX EdgeGuide",
        "DX Benchmark",
        "DX Monitor",
        "DX Agent Dev",
    ]
    for name in expected_names:
        assert name in splash
    expected_angles = ["0", "45", "90", "135", "180", "225", "270", "315"]
    for angle in expected_angles:
        assert f"angle: {angle}" in splash


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
    cards = re.findall(r'class="orbital-card"[^>]+data-app="([^"]+)"[^>]+data-angle="([^"]+)"', html)
    assert cards == [
        ("app", "0"),
        ("stream", "45"),
        ("zoo", "90"),
        ("compiler", "135"),
        ("planner", "180"),
        ("benchmark", "225"),
        ("dx_monitor", "270"),
        ("agent", "315"),
    ]


def test_splash_branches_follow_module_count():
    src = read("launcher/static/launcher-splash.js")
    icons = _js_block(src, "var _MODULE_ICONS")
    assert "sandbox" not in icons
    assert "var mainAngles = [22.5" not in src
    assert "ns._SPLASH_MODULES.length" in src
    assert "360 / moduleCount" in src
    assert "ns._SPLASH_MODULES.map" in src

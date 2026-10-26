"""Launcher wiring for the dx_agent_dev module."""
import sys
from pathlib import Path

_STUDIO_ROOT = Path(__file__).resolve().parent.parent.parent
_LAUNCHER = _STUDIO_ROOT / "launcher"
if str(_STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDIO_ROOT))


def _launcher_mod():
    import importlib
    if "launcher" in sys.modules and not hasattr(sys.modules["launcher"], "__path__"):
        del sys.modules["launcher"]
    return importlib.import_module("launcher.launcher")


def _src():
    return (_LAUNCHER / "launcher.py").read_text(encoding="utf-8")


def test_agent_port_constant():
    src = _src()
    assert "AGENT_PORT" in src and "8099" in src


def test_proxy_ports_has_agent():
    launcher = _launcher_mod()
    assert launcher._LAUNCHER_PROXY_PORTS.get("dx_agent_dev") == 8099


def test_alias_has_agent():
    launcher = _launcher_mod()
    assert launcher.MODULE_KEY_ALIASES.get("agent") == "dx_agent_dev"


def test_proxy_path_has_agent():
    launcher = _launcher_mod()
    assert launcher._MODULE_PROXY_PATHS.get("dx_agent_dev") == "/agent/"


def test_display_name_mapping():
    launcher = _launcher_mod()
    assert launcher._DISPLAY_NAME_TO_CANONICAL.get("DX Agent Dev") == "dx_agent_dev"


def test_agent_dir_constant():
    launcher = _launcher_mod()
    assert launcher.AGENT_DIR.name == "dx_agent_dev"


def test_health_status_has_agent():
    launcher = _launcher_mod()
    assert "agent" in launcher._build_health_status()


def test_referer_target_has_agent_no_widget():
    # _SUBAPP_REFERER_TARGETS is a handler class variable, so the contract is pinned on the source text.
    # inject_widget=False: the console gets no chat widget (same as dx_monitor).
    src = _src()
    # ports resolve dynamically from _LAUNCHER_PROXY_PORTS → targets carry server_id
    assert '("/agent", "dx_agent_dev", False)' in src


def test_nav_tab_has_agent_card():
    js = (_LAUNCHER / "static" / "launcher-app-frame.js").read_text(encoding="utf-8")
    compact = js.replace(" ", "")
    assert "app:'agent'" in compact
    assert "Agent Dev" in js


def test_auth_policy_has_agent_prefix():
    # _PROXY_PREFIX_MAP must route map_launcher_proxy("/agent/") to dx_agent_dev
    src = (_STUDIO_ROOT / "shared" / "auth_policy.py").read_text(encoding="utf-8")
    assert '"/agent": "dx_agent_dev"' in src

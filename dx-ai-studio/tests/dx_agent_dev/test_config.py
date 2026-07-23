"""dx_agent_dev config 상수 테스트."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_default_port_is_8099():
    from core import config
    assert config.DEFAULT_PORT == 8099


def test_server_name():
    from core import config
    assert config.SERVER_NAME == "DX Agent Dev"


def test_workspace_root_under_studio():
    from core import config
    assert config.WORKSPACE_ROOT.name == "sessions"
    assert config.WORKSPACE_ROOT.parent.name == "dx_agent_dev"
    assert config.WORKSPACE_ROOT.parent.parent.name == "var"
    assert config.WORKSPACE_ROOT.parent.parent.parent == config.STUDIO_DIR


def test_static_and_templates_dirs():
    from core import config
    assert config.STATIC_DIR.name == "static"
    assert config.TEMPLATES_DIR.name == "templates"


def test_harness_search_paths_includes_suite_root():
    from core import config
    paths = config.harness_search_paths()
    assert config.SUITE_ROOT in paths
    assert (config.SUITE_ROOT / "dx-agent-dev") in paths


def test_harness_search_paths_env_override(monkeypatch):
    monkeypatch.setenv("DX_HARNESS_ROOT", "/tmp/custom-harness")
    from core import config
    paths = config.harness_search_paths()
    assert Path("/tmp/custom-harness") == paths[0]

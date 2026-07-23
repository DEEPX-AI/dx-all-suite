"""config.py 경로 계산 테스트"""
import sys, os, pytest, importlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


class TestConfig:
    def test_script_dir_points_to_dx_stream(self):
        from core.config import SCRIPT_DIR
        assert SCRIPT_DIR.name == "dx_stream"
        assert SCRIPT_DIR.is_dir()

    def test_suite_root_exists(self):
        from core.config import SUITE_ROOT
        assert (SUITE_ROOT / "dx-ai-studio").is_dir()
        assert (SUITE_ROOT / "dx-runtime").is_dir()

    def test_dx_stream_root_default(self):
        from core.config import DX_STREAM_ROOT
        assert "dx-runtime" in str(DX_STREAM_ROOT)
        assert str(DX_STREAM_ROOT).endswith("dx_stream")

    def test_dx_stream_root_env_override(self, monkeypatch, tmp_path):
        monkeypatch.setenv("DX_STREAM_ROOT", str(tmp_path))
        from core import config
        importlib.reload(config)
        assert str(config.DX_STREAM_ROOT) == str(tmp_path)
        monkeypatch.delenv("DX_STREAM_ROOT")
        importlib.reload(config)

    def test_static_dir_exists(self):
        from core.config import STATIC_DIR
        assert STATIC_DIR.name == "static"

    def test_templates_dir_exists(self):
        from core.config import TEMPLATES_DIR
        assert TEMPLATES_DIR.name == "templates"

    def test_port_default(self):
        from core.config import DEFAULT_PORT
        assert DEFAULT_PORT == 8093

    def test_model_list_json_path(self):
        from core.config import MODEL_LIST_JSON
        assert MODEL_LIST_JSON.name == "model_list.json"

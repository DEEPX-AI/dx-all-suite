"""metadata.py 테스트 — parse_model 래퍼"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


class TestMetadataModule:
    def test_module_importable(self):
        from core.metadata import get_model_metadata
        assert callable(get_model_metadata)

    def test_returns_dict_structure(self):
        from core.metadata import get_model_metadata
        # Call with a nonexistent file — should return error dict, not crash
        result = get_model_metadata("/nonexistent/model.dxnn")
        assert isinstance(result, dict)
        assert "error" in result or "raw_output" in result

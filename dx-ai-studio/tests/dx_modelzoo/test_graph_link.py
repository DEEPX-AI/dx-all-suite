"""modelzoo model graph must open in the dx-compiler viewer (DX-TRON removed).

The detail page resolves the model's ABSOLUTE local ONNX path via a server endpoint
(.../artifacts/onnx/localpath), then deep-links to /compiler/?viewer_path=<path>. When the
ONNX isn't downloaded locally it falls back to opening the compiler.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DETAIL = ROOT / "dx_modelzoo" / "static" / "js" / "detail.js"
SERVER = ROOT / "dx_modelzoo" / "server.py"
DICT = ROOT / "dx_modelzoo" / "static" / "js" / "i18n-dict-detail.js"


def test_detail_graph_button_deeplinks_via_localpath():
    src = DETAIL.read_text(encoding="utf-8")
    assert "function openModelzooGraph(" in src
    assert "/artifacts/onnx/localpath" in src, "must resolve the absolute local ONNX path"
    assert "/compiler/?viewer_path=" in src, "must deep-link into the dx-compiler viewer"
    # graceful fallback to the compiler when not locally available
    assert "'/compiler/'" in src or '"/compiler/"' in src


def test_server_artifact_localpath_returns_resolved_path():
    src = SERVER.read_text(encoding="utf-8")
    assert "/localpath" in src and "want_local_path" in src
    # returns the resolved absolute path as JSON for local artifacts
    assert '"path": result["path"]' in src


def test_view_model_graph_i18n_key_present_all_langs():
    src = DICT.read_text(encoding="utf-8")
    assert "'View Model Graph'" in src
    for lang in ("ko", "ja", "'zh-CN'", "'zh-TW'", "es"):
        assert lang in src

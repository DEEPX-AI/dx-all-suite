"""dx_app 📊 Graph must deep-link into the dx-compiler graph viewer (DX-TRON removed).

dx-compiler parses ONNX only, so the Graph button is gated to ONNX models (dx_app's
inference models are .dxnn → button hidden). The old handler called the removed
/api/compiler/dxtron + modal-dxtron and must be gone.
"""
from pathlib import Path

MODELS_JS = Path(__file__).resolve().parents[2] / "dx_app" / "static" / "js" / "models.js"


def test_open_model_graph_deeplinks_to_compiler_viewer():
    src = MODELS_JS.read_text(encoding="utf-8")
    assert "function openModelGraph(" in src, "openModelGraph must be defined (was in deleted compiler.js)"
    assert "/compiler/?viewer_path=" in src, "must deep-link into dx-compiler viewer"


def test_graph_button_gated_to_onnx_and_no_dxtron():
    src = MODELS_JS.read_text(encoding="utf-8")
    assert "_onnxGraphArg(" in src, "Graph button must be gated on an ONNX path"
    # no references to the removed DX-TRON modal / compiler API
    assert "modal-dxtron" not in src
    assert "/api/compiler/dxtron" not in src

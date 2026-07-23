"""dx-compiler graph viewer must support a ?viewer_path deep-link.

DX-TRON is removed this release; other Studio modules (dx_app, modelzoo) hand off an
ONNX model via /compiler/?viewer_path=<abs path> and land on the rendered graph. The
viewer auto-parses that path on init via the existing /viewer/parse → loadModel('input').
"""
from pathlib import Path

VIEWER = Path(__file__).resolve().parents[2] / "dx_compiler" / "static" / "js" / "viewer_panel.js"


def test_viewer_panel_reads_viewer_path_query_param():
    src = VIEWER.read_text(encoding="utf-8")
    assert "viewer_path" in src, "deep-link query param missing"
    assert "URLSearchParams" in src or "location.search" in src
    # auto-loads the model graph on the input tab via the existing parse path
    assert "loadModel('input'" in src or "loadModel(\"input\"" in src

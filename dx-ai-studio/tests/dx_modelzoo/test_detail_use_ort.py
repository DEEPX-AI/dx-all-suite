"""The Model Zoo detail screen shows the USE_ORT pair next to FPS / FPS-Watt (renderRuntimePerformance)."""
from pathlib import Path

JS = Path(__file__).resolve().parents[2] / "dx_modelzoo" / "static" / "js" / "detail.js"


def _body(src, header, span=900):
    start = src.index(header)
    return src[start:start + span]


def test_runtime_performance_block_lists_the_use_ort_pair():
    body = _body(JS.read_text(encoding="utf-8"), "function renderRuntimePerformance(model) {")
    assert "['USE_ORT FPS', performance.use_ort_fps" in body
    assert "['USE_ORT FPS/Watt', performance.use_ort_fps_per_watt" in body

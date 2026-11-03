"""The publish table's USE_ORT columns reach the catalog as CPU-tail-inclusive E2E performance.

USE_ORT ON = NPU part plus the host CPU tail run by ONNX Runtime (dx_benchmark REPORT.md), so these values
are kept apart from the benchmark dataset's use_ort rows and never folded into performance.fps.
"""
from pathlib import Path

from dx_modelzoo.metadata.adapters import parse_internal_table_html

FIXTURE = Path(__file__).resolve().parents[1] / "dx_app" / "fixtures" / "internal_publish_v2_sample.html"


def _densenet():
    models = parse_internal_table_html(FIXTURE.read_text(encoding="utf-8"))["models"]
    return next(v for v in models.values() if v.get("display.name") == "DenseNet-121")


def test_use_ort_fps_is_parsed_as_its_own_field():
    assert _densenet()["performance.use_ort_fps"] == 102.0


def test_use_ort_fps_per_watt_is_parsed_as_its_own_field():
    assert _densenet()["performance.use_ort_fps_per_watt"] == 242.58


def test_plain_fps_is_not_overwritten_by_the_use_ort_column():
    entry = _densenet()
    assert entry["performance.fps"] == 102.0
    assert entry["performance.fps_per_watt"] == 237.32

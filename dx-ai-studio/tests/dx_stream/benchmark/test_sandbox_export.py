"""sandbox_export.py 테스트: benchmark 결과 → sandbox JSON 형식 변환"""
import json
from pathlib import Path

import pytest

BENCHMARK_DIR = Path(__file__).resolve().parents[4] / "dx-runtime" / "dx_stream" / "dx_stream" / "apps" / "benchmark"
# Guard on the actual source file, not the directory: a stale __pycache__ leftover
# can keep the dir present after staging dx_stream removed the benchmark app.
_BENCHMARK_APP = BENCHMARK_DIR / "sandbox_export.py"
pytestmark = [
    pytest.mark.requires_dx_runtime,
    pytest.mark.skipif(
        not _BENCHMARK_APP.is_file(),
        reason="dx-runtime benchmark app is not available",
    ),
]

@pytest.fixture
def mock_results(tmp_path):
    """모의 benchmark 결과 디렉토리"""
    result_dir = tmp_path / "results" / "test_hw" / "run_001"
    result_dir.mkdir(parents=True)
    model_results = [
        {
            "model_name": "yolov8n",
            "npu_task_ms": 1.234,
            "cpu_0_ms": 0.548,
            "status": "ok",
            "parse_model_output": {
                "format_version": "v8",
                "dxcom_version": "v2.3.0",
                "total_memory_bytes": 7130112,
                "input_tensors": [{"name": "images", "dtype": "UINT8", "shape": [1, 640, 640, 3]}],
            },
        },
        {
            "model_name": "resnet50",
            "npu_task_ms": 1.978,
            "cpu_0_ms": 0.321,
            "status": "ok",
            "parse_model_output": {
                "format_version": "v8",
                "dxcom_version": "v2.3.0",
                "total_memory_bytes": 3145728,
                "input_tensors": [{"name": "input", "dtype": "UINT8", "shape": [1, 224, 224, 3]}],
            },
        },
    ]
    (result_dir / "model_results.json").write_text(json.dumps(model_results))
    return result_dir


class TestStripAnsi:
    def test_strips_color_codes(self):
        from benchmark.sandbox_export import strip_ansi
        assert strip_ansi("\x1b[32mv2.3.0\x1b[0m") == "v2.3.0"

    def test_no_ansi_unchanged(self):
        from benchmark.sandbox_export import strip_ansi
        assert strip_ansi("plain text") == "plain text"


class TestNormalizeModelKey:
    def test_basic(self):
        from benchmark.sandbox_export import normalize_model_key
        assert normalize_model_key("YoloV8N.dxnn") == "yolov8n"

    def test_preserves_dots(self):
        from benchmark.sandbox_export import normalize_model_key
        assert normalize_model_key("3ddfa_v2_mobilnet0.5_120x120.dxnn") == "3ddfa_v2_mobilnet0.5_120x120"


class TestExportSandbox:
    def test_creates_npu_inference_times(self, mock_results, tmp_path):
        from benchmark.sandbox_export import export_sandbox
        output = tmp_path / "sandbox_out"
        export_sandbox([mock_results], output)

        npu_path = output / "npu_inference_times.json"
        assert npu_path.exists()
        data = json.loads(npu_path.read_text())
        assert "measured_npu_ms" in data
        assert "overhead" in data
        assert data["measured_npu_ms"]["yolov8n"] == 1.234
        assert data["overhead"]["yolov8n"]["runtime_overhead_ms"] == 0.548

    def test_creates_model_metadata(self, mock_results, tmp_path):
        from benchmark.sandbox_export import export_sandbox
        output = tmp_path / "sandbox_out"
        export_sandbox([mock_results], output)

        meta_path = output / "model_metadata.json"
        assert meta_path.exists()
        data = json.loads(meta_path.read_text())
        assert "metadata" in data
        assert "models" in data
        assert "yolov8n" in data["models"]
        assert data["models"]["yolov8n"]["model_binary_bytes"] == 7130112

    def test_output_dir_created(self, mock_results, tmp_path):
        from benchmark.sandbox_export import export_sandbox
        output = tmp_path / "new_dir" / "sandbox"
        export_sandbox([mock_results], output)
        assert output.exists()


class TestExportNpuRatios:
    def test_basic_ratios(self, tmp_path):
        from benchmark.sandbox_export import export_npu_ratios
        m1 = {"yolov8n": 1.0, "resnet50": 2.0, "exclusive": 3.0}
        h1 = {"yolov8n": 0.4, "resnet50": 0.9}
        export_npu_ratios(m1, h1, tmp_path)

        path = tmp_path / "npu_ratios_empirical.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["ratios"]["yolov8n"] == 0.4
        assert data["ratios"]["resnet50"] == 0.45
        assert "exclusive" not in data["ratios"]
        assert data["mean_ratio"] is not None

    def test_empty_overlap(self, tmp_path):
        from benchmark.sandbox_export import export_npu_ratios
        m1 = {"modelA": 1.0}
        h1 = {"modelB": 0.5}
        export_npu_ratios(m1, h1, tmp_path)
        data = json.loads((tmp_path / "npu_ratios_empirical.json").read_text())
        assert data["mean_ratio"] is None

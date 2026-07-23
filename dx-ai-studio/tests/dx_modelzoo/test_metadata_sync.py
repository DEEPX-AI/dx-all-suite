"""메타데이터 동기화 스키마, 정규화, 어댑터 테스트."""
import json
import os
import tempfile
from pathlib import Path
import pytest

from dx_modelzoo.metadata import schema
from dx_modelzoo.metadata.normalization import (
    canonical_model_id,
    is_missing_source_value,
    normalize_source_value,
)


ROOT = Path(__file__).resolve().parents[2]
SUITE_ROOT = ROOT.parent




def test_metadata_status_enum_contains_required_states():
    assert schema.SOURCE_STATUS == {
        "provided",
        "not_provided",
        "benchmark_required",
        "metadata_pending",
        "artifact_unavailable",
        "source_error",
        "stale_cache",
        "suspect",
    }


def test_artifact_ids_are_allowlisted():
    assert schema.ARTIFACT_IDS == {
        "onnx",
        "qlite_dxnn",
        "qlite_json",
        "qpro_dxnn",
        "qpro_json",
    }


def test_canonical_model_id_normalizes_common_model_names():
    assert canonical_model_id("AlexNet.dxnn") == "alexnet"
    assert canonical_model_id("YoloV8N") == "yolov8n"
    assert canonical_model_id("DamoYolo_tinynasL20_T.dxnn") == "damoyolo_tinynasl20_t"


def test_normalize_source_value_treats_placeholders_as_missing():
    for value in (None, "", " ", "-", "None", "none", "N/A", "n/a", "NULL", "NA", "not provided"):
        assert is_missing_source_value(value) is True, f"expected {value!r} to be missing"
        assert normalize_source_value(value) is None, f"expected {value!r} to normalize to None"


def test_normalize_source_value_preserves_real_values():
    assert normalize_source_value("120x120x3") == "120x120x3"
    assert normalize_source_value("  AFLW20003D  ") == "AFLW20003D"
    assert normalize_source_value(0) == 0
    assert normalize_source_value(0.0) == 0.0
    assert normalize_source_value(0.0) is not None




from dx_modelzoo.metadata.adapters import local_runtime_adapter


def test_local_runtime_adapter_reads_registry_manifest_and_examples(tmp_path):
    suite_root = tmp_path
    dx_app = suite_root / "dx-runtime" / "dx_app"
    (dx_app / "config").mkdir(parents=True)
    (dx_app / "scripts").mkdir()
    (dx_app / "models").mkdir()
    (dx_app / "src" / "cpp_example" / "classification" / "AlexNet").mkdir(parents=True)
    (dx_app / "src" / "python_example" / "classification" / "AlexNet").mkdir(parents=True)

    (dx_app / "config" / "model_registry.json").write_text(json.dumps([{
        "model_name": "AlexNet",
        "original_name": "AlexNet",
        "dxnn_file": "AlexNet.dxnn",
        "add_model_task": "classification",
        "input_width": 224,
        "input_height": 224,
    }]), encoding="utf-8")
    (dx_app / "scripts" / "modelzoo_manifest.json").write_text(json.dumps([{
        "name": "AlexNet",
        "dxnn_url": "https://sdk.deepx.ai/modelzoo/dxnn/2_3_0/AlexNet.dxnn",
    }]), encoding="utf-8")
    (dx_app / "models" / "AlexNet.dxnn").write_text("dxnn", encoding="utf-8")

    result = local_runtime_adapter(suite_root)
    assert result["ok"] is True
    alexnet = result["models"]["alexnet"]
    assert alexnet["display.name"] == "AlexNet"
    assert alexnet["display.task"] == "classification"
    assert alexnet["specification.input_width"] == 224
    assert alexnet["specification.input_height"] == 224
    assert alexnet["artifacts.qlite_dxnn.remote_url"].endswith("/AlexNet.dxnn")
    assert "demo.cpp_example" in alexnet
    assert "demo.python_example" in alexnet


def test_local_runtime_adapter_stores_relative_local_artifact_path(tmp_path):
    """로컬 artifact 경로는 artifact resolver가 수용하는 DX_APP_ROOT 상대 경로여야 한다."""
    suite_root = tmp_path
    dx_app = suite_root / "dx-runtime" / "dx_app"
    (dx_app / "config").mkdir(parents=True)
    (dx_app / "scripts").mkdir()
    (dx_app / "models").mkdir()

    (dx_app / "config" / "model_registry.json").write_text(json.dumps([{
        "model_name": "AlexNet",
        "original_name": "AlexNet",
        "dxnn_file": "AlexNet.dxnn",
        "add_model_task": "classification",
        "input_width": 224,
        "input_height": 224,
    }]), encoding="utf-8")
    (dx_app / "scripts" / "modelzoo_manifest.json").write_text("[]", encoding="utf-8")
    (dx_app / "models" / "AlexNet.dxnn").write_text("dxnn", encoding="utf-8")

    result = local_runtime_adapter(suite_root)

    assert result["ok"] is True
    alexnet = result["models"]["alexnet"]
    assert alexnet["artifacts.qlite_dxnn.local_path"] == "models/AlexNet.dxnn"
    assert alexnet["artifacts.qlite_dxnn.local_exists"] is True


def test_local_runtime_adapter_uses_dx_app_model_name_as_catalog_id(tmp_path):
    """dxnn 파일명 정규화가 dx_app 모델 ID와 다를 때도 model_name을 catalog ID로 써야 한다."""
    suite_root = tmp_path
    dx_app = suite_root / "dx-runtime" / "dx_app"
    (dx_app / "config").mkdir(parents=True)
    (dx_app / "scripts").mkdir()

    (dx_app / "config" / "model_registry.json").write_text(json.dumps([{
        "model_name": "yolov7_w6",
        "original_name": "YOLOV7_W6",
        "dxnn_file": "YoloV7W6.dxnn",
        "add_model_task": "object_detection",
    }]), encoding="utf-8")
    (dx_app / "scripts" / "modelzoo_manifest.json").write_text(json.dumps([{
        "name": "YoloV7W6",
        "dxnn_url": "https://sdk.deepx.ai/modelzoo/dxnn/2_3_0/YoloV7W6.dxnn",
    }]), encoding="utf-8")

    result = local_runtime_adapter(suite_root)

    assert "yolov7_w6" in result["models"]
    assert "yolov7w6" not in result["models"]
    assert result["models"]["yolov7_w6"]["artifacts.qlite_dxnn.remote_url"].endswith("/YoloV7W6.dxnn")




from dx_modelzoo.metadata.adapters import (
    benchmark_cache_adapter,
    internal_modelzoo_adapter,
    parse_internal_table_html,
)


def test_parse_internal_table_fixture_extracts_requested_fields():
    html = (ROOT / "tests" / "dx_modelzoo" / "fixtures" / "modelzoo_internal_table.html").read_text()
    result = parse_internal_table_html(html)
    alexnet = result["models"]["alexnet"]
    assert alexnet["specification.dataset"] == "ImageNet"
    assert alexnet["specification.input_resolution"] == "224x224"
    assert alexnet["legal.license"] == "BSD-3-Clause"
    assert alexnet["legal.source_url"] == "https://github.com/pytorch/vision"
    assert alexnet["evaluation.raw.accuracy"] == "56.54 / 79.09"
    assert alexnet["evaluation.qlite.accuracy"] == "56.10 / 78.80"
    assert alexnet["performance.fps"] == 226.354


def test_parse_internal_table_uses_name_without_variant_suffix_for_join_key():
    """사이트 Name이 버전/variant suffix를 가져도 dx_app 모델 ID 기준으로 merge되어야 한다."""
    html = """
    <table>
      <thead>
        <tr>
          <th>Task</th><th>Name</th><th>Class Name</th><th>Input Resolution</th>
          <th>NPU Q-Lite Accuracy</th><th>FPS</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>face_alignment</td>
          <td>3ddfa_v2_mobilnetv1_120x120-1</td>
          <td>3ddfa_v2_mobilnetv1_120x120</td>
          <td>120x120</td>
          <td>1.23</td>
          <td>45.6</td>
        </tr>
      </tbody>
    </table>
    """

    result = parse_internal_table_html(html)

    assert "3ddfa_v2_mobilnetv1_120x120" in result["models"]
    assert "3ddfa_v2_mobilnetv1_120x120_1" not in result["models"]
    model = result["models"]["3ddfa_v2_mobilnetv1_120x120"]
    assert model["display.name"] == "3ddfa_v2_mobilnetv1_120x120-1"
    assert model["display.class_name"] == "3ddfa_v2_mobilnetv1_120x120"
    assert model["specification.input_resolution"] == "120x120"
    assert model["evaluation.qlite.accuracy"] == "1.23"
    assert model["performance.fps"] == 45.6


def test_parse_internal_table_multilevel_headers_keep_links_and_face_model_values():
    """실제 사이트의 그룹 헤더/링크 셀에서도 값과 다운로드 링크가 맞는 column에 들어가야 한다."""
    html = """
    <table>
      <thead>
        <tr>
          <th rowspan="3">Task</th><th rowspan="3">Name</th><th rowspan="3">Class Name</th>
          <th rowspan="3">Dataset</th><th rowspan="3">Input Resolution</th>
          <th rowspan="3">Operations</th><th rowspan="3">Parameters</th>
          <th rowspan="3">License</th><th rowspan="3">Metric</th><th rowspan="3">Source</th>
          <th colspan="2">Raw</th><th colspan="6">NPU</th><th colspan="2">Performance</th>
        </tr>
        <tr>
          <th rowspan="2">Accuracy</th><th rowspan="2">ONNX</th>
          <th colspan="3">Q-Lite</th><th colspan="3">Q-Pro</th>
          <th rowspan="2">FPS</th><th rowspan="2">FPS/Watt</th>
        </tr>
        <tr>
          <th>Accuracy</th><th>DXNN</th><th>JSON</th>
          <th>Accuracy</th><th>DXNN</th><th>JSON</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Face Landmark Detection</td>
          <td>3ddfa_v2_mobilnet0.5_120x120-1</td>
          <td>TDDFA_V2_MobileNet05</td>
          <td>AFLW20003D</td>
          <td>120x120x3</td>
          <td>0.07</td>
          <td>0.86</td>
          <td>MIT</td>
          <td>NME</td>
          <td><a href="https://github.com/cleardusk/3DDFA_V2">source</a></td>
          <td>3.499</td>
          <td><a href="https://modelzoo-api.devops.dpx.ai/modelzoo/api/files/TDDFA_V2_MobileNet05.onnx"></a></td>
          <td>3.5906</td>
          <td><a href="https://modelzoo-api.devops.dpx.ai/modelzoo/api/files/TDDFA_V2_MobileNet05.dxnn">download</a></td>
          <td><a href="https://modelzoo-api.devops.dpx.ai/modelzoo/api/files/TDDFA_V2_MobileNet05.json">json</a></td>
          <td>-</td>
          <td></td>
          <td></td>
          <td>15,798</td>
          <td>24,849.00</td>
        </tr>
        <tr>
          <td>Face Landmark Detection</td>
          <td>3ddfa_v2_mobilnetv1_120x120-1</td>
          <td>TDDFA_V2_MobileNetV1</td>
          <td>AFLW20003D</td>
          <td>120x120x3</td>
          <td>0.23</td>
          <td>3.29</td>
          <td>MIT</td>
          <td>NME</td>
          <td><a href="https://github.com/cleardusk/3DDFA_V2">source</a></td>
          <td>3.449</td>
          <td><a href="https://modelzoo-api.devops.dpx.ai/modelzoo/api/files/TDDFA_V2_MobileNetV1.onnx"></a></td>
          <td>3.5173</td>
          <td><a href="https://modelzoo-api.devops.dpx.ai/modelzoo/api/files/TDDFA_V2_MobileNetV1.dxnn">download</a></td>
          <td><a href="https://modelzoo-api.devops.dpx.ai/modelzoo/api/files/TDDFA_V2_MobileNetV1.json">json</a></td>
          <td>-</td>
          <td></td>
          <td></td>
          <td>8,110</td>
          <td>8,880.91</td>
        </tr>
      </tbody>
    </table>
    """

    result = parse_internal_table_html(html)

    assert "3ddfa_v2_mobilnetv1_120x120" in result["models"]
    assert "3ddfa_v2_mobilnetv1_120x120_1" not in result["models"]
    assert "3ddfa_v2_mobilnet0_5_120x120" in result["models"]
    model = result["models"]["3ddfa_v2_mobilnetv1_120x120"]
    assert model["display.class_name"] == "TDDFA_V2_MobileNetV1"
    assert model["specification.dataset"] == "AFLW20003D"
    assert model["specification.input_resolution"] == "120x120x3"
    assert model["specification.operations"] == "0.23"
    assert model["specification.parameters"] == "3.29"
    assert model["legal.license"] == "MIT"
    assert model["legal.source_url"] == "https://github.com/cleardusk/3DDFA_V2"
    assert model["evaluation.raw.accuracy"] == "3.449"
    assert model["artifacts.onnx.remote_url"].endswith("/TDDFA_V2_MobileNetV1.onnx")
    assert model["evaluation.qlite.accuracy"] == "3.5173"
    assert model["artifacts.qlite_dxnn.remote_url"].endswith("/TDDFA_V2_MobileNetV1.dxnn")
    assert model["artifacts.qlite_json.remote_url"].endswith("/TDDFA_V2_MobileNetV1.json")
    assert model["performance.fps"] == 8110.0
    assert model["performance.fps_per_watt"] == 8880.91

    mobilenet05 = result["models"]["3ddfa_v2_mobilnet0_5_120x120"]
    assert mobilenet05["display.class_name"] == "TDDFA_V2_MobileNet05"
    assert mobilenet05["evaluation.raw.accuracy"] == "3.499"
    assert mobilenet05["evaluation.qlite.accuracy"] == "3.5906"
    assert mobilenet05["artifacts.onnx.remote_url"].endswith("/TDDFA_V2_MobileNet05.onnx")
    assert mobilenet05["performance.fps"] == 15798.0
    assert mobilenet05["performance.fps_per_watt"] == 24849.0


def test_parse_internal_table_uses_each_table_header_independently():
    """여러 task table이 있는 실제 publish HTML에서는 table별 header를 섞으면 안 된다."""
    table = """
    <table>
      <thead>
        <tr>
          <th rowspan="3">Task</th><th rowspan="3">Name</th><th rowspan="3">Class Name</th>
          <th rowspan="3">Dataset</th><th rowspan="3">Input Resolution</th>
          <th rowspan="3">Operations</th><th rowspan="3">Parameters</th>
          <th rowspan="3">License</th><th rowspan="3">Metric</th><th rowspan="3">Source</th>
          <th colspan="2">Raw</th><th colspan="6">NPU</th><th colspan="2">Performance</th>
        </tr>
        <tr>
          <th rowspan="2">Accuracy</th><th rowspan="2">ONNX</th>
          <th colspan="3">Q-Lite</th><th colspan="3">Q-Pro</th>
          <th rowspan="2">FPS</th><th rowspan="2">FPS/Watt</th>
        </tr>
        <tr>
          <th>Accuracy</th><th>DXNN</th><th>JSON</th>
          <th>Accuracy</th><th>DXNN</th><th>JSON</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{task}</td><td>{name}</td><td>{class_name}</td><td>AFLW20003D</td>
          <td>120x120x3</td><td>{ops}</td><td>{params}</td><td>MIT</td><td>NME</td>
          <td><a href="https://github.com/cleardusk/3DDFA_V2">source</a></td>
          <td>{raw}</td><td><a href="https://sdk.deepx.ai/modelzoo/onnx/{name}.onnx"></a></td>
          <td>{qlite}</td><td><a href="https://sdk.deepx.ai/modelzoo/dxnn/2_3_0/{dxnn_name}.dxnn"></a></td>
          <td><a href="https://sdk.deepx.ai/modelzoo/json/{name}.json"></a></td>
          <td>-</td><td><a href="https://sdk.deepx.ai/modelzoo/dxnn/2_2_0/q-pro/{name}.dxnn"></a></td>
          <td><a href="https://sdk.deepx.ai/modelzoo/q-pro-json/{name}.json"></a></td>
          <td>{fps}</td><td>{fps_watt}</td>
        </tr>
      </tbody>
    </table>
    """
    html = table.format(
        task="Face Landmark Detection",
        name="3ddfa_v2_mobilnet0.5_120x120-1",
        class_name="TDDFA_V2_MobileNet05",
        ops="0.07",
        params="0.86",
        raw="3.499",
        qlite="3.5906",
        dxnn_name="3ddfa_v2_mobilnet0.5_120x120",
        fps="15,798",
        fps_watt="24,849.00",
    ) + table.format(
        task="Face Landmark Detection",
        name="3ddfa_v2_mobilnetv1_120x120-1",
        class_name="TDDFA_V2_MobileNetV1",
        ops="0.23",
        params="3.29",
        raw="3.449",
        qlite="3.5173",
        dxnn_name="3ddfa_v2_mobilnetv1_120x120",
        fps="8,110",
        fps_watt="8,880.91",
    )

    result = parse_internal_table_html(html)

    model = result["models"]["3ddfa_v2_mobilnet0_5_120x120"]
    assert model["evaluation.raw.accuracy"] == "3.499"
    assert model["evaluation.qlite.accuracy"] == "3.5906"
    assert model["artifacts.onnx.remote_url"].endswith("/3ddfa_v2_mobilnet0.5_120x120-1.onnx")
    assert model["artifacts.qlite_dxnn.remote_url"].endswith("/3ddfa_v2_mobilnet0.5_120x120.dxnn")
    assert model["artifacts.qpro_dxnn.remote_url"].endswith("/3ddfa_v2_mobilnet0.5_120x120-1.dxnn")
    assert model["performance.fps"] == 15798.0
    assert model["performance.fps_per_watt"] == 24849.0


def test_parse_internal_table_joins_by_artifact_basename_for_dx_app_id():
    """Class Name/Name이 dx_app ID와 달라도 artifact 파일명으로 internal metadata를 붙여야 한다."""
    html = """
    <table>
      <thead>
        <tr>
          <th>Task</th><th>Name</th><th>Class Name</th><th>Dataset</th>
          <th>Raw Accuracy</th><th>Raw ONNX</th><th>NPU Q-Lite Accuracy</th><th>NPU Q-Lite DXNN</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Object Detection</td><td>DamoYoloT-2</td><td>damoyolo_tinynas_l20_t</td><td>COCO</td>
          <td>42.543</td>
          <td><a href="https://sdk.deepx.ai/modelzoo/onnx/DamoYoloT-2.onnx"></a></td>
          <td>42.295</td>
          <td><a href="https://sdk.deepx.ai/modelzoo/dxnn/2_3_0/DamoYolo_tinynasL20_T.dxnn"></a></td>
        </tr>
      </tbody>
    </table>
    """

    result = parse_internal_table_html(html)

    assert "damoyolo_tinynasl20_t" in result["models"]
    model = result["models"]["damoyolo_tinynasl20_t"]
    assert model["evaluation.raw.accuracy"] == "42.543"
    assert model["evaluation.qlite.accuracy"] == "42.295"
    assert model["artifacts.qlite_dxnn.remote_url"].endswith("/DamoYolo_tinynasL20_T.dxnn")


def test_parse_internal_table_maps_hailo_artifact_suffix_to_h_model_id():
    """homepage의 *_Hailo artifact는 dx_app의 *_h 모델 ID로 merge되어야 한다."""
    html = """
    <table>
      <thead>
        <tr>
          <th>Task</th><th>Name</th><th>Class Name</th><th>Dataset</th>
          <th>Raw Accuracy</th><th>NPU Q-Lite DXNN</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Image Classification</td><td>RegNetX1_6GF-3</td><td>RegNetX_1_6GF_3</td><td>ImageNet</td>
          <td>77.060</td>
          <td><a href="https://sdk.deepx.ai/modelzoo/dxnn/2_3_0/RegNetX1_6GF_Hailo.dxnn"></a></td>
        </tr>
      </tbody>
    </table>
    """

    result = parse_internal_table_html(html)

    assert "regnetx1_6gf_h" in result["models"]
    assert result["models"]["regnetx1_6gf_h"]["evaluation.raw.accuracy"] == "77.060"


def test_parse_internal_table_does_not_overwrite_base_model_with_hailo_variant():
    """Name suffix를 제거한 fallback join이 기본 모델을 Hailo 변형으로 덮어쓰면 안 된다."""
    html = """
    <table>
      <thead>
        <tr>
          <th>Task</th><th>Name</th><th>Class Name</th><th>Dataset</th>
          <th>Raw Accuracy</th><th>NPU Q-Lite DXNN</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Object Detection</td><td>YOLOV5M-1</td><td>YoloV5M</td><td>COCO</td>
          <td>45.082</td>
          <td><a href="https://sdk.deepx.ai/modelzoo/dxnn/2_3_0/YoloV5M.dxnn"></a></td>
        </tr>
        <tr>
          <td>Object Detection</td><td>YOLOV5M-2</td><td>YoloV5M_640</td><td>COCO</td>
          <td>42.482</td>
          <td><a href="https://sdk.deepx.ai/modelzoo/dxnn/2_3_0/YoloV5M_Hailo.dxnn"></a></td>
        </tr>
      </tbody>
    </table>
    """

    result = parse_internal_table_html(html)

    assert result["models"]["yolov5m"]["evaluation.raw.accuracy"] == "45.082"
    assert result["models"]["yolov5m_h"]["evaluation.raw.accuracy"] == "42.482"


def test_parse_internal_table_maps_npu_scoped_performance_headers():
    """실제 사이트처럼 Performance가 NPU 그룹 아래 있어도 FPS/FPS-Watt를 읽어야 한다."""
    html = """
    <table>
      <thead>
        <tr>
          <th rowspan="3">Task</th><th rowspan="3">Name</th><th rowspan="3">Class Name</th>
          <th rowspan="3">Dataset</th><th rowspan="3">Input Resolution</th>
          <th rowspan="3">Operations</th><th rowspan="3">Parameters</th>
          <th rowspan="3">License</th><th rowspan="3">Metric</th><th rowspan="3">Source</th>
          <th colspan="2">Raw</th><th colspan="8">NPU</th>
        </tr>
        <tr>
          <th rowspan="2">Accuracy</th><th rowspan="2">ONNX</th>
          <th colspan="3">Q-Lite</th><th colspan="3">Q-Pro</th><th colspan="2">Performance</th>
        </tr>
        <tr>
          <th>Accuracy</th><th>DXNN</th><th>JSON</th>
          <th>Accuracy</th><th>DXNN</th><th>JSON</th>
          <th>FPS</th><th>FPS/Watt</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Face Landmark Detection</td><td>3ddfa_v2_mobilnet0.5_120x120-1</td>
          <td>TDDFA_V2_MobileNet05</td><td>AFLW20003D</td><td>120x120x3</td>
          <td>0.07</td><td>0.86</td><td>MIT</td><td>NME</td><td></td>
          <td>3.499</td><td></td><td>3.5906</td><td></td><td></td><td>-</td><td></td><td></td>
          <td>15,798</td><td>24,849.00</td>
        </tr>
      </tbody>
    </table>
    """

    result = parse_internal_table_html(html)

    model = result["models"]["3ddfa_v2_mobilnet0_5_120x120"]
    assert model["performance.fps"] == 15798.0
    assert model["performance.fps_per_watt"] == 24849.0


def test_internal_modelzoo_adapter_fetches_publish_html_and_parses_rows():
    """internal_modelzoo는 stub이 아니라 publish HTML을 가져와 parser 결과를 반환해야 한다."""
    html = """
    <table>
      <thead>
        <tr><th>Task</th><th>Name</th><th>Class Name</th><th>Dataset</th><th>Input Resolution</th><th>FPS</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>Face Landmark Detection</td>
          <td>3ddfa_v2_mobilnet0.5_120x120-1</td>
          <td>TDDFA_V2_MobileNet05</td>
          <td>AFLW20003D</td>
          <td>120x120x3</td>
          <td>15,798</td>
        </tr>
      </tbody>
    </table>
    """
    seen_urls = []

    def fake_fetch(url):
        seen_urls.append(url)
        return html

    result = internal_modelzoo_adapter(SUITE_ROOT, fetch_text=fake_fetch)

    assert result["adapter"] == "internal_modelzoo"
    assert result["profile"] == "internal"
    assert result["ok"] is True
    assert seen_urls == ["https://modelzoo-publish-api.devops.dpx.ai/publish/html"]
    model = result["models"]["3ddfa_v2_mobilnet0_5_120x120"]
    assert model["specification.dataset"] == "AFLW20003D"
    assert model["specification.input_resolution"] == "120x120x3"
    assert model["performance.fps"] == 15798.0


def test_benchmark_cache_adapter_reads_normalized_cache():
    cache = ROOT / "tests" / "dx_modelzoo" / "fixtures" / "benchmark_cache.json"
    result = benchmark_cache_adapter(cache)
    assert result["adapter"] == "benchmark_cache"
    assert result["ok"] is True

    alexnet = result["models"]["alexnet"]
    assert alexnet["performance.fps"] == 226.354
    assert alexnet["performance.fps_per_watt"] == 12.5
    assert alexnet["performance.source"] == "benchmark_report"
    assert alexnet["performance.measured_at"] == "2026-05-14T13:00:00+09:00"
    assert alexnet["performance.device"] == "DX-M1"

    yolo = result["models"]["yolov8n"]
    assert yolo["performance.fps"] == 58.7
    assert yolo.get("performance.fps_per_watt") is None




from dx_modelzoo.metadata.adapters import (
    local_modelzoo_repo_adapter,
    parse_modelzoo_model_file,
    parse_modelzoo_yaml_file,
)
from dx_modelzoo.metadata.adapters import _extract_all_model_infos


def test_parse_modelzoo_modelinfo_fixture_extracts_metadata():
    fixture = ROOT / "tests" / "dx_modelzoo" / "fixtures" / "dx_modelzoo_model_info.py"
    result = parse_modelzoo_model_file(fixture)
    # B: parse_modelzoo_model_file always returns {cid: fields} dict
    assert isinstance(result, dict)
    assert "alexnet" in result
    fields = result["alexnet"]
    assert fields["specification.dataset"] == "ImageNet"
    assert fields["specification.metric.name"] == "TopK1, TopK5"
    assert fields["evaluation.raw.accuracy"] == "56.54 79.09"
    assert fields["evaluation.qlite.accuracy"] == "56.10 78.80"
    assert fields.get("legal.source_url") is None


def test_parse_modelzoo_yaml_file_extracts_current_repo_metadata(tmp_path):
    """현재 dx-modelzoo YAML 구조에서도 dataset/spec/input 정보를 추출해야 한다."""
    yaml_path = tmp_path / "SampleModel.yaml"
    yaml_path.write_text("""
name: SampleModel
task: image_classification
reference: https://github.com/example/model
description: Sample description
macs: 1.50 GMACs
params: 11.74 M
inputs:
- name: input
  shape:
  - 1
  - 3
  - 218
  - 178
  dtype: float32
  layout: NCHW
dataset:
  type: CelebA
profiles:
  onnx:
    target: onnx
  q-lite:
    target: dxnn
  q-pro:
    target: dxnn
""", encoding="utf-8")

    result = parse_modelzoo_yaml_file(yaml_path)

    assert "samplemodel" in result
    fields = result["samplemodel"]
    assert fields["display.name"] == "SampleModel"
    assert fields["display.task"] == "image_classification"
    assert fields["specification.dataset"] == "CelebA"
    assert fields["specification.operations"] == "1.50 GMACs"
    assert fields["specification.parameters"] == "11.74 M"
    assert fields["specification.input_resolution"] == "218x178"
    assert fields["technical.input_shape"] == [1, 3, 218, 178]
    assert fields["legal.source_url"] == "https://github.com/example/model"
    assert fields["content.use_case.en"] == "Sample description"


def test_parse_modelzoo_yaml_file_keeps_dynamic_batch_shape_and_resolution(tmp_path):
    """YAML shape의 -1 batch도 input shape/resolution 추출을 깨지 않아야 한다."""
    yaml_path = tmp_path / "DynamicBatch.yaml"
    yaml_path.write_text("""
name: DynamicBatch
inputs:
- name: input
  shape:
  - -1
  - 3
  - 224
  - 224
dataset:
  type: ImageNet
""", encoding="utf-8")

    fields = parse_modelzoo_yaml_file(yaml_path)["dynamicbatch"]

    assert fields["technical.input_shape"] == [-1, 3, 224, 224]
    assert fields["specification.input_resolution"] == "224x224"


def test_parse_modelzoo_yaml_file_keeps_section_after_blank_lines(tmp_path):
    """YAML section 내부 빈 줄 때문에 dataset.type을 놓치면 안 된다."""
    yaml_path = tmp_path / "BlankDataset.yaml"
    yaml_path.write_text("""
name: BlankDataset
dataset:

  type: CelebA
""", encoding="utf-8")

    fields = parse_modelzoo_yaml_file(yaml_path)["blankdataset"]

    assert fields["specification.dataset"] == "CelebA"


def test_local_modelzoo_repo_adapter_reads_real_model_sources():
    result = local_modelzoo_repo_adapter(SUITE_ROOT)
    assert result["adapter"] == "local_modelzoo_repo"
    assert result["ok"] is True
    assert {"models", "errors", "warnings"}.issubset(result)
    assert any(
        "specification.dataset" in model or "evaluation.raw.accuracy" in model
        for model in result["models"].values()
    )




def test_modelinfo_with_parentheses_in_strings_extracts_all_fields():
    """ModelInfo 블록 내 문자열에 괄호가 포함되어도 모든 필드를 파싱해야 함."""
    text = '''
class SomeModel:
    info = ModelInfo(
        name="TestModel",
        dataset=DatasetType.imagenet,
        evaluation=EvaluationType.image_classification,
        raw_performance="56.54 (Top-1) / 79.09",
        q_lite_performance="56.10 (Top-1) / 78.80",
        q_pro_performance=None,
        source="https://github.com/example/repo",
    )
'''
    results = _extract_all_model_infos(text)
    assert "testmodel" in results
    fields = results["testmodel"]
    assert fields["evaluation.raw.accuracy"] == "56.54 (Top-1) / 79.09"
    assert fields["evaluation.qlite.accuracy"] == "56.10 (Top-1) / 78.80"
    assert fields.get("evaluation.qpro.accuracy") is None
    assert fields["legal.source_url"] == "https://github.com/example/repo"


def test_modelinfo_malformed_block_does_not_crash():
    """잘못된 ModelInfo 블록은 크래시 없이 빈 결과를 반환해야 함."""
    text = '''
class Broken:
    info = ModelInfo(
        name="broken",
        raw_performance="unclosed (paren
    # missing closing paren for ModelInfo
'''
    results = _extract_all_model_infos(text)
    # 잘못된 블록은 무시됨
    assert results == {}




def test_parse_modelzoo_model_file_always_returns_dict_of_models():
    """단일 모델이든 멀티 모델이든 항상 {cid: fields} dict를 반환."""
    fixture = ROOT / "tests" / "dx_modelzoo" / "fixtures" / "dx_modelzoo_model_info.py"
    result = parse_modelzoo_model_file(fixture)
    assert isinstance(result, dict)
    # 각 value는 또 다른 dict (fields)
    for cid, fields in result.items():
        assert isinstance(cid, str)
        assert isinstance(fields, dict)


def test_parse_modelzoo_multi_model_file_returns_stable_shape():
    """멀티 모델 파일도 동일한 {cid: fields} 형태."""
    text = '''
class ModelA:
    info = ModelInfo(
        name="ModelAlpha",
        dataset=DatasetType.imagenet,
        evaluation=EvaluationType.image_classification,
        raw_performance="90.0",
        q_lite_performance="89.0",
    )

class ModelB:
    info = ModelInfo(
        name="ModelBeta",
        dataset=DatasetType.coco,
        evaluation=EvaluationType.coco,
        raw_performance="45.0",
        q_lite_performance="44.0",
    )
'''
    results = _extract_all_model_infos(text)
    assert "modelalpha" in results
    assert "modelbeta" in results
    assert results["modelalpha"]["evaluation.raw.accuracy"] == "90.0"
    assert results["modelbeta"]["specification.dataset"] == "COCO"




def test_modelinfo_source_url_extraction():
    """source 필드가 정의된 ModelInfo에서 legal.source_url을 추출해야 함."""
    text = '''
class ResNet:
    info = ModelInfo(
        name="ResNet50",
        dataset=DatasetType.imagenet,
        evaluation=EvaluationType.image_classification,
        raw_performance="76.13 92.87",
        q_lite_performance="75.80 92.50",
        source="https://github.com/pytorch/vision",
    )
'''
    results = _extract_all_model_infos(text)
    assert "resnet50" in results
    assert results["resnet50"]["legal.source_url"] == "https://github.com/pytorch/vision"




def test_benchmark_cache_empty_model_id_is_skipped(tmp_path):
    """빈 model id는 결과에 포함되지 않고 경고를 생성해야 함."""
    cache_data = {
        "schema_version": "1.0",
        "device": "DX-M1",
        "models": {
            "": {"fps": 100.0, "fps_per_watt": None, "source": "test", "measured_at": "2026-01-01"},
            "...": {"fps": 50.0, "fps_per_watt": None, "source": "test", "measured_at": "2026-01-01"},
            "valid_model": {"fps": 200.0, "fps_per_watt": 10.0, "source": "test", "measured_at": "2026-01-01"},
        },
    }
    cache_file = tmp_path / "bench.json"
    cache_file.write_text(json.dumps(cache_data))
    result = benchmark_cache_adapter(cache_file)
    assert result["ok"] is True
    # 빈/무의미 id는 포함되지 않아야 함
    assert "" not in result["models"]
    # valid_model은 포함
    assert "valid_model" in result["models"]
    # 경고가 있어야 함
    assert len(result["warnings"]) > 0


def test_extract_all_model_infos_empty_name_is_skipped():
    """name이 빈 문자열인 ModelInfo는 결과에 포함되면 안 됨."""
    text = '''
class Empty:
    info = ModelInfo(
        name="",
        dataset=DatasetType.imagenet,
        raw_performance="50.0",
    )
'''
    results = _extract_all_model_infos(text)
    assert "" not in results
    assert len(results) == 0




def test_benchmark_cache_adapter_missing_path(tmp_path):
    """존재하지 않는 캐시 파일 → ok True, 빈 models, warning."""
    result = benchmark_cache_adapter(tmp_path / "nonexistent.json")
    assert result["ok"] is True
    assert result["models"] == {}
    assert len(result["warnings"]) > 0


def test_benchmark_cache_adapter_malformed_json(tmp_path):
    """잘못된 JSON → ok False, errors."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{invalid json content")
    result = benchmark_cache_adapter(bad_file)
    assert result["ok"] is False
    assert len(result["errors"]) > 0


def test_local_runtime_adapter_missing_registry(tmp_path):
    """registry 파일 없음 → ok False, errors."""
    result = local_runtime_adapter(tmp_path)
    assert result["ok"] is False
    assert len(result["errors"]) > 0


def test_local_modelzoo_repo_adapter_missing_models_dir(tmp_path):
    """models 디렉토리 없음 → ok False, errors."""
    result = local_modelzoo_repo_adapter(tmp_path)
    assert result["ok"] is False
    assert len(result["errors"]) > 0




def test_local_runtime_adapter_manifest_missing_name_skips_and_warns(tmp_path):
    """manifest 항목에 name 없으면 해당 항목만 건너뛰고 뒤 항목은 정상 처리."""
    # 최소 디렉토리 구조
    config_dir = tmp_path / "dx-runtime" / "dx_app" / "config"
    config_dir.mkdir(parents=True)
    scripts_dir = tmp_path / "dx-runtime" / "dx_app" / "scripts"
    scripts_dir.mkdir(parents=True)
    # example dirs (빈 디렉토리)
    (tmp_path / "dx-runtime" / "dx_app" / "src" / "cpp_example").mkdir(parents=True)
    (tmp_path / "dx-runtime" / "dx_app" / "src" / "python_example").mkdir(parents=True)

    # registry: ValidModel 하나
    registry = [
        {
            "model_name": "ValidModel",
            "original_name": "ValidModel",
            "dxnn_file": "ValidModel.dxnn",
            "add_model_task": "classification",
            "input_width": 224,
            "input_height": 224,
        }
    ]
    config_dir.joinpath("model_registry.json").write_text(json.dumps(registry))

    # manifest: 첫 항목 name 없음, 둘째 항목 ValidModel
    manifest = [
        {"dxnn_url": "http://bad/no_name.dxnn"},
        {"name": "ValidModel", "dxnn_url": "http://good/ValidModel.dxnn"},
    ]
    scripts_dir.joinpath("modelzoo_manifest.json").write_text(json.dumps(manifest))

    result = local_runtime_adapter(tmp_path)
    assert result["ok"] is True
    # 뒷 항목의 artifact URL이 정상 매핑되어야 함
    assert "validmodel" in result["models"]
    assert result["models"]["validmodel"]["artifacts.qlite_dxnn.remote_url"] == "http://good/ValidModel.dxnn"
    # name 누락 경고가 있어야 함
    assert any("missing" in w and "name" in w for w in result["warnings"])




def test_modelinfo_source_none_yields_legal_source_url_none():
    """source=None인 ModelInfo에서 legal.source_url이 None으로 설정되어야 함."""
    text = '''
class NoSource:
    info = ModelInfo(
        name="NoSourceModel",
        dataset=DatasetType.imagenet,
        evaluation=EvaluationType.image_classification,
        raw_performance="70.0",
        q_lite_performance="69.0",
        source=None,
    )
'''
    results = _extract_all_model_infos(text)
    assert "nosourcemodel" in results
    fields = results["nosourcemodel"]
    # source=None → legal.source_url 키가 존재하며 값이 None
    assert "legal.source_url" in fields
    assert fields["legal.source_url"] is None




from dx_modelzoo.metadata.merge import merge_adapter_results


def test_merge_prefers_internal_for_accuracy_but_runtime_for_model_list():
    runtime = {
        "adapter": "local_runtime", "ok": True, "models": {
            "alexnet": {
                "display.name": "AlexNet",
                "display.task": "classification",
                "specification.input_width": 224,
                "specification.input_height": 224,
                "artifacts.qlite_dxnn.remote_url": "https://sdk.deepx.ai/modelzoo/dxnn/2_3_0/AlexNet.dxnn",
            }
        }, "errors": [], "warnings": []
    }
    internal = {
        "adapter": "internal_modelzoo", "ok": True, "models": {
            "alexnet": {
                "evaluation.raw.accuracy": "56.54 / 79.09",
                "performance.fps": 226.354,
                "legal.license": "BSD-3-Clause",
            },
            "not_in_sdk": {"display.name": "NotInSDK"},
        }, "errors": [], "warnings": []
    }
    catalog = merge_adapter_results([runtime, internal], source_profile="internal")
    assert [m["id"] for m in catalog["models"]] == ["alexnet"]
    model = catalog["models"][0]
    assert model["evaluation"]["raw"]["accuracy"] == "56.54 / 79.09"
    assert model["performance"]["fps"] == 226.354
    assert model["legal"]["license"] == "BSD-3-Clause"
    assert model["provenance"]["performance.fps"]["source"] == "internal_modelzoo"


def test_merge_generates_missing_status_and_editorial_text():
    runtime = {
        "adapter": "local_runtime", "ok": True, "models": {
            "alexnet": {"display.name": "AlexNet", "display.task": "classification"}
        }, "errors": [], "warnings": []
    }
    catalog = merge_adapter_results([runtime], source_profile="local")
    model = catalog["models"][0]
    assert "performance.fps" in model["missing"]
    assert model["performance"]["source_status"] == "benchmark_required"
    assert model["processor"]["status"] == "metadata_pending"
    assert model["content"]["use_case"]["en"]




from dx_modelzoo.metadata.cache import atomic_write_json, load_catalog_cache
from dx_modelzoo.metadata.sync import resolve_source_profile


def test_resolve_source_profile_precedence(tmp_path, monkeypatch):
    config = tmp_path / "metadata_sync_config.json"
    config.write_text('{"source_profile":"public"}')
    assert resolve_source_profile(cli_source="internal", env={}, config_path=config) == "internal"
    assert resolve_source_profile(cli_source=None, env={"DX_MODELZOO_METADATA_SOURCE": "local"}, config_path=config) == "local"
    assert resolve_source_profile(cli_source=None, env={}, config_path=config) == "public"


def test_atomic_cache_write_and_corrupt_cache_fallback(tmp_path):
    path = tmp_path / "generated_catalog.cache.json"
    atomic_write_json(path, {"schema_version": "2.0", "models": []})
    assert load_catalog_cache(path)["schema_version"] == "2.0"
    path.write_text("{bad json")
    assert load_catalog_cache(path) is None


def test_atomic_write_json_uses_unique_temp_and_cleans_up(tmp_path):
    path = tmp_path / "generated_catalog.json"
    atomic_write_json(path, {"schema_version": "2.0", "models": []})
    atomic_write_json(path, {"schema_version": "2.0", "models": [{"id": "a"}]})
    assert json.loads(path.read_text(encoding="utf-8"))["models"][0]["id"] == "a"
    assert not (tmp_path / "generated_catalog.tmp").exists()
    assert not any(tmp_path.glob(".generated_catalog.json.*.tmp"))


def test_atomic_write_json_cleans_temp_on_serialization_failure(tmp_path):
    path = tmp_path / "generated_catalog.failure.json"
    with pytest.raises(TypeError):
        atomic_write_json(path, {"bad": object()})
    assert not path.exists()
    assert not any(tmp_path.glob(".generated_catalog.failure.json.*.tmp"))


def test_sync_metadata_cli_local_writes_only_dx_ai_studio(tmp_path):
    import subprocess
    import sys
    out = tmp_path / "generated_catalog.json"
    report = tmp_path / "sync_report.json"
    cache = tmp_path / "generated_catalog.cache.json"
    # I1: 소스 트리에 캐시가 남지 않도록 --cache를 tmp_path로 지정
    default_cache = ROOT / "dx_modelzoo" / "data" / "generated_catalog.cache.json"
    cmd = [
        sys.executable,
        str(ROOT / "dx_modelzoo" / "tools" / "sync_metadata.py"),
        "--source", "local",
        "--output", str(out),
        "--cache", str(cache),
        "--report", str(report),
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert report.exists()
    # 소스 트리의 기본 캐시 경로에 파일이 생성되지 않아야 함
    assert not default_cache.exists(), "CLI should not write cache to source tree default path"


from dx_modelzoo.metadata.sync import run_sync, adapter_names_for_profile


def test_sync_failure_keeps_prior_cache_and_marks_stale(tmp_path):
    """모든 어댑터가 실패할 때 이전 캐시를 stale_cache로 마킹하여 사용."""
    cache = tmp_path / "generated_catalog.cache.json"
    previous = {
        "schema_version": "2.0",
        "source_profile": "internal",
        "generated_at": "2026-05-14T13:00:00+09:00",
        "models": [{
            "id": "alexnet",
            "display": {"name": "AlexNet", "task": "classification"},
            "performance": {"fps": 123.0, "source_status": "provided"},
            "provenance": {"performance.fps": {"source": "internal_modelzoo"}},
        }],
    }
    atomic_write_json(cache, previous)

    def failing_adapter(name):
        def _f(*args, **kwargs):
            return {"adapter": name, "ok": False, "models": {}, "errors": [f"{name} down"], "warnings": []}
        return _f

    result = run_sync(
        source_profile="internal",
        suite_root=SUITE_ROOT,
        cache_path=cache,
        output_path=tmp_path / "generated_catalog.json",
        report_path=tmp_path / "sync_report.json",
        adapter_overrides={
            "local_runtime": failing_adapter("local_runtime"),
            "local_modelzoo_repo": failing_adapter("local_modelzoo_repo"),
            "benchmark_cache": failing_adapter("benchmark_cache"),
            "internal_modelzoo": failing_adapter("internal_modelzoo"),
        },
    )
    model = result["catalog"]["models"][0]
    assert model["performance"]["fps"] == 123.0
    assert model["performance"]["source_status"] == "stale_cache"
    assert result["report"]["adapter_errors"]


def test_offline_mode_skips_network_adapters():
    assert adapter_names_for_profile("internal", offline=True) == [
        "local_runtime",
        "local_modelzoo_repo",
        "benchmark_cache",
    ]




def test_sync_network_failure_preserves_fresh_local_catalog(tmp_path):
    """로컬 어댑터가 성공하고 네트워크만 실패하면 fresh 카탈로그를 유지해야 함."""
    cache = tmp_path / "generated_catalog.cache.json"
    # 이전 캐시: alexnet fps 123.0
    previous = {
        "schema_version": "2.0",
        "source_profile": "internal",
        "generated_at": "2026-05-14T13:00:00+09:00",
        "models": [{
            "id": "alexnet",
            "display": {"name": "AlexNet", "task": "classification"},
            "performance": {"fps": 123.0, "source_status": "provided"},
            "provenance": {"performance.fps": {"source": "internal_modelzoo"}},
        }],
    }
    atomic_write_json(cache, previous)

    # 로컬 어댑터: 성공 (fresh display + artifact)
    def local_runtime_ok(*a, **kw):
        return {
            "adapter": "local_runtime", "ok": True,
            "models": {
                "alexnet": {
                    "display.name": "AlexNet",
                    "display.task": "classification",
                    "artifacts.qlite_dxnn.remote_url": "http://fresh/AlexNet.dxnn",
                },
            },
            "errors": [], "warnings": [],
        }

    def local_repo_ok(*a, **kw):
        return {"adapter": "local_modelzoo_repo", "ok": True, "models": {}, "errors": [], "warnings": []}

    def bench_ok(*a, **kw):
        return {"adapter": "benchmark_cache", "ok": True, "models": {}, "errors": [], "warnings": []}

    # 네트워크 어댑터: 실패
    def net_fail(*a, **kw):
        return {"adapter": "internal_modelzoo", "ok": False, "models": {}, "errors": ["network down"], "warnings": []}

    result = run_sync(
        source_profile="internal",
        suite_root=tmp_path,
        cache_path=cache,
        output_path=tmp_path / "catalog.json",
        report_path=tmp_path / "report.json",
        adapter_overrides={
            "local_runtime": local_runtime_ok,
            "local_modelzoo_repo": local_repo_ok,
            "benchmark_cache": bench_ok,
            "internal_modelzoo": net_fail,
        },
    )

    model = result["catalog"]["models"][0]
    # fresh 로컬 카탈로그를 사용해야 함 – stale fps 123.0으로 교체되면 안 됨
    assert model["display"]["name"] == "AlexNet"
    assert model["artifacts"]["qlite_dxnn"]["remote_url"] == "http://fresh/AlexNet.dxnn"
    assert model["performance"].get("fps") != 123.0  # stale 값이 아님
    assert model["performance"]["source_status"] != "stale_cache"
    # 네트워크 에러가 report에 기록되어야 함
    assert any("network down" in e for e in result["report"]["adapter_errors"])


def test_sync_all_adapters_fail_uses_stale_cache(tmp_path):
    """모든 어댑터 실패 시에만 이전 캐시를 stale_cache로 사용."""
    cache = tmp_path / "generated_catalog.cache.json"
    previous = {
        "schema_version": "2.0",
        "source_profile": "internal",
        "generated_at": "2026-05-14T13:00:00+09:00",
        "models": [{
            "id": "alexnet",
            "display": {"name": "AlexNet", "task": "classification"},
            "performance": {"fps": 123.0, "source_status": "provided"},
        }],
    }
    atomic_write_json(cache, previous)

    def fail_adapter(name):
        def _f(*a, **kw):
            return {"adapter": name, "ok": False, "models": {}, "errors": [f"{name} failed"], "warnings": []}
        return _f

    result = run_sync(
        source_profile="internal",
        suite_root=tmp_path,
        cache_path=cache,
        output_path=tmp_path / "catalog.json",
        report_path=tmp_path / "report.json",
        adapter_overrides={
            "local_runtime": fail_adapter("local_runtime"),
            "local_modelzoo_repo": fail_adapter("local_modelzoo_repo"),
            "benchmark_cache": fail_adapter("benchmark_cache"),
            "internal_modelzoo": fail_adapter("internal_modelzoo"),
        },
    )

    model = result["catalog"]["models"][0]
    assert model["performance"]["fps"] == 123.0
    assert model["performance"]["source_status"] == "stale_cache"




def test_missing_includes_fps_per_watt_when_absent():
    """fps_per_watt가 없으면 missing에 포함되어야 함 (_REQUIRED_PERF_FIELDS 활용)."""
    runtime = {
        "adapter": "local_runtime", "ok": True, "models": {
            "alexnet": {"display.name": "AlexNet", "display.task": "classification"}
        }, "errors": [], "warnings": []
    }
    catalog = merge_adapter_results([runtime], source_profile="local")
    model = catalog["models"][0]
    assert "performance.fps" in model["missing"]
    assert "performance.fps_per_watt" in model["missing"]




def test_merge_performance_defaults_to_none_when_absent():
    """fps, fps_per_watt가 없으면 None으로 출력 (deterministic)."""
    runtime = {
        "adapter": "local_runtime", "ok": True, "models": {
            "alexnet": {"display.name": "AlexNet", "display.task": "classification"}
        }, "errors": [], "warnings": []
    }
    catalog = merge_adapter_results([runtime], source_profile="local")
    model = catalog["models"][0]
    assert model["performance"]["fps"] is None
    assert model["performance"]["fps_per_watt"] is None


def test_merge_missing_includes_artifact_ids_when_absent():
    """아티팩트가 없으면 모든 ARTIFACT_IDS가 missing에 포함되어야 함."""
    runtime = {
        "adapter": "local_runtime", "ok": True, "models": {
            "alexnet": {"display.name": "AlexNet", "display.task": "classification"}
        }, "errors": [], "warnings": []
    }
    catalog = merge_adapter_results([runtime], source_profile="local")
    model = catalog["models"][0]
    for aid in schema.ARTIFACT_IDS:
        assert aid in model["missing"], f"{aid} should be in missing"


def test_merge_present_artifact_not_in_missing():
    """아티팩트가 있으면 missing에서 제외되어야 함."""
    runtime = {
        "adapter": "local_runtime", "ok": True, "models": {
            "alexnet": {
                "display.name": "AlexNet",
                "display.task": "classification",
                "artifacts.qlite_dxnn.remote_url": "http://example.com/AlexNet.dxnn",
            }
        }, "errors": [], "warnings": []
    }
    catalog = merge_adapter_results([runtime], source_profile="local")
    model = catalog["models"][0]
    assert "qlite_dxnn" not in model["missing"]
    # 다른 아티팩트는 여전히 missing
    assert "onnx" in model["missing"]
    assert "qlite_json" in model["missing"]


def test_string_none_input_resolution_not_propagated():
    """문자열 'None'이 input_resolution에 전파되지 않아야 한다."""
    runtime = {
        "adapter": "local_runtime", "ok": True,
        "models": {
            "testmodel": {
                "display.name": "TestModel",
                "display.task": "classification",
            }
        }, "errors": [], "warnings": []
    }
    table = {
        "adapter": "internal_table", "ok": True,
        "models": {
            "testmodel": {
                "specification.input_resolution": "None",
            }
        }, "errors": [], "warnings": []
    }
    catalog = merge_adapter_results([runtime, table], source_profile="local")
    model = catalog["models"][0]
    spec = model.get("specification", {})
    assert spec.get("input_resolution") != "None"


def test_dash_placeholder_stripped_through_parse_and_merge():
    """통합 테스트: HTML 대시 플레이스홀더가 parse → merge를 거치면 필드에서 제거된다."""
    html = """
    <table>
      <thead>
        <tr>
          <th>Task</th><th>Name</th><th>Class Name</th>
          <th>Input Resolution</th><th>NPU Q-Lite Accuracy</th><th>FPS</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>classification</td>
          <td>SmokeModel</td>
          <td>SmokeModel</td>
          <td>-</td>
          <td>-</td>
          <td>100.5</td>
        </tr>
      </tbody>
    </table>
    """
    table_result = parse_internal_table_html(html)

    runtime = {
        "adapter": "local_runtime", "ok": True,
        "models": {
            "smokemodel": {
                "display.name": "SmokeModel",
                "display.task": "classification",
                "specification.input_width": 0,
            },
        }, "errors": [], "warnings": [],
    }
    table_adapter = {
        "adapter": "internal_table", "ok": True,
        "models": table_result["models"],
        "errors": [], "warnings": [],
    }

    catalog = merge_adapter_results([runtime, table_adapter], source_profile="internal")
    model = [m for m in catalog["models"] if m["id"] == "smokemodel"][0]

    # 대시 플레이스홀더가 제거되어야 함
    spec = model.get("specification", {})
    assert spec.get("input_resolution") != "-"
    evaluation = model.get("evaluation", {})
    assert evaluation.get("qlite", {}).get("accuracy") != "-"

    # 숫자 0은 보존되어야 함
    assert spec.get("input_width") == 0




def test_modelinfo_block_quarantines_qlite_zero_accuracy():
    """ModelInfo에서 q_lite_performance='0.0'은 suspect로 격리되어야 한다."""
    text = '''
ModelInfo(
    name="ZeroModel",
    raw_performance="72.5",
    q_lite_performance="0.0",
)
'''
    result = _extract_all_model_infos(text)
    assert "zeromodel" in result
    fields = result["zeromodel"]
    # q_lite '0.0' → suspect quarantine
    assert "evaluation.qlite.accuracy" not in fields
    assert fields["evaluation.qlite.source_status"] == "suspect"
    assert fields["evaluation.qlite.suspect_value"] == "0.0"
    # raw 정상 값은 그대로
    assert fields["evaluation.raw.accuracy"] == "72.5"
    assert "evaluation.raw.source_status" not in fields


def test_modelinfo_block_does_not_quarantine_real_qlite_accuracy():
    """정상 q_lite_performance 값은 quarantine하지 않아야 한다."""
    text = '''
ModelInfo(
    name="NormalModel",
    q_lite_performance="56.10 78.80",
)
'''
    result = _extract_all_model_infos(text)
    fields = result["normalmodel"]
    assert fields["evaluation.qlite.accuracy"] == "56.10 78.80"
    assert "evaluation.qlite.source_status" not in fields
    assert "evaluation.qlite.suspect_value" not in fields


def test_modelinfo_block_quarantines_all_performance_zero_variants():
    """raw/qlite/qpro/qmaster 모두 0 값이면 suspect로 처리되어야 한다."""
    text = '''
ModelInfo(
    name="AllZero",
    raw_performance="0",
    q_lite_performance="0.0",
    q_pro_performance="0.00",
    q_master_performance="0",
)
'''
    result = _extract_all_model_infos(text)
    fields = result["allzero"]
    for prefix, zero_val in [
        ("evaluation.raw", "0"),
        ("evaluation.qlite", "0.0"),
        ("evaluation.qpro", "0.00"),
        ("evaluation.qmaster", "0"),
    ]:
        assert f"{prefix}.accuracy" not in fields, f"{prefix} should be quarantined"
        assert fields[f"{prefix}.source_status"] == "suspect", f"{prefix}"
        assert fields[f"{prefix}.suspect_value"] == zero_val, f"{prefix}"


def test_internal_table_marks_qlite_zero_accuracy_as_suspect():
    html = """
    <table><thead><tr>
      <th>Name</th><th>Class Name</th><th>NPU Q-Lite Accuracy</th>
    </tr></thead><tbody><tr>
      <td>yolov8n-1</td><td>YOLOv8n</td><td>0.0</td>
    </tr></tbody></table>
    """
    result = parse_internal_table_html(html)
    model = result["models"]["yolov8n"]
    assert "evaluation.qlite.accuracy" not in model
    assert model["evaluation.qlite.source_status"] == "suspect"
    assert model["evaluation.qlite.suspect_value"] == "0.0"


def test_internal_table_does_not_quarantine_real_accuracy():
    """정상적인 accuracy 값(0이 아닌)은 quarantine하지 않아야 한다."""
    html = """
    <table><thead><tr>
      <th>Name</th><th>Class Name</th><th>NPU Q-Lite Accuracy</th>
    </tr></thead><tbody><tr>
      <td>alexnet-1</td><td>AlexNet</td><td>56.10</td>
    </tr></tbody></table>
    """
    result = parse_internal_table_html(html)
    model = result["models"]["alexnet"]
    assert model["evaluation.qlite.accuracy"] == "56.10"
    assert "evaluation.qlite.source_status" not in model
    assert "evaluation.qlite.suspect_value" not in model


def test_internal_table_does_not_quarantine_fps_zero():
    """FPS 0 값은 quarantine하지 않아야 한다 – accuracy 필드만 대상."""
    html = """
    <table><thead><tr>
      <th>Name</th><th>Class Name</th><th>FPS</th>
    </tr></thead><tbody><tr>
      <td>testmodel-1</td><td>TestModel</td><td>0.0</td>
    </tr></tbody></table>
    """
    result = parse_internal_table_html(html)
    model = result["models"]["testmodel"]
    assert model["performance.fps"] == 0.0


def test_internal_table_quarantines_all_zero_accuracy_variants():
    """0, 0.0, 0.00 모두 suspect로 처리되어야 한다."""
    for zero_str in ("0", "0.0", "0.00"):
        html = f"""
        <table><thead><tr>
          <th>Name</th><th>Class Name</th><th>Raw Accuracy</th>
        </tr></thead><tbody><tr>
          <td>model-1</td><td>Model</td><td>{zero_str}</td>
        </tr></tbody></table>
        """
        result = parse_internal_table_html(html)
        model = result["models"]["model"]
        assert "evaluation.raw.accuracy" not in model, f"zero_str={zero_str}"
        assert model["evaluation.raw.source_status"] == "suspect", f"zero_str={zero_str}"
        assert model["evaluation.raw.suspect_value"] == zero_str, f"zero_str={zero_str}"




from dx_modelzoo.metadata.sync import run_sync


def test_coverage_report_counts_missing_and_suspect_fields(tmp_path):
    """run_sync 리포트에 coverage 섹션이 포함되어야 한다."""
    def fake_runtime(*a, **kw):
        return {
            "adapter": "local_runtime", "ok": True, "errors": [], "warnings": [],
            "models": {
                "complete_model": {
                    "display.name": "CompleteModel",
                    "display.task": "classification",
                    "performance.fps": 30.0,
                    "performance.fps_per_watt": 5.0,
                    "legal.license": "MIT",
                    "evaluation.qlite.accuracy": 0.95,
                },
                "incomplete_model": {
                    "display.name": "IncompleteModel",
                    "display.task": "object_detection",
                    "evaluation.qlite.source_status": "suspect",
                    "evaluation.qlite.suspect_value": "0.0",
                },
            },
        }

    result = run_sync(
        source_profile="local",
        suite_root=tmp_path,
        output_path=tmp_path / "generated.json",
        cache_path=tmp_path / "cache.json",
        report_path=tmp_path / "report.json",
        adapter_overrides={
            "local_runtime": fake_runtime,
            "local_modelzoo_repo": lambda *a, **kw: {
                "adapter": "local_modelzoo_repo", "ok": True,
                "models": {}, "errors": [], "warnings": [],
            },
            "benchmark_cache": lambda *a, **kw: {
                "adapter": "benchmark_cache", "ok": True,
                "models": {}, "errors": [], "warnings": [],
            },
        },
    )

    report = result["report"]
    assert "coverage" in report
    coverage = report["coverage"]
    assert coverage["missing_by_field"]["performance.fps"] >= 1
    assert coverage["suspect_by_field"]["evaluation.qlite.accuracy"] >= 1


def test_display_fields_have_summary_and_category_label():
    """병합 결과의 각 모델에 display.summary와 display.category_label이 있어야 한다."""
    runtime = {
        "adapter": "local_runtime", "ok": True, "errors": [], "warnings": [],
        "models": {
            "alexnet": {
                "display.name": "AlexNet",
                "display.task": "classification",
            },
            "yolov8n": {
                "display.name": "YoloV8N",
                "display.task": "object_detection",
            },
        },
    }
    catalog = merge_adapter_results([runtime], source_profile="local")
    for model in catalog["models"]:
        assert model["display"]["summary"], f"missing summary for {model['id']}"
        assert model["display"]["category_label"], f"missing category_label for {model['id']}"




def test_resolve_source_profile_reads_from_data_subdir(tmp_path):
    """resolve_source_profile이 dx_modelzoo/data/ 하위 config를 읽을 수 있어야 한다."""
    config_dir = tmp_path / "dx-ai-studio" / "dx_modelzoo" / "data"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "metadata_sync_config.json"
    config_path.write_text('{"source_profile": "internal"}')
    assert resolve_source_profile(config_path=config_path) == "internal"


def test_sync_metadata_config_path_prefers_data_subdir_over_legacy(tmp_path):
    """preferred config가 있으면 legacy config보다 우선해야 한다."""
    from dx_modelzoo.tools.sync_metadata import _resolve_metadata_config_path

    dx_ai_studio_root = tmp_path / "dx-ai-studio"
    preferred = dx_ai_studio_root / "dx_modelzoo" / "data" / "metadata_sync_config.json"
    legacy = dx_ai_studio_root / "metadata_sync_config.json"
    preferred.parent.mkdir(parents=True)
    preferred.write_text('{"source_profile": "internal"}', encoding="utf-8")
    legacy.write_text('{"source_profile": "public"}', encoding="utf-8")

    config_path = _resolve_metadata_config_path(dx_ai_studio_root)

    assert config_path == preferred
    assert resolve_source_profile(config_path=config_path) == "internal"


def test_sync_metadata_config_path_falls_back_to_legacy_when_preferred_absent(tmp_path):
    """preferred config가 없고 legacy config가 있으면 legacy를 사용해야 한다."""
    from dx_modelzoo.tools.sync_metadata import _resolve_metadata_config_path

    dx_ai_studio_root = tmp_path / "dx-ai-studio"
    legacy = dx_ai_studio_root / "metadata_sync_config.json"
    legacy.parent.mkdir(parents=True)
    legacy.write_text('{"source_profile": "public"}', encoding="utf-8")

    config_path = _resolve_metadata_config_path(dx_ai_studio_root)

    assert config_path == legacy
    assert resolve_source_profile(config_path=config_path) == "public"


def test_sync_metadata_config_path_defaults_local_when_configs_absent(tmp_path):
    """config 파일이 모두 없으면 preferred 경로를 반환하고 source는 local로 fallback해야 한다."""
    from dx_modelzoo.tools.sync_metadata import _resolve_metadata_config_path

    dx_ai_studio_root = tmp_path / "dx-ai-studio"
    config_path = _resolve_metadata_config_path(dx_ai_studio_root)

    assert config_path == dx_ai_studio_root / "dx_modelzoo" / "data" / "metadata_sync_config.json"
    assert resolve_source_profile(config_path=config_path) == "local"


def test_internal_adapter_passes_verify_tls_to_fetch(monkeypatch):
    """internal_modelzoo_adapter가 verify_tls 파라미터를 _fetch_url_text에 전달해야 한다."""
    from dx_modelzoo.metadata import adapters

    captured = {}

    def mock_fetch(url, *, verify_tls=True, timeout=30):
        captured["verify_tls"] = verify_tls
        return "<html><body><table></table></body></html>"

    monkeypatch.setattr(adapters, "_fetch_url_text", mock_fetch)
    # fetch_text를 전달하지 않으면 기본 동작으로 _fetch_url_text 사용
    adapters.internal_modelzoo_adapter("fake_root")
    assert captured.get("verify_tls") is True, \
        f"Expected verify_tls=True by default, got {captured.get('verify_tls')}"


def test_internal_adapter_respects_verify_tls_false(monkeypatch):
    """verify_tls=False를 명시적으로 전달하면 _fetch_url_text에 전파되어야 한다."""
    from dx_modelzoo.metadata import adapters

    captured = {}

    def mock_fetch(url, *, verify_tls=True, timeout=30):
        captured["verify_tls"] = verify_tls
        return "<html><body><table></table></body></html>"

    monkeypatch.setattr(adapters, "_fetch_url_text", mock_fetch)
    adapters.internal_modelzoo_adapter("fake_root", verify_tls=False)
    assert captured.get("verify_tls") is False, \
        f"Expected verify_tls=False when explicitly passed, got {captured.get('verify_tls')}"


def test_run_sync_passes_adapter_kwargs_to_internal_adapter(tmp_path):
    """run_sync가 명시적 adapter kwargs를 internal_modelzoo 어댑터에 전달해야 한다."""
    captured = {}

    def empty_adapter(name):
        def _adapter(*args, **kwargs):
            return {"adapter": name, "ok": True, "models": {}, "errors": [], "warnings": []}
        return _adapter

    def internal_adapter(suite_root, *, verify_tls=True):
        captured["suite_root"] = suite_root
        captured["verify_tls"] = verify_tls
        return {"adapter": "internal_modelzoo", "ok": True, "models": {}, "errors": [], "warnings": []}

    run_sync(
        source_profile="internal",
        suite_root=tmp_path,
        output_path=tmp_path / "catalog.json",
        report_path=tmp_path / "report.json",
        adapter_overrides={
            "local_runtime": empty_adapter("local_runtime"),
            "local_modelzoo_repo": empty_adapter("local_modelzoo_repo"),
            "benchmark_cache": empty_adapter("benchmark_cache"),
            "internal_modelzoo": internal_adapter,
        },
        adapter_kwargs={"internal_modelzoo": {"verify_tls": False}},
    )

    assert captured["suite_root"] == tmp_path
    assert captured["verify_tls"] is False


def test_sync_metadata_cli_no_verify_tls_passes_adapter_kwargs(tmp_path, monkeypatch):
    """CLI의 --no-verify-tls 옵션은 internal_modelzoo 어댑터 kwargs로 전달되어야 한다."""
    import sys
    from dx_modelzoo.tools import sync_metadata

    captured = {}

    def fake_run_sync(**kwargs):
        captured["adapter_kwargs"] = kwargs.get("adapter_kwargs")
        return {
            "catalog": {"models": []},
            "report": {"model_count": 0, "adapter_errors": []},
        }

    monkeypatch.setattr(sync_metadata, "_DX_AI_STUDIO_ROOT", tmp_path / "dx-ai-studio")
    monkeypatch.setattr(sync_metadata, "run_sync", fake_run_sync)
    monkeypatch.setattr(
        sys,
        "argv",
        ["sync_metadata.py", "--source", "internal", "--no-verify-tls"],
    )

    sync_metadata.main()

    assert captured["adapter_kwargs"] == {"internal_modelzoo": {"verify_tls": False}}


def test_sync_metadata_cli_no_verify_tls_warns_to_stderr(tmp_path, monkeypatch, capsys):
    """TLS 검증 비활성화 시 운영자가 로그에서 확인할 수 있어야 한다."""
    import sys
    from dx_modelzoo.tools import sync_metadata

    def fake_run_sync(**kwargs):
        return {
            "catalog": {"models": []},
            "report": {"model_count": 0, "adapter_errors": []},
        }

    monkeypatch.setattr(sync_metadata, "_DX_AI_STUDIO_ROOT", tmp_path / "dx-ai-studio")
    monkeypatch.setattr(sync_metadata, "run_sync", fake_run_sync)
    monkeypatch.setattr(
        sys,
        "argv",
        ["sync_metadata.py", "--source", "internal", "--no-verify-tls"],
    )

    sync_metadata.main()

    captured = capsys.readouterr()
    assert "TLS verification disabled" in captured.err

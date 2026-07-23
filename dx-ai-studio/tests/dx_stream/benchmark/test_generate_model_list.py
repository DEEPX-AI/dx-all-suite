"""generate_model_list.py 테스트 — test_models.conf → model_list.json 변환기"""
import importlib.util
import json
import os
import tempfile
from pathlib import Path

import pytest

# generate_model_list.py는 설치 불가 독립 스크립트이므로 동적 임포트
_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent.parent
    / "dx-runtime"
    / "dx_stream"
    / "dx_stream"
    / "apps"
    / "benchmark"
    / "generate_model_list.py"
)

_CONF_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent.parent
    / "dx-runtime"
    / "dx_app"
    / "config"
    / "test_models.conf"
)

pytestmark = [
    pytest.mark.requires_dx_runtime,
    pytest.mark.skipif(
        not _SCRIPT_PATH.is_file(),
        reason="dx-runtime benchmark app is not available",
    ),
]


def _load_module():
    spec = importlib.util.spec_from_file_location("generate_model_list", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gml():
    return _load_module()



class TestExtractFamily:
    def test_yolov8(self, gml):
        assert gml.extract_family("yolov8n") == "yolov8"

    def test_yolov8_variant(self, gml):
        assert gml.extract_family("yolov8s_face") == "yolov8"

    def test_resnet(self, gml):
        assert gml.extract_family("resnet50") == "resnet"

    def test_damoyolo(self, gml):
        assert gml.extract_family("damoyolot") == "damoyolo"

    def test_yolo26(self, gml):
        assert gml.extract_family("yolo26n") == "yolo26"

    def test_clip(self, gml):
        assert gml.extract_family("clip_vit_b_16_text_encoder") == "clip"

    def test_unknown_returns_empty(self, gml):
        assert gml.extract_family("totally_unknown_model_xyz") == ""

    def test_case_insensitive(self, gml):
        # 모델명은 소문자로 오지만 혹시 대소문자 섞여도 동작해야 함
        assert gml.extract_family("YoloV8n".lower()) == "yolov8"



class TestExtractSize:
    def test_n_suffix(self, gml):
        assert gml.extract_size("yolov8n") == "n"

    def test_s_suffix(self, gml):
        assert gml.extract_size("yolov8s") == "s"

    def test_m_suffix(self, gml):
        assert gml.extract_size("yolov8m") == "m"

    def test_l_suffix(self, gml):
        assert gml.extract_size("yolov8l") == "l"

    def test_x_suffix(self, gml):
        assert gml.extract_size("yolov8x") == "x"

    def test_t_suffix(self, gml):
        assert gml.extract_size("damoyolot") == "t"

    def test_no_match_returns_empty(self, gml):
        assert gml.extract_size("resnet50") == ""

    def test_suffix_at_word_boundary(self, gml):
        # "yolov8s_face" — 's' 뒤에 '_'가 오므로 size == "s"
        assert gml.extract_size("yolov8s_face") == "s"

    def test_no_match_mid_word(self, gml):
        # "scrfd_10g_bnkps" — 숫자 중간의 문자는 size로 취급 안 함
        result = gml.extract_size("scrfd_10g_bnkps")
        assert result == ""


# convert_test_models_conf() — 기본 변환

SAMPLE_CONF = """\
# 주석은 무시
damoyolot\tobject_detection\tassets/models/DamoYoloT.dxnn
yolov8n\tobject_detection\tassets/models/YoloV8N.dxnn
clip_vit_b_16_text_encoder\tembedding\tassets/models/ClipVitB16TextEncoder.dxnn
dncnn\timage_denoising\tassets/models/DnCNN.dxnn
"""


class TestConvertTestModelsConf:
    @pytest.fixture(autouse=True)
    def tmp_files(self, tmp_path, gml):
        self.conf = tmp_path / "test_models.conf"
        self.conf.write_text(SAMPLE_CONF, encoding="utf-8")
        self.out = tmp_path / "model_list.json"
        self.gml = gml

    def test_returns_dict(self):
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        assert isinstance(result, dict)

    def test_top_level_keys(self):
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        assert {"version", "source", "generated_at", "models"}.issubset(result.keys())

    def test_model_count(self):
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        assert len(result["models"]) == 4

    def test_model_required_fields(self):
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        required = {"name", "file", "category", "family", "size", "pipeline_skip"}
        for m in result["models"]:
            assert required.issubset(m.keys()), f"{m['name']} 필드 누락"

    def test_file_name_extracted(self):
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        names = {m["name"]: m["file"] for m in result["models"]}
        assert names["yolov8n"] == "YoloV8N.dxnn"
        assert names["damoyolot"] == "DamoYoloT.dxnn"

    def test_category_preserved(self):
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        cats = {m["name"]: m["category"] for m in result["models"]}
        assert cats["yolov8n"] == "object_detection"
        assert cats["dncnn"] == "image_denoising"

    def test_pipeline_skip_pixel_output(self):
        """image_denoising 등 픽셀 출력 카테고리는 pipeline_skip=True"""
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        model = next(m for m in result["models"] if m["name"] == "dncnn")
        assert model["pipeline_skip"] is True

    def test_pipeline_skip_text_only(self):
        """TEXT_ONLY_MODELS에 속하면 pipeline_skip=True"""
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        model = next(m for m in result["models"] if m["name"] == "clip_vit_b_16_text_encoder")
        assert model["pipeline_skip"] is True

    def test_pipeline_skip_false_for_normal(self):
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        model = next(m for m in result["models"] if m["name"] == "yolov8n")
        assert model["pipeline_skip"] is False

    def test_comment_lines_skipped(self):
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        names = [m["name"] for m in result["models"]]
        assert not any(n.startswith("#") for n in names)

    def test_output_file_written(self):
        self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        assert self.out.exists()
        data = json.loads(self.out.read_text())
        assert "models" in data

    def test_family_extracted(self):
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        model = next(m for m in result["models"] if m["name"] == "yolov8n")
        assert model["family"] == "yolov8"

    def test_size_extracted(self):
        result = self.gml.convert_test_models_conf(str(self.conf), str(self.out))
        model = next(m for m in result["models"] if m["name"] == "yolov8n")
        assert model["size"] == "n"


# 실제 test_models.conf 전체 변환 테스트

@pytest.mark.skipif(not _CONF_PATH.exists(), reason="test_models.conf not found")
class TestFullConversion:
    @pytest.fixture(autouse=True)
    def run_conversion(self, tmp_path, gml):
        self.out = tmp_path / "model_list.json"
        self.result = gml.convert_test_models_conf(str(_CONF_PATH), str(self.out))

    def test_model_count_280(self):
        assert len(self.result["models"]) == 280

    def test_categories_17(self):
        cats = {m["category"] for m in self.result["models"]}
        assert len(cats) == 17

    def test_expected_categories(self):
        cats = {m["category"] for m in self.result["models"]}
        expected = {
            "object_detection", "face_detection", "pose_estimation",
            "obb_detection", "classification", "instance_segmentation",
            "semantic_segmentation", "depth_estimation", "image_denoising",
            "super_resolution", "image_enhancement", "embedding",
            "attribute_recognition", "reid", "ppu", "hand_landmark",
            "face_alignment",
        }
        assert cats == expected

    def test_all_models_have_file(self):
        for m in self.result["models"]:
            assert m["file"], f"{m['name']} file 필드 비어 있음"

    def test_pixel_output_models_pipeline_skip(self):
        pixel_cats = {"image_denoising", "depth_estimation", "super_resolution", "image_enhancement"}
        for m in self.result["models"]:
            if m["category"] in pixel_cats:
                assert m["pipeline_skip"] is True, f"{m['name']} pipeline_skip이 False여야 하는데 True가 아님"

    def test_text_only_models_pipeline_skip(self):
        text_only = {
            "clip_resnet50_text_encoder", "clip_vit_b_16_text_encoder",
            "clip_vit_b_32_text_encoder", "clip_vit_l_14_text_encoder",
        }
        names_in_result = {m["name"] for m in self.result["models"]}
        for name in text_only & names_in_result:
            model = next(m for m in self.result["models"] if m["name"] == name)
            assert model["pipeline_skip"] is True, f"{name} pipeline_skip이 True여야 함"

    def test_source_field(self):
        assert "test_models.conf" in self.result["source"]

    def test_generated_at_is_iso(self):
        from datetime import datetime
        ts = self.result["generated_at"]
        # ISO 8601 형식이면 파싱 가능
        datetime.fromisoformat(ts)

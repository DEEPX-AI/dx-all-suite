"""models.py 테스트 — 모델 카탈로그"""
import os, sys, pytest, json, importlib
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


class TestModelCatalog:
    def test_model_has_required_fields(self):
        from core.models import get_models
        required = {"name", "file", "category", "description_ko", "description_en"}
        for m in get_models():
            assert required.issubset(m.keys()), f"Model {m.get('name')} missing fields"

    def test_categories_correct(self):
        from core.models import get_catalog_source, get_models
        cats = {m["category"] for m in get_models()}
        expected = {"object_detection", "face_detection", "pose_estimation", "segmentation", "classification"}
        if get_catalog_source() == "fallback":
            expected.add("obb_detection")
        assert cats == expected

    def test_category_counts(self):
        from core.models import get_catalog_source, get_models
        from collections import Counter
        counts = Counter(m["category"] for m in get_models())
        assert counts["object_detection"] == 8
        assert counts["face_detection"] == 3
        assert counts["pose_estimation"] == 3
        assert counts["segmentation"] == 1
        assert counts["classification"] == 1
        if get_catalog_source() == "manifest":
            assert counts["obb_detection"] == 0
        else:
            assert counts["obb_detection"] == 1

    def test_get_model_status(self, tmp_path):
        from core.models import get_model_status
        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "yolo26-n_640x640.dxnn").write_bytes(b"fake")
        with patch("core.models.MODELS_DIR", models_dir):
            status = get_model_status()
        assert status["yolo26-n_640x640.dxnn"]["installed"] is True

    def test_has_obb_category(self):
        from core.models import get_catalog_source, get_models_by_category
        cats = get_models_by_category()
        if get_catalog_source() == "manifest":
            assert "obb_detection" not in cats
        else:
            assert "obb_detection" in cats
            assert len(cats["obb_detection"]) >= 1

    def test_obb_model_entry(self):
        from core.models import get_catalog_source, get_models
        obb = [m for m in get_models() if m["category"] == "obb_detection"]
        if get_catalog_source() == "manifest":
            assert obb == []
        else:
            assert len(obb) >= 1
            assert obb[0]["file"] == "yolo26n-obb.dxnn"

    def test_total_model_count(self):
        from core.models import get_catalog_source, get_models
        assert len(get_models()) == (16 if get_catalog_source() == "manifest" else 17)


DEV_MODELS = [
    "EfficientNet_Lite0.dxnn", "SCRFD500M.dxnn", "YoloV5S_PPU.dxnn",
    "YOLOv5s_Face.dxnn", "yolo26n.dxnn", "yolo26n-pose.dxnn",
    "yolo26n-seg.dxnn", "YoloV5S.dxnn", "YoloV7.dxnn",
    "YoloV8N.dxnn", "YoloV9S.dxnn", "YoloXS.dxnn",
    "YOLOV11N.dxnn", "yolov8m_pose.dxnn", "SCRFD500M_PPU.dxnn",
    "YOLOV5Pose_PPU.dxnn",
]


def _reload_models_with_manifest(monkeypatch, tmp_path, request):
    orig = os.environ.get("DX_STREAM_ROOT")

    root = tmp_path / "runtime"
    root.mkdir()
    (root / "model_list.json").write_text(json.dumps({"version": "2_3_0", "models": DEV_MODELS}), encoding="utf-8")
    monkeypatch.setenv("DX_STREAM_ROOT", str(root))
    import core.config as config
    import core.runtime as runtime
    import core.models as models
    importlib.reload(config)
    importlib.reload(runtime)

    def _restore_modules():
        if orig is None:
            os.environ.pop("DX_STREAM_ROOT", None)
        else:
            os.environ["DX_STREAM_ROOT"] = orig
        import core.config as _cfg
        import core.runtime as _rt
        import core.models as _mdl
        importlib.reload(_cfg)
        importlib.reload(_rt)
        importlib.reload(_mdl)

    request.addfinalizer(_restore_modules)
    return importlib.reload(models)


def test_manifest_catalog_uses_runtime_models(monkeypatch, tmp_path, request):
    models = _reload_models_with_manifest(monkeypatch, tmp_path, request)

    files = [m["file"] for m in models.get_models()]

    # manifest 모드에서는 OBB 등 manifest에 없는 항목이 제외된다
    assert len(files) == 16
    assert "EfficientNet_Lite0.dxnn" in files
    assert "yolo26n-obb.dxnn" not in files
    assert models.get_catalog_source() == "manifest"

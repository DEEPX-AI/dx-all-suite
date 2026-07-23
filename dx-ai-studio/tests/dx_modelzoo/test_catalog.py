"""catalog.py 카탈로그 로드/필터 테스트"""
import sys, json, pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_modelzoo"))

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELZOO_DATA_DIR = PROJECT_ROOT / "dx_modelzoo" / "data"

# The dx-runtime staging catalog dropped the `_h` brand suffix from these model ids
# (e.g. yolov5l_h -> yolov5l) and renamed their dxnn files to the clean upstream naming.
# Three 6.1-variant P6 models (yolov5{m,n,s}6_61_h) were removed from staging entirely.
RELEASE_RENAMED_H_MODELS = {
    "yolov5l": "yolov5-l_640x640.dxnn",
    "yolov5m": "yolov5-m_640x640.dxnn",
    "yolov5s": "yolov5-s_640x640.dxnn",
    "regnetx1_6gf": "regnet-x1.6gf_224x224_v1.dxnn",
    "resnext50_32x4d": "resnext50-32x4d_224x224.dxnn",
    "segformer_b0_512x1024": "segformer_mit-b0_512x1024.dxnn",
}


def _catalog_models(path):
    return {
        model["id"]: model
        for model in json.loads(path.read_text(encoding="utf-8")).get("models", [])
    }


def _string_values(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from _string_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _string_values(nested)
    elif isinstance(value, str):
        yield value


@pytest.fixture
def sample_conf(tmp_path):
    """test_models.conf 샘플 생성"""
    conf = tmp_path / "test_models.conf"
    conf.write_text(
        "# comment\n"
        "yolov8n\tobject_detection\tassets/models/yolov8n.dxnn\n"
        "resnet50\tclassification\tassets/models/resnet50.dxnn\n"
        "scrfd_500m\tface_detection\tassets/models/scrfd_500m.dxnn\n"
    )
    return conf


@pytest.fixture
def sample_catalog(tmp_path):
    """model_catalog.json 샘플 생성"""
    catalog = tmp_path / "model_catalog.json"
    catalog.write_text(json.dumps({
        "version": "1.0",
        "categories": {},
        "models": [
            {
                "id": "yolov8n", "name": "YOLOv8n", "category": "object_detection",
                "description": {"en": "Fast detector", "ko": "빠른 탐지기"},
                "specification": {"fps": "1200", "input_resolution": "640x640"},
                "model_file": "assets/models/yolov8n.dxnn",
            },
            {
                "id": "resnet50", "name": "ResNet50", "category": "classification",
                "description": {"en": "Image classifier", "ko": "이미지 분류기"},
                "specification": {"fps": "800", "input_resolution": "224x224"},
                "model_file": "assets/models/resnet50.dxnn",
            },
        ]
    }))
    return catalog


class TestCatalogLoad:
    def test_parse_conf_returns_models(self, sample_conf):
        from core.catalog import parse_test_models_conf
        models = parse_test_models_conf(sample_conf)
        assert len(models) == 3
        assert models[0]["id"] == "yolov8n"
        assert models[0]["category"] == "object_detection"
        assert models[0]["model_file"] == "assets/models/yolov8n.dxnn"

    def test_parse_conf_skips_comments(self, sample_conf):
        from core.catalog import parse_test_models_conf
        models = parse_test_models_conf(sample_conf)
        ids = [m["id"] for m in models]
        assert "#" not in str(ids)

    def test_parse_conf_missing_file(self, tmp_path):
        from core.catalog import parse_test_models_conf
        models = parse_test_models_conf(tmp_path / "nonexistent.conf")
        assert models == []

    def test_load_catalog_json(self, sample_catalog):
        from core.catalog import load_catalog_json
        data = load_catalog_json(sample_catalog)
        assert len(data["models"]) == 2
        assert data["models"][0]["id"] == "yolov8n"

    def test_load_catalog_json_missing(self, tmp_path):
        from core.catalog import load_catalog_json
        data = load_catalog_json(tmp_path / "nope.json")
        assert data == {"version": "1.0", "categories": {}, "models": []}

    def test_release_renamed_h_models_use_current_ids_and_model_files(self):
        models = _catalog_models(MODELZOO_DATA_DIR / "model_catalog.json")

        for model_id, filename in RELEASE_RENAMED_H_MODELS.items():
            assert f"{model_id}ailo" not in models
            assert model_id in models
            model = models[model_id]
            assert model["class_name"] == model_id
            assert model["model_file"] == f"assets/models/{filename}"

    def test_release_catalog_does_not_expose_renamed_model_brand(self):
        models = _catalog_models(MODELZOO_DATA_DIR / "model_catalog.json")

        for model_id in RELEASE_RENAMED_H_MODELS:
            model = models[model_id]
            values = "\n".join(_string_values(model))
            assert "hailo" not in values.lower()

    def test_release_catalog_does_not_expose_brand_in_any_public_model(self):
        models = _catalog_models(MODELZOO_DATA_DIR / "model_catalog.json")

        for model in models.values():
            values = "\n".join(_string_values(model))
            assert "hailo" not in values.lower(), model["id"]

    def test_generated_catalog_does_not_expose_renamed_model_brand(self):
        path = MODELZOO_DATA_DIR / "generated_catalog.json"
        if not path.is_file():
            pytest.skip(
                "generated_catalog.json missing — run: "
                "python3 dx_modelzoo/tools/sync_metadata.py --offline"
            )
        models = _catalog_models(path)

        for model_id in RELEASE_RENAMED_H_MODELS:
            model = models[model_id]
            values = "\n".join(_string_values(model))
            assert "hailo" not in values.lower()


class TestCatalogFilter:
    def test_filter_by_category(self, sample_catalog):
        from core.catalog import load_catalog_json, filter_models
        data = load_catalog_json(sample_catalog)
        result = filter_models(data["models"], category="object_detection")
        assert len(result) == 1
        assert result[0]["id"] == "yolov8n"

    def test_filter_by_search(self, sample_catalog):
        from core.catalog import load_catalog_json, filter_models
        data = load_catalog_json(sample_catalog)
        result = filter_models(data["models"], search="resnet")
        assert len(result) == 1
        assert result[0]["id"] == "resnet50"

    def test_filter_no_match(self, sample_catalog):
        from core.catalog import load_catalog_json, filter_models
        data = load_catalog_json(sample_catalog)
        result = filter_models(data["models"], search="nonexistent_xyz")
        assert len(result) == 0

    def test_get_model_by_id(self, sample_catalog):
        from core.catalog import load_catalog_json, get_model
        data = load_catalog_json(sample_catalog)
        model = get_model(data["models"], "yolov8n")
        assert model is not None
        assert model["name"] == "YOLOv8n"

    def test_get_model_not_found(self, sample_catalog):
        from core.catalog import load_catalog_json, get_model
        data = load_catalog_json(sample_catalog)
        assert get_model(data["models"], "nonexistent") is None

    def test_count_by_category(self, sample_catalog):
        from core.catalog import load_catalog_json, count_by_category
        data = load_catalog_json(sample_catalog)
        counts = count_by_category(data["models"])
        assert counts["object_detection"] == 1
        assert counts["classification"] == 1


class TestCatalogMerge:
    def test_merge_enriches_conf_with_catalog(self, sample_conf, sample_catalog):
        from core.catalog import parse_test_models_conf, load_catalog_json, merge_conf_and_catalog
        conf = parse_test_models_conf(sample_conf)
        cat = load_catalog_json(sample_catalog)
        merged = merge_conf_and_catalog(conf, cat)
        yolo = [m for m in merged if m["id"] == "yolov8n"][0]
        assert yolo["name"] == "YOLOv8n"
        assert yolo["description"]["en"] == "Fast detector"

    def test_merge_conf_only_model_gets_defaults(self, sample_conf, sample_catalog):
        from core.catalog import parse_test_models_conf, load_catalog_json, merge_conf_and_catalog
        conf = parse_test_models_conf(sample_conf)
        cat = load_catalog_json(sample_catalog)
        merged = merge_conf_and_catalog(conf, cat)
        scrfd = [m for m in merged if m["id"] == "scrfd_500m"][0]
        assert scrfd["description"] == {"en": "", "ko": ""}

    def test_merge_preserves_all_conf_models(self, sample_conf, sample_catalog):
        from core.catalog import parse_test_models_conf, load_catalog_json, merge_conf_and_catalog
        conf = parse_test_models_conf(sample_conf)
        cat = load_catalog_json(sample_catalog)
        merged = merge_conf_and_catalog(conf, cat)
        assert len(merged) == 3


class TestCatalogQueryPagination:
    def test_sort_models_by_numeric_fps_missing_values_as_zero(self):
        from core.catalog import sort_models
        models = [
            {"id": "slow", "name": "Slow", "category": "classification", "specification": {"fps": "12.5"}},
            {"id": "missing", "name": "Missing", "category": "classification", "specification": {}},
            {"id": "fast", "name": "Fast", "category": "classification", "specification": {"fps": "120"}},
        ]
        result = sort_models(models, sort="fps", direction="desc")
        assert [m["id"] for m in result] == ["fast", "slow", "missing"]

    def test_paginate_models_clamps_page_and_page_size(self):
        from core.catalog import paginate_models
        models = [{"id": str(i)} for i in range(5)]
        page = paginate_models(models, page=-10, page_size=999)
        assert page["page"] == 1
        assert page["page_size"] == 200
        assert page["total"] == 5
        assert page["pages"] == 1
        assert page["has_next"] is False
        assert page["has_prev"] is False

    def test_paginate_empty_model_list(self):
        from core.catalog import paginate_models
        result = paginate_models([], page=1, page_size=10)
        assert result == {
            "models": [],
            "total": 0,
            "page": 1,
            "page_size": 10,
            "pages": 1,
            "has_next": False,
            "has_prev": False,
        }

    def test_query_catalog_filters_search_category_and_sorts(self):
        from core.catalog import query_catalog
        models = [
            {"id": "a", "name": "Alpha", "class_name": "AlphaNet", "category": "classification", "specification": {"fps": "10"}},
            {"id": "b", "name": "Beta", "class_name": "BetaDet", "category": "object_detection", "specification": {"fps": "50"}},
            {"id": "c", "name": "Gamma", "class_name": "GammaDet", "category": "object_detection", "specification": {"fps": "30"}},
        ]
        result = query_catalog(models, category="object_detection", search="det", sort="fps", direction="desc", page=1, page_size=1)
        assert result["total"] == 2
        assert result["pages"] == 2
        assert [m["id"] for m in result["models"]] == ["b"]
        assert result["has_next"] is True

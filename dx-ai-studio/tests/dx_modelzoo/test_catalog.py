"""catalog.py load/filter tests"""
import sys, json, pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_modelzoo"))

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELZOO_DATA_DIR = PROJECT_ROOT / "dx_modelzoo" / "data"

# In the dx-runtime staging catalog these model ids carry no `_h` brand suffix
# (e.g. yolov5l_h -> yolov5l) and their dxnn files use the upstream naming.
# The 6.1-variant P6 models (yolov5{m,n,s}6_61_h) are not in staging at all.
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
    """Write a sample test_models.conf"""
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
    """Write a sample model_catalog.json"""
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


def test_a_v9_only_model_says_which_dx_rt_it_needs(monkeypatch):
    """A model only in Model Zoo 2_5_0 is container v9: it downloads but does not run on DX-RT 3.4.2,
    so it must say which DX-RT it needs."""
    from dx_modelzoo.core.catalog import _enrich_model_entry
    from shared import dxrt

    new = {"artifacts": {"qlite_dxnn": {"remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/patchcore_224x224.dxnn"}}}
    old = {"artifacts": {"qlite_dxnn": {"remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_4_0/yolo26-n_640x640.dxnn"}}}
    monkeypatch.setattr(dxrt, "runtime_version", lambda: (3, 4, 2))
    assert _enrich_model_entry({}, new)["requires_dxrt"] == "3.5.0"
    assert "requires_dxrt" not in _enrich_model_entry({}, old)
    monkeypatch.setattr(dxrt, "runtime_version", lambda: (3, 5, 0))
    assert "requires_dxrt" not in _enrich_model_entry({}, new)


def test_models_only_on_the_publish_page_are_listed(monkeypatch):
    """A model missing from the curated catalog (only on the publish page / generated catalog) must still be
    listed, not only used to enrich other entries."""
    from dx_modelzoo.core import catalog
    from shared import dxrt

    monkeypatch.setattr(dxrt, "runtime_version", lambda: (3, 4, 2))
    monkeypatch.setattr(catalog, "load_generated_catalog", lambda: {"schema_version": "2.0", "models": [
        # Must be a model that no dx_app conf lists (the per-model conf already has patchcore)
        {"id": "brandnew_224x224", "display": {"name": "Brand New", "task": "anomaly_detection"},
         "artifacts": {"qlite_dxnn": {"remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/brandnew_224x224.dxnn"}},
         "legal": {"source_url": "No Reference"}},
        {"id": "mystery_x", "display": {"name": "X", "task": "Not A Task"}}]})
    try:
        models = {m["id"]: m for m in catalog.reload_catalog()["models"]}
    finally:
        monkeypatch.undo()
        catalog.reload_catalog()   # do not leave the fake catalog in the cache for later tests
    pc = models["brandnew_224x224"]
    assert pc["category"] == "anomaly_detection" and pc["publish_only"] is True
    assert pc["model_file"] == "assets/models/brandnew_224x224.dxnn"
    assert pc["requires_dxrt"] == "3.5.0"
    assert pc["legal"]["source_url"] == "", "page 의 'No Reference' 를 출처처럼 두지 않는다"
    assert "mystery_x" not in models, "모르는 task 는 목록에 넣지 않는다"


def test_a_per_model_test_models_conf_lists_each_model_once(tmp_path, monkeypatch):
    """The per-model dx_app test_models.conf is family<TAB>task<TAB>model_file<TAB>variant. Reading column 1
    (family) as the id lists efficientad three times and yolo26_depth five times. The variant (the .dxnn name) is
    the model; Model Zoo keeps the existing id for the same file (yolo26n) and the older task key."""
    from dx_modelzoo.core import catalog
    from shared.catalog_sources import parse_test_models_conf

    conf = tmp_path / "test_models.conf"
    conf.write_text("# Format: family<TAB>task<TAB>model_file<TAB>variant\n"
                    "yolo26\tobject_detection\tassets/models/yolo26-n_640x640.dxnn\tyolo26-n_640x640\n"
                    "efficientad\tanomaly_detection\tassets/models/efficientad-m-student_256x256.dxnn\tefficientad-m-student_256x256\n"
                    "efficientad\tanomaly_detection\tassets/models/efficientad-m-teacher_256x256.dxnn\tefficientad-m-teacher_256x256\n"
                    "resnet\timage_classification\tassets/models/resnet50_224x224.dxnn\tresnet50_224x224\n")
    rows = parse_test_models_conf(conf)
    assert [r["id"] for r in rows] == ["yolo26-n_640x640", "efficientad-m-student_256x256",
                                       "efficientad-m-teacher_256x256", "resnet50_224x224"]
    assert rows[1]["family"] == "efficientad"

    gen = {"schema_version": "2.0", "models": [
        {"id": "yolo26n", "display": {"task": "object_detection"},
         "artifacts": {"qlite_dxnn": {"remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/yolo26-n_640x640.dxnn"}}},
        {"id": "efficientad_m_student_256x256", "display": {"task": "anomaly_detection"},
         "artifacts": {"qlite_dxnn": {"remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/efficientad-m-student_256x256.dxnn"}}}]}
    ids = catalog.conf_ids_from_generated(rows, gen)
    assert [r["id"] for r in ids] == ["yolo26n", "efficientad_m_student_256x256",
                                      "efficientad-m-teacher_256x256", "resnet50_224x224"]
    assert ids[3]["category"] == "classification", "Model Zoo 는 짝이 있는 task 를 옛 key 로 묶는다"


def test_a_legacy_row_outside_the_curated_catalog_takes_the_id_of_its_file():
    """A 3-column row (yolo26_depth_n) and the per-model dx_app entry for the same model must share an id, or
    the images are not found. Curated catalog ids stay as they are (like DeiT, they carry their own data)."""
    from dx_modelzoo.core import catalog

    gen = {"models": [{"id": "yolo26_depth_n_768x768", "artifacts": {"qlite_dxnn": {
        "remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/yolo26-depth-n_768x768.dxnn"}}},
        {"id": "deitbase384", "artifacts": {"qlite_dxnn": {
            "remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/deit-b_384x384.dxnn"}}}]}
    rows = [{"id": "yolo26_depth_n", "name": "yolo26_depth_n", "category": "depth_estimation",
             "model_file": "assets/models/yolo26-depth-n_768x768.dxnn"},
            {"id": "deit_base384_distilled", "name": "deit_base384_distilled", "category": "classification",
             "model_file": "assets/models/deit-b_384x384.dxnn"}]
    out = catalog.conf_ids_from_generated(rows, gen, curated_ids=["deit_base384_distilled"])
    assert [r["id"] for r in out] == ["yolo26_depth_n_768x768", "deit_base384_distilled"]


def test_a_per_model_row_takes_the_task_of_its_example_dir(tmp_path, monkeypatch):
    """The per-model dx_app test_models.conf files repvgg-a0-reid under image_classification, but its example is in
    person_reid/ (the registry agrees) and its runner takes one query plus a gallery. Following the conf would run
    classification on a dog photo, so the task of the example folder, which decides how it runs, wins."""
    import json
    from dx_modelzoo.core import catalog
    from shared import dx_app_layout as layout

    root = tmp_path / "dx_app"
    ex = root / "src/python_example/person_reid/repvgg_reid/repvgg-a0-reid_256x128"
    ex.mkdir(parents=True)
    (ex / "repvgg-a0-reid_256x128_sync.py").write_text("")
    (ex / "config.json").write_text(json.dumps({"variant": "repvgg-a0-reid_256x128", "task": "person_reid"}))
    (root / "src/python_example/common/runner").mkdir(parents=True)
    conf = root / "config/test_models.conf"
    conf.parent.mkdir(parents=True)
    conf.write_text("repvgg_reid\timage_classification\tassets/models/repvgg-a0-reid_256x128.dxnn\trepvgg-a0-reid_256x128\n"
                    "casvit\timage_classification\tassets/models/casvit-t_224x224.dxnn\tcasvit-t_224x224\n")
    monkeypatch.setattr(catalog, "DX_APP_ROOT", root)
    monkeypatch.setattr(catalog, "CONFIG_FILE", conf)
    layout.clear_cache()
    try:
        rows = {r["id"]: r for r in catalog.parse_test_models_conf()}
    finally:
        layout.clear_cache()
    assert rows["repvgg-a0-reid_256x128"]["category"] == "person_reid"
    assert rows["casvit-t_224x224"]["category"] == "image_classification", "예제가 없으면 conf 그대로"


def test_a_registry_alias_row_does_not_list_its_model_twice(tmp_path):
    """The per-model dx_app registry has alias entries (deit_base384_distilled → deit_base_distilled_2, the same
    variant). The script that writes test_models.conf keeps aliases, so one variant can appear on two rows; the
    model must still be listed once. One row per variant."""
    from shared.catalog_sources import parse_test_models_conf
    conf = tmp_path / "test_models.conf"
    conf.write_text(
        "deit\timage_classification\tassets/models/deit-b_384x384.dxnn\tdeit-b_384x384\n"
        "deit\timage_classification\tassets/models/deit-b_384x384_distilled.dxnn\tdeit-b_384x384_distilled\n"
        "deit\timage_classification\tassets/models/deit-b_384x384_distilled.dxnn\tdeit-b_384x384_distilled\n")
    rows = parse_test_models_conf(conf)
    assert [r["id"] for r in rows] == ["deit-b_384x384", "deit-b_384x384_distilled"]


def test_the_real_catalog_has_no_duplicate_ids():
    import collections
    from dx_modelzoo.core import catalog
    ids = collections.Counter(m["id"] for m in catalog.get_catalog()["models"])
    dups = [k for k, v in ids.items() if v > 1]
    assert not dups, dups

"""Tests for model_catalog.py — V2 JSON manifest based discover_models."""

import json
from pathlib import Path

import pytest

BENCHMARK_DIR = Path(__file__).resolve().parents[4] / "dx-runtime" / "dx_stream" / "dx_stream" / "apps" / "benchmark"
# Guard on the actual source file, not the directory: a stale __pycache__ leftover
# can keep the dir present after staging dx_stream removed the benchmark app.
_BENCHMARK_APP = BENCHMARK_DIR / "model_catalog.py"
pytestmark = [
    pytest.mark.requires_dx_runtime,
    pytest.mark.skipif(
        not _BENCHMARK_APP.is_file(),
        reason="dx-runtime benchmark app is not available",
    ),
]

if _BENCHMARK_APP.is_file():
    from benchmark.model_catalog import (
        ModelEntry,
        discover_models,
        filter_models,
        ModelEntryV2,
        discover_models_v2,
        filter_models_v2,
    )



@pytest.fixture
def manifest_dir(tmp_path):
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    for name in ["YoloV8N.dxnn", "ResNet50.dxnn", "DnCNN_25.dxnn", "yolo26n.dxnn"]:
        (model_dir / name).touch()
    manifest = {
        "version": "2_3_0",
        "models": [
            {
                "name": "yolov8n",
                "file": "YoloV8N.dxnn",
                "category": "object_detection",
                "family": "yolov8",
                "size": "n",
                "pipeline_skip": False,
            },
            {
                "name": "resnet50",
                "file": "ResNet50.dxnn",
                "category": "classification",
                "family": "resnet",
                "size": "",
                "pipeline_skip": False,
            },
            {
                "name": "dncnn_25",
                "file": "DnCNN_25.dxnn",
                "category": "image_denoising",
                "family": "dncnn",
                "size": "",
                "pipeline_skip": True,
            },
            {
                "name": "yolo26n",
                "file": "yolo26n.dxnn",
                "category": "object_detection",
                "family": "yolo26",
                "size": "n",
                "pipeline_skip": False,
            },
            {
                "name": "missing_model",
                "file": "NotExist.dxnn",
                "category": "classification",
                "family": "unknown",
                "size": "",
                "pipeline_skip": False,
            },
        ],
    }
    (tmp_path / "model_list.json").write_text(json.dumps(manifest))
    return model_dir, tmp_path / "model_list.json"



class TestDiscoverModelsV2:
    def test_returns_four_entries_skipping_missing(self, manifest_dir):
        model_dir, manifest_path = manifest_dir
        entries = discover_models_v2(model_dir, manifest_path)
        assert len(entries) == 4

    def test_model_entry_fields(self, manifest_dir):
        model_dir, manifest_path = manifest_dir
        entries = discover_models_v2(model_dir, manifest_path)
        by_name = {e.name: e for e in entries}

        e = by_name["yolov8n"]
        assert e.task == "object_detection"
        assert e.task_suffix == "od"
        assert e.size == "n"
        assert e.family == "yolov8"
        assert e.path == model_dir / "YoloV8N.dxnn"

    def test_pipeline_skip_flag(self, manifest_dir):
        model_dir, manifest_path = manifest_dir
        entries = discover_models_v2(model_dir, manifest_path)
        by_name = {e.name: e for e in entries}

        assert by_name["dncnn_25"].pipeline_skip is True
        assert by_name["yolov8n"].pipeline_skip is False

    def test_sorted_by_task_family_size(self, manifest_dir):
        model_dir, manifest_path = manifest_dir
        entries = discover_models_v2(model_dir, manifest_path)
        keys = [(e.task, e.family, e.size) for e in entries]
        assert keys == sorted(keys)

    def test_missing_file_skipped(self, manifest_dir):
        model_dir, manifest_path = manifest_dir
        entries = discover_models_v2(model_dir, manifest_path)
        names = [e.name for e in entries]
        assert "missing_model" not in names

    def test_preprocess_override_and_postprocess_lib_defaults_none(self, manifest_dir):
        model_dir, manifest_path = manifest_dir
        entries = discover_models_v2(model_dir, manifest_path)
        for e in entries:
            assert e.preprocess_override is None
            assert e.postprocess_lib is None

    def test_str_representation(self, manifest_dir):
        model_dir, manifest_path = manifest_dir
        entries = discover_models_v2(model_dir, manifest_path)
        s = str(entries[0])
        assert "task=" in s
        assert "family=" in s
        assert "size=" in s



class TestFilterModelsV2:
    @pytest.fixture
    def entries(self, manifest_dir):
        model_dir, manifest_path = manifest_dir
        return discover_models_v2(model_dir, manifest_path)

    def test_filter_by_category(self, entries):
        result = filter_models_v2(entries, category="object_detection")
        assert all(e.task == "object_detection" for e in result)
        assert len(result) == 2

    def test_filter_by_family(self, entries):
        result = filter_models_v2(entries, model_family="resnet")
        assert len(result) == 1
        assert result[0].name == "resnet50"

    def test_filter_by_size(self, entries):
        result = filter_models_v2(entries, size="n")
        assert all(e.size == "n" for e in result)
        assert len(result) == 2

    def test_filter_by_name_glob(self, entries):
        result = filter_models_v2(entries, name_filter="yolo*")
        assert all(e.name.startswith("yolo") for e in result)

    def test_no_filter_returns_all(self, entries):
        result = filter_models_v2(entries)
        assert len(result) == 4

    def test_comma_separated_categories(self, entries):
        result = filter_models_v2(entries, category="object_detection,classification")
        tasks = {e.task for e in result}
        assert tasks == {"object_detection", "classification"}
        assert len(result) == 3

    def test_combined_filters(self, entries):
        result = filter_models_v2(entries, category="object_detection", size="n")
        assert len(result) == 2
        assert all(e.task == "object_detection" and e.size == "n" for e in result)



class TestBackwardCompat:
    def test_model_entry_exists(self):
        assert ModelEntry is not None

    def test_discover_models_callable(self):
        assert callable(discover_models)

    def test_filter_models_callable(self):
        assert callable(filter_models)

    def test_model_entry_fields_unchanged(self):
        from pathlib import Path
        e = ModelEntry(
            name="yolo26n.dxnn",
            path=Path("/tmp/yolo26n.dxnn"),
            task="object_detection",
            task_suffix="od",
            size="n",
        )
        assert e.name == "yolo26n.dxnn"
        assert e.task == "object_detection"
        assert e.task_suffix == "od"
        assert e.size == "n"



class TestLegacyStringManifest:
    """discover_models_v2 handles legacy manifests where models is a string list."""

    @pytest.fixture
    def legacy_manifest_dir(self, tmp_path):
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        for name in ["yolo26n.dxnn", "yolo26s-pose.dxnn", "yolo26m-seg.dxnn"]:
            (model_dir / name).touch()
        manifest = {
            "version": "2_3_0",
            "models": [
                "yolo26n.dxnn",
                "yolo26s-pose.dxnn",
                "yolo26m-seg.dxnn",
                "yolo26x.dxnn",  # file does not exist → skipped
            ],
        }
        (tmp_path / "model_list.json").write_text(json.dumps(manifest))
        return model_dir, tmp_path / "model_list.json"

    def test_discovers_existing_string_entries(self, legacy_manifest_dir):
        model_dir, manifest_path = legacy_manifest_dir
        entries = discover_models_v2(model_dir, manifest_path)
        assert len(entries) == 3

    def test_string_entry_fields(self, legacy_manifest_dir):
        model_dir, manifest_path = legacy_manifest_dir
        entries = discover_models_v2(model_dir, manifest_path)
        by_name = {e.name: e for e in entries}

        e = by_name["yolo26n.dxnn"]
        assert e.task == "object_detection"
        assert e.task_suffix == "od"
        assert e.size == "n"
        assert e.family == "yolo26"

        e = by_name["yolo26s-pose.dxnn"]
        assert e.task == "pose_estimation"
        assert e.task_suffix == "pose"
        assert e.size == "s"

    def test_missing_string_file_skipped(self, legacy_manifest_dir):
        model_dir, manifest_path = legacy_manifest_dir
        entries = discover_models_v2(model_dir, manifest_path)
        names = [e.name for e in entries]
        assert "yolo26x.dxnn" not in names

    def test_unrecognised_string_skipped(self, tmp_path):
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        (model_dir / "unknown_model.dxnn").touch()
        manifest = {"models": ["unknown_model.dxnn"]}
        manifest_path = tmp_path / "model_list.json"
        manifest_path.write_text(json.dumps(manifest))

        entries = discover_models_v2(model_dir, manifest_path)
        assert len(entries) == 0



class TestMalformedDictEntries:
    """discover_models_v2 skips malformed dict entries without crashing."""

    def test_missing_file_key_skipped(self, tmp_path):
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        (model_dir / "good.dxnn").touch()
        manifest = {
            "models": [
                {"name": "good", "file": "good.dxnn", "category": "object_detection"},
                {"name": "bad", "category": "classification"},  # missing 'file'
            ],
        }
        (tmp_path / "model_list.json").write_text(json.dumps(manifest))
        entries = discover_models_v2(model_dir, tmp_path / "model_list.json")
        assert len(entries) == 1
        assert entries[0].name == "good"

    def test_missing_category_key_skipped(self, tmp_path):
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        (model_dir / "m.dxnn").touch()
        manifest = {
            "models": [
                {"name": "m", "file": "m.dxnn"},  # missing 'category'
            ],
        }
        (tmp_path / "model_list.json").write_text(json.dumps(manifest))
        entries = discover_models_v2(model_dir, tmp_path / "model_list.json")
        assert len(entries) == 0

    def test_missing_name_key_skipped(self, tmp_path):
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        (model_dir / "m.dxnn").touch()
        manifest = {
            "models": [
                {"file": "m.dxnn", "category": "classification"},  # missing 'name'
            ],
        }
        (tmp_path / "model_list.json").write_text(json.dumps(manifest))
        entries = discover_models_v2(model_dir, tmp_path / "model_list.json")
        assert len(entries) == 0

    def test_non_dict_non_string_skipped(self, tmp_path):
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        manifest = {"models": [42, None, True]}
        (tmp_path / "model_list.json").write_text(json.dumps(manifest))
        entries = discover_models_v2(model_dir, tmp_path / "model_list.json")
        assert len(entries) == 0

    def test_models_key_is_null(self, tmp_path):
        """{"models": null} must return [] instead of crashing with TypeError."""
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        manifest = {"models": None}
        (tmp_path / "model_list.json").write_text(json.dumps(manifest))
        entries = discover_models_v2(model_dir, tmp_path / "model_list.json")
        assert entries == []

    def test_mixed_valid_and_malformed(self, tmp_path):
        model_dir = tmp_path / "models"
        model_dir.mkdir()
        (model_dir / "yolo26n.dxnn").touch()
        (model_dir / "Good.dxnn").touch()
        manifest = {
            "models": [
                "yolo26n.dxnn",  # valid string
                {"name": "g", "file": "Good.dxnn", "category": "classification"},  # valid dict
                {"name": "bad"},  # malformed dict
                42,  # invalid type
            ],
        }
        (tmp_path / "model_list.json").write_text(json.dumps(manifest))
        entries = discover_models_v2(model_dir, tmp_path / "model_list.json")
        assert len(entries) == 2

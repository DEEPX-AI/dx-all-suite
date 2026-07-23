"""Tests for V2 17-category expansion in benchmark/config.py."""

from pathlib import Path

import pytest

BENCHMARK_DIR = Path(__file__).resolve().parents[4] / "dx-runtime" / "dx_stream" / "dx_stream" / "apps" / "benchmark"
# Guard on the actual source file, not the directory: a stale __pycache__ leftover
# can keep the dir present after staging dx_stream removed the benchmark app.
_BENCHMARK_APP = BENCHMARK_DIR / "config.py"
pytestmark = [
    pytest.mark.requires_dx_runtime,
    pytest.mark.skipif(
        not _BENCHMARK_APP.is_file(),
        reason="dx-runtime benchmark app is not available",
    ),
]

if _BENCHMARK_APP.is_file():
    from benchmark.config import (
        CATEGORY_TO_SUFFIX,
        TASK_PREPROCESS,
        E2E_SUPPORTED_TASKS_V2,
        MULTI_STREAM_SUPPORTED_TASKS_V2,
        CATEGORY_VIDEO,
        FAMILY_POSTPROCESS_MAP,
        resolve_postprocess_lib,
        get_postprocess_config_path_v2,
        get_task_preprocess_v2,
        TASK_MAP,
        E2E_SUPPORTED_TASKS,
        MULTI_STREAM_SUPPORTED_TASKS,
        POSTPROCESS_LIB_DIR,
    )


class TestCategoryToSuffix:
    def test_17_categories_present(self):
        assert len(CATEGORY_TO_SUFFIX) == 17

    def test_all_categories_present(self):
        expected = {
            "object_detection", "face_detection", "pose_estimation",
            "instance_segmentation", "semantic_segmentation", "obb_detection",
            "classification", "embedding", "reid", "ppu",
            "attribute_recognition", "hand_landmark", "face_alignment",
            "image_denoising", "depth_estimation", "super_resolution",
            "image_enhancement",
        }
        assert set(CATEGORY_TO_SUFFIX.keys()) == expected

    def test_backward_compat_suffixes(self):
        assert CATEGORY_TO_SUFFIX["object_detection"] == "od"
        assert CATEGORY_TO_SUFFIX["pose_estimation"] == "pose"
        assert CATEGORY_TO_SUFFIX["classification"] == "cls"
        assert CATEGORY_TO_SUFFIX["obb_detection"] == "obb"

    def test_seg_semseg_distinction(self):
        assert CATEGORY_TO_SUFFIX["instance_segmentation"] == "seg"
        assert CATEGORY_TO_SUFFIX["semantic_segmentation"] == "semseg"


class TestTaskPreprocess:
    def test_13_entries(self):
        assert len(TASK_PREPROCESS) == 13

    def test_od_params(self):
        od = TASK_PREPROCESS["od"]
        assert od["resize_width"] == 640
        assert od["resize_height"] == 640
        assert od["pad_value"] == 114
        assert od["keep_ratio"] is True

    def test_cls_params(self):
        cls = TASK_PREPROCESS["cls"]
        assert cls["resize_width"] == 224
        assert cls["resize_height"] == 224
        assert cls["pad_value"] == 0
        assert cls["keep_ratio"] is False

    def test_obb_params(self):
        obb = TASK_PREPROCESS["obb"]
        assert obb["resize_width"] == 1024
        assert obb["resize_height"] == 1024

    def test_reid_params(self):
        reid = TASK_PREPROCESS["reid"]
        assert reid["resize_width"] == 128
        assert reid["resize_height"] == 256
        assert reid["keep_ratio"] is False


class TestE2ESupportedTasks:
    def test_13_tasks(self):
        assert len(E2E_SUPPORTED_TASKS_V2) == 13

    def test_excludes_pixel_output_categories(self):
        assert "image_denoising" not in E2E_SUPPORTED_TASKS_V2
        assert "depth_estimation" not in E2E_SUPPORTED_TASKS_V2
        assert "super_resolution" not in E2E_SUPPORTED_TASKS_V2
        assert "image_enhancement" not in E2E_SUPPORTED_TASKS_V2

    def test_includes_core_tasks(self):
        assert "object_detection" in E2E_SUPPORTED_TASKS_V2
        assert "face_detection" in E2E_SUPPORTED_TASKS_V2
        assert "pose_estimation" in E2E_SUPPORTED_TASKS_V2
        assert "classification" in E2E_SUPPORTED_TASKS_V2


class TestMultiStreamSupportedTasks:
    def test_excludes_classification(self):
        assert "classification" not in MULTI_STREAM_SUPPORTED_TASKS_V2

    def test_is_subset_of_e2e(self):
        assert MULTI_STREAM_SUPPORTED_TASKS_V2.issubset(E2E_SUPPORTED_TASKS_V2)

    def test_count(self):
        assert len(MULTI_STREAM_SUPPORTED_TASKS_V2) == len(E2E_SUPPORTED_TASKS_V2) - 1


class TestCategoryVideo:
    def test_13_entries(self):
        assert len(CATEGORY_VIDEO) == 13

    def test_od_video_correct(self):
        assert CATEGORY_VIDEO["object_detection"] == "assets/videos/blackbox-city-road.mp4"

    def test_face_video(self):
        assert CATEGORY_VIDEO["face_detection"] == "assets/videos/dance-solo.mov"

    def test_obb_video(self):
        assert CATEGORY_VIDEO["obb_detection"] == "assets/videos/obb.mp4"


class TestFamilyPostprocessMap:
    def test_has_entries(self):
        assert len(FAMILY_POSTPROCESS_MAP) >= 30

    def test_yolo26_od(self):
        lib = resolve_postprocess_lib("object_detection", "yolo26")
        assert lib is not None
        assert "yolo26od" in lib.name

    def test_scrfd_face(self):
        lib = resolve_postprocess_lib("face_detection", "scrfd")
        assert lib is not None
        assert "scrfd500m" in lib.name

    def test_classification_fallback(self):
        lib = resolve_postprocess_lib("classification", "resnet")
        assert lib is not None
        assert "generic_noop" in lib.name

    def test_no_lib_returns_none(self):
        """Truly unknown category/family returns None."""
        lib = resolve_postprocess_lib("unknown_category", "unknown_family")
        assert lib is None

    def test_generic_noop_fallback(self):
        """Models without specific lib get generic_noop."""
        lib = resolve_postprocess_lib("object_detection", "damoyolo")
        assert lib is not None
        assert "generic_noop" in lib.name

    def test_config_path_v2_returns_path(self):
        path = get_postprocess_config_path_v2("object_detection", "yolo26")
        assert path is not None
        assert path.exists()

    def test_config_path_v2_unsupported(self):
        """Truly unknown category returns None."""
        path = get_postprocess_config_path_v2("unknown_category", "unknown_family")
        assert path is None


class TestGetTaskPreprocessV2:
    def test_known_suffix_od(self):
        result = get_task_preprocess_v2("od")
        assert result["resize_width"] == 640
        assert result["keep_ratio"] is True

    def test_known_suffix_cls(self):
        result = get_task_preprocess_v2("cls")
        assert result["resize_width"] == 224
        assert result["keep_ratio"] is False

    def test_unknown_fallback(self):
        result = get_task_preprocess_v2("unknown_suffix")
        assert result["resize_width"] == 640
        assert result["resize_height"] == 640
        assert result["pad_value"] == 114
        assert result["keep_ratio"] is True

    def test_empty_fallback(self):
        result = get_task_preprocess_v2()
        assert result["resize_width"] == 640

    def test_returns_copy(self):
        r1 = get_task_preprocess_v2("od")
        r1["resize_width"] = 999
        r2 = get_task_preprocess_v2("od")
        assert r2["resize_width"] == 640


class TestBackwardCompat:
    def test_task_map_has_5_entries(self):
        assert len(TASK_MAP) == 5

    def test_task_map_values(self):
        assert TASK_MAP["od"] == "object_detection"
        assert TASK_MAP["pose"] == "pose_estimation"
        assert TASK_MAP["seg"] == "segmentation"
        assert TASK_MAP["obb"] == "oriented_bbox"
        assert TASK_MAP["cls"] == "classification"

    def test_e2e_supported_tasks_has_5(self):
        assert len(E2E_SUPPORTED_TASKS) == 5

    def test_e2e_supported_tasks_values(self):
        assert E2E_SUPPORTED_TASKS == {
            "object_detection", "pose_estimation", "segmentation",
            "oriented_bbox", "classification",
        }

    def test_multi_stream_supported_tasks_has_4(self):
        assert len(MULTI_STREAM_SUPPORTED_TASKS) == 4

    def test_multi_stream_supported_tasks_values(self):
        assert MULTI_STREAM_SUPPORTED_TASKS == {
            "object_detection", "pose_estimation", "segmentation", "oriented_bbox",
        }

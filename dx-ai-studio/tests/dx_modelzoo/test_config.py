"""config.py path computation tests"""
import sys, os, pytest, importlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_modelzoo"))


class TestConfig:
    def test_script_dir_points_to_dx_modelzoo(self):
        from core.config import SCRIPT_DIR
        assert SCRIPT_DIR.name == "dx_modelzoo"
        assert SCRIPT_DIR.is_dir()

    def test_suite_root_exists(self):
        from core.config import SUITE_ROOT
        assert (SUITE_ROOT / "dx-ai-studio").is_dir()
        assert (SUITE_ROOT / "dx-runtime").is_dir()

    def test_dx_app_root_default(self):
        from core.config import DX_APP_ROOT
        assert "dx-runtime" in str(DX_APP_ROOT)
        assert str(DX_APP_ROOT).endswith("dx_app")

    def test_dx_app_root_env_override(self, monkeypatch, tmp_path):
        monkeypatch.setenv("DX_APP_ROOT", str(tmp_path))
        from core import config
        importlib.reload(config)
        assert str(config.DX_APP_ROOT) == str(tmp_path)
        monkeypatch.delenv("DX_APP_ROOT")
        importlib.reload(config)

    def test_config_file_path(self):
        from core.config import CONFIG_FILE
        assert str(CONFIG_FILE).endswith("test_models.conf")

    def test_categories_has_37_entries(self):
        """22 (dx_app main) + 14 per-model layout keys (7 renamed tasks + 7 new tasks) + mainbody_detection."""
        from core.config import CATEGORIES
        assert len(CATEGORIES) == 37

    def test_categories_keys(self):
        from core.config import CATEGORIES
        required = {"object_detection", "classification", "ppu", "face_detection",
                    "pose_estimation", "semantic_segmentation", "instance_segmentation",
                    "image_denoising", "obb_detection", "reid", "embedding",
                    "attribute_recognition", "super_resolution", "face_alignment",
                    "depth_estimation", "image_enhancement", "hand_landmark",
                    # task keys from the staging catalog
                    "hand_detection", "keypoint_detection", "object_pose_estimation",
                    "panoptic_driving_perception", "3d_object_detection",
                    # task keys of the dx_app per-model layout
                    "image_classification", "oriented_object_detection", "face_landmark", "face_recognition",
                    "person_attribute", "low_light_enhancement", "person_reid",
                    "anomaly_detection", "zero_shot_image_classification", "zero_shot_instance_segmentation",
                    "image_matting", "image_retrieval", "visual_place_recognition", "face_attribute",
                    "mainbody_detection"}
        assert set(CATEGORIES.keys()) == required

    def test_default_port(self):
        from core.config import DEFAULT_PORT
        assert DEFAULT_PORT == 8094

    def test_dx_app_port(self):
        from core.config import DX_APP_PORT
        assert DX_APP_PORT == 8080

    def test_static_dir_exists(self):
        from core.config import STATIC_DIR
        assert STATIC_DIR.name == "static"

    def test_data_dir_exists(self):
        from core.config import DATA_DIR
        assert DATA_DIR.name == "data"

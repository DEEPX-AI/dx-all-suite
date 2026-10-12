"""Studio id remap for general-network public Model Zoo sync."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dx_modelzoo.metadata.studio_id_map import (
    load_studio_index,
    remap_public_models,
    resolve_studio_id,
)


class TestStudioIdMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = load_studio_index(ROOT.parent)

    def test_resolves_deit_display_alias(self):
        fields = {
            "display.class_name": "DeiT-Base (224x224)",
            "specification.input_resolution": "224x224x3",
            "specification.parameters": "86.57",
            "specification.operations": "18.01",
        }
        self.assertEqual(resolve_studio_id("deit_b_224x224", fields, self.index), "deit_base")

    def test_remap_collapses_artifact_key_to_studio_id(self):
        public = {
            "deit_b_224x224": {
                "display.class_name": "DeiT-Base (224x224)",
                "evaluation.raw.accuracy": "81.798",
            }
        }
        remapped, warnings = remap_public_models(public, self.index)
        self.assertIn("deit_base", remapped)
        self.assertEqual(remapped["deit_base"]["evaluation.raw.accuracy"], "81.798")
        self.assertEqual(warnings, [])

    def test_damoyolo_tinynas_onnx_suffix_maps_to_studio_id_not_classic_damoyolom(self):
        """DamoYoloM-2 (TinyNAS-L20M) must not collapse into damoyolom via shared GFLOPs/params."""
        fields = {
            "display.class_name": "DAMO-YOLO TinyNAS-L20M",
            "artifacts.onnx.remote_url": "https://sdk.deepx.ai/modelzoo/onnx/DamoYoloM-2.onnx",
            "specification.input_resolution": "640x640x3",
            "specification.parameters": "28.20",
            "specification.operations": "31.85",
            "evaluation.raw.accuracy": "49.421",
        }
        self.assertEqual(
            resolve_studio_id("damoyolom_2", fields, self.index),
            "damoyolo_tinynasl20_m",
        )
        remapped, _ = remap_public_models({"damoyolom_2": fields}, self.index)
        self.assertIn("damoyolo_tinynasl20_m", remapped)
        self.assertNotIn("damoyolom_2", remapped)
        self.assertEqual(remapped["damoyolo_tinynasl20_m"]["evaluation.raw.accuracy"], "49.421")

    def test_local_studio_catalog_baseline_count(self):
        from dx_modelzoo.metadata.adapters import local_studio_catalog_adapter

        result = local_studio_catalog_adapter(ROOT.parent)
        self.assertTrue(result["ok"])
        self.assertGreaterEqual(len(result["models"]), 340)


if __name__ == "__main__":
    unittest.main()


def test_unmapped_publish_models_are_one_row_each_with_a_task_key():
    """The publish page gives each model under two keys (name and .dxnn stem). A model missing from the studio
    catalog must still be one row, with a task key rather than the page text ("Anomaly Detection")."""
    from dx_modelzoo.metadata.studio_id_map import remap_public_models

    url = "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/patchcore_224x224.dxnn"
    fields = {"display.task": "Anomaly Detection", "display.name": "PatchCore",
              "artifacts.qlite_dxnn.remote_url": url}
    cls = {"display.task": "Image Classification", "display.name": "VitB",
           "artifacts.qlite_dxnn.remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/vit-b-p16_384x384.dxnn"}
    index = {"studio_ids": set(), "by_key": {}, "by_signature": {}}
    out, _ = remap_public_models({"patchcore": dict(fields), "patchcore_224x224": dict(fields),
                                  "vitbasep16": dict(cls), "vit_b_p16_384x384": dict(cls)}, index)
    assert sorted(out) == ["patchcore_224x224", "vit_b_p16_384x384"], sorted(out)
    assert out["patchcore_224x224"]["display.task"] == "anomaly_detection"
    assert out["vit_b_p16_384x384"]["display.task"] == "classification", "옛 key 가 있는 task 는 기존 무리와 같이"


def test_two_page_models_never_collapse_into_one_studio_id():
    """One row per .dxnn stem on the publish page. Merging similar names (yolo11-m and its pre-optimized build)
    into one studio id would drop one of them from the list."""
    from dx_modelzoo.metadata.studio_id_map import remap_public_models

    def row(stem, task="Object Detection"):
        return {"display.task": task, "display.name": stem,
                "artifacts.qlite_dxnn.remote_url": f"https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/{stem}.dxnn"}
    # Name/signature matching resolves the pre-optimized build to yolo11m too; by_key reproduces that collision
    index = {"studio_ids": {"yolo11m"}, "by_signature": {},
             "by_key": {"yolo11m": "yolo11m", "yolo11_m_640x640": "yolo11m", "yolo11_m_640x640_pre_optimized": "yolo11m"}}
    out, _ = remap_public_models({
        "yolo11m": row("yolo11-m_640x640"), "yolo11_m_640x640": row("yolo11-m_640x640"),
        "yolo11_m_640x640_pre_optimized": row("yolo11-m_640x640_pre-optimized")}, index)
    assert sorted(out) == ["yolo11_m_640x640_pre_optimized", "yolo11m"], sorted(out)
    assert out["yolo11m"]["artifacts.qlite_dxnn.remote_url"].endswith("/yolo11-m_640x640.dxnn")
    assert out["yolo11_m_640x640_pre_optimized"]["artifacts.qlite_dxnn.remote_url"].endswith("_pre-optimized.dxnn")


def test_both_keys_of_one_page_model_land_on_the_same_row():
    """The page gives one model under a name key and a stem key. If only the name key resolves to a studio id and the
    stem key becomes its own row, the model shows twice (yolov5m6 · yolov5_m6_1280x1280)."""
    from dx_modelzoo.metadata.studio_id_map import remap_public_models

    f = {"display.task": "Object Detection", "display.name": "YOLOv5-M6",
         "artifacts.qlite_dxnn.remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/yolov5-m6_1280x1280.dxnn"}
    index = {"studio_ids": {"yolov5m6"}, "by_signature": {}, "by_key": {"yolov5m6": "yolov5m6"}}
    out, _ = remap_public_models({"yolov5m6": dict(f), "yolov5_m6_1280x1280": dict(f)}, index)
    assert sorted(out) == ["yolov5m6"], sorted(out)


def test_a_stem_claimed_by_two_studio_ids_goes_to_the_one_named_after_it():
    """When the curated catalog has one model under two ids (yolov5m6 · yolov5_m6_1280x1280), a page row must not attach to both."""
    from dx_modelzoo.metadata.studio_id_map import remap_public_models

    f = {"display.task": "Object Detection", "display.name": "YOLOV5M6-1",
         "artifacts.qlite_dxnn.remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/yolov5-m6_1280x1280.dxnn"}
    index = {"studio_ids": {"yolov5m6", "yolov5_m6_1280x1280"}, "by_signature": {},
             "by_key": {"yolov5m6": "yolov5m6", "yolov5_m6_1280x1280": "yolov5_m6_1280x1280"}}
    out, _ = remap_public_models({"yolov5m6": dict(f), "yolov5_m6_1280x1280": dict(f)}, index)
    assert sorted(out) == ["yolov5_m6_1280x1280"], sorted(out)


def test_a_row_pushed_off_an_id_does_not_fall_back_onto_it_by_its_key():
    """The page's 1280 YOLOv5-M6 has the name key 'yolov5m6'. Once displaced from the studio's yolov5m6 (the 640
    build), it must not reattach through that key, or the two builds mix in one row."""
    from dx_modelzoo.metadata.studio_id_map import remap_public_models

    def row(stem):
        return {"display.task": "Object Detection", "display.name": stem,
                "artifacts.onnx.remote_url": f"https://sdk.deepx.ai/modelzoo/onnx/{stem}.onnx"}
    index = {"studio_ids": {"yolov5m6"}, "by_signature": {},
             "by_key": {"yolov5m6": "yolov5m6", "yolov5_m6_640x640": "yolov5m6"}}
    out, _ = remap_public_models({"yolov5_m6_640x640": row("yolov5-m6_640x640"), "yolov5m6": row("yolov5-m6_1280x1280"),
                                  "yolov5_m6_1280x1280": row("yolov5-m6_1280x1280")}, index)
    assert sorted(out) == ["yolov5_m6_1280x1280", "yolov5m6"], sorted(out)
    assert out["yolov5m6"]["artifacts.onnx.remote_url"].endswith("_640x640.onnx")

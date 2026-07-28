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

"""Public Model Zoo (developer.deepx.ai/modelzoo) HTML parser + adapter."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dx_modelzoo.metadata._public_parser import parse_public_modelzoo_html
from dx_modelzoo.metadata.adapters import public_modelzoo_adapter

# Minimal 2-model fixture mirroring the real 3-row grouped header.
_FIXTURE = """
<table class="model-zoo-table"><thead>
<tr><th rowspan="3">Class Name</th><th rowspan="3">Dataset</th><th rowspan="3">Input<br>Resolution</th>
<th rowspan="3">Operations<br>(GFLOPs)</th><th rowspan="3">Parameters<br>(M)</th><th rowspan="3">License</th>
<th rowspan="3">Metric</th><th rowspan="3">Source</th><th colspan="2" rowspan="2">Original (FP32)</th>
<th colspan="8">Quantized (INT8)</th><th rowspan="3">Sample<br>Apps</th></tr>
<tr><th colspan="3">Q-Lite</th><th colspan="3">Q-Pro</th><th colspan="2">Performance</th></tr>
<tr><th>Accuracy</th><th>ONNX</th><th>Accuracy</th><th>DXNN</th><th>JSON</th>
<th>Accuracy</th><th>DXNN</th><th>JSON</th><th>FPS</th><th>FPS/Watt</th></tr>
</thead><tbody>
<tr><td>AlexNet</td><td>ImageNet</td><td>224x224x3</td><td>0.72</td><td>61.10</td><td>BSD-3-Clause</td>
<td>Top1</td><td><a href="https://ex.com/alexnet">src</a></td>
<td>56.5</td><td><a href="https://sdk.deepx.ai/modelzoo/onnx/AlexNet-1.onnx">onnx</a></td>
<td>56.2</td><td><a href="https://sdk.deepx.ai/modelzoo/dxnn/AlexNet.dxnn">dxnn</a></td><td><a href="https://sdk.deepx.ai/j/AlexNet.json">json</a></td>
<td>56.4</td><td><a href="https://sdk.deepx.ai/qp/AlexNet.dxnn">dxnn</a></td><td><a href="https://sdk.deepx.ai/qpj/AlexNet.json">json</a></td>
<td>634</td><td>1435.06</td><td>cls</td></tr>
<tr><td>YoloV5S</td><td>COCO</td><td>640x640x3</td><td>16.5</td><td>7.20</td><td>GPL-3.0</td>
<td>mAP</td><td><a href="https://ex.com/yolo">src</a></td>
<td>37.4</td><td><a href="https://sdk.deepx.ai/o/YoloV5S-1.onnx">onnx</a></td>
<td>36.9</td><td><a href="https://sdk.deepx.ai/d/YoloV5S.dxnn">dxnn</a></td><td><a href="https://sdk.deepx.ai/j/YoloV5S.json">json</a></td>
<td></td><td></td><td></td>
<td>410</td><td>980.1</td><td>od</td></tr>
</tbody></table>
"""


class TestPublicParser(unittest.TestCase):
    def setUp(self):
        self.models, self.warns = parse_public_modelzoo_html(_FIXTURE)

    def test_parses_all_rows(self):
        self.assertEqual(len(self.models), 2)
        self.assertEqual(self.warns, [])

    def test_full_field_extraction(self):
        a = self.models["alexnet"]
        self.assertEqual(a["specification.input_resolution"], "224x224x3")
        self.assertEqual(a["specification.operations"], "0.72")
        self.assertEqual(a["specification.parameters"], "61.10")
        self.assertEqual(a["legal.license"], "BSD-3-Clause")
        self.assertEqual(a["specification.metric.name"], "Top1")
        self.assertEqual(a["legal.source_url"], "https://ex.com/alexnet")
        self.assertEqual(a["evaluation.raw.accuracy"], "56.5")
        self.assertEqual(a["evaluation.qlite.accuracy"], "56.2")
        self.assertEqual(a["evaluation.qpro.accuracy"], "56.4")
        self.assertEqual(a["performance.fps"], 634.0)
        self.assertEqual(a["performance.fps_per_watt"], 1435.06)

    def test_link_fields_take_href(self):
        a = self.models["alexnet"]
        self.assertEqual(a["artifacts.onnx.remote_url"], "https://sdk.deepx.ai/modelzoo/onnx/AlexNet-1.onnx")
        self.assertEqual(a["artifacts.qlite_dxnn.remote_url"], "https://sdk.deepx.ai/modelzoo/dxnn/AlexNet.dxnn")
        self.assertEqual(a["artifacts.qpro_json.remote_url"], "https://sdk.deepx.ai/qpj/AlexNet.json")

    def test_missing_qpro_is_blank_not_error(self):
        y = self.models["yolov5s"]
        self.assertNotIn("artifacts.qpro_dxnn.remote_url", y)  # empty cell -> field absent
        self.assertEqual(y["performance.fps"], 410.0)

    def test_adapter_uses_injected_fetch(self):
        r = public_modelzoo_adapter(".", fetch_text=lambda url: _FIXTURE)
        self.assertTrue(r["ok"])
        self.assertEqual(len(r["models"]), 2)

    def test_adapter_handles_fetch_failure(self):
        def boom(url):
            raise RuntimeError("network down")
        r = public_modelzoo_adapter(".", fetch_text=boom)
        self.assertFalse(r["ok"])
        self.assertTrue(r["errors"])

    def test_keyed_by_artifact_filename_not_display_name(self):
        # local catalog ids derive from the dxnn/onnx filename; the public key must match that,
        # not the display name. AlexNet.dxnn -> "alexnet", YoloV5S.dxnn -> "yolov5s".
        self.assertIn("alexnet", self.models)
        self.assertIn("yolov5s", self.models)
        # a model whose display name differs from its artifact stem is keyed by the artifact
        html = _FIXTURE.replace(">AlexNet<", ">AlexNet (ImageNet)<").replace(
            "AlexNet.dxnn", "alexnet_v1.dxnn")
        models, _ = parse_public_modelzoo_html(html)
        self.assertIn("alexnet_v1", models)

    def test_dotted_name_not_truncated(self):
        # artifact filename with a dot in the number (mobilnet0.5) must NOT be truncated
        # by double extension-stripping -> key keeps the full name to match the local id.
        html = _FIXTURE.replace("AlexNet.dxnn", "3ddfa_v2_mobilnet0.5_120x120.dxnn")
        models, _ = parse_public_modelzoo_html(html)
        self.assertIn("3ddfa_v2_mobilnet0_5_120x120", models)
        self.assertNotIn("3ddfa_v2_mobilnet0", models)

    def test_non_model_tables_skipped(self):
        models, warns = parse_public_modelzoo_html("<table><tr><th>Cookie</th></tr><tr><td>x</td></tr></table>")
        self.assertEqual(models, {})


if __name__ == "__main__":
    unittest.main()

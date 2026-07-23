"""dx_app ModelZoo HTML parser must handle BOTH server-rendered layouts:
  - public  (developer.deepx.ai/modelzoo/): [Class Name, Dataset, ...] — no Task/Name cols,
    model name = Class Name, category = section heading, spec cols start at index 0.
  - internal (devops publish):              [Task, Name, ClassName, Dataset, ...] — spec at 2.
Regression guard: the public page must not map dataset (ImageNet/COCO) into the name field.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dx_app"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dx_app" / "core"))

import modelzoo  # noqa: E402


def _link(url):
    return f'<a href="{url}">x</a>'


_PUBLIC_HTML = """
<h2>Object Detection (1)</h2>
<table>
  <tr><th>Class Name</th><th>Dataset</th><th>Input</th><th>Ops</th><th>Params</th>
      <th>License</th><th>Metric</th><th>Source</th><th>Original</th><th>Quantized</th><th>SampleApps</th></tr>
  <tr><th>Q-Lite</th><th>Q-Pro</th><th>Performance</th></tr>
  <tr><th>Accuracy</th><th>ONNX</th><th>Accuracy</th><th>DXNN</th><th>JSON</th>
      <th>Accuracy</th><th>DXNN</th><th>JSON</th><th>FPS</th><th>FPS/Watt</th></tr>
  <tr>
    <td>YoloV5S</td><td>COCO</td><td>640x640x3</td><td>7.5</td><td>7.2</td>
    <td>GPL-3.0</td><td>mAP</td><td></td><td>37.4</td><td>{onnx}</td>
    <td>36.9</td><td>{qld}</td><td>{qlj}</td>
    <td>36.5</td><td>{qpd}</td><td>{qpj}</td>
    <td>129</td><td>62.7</td><td></td>
  </tr>
</table>
""".format(
    onnx=_link("https://sdk.deepx.ai/modelzoo/onnx/YoloV5S-1.onnx"),
    qld=_link("https://sdk.deepx.ai/modelzoo/dxnn/2_3_0/YoloV5S.dxnn"),
    qlj=_link("https://sdk.deepx.ai/modelzoo/json/YoloV5S-1.json"),
    qpd=_link("https://sdk.deepx.ai/modelzoo/dxnn/2_2_0/q-pro/YoloV5S-1.dxnn"),
    qpj=_link("https://sdk.deepx.ai/modelzoo/q-pro-json/YoloV5S-1.json"),
)

_INTERNAL_HTML = """
<h2>Detection</h2>
<table>
  <tr><th>Task</th><th>Name</th><th>Class Name</th><th>Dataset</th><th>Input</th><th>Ops</th>
      <th>Params</th><th>License</th><th>Metric</th><th>Source</th><th>Raw</th><th>NPU</th></tr>
  <tr><th></th><th>Q-Lite</th><th>Q-Pro</th><th>Performance</th></tr>
  <tr><th>Acc</th><th>ONNX</th><th>Acc</th><th>DXNN</th><th>JSON</th>
      <th>Acc</th><th>DXNN</th><th>JSON</th><th>FPS</th><th>FPS/Watt</th></tr>
  <tr>
    <td>object_detection</td><td>YoloV5S</td><td>YoloV5SClass</td><td>COCO</td><td>640x640x3</td>
    <td>7.5</td><td>7.2</td><td>GPL-3.0</td><td>mAP</td><td></td>
    <td>37.4</td><td>{onnx}</td>
    <td>36.9</td><td>{qld}</td><td>{qlj}</td>
    <td>36.5</td><td>{qpd}</td><td>{qpj}</td>
    <td>129</td><td>62.7</td>
  </tr>
</table>
""".format(
    onnx=_link("https://x/YoloV5S.onnx"), qld=_link("https://x/ql.dxnn"), qlj=_link("https://x/ql.json"),
    qpd=_link("https://x/qp.dxnn"), qpj=_link("https://x/qp.json"),
)


def test_public_layout_maps_columns_correctly():
    models = modelzoo._parse_models(_PUBLIC_HTML)
    assert len(models) == 1
    m = models[0]
    assert m["name"] == "YoloV5S"           # Class Name, NOT the dataset
    assert m["task"] == "Object Detection"  # section heading, count suffix stripped
    assert m["dataset"] == "COCO"
    assert m["input_resolution"] == "640x640x3"
    assert m["ops"] == "7.5" and m["params"] == "7.2"
    assert m["onnx_url"] and m["onnx_url"].endswith("YoloV5S-1.onnx")
    assert m["qlite"]["dxnn_url"] and m["qlite"]["dxnn_url"].endswith("YoloV5S.dxnn")
    assert m["qpro"]["dxnn_url"] and m["qpro"]["dxnn_url"].endswith("YoloV5S-1.dxnn")
    assert m["fps"] == "129" and m["fps_per_watt"] == "62.7"


def test_internal_layout_still_works():
    models = modelzoo._parse_models(_INTERNAL_HTML)
    assert len(models) == 1
    m = models[0]
    assert m["name"] == "YoloV5S"
    assert m["task"] == "object_detection"
    assert m["dataset"] == "COCO"
    assert m["qlite"]["dxnn_url"].endswith("ql.dxnn")
    assert m["qpro"]["dxnn_url"].endswith("qp.dxnn")
    assert m["fps"] == "129"

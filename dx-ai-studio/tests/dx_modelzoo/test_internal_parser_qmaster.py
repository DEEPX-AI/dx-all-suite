"""The publish table's Q-Master columns reach the catalog (15 models offer Q-Master; the parser dropped them)."""
from dx_modelzoo.metadata.adapters import parse_internal_table_html

_HTML = """<table><thead>
<tr><th rowspan="3">Task</th><th rowspan="3">Name</th><th rowspan="3">Display Name</th>
<th rowspan="2" colspan="2">Raw</th><th colspan="3">NPU</th></tr>
<tr><th colspan="3">Q-Master</th></tr>
<tr><th>Accuracy</th><th>ONNX</th><th>Accuracy</th><th>DXNN</th><th>JSON</th></tr>
</thead><tbody><tr><td>object_detection</td><td>yolo26n-1</td><td>Ultralytics YOLO26-n</td><td>39.8752</td>
<td><a href="https://sdk.deepx.ai/modelzoo/onnx/yolo26-n_640x640.onnx">ONNX</a></td><td>39.078</td>
<td><a href="https://sdk.deepx.ai/modelzoo/q-master-dxnn/2_4_0/yolo26-n_640x640.dxnn">DXNN</a></td>
<td><a href="https://sdk.deepx.ai/modelzoo/q-master-json/2_4_0/yolo26-n_640x640.json">JSON</a></td></tr></tbody></table>"""


def test_q_master_columns_are_parsed():
    models = parse_internal_table_html(_HTML)["models"]
    entry = next(iter(models.values()))
    assert entry["evaluation.qmaster.accuracy"] == "39.078"
    assert entry["artifacts.qmaster_dxnn.remote_url"].endswith("/q-master-dxnn/2_4_0/yolo26-n_640x640.dxnn")
    assert entry["artifacts.qmaster_json.remote_url"].endswith("/q-master-json/2_4_0/yolo26-n_640x640.json")


def test_the_publish_task_is_kept_beside_the_merged_task():
    """display.task is merged from several sources; the publish table's own task column stays readable."""
    entry = next(iter(parse_internal_table_html(_HTML)["models"].values()))
    assert entry["display.publish_task"] == "object_detection"


def test_merge_keeps_the_publish_task():
    from dx_modelzoo.metadata.merge import _build_structured_model
    model = _build_structured_model("m", {"display.task": "embedding", "display.publish_task": "image_retrieval"}, {})
    assert model["display"]["task"] == "embedding" and model["display"]["publish_task"] == "image_retrieval"

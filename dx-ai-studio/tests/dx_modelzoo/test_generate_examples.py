"""Pure parts of the Model Zoo result image generator (dx_modelzoo/scripts/generate_examples.py).

A model is paired with the per-model dx_app example whose stem equals its .dxnn name, so a model without an
example is never run through another model's binary (which would stamp, say, a classification result on a
super-resolution image).
"""
from __future__ import annotations

import json

from dx_modelzoo.scripts import generate_examples as g
from shared import dx_app_layout as layout


def _m(mid, url, res=""):
    return {"id": mid, "category": "super_resolution", "specification": {"input_resolution": res},
            "artifacts": {"qlite_dxnn": {"remote_url": url}}}


def test_models_pair_with_their_own_example_by_file_name(tmp_path):
    root = tmp_path / "dx_app"
    ex = root / "src/python_example/super_resolution/espcn/espcn-x2_17x17"
    ex.mkdir(parents=True)
    (ex / "espcn-x2_17x17_sync.py").write_text("")
    (root / "config").mkdir()
    (root / "config/model_registry.json").write_text(json.dumps([{"variant": "espcn-x2_17x17", "family": "espcn"}]))
    layout.clear_cache()
    items = g.plan([_m("espcn_x2", "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/espcn-x2_17x17.dxnn"),
                    {"id": "beit", "artifacts": {"onnx": {"remote_url": "https://x/beit.onnx"}}}], root)
    assert items[0]["example"].py_dir == ex and items[0]["skip"] is None
    assert items[1]["skip"] == "no .dxnn artifact"
    layout.clear_cache()


def test_the_measured_input_shape_and_the_catalog_value():
    assert g._resolution([1, 640, 640, 3]) == "640x640x3"
    assert g._resolution([1, 3, 224, 224]) == "224x224x3", "NCHW 도 HxWxC 로"
    assert g._same_dims("1024x2048x3", "2048x1024x3"), "순서만 다른 것은 같다 (catalog 의 값이 섞여 있다)"
    assert not g._same_dims("640x640x3", "1280x1280x3")

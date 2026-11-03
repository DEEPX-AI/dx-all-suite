"""Publish-page task labels that differ from the runtime category keys must still reach the catalog.

Before this, a publish-only model whose label was not a CATEGORIES key was dropped without a trace
(catalog._generated_only_models), which removed 8 models from the 2026-10-30 page.
"""
from dx_modelzoo.core import catalog
from dx_modelzoo.core.config import CATEGORIES
from shared import tasks

PUBLISH_TO_RUNTIME = {
    "face_landmark_detection": "face_landmark",
    "face_attribute_recognition": "face_attribute",
    "image_de-noising": "image_denoising",
}


def test_publish_labels_resolve_to_runtime_category_keys():
    for label, key in PUBLISH_TO_RUNTIME.items():
        assert tasks.runtime_key(label) == key
        assert key in CATEGORIES


def test_unaliased_labels_pass_through_unchanged():
    assert tasks.runtime_key("image_classification") == "image_classification"


def test_publish_only_model_with_a_publish_label_is_kept_under_the_runtime_category():
    generated = {"models": [{
        "id": "dncnn_15_x",
        "display": {"name": "DnCNN-15", "task": "image_de-noising"},
        "artifacts": {"qlite_dxnn": {"remote_url": "https://sdk.deepx.ai/modelzoo/q-lite-dxnn/2_5_0/dncnn-15.dxnn"}},
    }]}
    out = catalog._generated_only_models(generated, set(), None)
    assert [m["id"] for m in out] == ["dncnn_15_x"]
    assert out[0]["category"] == "image_denoising"


def test_a_model_with_an_unknown_label_is_reported_not_silently_dropped(capsys):
    generated = {"models": [{"id": "mystery", "display": {"name": "X", "task": "no_such_task"}, "artifacts": {}}]}
    out = catalog._generated_only_models(generated, set(), None)
    assert out == []
    assert "mystery" in capsys.readouterr().out

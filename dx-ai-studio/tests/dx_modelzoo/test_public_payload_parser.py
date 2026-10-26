"""Reads __MODEL_ZOO_DATA__ from the public ModelZoo page.

The page carries a structured payload in the document rather than a server-rendered table.

Fields are read by name. The payload's `fields` array gives the column names, so nothing
depends on position: positional parsing can shift every field by one column (`fps` ←
`fps_per_watt`) and show wrong performance numbers.

And it never fails silently. It relies on the page structure, not an official API, so a
changed shape must raise instead of producing a partial catalog.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from dx_modelzoo.metadata._public_parser import parse_public_payload

FIXTURE = Path(__file__).parent / "fixtures" / "public_modelzoo_payload.html"


@pytest.fixture(scope="module")
def rows():
    return parse_public_payload(FIXTURE.read_text(encoding="utf-8"))


def test_every_row_is_read(rows):
    assert len(rows) == 8


def test_fields_are_read_by_name_not_position(rows):
    """Reading by name keeps values in place when the column order changes."""
    by_name = {r["display"]: r for r in rows}
    d = by_name["DenseNet-121"]
    assert d["task"] == "Image Classification"
    assert d["dataset"] == "ImageNet"
    assert d["metric"] == "Top1"
    assert d["params"] == pytest.approx(8.04)
    assert d["ops"] == pytest.approx(3.18)
    assert d["fps"] == pytest.approx(94)
    assert d["fps_per_watt"] == pytest.approx(213.8)
    assert d["license"] == "BSD-3-Clause"


def test_accuracy_is_read_per_tier(rows):
    by_name = {r["display"]: r for r in rows}
    d = by_name["DenseNet-121"]
    assert d["accuracy"]["raw"] == pytest.approx(74.436)
    assert d["accuracy"]["qlite"] == pytest.approx(73.97)
    assert d["accuracy"]["qpro"] == pytest.approx(74.25)
    assert d["accuracy"]["qmaster"] is None        # this model has none

    r = by_name["RepVGG-A0"]                       # a row with all four tiers
    assert r["accuracy"]["qmaster"] == pytest.approx(71.238)


def test_artifact_urls_are_absolute(rows):
    """A relative path (~onnx/…) must join the payload's base into a full URL."""
    d = next(r for r in rows if r["display"] == "DenseNet-121")
    onnx = d["artifacts"]["onnx"]
    assert onnx.startswith("https://sdk.deepx.ai/modelzoo/"), onnx
    assert "~" not in onnx.removeprefix("https://sdk.deepx.ai/modelzoo/")
    assert onnx.endswith("densenet121_224x224.onnx")


def test_absent_artifacts_are_absent_not_empty_strings(rows):
    d = next(r for r in rows if r["display"] == "YOLOv3 Darknet (640x640)")
    assert d["artifacts"].get("qpro_dxnn") is None


def test_missing_global_raises(recwarn):
    """Silent partial success is the worst case, so a missing payload fails loudly."""
    with pytest.raises(ValueError, match="__MODEL_ZOO_DATA__"):
        parse_public_payload("<html><body>no payload here</body></html>")


def test_unknown_field_layout_raises():
    """A required column missing from `fields` raises instead of leaving values empty."""
    broken = (
        '<script>window.__MODEL_ZOO_DATA__ = '
        '{"fields":["task","name"],"base":"https://x/","rows":[["a","b"]]};</script>'
    )
    with pytest.raises(ValueError, match="fields"):
        parse_public_payload(broken)


def test_nested_braces_do_not_truncate_the_payload():
    """The end is found by brace balance; a regex stopping at the first `}` would cut nested objects."""
    payload = (
        '<script>window.__MODEL_ZOO_DATA__ = '
        '{"fields":["task","name","display","dataset","input","ops","params",'
        '"license","metric","source","rawAcc","onnx","qlAcc","qlDxnn","qlJson",'
        '"qpAcc","qpDxnn","qpJson","qmAcc","qmDxnn","qmJson","fps","fpsw"],'
        '"base":"https://x/","note":{"nested":{"deep":1}},'
        '"rows":[["t","n","D","ds","1x1",1,2,"MIT","Top1","http://s",1.0,'
        '"~a.onnx",2.0,null,null,null,null,null,null,null,null,3,4]]};</script>'
    )
    rows = parse_public_payload(payload)
    assert len(rows) == 1 and rows[0]["display"] == "D"


# ── The shape the adapter uses ────────────────────────────────
# The adapter and studio_id_map expect {model id: {dotted leaf path: value}}.
# The leaf paths must match the established schema (specification.dataset /
# parameters / metric.name / evaluation.qmaster …).
from dx_modelzoo.metadata._public_parser import parse_public_modelzoo_html  # noqa: E402


@pytest.fixture(scope="module")
def models():
    parsed, _warnings = parse_public_modelzoo_html(FIXTURE.read_text(encoding="utf-8"))
    return parsed


def test_adapter_shape_is_keyed_by_model_id(models):
    assert isinstance(models, dict) and len(models) == 8
    assert all(isinstance(v, dict) for v in models.values())
    # The id comes from the artifact file name; a dot inside a number must not be stripped twice.
    assert "densenet121_224x224" in models


def test_leaf_paths_match_the_established_schema(models):
    f = models["densenet121_224x224"]
    assert f["display.class_name"] == "DenseNet-121"
    assert f["specification.dataset"] == "ImageNet"
    assert f["specification.input_resolution"] == "224x224x3"
    assert f["specification.parameters"] == pytest.approx(8.04)
    assert f["specification.operations"] == pytest.approx(3.18)
    assert f["specification.metric.name"] == "Top1"
    assert f["legal.license"] == "BSD-3-Clause"
    assert f["legal.source_url"].startswith("https://pytorch.org/")
    assert f["evaluation.raw.accuracy"] == pytest.approx(74.436)
    assert f["evaluation.qlite.accuracy"] == pytest.approx(73.97)
    assert f["evaluation.qpro.accuracy"] == pytest.approx(74.25)
    assert f["performance.fps"] == pytest.approx(94)
    assert f["performance.fps_per_watt"] == pytest.approx(213.8)
    assert f["artifacts.onnx.remote_url"].startswith("https://sdk.deepx.ai/modelzoo/")


def test_absent_tiers_do_not_appear_as_keys(models):
    """Absent values create no key rather than a None.

    merge picks 'the source that has a value', so a None could overwrite a value
    another source filled in.
    """
    f = models["densenet121_224x224"]
    assert "evaluation.qmaster.accuracy" not in f
    assert "artifacts.qmaster_dxnn.remote_url" not in f


def test_dotted_model_names_are_not_double_stripped(models):
    """A dot inside a number must not be taken for an extension.

    Stripping the extension of `3ddfa-v2_mobilenet-0.5_120x120.dxnn` before normalizing
    also drops `.5_120x120`, giving `3ddfa_v2_mobilenet_0`. The full file name is passed
    so Path.stem strips only once.
    """
    assert "3ddfa_v2_mobilenet_0_5_120x120" in models, sorted(models)

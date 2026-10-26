"""`/config/generate` must not store input_shapes that cannot be used.

Negative dimensions or wrong types must get a 4xx instead of being written to
config.json with a 200, where the error would surface only much later at compile time.

The valid range is not guessed: `dx-compiler/.deepx/toolsets/config-schema.md` says
"Dimensions: All must be positive integers (no -1, no 0)".

Some things are deliberately not checked here — whether batch is 1, whether keys match
ONNX node names. This API does not look at the model, so it cannot know, and refusing
them would reject valid input at wizard steps. This layer only blocks what it knows.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from tests.server_helpers import start_module_server

OK_BASE = {"calibration_num": 3, "calibration_method": "ema", "loader_mode": "default"}


@pytest.fixture()
def compiler():
    server, port = start_module_server("dx_compiler")
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()


def _generate(base, payload):
    req = urllib.request.Request(
        base + "/config/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


@pytest.mark.parametrize(
    "shape, why",
    [
        ([1, 3, -224, 224], "음수 차원"),
        ([1, 3, 0, 224], "0 차원"),
        ([1, 3, "not-a-number", 224], "문자열 차원"),
        ([1, 3, 224.5, 224], "실수 차원"),
        ([1, 3, True, 224], "bool 차원 — 파이썬에서 True 는 int 다"),
        ("1,3,224,224", "list 가 아닌 shape"),
        # A scalar differs from a string: a string iterates and fails per character,
        # but iterating an int raises TypeError — without a type guard that is a 500.
        (224, "list 가 아닌 스칼라 shape"),
    ],
)
def test_unusable_shapes_are_refused(compiler, shape, why):
    code, body = _generate(compiler, {**OK_BASE, "input_shapes": {"input.1": shape}})
    assert code == 400, f"{why}: {code} 로 통과했다 — {body}"
    assert body.get("error"), f"{why}: 이유를 말하지 않는다"


def test_input_shapes_must_be_a_mapping(compiler):
    code, body = _generate(compiler, {**OK_BASE, "input_shapes": [1, 3, 224, 224]})
    assert code == 400, body


def test_a_usable_shape_still_passes(compiler):
    code, body = _generate(compiler, {**OK_BASE, "input_shapes": {"input.1": [1, 3, 224, 224]}})
    assert code == 200, body
    assert body["config"]["inputs"] == {"input.1": [1, 3, 224, 224]}


def test_batch_and_node_names_are_left_to_the_compiler(compiler):
    """The docs support only batch=1, but this API does not look at the ONNX.

    Blocking here would reject valid input at wizard steps before a model is chosen.
    Only block what is known.
    """
    code, _ = _generate(compiler, {**OK_BASE, "input_shapes": {"whatever": [4, 3, 224, 224]}})
    assert code == 200, "이 계층이 알 수 없는 것을 막고 있다"


def test_the_calibration_num_behaviour_is_unchanged(compiler):
    """The shape checks must not override the existing calibration_num check."""
    code, body = _generate(
        compiler, {**OK_BASE, "calibration_num": "many", "input_shapes": {"i": [1, 3, 224, 224]}})
    assert code == 400 and "calibration_num" in body.get("error", ""), body


def test_a_negative_calibration_num_is_refused_too(compiler):
    """The server must match the front end's range check.

    The front end's `validateCalibNum` blocks `n <= 0`; the server must check the range
    too, not only the type, or a request that bypasses the GUI stores -5 as-is.
    """
    code, body = _generate(
        compiler, {**OK_BASE, "calibration_num": -5, "input_shapes": {"i": [1, 3, 224, 224]}})
    assert code == 400, f"음수 calibration_num 이 통과했다: {body}"

"""The same field must get the same rule at every endpoint.

`/compile/resume`, `/compile` and `/config/generate` accept the same concepts and
must judge them alike:

    enhanced_scheme with an unknown DXQ key   400 everywhere
    enhanced_scheme that is not a dict        400 everywhere
    calibration method                        400 for values outside the documented set

The rules live once in validation.py and every endpoint calls them, instead of
each endpoint growing its own.

TestResumeContractIsUnchanged pins the resume endpoint's 400 behaviour, so moving
its checks into validation.py cannot change what it accepts.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
import uuid

import pytest
from tests.dx_compiler._compile_paths import compile_paths_not_under_test, compile_jobs_outside_var  # noqa: F401  (path policy is not under test here; jobs go to tmp)

from tests.server_helpers import start_module_server


@pytest.fixture()
def compiler():
    server, port = start_module_server("dx_compiler")
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()


def _post(base, path, payload):
    req = urllib.request.Request(
        base + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _compile(base, **extra):
    fields = {"model_path": "/tmp/a.onnx", "config_path": "/tmp/a.json",
              "output_dir": "/tmp/o", **extra}
    b = uuid.uuid4().hex
    body = "".join(
        f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'
        for k, v in fields.items()) + f"--{b}--\r\n"
    req = urllib.request.Request(
        base + "/compile", data=body.encode(),
        headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]


_RESUME = {"qxnn_path": "/tmp/a.qxnn", "output_dir": "/tmp/o"}


class TestResumeContractIsUnchanged:
    """The resume endpoint keeps its existing contract."""

    @pytest.mark.parametrize("method", ["minmax", "ema", "iqr"])
    def test_the_three_documented_resume_methods_pass(self, compiler, method):
        """02_06_Execution_of_DX-COM.md:103 — `{minmax,ema,iqr}` (Resume-only)."""
        code, body = _post(compiler, "/compile/resume",
                           {**_RESUME, "recalibration_method": method})
        assert code == 200, f"{method} 를 막았다 — {body}"

    @pytest.mark.parametrize("method", ["고양이", "EMA", "", "  "])
    def test_other_resume_methods_are_refused(self, compiler, method):
        code, _ = _post(compiler, "/compile/resume",
                        {**_RESUME, "recalibration_method": method})
        # "" means "not specified" — that behaviour stays.
        expected = 200 if not method.strip() else 400
        assert code == expected

    def test_unknown_dxq_keys_are_still_refused(self, compiler):
        code, body = _post(compiler, "/compile/resume",
                           {**_RESUME, "enhanced_scheme": {"DXQ-P99": {}}})
        assert code == 400 and "DXQ-P99" in body

    def test_a_non_object_enhanced_scheme_is_still_refused(self, compiler):
        code, _ = _post(compiler, "/compile/resume",
                        {**_RESUME, "enhanced_scheme": [1, 2, 3]})
        assert code == 400

    def test_q_pro_and_enhanced_scheme_are_still_mutually_exclusive(self, compiler):
        code, _ = _post(compiler, "/compile/resume",
                        {**_RESUME, "use_q_pro": True,
                         "enhanced_scheme": {"DXQ-P3": {"num_samples": 8}}})
        assert code == 400


class TestCompileNowChecksWhatResumeAlreadyChecked:
    def test_an_unknown_dxq_key_is_refused(self, compiler):
        code, body = _compile(compiler, enhanced_scheme='{"DXQ-P99": {"num_samples": 8}}')
        assert code == 400, f"resume 은 막는 값을 /compile 이 통과시켰다 — {code} {body}"

    @pytest.mark.parametrize("raw", ['[1,2,3]', '"hello"', '42'])
    def test_a_non_object_enhanced_scheme_is_refused(self, compiler, raw):
        code, body = _compile(compiler, enhanced_scheme=raw)
        assert code == 400, f"enhanced_scheme={raw} 가 통과했다 — {code} {body}"

    def test_a_valid_scheme_still_compiles(self, compiler):
        """No over-blocking — a valid DXQ scheme must still pass."""
        code, body = _compile(compiler, enhanced_scheme='{"DXQ-P3": {"num_samples": 8}}')
        assert code == 200, f"정상 DXQ 를 막았다 — {code} {body}"


class TestDxqValuesMustBeObjects:
    """Scheme keys are whitelisted; their values must be objects too.

    Parameter **names** are not restricted — per 02_06:493 they differ per scheme
    (alpha, beta, cosim_num, num_samples), so restricting them would over-block.
    Only check that the value is an object.
    """

    @pytest.mark.parametrize("value", ["많이", 5, [1, 2], None])
    def test_a_scheme_value_that_is_not_an_object_is_refused(self, compiler, value):
        code, body = _post(compiler, "/compile/resume",
                           {**_RESUME, "enhanced_scheme": {"DXQ-P3": value}})
        assert code == 400, f"DXQ-P3={value!r} 가 통과했다 — {code} {body}"

    @pytest.mark.parametrize("params", [
        {"num_samples": 1024},
        {"alpha": 0.5},
        {"alpha": 0.1, "beta": 1.0, "cosim_num": 2},
        {},
    ])
    def test_documented_scheme_parameters_pass(self, compiler, params):
        """Parameter combinations from 02_06:493. Names are not whitelisted, so
        all of them must pass."""
        code, body = _post(compiler, "/compile/resume",
                           {**_RESUME, "enhanced_scheme": {"DXQ-P0": params}})
        assert code == 200, f"문서에 있는 인자를 막았다: {params} — {body}"


class TestConfigCalibrationMethodIsNotTheResumeOne:
    """Similar names, different things.

    config.json's calibration_method is `{ema, minmax}` (config-schema.md:76).
    Resume's recalibration_method is `{minmax, ema, iqr}`, which the docs mark
    **"(Resume-only)"** (02_06:103).

    Merging the two would let iqr into config.json. This test records why they stay
    separate, so they are not merged as an apparent duplicate.
    """

    @pytest.mark.parametrize("method", ["ema", "minmax"])
    def test_the_two_documented_methods_pass(self, compiler, method):
        code, body = _post(compiler, "/config/generate",
                           {"input_shapes": {"i": [1, 3, 8, 8]},
                            "calibration_method": method})
        assert code == 200, body
        assert json.loads(body)["config"]["calibration_method"] == method

    def test_iqr_is_resume_only_and_does_not_belong_in_config_json(self, compiler):
        code, body = _post(compiler, "/config/generate",
                           {"input_shapes": {"i": [1, 3, 8, 8]},
                            "calibration_method": "iqr"})
        assert code == 400, f"iqr 이 config.json 에 들어갔다 — {code} {body}"

    @pytest.mark.parametrize("method", ["고양이", "EMA", 5, {"a": 1}, []])
    def test_anything_else_is_refused(self, compiler, method):
        code, body = _post(compiler, "/config/generate",
                           {"input_shapes": {"i": [1, 3, 8, 8]},
                            "calibration_method": method})
        assert code == 400, f"calibration_method={method!r} 가 저장됐다 — {body}"

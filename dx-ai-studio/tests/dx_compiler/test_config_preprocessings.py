"""`/config/generate` must refuse unusable preprocessings.

Fields such as `resize.width` live inside `preprocessings[]` and must be validated.
Bad values reach the server straight from the GUI: the parameter inputs are free-text
`type="text"` fields and the collector sends `isNaN(num) ? raw : num`, so whatever is
typed is sent as-is.

What is NOT blocked matters more. Real configs in the repository look like:

    {"resize": {"mode": "pad", "size": 640,
                "pad_location": "edge",          # the UI sends upper-case 'EDGE'
                "pad_value": [114, 114, 114]}}   # the UI default is scalar 0
    {"transpose": {"axis": [2, 0, 1]}}           # list
    {"expandDim": {"axis": 0}}                   # scalar

The same parameter can be a scalar or a list and its case varies. Rules on such
things would block configs in use today. Only values with a clear meaning are checked.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest
from tests.dx_compiler._compile_paths import compile_paths_not_under_test, compile_jobs_outside_var  # noqa: F401  (path policy is not under test here; jobs go to tmp)

from tests.server_helpers import start_module_server

OK = {"loader_mode": "default", "dataset_path": "/tmp/calib",
      "input_shapes": {"images": [1, 3, 640, 640]}}

# A preprocessing chain taken verbatim from a real config in the repository.
# A rule that blocks it is wrong.
REAL_CHAIN = [
    {"resize": {"mode": "pad", "size": 640, "pad_location": "edge",
                "pad_value": [114, 114, 114]}},
    {"div": {"x": 255.0}},
    {"convertColor": {"form": "BGR2RGB"}},
    {"transpose": {"axis": [2, 0, 1]}},
    {"expandDim": {"axis": 0}},
]


@pytest.fixture()
def compiler():
    server, port = start_module_server("dx_compiler")
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()


def _generate(base, preps):
    payload = {**OK, "preprocessings": preps}
    req = urllib.request.Request(
        base + "/config/generate", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


class TestRealConfigsMustKeepWorking:
    """No over-blocking. If this class fails, the rule is wrong."""

    def test_the_chain_from_the_repositorys_own_configs_passes(self, compiler):
        code, body = _generate(compiler, REAL_CHAIN)
        assert code == 200, f"저장소의 실제 config 를 막았다 — {body}"
        assert body["config"]["default_loader"]["preprocessings"] == REAL_CHAIN

    @pytest.mark.parametrize("entry", [
        {"transpose": {"axis": [2, 0, 1]}},
        {"expandDim": {"axis": 0}},
        {"squeeze": {"axis": -1}},
        {"div": {"x": 255.0}},
        {"div": {"x": [255.0, 255.0, 255.0]}},
        {"subtract": {"x": -1.0}},
        {"resize": {"mode": "pad", "size": 640, "pad_value": [114, 114, 114]}},
        {"resize": {"mode": "pad", "size": 640, "pad_value": 0}},
        {"convertColor": {"form": "BGR2RGB"}},
        {"dtype": {"t": "float32"}},
        {"pil_2_cv": None},
        {"slice": {"channel": 3}},
    ])
    def test_shapes_that_vary_legitimately_are_left_alone(self, compiler, entry):
        """axis may be negative or a list; x and pad_value may be a scalar or a list.

        A rule here would block valid configs. Leave them alone.
        """
        code, body = _generate(compiler, [entry])
        assert code == 200, f"정당한 값을 막았다: {entry} — {body}"

    @pytest.mark.parametrize("name", ["resize2", "resize3", "resize_tv", "그런거"])
    def test_transform_names_are_not_whitelisted(self, compiler, name):
        """The vendor registry (02_06:394) has resize2, resize3 and resize_tv, which the
        UI does not offer. Blocking by the UI list would reject valid configs, and the
        documented list may be out of date. The compile step judges names."""
        code, body = _generate(compiler, [{name: {"size": 640}}])
        assert code == 200, f"transform 이름을 막았다: {name} — {body}"


class TestUnusableSizesAreRefused:
    @pytest.mark.parametrize("width, why", [
        (-640, "음수 — 티켓이 지목한 바로 그 값"),
        (0, "0 — 크기가 될 수 없다"),
        ("abc", "문자열"),
        ("640", "숫자처럼 보이는 문자열 — GUI 자유 입력이 이것을 만든다"),
        (True, "bool — 파이썬에서 True 는 int 다"),
        (None, "없음"),
    ])
    def test_a_resize_width_that_cannot_be_a_size_is_refused(self, compiler, width, why):
        code, body = _generate(compiler, [{"resize": {"mode": "default",
                                                      "width": width, "height": 640}}])
        assert code == 400, f"{why}: width={width!r} 가 통과했다 — {body}"

    @pytest.mark.parametrize("key", ["width", "height", "size", "scale"])
    def test_every_size_like_parameter_is_checked(self, compiler, key):
        code, body = _generate(compiler, [{"resize": {"mode": "default", key: -1}}])
        assert code == 400, f"{key}=-1 이 통과했다 — {body}"

    def test_centercrop_sizes_are_checked_too(self, compiler):
        """Size rules attach to the **parameter name**, not the transform name.
        Checking only resize would miss centercrop."""
        code, body = _generate(compiler, [{"centercrop": {"width": 0, "height": 224}}])
        assert code == 400, f"centercrop.width=0 이 통과했다 — {body}"


class TestNormalizeMustBeUsable:
    def test_a_zero_in_std_is_a_division_by_zero(self, compiler):
        code, body = _generate(compiler, [{"normalize": {"mean": [0, 0, 0],
                                                         "std": [1, 0, 1]}}])
        assert code == 400, f"std 의 0 이 통과했다 — 0 으로 나눈다. {body}"

    @pytest.mark.parametrize("std", ["많이", [1, "a", 1], 5.0, {"a": 1}])
    def test_std_must_be_a_list_of_numbers(self, compiler, std):
        code, body = _generate(compiler, [{"normalize": {"mean": [0, 0, 0], "std": std}}])
        assert code == 400, f"std={std!r} 가 통과했다 — {body}"

    def test_mean_and_std_must_describe_the_same_channels(self, compiler):
        code, body = _generate(compiler, [{"normalize": {"mean": [0, 0], "std": [1, 1, 1]}}])
        assert code == 400, f"길이가 다른 mean/std 가 통과했다 — {body}"

    @pytest.mark.parametrize("pair", [
        ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ([0.0, 0.0, 0.0], [1.0, 1.0, 1.0]),
        ([0.0], [255.0]),
        ([0, 0, 0], [255, 255, 255]),
    ])
    def test_documented_normalizations_pass(self, compiler, pair):
        """Combinations from the table at config-schema.md:140. All must pass."""
        mean, std = pair
        code, body = _generate(compiler, [{"normalize": {"mean": mean, "std": std}}])
        assert code == 200, f"문서에 있는 정규화를 막았다: {pair} — {body}"


class TestTheContainerItselfMustBeUsable:
    @pytest.mark.parametrize("value, why", [
        ({"resize": {"width": 640}}, "배열이 아니라 dict"),
        ("resize 640x640", "배열이 아니라 문자열"),
        (5, "배열이 아니라 숫자"),
        (["resize"], "원소가 dict 가 아님"),
        # The length-1 entries matter. Without the element type guard they pass
        # len(entry) != 1 and .items() raises AttributeError — a 500, not a 400.
        # A longer value such as "resize" (length 6) is caught by the next check
        # and would hide a missing guard.
        (["a"], "원소가 길이 1짜리 문자열"),
        ([["x"]], "원소가 길이 1짜리 리스트"),
        ([5], "원소가 숫자"),
        ([None], "원소가 None"),
        ([{"a": {}, "b": {}}], "원소에 transform 이 둘 — 순서를 알 수 없다"),
        ([{}], "빈 원소"),
        ([{"resize": 640}], "인자가 객체가 아님"),
    ])
    def test_a_malformed_container_is_refused(self, compiler, value, why):
        code, body = _generate(compiler, value)
        assert code == 400, f"{why}: 통과했다 — {body}"

    def test_an_absent_preprocessings_is_fine(self, compiler):
        """Compiling without preprocessing is valid."""
        payload = dict(OK)
        req = urllib.request.Request(
            compiler + "/config/generate", data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            assert r.status == 200


class TestTheOtherLoaderFields:
    """The other loader fields next to preprocessings get the same care."""

    @pytest.mark.parametrize("value, why", [
        ("jpg", "문자열 — dx_com 이 'j','p','g' 로 순회한다"),
        ([1, 2], "숫자 원소"),
        ([""], "빈 문자열"),
        (5, "배열이 아님"),
    ])
    def test_unusable_file_extensions_are_refused(self, compiler, value, why):
        code, body = _generate_field(compiler, {"file_extensions": value})
        assert code == 400, f"{why}: 통과했다 — {body}"

    def test_the_string_message_shows_the_exact_fix(self, compiler):
        code, body = _generate_field(compiler, {"file_extensions": "jpg"})
        assert "['jpg']" in body.get("error", ""), \
            f"무엇으로 고쳐야 하는지 보여주지 않는다 — {body}"

    def test_documented_file_extensions_pass(self, compiler):
        """The example from config-schema.md:126."""
        code, body = _generate_field(
            compiler, {"file_extensions": ["jpeg", "png", "jpg", "bmp"]})
        assert code == 200, body
        assert body["config"]["default_loader"]["file_extensions"] == \
            ["jpeg", "png", "jpg", "bmp"]

    @pytest.mark.parametrize("value", [5, ["/tmp"], {"p": "/tmp"}, True])
    def test_a_non_string_dataset_path_is_refused(self, compiler, value):
        code, body = _generate_field(compiler, {"dataset_path": value})
        assert code == 400, f"dataset_path={value!r} 가 저장됐다 — {body}"

    def test_a_boolean_calibration_num_is_refused(self, compiler):
        """bool is refused here as it is for input_shapes dimensions.
        int(True) is 1, so `true` would silently be stored as a sample count of 1."""
        code, body = _generate_field(compiler, {"calibration_num": True})
        assert code == 400, f"calibration_num=True 가 1 로 저장됐다 — {body}"


def _generate_field(base, extra):
    payload = {**OK, **extra}
    req = urllib.request.Request(
        base + "/config/generate", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

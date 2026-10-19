"""A 500 caused by a value the user sent is always a defect.

A 500 means "our fault". If the user sent a bad value, a 400 must say "that value
cannot be used". A 500 tells the user nothing and only leaves a stack trace in the
server log.

Each of these inputs must get a 400, not a 500:

    POST /compile          opt_level='abc'      unguarded int()
    POST /api/mkdir        300-character name   OSError(ENAMETOOLONG) must not leak
    POST /viewer/parse     path=12345           .strip() on a number
    POST /compile/resume   qxnn_path=5          same cause
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


def _post_json(base, path, payload):
    req = urllib.request.Request(
        base + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _post_form(base, path, fields):
    boundary = uuid.uuid4().hex
    body = "".join(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'
        for k, v in fields.items()) + f"--{boundary}--\r\n"
    req = urllib.request.Request(
        base + path, data=body.encode(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


_COMPILE_BASE = {
    "model_path": "/tmp/dx-probe.onnx",
    "config_path": "/tmp/dx-probe.json",
    "output_dir": "/tmp/dx-probe-out",
}


@pytest.mark.parametrize(
    "value, why",
    [
        ("abc", "숫자가 아닌 문자열"),
        ("1.5", "정수가 아닌 실수"),
        ("", "빈 값 — 빈 폼 필드로 실제 발생한다"),
    ],
)
def test_unparseable_opt_level_is_refused_not_a_crash(compiler, value, why):
    code, body = _post_form(compiler, "/compile", {**_COMPILE_BASE, "opt_level": value})
    assert code != 500, f"{why}: 사용자 입력이 서버를 터뜨렸다 — {body}"
    assert code == 400, f"{why}: 400 이어야 한다 — {code} {body}"


@pytest.mark.parametrize("value", ["-5", "999", "2"])
def test_opt_level_outside_the_documented_range_is_refused(compiler, value):
    """The docs fix opt_level to {0, 1} (02_06_Execution_of_DX-COM.md).

    It is a fixed enum, not something only the model knows, so this layer can decide.
    """
    code, body = _post_form(compiler, "/compile", {**_COMPILE_BASE, "opt_level": value})
    assert code == 400, f"opt_level={value} 가 통과했다 — {code} {body}"


@pytest.mark.parametrize("value", ["0", "1"])
def test_the_documented_opt_levels_still_pass(compiler, value):
    """No over-blocking — valid values must still pass."""
    code, _ = _post_form(compiler, "/compile", {**_COMPILE_BASE, "opt_level": value})
    assert code == 200, f"정상 opt_level={value} 를 막았다"


def test_an_unusable_directory_name_is_refused_not_a_crash(compiler):
    """fs_browse.make_directory promises to raise only ValueError.

    mkdir() raises OSError(ENAMETOOLONG) for a long name, and server.py catches only
    ValueError, so a leaked OSError would become a 500. The promise must hold.
    """
    code, body = _post_json(compiler, "/api/mkdir", {"path": "/tmp", "name": "x" * 300})
    assert code != 500, f"긴 이름이 서버를 터뜨렸다 — {body}"
    assert code == 400, f"400 이어야 한다 — {code} {body}"


@pytest.mark.parametrize("value", [12345, ["/tmp/a"], {"p": "/tmp/a"}, True])
def test_a_non_string_viewer_path_is_refused_not_a_crash(compiler, value):
    code, body = _post_json(compiler, "/viewer/parse", {"path": value})
    assert code != 500, f"path={value!r} 가 서버를 터뜨렸다 — {body}"
    assert code == 400, f"400 이어야 한다 — {code} {body}"


@pytest.mark.parametrize("value", [5, ["/tmp/a.qxnn"], {"p": 1}])
def test_a_non_string_qxnn_path_is_refused_not_a_crash(compiler, value):
    code, body = _post_json(
        compiler, "/compile/resume", {"qxnn_path": value, "output_dir": "/tmp/o"})
    assert code != 500, f"qxnn_path={value!r} 가 서버를 터뜨렸다 — {body}"
    assert code == 400, f"400 이어야 한다 — {code} {body}"

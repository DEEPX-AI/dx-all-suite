"""Compile paths may only be real files and folders inside the allowed roots.

`/compile` (model_path, config_path, output_dir) and `/compile/resume` hand these paths to
compiler_service, which reads them and writes outputs with mkdir, copyfile and replace. The
server may be reachable beyond localhost, so a request must not be able to point it anywhere.

Allowed roots: suite root, studio var/, the user's home, /media, /mnt, plus
DX_COMPILER_ALLOWED_ROOTS. Containment is checked by path components after resolve (not by
string prefix). Refusal happens before submit, any file read or mkdir.
"""
from __future__ import annotations

import importlib
import os

import pytest


def _pp():
    """path_policy as currently in sys.modules — another test (test_server) drops and re-imports dx_compiler,
    so the module and exception classes captured at collection may differ from what the service uses."""
    return importlib.import_module("dx_compiler.core.path_policy")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    """One allowed root (ws) and folders outside it (outside, and ws-evil which only shares the prefix)."""
    root = tmp_path / "ws"
    root.mkdir()
    (tmp_path / "ws-evil").mkdir()
    (tmp_path / "outside").mkdir()
    monkeypatch.setenv("DX_COMPILER_ALLOWED_ROOTS", str(root))
    monkeypatch.setattr(_pp(), "_default_roots", lambda: [])   # so home / suite roots do not cover tmp
    return root


def _file(p, text="x"):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


# ── Reads ─────────────────────────────────────────────────────────────────────

def test_a_file_inside_an_allowed_root_is_accepted_and_resolved(ws):
    m = _file(ws / "models" / "a.onnx")
    assert _pp().check_input_file(str(ws / "models" / ".." / "models" / "a.onnx"), "model_path") == m.resolve()


@pytest.mark.parametrize("where", ["dotdot", "prefix_sibling", "absolute_outside"])
def test_a_file_outside_is_refused(ws, where):
    outside = _file(ws.parent / "outside" / "a.onnx")
    sibling = _file(ws.parent / "ws-evil" / "a.onnx")
    raw = {"dotdot": str(ws / ".." / "outside" / "a.onnx"),
           "prefix_sibling": str(sibling),          # as a string, '/…/ws-evil' starts with '/…/ws'
           "absolute_outside": str(outside)}[where]
    with pytest.raises(_pp().PathPolicyError) as e:
        _pp().check_input_file(raw, "model_path")
    assert str(ws.parent) not in str(e.value), "오류에 서버 경로를 넣지 않는다"


def test_a_symlink_inside_that_points_outside_is_refused(ws):
    target = _file(ws.parent / "outside" / "secret.onnx")
    link = ws / "link.onnx"
    link.symlink_to(target)
    with pytest.raises(_pp().PathPolicyError):
        _pp().check_input_file(str(link), "model_path")


@pytest.mark.parametrize("kind", ["missing", "directory"])
def test_an_input_must_be_an_existing_regular_file(ws, kind):
    (ws / "d").mkdir()
    raw = str(ws / ("nope.onnx" if kind == "missing" else "d"))
    with pytest.raises(_pp().PathPolicyError):
        _pp().check_input_file(raw, "model_path")


def test_a_dataset_is_an_existing_directory_inside(ws):
    (ws / "calib").mkdir()
    assert _pp().check_input_dir(str(ws / "calib"), "dataset_path") == (ws / "calib").resolve()
    with pytest.raises(_pp().PathPolicyError):
        _pp().check_input_dir(str(ws.parent / "outside"), "dataset_path")


# ── Writes ────────────────────────────────────────────────────────────────────

def test_an_output_dir_that_does_not_exist_yet_is_checked_at_its_nearest_parent(ws):
    out = _pp().check_output_dir(str(ws / "out" / "run1"))
    assert out == (ws / "out" / "run1").resolve()
    assert not (ws / "out").exists(), "검사는 폴더를 만들지 않는다"


@pytest.mark.parametrize("where", ["outside", "prefix_sibling", "symlink_escape", "is_a_file"])
def test_an_output_dir_outside_or_odd_is_refused(ws, where):
    (ws / "esc").symlink_to(ws.parent / "outside", target_is_directory=True)
    _file(ws / "a.onnx")
    raw = {"outside": str(ws.parent / "outside" / "o"),
           "prefix_sibling": str(ws.parent / "ws-evil" / "o"),
           "symlink_escape": str(ws / "esc" / "o"),
           "is_a_file": str(ws / "a.onnx")}[where]
    with pytest.raises(_pp().PathPolicyError):
        _pp().check_output_dir(raw)
    assert not (ws.parent / "outside" / "o").exists()


def test_an_output_dir_cannot_be_another_jobs_folder(ws, monkeypatch):
    jobs = ws / "var" / "compiler" / "jobs"
    (jobs / "other-job" / "work").mkdir(parents=True)
    monkeypatch.setattr(_pp(), "_jobs_root", lambda: jobs)
    with pytest.raises(_pp().PathPolicyError):
        _pp().check_output_dir(str(jobs / "other-job" / "work"))


def test_publishing_never_overwrites_an_input(ws):
    q = _file(ws / "m.qxnn")
    assert _pp().would_overwrite_input(ws / "m.qxnn", [str(q)])
    assert not _pp().would_overwrite_input(ws / "m2.qxnn", [str(q)])


# ── Entry points ──────────────────────────────────────────────────────────────

def test_the_service_refuses_before_creating_a_job(ws):
    from dx_compiler.core.compiler_service import CompilerService
    svc = CompilerService()
    _file(ws.parent / "outside" / "a.onnx")
    _file(ws / "a.json", "{}")
    with pytest.raises(_pp().PathPolicyError):
        svc.submit(model_path=str(ws.parent / "outside" / "a.onnx"),
                   config_path=str(ws / "a.json"), output_dir=str(ws / "o"))
    _file(ws / "calib-config.json", '{"default_loader": {"dataset_path": "%s"}}' % (ws.parent / "outside"))
    _file(ws / "a.onnx")
    with pytest.raises(_pp().PathPolicyError):
        svc.submit(model_path=str(ws / "a.onnx"), config_path=str(ws / "calib-config.json"),
                   output_dir=str(ws / "o"))
    with pytest.raises(_pp().PathPolicyError):
        svc.submit_resume(qxnn_path=str(ws.parent / "outside" / "a.qxnn"),
                          output_dir=str(ws / "o"), recalibration_method="minmax")
    assert len(svc.jobs) == 0
    assert not (ws / "o").exists()


def test_the_http_routes_refuse_before_submit_and_touch_nothing_outside(ws, monkeypatch):
    import json
    import urllib.error
    import urllib.request
    import uuid

    import sys
    from tests.server_helpers import start_module_server

    victim = _file(ws.parent / "outside" / "victim.txt", "keep")
    mtime = os.stat(victim).st_mtime_ns
    calls = []
    _file(ws / "a.onnx")
    _file(ws / "a.json", "{}")

    server, port = start_module_server("dx_compiler")
    base = f"http://127.0.0.1:{port}"
    srv_mod = next(m for name, m in sys.modules.items()
                   if name.endswith("server") and hasattr(m, "compiler_service") and hasattr(m, "path_policy"))

    class _Job:
        job_id = "j1"
    monkeypatch.setattr(srv_mod.compiler_service, "submit", lambda **kw: calls.append(kw) or _Job())
    monkeypatch.setattr(srv_mod.compiler_service, "submit_resume", lambda **kw: calls.append(kw) or _Job())

    def form(fields):
        b = uuid.uuid4().hex
        body = "".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'
                       for k, v in fields.items()) + f"--{b}--\r\n"
        return urllib.request.Request(base + "/compile", data=body.encode(),
                                      headers={"Content-Type": f"multipart/form-data; boundary={b}"})

    def code(req):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()

    try:
        good = {"model_path": str(ws / "a.onnx"), "config_path": str(ws / "a.json"), "output_dir": str(ws / "o")}
        bad = [
            {**good, "model_path": str(ws.parent / "outside" / "victim.txt")},
            {**good, "config_path": str(ws / ".." / "outside" / "victim.txt")},
            {**good, "output_dir": str(ws.parent / "outside")},
        ]
        for fields in bad:
            c, body = code(form(fields))
            assert c in (400, 403), (fields, c)
            assert str(ws.parent) not in body
        c, body = code(urllib.request.Request(
            base + "/compile/resume", headers={"Content-Type": "application/json"},
            data=json.dumps({"qxnn_path": str(ws.parent / "outside" / "x.qxnn"),
                             "output_dir": str(ws / "o"), "recalibration_method": "minmax"}).encode()))
        assert c in (400, 403), c
        assert calls == [], "거부는 submit 전에"
        assert os.stat(victim).st_mtime_ns == mtime and victim.read_text() == "keep"
        c, _ = code(form(good))
        assert c == 200 and len(calls) == 1, "정상 요청은 그대로 통과"
    finally:
        server.shutdown()


# ── Relative dataset_path in the sample config ───────────────────────────────────

def _sdk_sample(ws, dataset="./calibration_dataset"):
    """The SDK sample layout: dx_com/sample_models/{onnx,json}/ + dx_com/calibration_dataset/.
    The sample config's dataset_path is relative, assuming dxcom runs from dx_com/."""
    com = ws / "dx_com"
    model = _file(com / "sample_models" / "onnx" / "m.onnx")
    cfg = _file(com / "sample_models" / "json" / "m.json",
                '{"inputs": {"x": [1, 3, 8, 8]}, "default_loader": {"dataset_path": "%s"}}' % dataset)
    _file(com / "calibration_dataset" / "0.jpeg")
    return model, cfg, com / "calibration_dataset"


def test_a_sample_config_with_a_relative_dataset_compiles_from_a_resolved_copy(ws, monkeypatch):
    """Setup → "use sample" puts the SDK sample config in the form. Its "./calibration_dataset"
    must be resolved the way the SDK examples run it, not against the studio's own folder (where
    it does not exist and /compile would answer 500), and dxcom gets a copy of the config with
    that absolute path."""
    import json
    from dx_compiler.core import compiler_service as cs

    started = []

    class _Thread:
        def __init__(self, target, args, daemon):
            started.append(args)

        def start(self):
            pass

    monkeypatch.setattr(cs.threading, "Thread", _Thread)
    model, cfg, dataset = _sdk_sample(ws)
    original = cfg.read_text()

    job = cs.CompilerService().submit(model_path=str(model), config_path=str(cfg), output_dir=str(ws / "o"))

    used = started[0][2]
    assert used != str(cfg)
    assert json.loads(open(used).read())["default_loader"]["dataset_path"] == str(dataset.resolve())
    assert json.loads(open(used).read())["inputs"] == {"x": [1, 3, 8, 8]}
    assert cfg.read_text() == original, "the user's config is never rewritten"
    assert job.config_path == used


def test_a_missing_dataset_in_the_config_is_a_400_not_a_500(ws):
    import urllib.error
    import urllib.request
    import uuid
    from tests.server_helpers import start_module_server

    model, cfg, _ = _sdk_sample(ws, dataset="./no_such_dataset")
    server, port = start_module_server("dx_compiler")
    b = uuid.uuid4().hex
    fields = {"model_path": str(model), "config_path": str(cfg), "output_dir": str(ws / "o")}
    body = "".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'
                   for k, v in fields.items()) + f"--{b}--\r\n"
    req = urllib.request.Request(f"http://127.0.0.1:{port}/compile", data=body.encode(),
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        with pytest.raises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(req, timeout=20)
        assert e.value.code == 400
        assert "dataset_path" in e.value.read().decode()
    finally:
        server.shutdown()

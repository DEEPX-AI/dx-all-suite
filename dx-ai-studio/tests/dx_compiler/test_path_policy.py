"""compile 경로는 허용된 폴더 안의 실제 파일 · 폴더만 (QA COM-A2, 2026-10-01).

`/compile` 은 model_path · config_path · output_dir 를 필수값인지만 보고 compiler_service.submit 에 넘겼고,
`/compile/resume` 은 타입만 봤다. 산출물은 요청이 준 폴더에 mkdir · copyfile · replace 됐다. 2026-09-18 에는
"서버를 localhost 밖에 노출하지 않는다" 는 전제로 일부러 검사하지 않았지만 (config.is_safe_path 주석), 기본 bind 가
모든 인터페이스라 전제가 성립하지 않았다 (COM-A1).

허용 루트: suite root · studio var/ · 사용자 홈 · /media · /mnt + DX_COMPILER_ALLOWED_ROOTS. resolve 후 경로
구성요소로 포함을 본다 (문자열 접두어 아님). 거부는 submit · 파일 읽기 · mkdir 전에.

spec: docs/superpowers/specs/2026-10-01-studio-remote-auth-and-compile-paths-design.md (D)
"""
from __future__ import annotations

import importlib
import os

import pytest


def _pp():
    """지금 sys.modules 의 path_policy — 다른 시험 (test_server) 이 dx_compiler 를 지우고 다시 import 하므로
    collection 때 잡은 모듈 · 예외 클래스는 서비스가 쓰는 것과 다를 수 있다."""
    return importlib.import_module("dx_compiler.core.path_policy")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    """허용 루트 하나 (ws) 와 그 밖 (outside · 접두어만 같은 ws-evil)."""
    root = tmp_path / "ws"
    root.mkdir()
    (tmp_path / "ws-evil").mkdir()
    (tmp_path / "outside").mkdir()
    monkeypatch.setenv("DX_COMPILER_ALLOWED_ROOTS", str(root))
    monkeypatch.setattr(_pp(), "_default_roots", lambda: [])   # 홈 · suite 가 tmp 를 덮지 않게
    return root


def _file(p, text="x"):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


# ── 읽기 ──────────────────────────────────────────────────────────────────────

def test_a_file_inside_an_allowed_root_is_accepted_and_resolved(ws):
    m = _file(ws / "models" / "a.onnx")
    assert _pp().check_input_file(str(ws / "models" / ".." / "models" / "a.onnx"), "model_path") == m.resolve()


@pytest.mark.parametrize("where", ["dotdot", "prefix_sibling", "absolute_outside"])
def test_a_file_outside_is_refused(ws, where):
    outside = _file(ws.parent / "outside" / "a.onnx")
    sibling = _file(ws.parent / "ws-evil" / "a.onnx")
    raw = {"dotdot": str(ws / ".." / "outside" / "a.onnx"),
           "prefix_sibling": str(sibling),          # '/…/ws-evil' 은 문자열로는 '/…/ws' 로 시작한다
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


# ── 쓰기 ──────────────────────────────────────────────────────────────────────

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


# ── 진입점 ────────────────────────────────────────────────────────────────────

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


# ── 샘플 config 의 상대 dataset_path ─────────────────────────────────────────────

def _sdk_sample(ws, dataset="./calibration_dataset"):
    """SDK 의 샘플 모양: dx_com/sample_models/{onnx,json}/ + dx_com/calibration_dataset/.
    샘플 config 의 dataset_path 는 dx_com/ 에서 dxcom 을 돌린다는 전제의 상대 경로다."""
    com = ws / "dx_com"
    model = _file(com / "sample_models" / "onnx" / "m.onnx")
    cfg = _file(com / "sample_models" / "json" / "m.json",
                '{"inputs": {"x": [1, 3, 8, 8]}, "default_loader": {"dataset_path": "%s"}}' % dataset)
    _file(com / "calibration_dataset" / "0.jpeg")
    return model, cfg, com / "calibration_dataset"


def test_a_sample_config_with_a_relative_dataset_compiles_from_a_resolved_copy(ws, monkeypatch):
    """Setup → "use sample" puts the SDK sample config in the form. Its "./calibration_dataset"
    was resolved against the studio's own folder: the check said it does not exist and /compile
    answered 500 — the sample compile never started. It is now resolved like the SDK examples
    run it, and dxcom gets a copy of the config with that absolute path."""
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

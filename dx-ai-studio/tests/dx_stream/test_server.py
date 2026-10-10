"""DX Stream server.py 통합 테스트.

테스트 포트 18093 사용 — 실제 서버 포트(8093)와 충돌 방지.
"""
import json
import http.client
import os
import sys
import threading
import time
from types import SimpleNamespace

import pytest
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))

TEST_PORT = 18093
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


@pytest.fixture(scope="module")
def server():
    from server import create_server
    httpd = create_server(port=TEST_PORT)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)
    yield httpd
    httpd.shutdown()
    httpd.server_close()


def _get(path: str) -> bytes:
    """GET 요청 헬퍼."""
    return urlopen(f"{BASE_URL}{path}", timeout=5).read()


def _get_json(path: str):
    """GET 요청 → JSON 파싱."""
    return json.loads(_get(path))


def _post_json(path: str, body: dict):
    """POST JSON body → 응답 dict"""
    import urllib.request
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{path}", data=data,
        headers={"Content-Type": "application/json"},
        method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=5).read())


# ── 테스트 ────────────────────────────────────────────────────


def test_get_root_returns_html(server):
    """GET / 는 200 + HTML을 반환해야 한다."""
    resp = urlopen(f"{BASE_URL}/", timeout=5)
    assert resp.status == 200
    body = resp.read().decode()
    assert "<html>" in body.lower() or "<!doctype html>" in body.lower()


def test_index_html_returns_html(server):
    resp = urlopen(f"{BASE_URL}/index.html", timeout=5)
    assert resp.status == 200
    body = resp.read().decode()
    assert "<html>" in body.lower() or "<!doctype html>" in body.lower()
    assert "DX Stream" in body


def test_api_status_returns_json(server):
    """GET /api/status 는 npu, gstreamer, models 키를 포함해야 한다."""
    data = _get_json("/api/status")
    assert "npu" in data
    assert "gstreamer" in data
    assert "models" in data


def test_api_demos_returns_list(server):
    """GET /api/demos 는 dev-backed 12개 데모 목록을 반환해야 한다."""
    data = _get_json("/api/demos")
    assert isinstance(data, list)
    assert len(data) == 12


def test_api_models_returns_catalog_object(server):
    """GET /api/models 는 카탈로그 객체를 반환해야 한다."""
    data = _get_json("/api/models")
    assert isinstance(data, dict)
    assert data["catalog_source"] in {"manifest", "fallback"}
    assert isinstance(data["models"], list)
    assert len(data["models"]) >= 1


def test_api_elements_returns_list(server):
    """GET /api/elements 는 13개 이상 엘리먼트를 반환해야 한다."""
    data = _get_json("/api/elements")
    assert isinstance(data, list)
    assert len(data) >= 13


def test_unknown_api_returns_404(server):
    """GET /api/nonexistent 는 404를 반환해야 한다."""
    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"{BASE_URL}/api/nonexistent", timeout=5)
    assert exc_info.value.code == 404


def test_static_css_served(server):
    """GET /static/css/stream.css 는 200 + Stream CSS를 반환해야 한다."""
    resp = urlopen(f"{BASE_URL}/static/css/stream.css", timeout=5)
    css = resp.read().decode()
    assert resp.status == 200
    assert "text/css" in resp.headers.get("Content-Type", "")
    assert "--stream-color" in css
    assert ".stream-badge" in css


def test_pipeline_iso_css_served(server):
    resp = urlopen(f"{BASE_URL}/static/css/pipeline-iso.css", timeout=5)
    css = resp.read().decode()
    assert resp.status == 200
    assert "text/css" in resp.headers.get("Content-Type", "")
    assert ".pipeline-builder" in css
    assert ".palette-panel" in css


def test_shared_foundation_css_served(server):
    css = _get("/static/shared/dx-fonts.css").decode()
    assert "/static/shared/fonts/inter-4.1-var-latin.woff2" in css


def test_shared_font_served(server):
    data = _get("/static/shared/fonts/inter-4.1-var-latin.woff2")
    assert data
    assert data[:4] == b"wOF2"


def test_api_setup_log_returns_json(server):
    data = _get_json("/api/setup/log")
    assert "log" in data
    assert "done" in data


def test_api_setup_status_returns_dict(server):
    data = _get_json("/api/setup/status")
    assert isinstance(data, dict)
    assert "build" in data


def test_tutorial_tags_in_html(server):
    """index.html에 tutorial 관련 3개 태그가 존재하는지 확인."""
    resp = urlopen(f"{BASE_URL}/", timeout=5)
    html = resp.read().decode()
    assert 'tutorial-engine.js' in html, "tutorial-engine.js 태그 누락"
    assert 'tutorial.js' in html, "tutorial.js 태그 누락"
    assert 'tutorial.css' in html, "tutorial.css 태그 누락"


def test_api_pipeline_status(server):
    """GET /api/pipeline/status 는 running 필드를 반환해야 한다."""
    data = _get_json("/api/pipeline/status")
    assert "running" in data
    assert data["running"] is False


def test_post_without_body_handler_drains_keepalive_body(server):
    """body를 쓰지 않는 POST 핸들러도 keep-alive 요청 본문을 소비해야 한다."""
    conn = http.client.HTTPConnection("127.0.0.1", TEST_PORT, timeout=5)
    try:
        conn.request(
            "POST",
            "/api/setup/stop",
            body=b"{}",
            headers={"Content-Type": "application/json", "Content-Length": "2"},
        )
        first = conn.getresponse()
        first.read()
        assert first.status == 200

        conn.request("GET", "/api/pipeline/status")
        second = conn.getresponse()
        body = second.read().decode()
    finally:
        conn.close()

    assert second.status == 200
    assert json.loads(body)["running"] is False


def test_api_pipeline_elements_wrapped(server):
    """API 응답이 categories + connection_rules를 포함하는지 확인"""
    data = _get_json("/api/pipeline/elements")
    assert "categories" in data
    assert "connection_rules" in data
    assert "element_overrides" in data
    assert "semantic_warnings" in data
    assert "auto_converter_rules" in data
    assert isinstance(data["categories"], dict)
    assert "source" in data["categories"]

def test_api_pipeline_validate_connection(server):
    """서버사이드 연결 검증"""
    data = _post_json("/api/pipeline/validate-connection",
                      {"from_elem": "urisourcebin", "to_elem": "DxPreprocess"})
    assert data["result"] == "allow"

def test_api_pipeline_validate_connection_block(server):
    data = _post_json("/api/pipeline/validate-connection",
                      {"from_elem": "fpsdisplaysink", "to_elem": "DxInfer"})
    assert data["result"] == "block"


def test_api_models_returns_catalog_source(server):
    data = _get_json("/api/models")
    assert isinstance(data, dict)
    assert data["catalog_source"] in {"manifest", "fallback"}
    assert isinstance(data["models"], list)


def test_stream_server_exposes_model_upload_route():
    source = (
        Path(__file__).resolve().parent.parent.parent
        / "dx_stream"
        / "server.py"
    ).read_text(encoding="utf-8")
    assert 'path == "/api/models/upload"' in source


def test_plugin_preflight_uses_request_node_types_not_rendered_pipeline():
    source = (
        Path(__file__).resolve().parent.parent.parent
        / "dx_stream"
        / "server.py"
    ).read_text(encoding="utf-8")
    assert "_deepx_element_types" in source


def test_demo_start_returns_contract_failure_before_pipeline_creation(monkeypatch):
    import server as server_mod
    from shared.runtime_contract import ContractResult
    from shared.runtime_profile import ContractCheck

    failed = ContractResult((ContractCheck(
        check_id="profile.active",
        required="active runtime profile",
        observed="missing",
        passed=False,
        remediation="Complete Runtime Setup.",
    ),))
    monkeypatch.setattr(server_mod, "_stream_launch_contract", lambda _demo: (failed, None))
    monkeypatch.setattr(server_mod, "_pipeline_mgr", object())
    handler, sent = _pipeline_handler(server_mod, {})

    handler._handle_demo_start("/api/demos/0/start")

    assert sent["code"] == 424
    assert sent["payload"]["error"] == "contract_failed"
    assert "profile.active" in sent["payload"]["message"]
    assert "profile.active" not in sent["payload"]["detail"], "check id 는 message 에 한 번만 (release audit S-7)"


def test_demo_start_returns_sanitized_structured_launch_error(monkeypatch):
    import server as server_mod
    from dx_stream.core import mjpeg
    from shared.runtime_contract import ContractResult

    runtime_context = SimpleNamespace(python_executable=Path("/runtime/infer/bin/python3"))
    stops = []
    monkeypatch.setattr(
        server_mod,
        "_stream_launch_contract",
        lambda _demo: (ContractResult(()), runtime_context),
    )
    monkeypatch.setattr(server_mod, "validate_stream_pipeline", lambda *_a, **_kw: ContractResult(()))
    monkeypatch.setattr(server_mod, "build_child_environment", lambda _context: {})
    monkeypatch.setattr(server_mod, "detect_encoder", lambda: {})
    monkeypatch.setattr(server_mod, "_pipeline_mgr", object())
    monkeypatch.setattr(server_mod, "_stop_all_playback", lambda: stops.append("stop"))
    monkeypatch.setattr(server_mod, "_check_webrtc_available", lambda: True)
    monkeypatch.setattr(server_mod, "_try_start_webrtc_pipeline", lambda *_a, **_kw: None)
    monkeypatch.setattr(server_mod.demos, "build_pipeline_str", lambda *_a, **_kw: "videotestsrc ! fakesink")
    monkeypatch.setattr(mjpeg, "build_mjpeg_pipeline", lambda pipeline: pipeline)
    monkeypatch.setattr(mjpeg, "start", lambda *_a, **_kw: None)
    monkeypatch.setattr(mjpeg, "wait_until_ready", lambda **_kw: (False, "Traceback: backend secret"))
    monkeypatch.setattr(mjpeg, "stop", lambda: None)
    handler, sent = _pipeline_handler(server_mod, {})

    handler._handle_demo_start("/api/demos/0/start")

    assert stops == ["stop"]
    assert sent["code"] == 500
    assert sent["payload"]["error"] == "pipeline_error"
    assert isinstance(sent["payload"]["message"], str)
    assert isinstance(sent["payload"]["detail"], str)
    assert sent["payload"]["attempted_modes"] == ["webrtc", "mjpeg"]
    assert sent["payload"]["remediation"]
    assert sent["payload"]["playback_active"] is False
    assert "Traceback" not in sent["payload"]["detail"]


def test_pipeline_run_returns_contract_failure_before_conversion(monkeypatch):
    import server as server_mod
    from shared.runtime_contract import ContractResult
    from shared.runtime_profile import ContractCheck

    failed = ContractResult((ContractCheck(
        check_id="profile.active",
        required="active runtime profile",
        observed="missing",
        passed=False,
        remediation="Complete Runtime Setup.",
    ),))
    monkeypatch.setattr(server_mod, "_active_stream_context", lambda: (failed, None))
    monkeypatch.setattr(server_mod, "_pipeline_mgr", object())
    handler, sent = _pipeline_handler(server_mod, {"nodes": [], "edges": []})

    handler._handle_pipeline_run()

    assert sent["code"] == 424
    assert sent["payload"]["error"] == "contract_failed"
    assert "profile.active" in sent["payload"]["message"]
    assert "profile.active" not in sent["payload"]["detail"], "check id 는 message 에 한 번만 (release audit S-7)"


def _pipeline_handler(server_mod, body):
    sent = {}
    handler = object.__new__(server_mod.DXStreamHandler)
    handler._safe_read_json = lambda: body
    handler.send_json = lambda payload, code=200: sent.update(
        payload=payload, code=code
    )
    def capture_error(code, error, message, detail=""):
        payload = {"error": error, "message": message}
        if detail:
            payload["detail"] = detail
        sent.update(payload=payload, code=code)
    handler._error = capture_error
    return handler, sent


def _allow_active_stream_context(monkeypatch, server_mod):
    from shared.runtime_contract import ContractResult

    context = SimpleNamespace(
        python_executable=Path("/runtime/infer/bin/python3"),
        venv_root=Path("/runtime/infer"),
        library_dirs=(Path("/runtime/lib"),),
        plugin_dir=Path("/runtime/gst"),
        postprocess_lib_dir=Path("/runtime/postprocess"),
    )
    monkeypatch.setattr(server_mod, "_active_stream_context", lambda: (ContractResult(()), context))
    monkeypatch.setattr(
        server_mod,
        "validate_stream_pipeline",
        lambda *_args, **_kwargs: ContractResult(()),
    )


def test_pipeline_run_returns_424_for_dx_node_when_plugin_is_missing(monkeypatch):
    import server as server_mod

    _allow_active_stream_context(monkeypatch, server_mod)
    monkeypatch.setattr(server_mod, "_pipeline_mgr", object())
    monkeypatch.setattr(server_mod, "pipeline_json_to_gst", lambda _body: "dxinfer")
    monkeypatch.setattr(server_mod.gst_env, "plugin_available", lambda: False)
    handler, sent = _pipeline_handler(
        server_mod,
        {"nodes": [{"id": "infer", "type": "DxInfer", "props": {}}], "edges": []},
    )

    handler._handle_pipeline_run()

    assert sent["code"] == 424
    assert sent["payload"]["error"] == "missing_dxstream_plugin"


def test_pipeline_run_does_not_preflight_property_value_as_dx_element(monkeypatch):
    import sys
    import dx_stream.core as stream_core
    import server as server_mod

    _allow_active_stream_context(monkeypatch, server_mod)

    class FakePipelineManager:
        def stop(self):
            return None

    class FakeMjpeg:
        def stop(self):
            return None

        def start(self, _pipeline, extra_env=None):
            return None

        def wait_until_ready(self, timeout=5.0, require_frame=True):
            return True, ""

        def get_sink_str(self):
            return "jpegenc ! fdsink fd=1"

        def build_mjpeg_pipeline(self, pipeline):
            return pipeline

    fake_mjpeg = FakeMjpeg()
    fake_module = type(sys)("fake_mjpeg_for_preflight")
    fake_module.stop = fake_mjpeg.stop
    fake_module.start = fake_mjpeg.start
    fake_module.wait_until_ready = fake_mjpeg.wait_until_ready
    fake_module.get_sink_str = fake_mjpeg.get_sink_str
    fake_module.build_mjpeg_pipeline = fake_mjpeg.build_mjpeg_pipeline
    monkeypatch.setitem(sys.modules, "dx_stream.core.mjpeg", fake_module)
    monkeypatch.setattr(stream_core, "mjpeg", fake_module)
    monkeypatch.setattr(server_mod, "_pipeline_mgr", FakePipelineManager())
    monkeypatch.setattr(server_mod, "_webrtc_handler", None)
    monkeypatch.setattr(
        server_mod,
        "pipeline_json_to_gst",
        lambda _body: "videotestsrc location=model.dxnn ! fakesink",
    )
    monkeypatch.setattr(server_mod.gst_env, "plugin_available", lambda: False)
    handler, sent = _pipeline_handler(
        server_mod,
        {
            "nodes": [
                {
                    "id": "source",
                    "type": "videotestsrc",
                    "props": {"location": "model.dxnn"},
                }
            ],
            "edges": [],
        },
    )

    handler._handle_pipeline_run()

    assert sent["code"] == 200
    assert sent["payload"]["output_mode"] == "mjpeg"


class _MemoryModelFile:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def exists(self):
        return self.name in self.parent.files

    def write_bytes(self, data):
        self.parent.files[self.name] = data
        return len(data)


class _MemoryModelsDir:
    def __init__(self):
        self.files = {}

    def __truediv__(self, name):
        return _MemoryModelFile(self, name)

    def mkdir(self, **_kwargs):
        return None


def _model_upload_handler(server_mod, filename, data):
    sent = {}
    handler = object.__new__(server_mod.DXStreamHandler)
    handler.parse_multipart = lambda: ({}, {"model": {"filename": filename, "data": data}})
    handler.send_json = lambda payload, code=200: sent.update(
        payload=payload, code=code
    )
    handler._error = lambda code, error, message, detail="": sent.update(
        payload={"error": error, "message": message}, code=code
    )
    return handler, sent


def test_model_upload_accepts_dxnn_and_preserves_bytes(monkeypatch, tmp_path):
    from dx_stream.core import config as stream_config
    import server as server_mod

    models_dir = tmp_path / "models"
    monkeypatch.setattr(stream_config, "MODELS_DIR", models_dir)
    payload = b"\x00DXNN\xffbinary"
    handler, sent = _model_upload_handler(server_mod, "custom model.dxnn", payload)

    handler._handle_model_upload()

    assert sent["code"] == 200
    assert sent["payload"] == {"uploaded": True, "name": "custom_model.dxnn"}
    assert (models_dir / "custom_model.dxnn").read_bytes() == payload


def test_model_upload_rejects_non_dxnn_name(monkeypatch):
    from dx_stream.core import config as stream_config
    import server as server_mod

    monkeypatch.setattr(stream_config, "MODELS_DIR", _MemoryModelsDir())
    handler, sent = _model_upload_handler(server_mod, "custom-model.onnx", b"model")

    handler._handle_model_upload()

    assert sent["code"] == 400
    assert sent["payload"]["error"] == "bad_request"


def test_model_upload_rejects_duplicate_sanitized_name(monkeypatch, tmp_path):
    from dx_stream.core import config as stream_config
    import server as server_mod

    models_dir = tmp_path / "models"
    models_dir.mkdir()
    (models_dir / "custom_model.dxnn").write_bytes(b"original")
    monkeypatch.setattr(stream_config, "MODELS_DIR", models_dir)
    handler, sent = _model_upload_handler(server_mod, "custom model.dxnn", b"new")

    handler._handle_model_upload()

    assert sent["code"] == 409
    assert sent["payload"]["error"] == "conflict"
    assert (models_dir / "custom_model.dxnn").read_bytes() == b"original"


def test_model_upload_preserves_race_winner_with_atomic_no_replace_publish(
    monkeypatch, tmp_path
):
    """A file created after validation must not be overwritten by this upload."""
    from dx_stream.core import config as stream_config
    import server as server_mod

    models_dir = tmp_path / "models"
    models_dir.mkdir()
    target = models_dir / "race.dxnn"
    winner = b"concurrent writer"
    original_exists = Path.exists
    original_link = os.link

    def publish_race_winner():
        if not original_exists(target):
            target.write_bytes(winner)

    def exists_then_race(path):
        if path == target:
            publish_race_winner()
            return False
        return original_exists(path)

    def link_then_race(source, destination, *args, **kwargs):
        if Path(destination) == target:
            publish_race_winner()
        return original_link(source, destination, *args, **kwargs)

    monkeypatch.setattr(stream_config, "MODELS_DIR", models_dir)
    monkeypatch.setattr(Path, "exists", exists_then_race)
    monkeypatch.setattr(server_mod.os, "link", link_then_race)
    handler, sent = _model_upload_handler(server_mod, "race.dxnn", b"losing upload")

    handler._handle_model_upload()

    assert sent["code"] == 409
    assert sent["payload"]["error"] == "conflict"
    assert target.read_bytes() == winner
    assert not list(models_dir.glob(".upload-*"))


# ── Route contracts: pipeline CRUD, custom-library, diagnostics ─────────────
#
# These cover the GET/POST routes the suite never exercised. Every filesystem
# root is redirected into tmp_path first: PIPELINES_DIR points at the REAL
# dx-runtime/dx_stream/dx_stream/pipelines tree, so an unredirected save would
# drop test JSON next to the shipped run_*.sh scripts.


def _request(method: str, path: str, body=None):
    """Return (status, payload) — including for 4xx, which urlopen raises on."""
    import urllib.request

    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data,
                                 headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        raw = resp.read()
        return resp.status, (json.loads(raw) if raw else None)
    except HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw.decode(errors="replace")


def _post_raw(path: str, raw: bytes, content_type="application/json"):
    import urllib.request

    req = urllib.request.Request(f"{BASE_URL}{path}", data=raw,
                                 headers={"Content-Type": content_type}, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status, json.loads(resp.read())
    except HTTPError as e:
        return e.code, json.loads(e.read())


# Names that must never reach the filesystem as a pipeline/library identifier.
BAD_NAMES = ["", ".", "..", ".hidden", "a/b", "../escape", "/abs"]


@pytest.fixture()
def pipelines_dir(tmp_path, monkeypatch):
    """Redirect PIPELINES_DIR away from the real dx-runtime tree."""
    from dx_stream.core import config as stream_config

    d = tmp_path / "pipelines"
    d.mkdir()
    monkeypatch.setattr(stream_config, "PIPELINES_DIR", d)
    return d


class TestPipelineCrudRoutes:
    def test_save_list_load_delete_round_trip(self, server, pipelines_dir):
        payload = {"name": "mypipe", "nodes": [{"id": "src"}], "edges": []}
        status, saved = _request("POST", "/api/pipeline/save", payload)
        assert (status, saved["saved"], saved["name"]) == (200, True, "mypipe")
        assert (pipelines_dir / "mypipe.json").is_file()

        assert _request("GET", "/api/pipeline/list")[1] == ["mypipe"]

        status, loaded = _request("GET", "/api/pipeline/load/mypipe")
        assert status == 200 and loaded["nodes"] == [{"id": "src"}]

        status, deleted = _request("POST", "/api/pipeline/delete/mypipe")
        assert (status, deleted["deleted"]) == (200, True)
        assert not (pipelines_dir / "mypipe.json").exists()
        assert _request("GET", "/api/pipeline/list")[1] == []

    def test_list_is_sorted_and_only_reports_json_stems(self, server, pipelines_dir):
        for n in ("zeta", "alpha", "mid"):
            (pipelines_dir / f"{n}.json").write_text("{}")
        (pipelines_dir / "notes.txt").write_text("ignore me")
        assert _request("GET", "/api/pipeline/list")[1] == ["alpha", "mid", "zeta"]

    def test_load_missing_pipeline_is_404(self, server, pipelines_dir):
        status, body = _request("GET", "/api/pipeline/load/nope")
        assert status == 404 and body["error"] == "not_found"

    def test_delete_is_idempotent(self, server, pipelines_dir):
        """The UI fires delete optimistically; a second delete must not 500."""
        status, body = _request("POST", "/api/pipeline/delete/never-existed")
        assert (status, body["deleted"]) == (200, True)

    @pytest.mark.parametrize("bad", BAD_NAMES)
    def test_save_rejects_unsafe_names(self, server, pipelines_dir, bad):
        status, body = _request("POST", "/api/pipeline/save", {"name": bad, "nodes": []})
        assert status == 400 and body["error"] == "bad_request"
        assert list(pipelines_dir.iterdir()) == [], "a rejected save must write nothing"

    def test_save_rejects_whitespace_only_name(self, server, pipelines_dir):
        status, _ = _request("POST", "/api/pipeline/save", {"name": "   ", "nodes": []})
        assert status == 400
        assert list(pipelines_dir.iterdir()) == []

    def test_load_and_delete_reject_dotfile_names(self, server, pipelines_dir):
        (pipelines_dir / ".secret.json").write_text('{"x":1}')
        assert _request("GET", "/api/pipeline/load/.secret")[0] == 400
        assert _request("POST", "/api/pipeline/delete/.secret")[0] == 400
        assert (pipelines_dir / ".secret.json").is_file(), "guarded delete must not unlink"

    def test_url_encoded_traversal_does_not_escape(self, server, pipelines_dir, tmp_path):
        """%2F / %2E stay literal in the path, so they cannot rebuild a separator.
        Either a 400 or a 404 is acceptable — escaping the directory is not."""
        outside = tmp_path / "outside.json"
        outside.write_text('{"pwned": true}')
        status, _ = _request("GET", "/api/pipeline/load/..%2F..%2Foutside")
        assert status in (400, 404)
        assert outside.read_text() == '{"pwned": true}'

    def test_saved_payload_is_readable_json(self, server, pipelines_dir):
        _request("POST", "/api/pipeline/save", {"name": "p", "nodes": [], "meta": {"a": 1}})
        assert json.loads((pipelines_dir / "p.json").read_text())["meta"] == {"a": 1}


class TestMalformedBodies:
    def test_invalid_json_body_is_400_not_500(self, server, pipelines_dir):
        status, body = _post_raw("/api/pipeline/save", b"{not json")
        assert status == 400
        assert "JSON" in body["error"]
        assert list(pipelines_dir.iterdir()) == []

    def test_missing_name_field_is_400(self, server, pipelines_dir):
        status, body = _request("POST", "/api/pipeline/save", {"nodes": []})
        assert status == 400 and body["error"] == "bad_request"

    def test_error_envelope_is_inconsistent_for_malformed_json(self, server, pipelines_dir):
        """KNOWN DIVERGENCE, pinned so a fix is deliberate rather than accidental.

        Every guarded route answers {"error": "<machine code>", "message": "<sentence>"},
        but a body that fails to parse answers {"error": "Invalid JSON: <sentence>"} —
        `error` carries prose and there is no `message`. A client that switches on
        `error` (the studio's translatedError() does) cannot classify this one.

        Deliberately asserts the CURRENT shape. When the envelope is unified, this
        test fails and should be replaced by the bad_request assertion above.
        """
        _, parse_fail = _post_raw("/api/pipeline/save", b"{not json")
        _, guarded = _request("POST", "/api/pipeline/save", {"name": "../x"})

        assert set(guarded) == {"error", "message"}
        assert guarded["error"] == "bad_request"

        assert set(parse_fail) == {"error"}, "malformed-JSON replies carry no message key"
        assert parse_fail["error"].startswith("Invalid JSON")

    def test_empty_body_falls_through_to_field_validation(self, server, pipelines_dir):
        """An empty body parses to {}, so it fails on the missing name rather than
        as a parse error — a different path from the malformed case above."""
        status, body = _post_raw("/api/pipeline/save", b"")
        assert status == 400 and body["error"] == "bad_request"


class TestCustomLibraryRoutes:
    @pytest.fixture()
    def lib_roots(self, tmp_path, monkeypatch):
        from dx_stream.core import custom_library as CL

        src = tmp_path / "postprocess_library"
        inst = tmp_path / "installed"
        src.mkdir()
        inst.mkdir()
        monkeypatch.setattr(CL, "POSTPROC_LIB_DIR", src)
        monkeypatch.setattr(CL, "INSTALLED_SO_DIR", inst)
        return src, inst

    def test_list_reports_a_library_with_meson_build(self, server, lib_roots):
        src, _ = lib_roots
        (src / "mylib").mkdir()
        (src / "mylib" / "meson.build").write_text("project()")
        status, body = _request("GET", "/api/custom-library")
        assert status == 200
        assert [lib["name"] for lib in body] == ["mylib"]
        assert body[0]["built"] is False

    def test_available_so_lists_installed_shared_objects(self, server, lib_roots):
        _, inst = lib_roots
        (inst / "libpostprocess_x.so").write_bytes(b"1234")
        status, body = _request("GET", "/api/custom-library/available-so")
        assert status == 200
        assert [s["name"] for s in body] == ["libpostprocess_x.so"]
        assert body[0]["size"] == 4

    def test_build_log_shape(self, server):
        status, body = _request("GET", "/api/custom-library/build-log")
        assert status == 200 and set(body) == {"log", "done"}

    def test_upload_writes_decoded_sources(self, server, lib_roots):
        import base64

        src, _ = lib_roots
        status, body = _request("POST", "/api/custom-library/upload", {
            "name": "newlib",
            "files": {"postprocess.cpp": base64.b64encode(b"int main(){}").decode()},
        })
        assert status == 200 and body["name"] == "newlib"
        assert (src / "newlib" / "postprocess.cpp").read_text() == "int main(){}"

    @pytest.mark.parametrize("bad", ["../escape", "a/b", ".hidden", ".."])
    def test_upload_rejects_unsafe_library_names(self, server, lib_roots, bad):
        import base64

        src, _ = lib_roots
        status, body = _request("POST", "/api/custom-library/upload", {
            "name": bad, "files": {"a.c": base64.b64encode(b"x").decode()},
        })
        assert status == 400 and body["error"] == "bad_request"
        assert list(src.iterdir()) == []

    def test_upload_requires_name_and_files(self, server, lib_roots):
        assert _request("POST", "/api/custom-library/upload", {"files": {}})[0] == 400
        assert _request("POST", "/api/custom-library/upload", {"name": "x"})[0] == 400

    def test_binary_upload_is_rejected_with_a_readable_reason(self, server, lib_roots):
        """A .so dropped into the source uploader must not become mojibake on disk."""
        import base64

        status, body = _request("POST", "/api/custom-library/upload", {
            "name": "binlib",
            "files": {"blob.so": base64.b64encode(b"\x7fELF\x00\xff\xfe").decode()},
        })
        assert status == 400
        assert "text source" in body["message"]


class TestReadOnlyDiagnosticsRoutes:
    def test_diagnostics_returns_an_object(self, server):
        status, body = _request("GET", "/api/diagnostics")
        assert status == 200 and isinstance(body, dict)

    def test_stream_stats_reports_a_mode(self, server):
        status, body = _request("GET", "/api/stream/stats")
        assert status == 200 and isinstance(body, dict)
        assert "mode" in body or "streaming" in body

    def test_webrtc_ice_is_a_list_even_without_a_session(self, server):
        status, body = _request("GET", "/api/webrtc/ice")
        assert status == 200 and isinstance(body, list)


class TestModelMetadataRoute:
    @pytest.mark.parametrize("bad", ["..", ".hidden", ""])
    def test_rejects_unsafe_model_filenames(self, server, bad):
        """Must be rejected by the GUARD (400), not merely miss on disk (404).

        Asserting `status in (400, 404)` here would be useless: with the guard
        deleted, ".." resolves to a directory, is_file() is False, and the route
        answers 404 — the looser assertion passes against the broken code.
        """
        status, body = _request("GET", f"/api/models/{bad}/metadata")
        assert status == 400, f"{bad!r} must be rejected by the filename guard"
        assert body["error"] == "bad_request"
        assert body["message"] == "Invalid model filename"

    def test_extra_path_segments_cannot_walk_out(self, server, tmp_path, monkeypatch):
        """The URL is decoded before routing, so %2F becomes a real separator —
        but only ONE segment is ever used as the filename, which is what stops
        "a/../../etc" from reaching the filesystem as a path."""
        from dx_stream.core import config as stream_config

        monkeypatch.setattr(stream_config, "MODELS_DIR", tmp_path)
        for probe in ("a%2Fb", "sub/deep", "x/../../etc/passwd"):
            status, body = _request("GET", f"/api/models/{probe}/metadata")
            assert status == 404
            # Only the first segment survives — never a composed path.
            assert "/" not in body["message"].split(": ", 1)[1]

    def test_missing_model_is_404(self, server, tmp_path, monkeypatch):
        from dx_stream.core import config as stream_config

        monkeypatch.setattr(stream_config, "MODELS_DIR", tmp_path)
        status, body = _request("GET", "/api/models/absent.dxnn/metadata")
        assert status == 404 and body["error"] == "not_found"


class TestUnknownPostEndpoint:
    def test_unknown_post_route_is_404(self, server):
        status, body = _request("POST", "/api/definitely/not/a/route", {})
        assert status == 404 and body["error"] == "not_found"

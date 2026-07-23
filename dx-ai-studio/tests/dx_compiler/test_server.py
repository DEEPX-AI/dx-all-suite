"""DX Compiler server runtime tests."""
from __future__ import annotations

import importlib.util
import json
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_compiler_server_import_does_not_require_core_path(monkeypatch):
    """dx_compiler.server must be importable with only the project root on sys.path."""
    _clear_stale_modules()
    root = Path(__file__).resolve().parents[2]
    monkeypatch.syspath_prepend(str(root))
    import dx_compiler.server as server
    assert hasattr(server, "create_server")


def test_dx_compiler_create_server_returns_http_server():
    """create_server(port) returns a usable HTTP server with expected attributes."""
    _clear_stale_modules()
    _reset_sys_path()
    from dx_compiler.server import create_server
    srv = create_server(port=28095)
    try:
        assert hasattr(srv, "serve_forever")
        assert hasattr(srv, "shutdown")
        assert hasattr(srv, "server_close")
        host, port = srv.server_address
        assert port == 28095
    finally:
        srv.server_close()

COMPILER_DIR = ROOT / "dx_compiler"
TEST_PORT = 18095
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"

# 다른 테스트 conftest 훅(예: dx_stream)이 등록한 모듈과 충돌 방지용 프리픽스 목록
_STALE_MODULE_PREFIXES = ("core", "shared", "server", "dx_compiler_server_for_tests", "dx_compiler")


def _clear_stale_modules():
    """sys.modules에서 다른 앱이 남긴 core/shared/server 모듈을 제거한다."""
    for name in list(sys.modules):
        if any(
            name == prefix or name.startswith(prefix + ".")
            for prefix in _STALE_MODULE_PREFIXES
        ):
            del sys.modules[name]


def _reset_sys_path():
    """sys.path에서 COMPILER_DIR/ROOT 항목을 제거한 후 재삽입하여 결정적 순서를 보장한다.

    최종 순서: COMPILER_DIR(idx 0) → ROOT(idx 1) → 기존 항목들.
    TODO(Task 4.1): 모든 컴파일러 테스트가 package import만 사용하면 COMPILER_DIR 삽입을 제거한다.
    """
    root_str, compiler_str = str(ROOT), str(COMPILER_DIR)
    for p in (root_str, compiler_str):
        while p in sys.path:
            sys.path.remove(p)
    # COMPILER_DIR를 먼저 insert(0)하면 ROOT가 0으로 밀리므로 역순으로 삽입
    sys.path.insert(0, root_str)
    sys.path.insert(0, compiler_str)


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


# module-scoped fixture: 하나의 서버 인스턴스를 모든 테스트가 공유한다.
# 이 서버는 읽기 전용/안전한 라우트에만 사용되어야 한다 — 상태를 변경하는
# 요청은 별도의 function-scoped 서버를 사용할 것.
@pytest.fixture(scope="module")
def server():
    _clear_stale_modules()
    _reset_sys_path()

    spec = importlib.util.spec_from_file_location(
        "dx_compiler_server_for_tests", COMPILER_DIR / "server.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)

    _clear_stale_modules()
    spec.loader.exec_module(module)

    srv = ReusableThreadingHTTPServer(("127.0.0.1", TEST_PORT), module.CompilerHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()

    ready = False
    for _ in range(30):
        try:
            urlopen(f"{BASE_URL}/feature-check", timeout=1)
            ready = True
            break
        except Exception:
            time.sleep(0.1)

    if not ready:
        srv.shutdown()
        srv.server_close()
        pytest.fail("Compiler server failed to become ready on /feature-check")

    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()
        sys.modules.pop("dx_compiler_server_for_tests", None)
        _clear_stale_modules()
        for p in (str(COMPILER_DIR), str(ROOT)):
            while p in sys.path:
                sys.path.remove(p)


def _get_raw(path: str):
    resp = urlopen(f"{BASE_URL}{path}", timeout=5)
    return resp.read().decode(), resp.status, resp.headers.get("Content-Type", "")


def _get_json(path: str):
    body, _, _ = _get_raw(path)
    return json.loads(body)


def _request(path: str, *, method: str = "GET", body: bytes | None = None):
    req = Request(f"{BASE_URL}{path}", data=body, method=method)
    return urlopen(req, timeout=5)


def _expect_http_error(path: str, *, method: str = "GET", body: bytes | None = None):
    with pytest.raises(HTTPError) as exc:
        _request(path, method=method, body=body)
    error_body = exc.value.read()
    return exc.value.code, error_body, exc.value.headers.get("Content-Type", "")


def _multipart_upload_body(filename: str, data: bytes = b"payload", boundary: str = "----DXCompilerTestBoundary"):
    body = b"\r\n".join([
        f"--{boundary}".encode("utf-8"),
        f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode("utf-8"),
        b"Content-Type: application/octet-stream",
        b"",
        data,
        f"--{boundary}--".encode("utf-8"),
        b"",
    ])
    return body, {"Content-Type": f"multipart/form-data; boundary={boundary}"}


def _post_upload(filename: str, data: bytes = b"payload"):
    body, headers = _multipart_upload_body(filename, data)
    req = Request(f"{BASE_URL}/upload", data=body, method="POST", headers=headers)
    return urlopen(req, timeout=5)


def test_compiler_asset_rewrite_only_applies_to_full_page_route():
    source = (COMPILER_DIR / "server.py").read_text(encoding="utf-8")
    assert 'html = self._render("index.html")' in source
    assert 'render_html_with_asset_hashes(html, asset_scope="dx_compiler")' in source
    assert 'self._render("partials/progress.html", job_id=job.job_id)' in source
    progress_idx = source.index('self._render("partials/progress.html", job_id=job.job_id)')
    root_idx = source.index('html = self._render("index.html")')
    rewrite_idx = source.index('render_html_with_asset_hashes(html, asset_scope="dx_compiler")')
    assert root_idx < rewrite_idx < progress_idx


def test_setup_panel_does_not_disable_form_pointer_events():
    source = (COMPILER_DIR / "static" / "js" / "setup_panel.js").read_text(encoding="utf-8")
    assert ".compile-btn" in source
    assert "pointerEvents" not in source


def test_root_returns_rendered_html_with_cache_busters(server):
    body, status, ct = _get_raw("/")
    assert status == 200
    assert "text/html" in ct
    assert "DX Compiler" in body
    assert 'href="/static/css/graph_viewer.css?m=dx_compiler&v=' in body
    assert 'href="/static/css/style.css?m=dx_compiler&v=' in body
    assert "/static/js/compiler-i18n.js?m=dx_compiler&v=" in body


def test_index_html_returns_same_app_shell(server):
    body, status, ct = _get_raw("/index.html")
    assert status == 200
    assert "text/html" in ct
    assert "DX Compiler" in body


def test_shared_i18n_js_served(server):
    body, status, ct = _get_raw("/static/shared/i18n.js")
    assert status == 200
    assert "DXI18n" in body
    assert "SUPPORTED_LANGS" in body


def test_local_compiler_assets_served(server):
    css, status, ct = _get_raw("/static/css/style.css")
    assert status == 200
    assert "css" in ct.lower()
    assert len(css.strip()) > 0

    js, status, ct = _get_raw("/static/js/compiler-i18n.js")
    assert status == 200
    assert "javascript" in ct.lower()
    assert len(js.strip()) > 0


def test_feature_check_returns_unconfigured_contract(server):
    data = _get_json("/feature-check")
    assert isinstance(data.get("compile"), bool)
    assert data.get("setup_available") is True


def test_feature_status_marks_node_selection_unavailable_for_subprocess_compile(monkeypatch, tmp_path):
    """Subprocess-only compile support must expose node-selection limits before submit."""
    _clear_stale_modules()
    _reset_sys_path()
    import dx_compiler.server as server_mod

    original_find_spec = server_mod.importlib.util.find_spec

    def fake_find_spec(name):
        if name == "dx_com":
            return None
        return original_find_spec(name)

    class FakeSetupService:
        def get_venv_python(self):
            return str(tmp_path / "python")

        def check_status(self):
            return {"dx_com_installed": True}

    monkeypatch.setattr(server_mod.importlib.util, "find_spec", fake_find_spec)
    monkeypatch.setattr(server_mod, "setup_service", FakeSetupService())

    status = server_mod._compiler_feature_status()

    assert status["compile"] is True
    assert status["capabilities"]["node_selection"] is False
    assert any(
        warning["key"] == "node_selection_unsupported_subprocess"
        for warning in status["warnings"]
    )


def test_subprocess_node_selection_records_structured_capability_warning(monkeypatch, tmp_path):
    """Runtime fallback must not rely on log text as the only UI-visible signal."""
    _clear_stale_modules()
    _reset_sys_path()
    from dx_compiler.core import setup_service as setup_module
    from dx_compiler.core.compiler_service import CompileJob, CompilerService

    svc = CompilerService()
    job = CompileJob(job_id="subprocess-node-selection")
    job.node_selection_enabled = True
    subprocess_called = {"value": False}

    def fake_subprocess(job_arg, *args):
        subprocess_called["value"] = True
        job_arg.status = "done"

    monkeypatch.setattr(setup_module.setup_service, "get_venv_python", lambda: str(tmp_path / "python"))
    monkeypatch.setattr(svc, "_is_dx_com_available", lambda: False)
    monkeypatch.setattr(svc, "_run_compile_subprocess", fake_subprocess)

    svc._run_compile(
        job,
        "model.onnx",
        "config.json",
        str(tmp_path),
        1,
        False,
        False,
        False,
        False,
        None,
        None,
        None,
        False,
    )

    assert subprocess_called["value"] is True
    assert job.node_selection_enabled is False
    assert job.capabilities["node_selection"] is False
    assert any(
        warning["key"] == "node_selection_unsupported_subprocess"
        for warning in job.warnings
    )
    assert any(
        "Node selection is not supported in subprocess compile mode" in line
        for line in job.log_buffer.get_new_lines(0)
    )


def test_run_compile_does_not_overwrite_timeout_error(monkeypatch, tmp_path):
    """A job already marked timed out by SSE must not become done when compile returns."""
    _clear_stale_modules()
    _reset_sys_path()
    from dx_compiler.core import compiler_bridge
    from dx_compiler.core import setup_service as setup_module
    from dx_compiler.core.compiler_service import CompileJob, CompilerService

    svc = CompilerService()
    job = CompileJob(job_id="timeout-overwrite", output_dir=str(tmp_path))

    def fake_run_compile(**_kwargs):
        job.status = "error"
        job.error = "Compile timed out after 1 seconds."

    monkeypatch.setattr(setup_module.setup_service, "get_venv_python", lambda: None)
    monkeypatch.setattr(svc, "_is_dx_com_available", lambda: True)
    monkeypatch.setattr(compiler_bridge, "run_compile", fake_run_compile)

    svc._run_compile(
        job,
        "model.onnx",
        "config.json",
        str(tmp_path),
        1,
        False,
        False,
        False,
        False,
        None,
        None,
        None,
        False,
    )

    assert job.status == "error"
    assert "timed out" in (job.error or "").lower()
    assert job.progress < 100.0


def test_run_compile_subprocess_does_not_overwrite_timeout_error(monkeypatch, tmp_path):
    """A subprocess done event must not override an SSE timeout error."""
    _clear_stale_modules()
    _reset_sys_path()
    import subprocess
    from dx_compiler.core.compiler_service import CompileJob, CompilerService

    svc = CompilerService()
    job = CompileJob(job_id="timeout-subprocess", output_dir=str(tmp_path))

    class FakeStdin:
        def write(self, _data):
            return None

        def close(self):
            return None

    class FakeStdout:
        def __iter__(self):
            job.status = "error"
            job.error = "Compile timed out after 1 seconds."
            yield json.dumps({"type": "done"}) + "\n"

    class FakeStderr:
        def read(self):
            return ""

    class FakeProc:
        stdin = FakeStdin()
        stdout = FakeStdout()
        stderr = FakeStderr()
        returncode = 0

        def wait(self):
            return self.returncode

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: FakeProc())

    svc._run_compile_subprocess(
        job,
        str(tmp_path / "python"),
        "model.onnx",
        "config.json",
        str(tmp_path),
        1,
        False,
        False,
        False,
        False,
        None,
        False,
    )

    assert job.status == "error"
    assert "timed out" in (job.error or "").lower()
    assert job.progress < 100.0


def test_compile_job_error_state_wins_over_late_done_transition():
    """Status transitions must keep timeout/error from being overwritten by late completion."""
    _clear_stale_modules()
    _reset_sys_path()
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="late-done")
    job.mark_error("Compile timed out after 1 seconds.")

    assert job.mark_done() is False
    assert job.status == "error"
    assert "timed out" in (job.error or "").lower()
    assert job.progress < 100.0


def test_compile_job_error_state_wins_over_late_running_transition():
    """A worker starting late must not overwrite a terminal SSE/config error."""
    _clear_stale_modules()
    _reset_sys_path()
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="late-running")
    job.mark_error("DX_COMPILER_MAX_JOB_SECONDS must be a number")

    assert job.mark_running() is False
    assert job.status == "error"
    assert "DX_COMPILER_MAX_JOB_SECONDS" in (job.error or "")


def test_compile_job_done_state_wins_over_late_error_transition():
    """A completed job must not be changed to error by a late SSE/worker race."""
    _clear_stale_modules()
    _reset_sys_path()
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="late-error")
    assert job.mark_done() is True

    assert job.mark_error("DX_COMPILER_MAX_JOB_SECONDS must be a number") is False
    assert job.status == "done"
    assert job.error is None
    assert job.progress == 100.0


def test_compile_job_first_error_wins_over_late_error_transition():
    """A later worker exception must not replace the original terminal error."""
    _clear_stale_modules()
    _reset_sys_path()
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="late-second-error")
    assert job.mark_error("Compile timed out after 1 seconds.") is True

    assert job.mark_error("Worker exited with code 1") is False
    assert job.status == "error"
    assert job.error == "Compile timed out after 1 seconds."


def test_sse_progress_includes_structured_capabilities_on_complete(monkeypatch, tmp_path):
    """Terminal SSE payload must expose capabilities/warnings to the browser."""
    _clear_stale_modules()
    _reset_sys_path()
    import dx_compiler.server as server_mod
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="capabilities-job", status="done", output_dir=str(tmp_path))
    job.capabilities["node_selection"] = False
    job.warnings.append({
        "key": "node_selection_unsupported_subprocess",
        "message": "Node selection is not available in subprocess compile mode.",
    })

    class FakeCompilerService:
        def get_job(self, job_id):
            assert job_id == job.job_id
            return job

    events = []
    handler = server_mod.CompilerHandler.__new__(server_mod.CompilerHandler)
    handler.start_sse = lambda: None
    handler.end_sse = lambda: None
    handler.send_sse = lambda event, data: events.append((event, data)) or True
    monkeypatch.setattr(server_mod, "compiler_service", FakeCompilerService())

    server_mod.CompilerHandler._sse_progress(handler, job.job_id)

    complete_events = [data for event, data in events if event == "complete"]
    assert complete_events
    assert complete_events[-1]["capabilities"]["node_selection"] is False
    assert complete_events[-1]["warnings"][0]["key"] == "node_selection_unsupported_subprocess"


def test_sse_progress_times_out_long_running_jobs(monkeypatch, tmp_path):
    """Long-running compile jobs must emit an SSE error instead of spinning forever."""
    _clear_stale_modules()
    _reset_sys_path()
    import dx_compiler.server as server_mod
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="timeout-job", status="running", output_dir=str(tmp_path))
    job.start_monotonic = 0.0

    terminated = []

    class FakeCompilerService:
        def get_job(self, job_id):
            assert job_id == job.job_id
            return job

        def terminate_job(self, target_job, message):
            # Mirror the real service: kill the worker AND mark the job errored.
            terminated.append((target_job, message))
            return target_job.mark_error(message)

    events = []
    handler = server_mod.CompilerHandler.__new__(server_mod.CompilerHandler)
    handler.start_sse = lambda: None
    handler.end_sse = lambda: None
    handler.send_sse = lambda event, data: events.append((event, data)) or True

    monkeypatch.setenv("DX_COMPILER_MAX_JOB_SECONDS", "0.05")
    monkeypatch.setattr(server_mod, "compiler_service", FakeCompilerService())
    monkeypatch.setattr(server_mod.time, "monotonic", lambda: 0.10)

    def fail_sleep(_seconds):
        raise AssertionError("timed out job should emit error before sleeping")

    monkeypatch.setattr(server_mod.time, "sleep", fail_sleep)

    server_mod.CompilerHandler._sse_progress(handler, job.job_id)

    error_events = [data for event, data in events if event == "error"]
    assert error_events
    assert job.status == "error"
    # The timeout must actually terminate the worker, not merely report.
    assert terminated, "timeout should invoke terminate_job to kill the worker"
    assert "timed out" in (job.error or "").lower()
    assert "timed out" in (error_events[-1]["error"] or "").lower()


def test_sse_progress_reports_invalid_timeout_configuration(monkeypatch, tmp_path):
    """Invalid timeout env should be surfaced as an SSE error, not crash the handler."""
    _clear_stale_modules()
    _reset_sys_path()
    import dx_compiler.server as server_mod
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="invalid-timeout-job", status="running", output_dir=str(tmp_path))

    class FakeCompilerService:
        def get_job(self, job_id):
            assert job_id == job.job_id
            return job

    events = []
    handler = server_mod.CompilerHandler.__new__(server_mod.CompilerHandler)
    handler.start_sse = lambda: None
    handler.end_sse = lambda: None
    handler.send_sse = lambda event, data: events.append((event, data)) or True

    monkeypatch.setenv("DX_COMPILER_MAX_JOB_SECONDS", "invalid")
    monkeypatch.setattr(server_mod, "compiler_service", FakeCompilerService())

    server_mod.CompilerHandler._sse_progress(handler, job.job_id)

    error_events = [data for event, data in events if event == "error"]
    assert error_events
    assert job.status == "error"
    assert "DX_COMPILER_MAX_JOB_SECONDS" in (error_events[-1]["error"] or "")


def test_sse_progress_keeps_completed_job_when_timeout_config_is_invalid(monkeypatch, tmp_path):
    """Reconnects for terminal jobs must not turn successful jobs into config errors."""
    _clear_stale_modules()
    _reset_sys_path()
    import dx_compiler.server as server_mod
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="complete-invalid-config", status="done", output_dir=str(tmp_path))
    job.progress = 100.0

    class FakeCompilerService:
        def get_job(self, job_id):
            assert job_id == job.job_id
            return job

    events = []
    handler = server_mod.CompilerHandler.__new__(server_mod.CompilerHandler)
    handler.start_sse = lambda: None
    handler.end_sse = lambda: None
    handler.send_sse = lambda event, data: events.append((event, data)) or True

    monkeypatch.setenv("DX_COMPILER_MAX_JOB_SECONDS", "invalid")
    monkeypatch.setattr(server_mod, "compiler_service", FakeCompilerService())

    server_mod.CompilerHandler._sse_progress(handler, job.job_id)

    assert job.status == "done"
    assert job.error is None
    assert [event for event, _data in events] == ["complete"]


def test_sse_progress_keeps_concurrent_completion_during_invalid_timeout_parse(monkeypatch, tmp_path):
    """If a job completes while timeout config is parsed, SSE must not convert it to error."""
    _clear_stale_modules()
    _reset_sys_path()
    import dx_compiler.server as server_mod
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="complete-during-config", status="running", output_dir=str(tmp_path))

    class FakeCompilerService:
        def get_job(self, job_id):
            assert job_id == job.job_id
            return job

    def complete_then_raise():
        job.mark_done()
        raise ValueError("DX_COMPILER_MAX_JOB_SECONDS must be a number")

    events = []
    handler = server_mod.CompilerHandler.__new__(server_mod.CompilerHandler)
    handler.start_sse = lambda: None
    handler.end_sse = lambda: None
    handler.send_sse = lambda event, data: events.append((event, data)) or True

    monkeypatch.setattr(server_mod, "compiler_service", FakeCompilerService())
    monkeypatch.setattr(server_mod, "_compiler_max_job_seconds", complete_then_raise)

    server_mod.CompilerHandler._sse_progress(handler, job.job_id)

    assert job.status == "done"
    assert job.error is None
    assert [event for event, _data in events] == ["complete"]


def test_setup_status_returns_unconfigured_contract(server):
    data = _get_json("/setup/status")
    for key in ("dx_com_installed", "dx_com_version", "venv_path", "venv_python", "sample_models", "calibration_data"):
        assert key in data
    assert isinstance(data["dx_com_installed"], bool)
    assert isinstance(data["sample_models"], dict)
    assert isinstance(data["calibration_data"], dict)


def test_setup_sample_models_returns_list(server):
    data = _get_json("/setup/sample-models")
    assert isinstance(data, list)
    if data:
        assert {"name", "downloaded", "onnx_path", "config_path"}.issubset(data[0])


def test_api_chat_config_returns_json(server):
    data = _get_json("/api/chat/config")
    assert isinstance(data, dict)
    assert isinstance(data.get("configured"), bool)


@pytest.mark.parametrize("method,body", [
    ("GET", None),
    ("POST", b"{}"),
    ("PUT", b"{}"),
    ("PATCH", b"{}"),
    ("DELETE", None),
])
def test_unknown_routes_return_json_404(server, method, body):
    code, error_body, ct = _expect_http_error("/does-not-exist", method=method, body=body)
    assert code == 404
    assert "application/json" in ct
    data = json.loads(error_body.decode())
    assert data["error"] == "Not found"




@pytest.mark.parametrize("filename", ["model.onnx", "compile_config.json"])
def test_compiler_upload_accepts_expected_extensions(server, filename):
    resp = _post_upload(filename, b"{}")
    payload = json.loads(resp.read().decode())
    assert resp.status == 200
    assert payload["filename"] == filename
    uploaded = Path(payload["path"])
    try:
        assert uploaded.name == filename
        assert uploaded.read_bytes() == b"{}"
    finally:
        uploaded.unlink(missing_ok=True)


@pytest.mark.parametrize("filename", ["tool.py", "run.sh", "app.exe", "README", "evil.py.onnx", "exploit.sh.json"])
def test_compiler_upload_rejects_unexpected_extensions(server, filename):
    body, headers = _multipart_upload_body(filename, b"bad")
    req = Request(f"{BASE_URL}/upload", data=body, method="POST", headers=headers)
    with pytest.raises(HTTPError) as exc:
        urlopen(req, timeout=5)
    assert exc.value.code == 400
    payload = json.loads(exc.value.read().decode())
    assert "Unsupported upload file type" in payload["error"]


def test_compiler_upload_oversized_multipart_rejected_before_body_read(monkeypatch):
    _clear_stale_modules()
    _reset_sys_path()
    import dx_compiler.server as server_mod
    from shared.dx_server import RequestBodyError

    class Headers(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    class FailOnRead:
        def read(self, *_args, **_kwargs):
            raise AssertionError("oversized multipart body should not be read")

    handler = server_mod.CompilerHandler.__new__(server_mod.CompilerHandler)
    handler.headers = Headers({
        "Content-Type": "multipart/form-data; boundary=too-large",
        "Content-Length": str(handler.upload_max_bytes + 1),
    })
    handler.rfile = FailOnRead()

    with pytest.raises(RequestBodyError) as exc:
        handler.parse_multipart()
    assert exc.value.status_code == 413




def test_find_fresh_dxnn_ignores_optimized_ckpt(tmp_path, monkeypatch):
    """_find_fresh_dxnn should exclude optimized_ckpt.dxnn, not optimized_model."""
    _clear_stale_modules()
    _reset_sys_path()
    import dx_compiler.server as _server_mod
    from dx_compiler.server import _find_fresh_dxnn

    start = time.time()
    time.sleep(0.05)

    ckpt = tmp_path / "optimized_ckpt.dxnn"
    final = tmp_path / "final_model.dxnn"
    ckpt.write_text("checkpoint", encoding="utf-8")
    final.write_text("final", encoding="utf-8")

    # Force checkpoint-first ordering so the test is deterministic:
    # a buggy implementation without the filter would return ckpt.
    original_glob = _server_mod.glob_mod.glob

    def _ckpt_first_glob(pattern, **kwargs):
        results = original_glob(pattern, **kwargs)
        return sorted(results, key=lambda p: (0 if "optimized_ckpt" in p else 1))

    monkeypatch.setattr(_server_mod.glob_mod, "glob", _ckpt_first_glob)

    result = _find_fresh_dxnn(str(tmp_path), start)
    assert result == str(final)


def test_legacy_checkpoint_route_still_removed(server):
    """POST /compile/checkpoint should return 404 (legacy checkpoint UI removed)."""
    # Build minimal multipart body
    boundary = "----TestBoundary"
    body_lines = [
        f"--{boundary}",
        'Content-Disposition: form-data; name="checkpoint_path"',
        "",
        "/nonexistent/x.dxnn",
        f"--{boundary}",
        'Content-Disposition: form-data; name="output_dir"',
        "",
        "/nonexistent",
        f"--{boundary}--",
    ]
    body = "\r\n".join(body_lines).encode("utf-8")
    req = Request(
        f"{BASE_URL}/compile/checkpoint",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with pytest.raises(HTTPError) as exc:
        urlopen(req, timeout=5)
    assert exc.value.code == 404


def test_compile_range_resume_preserved(server):
    """POST /compile/{job_id}/resume must still work for paused jobs."""
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="test-resume-job")
    job.paused = True

    # The module-scoped server's handler has compiler_service in its globals.
    handler_cls = server.RequestHandlerClass
    svc = handler_cls._compile_resume.__globals__["compiler_service"]
    svc.jobs["test-resume-job"] = job
    try:
        body = json.dumps({
            "input_nodes": ["node_a"],
            "output_nodes": ["node_b"],
        }).encode("utf-8")
        req = Request(
            f"{BASE_URL}/compile/test-resume-job/resume",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        resp = urlopen(req, timeout=5)
        payload = json.loads(resp.read().decode())
        assert resp.status == 200
        assert payload["status"] == "resumed"
        assert job.selected_input_nodes == ["node_a"]
        assert job.selected_output_nodes == ["node_b"]
        assert job.pause_event.is_set()
    finally:
        svc.jobs.pop("test-resume-job", None)


def test_checkpoint_backend_symbols_removed():
    """Legacy checkpoint-only service methods must not exist."""
    _clear_stale_modules()
    _reset_sys_path()
    import inspect
    from dx_compiler.core.compiler_service import CompileJob, CompilerService
    from dx_compiler.core.compiler_bridge import run_compile

    assert not hasattr(CompilerService, "submit_checkpoint")
    assert not hasattr(CompilerService, "_run_checkpoint_compile")

    sig = inspect.signature(run_compile)
    assert "start_from" not in sig.parameters
    assert "output_name" not in sig.parameters
    assert "checkpoint" in sig.parameters
    assert "recalibration_method" in sig.parameters
    assert "dataset_path" in sig.parameters

    job = CompileJob(job_id="j")
    assert not hasattr(job, "is_checkpoint")
    assert not hasattr(job, "checkpoint_output_name")
    assert hasattr(job, "qxnn_checkpoint_path")

"""Tests for lab_portal manifest/capabilities primitives."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_STUDIO_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_STUDIO_DIR / "shared"))


@pytest.fixture(autouse=True)
def _reset_lab_portal_state():
    yield
    import lab_portal
    lab_portal._manifests.clear()
    lab_portal._apply_locks.clear()


def test_lab_capabilities_shape_has_expected_keys():
    from lab_portal import lab_capabilities
    data = lab_capabilities()
    assert data["ok"] is True
    assert isinstance(data["task_categories"], list)
    assert {"DX_APP_ROOT", "OUTPUTS_DIR"} <= set(data["allowed_roots"])
    assert "add_model_wizard" in data["feature_flags"]


def test_manifest_expired_error_shape():
    from lab_portal import create_manifest, get_manifest
    mid = create_manifest(kind="add_model", inputs={"model_name": "x"})["id"]
    # Bare module path is correct because tests/dx_app/conftest.py pins dx_app/core.
    with patch("lab_portal.time.time", return_value=10**12):
        data, code = get_manifest(mid)
    assert code == 404
    assert data["error_code"] == "manifest_expired"


def test_apply_lock_reports_conflict():
    from lab_portal import acquire_apply_lock, release_apply_lock
    mid = "lab_test_123"
    assert acquire_apply_lock(mid) == (True, None)
    ok, err = acquire_apply_lock(mid)
    assert ok is False
    assert err == {"error_code": "apply_in_progress"}
    release_apply_lock(mid)


def test_apply_lock_acquire_is_guarded_by_mutex(monkeypatch):
    import lab_portal

    class Guard:
        entered = 0

        def __enter__(self):
            self.entered += 1

        def __exit__(self, exc_type, exc, tb):
            return False

    guard = Guard()
    monkeypatch.setattr(lab_portal, "_apply_lock_mutex", guard, raising=False)
    ok, err = lab_portal.acquire_apply_lock("lab_mutex_guard")
    assert ok is True
    assert err is None
    assert guard.entered == 1
    lab_portal.release_apply_lock("lab_mutex_guard")
    assert guard.entered == 2


def test_manifest_store_create_and_get_are_guarded_by_mutex(monkeypatch):
    import lab_portal

    class Guard:
        entered = 0

        def __enter__(self):
            self.entered += 1

        def __exit__(self, exc_type, exc, tb):
            return False

    guard = Guard()
    monkeypatch.setattr(lab_portal, "_manifests_lock", guard, raising=False)
    manifest = lab_portal.create_manifest("add_model")
    assert guard.entered >= 1

    entered_after_create = guard.entered
    data, code = lab_portal.get_manifest(manifest["id"])
    assert code == 200
    assert data["id"] == manifest["id"]
    assert guard.entered > entered_after_create


def test_result_with_http_status_only_uses_error_status():
    from lab_portal import _result_with_http_status
    # Non-error dict with integer status should NOT be treated as HTTP code
    body, code = _result_with_http_status({"ok": True, "status": 0})
    assert code == 200
    assert body["status"] == 0
    # Error dict with integer status SHOULD be extracted as HTTP code
    body, code = _result_with_http_status({"error": "bad", "status": 400})
    assert code == 400
    assert "status" not in body


def test_manifest_store_evicts_expired_items_on_create():
    from lab_portal import create_manifest, get_manifest
    with patch("lab_portal.time.time", return_value=100):
        old_id = create_manifest(kind="add_model")["id"]
    with patch("lab_portal.time.time", return_value=100 + 4 * 60 * 60 + 1):
        create_manifest(kind="add_model")
        data, code = get_manifest(old_id)
    assert code == 404
    assert data["error_code"] == "manifest_expired"


def test_capabilities_route_no_token_returns_403_without_status():
    """GET /api/lab/capabilities without X-Lab-Token → 403, no 'status' in body."""
    import server

    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/capabilities"
    handler.query = {}
    handler.headers = {"Origin": "http://localhost:8080"}
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()

    assert captured["code"] == 403
    assert "error" in captured["data"]
    assert "status" not in captured["data"]


def test_create_manifest_protects_identity_fields():
    from lab_portal import create_manifest
    manifest = create_manifest("add_model", id="../../bad", created_at=0)
    assert manifest["id"].startswith("lab_")
    assert ".." not in manifest["id"]
    assert manifest["created_at"] != 0


def test_manifest_store_caps_active_items(monkeypatch):
    import lab_portal
    monkeypatch.setattr(lab_portal, "MAX_MANIFESTS", 2)
    first = lab_portal.create_manifest("add_model")["id"]
    second = lab_portal.create_manifest("add_model")["id"]
    third = lab_portal.create_manifest("add_model")["id"]
    assert lab_portal.get_manifest(first)[1] == 404
    assert lab_portal.get_manifest(second)[1] == 200
    assert lab_portal.get_manifest(third)[1] == 200


def test_capabilities_route_allows_server_name_origin():
    import types
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/capabilities"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://dx-local.test:8080"}
    handler.server = types.SimpleNamespace(server_name="dx-local.test")
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 200
    assert captured["data"]["ok"] is True


def test_capabilities_route_does_not_trust_host_header_for_origin():
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/capabilities"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "https://evil.example.com", "Host": "evil.example.com"}
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_capabilities_route_does_not_trust_host_header_with_real_server():
    """Host header must not widen the allow-list even when handler.server exists."""
    import types
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/capabilities"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "https://evil.example.com", "Host": "evil.example.com"}
    handler.server = types.SimpleNamespace(server_name="real-server.local")
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403




def test_add_model_dry_run_returns_manifest_without_writing(tmp_path, monkeypatch):
    import lab_portal
    from developer import lab_session
    dx_app_root = tmp_path / "runtime" / "dx_app"
    dx_app_root.mkdir(parents=True)
    outputs_dir = tmp_path / "studio" / "dx_app" / "outputs"
    outputs_dir.mkdir(parents=True)
    source = outputs_dir / "demo.dxnn"
    source.write_bytes(b"DXNN")
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", dx_app_root)
    monkeypatch.setattr(lab_portal, "CPP_DIR", dx_app_root / "src" / "cpp_example")
    monkeypatch.setattr(lab_portal, "PY_DIR", dx_app_root / "src" / "python_example")
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", outputs_dir)
    monkeypatch.setattr(lab_portal, "SCRIPT_DIR", outputs_dir.parent)
    before = set(tmp_path.rglob("*"))
    result = lab_portal.plan_add_model(lab_session()["token"], {
        "model_name": "demo_model",
        "category": "object_detection",
        "task_type": "object_detection",
        "lang": "python",
        "source_path": "outputs/demo.dxnn",
        "postprocessor": "yolov8",
    })
    assert result["kind"] == "add_model"
    assert result["status"] == "ready"
    assert all("root" in op and "path" in op for op in result["operations"])
    assert all(op["root"] == "DX_APP_ROOT" for op in result["operations"])
    assert all(not Path(op["path"]).is_absolute() for op in result["operations"])
    assert set(tmp_path.rglob("*")) == before


def test_add_model_dry_run_reports_overwrite_confirmation(tmp_path, monkeypatch):
    import lab_portal
    from developer import lab_session
    dx_app_root = tmp_path / "runtime" / "dx_app"
    existing = dx_app_root / "src" / "cpp_example" / "object_detection" / "demo_model"
    existing.mkdir(parents=True)
    outputs_dir = tmp_path / "studio" / "dx_app" / "outputs"
    outputs_dir.mkdir(parents=True)
    source = outputs_dir / "demo.dxnn"
    source.write_bytes(b"DXNN")
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", dx_app_root)
    monkeypatch.setattr(lab_portal, "CPP_DIR", dx_app_root / "src" / "cpp_example")
    monkeypatch.setattr(lab_portal, "PY_DIR", dx_app_root / "src" / "python_example")
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", outputs_dir)
    monkeypatch.setattr(lab_portal, "SCRIPT_DIR", outputs_dir.parent)
    result = lab_portal.plan_add_model(lab_session()["token"], {
        "model_name": "demo_model",
        "category": "object_detection",
        "task_type": "object_detection",
        "lang": "cpp",
        "source_path": str(source),
        "postprocessor": "yolov8",
    })
    assert result["status"] == "ready"
    assert result["confirmations"][0]["key"] == "overwrite"
    assert result["confirmations"][0]["expected"] == "overwrite:demo_model"
    assert result["operations"][0]["action"] == "modify"
    assert result["operations"][0]["root"] == "DX_APP_ROOT"
    assert not Path(result["operations"][0]["path"]).is_absolute()
    assert "label" in result["confirmations"][0]
    assert "message" not in result["confirmations"][0]
    assert result["summary"] == "Add demo_model to object_detection"


def test_add_model_dry_run_rejects_source_path_traversal():
    from developer import lab_session
    from lab_portal import plan_add_model
    result = plan_add_model(lab_session()["token"], {
        "model_name": "demo_model",
        "category": "object_detection",
        "task_type": "object_detection",
        "lang": "python",
        "source_path": "../../etc/passwd",
    })
    assert result.get("error")
    assert result.get("status") == 400


def test_add_model_dry_run_route_preserves_manifest_status(tmp_path, monkeypatch):
    import types
    import server
    import lab_portal
    from developer import lab_session
    tok = lab_session()["token"]
    dx_app_root = tmp_path / "runtime" / "dx_app"
    dx_app_root.mkdir(parents=True)
    outputs_dir = tmp_path / "studio" / "dx_app" / "outputs"
    outputs_dir.mkdir(parents=True)
    source = outputs_dir / "demo.dxnn"
    source.write_bytes(b"DXNN")
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", dx_app_root)
    monkeypatch.setattr(lab_portal, "CPP_DIR", dx_app_root / "src" / "cpp_example")
    monkeypatch.setattr(lab_portal, "PY_DIR", dx_app_root / "src" / "python_example")
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", outputs_dir)
    monkeypatch.setattr(lab_portal, "SCRIPT_DIR", outputs_dir.parent)
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/add_model/dry_run"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {
        "model_name": "demo_model",
        "category": "object_detection",
        "task_type": "object_detection",
        "lang": "python",
        "source_path": "outputs/demo.dxnn",
        "postprocessor": "yolov8",
    }
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 200
    assert captured["data"]["status"] == "ready"


def test_add_model_dry_run_target_path_stays_under_language_root(monkeypatch, tmp_path):
    """Defense-in-depth: resolve_under rejects traversal even if category validator is bypassed."""
    import lab_portal
    from developer import lab_session
    dx_app_root = tmp_path / "runtime" / "dx_app"
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", dx_app_root)
    monkeypatch.setattr(lab_portal, "CPP_DIR", dx_app_root / "src" / "cpp_example")
    monkeypatch.setattr(lab_portal, "PY_DIR", dx_app_root / "src" / "python_example")
    monkeypatch.setattr(lab_portal, "_require_lab_category", lambda _category: None)
    result = lab_portal.plan_add_model(lab_session()["token"], {
        "model_name": "demo_model",
        "category": "../../escape",
        "lang": "cpp",
    })
    assert result.get("status") == 400
    assert "outside allowed roots" in result.get("error", "")


def test_add_model_dry_run_route_rejects_hostile_origin():
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/add_model/dry_run"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "https://evil.example.com"}
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"model_name": "demo_model"}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_add_model_dry_run_route_invalid_token_returns_403_without_status():
    import server
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/add_model/dry_run"
    handler.query = {}
    handler.headers = {"X-Lab-Token": "invalid"}
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"model_name": "demo_model"}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403
    assert "status" not in captured.get("data", {})




def test_add_model_apply_rejects_expired_manifest():
    from developer import lab_session
    from lab_portal import apply_add_model
    res, code = apply_add_model(lab_session()["token"], {"manifest_id": "missing"})
    assert code == 404
    assert res["error_code"] == "manifest_expired"


def test_add_model_apply_conflict_when_lock_held():
    from developer import lab_session
    from lab_portal import create_manifest, acquire_apply_lock, release_apply_lock, apply_add_model
    manifest = create_manifest("add_model", inputs={"model_name": "demo"}, status="ready")
    acquire_apply_lock(manifest["id"])
    try:
        res, code = apply_add_model(lab_session()["token"], {"manifest_id": manifest["id"]})
    finally:
        release_apply_lock(manifest["id"])
    assert code == 409
    assert res["error_code"] == "apply_in_progress"


def test_add_model_apply_rechecks_ready_status_after_lock(monkeypatch):
    """If status changes while waiting for the lock, apply_add_model must not run dev_add."""
    from developer import lab_session
    import lab_portal
    calls = []
    manifest = lab_portal.create_manifest(
        "add_model",
        inputs={
            "model_name": "demo",
            "category": "object_detection",
            "task_type": "object_detection",
            "lang": "python",
            "postprocessor": "yolov8",
        },
        status="ready",
    )

    def fake_acquire_apply_lock(manifest_id):
        manifest["status"] = "applied"
        return True, None

    def fake_dev_add(*args, **kwargs):
        calls.append((args, kwargs))
        return {"ok": True}

    monkeypatch.setattr(lab_portal, "acquire_apply_lock", fake_acquire_apply_lock)
    monkeypatch.setattr(lab_portal, "dev_add", fake_dev_add)
    res, code = lab_portal.apply_add_model(lab_session()["token"], {"manifest_id": manifest["id"]})
    assert code == 400
    assert res["error_code"] == "manifest_not_ready"
    assert calls == []


def test_add_model_apply_rejects_non_ready_manifest():
    from developer import lab_session
    from lab_portal import create_manifest, apply_add_model
    manifest = create_manifest("add_model", inputs={"model_name": "demo"}, status="blocked")
    res, code = apply_add_model(lab_session()["token"], {"manifest_id": manifest["id"]})
    assert code == 400
    assert res["error_code"] == "manifest_not_ready"


def test_add_model_apply_requires_matching_confirmation():
    from developer import lab_session
    from lab_portal import create_manifest, apply_add_model
    manifest = create_manifest(
        "add_model",
        inputs={"model_name": "demo", "category": "object_detection", "lang": "python"},
        status="ready",
        confirmations=[{"key": "overwrite", "expected": "overwrite:demo", "label": "Overwrite"}],
    )
    res, code = apply_add_model(lab_session()["token"], {"manifest_id": manifest["id"], "confirmations": {"overwrite": "wrong"}})
    assert code == 400
    assert res["error_code"] == "confirmation_required"
    assert res["missing"]["key"] == "overwrite"


def test_add_model_apply_uses_manifest_inputs_and_releases_lock(monkeypatch):
    from developer import lab_session
    import lab_portal
    calls = []
    def fake_dev_add(tok, mn, tt, lang, cat, pp, sync_only=False, confirm_overwrite=False):
        calls.append((mn, tt, lang, cat, pp, sync_only, confirm_overwrite))
        return {"ok": True, "output": "done"}
    monkeypatch.setattr(lab_portal, "dev_add", fake_dev_add)
    manifest = lab_portal.create_manifest(
        "add_model",
        inputs={"model_name": "demo", "category": "object_detection", "task_type": "object_detection", "lang": "python", "postprocessor": "yolov8"},
        status="ready",
        confirmations=[{"key": "overwrite", "expected": "overwrite:demo", "label": "Overwrite"}],
    )
    tok = lab_session()["token"]
    res, code = lab_portal.apply_add_model(tok, {
        "manifest_id": manifest["id"],
        "confirmations": {"overwrite": "overwrite:demo"},
        "model_name": "evil_request_payload",
    })
    assert code == 200
    assert res["ok"] is True
    assert calls == [("demo", "object_detection", "python", "object_detection", "yolov8", False, True)]
    ok, _ = lab_portal.acquire_apply_lock(manifest["id"])
    assert ok is True
    lab_portal.release_apply_lock(manifest["id"])


def test_add_model_apply_rejects_wrong_manifest_kind():
    from developer import lab_session
    from lab_portal import create_manifest, apply_add_model
    manifest = create_manifest("delete_model", inputs={"model_name": "demo"}, status="ready")
    res, code = apply_add_model(lab_session()["token"], {"manifest_id": manifest["id"]})
    assert code == 400
    assert res["error_code"] == "invalid_manifest_kind"




def test_add_model_apply_route_rejects_hostile_origin():
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/add_model/apply"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "https://evil.example.com"}
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"manifest_id": "whatever"}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_add_model_apply_route_preserves_dev_add_result(monkeypatch):
    import types
    import server
    import lab_portal
    from developer import lab_session
    tok = lab_session()["token"]

    def fake_dev_add(tok, mn, tt, lang, cat, pp, sync_only=False, confirm_overwrite=False):
        return {"ok": True, "output": "created"}
    monkeypatch.setattr(lab_portal, "dev_add", fake_dev_add)

    manifest = lab_portal.create_manifest(
        "add_model",
        inputs={"model_name": "demo", "category": "object_detection", "task_type": "object_detection", "lang": "python", "postprocessor": "yolov8"},
        status="ready",
    )
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/add_model/apply"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"manifest_id": manifest["id"]}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 200
    assert captured["data"]["ok"] is True
    assert captured["data"]["output"] == "created"


def test_add_model_apply_marks_manifest_applied_after_success(monkeypatch):
    from developer import lab_session
    import lab_portal
    monkeypatch.setattr(lab_portal, "dev_add", lambda *args, **kwargs: {"ok": True, "output": "done"})
    manifest = lab_portal.create_manifest(
        "add_model",
        inputs={"model_name": "demo", "category": "object_detection", "task_type": "object_detection", "lang": "python"},
        status="ready",
    )
    tok = lab_session()["token"]
    res, code = lab_portal.apply_add_model(tok, {"manifest_id": manifest["id"]})
    assert code == 200
    assert res["ok"] is True
    assert manifest["status"] == "applied"
    res2, code2 = lab_portal.apply_add_model(tok, {"manifest_id": manifest["id"]})
    assert code2 == 400
    assert res2["error_code"] == "manifest_not_ready"




def test_add_model_smoke_rejects_expired_manifest():
    from developer import lab_session
    from lab_portal import smoke_add_model
    res, code = smoke_add_model(lab_session()["token"], {"manifest_id": "missing"})
    assert code == 404
    assert res["error_code"] == "manifest_expired"


def test_add_model_smoke_returns_blocked_for_valid_manifest(tmp_path, monkeypatch):
    import lab_portal
    from developer import lab_session
    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir()
    source = outputs_dir / "demo.dxnn"
    source.write_bytes(b"DXNN")
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", outputs_dir)
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", tmp_path / "dx_app")
    monkeypatch.setattr(lab_portal, "SCRIPT_DIR", tmp_path)
    manifest = lab_portal.create_manifest(
        "add_model",
        inputs={"model_name": "demo", "category": "object_detection", "source_path": str(source)},
        status="ready",
    )
    res, code = lab_portal.smoke_add_model(lab_session()["token"], {"manifest_id": manifest["id"]})
    assert code == 200
    assert res["ok"] is False
    assert res["status"] == "blocked"
    assert res["blocker"] == "sample_input_required"


def test_add_model_smoke_route_rejects_hostile_origin():
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/add_model/smoke"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "https://evil.example.com"}
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"manifest_id": "whatever"}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_add_model_smoke_requires_source_path():
    from developer import lab_session
    from lab_portal import create_manifest, smoke_add_model
    manifest = create_manifest("add_model", inputs={"model_name": "demo"}, status="ready")
    res, code = smoke_add_model(lab_session()["token"], {"manifest_id": manifest["id"]})
    assert code == 200
    assert res["ok"] is False
    assert res["status"] == "blocked"
    assert res["blocker"] == "source_path_required"




def test_task_dry_run_returns_generated_file_previews_without_writing(tmp_path, monkeypatch):
    import lab_portal
    from developer import lab_session
    from lab_portal import plan_task_scaffold
    dx_root = tmp_path / "dx_app"
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", dx_root)
    monkeypatch.setattr(lab_portal, "CPP_DIR", dx_root / "src" / "cpp_example")
    monkeypatch.setattr(lab_portal, "PY_DIR", dx_root / "src" / "python_example")
    before = set(dx_root.rglob("*")) if dx_root.exists() else set()
    tok = lab_session()["token"]
    result = plan_task_scaffold(tok, {"task_name": "my_task", "lang": "python", "scaffold_type": "full"})
    assert result["kind"] == "task_scaffold"
    assert result["operations"]
    assert all(op["action"] == "create" for op in result["operations"])
    assert any("TODO(TEMPLATE-PLACEHOLDER)" in op["preview"] for op in result["operations"])
    after = set(dx_root.rglob("*")) if dx_root.exists() else set()
    assert after == before


def test_task_dry_run_supports_postprocessor_only_scaffold():
    from developer import lab_session
    from lab_portal import plan_task_scaffold
    result = plan_task_scaffold(lab_session()["token"], {
        "task_name": "my_task",
        "lang": "python",
        "scaffold_type": "postprocessor",
    })
    paths = [op["path"] for op in result["operations"]]
    assert paths
    assert all("/processors/" in path or path.startswith("src/python_example/common/processors/") for path in paths)


def test_task_dry_run_generated_paths_stay_under_allowed_roots(tmp_path, monkeypatch):
    import lab_portal
    from developer import lab_session
    from lab_portal import plan_task_scaffold
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", tmp_path / "dx_app")
    monkeypatch.setattr(lab_portal, "CPP_DIR", tmp_path / "dx_app" / "src" / "cpp_example")
    monkeypatch.setattr(lab_portal, "PY_DIR", tmp_path / "dx_app" / "src" / "python_example")
    result = plan_task_scaffold(lab_session()["token"], {"task_name": "../bad", "lang": "python", "scaffold_type": "full"})
    assert result.get("error") or all(".." not in op["path"].split("/") for op in result.get("operations", []))


def test_task_dry_run_rejects_unknown_scaffold_type():
    from developer import lab_session
    from lab_portal import plan_task_scaffold
    result = plan_task_scaffold(lab_session()["token"], {
        "task_name": "my_task",
        "lang": "python",
        "scaffold_type": "unknown_type",
    })
    assert result.get("error")
    assert result.get("status") == 400


def test_task_dry_run_marks_existing_targets_as_modify(tmp_path, monkeypatch):
    import lab_portal
    from developer import lab_session
    from lab_portal import plan_task_scaffold
    dx_root = tmp_path / "dx_app"
    py_dir = dx_root / "src" / "python_example"
    (py_dir / "common" / "processors").mkdir(parents=True)
    (py_dir / "common" / "processors" / "my_task_postprocessor.py").write_text("old")
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", dx_root)
    monkeypatch.setattr(lab_portal, "CPP_DIR", dx_root / "src" / "cpp_example")
    monkeypatch.setattr(lab_portal, "PY_DIR", py_dir)
    result = plan_task_scaffold(lab_session()["token"], {
        "task_name": "my_task",
        "lang": "python",
        "scaffold_type": "full",
    })
    assert result["kind"] == "task_scaffold"
    modify_ops = [op for op in result["operations"] if op["action"] == "modify"]
    assert len(modify_ops) >= 1
    assert result["confirmations"]
    assert result["confirmations"][0]["key"] == "overwrite"
    assert result["confirmations"][0]["expected"] == "overwrite:my_task"


def test_task_dry_run_cpp_only_generates_cpp_files():
    from developer import lab_session
    from lab_portal import plan_task_scaffold
    result = plan_task_scaffold(lab_session()["token"], {
        "task_name": "my_task",
        "lang": "cpp",
        "scaffold_type": "full",
    })
    assert result["kind"] == "task_scaffold"
    paths = [op["path"] for op in result["operations"]]
    assert all("cpp_example" in p for p in paths)
    assert not any("python_example" in p for p in paths)




def test_task_apply_rejects_expired_manifest():
    from developer import lab_session
    from lab_portal import apply_task_scaffold
    res, code = apply_task_scaffold(lab_session()["token"], {"manifest_id": "missing"})
    assert code == 404
    assert res["error_code"] == "manifest_expired"


def test_task_apply_rejects_wrong_manifest_kind():
    from developer import lab_session
    from lab_portal import create_manifest, apply_task_scaffold
    manifest = create_manifest("add_model", inputs={"task_name": "demo"}, status="ready")
    res, code = apply_task_scaffold(lab_session()["token"], {"manifest_id": manifest["id"]})
    assert code == 400
    assert res["error_code"] == "invalid_manifest_kind"


def test_task_apply_rejects_non_ready_manifest():
    from developer import lab_session
    from lab_portal import create_manifest, apply_task_scaffold
    manifest = create_manifest("task_scaffold", inputs={"task_name": "demo"}, status="blocked")
    res, code = apply_task_scaffold(lab_session()["token"], {"manifest_id": manifest["id"]})
    assert code == 400
    assert res["error_code"] == "manifest_not_ready"


def test_task_apply_requires_matching_confirmation():
    from developer import lab_session
    from lab_portal import create_manifest, apply_task_scaffold
    manifest = create_manifest(
        "task_scaffold",
        inputs={"task_name": "demo", "lang": "python", "scaffold_type": "full"},
        status="ready",
        confirmations=[{"key": "overwrite", "expected": "overwrite:demo", "label": "Overwrite"}],
    )
    res, code = apply_task_scaffold(lab_session()["token"], {
        "manifest_id": manifest["id"],
        "confirmations": {"overwrite": "wrong"},
    })
    assert code == 400
    assert res["error_code"] == "confirmation_required"
    assert res["missing"]["key"] == "overwrite"


def test_task_apply_uses_manifest_inputs_and_marks_applied(monkeypatch):
    from developer import lab_session
    import lab_portal
    calls = []

    def fake_dev_new_task(tok, task_name, lang="both", confirm_overwrite=False, scaffold_type="full"):
        calls.append((task_name, lang, confirm_overwrite))
        return {"ok": True, "task_name": task_name, "files": [], "count": 0}
    monkeypatch.setattr(lab_portal, "dev_new_task", fake_dev_new_task)

    manifest = lab_portal.create_manifest(
        "task_scaffold",
        inputs={"task_name": "demo", "lang": "python", "scaffold_type": "full"},
        status="ready",
    )
    tok = lab_session()["token"]
    res, code = lab_portal.apply_task_scaffold(tok, {
        "manifest_id": manifest["id"],
        "task_name": "evil_payload_override",
    })
    assert code == 200
    assert res["ok"] is True
    assert calls == [("demo", "python", True)]
    assert manifest["status"] == "applied"
    # Second apply should fail
    res2, code2 = lab_portal.apply_task_scaffold(tok, {"manifest_id": manifest["id"]})
    assert code2 == 400
    assert res2["error_code"] == "manifest_not_ready"


def test_task_apply_postprocessor_scaffold_creates_only_postprocessor_files(tmp_path, monkeypatch):
    """apply_task_scaffold with scaffold_type='postprocessor' must NOT create visualizer/runner/base files."""
    import developer
    import lab_portal
    from developer import lab_session

    dx_root = tmp_path / "dx_app"
    monkeypatch.setattr(developer, "DX_APP_ROOT", dx_root)
    monkeypatch.setattr(developer, "CPP_DIR", dx_root / "src" / "cpp_example")
    monkeypatch.setattr(developer, "PY_DIR", dx_root / "src" / "python_example")
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", dx_root)
    monkeypatch.setattr(lab_portal, "CPP_DIR", dx_root / "src" / "cpp_example")
    monkeypatch.setattr(lab_portal, "PY_DIR", dx_root / "src" / "python_example")

    manifest = lab_portal.create_manifest(
        "task_scaffold",
        inputs={"task_name": "demo", "lang": "both", "scaffold_type": "postprocessor"},
        status="ready",
    )
    tok = lab_session()["token"]
    res, code = lab_portal.apply_task_scaffold(tok, {"manifest_id": manifest["id"]})
    assert code == 200
    assert res["ok"] is True

    created = [Path(f) for f in res["files"]]
    for f in created:
        assert "processors" in f.parts, f"unexpected non-postprocessor file: {f}"
    assert not any("visualizer" in f.name for f in created)
    assert not any("runner" in f.name for f in created)
    assert not any("factory" in f.name for f in created)


def test_task_apply_payload_cannot_override_scaffold_type(tmp_path, monkeypatch):
    """Request payload scaffold_type must not override the manifest's scaffold_type."""
    import developer
    import lab_portal
    from developer import lab_session

    dx_root = tmp_path / "dx_app"
    monkeypatch.setattr(developer, "DX_APP_ROOT", dx_root)
    monkeypatch.setattr(developer, "CPP_DIR", dx_root / "src" / "cpp_example")
    monkeypatch.setattr(developer, "PY_DIR", dx_root / "src" / "python_example")
    monkeypatch.setattr(lab_portal, "DX_APP_ROOT", dx_root)
    monkeypatch.setattr(lab_portal, "CPP_DIR", dx_root / "src" / "cpp_example")
    monkeypatch.setattr(lab_portal, "PY_DIR", dx_root / "src" / "python_example")

    manifest = lab_portal.create_manifest(
        "task_scaffold",
        inputs={"task_name": "demo", "lang": "both", "scaffold_type": "postprocessor"},
        status="ready",
    )
    tok = lab_session()["token"]
    res, code = lab_portal.apply_task_scaffold(tok, {
        "manifest_id": manifest["id"],
        "scaffold_type": "full",
    })
    assert code == 200
    assert res["ok"] is True
    created = [Path(f) for f in res["files"]]
    for f in created:
        assert "processors" in f.parts, f"payload override created non-postprocessor file: {f}"


def test_task_apply_conflict_when_lock_held():
    from developer import lab_session
    from lab_portal import create_manifest, acquire_apply_lock, release_apply_lock, apply_task_scaffold
    manifest = create_manifest("task_scaffold", inputs={"task_name": "demo", "lang": "python", "scaffold_type": "full"}, status="ready")
    acquire_apply_lock(manifest["id"])
    try:
        res, code = apply_task_scaffold(lab_session()["token"], {"manifest_id": manifest["id"]})
    finally:
        release_apply_lock(manifest["id"])
    assert code == 409
    assert res["error_code"] == "apply_in_progress"


def test_task_apply_rechecks_ready_status_after_lock(monkeypatch):
    """If status changes while waiting for the lock, apply_task_scaffold must not run dev_new_task."""
    from developer import lab_session
    import lab_portal
    calls = []
    manifest = lab_portal.create_manifest(
        "task_scaffold",
        inputs={"task_name": "demo", "lang": "python", "scaffold_type": "full"},
        status="ready",
    )

    def fake_acquire_apply_lock(manifest_id):
        manifest["status"] = "applied"
        return True, None

    def fake_dev_new_task(*args, **kwargs):
        calls.append((args, kwargs))
        return {"ok": True}

    monkeypatch.setattr(lab_portal, "acquire_apply_lock", fake_acquire_apply_lock)
    monkeypatch.setattr(lab_portal, "dev_new_task", fake_dev_new_task)
    res, code = lab_portal.apply_task_scaffold(lab_session()["token"], {"manifest_id": manifest["id"]})
    assert code == 400
    assert res["error_code"] == "manifest_not_ready"
    assert calls == []




def test_task_dry_run_route_rejects_hostile_origin():
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/task/dry_run"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "https://evil.example.com"}
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"task_name": "demo"}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_task_dry_run_route_invalid_token_returns_403_without_status():
    import server
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/task/dry_run"
    handler.query = {}
    handler.headers = {"X-Lab-Token": "invalid"}
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"task_name": "demo"}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403
    assert "status" not in captured.get("data", {})


def test_task_apply_route_rejects_hostile_origin():
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/task/apply"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "https://evil.example.com"}
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"manifest_id": "whatever"}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_task_apply_route_preserves_dev_new_task_result(monkeypatch):
    import types
    import server
    import lab_portal
    from developer import lab_session
    tok = lab_session()["token"]

    def fake_dev_new_task(tok, task_name, lang="both", confirm_overwrite=False, scaffold_type="full"):
        return {"ok": True, "task_name": task_name, "files": ["a.py"], "count": 1}
    monkeypatch.setattr(lab_portal, "dev_new_task", fake_dev_new_task)

    manifest = lab_portal.create_manifest(
        "task_scaffold",
        inputs={"task_name": "demo", "lang": "python", "scaffold_type": "full"},
        status="ready",
    )
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/task/apply"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"manifest_id": manifest["id"]}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 200
    assert captured["data"]["ok"] is True




def test_build_task_file_plan_rejects_invalid_lang():
    """build_task_file_plan must return an error for unsupported lang values."""
    from developer import build_task_file_plan
    file_plan, err = build_task_file_plan("my_task", lang="garbage_value", scaffold_type="full")
    assert err is not None, "Expected error for invalid lang"
    assert err.get("status") == 400
    assert file_plan == []


def test_plan_task_scaffold_rejects_invalid_lang():
    """plan_task_scaffold must return status 400 and no manifest for invalid lang."""
    from developer import lab_session
    from lab_portal import plan_task_scaffold
    result = plan_task_scaffold(lab_session()["token"], {
        "task_name": "my_task",
        "lang": "garbage_value",
        "scaffold_type": "full",
    })
    assert result.get("error")
    assert result.get("status") == 400
    assert "kind" not in result  # no manifest created


def test_dev_new_task_rejects_invalid_lang():
    """dev_new_task must return status 400, not ok:True with count:0."""
    from developer import lab_session, dev_new_task
    result = dev_new_task(lab_session()["token"], "my_task", lang="garbage_value")
    assert result.get("status") == 400
    assert result.get("error")
    assert result.get("ok", None) is not True


def test_task_dry_run_route_returns_400_for_invalid_lang():
    """Route-level: plan_task_scaffold_response with invalid lang returns HTTP 400."""
    from developer import lab_session
    from lab_portal import plan_task_scaffold_response
    tok = lab_session()["token"]
    result, code = plan_task_scaffold_response(tok, {
        "task_name": "my_task",
        "lang": "invalid_lang",
        "scaffold_type": "full",
    })
    assert code == 400
    assert result.get("error")




def test_generated_files_returns_only_manifest_operations():
    from lab_portal import create_manifest, generated_files_for_manifest
    manifest = create_manifest("task_scaffold", operations=[
        {"action": "create", "root": "DX_APP_ROOT",
         "path": "src/python_example/common/processors/x.py",
         "preview": "content", "exists": False, "risk": "low"},
    ])
    res, code = generated_files_for_manifest(manifest["id"])
    assert code == 200
    assert res["files"][0]["path"].endswith("x.py")
    assert res["files"][0]["preview"] == "content"


def test_generated_files_includes_size_as_utf8_byte_length():
    from lab_portal import create_manifest, generated_files_for_manifest
    preview = "héllo"  # 6 bytes in UTF-8
    manifest = create_manifest("task_scaffold", operations=[
        {"action": "create", "root": "DX_APP_ROOT",
         "path": "a.py", "preview": preview, "exists": False, "risk": "low"},
    ])
    res, code = generated_files_for_manifest(manifest["id"])
    assert code == 200
    assert res["files"][0]["size"] == len(preview.encode("utf-8"))


def test_generated_files_unknown_manifest_returns_manifest_expired():
    from lab_portal import generated_files_for_manifest
    res, code = generated_files_for_manifest("lab_missing_999")
    assert code == 404
    assert res["error_code"] == "manifest_expired"


def test_generated_files_excludes_non_create_modify_operations():
    from lab_portal import create_manifest, generated_files_for_manifest
    manifest = create_manifest("task_scaffold", operations=[
        {"action": "create", "root": "DX_APP_ROOT",
         "path": "src/python_example/common/processors/a.py",
         "preview": "a", "exists": False, "risk": "low"},
        {"action": "delete", "root": "DX_APP_ROOT",
         "path": "src/python_example/common/processors/b.py",
         "preview": "", "exists": True, "risk": "high"},
        {"action": "run", "root": "DX_APP_ROOT",
         "path": "scripts/run.sh",
         "preview": "", "exists": True, "risk": "medium"},
    ])
    res, code = generated_files_for_manifest(manifest["id"])
    assert code == 200
    assert [f["path"] for f in res["files"]] == [
        "src/python_example/common/processors/a.py"
    ]


def test_generated_files_includes_modify_operations():
    from lab_portal import create_manifest, generated_files_for_manifest
    manifest = create_manifest("task_scaffold", operations=[
        {"action": "modify", "root": "DX_APP_ROOT",
         "path": "src/mod.py", "preview": "modified", "exists": True, "risk": "low"},
    ])
    res, code = generated_files_for_manifest(manifest["id"])
    assert code == 200
    assert len(res["files"]) == 1
    assert res["files"][0]["path"] == "src/mod.py"
    assert res["files"][0]["root"] == "DX_APP_ROOT"


def test_generated_files_route_requires_lab_token():
    import server
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/generated/lab_test_123"
    handler.query = {}
    handler.headers = {}
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_generated_files_route_rejects_hostile_origin():
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/generated/lab_test_456"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "https://evil.example.com"}
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_generated_files_route_checks_origin_before_manifest_id_validation():
    import server
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/generated/../secret"
    handler.query = {}
    handler.headers = {"Origin": "https://evil.example.com"}
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403
    assert captured["data"].get("error") != "Unsafe manifest id"


def test_generated_files_route_checks_token_before_manifest_id_validation():
    import server
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/generated/../secret"
    handler.query = {}
    handler.headers = {"Origin": "http://localhost:8080"}
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403
    assert captured["data"].get("error") != "Unsafe manifest id"


def test_generated_files_route_rejects_unsafe_id_with_slash():
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/generated/../secret"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 400


def test_generated_files_route_rejects_unsafe_id_with_dot():
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/generated/lab_bad.extra"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 400


def test_generated_files_route_rejects_id_without_lab_prefix():
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/generated/bad_prefix_123"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 400


def test_generated_files_route_valid_returns_files():
    import server
    from developer import lab_session
    from lab_portal import create_manifest
    tok = lab_session()["token"]
    manifest = create_manifest("task_scaffold", operations=[
        {"action": "create", "root": "DX_APP_ROOT",
         "path": "hello.py", "preview": "print('hi')",
         "exists": False, "risk": "low"},
    ])
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = f"/api/lab/generated/{manifest['id']}"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 200
    assert captured["data"]["files"][0]["path"] == "hello.py"
    assert captured["data"]["files"][0]["preview"] == "print('hi')"




def test_list_pending_manifests_returns_active_only():
    """list_pending_manifests() returns only non-expired, active (ready) manifests."""
    from lab_portal import create_manifest, list_pending_manifests
    m1 = create_manifest("add_model", inputs={"model_name": "a"}, status="ready")
    m2 = create_manifest("add_model", inputs={"model_name": "b"}, status="applied")
    m3 = create_manifest("task_scaffold", inputs={"task_name": "c"}, status="ready")
    result = list_pending_manifests()
    ids = [m["id"] for m in result]
    assert m1["id"] in ids
    assert m3["id"] in ids
    assert m2["id"] not in ids


def test_list_pending_manifests_excludes_expired():
    """list_pending_manifests() must exclude expired manifests."""
    from lab_portal import create_manifest, list_pending_manifests
    with patch("lab_portal.time.time", return_value=100):
        old = create_manifest("add_model", inputs={"model_name": "old"}, status="ready")
    with patch("lab_portal.time.time", return_value=100 + 4 * 60 * 60 + 1):
        result = list_pending_manifests()
    assert all(m["id"] != old["id"] for m in result)


def test_change_summary_by_root_groups_operations():
    """change_summary_by_root(manifest_id) groups create/modify/delete counts by root."""
    from lab_portal import create_manifest, change_summary_by_root
    m = create_manifest("add_model", operations=[
        {"action": "create", "root": "DX_APP_ROOT", "path": "a.py", "exists": False, "preview": "", "risk": "low"},
        {"action": "modify", "root": "DX_APP_ROOT", "path": "b.py", "exists": True, "preview": "", "risk": "low"},
        {"action": "create", "root": "OUTPUTS_DIR", "path": "c.py", "exists": False, "preview": "", "risk": "low"},
        {"action": "delete", "root": "DX_APP_ROOT", "path": "d.py", "exists": True, "preview": "", "risk": "high"},
    ])
    result, code = change_summary_by_root(m["id"])
    assert code == 200
    assert result["DX_APP_ROOT"]["create"] == 1
    assert result["DX_APP_ROOT"]["modify"] == 1
    assert result["DX_APP_ROOT"]["delete"] == 1
    assert result["OUTPUTS_DIR"]["create"] == 1


def test_change_summary_by_root_expired_manifest():
    """change_summary_by_root returns 404 for expired manifests."""
    from lab_portal import change_summary_by_root
    result, code = change_summary_by_root("lab_nonexistent_id")
    assert code == 404
    assert result["error_code"] == "manifest_expired"


def test_rollback_manifest_rejects_unsupported():
    """rollback_manifest rejects manifests with rollback.supported === false."""
    from lab_portal import create_manifest, rollback_manifest
    m = create_manifest("add_model", rollback={"supported": False, "operations": []})
    result, code = rollback_manifest(m["id"], {})
    assert code == 400
    assert result["error_code"] == "rollback_unsupported"
    assert "instructions" in result or "message" in result


def test_rollback_manifest_requires_delete_confirmation():
    """Rollback with delete operations requires delete:<model_name> confirmation."""
    from lab_portal import create_manifest, rollback_manifest
    m = create_manifest(
        "add_model",
        inputs={"model_name": "demo"},
        rollback={
            "supported": True,
            "operations": [
                {"action": "delete", "root": "DX_APP_ROOT", "path": "demo/file.py", "exists": True, "preview": "", "risk": "high"},
            ],
        },
        confirmations=[{"key": "delete", "expected": "delete:demo", "label": "Delete demo"}],
    )
    result, code = rollback_manifest(m["id"], {})
    assert code == 400
    assert result["error_code"] == "confirmation_required"


def test_scoped_git_plan_returns_manifest_paths():
    """scoped_git_plan returns file paths derived from manifest operations."""
    from lab_portal import create_manifest, scoped_git_plan
    m = create_manifest("add_model", operations=[
        {"action": "create", "root": "DX_APP_ROOT", "path": "a.py", "exists": False, "preview": "", "risk": "low"},
        {"action": "modify", "root": "DX_APP_ROOT", "path": "b.py", "exists": True, "preview": "", "risk": "low"},
    ], status="applied")
    result, code = scoped_git_plan(m["id"], {})
    assert code == 200
    assert "files" in result
    assert set(result["files"]) == {"a.py", "b.py"}
    assert result.get("preview_only") is True


def test_scoped_git_plan_rejects_paths_not_in_manifest():
    """scoped_git_plan rejects file list with paths not present in manifest operations."""
    from lab_portal import create_manifest, scoped_git_plan
    m = create_manifest("add_model", operations=[
        {"action": "create", "root": "DX_APP_ROOT", "path": "a.py", "exists": False, "preview": "", "risk": "low"},
    ], status="applied")
    result, code = scoped_git_plan(m["id"], {"files": ["a.py", "evil.py"]})
    assert code == 400
    assert result["error_code"] == "path_not_in_manifest"


def test_scoped_git_plan_requires_push_confirmation():
    """scoped_git_plan with push=true requires explicit 'push' confirmation."""
    from lab_portal import create_manifest, scoped_git_plan
    m = create_manifest("add_model", operations=[
        {"action": "create", "root": "DX_APP_ROOT", "path": "a.py", "exists": False, "preview": "", "risk": "low"},
    ], status="applied")
    result, code = scoped_git_plan(m["id"], {"push": True})
    assert code == 400
    assert result["error_code"] == "confirmation_required"


def test_scoped_git_plan_expired_manifest():
    """scoped_git_plan returns 404 for expired manifests."""
    from lab_portal import scoped_git_plan
    result, code = scoped_git_plan("lab_nonexistent_id", {})
    assert code == 404
    assert result["error_code"] == "manifest_expired"


def test_manifests_route_returns_pending_list():
    """GET /api/lab/manifests returns pending manifest list."""
    import types
    import server
    from developer import lab_session
    from lab_portal import create_manifest
    tok = lab_session()["token"]
    m = create_manifest("add_model", inputs={"model_name": "demo"}, status="ready")
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/manifests"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 200
    assert isinstance(captured["data"]["manifests"], list)
    assert any(m2["id"] == m["id"] for m2 in captured["data"]["manifests"])


def test_manifests_route_includes_backend_change_summary():
    """GET /api/lab/manifests must expose backend-computed change_summary."""
    import types
    import server
    from developer import lab_session
    from lab_portal import create_manifest
    tok = lab_session()["token"]
    m = create_manifest("add_model", operations=[
        {"action": "create", "root": "DX_APP_ROOT", "path": "x.py", "exists": False, "preview": "", "risk": "low"},
        {"action": "delete", "root": "DX_APP_ROOT", "path": "old.py", "exists": True, "preview": "", "risk": "high"},
        {"action": "modify", "root": "OUTPUTS_DIR", "path": "out.txt", "exists": True, "preview": "", "risk": "low"},
    ], status="ready")
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/manifests"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 200
    item = next(m2 for m2 in captured["data"]["manifests"] if m2["id"] == m["id"])
    assert item["change_summary"]["DX_APP_ROOT"]["create"] == 1
    assert item["change_summary"]["DX_APP_ROOT"]["delete"] == 1
    assert item["change_summary"]["OUTPUTS_DIR"]["modify"] == 1


def test_manifests_route_requires_lab_token():
    """GET /api/lab/manifests without X-Lab-Token must return 403."""
    import types
    import server
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "GET"
    handler.url_path = "/api/lab/manifests"
    handler.query = {}
    handler.headers = {"Origin": "http://localhost:8080"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_rollback_route_requires_lab_token():
    """POST /api/lab/rollback without X-Lab-Token must return 403."""
    import types
    import server
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/rollback"
    handler.query = {}
    handler.headers = {"Origin": "http://localhost:8080"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"manifest_id": "lab_missing_123"}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_git_plan_route_rejects_hostile_origin():
    """POST /api/lab/git/plan from hostile origin must return 403."""
    import types
    import server
    from developer import lab_session
    tok = lab_session()["token"]
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/git/plan"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "https://evil.example.com"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"manifest_id": "lab_missing_123"}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 403


def test_rollback_route_rejects_unsupported():
    """POST /api/lab/rollback rejects rollback.supported === false."""
    import types
    import server
    from developer import lab_session
    from lab_portal import create_manifest
    tok = lab_session()["token"]
    m = create_manifest("add_model", rollback={"supported": False, "operations": []})
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/rollback"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"manifest_id": m["id"]}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 400
    assert captured["data"]["error_code"] == "rollback_unsupported"


def test_git_plan_route_returns_preview():
    """POST /api/lab/git/plan returns scoped preview."""
    import types
    import server
    from developer import lab_session
    from lab_portal import create_manifest
    tok = lab_session()["token"]
    m = create_manifest("add_model", operations=[
        {"action": "create", "root": "DX_APP_ROOT", "path": "x.py", "exists": False, "preview": "", "risk": "low"},
    ], status="applied")
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/git/plan"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"manifest_id": m["id"]}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 200
    assert "x.py" in captured["data"]["files"]
    assert captured["data"]["preview_only"] is True


def test_git_plan_route_rejects_outside_paths():
    """POST /api/lab/git/plan rejects files not in manifest."""
    import types
    import server
    from developer import lab_session
    from lab_portal import create_manifest
    tok = lab_session()["token"]
    m = create_manifest("add_model", operations=[
        {"action": "create", "root": "DX_APP_ROOT", "path": "x.py", "exists": False, "preview": "", "risk": "low"},
    ], status="applied")
    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = "/api/lab/git/plan"
    handler.query = {}
    handler.headers = {"X-Lab-Token": tok, "Origin": "http://localhost:8080"}
    handler.server = types.SimpleNamespace(server_name="localhost")
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: {"manifest_id": m["id"], "files": ["x.py", "evil.py"]}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *a, **kw: captured.update({"code": code})
    handler.route()
    assert captured["code"] == 400
    assert captured["data"]["error_code"] == "path_not_in_manifest"


def test_overwrite_confirmation_requires_manifest_specific_value():
    """Overwrite confirmation must match manifest-specific expected value."""
    from lab_portal import create_manifest, rollback_manifest
    m = create_manifest(
        "add_model",
        inputs={"model_name": "demo"},
        rollback={
            "supported": True,
            "operations": [
                {"action": "modify", "root": "DX_APP_ROOT", "path": "demo/file.py", "exists": True, "preview": "", "risk": "medium"},
            ],
        },
        confirmations=[{"key": "overwrite", "expected": "overwrite:demo", "label": "Overwrite demo"}],
    )
    result, code = rollback_manifest(m["id"], {"confirmations": {"overwrite": "wrong_value"}})
    assert code == 400
    assert result["error_code"] == "confirmation_required"

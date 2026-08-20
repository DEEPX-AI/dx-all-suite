"""RED route contracts for session-protected Lab Composer APIs."""

import pytest


COMPOSER_ROUTES = (
    "/api/lab/composer/quick_start",
    "/api/lab/composer/template",
    "/api/lab/composer/customize",
    "/api/lab/composer/plugin/apply",
    "/api/lab/composer/run",
    "/api/lab/composer/export",
    "/api/lab/composer/recipe/export",
    "/api/lab/composer/recipe/import",
)


def _ready_workflow():
    return {
        "schema_version": 1,
        "id": "workflow_route_test",
        "source": "quick_start",
        "template_id": None,
        "model": {
            "name": "resnet18",
            "category": "classification",
            "model_file": "assets/models/resnet18_224x224.dxnn",
            "language": "cpp",
            "variant": "sync",
        },
        "input": {"kind": "image", "path": "sample/img/sample_dog.jpg"},
        "nodes": [
            {"id": "input", "kind": "input", "enabled": True, "params": {}},
            {"id": "preprocess", "kind": "builtin_preprocess", "enabled": True, "params": {}},
            {"id": "inference", "kind": "inference", "enabled": True, "params": {}},
            {"id": "postprocess", "kind": "builtin_postprocess", "enabled": True, "params": {}},
            {"id": "visualize", "kind": "builtin_visualizer", "enabled": True, "params": {}},
        ],
        "plugins": [],
        "execution": {"device_id": None, "save_output": True},
        "validation": {"status": "ready", "blockers": [], "warnings": []},
    }


def _canonical_graph_layout():
    return {
        "version": 1,
        "nodes": [
            {"id": "input", "x": 120, "y": 160},
            {"id": "preprocess", "x": 360, "y": 160},
            {"id": "inference", "x": 600, "y": 160},
            {"id": "postprocess", "x": 840, "y": 160},
            {"id": "visualize", "x": 1080, "y": 160},
        ],
        "edges": [
            {"id": "input-preprocess", "from": "input", "to": "preprocess"},
            {"id": "preprocess-inference", "from": "preprocess", "to": "inference"},
            {"id": "inference-postprocess", "from": "inference", "to": "postprocess"},
            {"id": "postprocess-visualize", "from": "postprocess", "to": "visualize"},
        ],
        "viewport": {"zoom": 1.25, "offset_x": 12, "offset_y": -20},
    }

def _post_route(path, payload, headers=None):
    import server

    captured = {}
    handler = object.__new__(server.Handler)
    handler.command = "POST"
    handler.url_path = path
    handler.query = {}
    handler.headers = headers or {}
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: payload
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *args, **kwargs: captured.update({"code": code})
    handler.route()
    return captured


@pytest.mark.parametrize("path", COMPOSER_ROUTES)
def test_composer_routes_require_x_lab_token(path):
    captured = _post_route(path, {}, headers={"Origin": "http://localhost:8080"})
    assert captured["code"] == 403
    assert captured["data"]["error"] == "Lab session required"


@pytest.mark.parametrize("path", COMPOSER_ROUTES)
def test_composer_routes_reject_hostile_origin_even_with_valid_token(path):
    from developer import lab_session

    token = lab_session()["token"]
    captured = _post_route(
        path,
        {},
        headers={"X-Lab-Token": token, "Origin": "https://evil.example.com"},
    )
    assert captured["code"] == 403
    assert captured["data"]["error"] == "Cross-origin access denied"


def test_plugin_scaffold_preview_route_requires_local_lab_session():
    from developer import lab_session

    missing_token = _post_route(
        "/api/lab/composer/plugin/dry_run",
        {},
        headers={"Origin": "http://localhost:8080"},
    )
    hostile_origin = _post_route(
        "/api/lab/composer/plugin/dry_run",
        {},
        headers={"X-Lab-Token": lab_session()["token"], "Origin": "https://evil.example.com"},
    )

    assert missing_token["code"] == 403
    assert missing_token["data"]["error"] == "Lab session required"
    assert hostile_origin["code"] == 403
    assert hostile_origin["data"]["error"] == "Cross-origin access denied"


def test_plugin_scaffold_preview_route_returns_a_session_bound_dry_run_manifest(tmp_path, monkeypatch):
    import lab_portal
    from developer import lab_session

    planner = getattr(lab_portal, "plan_composer_plugin_scaffold_response", None)
    assert callable(planner)

    token = lab_session()["token"]
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", tmp_path / "outputs")
    workflow_manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=token
    )
    captured = _post_route(
        "/api/lab/composer/plugin/dry_run",
        {
            "workflow_manifest_id": workflow_manifest["id"],
            "plugin_name": "custom_preprocess",
            "stage": "preprocess",
            "language": "python",
        },
        headers={"X-Lab-Token": token, "Origin": "http://localhost:8080"},
    )

    assert captured["code"] == 200
    assert captured["data"]["kind"] == "composer_plugin_scaffold"
    assert captured["data"]["creator_token"] == token


def test_composer_run_rejects_expired_workflow_without_invoking_inference(monkeypatch):
    import lab_portal
    from developer import lab_session

    manifest = lab_portal.create_manifest(
        "composer_workflow",
        workflow={"validation": {"status": "ready"}},
    )
    with lab_portal._manifests_lock:
        lab_portal._manifests[manifest["id"]]["created_at"] = 0
    monkeypatch.setattr(
        lab_portal,
        "run_inference",
        lambda **kwargs: pytest.fail("Expired workflow must not invoke inference"),
        raising=False,
    )

    captured = _post_route(
        "/api/lab/composer/run",
        {"manifest_id": manifest["id"]},
        headers={"X-Lab-Token": lab_session()["token"], "Origin": "http://localhost:8080"},
    )

    assert captured["code"] == 404
    assert captured["data"]["error_code"] == "manifest_expired"


def test_composer_manifest_is_bound_to_its_creator_session():
    import lab_portal
    from developer import lab_session

    creator_token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow",
        workflow={"validation": {"status": "ready"}},
        creator_token=creator_token,
    )

    assert manifest["creator_token"] == creator_token
    assert lab_portal.resolve_manifest(manifest["id"], token=creator_token)["id"] == manifest["id"]
    with pytest.raises(PermissionError, match="session|creator|owner"):
        lab_portal.resolve_manifest(manifest["id"], token="different-lab-session")


def test_composer_planners_issue_owner_bound_manifests_from_current_registry(monkeypatch):
    import lab_portal
    from developer import lab_session

    model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    monkeypatch.setattr(lab_portal, "get_models", lambda: [model], raising=False)
    monkeypatch.setattr(
        lab_portal, "get_images", lambda category: ["sample/img/sample_dog.jpg"], raising=False
    )
    monkeypatch.setattr(lab_portal, "get_videos", lambda *a, **k: ["sample/video/sample.mp4"], raising=False)
    token = lab_session()["token"]

    quick, quick_code = lab_portal.plan_composer_quick_start(
        token, {"selection": {"name": "resnet18", "category": "classification"}}
    )
    template, template_code = lab_portal.plan_composer_template(
        token, {"template_id": "classification_image"}
    )

    assert quick_code == template_code == 200
    assert quick["manifest_id"]
    assert quick["workflow"]["model"]["model_file"] == model["model_file"]
    assert template["workflow"]["template_id"] == "classification_image"
    assert lab_portal.resolve_manifest(quick["manifest_id"], token=token)["creator_token"] == token
    with pytest.raises(PermissionError, match="session|creator|owner"):
        lab_portal.resolve_manifest(quick["manifest_id"], token="another-valid-lab-token")


def test_composer_quick_start_accepts_documented_selection_payload(monkeypatch):
    import lab_portal
    from developer import lab_session

    model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    monkeypatch.setattr(lab_portal, "get_models", lambda: [model], raising=False)
    monkeypatch.setattr(
        lab_portal, "get_images", lambda category: ["sample/img/sample_dog.jpg"], raising=False
    )

    result, code = lab_portal.plan_composer_quick_start(
        lab_session()["token"],
        {"selection": {"name": "resnet18", "category": "classification"}},
    )

    assert code == 200
    assert result["status"] == "ready"
    assert result["workflow"]["model"] == {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "language": "cpp",
        "variant": "sync",
    }


def test_composer_template_honors_requested_compatible_model_without_fallback(monkeypatch):
    import lab_portal
    from developer import lab_session

    first_detection = {
        "name": "first_detection",
        "category": "object_detection",
        "model_file": "assets/models/first_detection.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    requested_detection = {
        "name": "requested_detection",
        "category": "object_detection",
        "model_file": "assets/models/requested_detection.dxnn",
        "model_exists": True,
        "py_sync": True,
    }
    classification = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    monkeypatch.setattr(
        lab_portal,
        "get_models",
        lambda: [first_detection, requested_detection, classification],
        raising=False,
    )
    monkeypatch.setattr(
        lab_portal, "get_images", lambda category: ["sample/img/sample_dog.jpg"], raising=False
    )
    monkeypatch.setattr(lab_portal, "get_videos", lambda *a, **k: [], raising=False)
    token = lab_session()["token"]

    selected, selected_code = lab_portal.plan_composer_template(
        token,
        {"template_id": "detection_image", "model_name": "requested_detection"},
    )
    incompatible, incompatible_code = lab_portal.plan_composer_template(
        token,
        {"template_id": "detection_image", "model_name": "resnet18"},
    )

    assert selected_code == 200
    assert selected["status"] == "ready"
    assert selected["workflow"]["model"]["name"] == "requested_detection"
    assert incompatible_code == 400
    assert incompatible["error_code"] == "template_model_mismatch"
    assert "resnet18" in incompatible["error"]
    assert "object_detection" in incompatible["error"]


def test_composer_route_rejects_cross_token_manifest_owner(monkeypatch):
    import lab_portal
    from developer import lab_session

    token = lab_session()["token"]
    other_token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=token
    )
    monkeypatch.setattr(
        lab_portal,
        "run_inference",
        lambda **kwargs: pytest.fail("Wrong owner must not invoke inference"),
        raising=False,
    )

    captured = _post_route(
        "/api/lab/composer/run",
        {"manifest_id": manifest["id"]},
        headers={"X-Lab-Token": other_token, "Origin": "http://localhost:8080"},
    )

    assert captured["code"] == 403
    assert captured["data"]["error_code"] == "manifest_owner_forbidden"


def test_composer_run_rejects_blocked_workflow_without_invoking_inference(monkeypatch):
    import lab_portal
    from developer import lab_session

    token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow",
        workflow={"validation": {"status": "blocked", "blockers": [{"node_id": "inference", "code": "inference_required"}]}},
        status="blocked",
        creator_token=token,
    )
    monkeypatch.setattr(
        lab_portal,
        "run_inference",
        lambda **kwargs: pytest.fail("Blocked workflow must not invoke inference"),
        raising=False,
    )

    captured = _post_route(
        "/api/lab/composer/run",
        {"manifest_id": manifest["id"]},
        headers={"X-Lab-Token": token, "Origin": "http://localhost:8080"},
    )

    assert captured["code"] == 400
    assert captured["data"]["error_code"] == "workflow_blocked"


def test_recipe_export_returns_portable_recipe_and_enforces_workflow_ownership():
    import lab_portal
    from developer import lab_session

    owner_token = lab_session()["token"]
    other_token = lab_session()["token"]
    ready_manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=owner_token
    )

    exported = _post_route(
        "/api/lab/composer/recipe/export",
        {"manifest_id": ready_manifest["id"]},
        headers={"X-Lab-Token": owner_token, "Origin": "http://localhost:8080"},
    )

    assert exported["code"] == 200
    recipe = exported["data"]["recipe"]
    assert recipe["schema_version"] == 1
    assert "model_file" not in recipe["model"]
    assert recipe["input"] == {"kind": "image"}

    blocked_workflow = _ready_workflow()
    blocked_workflow["nodes"] = [
        node for node in blocked_workflow["nodes"] if node["id"] != "inference"
    ]
    blocked_manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=blocked_workflow, status="blocked", creator_token=owner_token
    )
    blocked = _post_route(
        "/api/lab/composer/recipe/export",
        {"manifest_id": blocked_manifest["id"]},
        headers={"X-Lab-Token": owner_token, "Origin": "http://localhost:8080"},
    )

    assert blocked["code"] == 400
    assert blocked["data"]["error_code"] == "workflow_blocked"

    forbidden = _post_route(
        "/api/lab/composer/recipe/export",
        {"manifest_id": ready_manifest["id"]},
        headers={"X-Lab-Token": other_token, "Origin": "http://localhost:8080"},
    )

    assert forbidden["code"] == 403
    assert forbidden["data"]["error_code"] == "manifest_owner_forbidden"


def test_recipe_export_validates_completed_plugins_from_the_controlled_workspace(monkeypatch, tmp_path):
    import lab_portal
    from developer import lab_session

    token = lab_session()["token"]
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", tmp_path / "outputs")
    workflow = _ready_workflow()
    workflow["plugins"] = [{
        "id": "custom_preprocess",
        "stage": "preprocess",
        "language": "python",
        "entrypoint": "plugins/preprocess/custom_preprocess.py",
        "interface_version": 1,
        "enabled": True,
    }]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=workflow, creator_token=token
    )
    plugin = (
        lab_portal.OUTPUTS_DIR / "lab_composer" / manifest["id"] / "plugins" /
        "preprocess" / "custom_preprocess.py"
    )
    plugin.parent.mkdir(parents=True)
    plugin.write_text("def preprocess(image, context):\n    return image\n", encoding="utf-8")

    exported, code = lab_portal.export_composer_recipe(token, {"manifest_id": manifest["id"]})

    assert code == 200
    assert exported["recipe"]["plugins"] == workflow["plugins"]


def test_composer_run_converts_server_manifest_to_precise_inference_values(monkeypatch):
    import lab_portal
    from developer import lab_session

    workflow = _ready_workflow()
    workflow["model"]["model_file"] = "browser-supplied-stale.dxnn"
    token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=workflow, creator_token=token
    )
    invoked = {}

    def record_inference(**kwargs):
        invoked.update(kwargs)
        return {"status": "ok"}

    monkeypatch.setattr(lab_portal, "run_inference", record_inference, raising=False)
    monkeypatch.setattr(
        lab_portal,
        "get_models",
        lambda: [{
            "name": "resnet18",
            "category": "classification",
            "model_file": "assets/models/current_resnet18.dxnn",
            "model_exists": True,
            "cpp_sync": True,
        }],
        raising=False,
    )

    captured = _post_route(
        "/api/lab/composer/run",
        {"manifest_id": manifest["id"]},
        headers={"X-Lab-Token": token, "Origin": "http://localhost:8080"},
    )

    assert captured["code"] == 200
    assert invoked == {
        "model_name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/current_resnet18.dxnn",
        "lang": "cpp",
        "variant": "sync",
        "input_type": "image",
        "image_path": "sample/img/sample_dog.jpg",
        "video_path": None,
        "device_id": None,
        "save_output": True,
    }


def test_composer_run_validates_completed_plugins_from_the_controlled_workspace(tmp_path, monkeypatch):
    import lab_portal
    from developer import lab_session

    token = lab_session()["token"]
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", tmp_path / "outputs")
    workflow = _ready_workflow()
    workflow["plugins"] = [{
        "id": "custom_preprocess",
        "stage": "preprocess",
        "language": "python",
        "entrypoint": "plugins/preprocess/custom_preprocess.py",
        "interface_version": 1,
        "enabled": True,
    }]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=workflow, creator_token=token
    )
    plugin = (
        lab_portal.OUTPUTS_DIR / "lab_composer" / manifest["id"] / "plugins" /
        "preprocess" / "custom_preprocess.py"
    )
    plugin.parent.mkdir(parents=True)
    plugin.write_text("def preprocess(image, context):\n    return image\n", encoding="utf-8")
    monkeypatch.setattr(
        lab_portal,
        "get_models",
        lambda: [{
            "name": "resnet18",
            "category": "classification",
            "model_file": "assets/models/resnet18_224x224.dxnn",
            "model_exists": True,
            "cpp_sync": True,
        }],
    )
    invoked = {}
    monkeypatch.setattr(
        lab_portal,
        "run_inference",
        lambda **kwargs: invoked.update(kwargs) or {"status": "ok"},
    )

    result, code = lab_portal.run_composer_workflow(token, {"manifest_id": manifest["id"]})

    assert code == 200
    assert result == {"status": "ok"}
    assert invoked["model_name"] == "resnet18"


def test_composer_customize_applies_only_whitelisted_execution_updates():
    import lab_portal
    from developer import lab_session

    customize = getattr(lab_portal, "customize_composer_workflow", None)
    assert callable(customize)

    token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=token
    )
    updated, updated_code = customize(
        token,
        {
            "manifest_id": manifest["id"],
            "updates": {"execution": {"save_output": False}},
        },
    )
    rejected, rejected_code = customize(
        token,
        {
            "manifest_id": manifest["id"],
            "updates": {"model": {"model_file": "/browser-controlled.dxnn"}},
        },
    )

    assert updated_code == 200
    assert updated["status"] == "ready"
    assert updated["workflow"]["execution"] == {"device_id": None, "save_output": False}
    assert rejected_code == 400
    assert rejected["error_code"] == "workflow_patch_forbidden"
    assert lab_portal.resolve_manifest(manifest["id"], token=token)["workflow"]["model"]["model_file"] == (
        "assets/models/resnet18_224x224.dxnn"
    )


def test_composer_customize_accepts_model_supported_postprocess_settings_and_exposes_capabilities(monkeypatch):
    import lab_portal
    from developer import lab_session

    model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    monkeypatch.setattr(lab_portal, "get_models", lambda: [model])
    monkeypatch.setattr(
        lab_portal, "load_model_config", lambda category, name: {"top_k": 5}, raising=False
    )
    token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=token
    )

    updated, status = lab_portal.customize_composer_workflow(
        token,
        {
            "manifest_id": manifest["id"],
            "updates": {
                "execution": {
                    "config_overrides": {"top_k": 3},
                    "postprocess_implementation": "standard",
                },
            },
        },
    )

    assert status == 200
    assert updated["workflow"]["execution"] == {
        "device_id": None,
        "save_output": True,
        "config_overrides": {"top_k": 3},
        "postprocess_implementation": "standard",
    }
    assert updated["processor_capabilities"] == {
        "preprocess": {"factory_owned": True},
        "postprocess": {
            "implementation_options": ["standard"],
            "tunable_defaults": {"top_k": 5},
            "tunable_keys": ["top_k"],
        },
    }


@pytest.mark.parametrize(
    "overrides",
    [
        {"unknown": 1},
        {"top_k": True},
        {"top_k": "3"},
        {"top_k": float("nan")},
        {"top_k": float("inf")},
        {"top_k": []},
        {"top_k": {"value": 3}},
    ],
)
def test_composer_customize_rejects_unsafe_or_unsupported_postprocess_overrides(monkeypatch, overrides):
    import lab_portal
    from developer import lab_session

    model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    monkeypatch.setattr(lab_portal, "get_models", lambda: [model])
    monkeypatch.setattr(
        lab_portal, "load_model_config", lambda category, name: {"top_k": 5}, raising=False
    )
    token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=token
    )

    result, status = lab_portal.customize_composer_workflow(
        token,
        {"manifest_id": manifest["id"], "updates": {"execution": {"config_overrides": overrides}}},
    )

    assert status == 400
    assert result["error_code"] == "workflow_patch_invalid"
    assert lab_portal.resolve_manifest(manifest["id"], token=token)["workflow"]["execution"] == {
        "device_id": None,
        "save_output": True,
    }


def test_composer_postprocess_implementation_is_registry_gated_and_resets_on_model_change(monkeypatch):
    import lab_portal
    from developer import lab_session

    cpp_postprocess_model = {
        "name": "supported_model",
        "category": "classification",
        "model_file": "assets/models/supported_model.dxnn",
        "model_exists": True,
        "py_sync": True,
        "py_sync_cpp_postprocess": True,
    }
    standard_model = {
        "name": "standard_model",
        "category": "classification",
        "model_file": "assets/models/standard_model.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    monkeypatch.setattr(lab_portal, "get_models", lambda: [cpp_postprocess_model, standard_model])
    monkeypatch.setattr(
        lab_portal, "load_model_config", lambda category, name: {}, raising=False
    )
    monkeypatch.setattr(
        lab_portal,
        "_workflow_assets",
        lambda category, input_kind: ["sample/img/sample_dog.jpg"],
    )
    token = lab_session()["token"]
    workflow = _ready_workflow()
    workflow["model"] = {
        "name": "supported_model",
        "category": "classification",
        "model_file": "assets/models/supported_model.dxnn",
        "language": "python",
        "variant": "sync",
    }
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=workflow, creator_token=token
    )

    configured, configured_status = lab_portal.customize_composer_workflow(
        token,
        {
            "manifest_id": manifest["id"],
            "updates": {"execution": {"postprocess_implementation": "cpp_postprocess"}},
        },
    )
    reset, reset_status = lab_portal.customize_composer_workflow(
        token,
        {
            "manifest_id": manifest["id"],
            "updates": {"model_selection": {"model_file": standard_model["model_file"]}},
        },
    )

    assert configured_status == reset_status == 200
    assert configured["workflow"]["execution"]["postprocess_implementation"] == "cpp_postprocess"
    assert reset["workflow"]["execution"]["postprocess_implementation"] == "standard"
    assert reset["processor_capabilities"]["postprocess"]["implementation_options"] == ["standard"]


def test_composer_run_passes_validated_postprocess_settings_to_the_registry_runner(monkeypatch):
    import lab_portal
    from developer import lab_session

    model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/current_resnet18.dxnn",
        "model_exists": True,
        "py_sync": True,
        "py_sync_cpp_postprocess": True,
    }
    workflow = _ready_workflow()
    workflow["execution"].update({
        "config_overrides": {"top_k": 3},
        "postprocess_implementation": "cpp_postprocess",
    })
    token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=workflow, creator_token=token
    )
    invoked = {}
    monkeypatch.setattr(lab_portal, "get_models", lambda: [model])
    monkeypatch.setattr(
        lab_portal, "load_model_config", lambda category, name: {"top_k": 5}, raising=False
    )
    monkeypatch.setattr(
        lab_portal,
        "run_inference",
        lambda **kwargs: invoked.update(kwargs) or {"status": "ok"},
    )

    result, status = lab_portal.run_composer_workflow(token, {"manifest_id": manifest["id"]})

    assert status == 200
    assert result == {"status": "ok"}
    assert invoked == {
        "model_name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/current_resnet18.dxnn",
        "lang": "python",
        "variant": "sync_cpp_postprocess",
        "input_type": "image",
        "image_path": "sample/img/sample_dog.jpg",
        "video_path": None,
        "device_id": None,
        "save_output": True,
        "config_overrides": {"top_k": 3},
    }


def test_composer_recipe_round_trips_validated_processor_settings(monkeypatch):
    import lab_portal
    from developer import lab_session

    model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "py_sync": True,
        "py_sync_cpp_postprocess": True,
    }
    monkeypatch.setattr(lab_portal, "get_models", lambda: [model])
    monkeypatch.setattr(lab_portal, "get_images", lambda category: ["sample/img/sample_dog.jpg"])
    monkeypatch.setattr(lab_portal, "get_videos", lambda *a, **k: [])
    monkeypatch.setattr(
        lab_portal, "load_model_config", lambda category, name: {"top_k": 5}, raising=False
    )
    token = lab_session()["token"]
    workflow = _ready_workflow()
    workflow["execution"].update({
        "config_overrides": {"top_k": 3},
        "postprocess_implementation": "cpp_postprocess",
    })
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=workflow, creator_token=token
    )

    exported, export_status = lab_portal.export_composer_recipe(
        token, {"manifest_id": manifest["id"]}
    )
    imported, import_status = lab_portal.import_composer_recipe(
        token, {"recipe": exported["recipe"]}
    )

    assert export_status == import_status == 200
    assert exported["recipe"]["execution"] == workflow["execution"]
    assert imported["workflow"]["execution"] == workflow["execution"]


def test_composer_customize_persists_only_a_canonical_graph_layout():
    import lab_portal
    from developer import lab_session

    token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=token
    )
    layout = _canonical_graph_layout()

    updated, status = lab_portal.customize_composer_workflow(
        token,
        {"manifest_id": manifest["id"], "updates": {"graph_layout": layout}},
    )

    assert status == 200
    assert updated["status"] == "ready"
    assert updated["workflow"]["graph_layout"] == layout
    assert lab_portal.resolve_manifest(manifest["id"], token=token)["workflow"]["graph_layout"] == layout


@pytest.mark.parametrize(
    "layout",
    [
        None,
        [],
        {**_canonical_graph_layout(), "unexpected": True},
    ],
)
def test_composer_customize_rejects_malformed_graph_layout_patches(layout):
    import lab_portal
    from developer import lab_session

    token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=token
    )

    result, status = lab_portal.customize_composer_workflow(
        token,
        {"manifest_id": manifest["id"], "updates": {"graph_layout": layout}},
    )

    assert status == 400
    assert result["error_code"] == "workflow_patch_invalid"
    assert "graph_layout" not in lab_portal.resolve_manifest(manifest["id"], token=token)["workflow"]


def test_composer_recipe_round_trips_canonical_graph_layout(monkeypatch):
    import lab_portal
    from developer import lab_session

    model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    monkeypatch.setattr(lab_portal, "get_models", lambda: [model])
    monkeypatch.setattr(lab_portal, "get_images", lambda category: ["sample/img/sample_dog.jpg"])
    monkeypatch.setattr(lab_portal, "get_videos", lambda *a, **k: [])
    token = lab_session()["token"]
    workflow = _ready_workflow()
    workflow["graph_layout"] = _canonical_graph_layout()
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=workflow, creator_token=token
    )

    exported, export_status = lab_portal.export_composer_recipe(
        token, {"manifest_id": manifest["id"]}
    )
    imported, import_status = lab_portal.import_composer_recipe(
        token, {"recipe": exported["recipe"]}
    )

    assert export_status == import_status == 200
    assert exported["recipe"]["graph_layout"] == _canonical_graph_layout()
    assert imported["workflow"]["graph_layout"] == _canonical_graph_layout()


def test_composer_customize_resolves_only_registry_models_and_compatible_assets(monkeypatch):
    import lab_portal
    from developer import lab_session

    token = lab_session()["token"]
    selected = {
        "name": "yolov8n",
        "category": "object_detection",
        "model_file": "assets/models/yolov8n.dxnn",
        "model_exists": True,
        "cpp_sync": True,
        "py_sync": False,
    }
    monkeypatch.setattr(lab_portal, "get_models", lambda: [selected])
    monkeypatch.setattr(
        lab_portal,
        "_workflow_assets",
        lambda category, input_kind: ["sample/img/detection.jpg", "sample/img/alternate.jpg"],
    )
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=token
    )

    updated, code = lab_portal.customize_composer_workflow(
        token,
        {
            "manifest_id": manifest["id"],
            "updates": {"model_selection": {"model_file": selected["model_file"]}},
        },
    )
    asset_updated, asset_code = lab_portal.customize_composer_workflow(
        token,
        {
            "manifest_id": manifest["id"],
            "updates": {"input_selection": {"path": "sample/img/alternate.jpg"}},
        },
    )
    rejected, rejected_code = lab_portal.customize_composer_workflow(
        token,
        {
            "manifest_id": manifest["id"],
            "updates": {"input_selection": {"path": "/browser-controlled.jpg"}},
        },
    )

    assert code == 200
    assert updated["workflow"]["model"] == {
        "name": "yolov8n",
        "category": "object_detection",
        "model_file": "assets/models/yolov8n.dxnn",
        "language": "cpp",
        "variant": "sync",
    }
    assert updated["workflow"]["input"] == {"kind": "image", "path": "sample/img/detection.jpg"}
    assert asset_code == 200
    assert asset_updated["workflow"]["input"]["path"] == "sample/img/alternate.jpg"
    assert rejected_code == 400
    assert rejected["error_code"] == "workflow_patch_invalid"


def test_composer_customize_retains_default_resolution_blockers():
    import lab_portal
    from developer import lab_session

    token = lab_session()["token"]
    workflow = _ready_workflow()
    workflow["model"] = {}
    workflow["plugins"] = [{
        "id": "custom_preprocess",
        "stage": "preprocess",
        "language": "python",
        "entrypoint": "plugins/preprocess/custom_preprocess.py",
        "interface_version": 1,
        "enabled": True,
    }]
    workflow["validation"] = {
        "status": "blocked",
        "blockers": [
            {"node_id": "model", "code": "runnable_model_not_found"},
            {"node_id": "custom_preprocess", "code": "plugin_incomplete"},
        ],
        "warnings": [],
    }
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=workflow, creator_token=token
    )

    updated, code = lab_portal.customize_composer_workflow(
        token,
        {
            "manifest_id": manifest["id"],
            "updates": {
                "execution": {"save_output": False},
                "plugins": [{"id": "custom_preprocess", "enabled": False}],
            },
        },
    )

    assert code == 200
    assert {"node_id": "model", "code": "runnable_model_not_found"} in updated["validation"]["blockers"]
    assert {"node_id": "custom_preprocess", "code": "plugin_incomplete"} not in updated["validation"]["blockers"]


def test_resolution_blocker_updates_are_scoped_to_the_target_node():
    import lab_portal

    workflow = {
        "validation": {
            "status": "blocked",
            "blockers": [
                {"node_id": "model", "code": "runnable_model_not_found"},
                {"node_id": "future_node", "code": "runnable_model_not_found"},
            ],
            "warnings": [],
        },
    }

    lab_portal._set_composer_resolution_blocker(
        workflow, "model", "runnable_model_not_found", False
    )

    assert workflow["validation"]["blockers"] == [
        {"node_id": "future_node", "code": "runnable_model_not_found"},
    ]


def test_composer_plugin_apply_writes_only_the_confirmed_scaffold_and_blocks_incomplete_plugin(monkeypatch, tmp_path):
    import lab_portal
    from developer import lab_session

    apply_scaffold = getattr(lab_portal, "apply_composer_plugin_scaffold", None)
    assert callable(apply_scaffold)

    token = lab_session()["token"]
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", tmp_path / "outputs")
    workflow_manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=token
    )
    scaffold = lab_portal.plan_composer_plugin_scaffold(
        token,
        {
            "workflow_manifest_id": workflow_manifest["id"],
            "plugin_name": "custom_preprocess",
            "stage": "preprocess",
            "language": "python",
        },
    )
    applied, code = apply_scaffold(token, {"plugin_manifest_id": scaffold["id"]})

    assert code == 200
    assert applied["status"] == "blocked"
    assert applied["workflow"]["plugins"] == [{
        "id": "custom_preprocess",
        "stage": "preprocess",
        "language": "python",
        "entrypoint": "plugins/preprocess/custom_preprocess.py",
        "interface_version": 1,
        "enabled": True,
    }]
    plugin = tmp_path / "outputs" / "lab_composer" / workflow_manifest["id"] / "plugins" / "preprocess" / "custom_preprocess.py"
    assert plugin.is_file()
    assert {"node_id": "custom_preprocess", "code": "plugin_incomplete"} in applied["validation"]["blockers"]


def test_composer_export_builds_owned_ready_package_and_returns_download_metadata(monkeypatch, tmp_path):
    import lab_portal
    from developer import lab_session

    token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=token
    )
    registry_model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/current_resnet18.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    captured_build = {}
    monkeypatch.setattr(lab_portal, "OUTPUTS_DIR", tmp_path / "outputs")
    archive = lab_portal.OUTPUTS_DIR / "lab_packages" / "workflow_route_test-demo.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_bytes(b"portable package archive")

    def build_package(**kwargs):
        captured_build.update(kwargs)
        return {
            "archive_path": archive,
            "download_name": archive.name,
            "copy_out_verified": True,
        }

    monkeypatch.setattr(lab_portal, "get_models", lambda: [registry_model], raising=False)
    monkeypatch.setattr(lab_portal, "build_workflow_package", build_package, raising=False)

    exported = _post_route(
        "/api/lab/composer/export",
        {"manifest_id": manifest["id"], "package_type": "run"},
        headers={"X-Lab-Token": token, "Origin": "http://localhost:8080"},
    )

    assert exported["code"] == 200
    assert captured_build["package_type"] == "run"
    assert captured_build["source_root"] == lab_portal.DX_APP_ROOT
    assert captured_build["output_root"] == lab_portal.OUTPUTS_DIR
    assert captured_build["workflow"]["model"]["model_file"] == registry_model["model_file"]
    assert exported["data"] == {
        "package_type": "run",
        "download": {
            "name": "workflow_route_test-demo.zip",
            "url": "/outputs/lab_packages/workflow_route_test-demo.zip",
        },
        "copy_out_verified": True,
    }


def test_composer_export_rejects_invalid_type_and_other_session(monkeypatch):
    import lab_portal
    from developer import lab_session

    owner_token = lab_session()["token"]
    other_token = lab_session()["token"]
    manifest = lab_portal.create_manifest(
        "composer_workflow", workflow=_ready_workflow(), creator_token=owner_token
    )
    monkeypatch.setattr(
        lab_portal,
        "build_workflow_package",
        lambda **kwargs: pytest.fail("Invalid export requests must not build a package"),
        raising=False,
    )

    invalid = _post_route(
        "/api/lab/composer/export",
        {"manifest_id": manifest["id"], "package_type": "shell"},
        headers={"X-Lab-Token": owner_token, "Origin": "http://localhost:8080"},
    )
    forbidden = _post_route(
        "/api/lab/composer/export",
        {"manifest_id": manifest["id"], "package_type": "run"},
        headers={"X-Lab-Token": other_token, "Origin": "http://localhost:8080"},
    )

    assert invalid["code"] == 400
    assert invalid["data"]["error_code"] == "package_type_invalid"
    assert forbidden["code"] == 403
    assert forbidden["data"]["error_code"] == "manifest_owner_forbidden"


@pytest.mark.parametrize(
    "recipe",
    [
        {"schema_version": 2},
        {
            "schema_version": 1,
            "plugins": [{"id": "unsafe", "entrypoint": "../../outside.py"}],
        },
        {
            "schema_version": 1,
            "model": {"name": "download_only", "category": "classification"},
        },
    ],
)
def test_recipe_import_rejects_nonportable_or_unrunnable_content(recipe):
    from developer import lab_session

    captured = _post_route(
        "/api/lab/composer/recipe/import",
        {"recipe": recipe},
        headers={"X-Lab-Token": lab_session()["token"], "Origin": "http://localhost:8080"},
    )

    assert captured["code"] == 400
    assert captured["data"]["error_code"] in {
        "recipe_schema_unsupported",
        "plugin_path_unsafe",
        "runnable_model_not_found",
    }


def test_recipe_import_accepts_schema_one_safe_plugins_and_reresolves_model():
    import lab_portal

    registry_model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "cpp": True,
        "cpp_sync": True,
    }
    recipe = {
        "schema_version": 1,
        "model": {
            "name": "resnet18",
            "category": "classification",
            "language": "cpp",
            "variant": "sync",
        },
        "input": {"kind": "image"},
        "plugins": [{
            "id": "custom_postprocess",
            "stage": "postprocess",
            "language": "python",
            "entrypoint": "plugins/postprocess/clean.py",
            "interface_version": 1,
            "enabled": True,
        }],
    }

    workflow = lab_portal.import_recipe(recipe, models=[registry_model])

    assert workflow["schema_version"] == 1
    assert workflow["model"]["model_file"] == registry_model["model_file"]
    assert workflow["plugins"][0]["entrypoint"] == "plugins/postprocess/clean.py"


def test_recipe_import_resolves_a_real_video_asset_for_video_input():
    import lab_portal

    registry_model = {
        "name": "resnet18",
        "category": "classification",
        "model_file": "assets/models/resnet18_224x224.dxnn",
        "model_exists": True,
        "cpp_sync": True,
    }
    workflow = lab_portal.import_recipe(
        {
            "schema_version": 1,
            "model": {"name": "resnet18", "category": "classification"},
            "input": {"kind": "video"},
            "plugins": [],
        },
        models=[registry_model],
        images=["sample/img/sample_dog.jpg"],
        videos=["assets/videos/sample.mp4"],
    )

    assert workflow["input"] == {"kind": "video", "path": "assets/videos/sample.mp4"}
    assert workflow["validation"]["status"] == "ready"
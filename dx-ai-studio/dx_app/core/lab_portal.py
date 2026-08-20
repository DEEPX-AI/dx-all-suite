"""Lab Extension Portal backend helpers."""

import copy
import math
import re
import secrets
import threading
import time
from pathlib import Path
from collections import OrderedDict

from dx_app.core import config
from dx_app.core.config import DX_APP_ROOT, CPP_DIR, PY_DIR, OUTPUTS_DIR, TEMPLATES_DIR
from dx_app.core.developer import require_lab, _require_lab_model_name, _require_lab_category, dev_add, dev_new_task, build_task_file_plan
from dx_app.core.dx_app_security import resolve_existing_file, resolve_under
from dx_app.core.lab_workflow import (
    PACKAGE_TYPES,
    PLUGIN_INTERFACE_VERSION,
    PLUGIN_LANGUAGES,
    PLUGIN_STAGES,
    SUPPORTED_NODE_KINDS,
    WORKFLOW_SCHEMA_VERSION,
    WORKFLOW_TEMPLATES,
    build_quick_start_workflow,
    build_template_workflow,
    normalize_graph_layout,
    resolve_runnable_model,
    validate_graph_layout,
    validate_workflow,
)
from dx_app.core.models import get_models
from dx_app.core.assets import get_images, get_videos
from dx_app.core.demos import build_demos_payload
from dx_app.core.inference import run_inference
from dx_app.core.lab_package import build_workflow_package
from dx_app.core.run_config import RUN_TUNABLE_KEYS, load_model_config

SCRIPT_DIR = config.SCRIPT_DIR


def _error_response(err, default_status=400):
    """Return (body, http_code) from an error dict without mutating the original."""
    if not isinstance(err, dict):
        return {"error": str(err)}, default_status
    code = err.get("status", default_status)
    body = {k: v for k, v in err.items() if k != "status"}
    return body, code


def _result_with_http_status(result, default_status=200):
    """Extract HTTP status from an error result dict without mutating the original."""
    if isinstance(result, dict) and "error" in result and isinstance(result.get("status"), int):
        body = dict(result)
        code = body.pop("status")
        return body, code
    return result, default_status

MANIFEST_TTL_SECONDS = 4 * 60 * 60
MAX_MANIFESTS = 256
_manifests = OrderedDict()
_manifests_lock = threading.RLock()
_apply_locks = set()
_apply_lock_mutex = threading.Lock()
_PLUGIN_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_CPP_PLUGIN_SOURCE_RE = re.compile(
    r"^\s*(plugins/(?:preprocess|postprocess)/[A-Za-z][A-Za-z0-9_]*\.hpp)\s*$",
    re.MULTILINE,
)
_POSTPROCESS_IMPLEMENTATIONS = frozenset({"standard", "cpp_postprocess"})
_COMPOSER_EXECUTION_KEYS = frozenset({
    "device_id",
    "save_output",
    "config_overrides",
    "postprocess_implementation",
})


def _safe_lab_id(prefix):
    return f"{prefix}_{int(time.time())}_{secrets.token_urlsafe(8).replace('-', '_')}"


def _evict_expired_manifests():
    with _manifests_lock:
        for manifest_id in list(_manifests):
            if _expired(_manifests[manifest_id]):
                _manifests.pop(manifest_id, None)


def _base_manifest(kind, inputs=None):
    return {
        "id": _safe_lab_id("lab"),
        "kind": kind,
        "status": "ready",
        "inputs": inputs or {},
        "summary": "",
        "operations": [],
        "blockers": [],
        "warnings": [],
        "artifacts": [],
        "confirmations": [],
        "rollback": {"supported": False, "operations": []},
        "created_at": time.time(),
    }


def create_manifest(kind, inputs=None, **updates):
    with _manifests_lock:
        _evict_expired_manifests()
        manifest = _base_manifest(kind, inputs)
        protected = {"id", "created_at"}
        manifest.update({k: v for k, v in updates.items() if k not in protected})
        _manifests[manifest["id"]] = manifest
        while len(_manifests) > MAX_MANIFESTS:
            _manifests.popitem(last=False)
        return manifest


def _expired(manifest):
    return time.time() - float(manifest.get("created_at", 0)) > MANIFEST_TTL_SECONDS


def get_manifest(manifest_id):
    with _manifests_lock:
        manifest = _manifests.get(manifest_id)
        if not manifest or _expired(manifest):
            _manifests.pop(manifest_id, None)
            return {"error": "Manifest expired", "error_code": "manifest_expired"}, 404
        return manifest, 200


def resolve_manifest(manifest_id, token=None):
    """Resolve an active manifest and enforce ownership for Composer workflows."""
    manifest, code = get_manifest(manifest_id)
    if code != 200:
        return manifest
    if manifest.get("kind") == "composer_workflow":
        if not token or manifest.get("creator_token") != token:
            raise PermissionError("Manifest owner session does not match creator")
    return manifest


def _owned_composer_manifest(tok, manifest_id):
    """Return an owned Composer manifest as a route-style (body, status) pair."""
    manifest, code = get_manifest(manifest_id)
    if code != 200:
        return manifest, code
    if manifest.get("kind") != "composer_workflow":
        return {"error": "Invalid manifest kind", "error_code": "invalid_manifest_kind"}, 400
    try:
        resolve_manifest(manifest_id, token=tok)
    except PermissionError:
        return {
            "error": "Manifest belongs to a different Lab session",
            "error_code": "manifest_owner_forbidden",
        }, 403
    return manifest, 200


def _plugin_scaffold_error(message, code):
    return {"error": message, "error_code": code, "status": 400}


def _plugin_template(stage, language):
    suffix = "py" if language == "python" else "hpp"
    template = TEMPLATES_DIR / "lab_plugins" / f"{language}_{stage}.{suffix}"
    try:
        return template.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _cpp_plugin_sources(cmake_path):
    """Return safe plugin entries from a generated CMake source list."""
    if not cmake_path.is_file() or cmake_path.is_symlink():
        return []
    try:
        return list(dict.fromkeys(_CPP_PLUGIN_SOURCE_RE.findall(
            cmake_path.read_text(encoding="utf-8")
        )))
    except (OSError, UnicodeDecodeError):
        return []


def _has_symlink_component(path, root):
    """Return whether ``path`` or an ancestor below ``root`` is a symlink."""
    root = Path(root)
    candidate = Path(path)
    try:
        relative_path = candidate.relative_to(root)
    except ValueError:
        return True
    current = root
    if current.is_symlink():
        return True
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def plan_composer_plugin_scaffold(tok, payload):
    """Return a session-bound plugin file preview without writing any files."""
    err = require_lab(tok)
    if err:
        return err
    payload = payload if isinstance(payload, dict) else {}
    workflow_id = payload.get("workflow_manifest_id", "")
    workflow_manifest, code = _owned_composer_manifest(tok, workflow_id)
    if code != 200:
        result = dict(workflow_manifest)
        result["status"] = code
        return result

    name = payload.get("plugin_name", "")
    stage = payload.get("stage", "")
    language = payload.get("language", "")
    if not isinstance(name, str) or not _PLUGIN_NAME_RE.fullmatch(name):
        return _plugin_scaffold_error("Invalid plugin name", "plugin_name_invalid")
    if stage not in PLUGIN_STAGES:
        return _plugin_scaffold_error("Invalid plugin stage", "plugin_stage_invalid")
    if language not in PLUGIN_LANGUAGES:
        return _plugin_scaffold_error("Invalid plugin language", "plugin_language_invalid")

    content = _plugin_template(stage, language)
    if content is None:
        return _plugin_scaffold_error("Plugin scaffold template is unavailable", "plugin_template_unavailable")

    workspace = Path("lab_composer") / workflow_manifest["id"]
    extension = ".py" if language == "python" else ".hpp"
    plugin_path = workspace / "plugins" / stage / f"{name}{extension}"
    paths_and_content = [(plugin_path, content)]
    if language == "cpp":
        cmake_path = workspace / "CMakeLists.txt"
        try:
            cmake_target = resolve_under(str(OUTPUTS_DIR / cmake_path), (OUTPUTS_DIR,))
        except ValueError as exc:
            return _plugin_scaffold_error(str(exc), "plugin_path_unsafe")
        if _has_symlink_component(cmake_target, OUTPUTS_DIR):
            return _plugin_scaffold_error("Plugin target must not be a symlink", "plugin_path_unsafe")
        plugin_source = (Path("plugins") / stage / f"{name}{extension}").as_posix()
        sources = _cpp_plugin_sources(cmake_target)
        if plugin_source not in sources:
            sources.append(plugin_source)
        cmake_content = (
            "# Generated DX App Lab plugin source list\n"
            "set(DX_APP_LAB_PLUGIN_SOURCES\n"
            + "".join(f"    {source}\n" for source in sources)
            + ")\n"
        )
        paths_and_content.append((cmake_path, cmake_content))

    operations = []
    confirmations = []
    existing_paths = []
    for relative_path, preview in paths_and_content:
        try:
            target = resolve_under(str(OUTPUTS_DIR / relative_path), (OUTPUTS_DIR,))
        except ValueError as exc:
            return _plugin_scaffold_error(str(exc), "plugin_path_unsafe")
        if _has_symlink_component(target, OUTPUTS_DIR):
            return _plugin_scaffold_error("Plugin target must not be a symlink", "plugin_path_unsafe")
        exists = target.exists()
        operations.append(_operation(
            "modify" if exists else "create",
            "OUTPUTS_DIR",
            relative_path.as_posix(),
            exists=exists,
            preview=preview,
        ))
        if exists:
            existing_paths.append(relative_path.as_posix())
    if existing_paths:
        confirmations.append({
            "key": "overwrite",
            "expected": f"overwrite:{name}",
            "label": "Overwrite existing plugin scaffold files",
        })

    return create_manifest(
        "composer_plugin_scaffold",
        inputs={
            "workflow_manifest_id": workflow_manifest["id"],
            "plugin_name": name,
            "stage": stage,
            "language": language,
            "plugin_root": workspace.as_posix(),
        },
        creator_token=tok,
        operations=operations,
        confirmations=confirmations,
        status="ready",
        summary=f"Create {language} {stage} plugin {name}",
    )


def plan_composer_plugin_scaffold_response(tok, payload):
    """Wrap plugin scaffold planning for HTTP routes without leaking status fields."""
    return _result_with_http_status(plan_composer_plugin_scaffold(tok, payload))


def _is_finite_numeric_scalar(value):
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _postprocess_tunable_defaults(model):
    """Return only numeric Factory config fields explicitly supported by the Run UI."""
    if not isinstance(model, dict):
        return {}
    category = model.get("category")
    name = model.get("name")
    if not isinstance(category, str) or not category or not isinstance(name, str) or not name:
        return {}
    config_values = load_model_config(category, name)
    if not isinstance(config_values, dict):
        return {}
    return {
        key: config_values[key]
        for key in sorted(RUN_TUNABLE_KEYS)
        if key in config_values and _is_finite_numeric_scalar(config_values[key])
    }


def _postprocess_implementation_options(model):
    options = ["standard"]
    if isinstance(model, dict) and model.get("py_sync_cpp_postprocess") is True:
        options.append("cpp_postprocess")
    return options


def _processor_capabilities(model):
    """Describe only server-resolved built-in processor controls for the Inspector."""
    defaults = _postprocess_tunable_defaults(model)
    return {
        "preprocess": {"factory_owned": True},
        "postprocess": {
            "implementation_options": _postprocess_implementation_options(model),
            "tunable_defaults": defaults,
            "tunable_keys": sorted(defaults),
        },
    }


def _workflow_registry_model(workflow):
    if not isinstance(workflow, dict):
        return None
    return resolve_runnable_model(workflow.get("model", {}), get_models())


def _normalize_processor_execution(execution, model, *, strict):
    """Validate or safely reset processor settings against the current model registry entry."""
    if not isinstance(execution, dict):
        return None, "Workflow execution is invalid"
    normalized = copy.deepcopy(execution)
    defaults = _postprocess_tunable_defaults(model)
    allowed_keys = set(defaults)

    if "config_overrides" in normalized:
        overrides = normalized["config_overrides"]
        if not isinstance(overrides, dict):
            return None, "Postprocess overrides must be an object"
        clean_overrides = {}
        for key, value in overrides.items():
            if key not in allowed_keys:
                if strict:
                    return None, "Postprocess override is not supported by the selected model"
                continue
            if not _is_finite_numeric_scalar(value):
                if strict:
                    return None, "Postprocess overrides must be finite numeric values"
                continue
            clean_overrides[key] = value
        normalized["config_overrides"] = clean_overrides

    implementation = normalized.get("postprocess_implementation", "standard")
    if not isinstance(implementation, str) or implementation not in _POSTPROCESS_IMPLEMENTATIONS:
        if strict:
            return None, "Postprocess implementation is invalid"
        implementation = "standard"
    if implementation not in _postprocess_implementation_options(model):
        if strict:
            return None, "Postprocess implementation is not supported by the selected model"
        implementation = "standard"
    if "postprocess_implementation" in normalized or implementation != "standard":
        normalized["postprocess_implementation"] = implementation
    return normalized, None


def _effective_composer_runner(model, execution):
    """Map normalized settings to a registry-authorized runner, never client metadata."""
    if (
        isinstance(execution, dict)
        and execution.get("postprocess_implementation") == "cpp_postprocess"
        and isinstance(model, dict)
        and model.get("py_sync_cpp_postprocess") is True
    ):
        return "python", "sync_cpp_postprocess"
    if isinstance(model, dict) and model.get("cpp_sync"):
        return "cpp", "sync"
    return "python", "sync"


def _composer_manifest_response(manifest):
    workflow = manifest.get("workflow", {})
    validation = workflow.get("validation", {}) if isinstance(workflow, dict) else {}
    return {
        "manifest_id": manifest["id"],
        "workflow": workflow,
        "status": manifest.get("status", validation.get("status", "blocked")),
        "validation": validation,
        "processor_capabilities": _processor_capabilities(_workflow_registry_model(workflow)),
    }, 200


def _demo_default_asset(model_name, category, input_kind):
    """The demo's own default_image/default_video (build_demos_payload, sourced from
    run_demo.sh) — more precise than the category-wide CAT_IMAGE/CAT_VIDEO default.
    None if no demo matches this (model_name, category)."""
    if not model_name or not category:
        return None
    try:
        demos = build_demos_payload().get("demos", [])
    except Exception:
        return None
    key = "default_video" if input_kind == "video" else "default_image"
    for d in demos:
        run_ref = d.get("run_ref") or {}
        if run_ref.get("category") == category and run_ref.get("model_name") == model_name:
            value = d.get(key)
            if value:
                return value
    return None


def _category_default_asset(category, input_kind):
    """The category's canonical CAT_IMAGE/CAT_VIDEO asset (dx_app.core.config)."""
    if not category:
        return None
    try:
        from dx_app.core.config import CAT_IMAGE, CAT_VIDEO
    except Exception:
        return None
    return (CAT_VIDEO if input_kind == "video" else CAT_IMAGE).get(category) or None


def _preferred_default_asset(model_name, category, input_kind):
    """Resolution order: (a) the model's own demo default, (b) the category default."""
    return _demo_default_asset(model_name, category, input_kind) or _category_default_asset(category, input_kind)


def _workflow_assets(category, input_kind):
    """Return only the current Lab asset list compatible with an input kind."""
    if input_kind == "video":
        return get_videos(category)
    return get_images(category)


_COMPOSER_RESOLUTION_BLOCKER_CODES = frozenset({
    "runnable_model_not_found",
    "compatible_input_not_found",
    "template_not_found",
})


def _refresh_composer_validation(workflow, plugin_root=None):
    """Retain immutable resolution blockers while recomputing mutable validation."""
    if isinstance(workflow, dict):
        workflow["graph_layout"] = normalize_graph_layout(workflow.get("graph_layout"))
    initial = workflow.get("validation", {}) if isinstance(workflow, dict) else {}
    validation = validate_workflow(workflow, plugin_root=plugin_root)

    blockers = []
    resolution_blockers = [
        blocker for blocker in initial.get("blockers", [])
        if isinstance(blocker, dict)
        and blocker.get("code") in _COMPOSER_RESOLUTION_BLOCKER_CODES
    ]
    for blocker in resolution_blockers + validation.get("blockers", []):
        if blocker not in blockers:
            blockers.append(blocker)
    workflow["validation"] = {
        "status": "blocked" if blockers else "ready",
        "blockers": blockers,
        "warnings": validation.get("warnings", []),
    }
    return workflow["validation"]


def _composer_patch_error(code, message="Workflow customization is not allowed"):
    return {"error": message, "error_code": code}, 400


def _set_composer_resolution_blocker(workflow, node_id, code, present):
    """Update only one server-resolution blocker before canonical revalidation."""
    validation = workflow.get("validation") if isinstance(workflow, dict) else None
    validation = validation if isinstance(validation, dict) else {}
    blockers = validation.get("blockers") if isinstance(validation.get("blockers"), list) else []
    retained = [
        blocker for blocker in blockers
        if (
            not isinstance(blocker, dict)
            or blocker.get("node_id") != node_id
            or blocker.get("code") != code
        )
    ]
    if present:
        retained.append({"node_id": node_id, "code": code})
    workflow["validation"] = {
        "status": "blocked" if retained else "ready",
        "blockers": retained,
        "warnings": validation.get("warnings") if isinstance(validation.get("warnings"), list) else [],
    }


def _workflow_model_from_registry(model):
    """Project a verified runnable registry record into canonical workflow identity."""
    if not isinstance(model, dict):
        return None
    name = model.get("name")
    category = model.get("category")
    model_file = model.get("model_file")
    if not all(isinstance(value, str) and value for value in (name, category, model_file)):
        return None
    if model.get("cpp_sync"):
        language = "cpp"
    elif model.get("py_sync"):
        language = "python"
    else:
        return None
    return {
        "name": name,
        "category": category,
        "model_file": model_file,
        "language": language,
        "variant": "sync",
    }


def _compatible_composer_assets(category, input_kind, model_name=None):
    """Return trusted, selectable current assets for a workflow input type, ordered by
    _workflow_assets (model demo default, then category default, then generic gallery).

    Returns (assets, preferred) — the resolved default preference is handed back so
    callers can derive a `generic` marker without a second _preferred_default_asset (and
    thus build_demos_payload) call."""
    if input_kind not in ("image", "video"):
        return [], None
    assets = [
        asset for asset in _workflow_assets(category, input_kind)
        if isinstance(asset, str) and asset
    ]
    preferred = _preferred_default_asset(model_name, category, input_kind)
    if preferred and preferred in assets and assets[0] != preferred:
        assets = [preferred] + [a for a in assets if a != preferred]
    return assets, preferred


def _apply_composer_updates(workflow, updates):
    """Apply only the fixed, non-executable Composer customization schema."""
    if not isinstance(updates, dict) or not updates:
        return None, _composer_patch_error("workflow_patch_invalid", "Workflow updates are required")
    if set(updates) - {"execution", "plugins", "model_selection", "input_selection", "graph_layout"}:
        return None, _composer_patch_error("workflow_patch_forbidden")

    candidate = copy.deepcopy(workflow)
    if not isinstance(candidate, dict):
        return None, _composer_patch_error("workflow_patch_invalid", "Workflow is invalid")

    if "graph_layout" in updates:
        graph_layout = updates["graph_layout"]
        if not isinstance(graph_layout, dict):
            return None, _composer_patch_error("workflow_patch_invalid", "Graph layout is invalid")
        if validate_graph_layout(graph_layout):
            return None, _composer_patch_error("workflow_patch_invalid", "Graph layout is invalid")
        candidate["graph_layout"] = copy.deepcopy(graph_layout)

    processor_settings_updated = False
    if "execution" in updates:
        execution = updates["execution"]
        if not isinstance(execution, dict) or set(execution) - _COMPOSER_EXECUTION_KEYS:
            return None, _composer_patch_error("workflow_patch_forbidden")
        current_execution = candidate.get("execution")
        if not isinstance(current_execution, dict):
            return None, _composer_patch_error("workflow_patch_invalid", "Workflow execution is invalid")
        if "device_id" in execution:
            device_id = execution["device_id"]
            if isinstance(device_id, bool) or (device_id is not None and (not isinstance(device_id, int) or device_id < 0)):
                return None, _composer_patch_error("workflow_patch_invalid", "Device ID must be a non-negative integer or null")
            current_execution["device_id"] = device_id
        if "save_output" in execution:
            if not isinstance(execution["save_output"], bool):
                return None, _composer_patch_error("workflow_patch_invalid", "Save output must be a boolean")
            current_execution["save_output"] = execution["save_output"]
        if "config_overrides" in execution:
            current_execution["config_overrides"] = copy.deepcopy(execution["config_overrides"])
            processor_settings_updated = True
        if "postprocess_implementation" in execution:
            current_execution["postprocess_implementation"] = execution["postprocess_implementation"]
            processor_settings_updated = True

    if "model_selection" in updates:
        selection = updates["model_selection"]
        if (
            not isinstance(selection, dict)
            or set(selection) != {"model_file"}
            or not isinstance(selection.get("model_file"), str)
            or not selection["model_file"]
        ):
            return None, _composer_patch_error("workflow_patch_forbidden")
        selected_model = resolve_runnable_model(selection, get_models())
        canonical_model = _workflow_model_from_registry(selected_model)
        if canonical_model is None:
            return None, _composer_patch_error(
                "workflow_patch_invalid",
                "Selected model is not runnable in the current registry",
            )
        candidate["model"] = canonical_model
        _set_composer_resolution_blocker(candidate, "model", "runnable_model_not_found", False)
        input_data = candidate.get("input")
        if not isinstance(input_data, dict):
            return None, _composer_patch_error("workflow_patch_invalid", "Workflow input is invalid")
        input_kind = input_data.get("kind")
        compatible_assets, preferred = _compatible_composer_assets(
            canonical_model["category"], input_kind, canonical_model["name"]
        )
        if input_kind in ("image", "video"):
            if compatible_assets:
                if input_data.get("path") not in compatible_assets:
                    input_data["path"] = compatible_assets[0]
                # input_generic=True: no model demo default or category default was
                # available/installed, so the resolver fell back to the generic gallery.
                # Added as a sibling top-level key (not under "input") so it does not
                # disturb the existing input={"kind","path"} shape the frontend reads.
                candidate["input_generic"] = not (preferred and preferred in compatible_assets)
                _set_composer_resolution_blocker(candidate, "input", "compatible_input_not_found", False)
            else:
                input_data["path"] = ""
                candidate["input_generic"] = True
                _set_composer_resolution_blocker(candidate, "input", "compatible_input_not_found", True)

    if processor_settings_updated or "model_selection" in updates:
        model = _workflow_registry_model(candidate)
        if model is None:
            return None, _composer_patch_error(
                "workflow_patch_invalid", "Selected model is not runnable in the current registry"
            )
        normalized_execution, processor_error = _normalize_processor_execution(
            candidate.get("execution"),
            model,
            strict=processor_settings_updated,
        )
        if processor_error:
            return None, _composer_patch_error("workflow_patch_invalid", processor_error)
        candidate["execution"] = normalized_execution

    if "input_selection" in updates:
        selection = updates["input_selection"]
        if (
            not isinstance(selection, dict)
            or set(selection) != {"path"}
            or not isinstance(selection.get("path"), str)
            or not selection["path"]
        ):
            return None, _composer_patch_error("workflow_patch_forbidden")
        input_data = candidate.get("input")
        model = candidate.get("model")
        if not isinstance(input_data, dict) or not isinstance(model, dict):
            return None, _composer_patch_error("workflow_patch_invalid", "Workflow input is invalid")
        compatible_assets, _preferred = _compatible_composer_assets(
            model.get("category"), input_data.get("kind"), model.get("name")
        )
        if selection["path"] not in compatible_assets:
            return None, _composer_patch_error(
                "workflow_patch_invalid",
                "Selected input is not compatible with the current workflow",
            )
        input_data["path"] = selection["path"]
        _set_composer_resolution_blocker(candidate, "input", "compatible_input_not_found", False)

    if "plugins" in updates:
        plugin_updates = updates["plugins"]
        plugins = candidate.get("plugins")
        if not isinstance(plugin_updates, list) or not isinstance(plugins, list):
            return None, _composer_patch_error("workflow_patch_invalid", "Plugin updates are invalid")
        indexed_plugins = {
            plugin.get("id"): plugin
            for plugin in plugins
            if isinstance(plugin, dict) and isinstance(plugin.get("id"), str)
        }
        seen_plugin_ids = set()
        for plugin_update in plugin_updates:
            if (
                not isinstance(plugin_update, dict)
                or set(plugin_update) != {"id", "enabled"}
                or not isinstance(plugin_update.get("id"), str)
                or not isinstance(plugin_update.get("enabled"), bool)
                or plugin_update["id"] in seen_plugin_ids
                or plugin_update["id"] not in indexed_plugins
            ):
                return None, _composer_patch_error("workflow_patch_forbidden")
            seen_plugin_ids.add(plugin_update["id"])
            indexed_plugins[plugin_update["id"]]["enabled"] = plugin_update["enabled"]

    return candidate, None


def customize_composer_workflow(tok, payload):
    """Apply a safe patch to an owned workflow, then immediately revalidate it."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)
    payload = payload if isinstance(payload, dict) else {}
    manifest, code = _owned_composer_manifest(tok, payload.get("manifest_id", ""))
    if code != 200:
        return manifest, code
    ok, lock_err = acquire_apply_lock(manifest["id"])
    if not ok:
        return lock_err, 409
    try:
        workflow, patch_error = _apply_composer_updates(manifest.get("workflow"), payload.get("updates"))
        if patch_error:
            return patch_error
        try:
            plugin_root = _composer_plugin_root(manifest)
        except ValueError:
            return _composer_patch_error("plugin_workspace_unsafe", "Composer plugin workspace is unsafe")
        validation = _refresh_composer_validation(workflow, plugin_root=plugin_root)
        manifest["workflow"] = workflow
        manifest["status"] = validation["status"]
        response, response_code = _composer_manifest_response(manifest)
        response["applied_updates"] = copy.deepcopy(payload["updates"])
        return response, response_code
    finally:
        release_apply_lock(manifest["id"])


def apply_composer_plugin_scaffold(tok, payload):
    """Write only a confirmed server-generated scaffold and attach its plugin reference."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)
    payload = payload if isinstance(payload, dict) else {}
    scaffold, code = get_manifest(payload.get("plugin_manifest_id", ""))
    if code != 200:
        return scaffold, code
    if scaffold.get("kind") != "composer_plugin_scaffold":
        return {"error": "Invalid manifest kind", "error_code": "invalid_manifest_kind"}, 400
    if scaffold.get("creator_token") != tok:
        return {
            "error": "Manifest belongs to a different Lab session",
            "error_code": "manifest_owner_forbidden",
        }, 403
    if scaffold.get("status") != "ready":
        return {"error": "Plugin scaffold is not ready", "error_code": "manifest_not_ready"}, 400
    confirmed, missing = _confirmations_match(scaffold, payload)
    if not confirmed:
        return {"error": "Confirmation required", "error_code": "confirmation_required", "missing": missing}, 400

    inputs = scaffold.get("inputs", {})
    workflow_manifest, code = _owned_composer_manifest(tok, inputs.get("workflow_manifest_id", ""))
    if code != 200:
        return workflow_manifest, code
    stage = inputs.get("stage")
    language = inputs.get("language")
    name = inputs.get("plugin_name")
    if (
        stage not in PLUGIN_STAGES
        or language not in PLUGIN_LANGUAGES
        or not isinstance(name, str)
        or not _PLUGIN_NAME_RE.fullmatch(name)
    ):
        return _composer_patch_error("plugin_scaffold_invalid", "Plugin scaffold is invalid")

    expected_root = Path("lab_composer") / workflow_manifest["id"]
    expected_path = expected_root / "plugins" / stage / f"{name}{'.py' if language == 'python' else '.hpp'}"
    operations = scaffold.get("operations", [])
    if not isinstance(operations, list) or not operations:
        return _composer_patch_error("plugin_scaffold_invalid", "Plugin scaffold operations are invalid")

    ok, lock_err = acquire_apply_lock(workflow_manifest["id"])
    if not ok:
        return lock_err, 409
    try:
        written_paths = []
        for operation in operations:
            if not isinstance(operation, dict) or operation.get("root") != "OUTPUTS_DIR":
                return _composer_patch_error("plugin_scaffold_invalid", "Plugin scaffold operation is invalid")
            relative = Path(str(operation.get("path", "")))
            preview = operation.get("preview")
            if not isinstance(preview, str):
                return _composer_patch_error("plugin_scaffold_invalid", "Plugin scaffold preview is invalid")
            try:
                if relative != expected_path and relative != expected_root / "CMakeLists.txt":
                    raise ValueError("Unexpected plugin scaffold path")
                target = resolve_under(str(OUTPUTS_DIR / relative), (OUTPUTS_DIR,))
            except ValueError:
                return _composer_patch_error("plugin_path_unsafe", "Plugin scaffold path is unsafe")
            if _has_symlink_component(target, OUTPUTS_DIR):
                return _composer_patch_error("plugin_path_unsafe", "Plugin scaffold path is unsafe")
            target.parent.mkdir(parents=True, exist_ok=True)
            if _has_symlink_component(target.parent, OUTPUTS_DIR):
                return _composer_patch_error("plugin_path_unsafe", "Plugin scaffold path is unsafe")
            target.write_text(preview, encoding="utf-8")
            written_paths.append(relative)

        if expected_path not in written_paths:
            return _composer_patch_error("plugin_scaffold_invalid", "Plugin source was not generated")
        workflow = copy.deepcopy(workflow_manifest.get("workflow"))
        if not isinstance(workflow, dict):
            return _composer_patch_error("workflow_patch_invalid", "Workflow is invalid")
        plugin = {
            "id": name,
            "stage": stage,
            "language": language,
            "entrypoint": (Path("plugins") / stage / expected_path.name).as_posix(),
            "interface_version": PLUGIN_INTERFACE_VERSION,
            "enabled": True,
        }
        existing_plugins = workflow.get("plugins", [])
        if not isinstance(existing_plugins, list):
            return _composer_patch_error("workflow_patch_invalid", "Workflow plugins are invalid")
        workflow["plugins"] = [
            existing for existing in existing_plugins
            if not isinstance(existing, dict) or existing.get("stage") != stage
        ] + [plugin]
        plugin_root = _composer_plugin_root(workflow_manifest)
        validation = _refresh_composer_validation(workflow, plugin_root=plugin_root)
        workflow_manifest["workflow"] = workflow
        workflow_manifest["status"] = validation["status"]
        scaffold["status"] = "applied"
        response, response_code = _composer_manifest_response(workflow_manifest)
        response["applied_plugin"] = plugin
        return response, response_code
    finally:
        release_apply_lock(workflow_manifest["id"])


def plan_composer_quick_start(tok, payload):
    """Build a token-bound Composer Quick Start workflow from current server data."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)
    payload = payload if isinstance(payload, dict) else {}
    selection = payload.get("selection")
    if not isinstance(selection, dict):
        selection = payload.get("model") if isinstance(payload.get("model"), dict) else {}
    models = get_models()
    model = resolve_runnable_model(selection, models)
    category = (model or selection).get("category", "")
    model_name = (model or selection).get("name")
    input_kind = "video" if "video" in str(category).lower() else "image"
    assets, preferred = _compatible_composer_assets(category, input_kind, model_name)
    workflow = build_quick_start_workflow(selection, models, assets)
    input_data = workflow.get("input")
    if isinstance(input_data, dict) and input_data.get("kind") in ("image", "video"):
        # Sibling top-level key (see _apply_composer_updates) — leaves the input={"kind","path"}
        # shape untouched.
        # "generic" = no category-specific default is available among the compatible
        # assets — same semantics as the customize path (_apply_composer_updates). Do NOT
        # compare to the chosen input path: build_quick_start_workflow may pick a different
        # (still valid) asset via its own stem-matching, which would falsely flag generic.
        workflow["input_generic"] = not (preferred and preferred in assets)
    _refresh_composer_validation(workflow)
    manifest = create_manifest(
        "composer_workflow",
        workflow=workflow,
        creator_token=tok,
        status=workflow["validation"]["status"],
        summary="Composer Quick Start workflow",
    )
    return _composer_manifest_response(manifest)


def plan_composer_template(tok, payload):
    """Build a token-bound Composer template workflow from current server data."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)
    payload = payload if isinstance(payload, dict) else {}
    template_id = payload.get("template_id", "")
    template = WORKFLOW_TEMPLATES.get(template_id, {})
    category = template.get("category")
    models = get_models()
    requested = payload.get("selection")
    if not isinstance(requested, dict) and payload.get("model_name"):
        requested = {"name": payload["model_name"]}
    if isinstance(requested, dict):
        selected_model = resolve_runnable_model(requested, models)
        if selected_model and category and selected_model.get("category") != category:
            # Explicit model request whose category conflicts with the template: surface
            # this to the caller rather than silently falling back to a different model.
            return {
                "error": (
                    f"Model '{selected_model.get('name', '')}' is category "
                    f"'{selected_model.get('category', '')}', which does not match "
                    f"template '{template_id}' (requires category '{category}')"
                ),
                "error_code": "template_model_mismatch",
            }, 400
        candidate_models = [selected_model] if selected_model else []
    else:
        candidate_models = models
    workflow = build_template_workflow(
        template_id,
        candidate_models,
        get_images(category),
        get_videos(),
    )
    _refresh_composer_validation(workflow)
    manifest = create_manifest(
        "composer_workflow",
        workflow=workflow,
        creator_token=tok,
        status=workflow["validation"]["status"],
        summary="Composer template workflow",
    )
    return _composer_manifest_response(manifest)


def run_composer_workflow(tok, payload, job_id=None):
    """Run an owned, ready workflow using current runnable registry values only.

    job_id (optional): when set, forwarded to run_inference so run_progress can report live
    frame progress for the async composer run path."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)
    payload = payload if isinstance(payload, dict) else {}
    manifest, code = _owned_composer_manifest(tok, payload.get("manifest_id", ""))
    if code != 200:
        return manifest, code

    workflow = manifest.get("workflow")
    if isinstance(workflow, dict):
        workflow["graph_layout"] = normalize_graph_layout(workflow.get("graph_layout"))
    try:
        plugin_root = _composer_plugin_root(manifest)
    except ValueError as exc:
        return {
            "error": "Composer plugin workspace is unsafe",
            "error_code": "plugin_workspace_unsafe",
            "detail": str(exc),
        }, 400
    validation = validate_workflow(workflow, plugin_root=plugin_root)
    if validation["status"] != "ready":
        manifest["status"] = "blocked"
        if isinstance(workflow, dict):
            workflow["validation"] = validation
        return {
            "error": "Workflow is blocked",
            "error_code": "workflow_blocked",
            "validation": validation,
        }, 400

    model = resolve_runnable_model(workflow.get("model", {}), get_models())
    if not model:
        return {
            "error": "Runnable model not found in the current registry",
            "error_code": "runnable_model_not_found",
        }, 400
    execution, processor_error = _normalize_processor_execution(
        workflow.get("execution"), model, strict=True
    )
    if processor_error:
        return {
            "error": processor_error,
            "error_code": "workflow_processor_settings_invalid",
        }, 400
    input_data = workflow.get("input", {})
    input_kind = input_data.get("kind")
    if input_kind not in ("image", "video"):
        return {
            "error": "Workflow input is not runnable",
            "error_code": "workflow_blocked",
            "validation": validation,
        }, 400

    language, variant = _effective_composer_runner(model, execution)
    inference_request = {
        "model_name": model.get("name", ""),
        "category": model.get("category", ""),
        "model_file": model.get("model_file", ""),
        "lang": language,
        "variant": variant,
        "input_type": input_kind,
        "image_path": input_data.get("path") if input_kind == "image" else None,
        "video_path": input_data.get("path") if input_kind == "video" else None,
        "device_id": execution.get("device_id"),
        "save_output": execution.get("save_output", True),
    }
    if execution.get("config_overrides"):
        inference_request["config_overrides"] = execution["config_overrides"]
    if job_id is not None:
        inference_request["job_id"] = job_id
    result = run_inference(**inference_request)
    if isinstance(result, dict) and result.get("error"):
        return _result_with_http_status(result, 400)
    return _result_with_http_status(result)


def _composer_plugin_root(manifest):
    """Return the controlled Composer plugin workspace only when it is safe."""
    workspace = OUTPUTS_DIR / "lab_composer" / manifest["id"]
    try:
        workspace = resolve_under(str(workspace), (OUTPUTS_DIR,))
    except ValueError as exc:
        raise ValueError("Composer plugin workspace path is unsafe") from exc
    if not workspace.exists():
        return None
    if _has_symlink_component(workspace, OUTPUTS_DIR) or not workspace.is_dir():
        raise ValueError("Composer plugin workspace is unsafe")
    return workspace


def _package_download_metadata(package_result):
    """Publish only a regular archive in the Lab package output namespace."""
    archive_value = package_result.get("archive_path") if isinstance(package_result, dict) else None
    try:
        archive = resolve_existing_file(str(archive_value), (OUTPUTS_DIR,), (".zip",))
        relative = archive.relative_to(OUTPUTS_DIR)
    except (TypeError, ValueError) as exc:
        raise ValueError("Package exporter did not create a safe download archive") from exc
    if (
        _has_symlink_component(archive, OUTPUTS_DIR)
        or len(relative.parts) != 2
        or relative.parts[0] != "lab_packages"
    ):
        raise ValueError("Package exporter did not create a safe download archive")
    return {
        "name": archive.name,
        "url": "/outputs/" + relative.as_posix(),
    }


def export_composer_package(tok, payload):
    """Export an owned ready Composer workflow as a portable package archive."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)
    payload = payload if isinstance(payload, dict) else {}
    package_type = payload.get("package_type")
    if package_type not in PACKAGE_TYPES:
        return {
            "error": "Unsupported package type",
            "error_code": "package_type_invalid",
            "allowed_package_types": list(PACKAGE_TYPES),
        }, 400

    manifest, code = _owned_composer_manifest(tok, payload.get("manifest_id", ""))
    if code != 200:
        return manifest, code
    workflow = manifest.get("workflow")
    if isinstance(workflow, dict):
        workflow["graph_layout"] = normalize_graph_layout(workflow.get("graph_layout"))
    try:
        plugin_root = _composer_plugin_root(manifest)
    except ValueError as exc:
        return {
            "error": "Composer plugin workspace is unsafe",
            "error_code": "plugin_workspace_unsafe",
            "detail": str(exc),
        }, 400

    validation = validate_workflow(workflow, plugin_root=plugin_root)
    if validation["status"] != "ready":
        manifest["status"] = "blocked"
        if isinstance(workflow, dict):
            workflow["validation"] = validation
        return {
            "error": "Workflow is blocked",
            "error_code": "workflow_blocked",
            "validation": validation,
        }, 400

    model = resolve_runnable_model(workflow.get("model", {}), get_models())
    if not model:
        return {
            "error": "Runnable model not found in the current registry",
            "error_code": "runnable_model_not_found",
        }, 400
    execution, processor_error = _normalize_processor_execution(
        workflow.get("execution"), model, strict=True
    )
    if processor_error:
        return {
            "error": processor_error,
            "error_code": "workflow_processor_settings_invalid",
        }, 400
    language, variant = _effective_composer_runner(model, execution)

    package_workflow = copy.deepcopy(workflow)
    package_workflow["model"] = {
        "name": model.get("name", ""),
        "category": model.get("category", ""),
        "model_file": model.get("model_file", ""),
        "language": language,
        "variant": variant,
    }
    package_workflow["execution"] = execution
    package_validation = validate_workflow(package_workflow, plugin_root=plugin_root)
    if package_validation["status"] != "ready":
        return {
            "error": "Workflow is blocked",
            "error_code": "workflow_blocked",
            "validation": package_validation,
        }, 400
    if package_workflow.get("plugins") and plugin_root is None:
        return {
            "error": "Declared plugins have no controlled Composer workspace",
            "error_code": "plugin_workspace_unavailable",
        }, 400

    try:
        package_result = build_workflow_package(
            workflow=package_workflow,
            package_type=package_type,
            source_root=DX_APP_ROOT,
            output_root=OUTPUTS_DIR,
            plugin_root=plugin_root,
        )
        download = _package_download_metadata(package_result)
    except (OSError, RuntimeError, ValueError) as exc:
        return {
            "error": "Portable package export failed",
            "error_code": "package_export_failed",
            "detail": str(exc),
        }, 400
    return {
        "package_type": package_type,
        "download": download,
        "copy_out_verified": bool(package_result.get("copy_out_verified")),
    }, 200


def _recipe_plugin_path_safe(plugin):
    entrypoint = Path(str(plugin.get("entrypoint", "")))
    return (
        bool(plugin.get("entrypoint"))
        and not entrypoint.is_absolute()
        and ".." not in entrypoint.parts
        and len(entrypoint.parts) >= 3
        and entrypoint.parts[0] == "plugins"
        and entrypoint.parts[1] == plugin.get("stage")
    )


def export_composer_recipe(tok, payload):
    """Export an owned validated workflow without binary or asset-path references."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)
    payload = payload if isinstance(payload, dict) else {}
    manifest, code = _owned_composer_manifest(tok, payload.get("manifest_id", ""))
    if code != 200:
        return manifest, code
    workflow = manifest.get("workflow")
    if isinstance(workflow, dict):
        workflow["graph_layout"] = normalize_graph_layout(workflow.get("graph_layout"))
    try:
        plugin_root = _composer_plugin_root(manifest)
    except ValueError as exc:
        return {
            "error": "Composer plugin workspace is unsafe",
            "error_code": "plugin_workspace_unsafe",
            "detail": str(exc),
        }, 400
    validation = validate_workflow(workflow, plugin_root=plugin_root)
    if validation["status"] != "ready":
        return {
            "error": "Workflow is blocked",
            "error_code": "workflow_blocked",
            "validation": validation,
        }, 400
    model = workflow["model"]
    recipe = {
        "schema_version": WORKFLOW_SCHEMA_VERSION,
        "model": {key: model.get(key) for key in ("name", "category", "language", "variant")},
        "input": {"kind": workflow["input"].get("kind")},
        "nodes": workflow.get("nodes", []),
        "plugins": workflow.get("plugins", []),
        "execution": dict(workflow.get("execution", {})),
        "graph_layout": copy.deepcopy(workflow["graph_layout"]),
    }
    return {"recipe": recipe}, 200


def import_recipe(recipe, models=None, images=None, videos=None):
    """Return a canonical workflow or a structured recipe-import error dictionary."""
    if not isinstance(recipe, dict) or recipe.get("schema_version") != WORKFLOW_SCHEMA_VERSION:
        return {"error": "Unsupported recipe schema", "error_code": "recipe_schema_unsupported"}
    graph_layout = recipe.get("graph_layout")
    if graph_layout is not None and validate_graph_layout(graph_layout):
        return {"error": "Recipe graph layout is invalid", "error_code": "graph_layout_invalid"}
    plugins = recipe.get("plugins", [])
    if not isinstance(plugins, list) or any(
        not isinstance(plugin, dict) or not _recipe_plugin_path_safe(plugin)
        for plugin in plugins
    ):
        return {"error": "Plugin entrypoint is unsafe", "error_code": "plugin_path_unsafe"}

    registry = get_models() if models is None else models
    selection = recipe.get("model", {})
    model = resolve_runnable_model(selection, registry)
    if not model:
        return {"error": "Runnable model not found", "error_code": "runnable_model_not_found"}
    requested_input = recipe.get("input", {})
    input_kind = requested_input.get("kind", "image") if isinstance(requested_input, dict) else "image"
    if input_kind not in ("image", "video", "camera"):
        return {"error": "Recipe input is invalid", "error_code": "recipe_input_invalid"}
    if images is None:
        images = get_images(model.get("category"))
    if videos is None:
        videos = get_videos()
    assets = videos if input_kind == "video" else images
    template_id = {"video": "video", "camera": "camera"}.get(input_kind)
    workflow = build_quick_start_workflow(
        {"name": model.get("name", "")},
        registry,
        assets,
        template_id=template_id,
    )
    workflow["source"] = "recipe"
    workflow["graph_layout"] = copy.deepcopy(normalize_graph_layout(graph_layout))
    workflow["plugins"] = [dict(plugin) for plugin in plugins]
    execution = recipe.get("execution", {})
    if not isinstance(execution, dict) or set(execution) - _COMPOSER_EXECUTION_KEYS:
        return {"error": "Recipe execution is invalid", "error_code": "recipe_execution_invalid"}
    imported_execution = dict(workflow.get("execution", {}))
    if "device_id" in execution:
        device_id = execution["device_id"]
        if isinstance(device_id, bool) or (device_id is not None and (not isinstance(device_id, int) or device_id < 0)):
            return {"error": "Recipe device ID is invalid", "error_code": "recipe_execution_invalid"}
        imported_execution["device_id"] = device_id
    if "save_output" in execution:
        if not isinstance(execution["save_output"], bool):
            return {"error": "Recipe save output is invalid", "error_code": "recipe_execution_invalid"}
        imported_execution["save_output"] = execution["save_output"]
    for key in ("config_overrides", "postprocess_implementation"):
        if key in execution:
            imported_execution[key] = copy.deepcopy(execution[key])
    normalized_execution, processor_error = _normalize_processor_execution(
        imported_execution, model, strict=True
    )
    if processor_error:
        return {"error": processor_error, "error_code": "recipe_execution_invalid"}
    workflow["execution"] = normalized_execution
    _refresh_composer_validation(workflow)
    return workflow


def import_composer_recipe(tok, payload):
    """Import a recipe into a new token-bound Composer manifest."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)
    payload = payload if isinstance(payload, dict) else {}
    recipe = payload.get("recipe")
    selection = recipe.get("model", {}) if isinstance(recipe, dict) else {}
    category = selection.get("category") if isinstance(selection, dict) else None
    workflow = import_recipe(
        recipe,
        models=get_models(),
        images=get_images(category),
        videos=get_videos(),
    )
    if workflow.get("error"):
        return _error_response(workflow, 400)
    manifest = create_manifest(
        "composer_workflow",
        workflow=workflow,
        creator_token=tok,
        status=workflow["validation"]["status"],
        summary="Imported Composer recipe",
    )
    return _composer_manifest_response(manifest)


def acquire_apply_lock(manifest_id):
    with _apply_lock_mutex:
        if manifest_id in _apply_locks:
            return False, {"error_code": "apply_in_progress"}
        _apply_locks.add(manifest_id)
        return True, None


def release_apply_lock(manifest_id):
    with _apply_lock_mutex:
        _apply_locks.discard(manifest_id)


def lab_capabilities():
    return {
        "ok": True,
        "task_categories": [{"id": c, "label": config.CAT_LABEL.get(c, c)} for c in config.CATEGORIES],
        "postprocessors": config.POSTPROCESSORS,
        "allowed_roots": ["DX_APP_ROOT", "OUTPUTS_DIR"],
        "feature_flags": {
            "portal_shell": True,
            "add_model_wizard": False,
            "task_wizard": False,
            "experiment_pipeline": False,
            "benchmark_step": False,
            "rollback": False,
        },
        "composer": {
            "schema_version": WORKFLOW_SCHEMA_VERSION,
            "templates": {
                template_id: {
                    "category": template.get("category"),
                    "input_kind": template.get("input_kind"),
                }
                for template_id, template in WORKFLOW_TEMPLATES.items()
            },
            "supported_node_kinds": list(SUPPORTED_NODE_KINDS),
            "package_types": list(PACKAGE_TYPES),
            "feature_flags": {
                "quick_start": True,
                "templates": True,
                "custom_plugins": True,
                "recipe_import_export": True,
                "run_package_export": True,
                "developer_package_export": "developer" in PACKAGE_TYPES,
                "plugin_stages": list(PLUGIN_STAGES),
                "plugin_languages": list(PLUGIN_LANGUAGES),
                "plugin_interface_version": PLUGIN_INTERFACE_VERSION,
            },
        },
    }


def _operation(action, root, path, exists=False, preview="", risk="low"):
    return {
        "action": action,
        "root": str(root),
        "path": str(path),
        "exists": exists,
        "preview": preview,
        "risk": risk,
    }


def plan_add_model(tok, payload):
    """Dry-run: validate inputs and return a manifest without writing files."""
    err = require_lab(tok)
    if err:
        return err

    mn = payload.get("model_name", "")
    cat = payload.get("category", "")
    tt = payload.get("task_type", "")
    lang = payload.get("lang", "both")
    pp = payload.get("postprocessor", "")
    source_path = payload.get("source_path", "")

    err = _require_lab_model_name(mn)
    if err:
        return err
    err = _require_lab_category(cat)
    if err:
        return err

    if source_path:
        err = _validate_source_path(source_path)
        if err:
            return err

    bases = {"cpp": [CPP_DIR], "python": [PY_DIR], "both": [CPP_DIR, PY_DIR]}.get(lang, [CPP_DIR, PY_DIR])
    operations = []
    confirmations = []
    existing_dirs = []

    for base in bases:
        try:
            target = resolve_under(str(base / cat / mn), (base,))
        except ValueError as e:
            return {"error": str(e), "status": 400}
        rel = target.relative_to(DX_APP_ROOT)
        exists = target.exists()
        operation_action = "modify" if exists else "create"
        operations.append(_operation(operation_action, "DX_APP_ROOT", str(rel), exists=exists))
        if exists:
            existing_dirs.append(str(rel))

    if existing_dirs:
        confirmations.append({
            "key": "overwrite",
            "expected": f"overwrite:{mn}",
            "label": "Overwrite existing model files",
        })

    inputs = {
        "model_name": mn,
        "category": cat,
        "task_type": tt,
        "lang": lang,
        "postprocessor": pp,
    }
    if source_path:
        inputs["source_path"] = source_path

    return create_manifest(
        kind="add_model",
        inputs=inputs,
        operations=operations,
        confirmations=confirmations,
        status="ready",
        summary=f"Add {mn} to {cat}",
    )


def _confirmations_match(manifest, payload):
    """Return (True, None) or (False, missing_confirmation_item)."""
    expected = manifest.get("confirmations", [])
    if not expected:
        return True, None
    provided = payload.get("confirmations", {})
    if not isinstance(provided, dict):
        return False, expected[0]
    for conf in expected:
        key = conf["key"]
        if provided.get(key) != conf["expected"]:
            return False, conf
    return True, None


def _validate_source_path(source_path):
    """Validate source_path under allowed roots with .dxnn extension. Returns error tuple or None."""
    raw = Path(source_path)
    if not raw.is_absolute():
        candidate = str(SCRIPT_DIR / raw)
    else:
        candidate = str(raw)
    allowed_roots = (OUTPUTS_DIR, DX_APP_ROOT)
    try:
        resolve_existing_file(candidate, allowed_roots, (".dxnn",))
    except ValueError as e:
        return {"error": str(e), "status": 400}
    return None


def plan_add_model_response(tok, payload):
    """Wrap plan_add_model for route use, converting error status non-mutatingly."""
    result = plan_add_model(tok, payload)
    return _result_with_http_status(result)


def apply_add_model(tok, payload):
    """Apply an add_model manifest: validate, lock, call dev_add with manifest inputs."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)

    manifest_id = payload.get("manifest_id", "")
    result, code = get_manifest(manifest_id)
    if code != 200:
        return result, code

    manifest = result
    if manifest["kind"] != "add_model":
        return {"error": "Invalid manifest kind", "error_code": "invalid_manifest_kind"}, 400

    if manifest["status"] != "ready":
        return {"error": "Manifest is not ready", "error_code": "manifest_not_ready"}, 400

    ok, missing = _confirmations_match(manifest, payload)
    if not ok:
        return {"error": "Confirmation required", "error_code": "confirmation_required", "missing": missing}, 400

    ok, lock_err = acquire_apply_lock(manifest["id"])
    if not ok:
        return lock_err, 409

    try:
        if manifest["status"] != "ready":
            return {"error": "Manifest is not ready", "error_code": "manifest_not_ready"}, 400
        data = manifest["inputs"]
        res = dev_add(
            tok,
            data.get("model_name", ""),
            data.get("task_type", data.get("category", "")),
            data.get("lang", "both"),
            data.get("category", "object_detection"),
            data.get("postprocessor", ""),
            False,
            True,
        )
        body, http_code = _result_with_http_status(res)
        if isinstance(body, dict) and body.get("ok") is True and http_code == 200:
            manifest["status"] = "applied"
        return body, http_code
    finally:
        release_apply_lock(manifest["id"])


def smoke_add_model(tok, payload):
    """Smoke check for add_model manifest — validates readiness without executing."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)

    manifest_id = payload.get("manifest_id", "")
    result, code = get_manifest(manifest_id)
    if code != 200:
        return result, code

    manifest = result
    if manifest["kind"] != "add_model":
        return {"error": "Invalid manifest kind", "error_code": "invalid_manifest_kind"}, 400

    if manifest["status"] != "ready":
        return {"error": "Manifest is not ready", "error_code": "manifest_not_ready"}, 400

    source_path = manifest["inputs"].get("source_path", "")
    if not source_path:
        return {"ok": False, "status": "blocked", "blocker": "source_path_required"}, 200

    err = _validate_source_path(source_path)
    if err:
        return _error_response(err, 400)

    return {"ok": False, "status": "blocked", "blocker": "sample_input_required"}, 200


def generated_files_for_manifest(manifest_id):
    """Return preview files from a manifest filtered to create/modify actions."""
    result, code = get_manifest(manifest_id)
    if code != 200:
        return result, code
    manifest = result
    files = []
    for op in manifest.get("operations", []):
        if op.get("action") in ("create", "modify"):
            preview = op.get("preview", "")
            files.append({
                "root": op.get("root", ""),
                "path": op.get("path", ""),
                "preview": preview,
                "size": len(preview.encode("utf-8")),
            })
    return {"files": files}, 200


def list_pending_manifests():
    """Return active (ready) non-expired manifests."""
    _evict_expired_manifests()
    return [m for m in _manifests.values() if not _expired(m) and m.get("status") == "ready"]


def change_summary_by_root(manifest_id):
    """Group create/modify/delete counts by root for a manifest."""
    result, code = get_manifest(manifest_id)
    if code != 200:
        return result, code
    summary = {}
    for op in result.get("operations", []):
        root = op.get("root", "unknown")
        action = op.get("action", "unknown")
        if root not in summary:
            summary[root] = {"create": 0, "modify": 0, "delete": 0}
        if action in summary[root]:
            summary[root][action] += 1
    return summary, 200


def rollback_manifest(manifest_id, payload):
    """Rollback a manifest. Rejects unsupported rollback; requires confirmations."""
    result, code = get_manifest(manifest_id)
    if code != 200:
        return result, code
    manifest = result
    rollback = manifest.get("rollback", {})
    if not rollback.get("supported"):
        return {
            "error": "Rollback not supported for this manifest",
            "error_code": "rollback_unsupported",
            "message": "Manual rollback required. Review the manifest operations and undo changes manually.",
        }, 400
    ok, missing = _confirmations_match(manifest, payload)
    if not ok:
        return {"error": "Confirmation required", "error_code": "confirmation_required", "missing": missing}, 400
    return {"ok": True, "message": "Rollback planned (preview only)"}, 200


def scoped_git_plan(manifest_id, payload):
    """Return scoped git plan with files derived only from manifest operations."""
    result, code = get_manifest(manifest_id)
    if code != 200:
        return result, code
    manifest = result
    manifest_paths = {op.get("path") for op in manifest.get("operations", []) if op.get("path")}

    requested_files = payload.get("files")
    if requested_files:
        outside = [f for f in requested_files if f not in manifest_paths]
        if outside:
            return {
                "error": "Files not present in manifest operations",
                "error_code": "path_not_in_manifest",
                "invalid_paths": outside,
            }, 400
        plan_files = list(requested_files)
    else:
        plan_files = sorted(manifest_paths)

    if payload.get("push"):
        confirmations = payload.get("confirmations", {})
        if confirmations.get("push") != "push":
            return {
                "error": "Push confirmation required",
                "error_code": "confirmation_required",
                "missing": {"key": "push", "expected": "push", "label": "Confirm push"},
            }, 400

    return {"files": plan_files, "preview_only": True}, 200


_SAFE_LAB_ID_RE = re.compile(r"^lab_[A-Za-z0-9_-]+$")


def validate_lab_manifest_id(manifest_id):
    """Return None if safe, or an error string if the ID is unsafe."""
    if not manifest_id:
        return "Empty manifest id"
    if "/" in manifest_id or "\\" in manifest_id or "." in manifest_id:
        return "Unsafe manifest id"
    if not _SAFE_LAB_ID_RE.match(manifest_id):
        return "Invalid manifest id format"
    return None




def plan_task_scaffold(tok, payload):
    """Dry-run: validate inputs and return a manifest with generated file previews."""
    err = require_lab(tok)
    if err:
        return err

    task_name = payload.get("task_name", "")
    lang = payload.get("lang", "both")
    scaffold_type = payload.get("scaffold_type", "full")

    file_plan, plan_err = build_task_file_plan(task_name, lang, scaffold_type, cpp_dir=CPP_DIR, py_dir=PY_DIR)
    if plan_err:
        return plan_err

    operations = []
    confirmations = []
    existing_files = []

    for fp, content in file_plan:
        # Path safety: ensure target stays under allowed roots
        if lang in ("both", "cpp") and str(fp).startswith(str(CPP_DIR)):
            allowed = (CPP_DIR / "common",)
        else:
            allowed = (PY_DIR / "common",)
        try:
            resolved = resolve_under(str(fp), allowed)
        except ValueError as e:
            return {"error": str(e), "status": 400}

        rel = resolved.relative_to(DX_APP_ROOT)
        exists = resolved.exists()
        action = "modify" if exists else "create"
        operations.append(_operation(action, "DX_APP_ROOT", str(rel), exists=exists, preview=content))
        if exists:
            existing_files.append(str(rel))

    if existing_files:
        normalized = task_name.lower().replace("-", "_")
        confirmations.append({
            "key": "overwrite",
            "expected": f"overwrite:{normalized}",
            "label": "Overwrite existing task files",
        })

    inputs = {
        "task_name": task_name,
        "lang": lang,
        "scaffold_type": scaffold_type,
    }

    return create_manifest(
        kind="task_scaffold",
        inputs=inputs,
        operations=operations,
        confirmations=confirmations,
        status="ready",
        summary=f"Create {task_name} task skeleton ({scaffold_type})",
    )


def plan_task_scaffold_response(tok, payload):
    """Wrap plan_task_scaffold for route use, converting error status non-mutatingly."""
    result = plan_task_scaffold(tok, payload)
    return _result_with_http_status(result)


EXPERIMENT_STEPS = ["compile", "register", "smoke", "benchmark", "package"]
_STEP_INDEX = {s: i for i, s in enumerate(EXPERIMENT_STEPS)}
MAX_EXPERIMENT_RUNS = 128
_LOG_MAX_CHARS = 4096
_LOG_LINE_MAX_CHARS = 1024
_experiment_runs = OrderedDict()
_experiment_lock = threading.Lock()

_SAFE_RUN_ID_RE = re.compile(r"^run_[A-Za-z0-9_-]+$")


def _safe_run_id():
    return f"run_{int(time.time())}_{secrets.token_urlsafe(8).replace('-', '_')}"


def _validate_run_id(run_id):
    """Return error tuple (body, code) if invalid, else None."""
    if not run_id or "/" in run_id or "\\" in run_id or "." in run_id:
        return {"error": "Unsafe run id", "error_code": "invalid_run_id"}, 400
    if not _SAFE_RUN_ID_RE.match(run_id):
        return {"error": "Invalid run id format", "error_code": "invalid_run_id"}, 400
    return None


def _validate_experiment_source_path(source_path):
    """Validate source_path for experiment runs. Returns error tuple or None."""
    raw = Path(source_path)
    if not raw.is_absolute():
        candidate = str(SCRIPT_DIR / raw)
    else:
        candidate = str(raw)
    allowed_roots = (OUTPUTS_DIR, DX_APP_ROOT)
    try:
        resolve_existing_file(candidate, allowed_roots, (".dxnn",))
    except ValueError as e:
        return {"error": str(e), "error_code": "invalid_source_path"}, 400
    return None


def _new_run_state(run_id, inputs):
    now = time.time()
    steps = [
        {"id": s, "status": "current" if i == 0 else "pending"}
        for i, s in enumerate(EXPERIMENT_STEPS)
    ]
    return {
        "id": run_id,
        "status": "pending",
        "current_step": "compile",
        "steps": steps,
        "inputs": dict(inputs),
        "blockers": [],
        "log_tail": [],
        "created_at": now,
        "updated_at": now,
    }


def _evict_experiment_runs():
    """Evict oldest completed/cancelled/failed runs when over cap."""
    while len(_experiment_runs) > MAX_EXPERIMENT_RUNS:
        evicted = False
        for rid in list(_experiment_runs):
            if _experiment_runs[rid]["status"] in ("completed", "cancelled", "failed"):
                _experiment_runs.pop(rid, None)
                evicted = True
                break
        if not evicted:
            _experiment_runs.popitem(last=False)


def _deep_copy_run(run):
    """Return a deep copy of a run dict for immutability."""
    import copy
    return copy.deepcopy(run)


_TERMINAL_STATUSES = {"cancelled", "failed", "completed"}


def active_experiment_run_for_source(source_path):
    """Return run id if source_path has a non-terminal active run, else None."""
    with _experiment_lock:
        for rid, run in _experiment_runs.items():
            if run["status"] not in _TERMINAL_STATUSES and run.get("inputs", {}).get("source_path") == source_path:
                return rid
    return None


def start_experiment_run(payload):
    source_path = payload.get("source_path", "")
    if not source_path:
        return {"error": "source_path required", "error_code": "missing_source_path"}, 400

    err = _validate_experiment_source_path(source_path)
    if err:
        return err

    run_id = _safe_run_id()
    inputs = {"source_path": source_path, "model_name": payload.get("model_name", "")}
    run = _new_run_state(run_id, inputs)

    with _experiment_lock:
        # Atomic duplicate-source check under the same lock that inserts
        for rid, existing in _experiment_runs.items():
            if existing["status"] not in _TERMINAL_STATUSES and existing.get("inputs", {}).get("source_path") == source_path:
                return {"error": "Experiment already running for this source", "error_code": "run_in_progress"}, 409
        _experiment_runs[run_id] = run
        _evict_experiment_runs()
        return _deep_copy_run(run), 200


def get_experiment_run(run_id):
    err = _validate_run_id(run_id)
    if err:
        return err
    with _experiment_lock:
        run = _experiment_runs.get(run_id)
        if not run:
            return {"error": "Run not found", "error_code": "run_not_found"}, 404
        return _deep_copy_run(run), 200


def cancel_experiment_run(run_id):
    err = _validate_run_id(run_id)
    if err:
        return err
    with _experiment_lock:
        run = _experiment_runs.get(run_id)
        if not run:
            return {"error": "Run not found", "error_code": "run_not_found"}, 404

        # Terminal-state guard (consistent with advance/fail)
        if run["status"] in ("cancelled", "failed", "completed"):
            return {"error": "Run is in terminal state", "error_code": "run_terminal"}, 409

        run["status"] = "cancelled"
        run["updated_at"] = time.time()
        for step in run["steps"]:
            if step["status"] in ("pending", "current"):
                step["status"] = "cancelled"
        return _deep_copy_run(run), 200


def advance_experiment_step(run_id, next_step):
    err = _validate_run_id(run_id)
    if err:
        return err
    with _experiment_lock:
        run = _experiment_runs.get(run_id)
        if not run:
            return {"error": "Run not found", "error_code": "run_not_found"}, 404

        # Terminal-state guard
        if run["status"] in ("cancelled", "failed", "completed"):
            return {"error": "Run is in terminal state", "error_code": "run_terminal"}, 409

        current = run["current_step"]
        cur_idx = _STEP_INDEX.get(current)
        next_idx = _STEP_INDEX.get(next_step)

        if next_idx is None or cur_idx is None or next_idx != cur_idx + 1:
            return {"error": "Invalid step transition", "error_code": "invalid_step_transition"}, 400

        run["steps"][cur_idx]["status"] = "done"
        run["steps"][next_idx]["status"] = "current"
        run["current_step"] = next_step
        run["updated_at"] = time.time()

        return _deep_copy_run(run), 200


def mark_experiment_step_failed(run_id, step, message):
    err = _validate_run_id(run_id)
    if err:
        return err
    with _experiment_lock:
        run = _experiment_runs.get(run_id)
        if not run:
            return {"error": "Run not found", "error_code": "run_not_found"}, 404

        # Terminal-state guard
        if run["status"] in ("cancelled", "failed", "completed"):
            return {"error": "Run is in terminal state", "error_code": "run_terminal"}, 409

        step_idx = _STEP_INDEX.get(step)
        if step_idx is None:
            return {"error": "Unknown step", "error_code": "unknown_step"}, 400

        # Only the current step can be marked as failed
        if step != run["current_step"]:
            return {"error": "Can only fail the current step", "error_code": "invalid_step"}, 400

        run["steps"][step_idx]["status"] = "failed"
        run["steps"][step_idx]["message"] = str(message)
        run["status"] = "failed"
        run["blockers"].append({"code": f"{step}_failed", "message": str(message)})
        run["updated_at"] = time.time()

        for s in run["steps"]:
            if s["status"] in ("pending", "current") and s["id"] != step:
                s["status"] = "cancelled"

        return _deep_copy_run(run), 200


def append_experiment_log(run_id, line):
    err = _validate_run_id(run_id)
    if err:
        return err
    with _experiment_lock:
        run = _experiment_runs.get(run_id)
        if not run:
            return {"error": "Run not found", "error_code": "run_not_found"}, 404

        truncated = str(line)[:_LOG_LINE_MAX_CHARS]
        run["log_tail"].append(truncated)
        run["updated_at"] = time.time()

        # Bound log_tail to _LOG_MAX_CHARS total joined length (linear approach)
        total = sum(len(entry) for entry in run["log_tail"])
        total += max(len(run["log_tail"]) - 1, 0)  # newline separators
        while run["log_tail"] and total > _LOG_MAX_CHARS:
            removed = run["log_tail"].pop(0)
            total -= len(removed)
            if run["log_tail"]:
                total -= 1  # removed a newline separator

    return {"ok": True}, 200


def apply_task_scaffold(tok, payload):
    """Apply a task_scaffold manifest: validate, lock, call dev_new_task with manifest inputs."""
    err = require_lab(tok)
    if err:
        return _error_response(err, 403)

    manifest_id = payload.get("manifest_id", "")
    result, code = get_manifest(manifest_id)
    if code != 200:
        return result, code

    manifest = result
    if manifest["kind"] != "task_scaffold":
        return {"error": "Invalid manifest kind", "error_code": "invalid_manifest_kind"}, 400

    if manifest["status"] != "ready":
        return {"error": "Manifest is not ready", "error_code": "manifest_not_ready"}, 400

    ok, missing = _confirmations_match(manifest, payload)
    if not ok:
        return {"error": "Confirmation required", "error_code": "confirmation_required", "missing": missing}, 400

    ok, lock_err = acquire_apply_lock(manifest["id"])
    if not ok:
        return lock_err, 409

    try:
        if manifest["status"] != "ready":
            return {"error": "Manifest is not ready", "error_code": "manifest_not_ready"}, 400
        data = manifest["inputs"]
        res = dev_new_task(
            tok,
            data.get("task_name", ""),
            data.get("lang", "both"),
            confirm_overwrite=True,
            scaffold_type=data.get("scaffold_type", "full"),
        )
        body, http_code = _result_with_http_status(res)
        if isinstance(body, dict) and body.get("ok") is True and http_code == 200:
            manifest["status"] = "applied"
        return body, http_code
    finally:
        release_apply_lock(manifest["id"])

"""Lab Extension Portal backend helpers."""

import copy
import re
import secrets
import shlex
import shutil
import subprocess
import threading
import time
from pathlib import Path
from collections import OrderedDict

from dx_app.core import config
from dx_app.core.config import DX_APP_ROOT, CPP_DIR, PY_DIR, OUTPUTS_DIR
from dx_app.core.developer import require_lab, _require_lab_model_name, _require_lab_category, dev_add, dev_new_task, build_task_file_plan, pick_reference, reference_examples
from dx_app.core.dx_app_security import resolve_existing_file, resolve_under

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
        "reference_examples": reference_examples(),
        "experiment_models": experiment_model_choices(),
        "allowed_roots": ["DX_APP_ROOT", "OUTPUTS_DIR"],
        "feature_flags": {
            "portal_shell": True,
            "add_model_wizard": True,
            "task_wizard": True,
            "experiment_pipeline": True,
            "benchmark_step": True,
            "rollback": True,
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
    if lang not in ("cpp", "python", "both"):
        lang = "both"

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

    base_model, err = pick_reference(cat, lang, payload.get("base_model", ""))
    if err:
        return err

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
        "base_model": base_model,
    }
    if source_path:
        inputs["source_path"] = source_path

    return create_manifest(
        kind="add_model",
        inputs=inputs,
        operations=operations,
        confirmations=confirmations,
        status="ready",
        summary=f"Add {mn} to {cat} (from {base_model})",
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
            base_model=data.get("base_model", ""),
        )
        body, http_code = _result_with_http_status(res)
        if isinstance(body, dict) and body.get("ok") is True and http_code == 200:
            _mark_applied(manifest, data.get("model_name", ""), body.get("created") or [],
                          overwrote=bool(body.get("overwrote")))
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
    """Files of a Lab change: the previews of a dry run, or what an applied change really wrote."""
    result, code = get_manifest(manifest_id)
    if code != 200:
        return result, code
    manifest = result
    if manifest.get("status") == "applied":
        return {"files": _applied_files(manifest)}, 200
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


_PREVIEW_MAX_BYTES = 64 * 1024


def _applied_files(manifest):
    """Every file under the paths an applied change wrote, with a text preview (pycache left out)."""
    files = []
    for op in manifest.get("operations", []):
        target = DX_APP_ROOT / op.get("path", "")
        paths = sorted(p for p in target.rglob("*") if p.is_file()) if target.is_dir() else [target]
        for p in paths:
            if not p.is_file() or "__pycache__" in p.parts:
                continue
            size = p.stat().st_size
            try:
                preview = p.read_text(encoding="utf-8", errors="replace") if size <= _PREVIEW_MAX_BYTES else ""
            except OSError:
                preview = ""
            files.append({"root": "DX_APP_ROOT", "path": p.relative_to(DX_APP_ROOT).as_posix(),
                          "preview": preview, "size": size})
    return files


_LAB_CHANGE_KINDS = ("add_model", "task_scaffold")
_LISTED_STATUSES = ("ready", "applied", "rolled_back")


def list_pending_manifests():
    """Return active (ready) non-expired manifests."""
    _evict_expired_manifests()
    return [m for m in _manifests.values() if not _expired(m) and m.get("status") == "ready"]


def list_lab_manifests():
    """Add Model / Create Task changes of this session, newest first — previews, applied and rolled back."""
    _evict_expired_manifests()
    with _manifests_lock:
        items = [m for m in _manifests.values()
                 if not _expired(m) and m.get("kind") in _LAB_CHANGE_KINDS and m.get("status") in _LISTED_STATUSES]
    items = sorted(items, key=lambda m: m.get("applied_at") or m.get("created_at", 0), reverse=True)
    # Each Dry Run makes a manifest; of the previews for one target only the newest is worth listing.
    seen, out = set(), []
    for m in items:
        inputs = m.get("inputs", {})
        key = (m.get("kind"), inputs.get("model_name") or inputs.get("task_name"), inputs.get("category"))
        if m.get("status") == "ready":
            if key in seen:
                continue
            seen.add(key)
        out.append(m)
    return out


def _mark_applied(manifest, name, created, overwrote=False):
    """Record what an apply wrote. Rollback deletes exactly the paths that did not exist before; a change that
    overwrote existing files cannot be undone by deleting, so it is left to the user."""
    manifest["status"] = "applied"
    manifest["applied_at"] = time.time()
    manifest["rollback"] = {
        "supported": bool(created) and not overwrote,
        "paths": list(created),
        "confirmation": {"key": "rollback", "expected": f"rollback:{name}", "label": f"Type rollback:{name}"},
    }


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
    """Undo an applied Lab change: delete exactly the paths its apply created, after a typed confirmation."""
    result, code = get_manifest(manifest_id)
    if code != 200:
        return result, code
    manifest = result
    if manifest.get("status") != "applied":
        return {"error": "Only an applied change can be rolled back", "error_code": "not_applied"}, 400
    rollback = manifest.get("rollback", {})
    if not rollback.get("supported"):
        return {
            "error": "Rollback not supported for this manifest",
            "error_code": "rollback_unsupported",
            "message": "This change overwrote existing files. Review the listed paths and restore them manually.",
        }, 400
    confirmation = rollback.get("confirmation") or {}
    provided = payload.get("confirmations") if isinstance(payload.get("confirmations"), dict) else {}
    if not confirmation or provided.get(confirmation.get("key")) != confirmation.get("expected"):
        return {"error": "Confirmation required", "error_code": "confirmation_required", "missing": confirmation}, 400
    removed = []
    for rel in rollback.get("paths", []):
        try:
            target = resolve_under(str(DX_APP_ROOT / rel), (PY_DIR, CPP_DIR))
        except ValueError:
            continue
        if target.is_dir():
            shutil.rmtree(target)
        elif target.is_file():
            target.unlink()
        else:
            continue
        removed.append(rel)
    from shared import dx_app_layout as _layout
    _layout.clear_cache()
    manifest["status"] = "rolled_back"
    manifest["rolled_back_at"] = time.time()
    return {"ok": True, "removed": removed, "message": f"Removed {len(removed)} path(s)."}, 200


def scoped_git_plan(manifest_id, payload):
    """Return the files a Lab change wrote and the git commands that commit exactly those.

    Studio never runs git on the user's dx_app checkout; it hands over the commands. An applied change lists what
    the apply really created (rollback paths); otherwise the manifest operation paths."""
    result, code = get_manifest(manifest_id)
    if code != 200:
        return result, code
    manifest = result
    if manifest.get("status") == "rolled_back":
        return {"error": "This change was rolled back; there is nothing to commit.",
                "error_code": "nothing_to_commit"}, 409
    manifest_paths = {op.get("path") for op in manifest.get("operations", []) if op.get("path")}
    created = (manifest.get("rollback") or {}).get("paths") or []
    if manifest.get("status") == "applied" and created:
        manifest_paths = set(created)

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

    repo = str(DX_APP_ROOT)
    message = manifest.get("summary") or f"Lab change {manifest_id}"
    commands = [
        f"git -C {shlex.quote(repo)} add -- " + " ".join(shlex.quote(f) for f in plan_files),
        f"git -C {shlex.quote(repo)} commit -m {shlex.quote(message)}",
    ]
    return {"files": plan_files, "repo": repo, "commands": commands, "preview_only": True}, 200


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


# The input is a compiled .dxnn, so the pipeline checks it with the DX-RT tools rather than compiling:
# inspect (parse_model reads the file), smoke (one inference on the NPU), benchmark (throughput, FPS).
EXPERIMENT_STEPS = ["inspect", "smoke", "benchmark"]
EXPERIMENT_BENCHMARK_LOOPS = 100
_EXPERIMENT_STEP_TIMEOUT = 180
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
        "current_step": EXPERIMENT_STEPS[0],
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
        proc = _experiment_procs.get(run_id)
        if proc is not None:
            try:
                proc.kill()
            except OSError:
                pass
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


_experiment_procs = {}
_FPS_RE = re.compile(r"FPS\s*:\s*([0-9]+(?:\.[0-9]+)?)")


def _experiment_popen(cmd, **kwargs):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            errors="replace", **kwargs)


def _dxrt_tool(name):
    return shutil.which(name) or f"/usr/local/bin/{name}"


def _experiment_commands(model_path):
    return {
        "inspect": [_dxrt_tool("parse_model"), "-m", model_path],
        "smoke": [_dxrt_tool("run_model"), "-m", model_path, "-s", "-l", "1"],
        "benchmark": [_dxrt_tool("run_model"), "-m", model_path, "-l", str(EXPERIMENT_BENCHMARK_LOOPS)],
    }


def _experiment_source(source_path):
    raw = Path(source_path)
    return str(raw if raw.is_absolute() else SCRIPT_DIR / raw)


def _run_experiment_step(run_id, step, cmd):
    """Run one step's command, streaming its output into the run log. Returns (ok, last_lines)."""
    try:
        proc = _experiment_popen(cmd)
    except OSError as exc:
        return False, [f"{Path(cmd[0]).name}: {exc}"]
    with _experiment_lock:
        _experiment_procs[run_id] = proc
    lines = []
    try:
        for line in proc.stdout:
            line = line.rstrip()
            if not line.strip():
                continue
            lines.append(line)
            append_experiment_log(run_id, line)
        rc = proc.wait(timeout=_EXPERIMENT_STEP_TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        return False, lines + [f"{step} timed out after {_EXPERIMENT_STEP_TIMEOUT}s"]
    finally:
        with _experiment_lock:
            _experiment_procs.pop(run_id, None)
    failed = rc != 0 or any("[dxrt-exception]" in l for l in lines)
    return not failed, lines[-3:]


def _experiment_cancelled(run_id):
    with _experiment_lock:
        run = _experiment_runs.get(run_id)
        return not run or run["status"] == "cancelled"


def _experiment_worker(run_id):
    with _experiment_lock:
        run = _experiment_runs.get(run_id)
        if not run or run["status"] != "pending":
            return
        run["status"] = "running"
        source = run["inputs"]["source_path"]
    commands = _experiment_commands(_experiment_source(source))
    for index, step in enumerate(EXPERIMENT_STEPS):
        if _experiment_cancelled(run_id):
            return
        append_experiment_log(run_id, f"$ {' '.join([Path(commands[step][0]).name] + commands[step][1:])}")
        ok, tail = _run_experiment_step(run_id, step, commands[step])
        if _experiment_cancelled(run_id):
            return
        if not ok:
            reason = next((l for l in reversed(tail) if l.strip()), f"{step} failed")
            mark_experiment_step_failed(run_id, step, reason.strip())
            return
        if step == "benchmark":
            fps = [float(m.group(1)) for l in tail for m in [_FPS_RE.search(l)] if m]
            with _experiment_lock:
                run = _experiment_runs.get(run_id)
                if run is not None and fps:
                    run["result"] = {"fps": fps[-1], "loops": EXPERIMENT_BENCHMARK_LOOPS}
        if index + 1 < len(EXPERIMENT_STEPS):
            advance_experiment_step(run_id, EXPERIMENT_STEPS[index + 1])
    with _experiment_lock:
        run = _experiment_runs.get(run_id)
        if run is not None and run["status"] == "running":
            run["steps"][-1]["status"] = "done"
            run["status"] = "completed"
            run["updated_at"] = time.time()


def launch_experiment_run(run_id):
    """Start the worker that drives a pending run through inspect → smoke → benchmark."""
    worker = threading.Thread(target=_experiment_worker, args=(run_id,), name=f"lab-experiment-{run_id}",
                              daemon=True)
    worker.start()
    return worker


def experiment_model_choices():
    """Compiled models the Experiment can check: outputs/ first (what the user compiled), then assets/models."""
    seen, out = set(), []
    for root in (OUTPUTS_DIR, DX_APP_ROOT / "assets" / "models"):
        try:
            found = sorted(root.rglob("*.dxnn"), key=lambda p: (-p.stat().st_mtime, p.name))
        except OSError:
            continue
        for p in found[:200]:
            if p.name in seen or p.stat().st_size == 0:
                continue
            seen.add(p.name)
            out.append({"name": p.stem, "path": str(p)})
    return out


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
            ops = manifest.get("operations", [])
            _mark_applied(manifest, (data.get("task_name", "") or "").lower().replace("-", "_"),
                          [op["path"] for op in ops if op.get("action") == "create"],
                          overwrote=any(op.get("action") == "modify" for op in ops))
        return body, http_code
    finally:
        release_apply_lock(manifest["id"])

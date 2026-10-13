#!/usr/bin/env python3
"""DX Model Zoo web server — port 8094."""
import json
import threading
from pathlib import Path

from shared.dx_server import DXBaseHandler, DXServer
from shared.chat import ChatEngine
from shared.chat import module_fallbacks as _module_fallbacks
from dx_modelzoo.core.config import (DEFAULT_PORT, STATIC_DIR, TEMPLATES_DIR, DATA_DIR,
                         DX_APP_ROOT, CPP_DIR, PY_DIR, SERVER_NAME,
                         SAMPLE_IMG_DIR, SAMPLE_IMAGES, MODEL_IMAGE_OVERRIDE)
from dx_modelzoo.core.catalog import (
    get_catalog,
    reload_catalog,
    filter_models,
    catalog_stats,
    get_model,
    count_by_category,
    query_catalog,
    apply_generated_catalog,
    build_catalog_view_payload,
)
from dx_modelzoo.core.proxy import proxy_request, is_dx_app_alive, is_safe_model_id
from dx_modelzoo.metadata.sanitize import sanitize_browser_model
from dx_modelzoo.core.model_card import catalog_date
from dx_modelzoo.core.model_card_labels import LABELS as MODEL_CARD_LABELS
from dx_modelzoo.core.model_card_studio import DxAppMissing, NoDxAppExample, studio_card
from shared.paths import STUDIO_ROOT
from shared.shell import ShellSpec


def _collect_demo_files(demo):
    """Collect cpp/python example code from the demo dict and return (cpp_code, py_code)."""
    cpp_code = py_code = ""
    cpp_rel = demo.get("cpp_example", "")
    if cpp_rel:
        cpp_dir = DX_APP_ROOT / cpp_rel
        if cpp_dir.is_dir():
            if not _is_safe_demo_dir(cpp_dir, DX_APP_ROOT):
                raise ValueError("Path traversal detected")
            for f in sorted(cpp_dir.glob("*.cpp")):
                cpp_code += f"// === {f.name} ===\n{f.read_text(encoding='utf-8', errors='replace')}\n\n"
    py_rel = demo.get("python_example", "")
    if py_rel:
        py_dir = DX_APP_ROOT / py_rel
        if py_dir.is_dir():
            if not _is_safe_demo_dir(py_dir, DX_APP_ROOT):
                raise ValueError("Path traversal detected")
            for f in sorted(py_dir.glob("*.py")):
                py_code += f"# === {f.name} ===\n{f.read_text(encoding='utf-8', errors='replace')}\n\n"
    return cpp_code, py_code


def _is_safe_demo_dir(path, root):
    """Check, after resolving, that a path is under root (prevents symlink/prefix escapes)."""
    # Python 3.8-safe (Path.is_relative_to is 3.9+): decide with relative_to + ValueError.
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False

# Runtime state of the metadata sync
_sync_state = {
    "last_report": None,
    "last_synced_at": None,
    "source_profile": "public",
}
_sync_lock = threading.RLock()
_sync_running = False

_chat_engine = ChatEngine(
    app_name="dx_modelzoo",
    fallback_rules=_module_fallbacks.rules("dx_modelzoo")
)



# ── Shared app shell ────────────────────────────────────────────
# A single catalog screen, so there is no tab row — the template root carries .dx-shell--no-tabs.
# The model count is page-level state and sits on the left of the header (next to the page name);
# the homepage link and the dx_app connection dot go in the toolbar slot.
_MODEL_COUNT = '<span class="mz-model-count" id="modelCount"></span>'

_ZOO_TOOLBAR = (
    '<a href="https://developer.deepx.ai/modelzoo/" target="_blank" rel="noopener"'
    ' class="mz-btn mz-btn-outline mz-homepage-link" style="gap:4px;white-space:nowrap;text-decoration:none"'
    ' data-i18n-title="ModelZoo public site" title="ModelZoo public site"'
    ' aria-label="ModelZoo public site" data-i18n-aria-label="ModelZoo public site">'
    '<span class="mz-homepage-text" data-i18n="ModelZoo Homepage">ModelZoo Homepage</span>'
    '<svg class="dx-ico" aria-hidden="true"><use href="/static/shared/dx-icons.svg#external"></use></svg></a>'
    # A bare 8px dot did not say what it was the status of (and the tutorial spotlight was just a dot) — add a label
    '<span class="mz-dx-app-indicator" id="dxAppIndicator" role="status" title="DX App">'
    '<span class="mz-dx-app-status" id="dxAppStatus" aria-hidden="true"></span>'
    '<span class="mz-dx-app-label">DX App</span></span>'
)

DX_MODELZOO_SHELL = ShellSpec(
    module_key="zoo",
    toolbar_extra=_ZOO_TOOLBAR,
    header_extra=_MODEL_COUNT,
)

class ModelZooHandler(DXBaseHandler):
    server_name = SERVER_NAME
    static_dir = STATIC_DIR
    templates_dir = TEMPLATES_DIR
    shell_spec = DX_MODELZOO_SHELL
    log_silent = True

    def route(self):
        if self.handle_chat_routes(_chat_engine):
            return

        if self.route_common():
            return

        path = self.url_path
        qs = self.query

        if self.command == "GET":
            if path == "/api/catalog":
                cat = get_catalog()
                category = qs.get("category", [None])[0]
                search = qs.get("search", [None])[0]
                models = filter_models(cat["models"], category=category, search=search)
                stats = catalog_stats(models)
                safe_models = [sanitize_browser_model(model) for model in models]
                payload = {"ok": True, "models": safe_models,
                           "categories": cat["categories"], "count": len(safe_models),
                           "variant_count": stats["variant_count"],
                           "unique_model_count": stats["unique_model_count"]}
                # When and from what this list was built. The handler picks fields explicitly, so putting
                # them on get_catalog() alone would not reach the page.
                for key in ("generated_at", "source_profile"):
                    if cat.get(key):
                        payload[key] = cat[key]
                return self.send_json(payload)

            if path == "/api/categories":
                cat = get_catalog()
                counts = count_by_category(cat["models"])
                cats = []
                for cid, cinfo in cat["categories"].items():
                    cats.append({"id": cid, **cinfo, "count": counts.get(cid, 0)})
                return self.send_json({"ok": True, "categories": cats})

            if path == "/api/health":
                return self.send_json({"ok": True, "dx_app_alive": is_dx_app_alive()})

            if path == "/api/sample-images":
                category = qs.get("category", [None])[0]
                model_id = qs.get("model_id", [None])[0]
                images = []
                default_image = None
                sample_dir = None
                if SAMPLE_IMG_DIR.exists():
                    images = sorted(
                        f.name for f in SAMPLE_IMG_DIR.iterdir()
                        if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png'}
                    )
                    # Per-model override wins over the task default (e.g. scrfd500m_ppu
                    # is a face detector → sample_face, not the ppu default street shot).
                    raw_default = MODEL_IMAGE_OVERRIDE.get(model_id or "") or SAMPLE_IMAGES.get(category or "", "")
                    if raw_default:
                        fname = Path(raw_default).name
                        if fname in images:
                            default_image = fname
                    if not default_image and images:
                        default_image = images[0]
                    # The grid + run path both need the dir the files live in (relative
                    # to dx_app root). Without this the client bails with "Sample not
                    # available" even though images exist.
                    if images:
                        sample_dir = "sample/img"
                return self.send_json({"ok": True, "images": images,
                                       "default": default_image, "sample_dir": sample_dir})

            if path.startswith("/api/sample-image/"):
                filename = path[len("/api/sample-image/"):]
                if not filename:
                    return self.send_error(400, "Filename required")
                try:
                    target = (SAMPLE_IMG_DIR / filename).resolve()
                    target.relative_to(SAMPLE_IMG_DIR.resolve())  # 3.8-safe; raises ValueError if outside root
                except Exception:
                    return self.send_error(403, "Forbidden")
                if not target.is_file():
                    return self.send_error(404, "Not Found")
                if target.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
                    return self.send_error(403, "Forbidden")
                suffix = target.suffix.lower()
                content_type = "image/png" if suffix == ".png" else "image/jpeg"
                data = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                self.wfile.write(data)
                return

            # API: card/list catalog view (handled before the model-detail prefix match)
            if path in ("/api/catalog/card", "/api/catalog/list"):
                cat = get_catalog()
                view = "card" if path.endswith("/card") else "list"
                payload = build_catalog_view_payload(
                    cat["models"],
                    cat["categories"],
                    view=view,
                    category=qs.get("category", [None])[0],
                    search=qs.get("search", [None])[0],
                    sort=qs.get("sort", ["name"])[0],
                    direction=qs.get("dir", ["asc"])[0],
                    page=qs.get("page", ["1"])[0],
                    page_size=qs.get("page_size", ["60"])[0],
                )
                payload["models"] = [sanitize_browser_model(model) for model in payload["models"]]
                return self.send_json(payload)

            # API: paginated catalog (matched before model detail)
            if path == "/api/catalog/page":
                cat = get_catalog()
                category = qs.get("category", [None])[0]
                search = qs.get("search", [None])[0]
                filtered_models = filter_models(cat["models"], category=category, search=search)
                stats = catalog_stats(filtered_models)
                result = query_catalog(
                    cat["models"],
                    category=category,
                    search=search,
                    sort=qs.get("sort", ["name"])[0],
                    direction=qs.get("dir", ["asc"])[0],
                    page=qs.get("page", ["1"])[0],
                    page_size=qs.get("page_size", ["60"])[0],
                )
                safe_models = [sanitize_browser_model(model) for model in result["models"]]
                return self.send_json({
                    "ok": True,
                    "models": safe_models,
                    "categories": cat["categories"],
                    "count": result["total"],
                    "total": result["total"],
                    "page": result["page"],
                    "page_size": result["page_size"],
                    "pages": result["pages"],
                    "has_next": result["has_next"],
                    "has_prev": result["has_prev"],
                    "variant_count": stats["variant_count"],
                    "unique_model_count": stats["unique_model_count"],
                })

            # API: artifact endpoint (matched before model detail)
            if path.startswith("/api/catalog/") and "/artifacts/" in path:
                return self._handle_artifact_request(path)

            if path == "/api/metadata/sync/status":
                return self._handle_sync_status()

            if path == "/api/metadata/sync/report":
                return self._handle_sync_report()

            if path == "/api/model_card/labels":
                return self.send_json({"ok": True, "keys": list(MODEL_CARD_LABELS)})

            # API: model detail (after categories/health — avoids prefix collisions)
            if path.startswith("/api/catalog/"):
                model_id = path[len("/api/catalog/"):]
                if not is_safe_model_id(model_id):
                    return self.send_json({"ok": False, "error": "Invalid model ID", "code": "INVALID_PARAM"}, 400)
                cat = get_catalog()
                model = get_model(cat["models"], model_id)
                if not model:
                    return self.send_json({"ok": False, "error": f"Model '{model_id}' not found", "code": "MODEL_NOT_FOUND"}, 404)
                return self.send_json({"ok": True, "model": sanitize_browser_model(model)})

            if path.startswith("/api/demo/code/"):
                model_id = path[len("/api/demo/code/"):]
                return self._serve_demo_code(model_id)

            if path.startswith("/api/proxy/"):
                return self._handle_proxy("GET", path, self.parsed.query)

            if path.startswith("/data/"):
                rel = path[6:]
                # Thumbnail fallback: some catalog ids are resolution/variant spins
                # (e.g. yolov5m6_1280) that have no per-id thumbnail file. Fall back to the
                # base-family thumbnail by dropping trailing _<token> segments one at a time,
                # so the card shows the architecture's image instead of a broken placeholder.
                if rel.startswith("thumbnails/") and rel.endswith(".jpg") \
                        and not (DATA_DIR / rel).is_file():
                    stem = rel[len("thumbnails/"):-len(".jpg")]
                    while "_" in stem:
                        stem = stem.rsplit("_", 1)[0]
                        cand = DATA_DIR / "thumbnails" / (stem + ".jpg")
                        if cand.is_file():
                            rel = "thumbnails/" + stem + ".jpg"
                            break
                return self.serve_static(rel, DATA_DIR)

        if self.command == "POST":
            if path == "/api/metadata/sync":
                return self._handle_sync_post()

            if path.startswith("/api/model_card/"):
                return self._handle_model_card(path[len("/api/model_card/"):])

            if path.startswith("/api/proxy/"):
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length) if length else None
                ct = self.headers.get("Content-Type", "")
                return self._handle_proxy("POST", path, self.parsed.query, body, ct)

        self.route_legacy()

    def _handle_model_card(self, model_id):
        """POST /api/model_card/<id> {lang, labels, task_label} → the card as an HTML attachment."""
        payload = self.read_json_body()  # bad JSON → RequestBodyError → 400 in the dispatcher
        if not is_safe_model_id(model_id):
            return self.send_json({"ok": False, "error": "Invalid model ID", "code": "INVALID_PARAM"}, 400)
        cat = get_catalog()
        model = get_model(cat["models"], model_id)
        if not model:
            return self.send_json({"ok": False, "error": f"Model '{model_id}' not found", "code": "MODEL_NOT_FOUND"}, 404)
        try:
            html, filename = studio_card(model, cat.get("categories") or {}, payload, dx_app_root=DX_APP_ROOT,
                                         data_dir=DATA_DIR,
                                         benchmark_path=STUDIO_ROOT / "dx_benchmark" / "dataset.json",
                                         asof=catalog_date(cat.get("generated_at")))
        except DxAppMissing:
            return self.send_json({"ok": False, "error": "The dx_app checkout is missing", "code": "DX_APP_MISSING"}, 503)
        except NoDxAppExample:
            return self.send_json({"ok": False, "error": "No dx_app example for this model", "code": "MODEL_NOT_FOUND"}, 404)
        return self.send_bytes(html.encode("utf-8"), "text/html; charset=utf-8", filename=filename)

    def _handle_proxy(self, method, path, query, body=None, content_type=None):
        if body and content_type and "application/json" in content_type:
            try:
                json.loads(body)
            except json.JSONDecodeError as e:
                return self.send_json({"ok": False, "error": f"Invalid JSON: {e}", "code": "PARSE_ERROR"}, 400)

        if "/proxy/inference" in path:
            target = "/api/run"
        elif "/proxy/modelzoo/" in path:
            target = "/api/modelzoo/" + path.split("/proxy/modelzoo/")[1]
        else:
            return self.send_json({"ok": False, "error": "Unknown proxy target", "code": "INVALID_PARAM"}, 400)

        hdrs = {}
        if content_type:
            hdrs["Content-Type"] = content_type
        status, headers, resp_body = proxy_request(method, target, query, body, hdrs)
        self.send_response(status)
        for name, val in headers:
            if name.lower() not in ("transfer-encoding",):
                self.send_header(name, val)
        self.end_headers()
        self.wfile.write(resp_body)

    def _serve_demo_code(self, model_id):
        if not is_safe_model_id(model_id):
            return self.send_json({"ok": False, "error": "Invalid model ID", "code": "INVALID_PARAM"}, 400)
        cat = get_catalog()
        model = get_model(cat["models"], model_id)
        if not model:
            return self.send_json({"ok": False, "error": f"Model '{model_id}' not found", "code": "MODEL_NOT_FOUND"}, 404)
        demo = model.get("demo", {})
        try:
            cpp_code, py_code = _collect_demo_files(demo)
        except ValueError:
            return self.send_json({"ok": False, "error": "Path traversal detected", "code": "INVALID_PARAM"}, 400)
        return self.send_json({"ok": True, "cpp": cpp_code, "python": py_code,
                               "cli_command": demo.get("cli_command", "")})

    def _handle_artifact_request(self, path):
        """GET /api/catalog/<model_id>/artifacts/<artifact_id>"""
        from dx_modelzoo.metadata.artifacts import validate_artifact_id, resolve_artifact

        remainder = path[len("/api/catalog/"):]
        parts = remainder.split("/artifacts/", 1)
        if len(parts) != 2:
            return self.send_json({"ok": False, "error_code": "invalid_request"}, 400)
        model_id, artifact_id = parts

        # Graph deep-link: ".../artifacts/<id>/localpath" returns the resolved ABSOLUTE
        # local path as JSON (not the file bytes) so the UI can hand it to the dx-compiler
        # graph viewer (DX-TRON removed this release).
        want_local_path = False
        if artifact_id.endswith("/localpath"):
            artifact_id = artifact_id[: -len("/localpath")]
            want_local_path = True

        if not is_safe_model_id(model_id):
            return self.send_json({"ok": False, "error_code": "unknown_model"}, 404)

        cat = get_catalog()
        model = get_model(cat["models"], model_id)
        if not model:
            return self.send_json({"ok": False, "error_code": "unknown_model"}, 404)

        try:
            validate_artifact_id(artifact_id)
        except ValueError:
            return self.send_json({"ok": False, "error_code": "unknown_artifact"}, 404)

        result = resolve_artifact(model, artifact_id, source_profile="local",
                                  local_root=DX_APP_ROOT if DX_APP_ROOT.exists() else None)

        if result.get("error_code") in ("unsafe_artifact_path", "unsafe_artifact_url"):
            return self.send_json({"ok": False, "error_code": result["error_code"]}, 400)

        if want_local_path:
            if result.get("available") and result.get("type") == "local" and result.get("path"):
                return self.send_json({"ok": True, "path": result["path"]})
            return self.send_json({"ok": False, "error_code": "not_local_artifact"}, 404)

        if not result.get("available"):
            return self.send_json({"ok": False, "error_code": "artifact_unavailable"}, 404)

        if result["type"] == "local":
            artifact_path = Path(result["path"])
            try:
                data = artifact_path.read_bytes()
                content_type = "application/octet-stream"
                return self.send_bytes(data, content_type, filename=artifact_path.name)
            except (OSError, IOError):
                return self.send_json({"ok": False, "error_code": "artifact_unavailable"}, 404)

        if result["type"] == "remote" and result.get("url"):
            self.send_response(302)
            self.send_header("Location", result["url"])
            self.end_headers()
            return

        return self.send_json({"ok": False, "error_code": "artifact_unavailable"}, 404)

    def _handle_sync_status(self):
        """GET /api/metadata/sync/status"""
        from dx_modelzoo.metadata.schema import SCHEMA_VERSION
        with _sync_lock:
            state = dict(_sync_state)
        return self.send_json({
            "ok": True,
            "source_profile": state["source_profile"],
            "last_synced_at": state["last_synced_at"],
            "schema_version": SCHEMA_VERSION,
            "status": "synced" if state["last_synced_at"] else "not_run",
        })

    def _handle_sync_report(self):
        """GET /api/metadata/sync/report"""
        with _sync_lock:
            report = _sync_state["last_report"]
            source_profile = _sync_state["source_profile"]
        if report:
            return self.send_json({"ok": True, **report})
        return self.send_json({
            "ok": True,
            "status": "not_run",
            "source_profile": source_profile,
        })

    def _handle_sync_post(self):
        """POST /api/metadata/sync"""
        import os
        from datetime import datetime, timezone
        from dx_modelzoo.metadata.sync import resolve_source_profile, run_sync
        from dx_modelzoo.tools.sync_metadata import _resolve_metadata_config_path

        length = int(self.headers.get("Content-Length", 0))
        body = {}
        if length:
            try:
                body = json.loads(self.rfile.read(length))
            except (json.JSONDecodeError, ValueError):
                return self.send_json({"ok": False, "error_code": "invalid_request"}, 400)

        studio_root = Path(__file__).resolve().parent.parent
        config_path = _resolve_metadata_config_path(studio_root)
        source = body.get("source") or resolve_source_profile(
            env=os.environ,
            config_path=config_path,
        )
        valid_sources = {"local", "internal", "public"}
        if source not in valid_sources:
            return self.send_json({"ok": False, "error_code": "invalid_source_profile"}, 400)

        offline = body.get("offline", False)
        if source == "local" and offline:
            return self.send_json({
                "ok": False,
                "error_code": "local_offline_forbidden",
                "error": (
                    "local+offline sync strips public artifact URLs. "
                    "Use source=public on general network or source=local without offline."
                ),
            }, 400)
        global _sync_running
        with _sync_lock:
            if _sync_running:
                return self.send_json({"ok": False, "error_code": "sync_in_progress"}, 409)
            _sync_running = True

        try:
            suite_root = Path(__file__).resolve().parent.parent.parent
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            output_path = DATA_DIR / "generated_catalog.json"
            report_path = DATA_DIR / "sync_report.json"
            cache_path = DATA_DIR / "generated_catalog.cache.json"
            try:
                result = run_sync(
                    source_profile=source,
                    suite_root=suite_root,
                    output_path=output_path,
                    cache_path=cache_path,
                    report_path=report_path,
                    offline=offline,
                )
            except Exception as exc:
                return self.send_json({
                    "ok": False,
                    "error_code": "sync_error",
                    "error": str(exc),
                }, 500)
        finally:
            with _sync_lock:
                _sync_running = False

        catalog = result.get("catalog", {})
        report = result.get("report", {})
        now = datetime.now(timezone.utc).isoformat()

        # Refresh the in-memory catalog
        if catalog:
            apply_generated_catalog(catalog)

        with _sync_lock:
            _sync_state["last_report"] = report
            _sync_state["last_synced_at"] = now
            _sync_state["source_profile"] = source

        has_errors = bool(report.get("adapter_errors"))
        status = "partial" if has_errors else "ok"

        return self.send_json({
            "ok": True,
            "source_profile": source,
            "status": status,
            "models": len(catalog.get("models", [])),
            "synced_at": now,
        })


def create_server(port=DEFAULT_PORT):
    """Server factory for tests: returns an HTTPServer instance."""
    from http.server import ThreadingHTTPServer
    reload_catalog()
    srv = ThreadingHTTPServer(("127.0.0.1", port), ModelZooHandler)
    srv.daemon_threads = True
    return srv


def _maybe_auto_sync():
    """First-run / staleness background metadata sync (opt-out).

    On startup, if the generated catalog is missing or stale, refresh it from the online
    source in a daemon thread — so a fresh install shows real FPS and working download URLs
    without a manual sync. Skips cleanly when disabled, or on a local/air-gapped profile;
    never blocks boot and never crashes on failure (offline → keep the base catalog).

    Opt-out: DX_MODELZOO_AUTOSYNC=0. Staleness window: DX_MODELZOO_AUTOSYNC_MAX_AGE_DAYS (7)."""
    import os
    import time
    if os.environ.get("DX_MODELZOO_AUTOSYNC", "1").strip().lower() in ("0", "false", "no", "off"):
        return
    try:
        from dx_modelzoo.metadata.sync import resolve_source_profile, run_sync
        from dx_modelzoo.tools.sync_metadata import _resolve_metadata_config_path
    except Exception:
        return
    studio_root = Path(__file__).resolve().parent.parent          # dx-ai-studio
    suite_root = studio_root.parent                                # dx-all-suite
    try:
        source = resolve_source_profile(
            env=os.environ, config_path=_resolve_metadata_config_path(studio_root))
    except Exception:
        source = "public"
    # Only online profiles need a network sync. 'local' is offline/air-gap-friendly (and
    # local+offline sync is forbidden) — never auto-hit the network for it.
    if source not in ("public", "internal"):
        return
    try:
        max_age_days = float(os.environ.get("DX_MODELZOO_AUTOSYNC_MAX_AGE_DAYS", "7"))
    except ValueError:
        max_age_days = 7.0
    gen = DATA_DIR / "generated_catalog.json"
    try:
        if gen.is_file() and max_age_days > 0:
            if (time.time() - gen.stat().st_mtime) / 86400.0 < max_age_days:
                return  # recent enough — skip
    except OSError:
        pass

    def _worker():
        global _sync_running
        with _sync_lock:
            if _sync_running:
                return
            _sync_running = True
        try:
            result = run_sync(
                source_profile=source,
                suite_root=suite_root,
                output_path=DATA_DIR / "generated_catalog.json",
                cache_path=DATA_DIR / "generated_catalog.cache.json",
                report_path=DATA_DIR / "sync_report.json",
                offline=False,
            )
            catalog = result.get("catalog", {}) if isinstance(result, dict) else {}
            if catalog:
                apply_generated_catalog(catalog)
            else:
                reload_catalog()
            print(f"[dx_modelzoo] auto-sync ({source}) complete: "
                  f"{len(catalog.get('models', []))} models", flush=True)
        except Exception as exc:
            # Offline / air-gapped / unreachable → keep base catalog, no crash, no spam.
            print(f"[dx_modelzoo] auto-sync skipped ({source}): {exc}", flush=True)
        finally:
            with _sync_lock:
                _sync_running = False

    threading.Thread(target=_worker, name="modelzoo-autosync", daemon=True).start()


if __name__ == "__main__":
    reload_catalog()
    _maybe_auto_sync()
    DXServer(ModelZooHandler, SERVER_NAME, DEFAULT_PORT).start()

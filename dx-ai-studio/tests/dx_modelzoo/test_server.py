"""server.py 라우팅 테스트"""
import re
import sys, json, pytest, threading, time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

MODULE_DIR = Path(__file__).resolve().parent.parent.parent / "dx_modelzoo"

TEST_PORT = 18094


def _load_create_server():
    sys.modules.pop("server", None)
    sys.path.insert(0, str(MODULE_DIR))
    try:
        from server import create_server
    finally:
        sys.path.remove(str(MODULE_DIR))
    return create_server


@pytest.fixture(scope="module")
def server():
    """테스트용 서버 시작/정지."""
    create_server = _load_create_server()
    srv = create_server(TEST_PORT)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    for _ in range(20):
        try:
            urlopen(f"http://127.0.0.1:{TEST_PORT}/api/categories", timeout=1)
            break
        except Exception:
            time.sleep(0.2)
    yield srv
    srv.shutdown()
    srv.server_close()
    sys.modules.pop("server", None)


class TestServerRoutes:
    def test_root_returns_html(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/")
        assert resp.status == 200
        assert "text/html" in resp.headers.get("Content-Type", "")

    def test_index_html_returns_html(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/index.html")
        html = resp.read().decode()
        assert resp.status == 200
        assert "text/html" in resp.headers.get("Content-Type", "")
        assert "DX Model Zoo" in html

    def test_api_catalog(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog")
        data = json.loads(resp.read())
        assert "models" in data
        assert "categories" in data

    def test_api_catalog_exposes_variant_and_unique_counts(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog")
        data = json.loads(resp.read())
        assert "variant_count" in data
        assert "unique_model_count" in data
        assert data["variant_count"] == len(data["models"])
        assert data["unique_model_count"] <= data["variant_count"]

    def test_api_categories(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/categories")
        data = json.loads(resp.read())
        assert "categories" in data

    def test_api_catalog_filter(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog?category=classification")
        data = json.loads(resp.read())
        for m in data["models"]:
            assert m["category"] == "classification"

    def test_api_catalog_has_models(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog")
        data = json.loads(resp.read())
        from core.config import CONFIG_FILE
        if CONFIG_FILE.exists():
            assert len(data["models"]) > 0, "test_models.conf exists but no models loaded"

    def test_api_catalog_model_detail(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog")
        data = json.loads(resp.read())
        if data["models"]:
            mid = data["models"][0]["id"]
            resp2 = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/{mid}")
            detail = json.loads(resp2.read())
            assert detail.get("model", {}).get("id") == mid

    def test_api_catalog_detail_body_does_not_expose_internal_hosts(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog")
        data = json.loads(resp.read())
        if not data["models"]:
            pytest.skip("No models loaded")
        model_id = data["models"][0]["id"]
        body = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/{model_id}").read().decode()
        assert "modelzoo-api.devops.dpx.ai" not in body
        assert "modelzoo-publish-api.devops.dpx.ai" not in body

    def test_api_catalog_endpoints_have_distinct_shapes(self, server):
        catalog = json.loads(urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog").read())
        page = json.loads(urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/page?page=1&page_size=2").read())
        card = json.loads(urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/card?page=1&page_size=2").read())
        list_view = json.loads(urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/list?page=1&page_size=2").read())

        assert "models" in catalog and "model" not in catalog and "view" not in catalog
        assert "variant_count" in catalog and "unique_model_count" in catalog

        assert "models" in page and "view" not in page and "model" not in page
        assert "page" in page and "page_size" in page and "total" in page
        assert "variant_count" in page and "unique_model_count" in page

        assert card.get("view") == "card" and "models" in card and "model" not in card
        assert "page" in card and "page_size" in card and "total" in card
        assert "variant_count" in card and "unique_model_count" in card

        assert list_view.get("view") == "list" and "models" in list_view and "model" not in list_view
        assert "page" in list_view and "page_size" in list_view and "total" in list_view
        assert "variant_count" in list_view and "unique_model_count" in list_view

        if catalog["models"]:
            model_id = catalog["models"][0]["id"]
            detail = json.loads(urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/{model_id}").read())
            assert "model" in detail and "models" not in detail and "view" not in detail

    def test_api_catalog_model_detail_hides_internal_remote_urls(self, server, monkeypatch):
        handler_globals = server.RequestHandlerClass.route.__globals__
        original_model = {
            "id": "safe_model",
            "name": "Safe Model",
            "category": "classification",
            "artifacts": {
                "onnx": {
                    "remote_url": "https://modelzoo-api.devops.dpx.ai/files/safe_model.onnx",
                },
                "qpro_json": {
                    "remote_url": "https://sdk.deepx.ai/files/safe_model.json",
                },
            },
        }

        def fake_get_catalog():
            return {"models": [original_model], "categories": {}, "count": 1}

        def fake_get_model(models, model_id):
            return original_model if model_id == "safe_model" else None

        monkeypatch.setitem(handler_globals, "get_catalog", fake_get_catalog)
        monkeypatch.setitem(handler_globals, "get_model", fake_get_model)

        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/safe_model")
        body = json.loads(resp.read())
        model = body["model"]

        assert model["artifacts"]["onnx"].get("remote_url") is None
        assert model["artifacts"]["qpro_json"]["remote_url"] == "https://sdk.deepx.ai/files/safe_model.json"
        assert original_model["artifacts"]["onnx"]["remote_url"].startswith("https://modelzoo-api")

    def test_api_catalog_hides_internal_remote_urls(self, server, monkeypatch):
        handler_globals = server.RequestHandlerClass.route.__globals__
        original_model = {
            "id": "safe_model",
            "name": "Safe Model",
            "category": "classification",
            "artifacts": {
                "onnx": {
                    "remote_url": "https://modelzoo-api.devops.dpx.ai/files/safe_model.onnx",
                },
                "qpro_json": {
                    "remote_url": "https://sdk.deepx.ai/files/safe_model.json",
                },
            },
        }

        def fake_get_catalog():
            return {
                "models": [original_model],
                "categories": {"classification": {"name": "Classification"}},
                "count": 1,
            }

        def fake_filter_models(models, category=None, search=None):
            return list(models)

        monkeypatch.setitem(handler_globals, "get_catalog", fake_get_catalog)
        monkeypatch.setitem(handler_globals, "filter_models", fake_filter_models)

        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog")
        body = json.loads(resp.read())
        model = body["models"][0]

        assert model["artifacts"]["onnx"].get("remote_url") is None
        assert model["artifacts"]["qpro_json"]["remote_url"] == "https://sdk.deepx.ai/files/safe_model.json"
        assert original_model["artifacts"]["onnx"]["remote_url"].startswith("https://modelzoo-api")

    def test_api_catalog_list_hides_internal_remote_urls(self, server, monkeypatch):
        handler_globals = server.RequestHandlerClass.route.__globals__
        original_model = {
            "id": "safe_model",
            "name": "Safe Model",
            "category": "classification",
            "artifacts": {
                "onnx": {
                    "remote_url": "https://modelzoo-api.devops.dpx.ai/files/safe_model.onnx",
                },
                "qpro_json": {
                    "remote_url": "https://sdk.deepx.ai/files/safe_model.json",
                },
            },
        }

        def fake_get_catalog():
            return {
                "models": [original_model],
                "categories": {"classification": {"name": "Classification"}},
                "count": 1,
            }

        def fake_build_payload(models, categories, view, **query):
            return {
                "ok": True,
                "view": view,
                "models": list(models),
                "categories": categories,
                "count": 1,
                "total": 1,
                "page": 1,
                "page_size": 1,
                "pages": 1,
                "has_next": False,
                "has_prev": False,
            }

        monkeypatch.setitem(handler_globals, "get_catalog", fake_get_catalog)
        monkeypatch.setitem(handler_globals, "build_catalog_view_payload", fake_build_payload)

        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/list?page=1&page_size=1")
        body = json.loads(resp.read())
        model = body["models"][0]

        assert body["view"] == "list"
        assert model["artifacts"]["onnx"].get("remote_url") is None
        assert model["artifacts"]["qpro_json"]["remote_url"] == "https://sdk.deepx.ai/files/safe_model.json"
        assert original_model["artifacts"]["onnx"]["remote_url"].startswith("https://modelzoo-api")

    def test_api_catalog_card_hides_internal_remote_urls(self, server, monkeypatch):
        handler_globals = server.RequestHandlerClass.route.__globals__
        original_model = {
            "id": "safe_model",
            "name": "Safe Model",
            "category": "classification",
            "artifacts": {
                "onnx": {
                    "remote_url": "https://modelzoo-api.devops.dpx.ai/files/safe_model.onnx",
                },
                "qpro_json": {
                    "remote_url": "https://sdk.deepx.ai/files/safe_model.json",
                },
            },
        }

        def fake_get_catalog():
            return {
                "models": [original_model],
                "categories": {"classification": {"name": "Classification"}},
                "count": 1,
            }

        def fake_build_payload(models, categories, view, **query):
            return {
                "ok": True,
                "view": view,
                "models": list(models),
                "categories": categories,
                "count": 1,
                "total": 1,
                "page": 1,
                "page_size": 1,
                "pages": 1,
                "has_next": False,
                "has_prev": False,
            }

        monkeypatch.setitem(handler_globals, "get_catalog", fake_get_catalog)
        monkeypatch.setitem(handler_globals, "build_catalog_view_payload", fake_build_payload)

        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/card?page=1&page_size=1")
        body = json.loads(resp.read())
        model = body["models"][0]

        assert body["view"] == "card"
        assert model["artifacts"]["onnx"].get("remote_url") is None
        assert model["artifacts"]["qpro_json"]["remote_url"] == "https://sdk.deepx.ai/files/safe_model.json"
        assert original_model["artifacts"]["onnx"]["remote_url"].startswith("https://modelzoo-api")

    def test_api_catalog_page_hides_internal_remote_urls(self, server, monkeypatch):
        handler_globals = server.RequestHandlerClass.route.__globals__
        original_model = {
            "id": "safe_model",
            "name": "Safe Model",
            "category": "classification",
            "artifacts": {
                "onnx": {
                    "remote_url": "https://modelzoo-api.devops.dpx.ai/files/safe_model.onnx",
                },
                "qpro_json": {
                    "remote_url": "https://sdk.deepx.ai/files/safe_model.json",
                },
            },
        }

        def fake_get_catalog():
            return {
                "models": [original_model],
                "categories": {"classification": {"name": "Classification"}},
                "count": 1,
            }

        def fake_query_catalog(models, **kwargs):
            return {
                "models": list(models),
                "total": 1,
                "page": 1,
                "page_size": 1,
                "pages": 1,
                "has_next": False,
                "has_prev": False,
            }

        monkeypatch.setitem(handler_globals, "get_catalog", fake_get_catalog)
        monkeypatch.setitem(handler_globals, "query_catalog", fake_query_catalog)

        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/page?page=1&page_size=1")
        body = json.loads(resp.read())
        model = body["models"][0]

        assert model["artifacts"]["onnx"].get("remote_url") is None
        assert model["artifacts"]["qpro_json"]["remote_url"] == "https://sdk.deepx.ai/files/safe_model.json"
        assert original_model["artifacts"]["onnx"]["remote_url"].startswith("https://modelzoo-api")

    def test_api_catalog_model_not_found(self, server):
        try:
            urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/nonexistent_model_xyz")
            assert False, "Should have raised"
        except URLError as e:
            assert e.code == 404

    def test_static_css(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/static/css/style.css")
        css = resp.read().decode()
        assert resp.status == 200
        assert ".mz-topbar" in css
        assert ".mz-card" in css

    def test_path_traversal_blocked(self, server):
        try:
            urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/..%2F..%2Fetc%2Fpasswd")
            assert False, "Should have raised"
        except URLError as e:
            assert e.code in (400, 404)

    def test_tutorial_tags_in_html(self, server):
        """index.html에 tutorial 관련 3개 태그가 존재하는지 확인."""
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/")
        html = resp.read().decode()
        assert 'tutorial-engine.js' in html, "tutorial-engine.js 태그 누락"
        assert 'tutorial.js' in html, "tutorial.js 태그 누락"
        assert 'tutorial.css' in html, "tutorial.css 태그 누락"

    def test_shared_font_served(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/static/shared/fonts/inter-v20-latin-regular.woff2")
        data = resp.read()
        content_type = resp.headers.get("Content-Type", "").lower()
        assert resp.status == 200
        assert data
        assert "font" in content_type or content_type == "application/octet-stream"

    def test_shared_css_foundation(self, server):
        for path in (
            "/static/shared/dx-fonts.css",
            "/static/shared/dx-tokens.css",
            "/static/shared/dx-base.css",
            "/static/shared/dx-utilities.css",
        ):
            resp = urlopen(f"http://127.0.0.1:{TEST_PORT}{path}")
            body = resp.read().decode()
            assert resp.status == 200
            assert body.strip()

    def test_api_catalog_page_route_not_treated_as_model_detail(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/page?page=1&page_size=2")
        data = json.loads(resp.read())
        assert resp.status == 200
        assert data["ok"] is True
        assert "page" in data
        assert "page_size" in data
        assert "total" in data
        assert "has_next" in data
        assert "variant_count" in data
        assert "unique_model_count" in data
        assert data["variant_count"] == data["total"]
        assert data["unique_model_count"] <= data["variant_count"]
        assert isinstance(data["models"], list)

    def test_api_catalog_card_route_not_treated_as_model_detail(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/card?page=1&page_size=5")
        data = json.loads(resp.read())
        assert resp.status == 200
        assert data["ok"] is True
        assert data["view"] == "card"
        assert isinstance(data["models"], list)
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "pages" in data
        assert "has_next" in data
        assert "has_prev" in data
        assert "variant_count" in data
        assert "unique_model_count" in data
        assert data["variant_count"] == data["total"]
        assert data["unique_model_count"] <= data["variant_count"]

    def test_api_catalog_list_route_not_treated_as_model_detail(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/list?page=1&page_size=5")
        data = json.loads(resp.read())
        assert resp.status == 200
        assert data["ok"] is True
        assert data["view"] == "list"
        assert isinstance(data["models"], list)
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "pages" in data
        assert "has_next" in data
        assert "has_prev" in data
        assert "variant_count" in data
        assert "unique_model_count" in data
        assert data["variant_count"] == data["total"]
        assert data["unique_model_count"] <= data["variant_count"]

    def test_api_catalog_page_filters_sorts_and_limits(self, server):
        resp = urlopen(
            f"http://127.0.0.1:{TEST_PORT}/api/catalog/page?category=classification&sort=fps&dir=desc&page=1&page_size=3"
        )
        data = json.loads(resp.read())
        assert data["ok"] is True
        assert data["page"] == 1
        assert data["page_size"] == 3
        assert len(data["models"]) <= 3
        for model in data["models"]:
            assert model["category"] == "classification"

    @pytest.mark.parametrize("qs_params", [
        "page=0",
        "page=-1",
        "page_size=99999",
        "page=abc",
        "page=0&page_size=-5",
        "page=1&page_size=0",
    ])
    def test_api_catalog_page_bad_params_clamp_safely(self, server, qs_params):
        """비정상/엣지 쿼리 파라미터가 500을 유발하지 않고 안전하게 클램핑되는지 확인."""
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog/page?{qs_params}")
        data = json.loads(resp.read())
        assert resp.status == 200
        assert data["ok"] is True
        assert data["page"] >= 1
        assert 1 <= data["page_size"] <= 200
        assert isinstance(data["models"], list)

    def test_explorer_shell_markup_present(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/")
        html = resp.read().decode()
        for cls in ("mz-explorer-shell", "mz-filter-rail", "mz-explorer-main"):
            assert re.search(
                rf'class\s*=\s*"[^"]*\b{cls}\b[^"]*"', html
            ), f"expected class token '{cls}' in HTML"
        assert 'id="catalogView"' in html
        assert 'id="detailView"' in html
        assert 'id="modelCount"' in html
        assert 'id="sortSelect"' in html
        assert 'aria-label="Sort by"' in html
        assert 'data-i18n-title="Sort by"' in html

    def test_data_model_catalog_json_served(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/data/model_catalog.json")
        data = json.loads(resp.read())
        assert resp.status == 200
        assert isinstance(data, dict)
        assert "categories" in data


    def test_api_catalog_exposes_enriched_fields_when_generated_catalog_exists(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/catalog")
        data = json.loads(resp.read())
        if not data["models"]:
            pytest.skip("No models loaded (test_models.conf absent)")
        model = data["models"][0]
        assert "specification" in model
        assert "artifacts" in model or "model_file" in model
        assert "processor" in model


    def test_metadata_sync_status_endpoint_returns_source_and_last_sync(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/metadata/sync/status")
        data = json.loads(resp.read())
        assert "source_profile" in data
        assert "last_synced_at" in data
        assert "schema_version" in data

    def test_metadata_sync_report_endpoint_returns_last_report(self, server):
        resp = urlopen(f"http://127.0.0.1:{TEST_PORT}/api/metadata/sync/report")
        data = json.loads(resp.read())
        assert "source_profile" in data or data["status"] in {"not_run", "unavailable"}

    def test_metadata_sync_post_runs_validated_local_sync(self, server, monkeypatch, tmp_path):
        handler_globals = server.RequestHandlerClass._handle_sync_post.__globals__
        data_dir = tmp_path / "modelzoo-data"
        data_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setitem(handler_globals, "DATA_DIR", data_dir)
        monkeypatch.setitem(handler_globals, "_sync_running", False)

        request = Request(
            f"http://127.0.0.1:{TEST_PORT}/api/metadata/sync",
            data=json.dumps({"source": "local"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urlopen(request)
        data = json.loads(resp.read())
        assert data["source_profile"] == "local"
        assert data["status"] in {"ok", "partial"}
        assert "models" in data
        assert (data_dir / "generated_catalog.json").exists()
        assert (data_dir / "generated_catalog.cache.json").exists()
        assert (data_dir / "sync_report.json").exists()

    def test_metadata_sync_post_rejects_unknown_source(self, server):
        request = Request(
            f"http://127.0.0.1:{TEST_PORT}/api/metadata/sync",
            data=json.dumps({"source": "evil"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urlopen(request)
        except HTTPError as e:
            body = json.loads(e.read())
            assert e.code == 400
            assert body["error_code"] == "invalid_source_profile"
        else:
            raise AssertionError("expected HTTPError")

    def test_metadata_sync_post_rejects_concurrent_requests(self, server, monkeypatch, tmp_path):
        handler_globals = server.RequestHandlerClass._handle_sync_post.__globals__
        data_dir = tmp_path / "modelzoo-data"
        data_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setitem(handler_globals, "DATA_DIR", data_dir)
        monkeypatch.setitem(handler_globals, "_sync_running", False)

        from dx_modelzoo.metadata import sync as sync_mod
        entered = threading.Event()
        release = threading.Event()
        first_result = {}

        def slow_run_sync(**kwargs):
            entered.set()
            release.wait(timeout=3)
            return {
                "catalog": {"models": []},
                "report": {"model_count": 0, "adapter_errors": []},
            }

        monkeypatch.setattr(sync_mod, "run_sync", slow_run_sync)

        def _first_request():
            req = Request(
                f"http://127.0.0.1:{TEST_PORT}/api/metadata/sync",
                data=json.dumps({"source": "local"}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                resp = urlopen(req, timeout=5)
                first_result["status"] = resp.status
                first_result["body"] = json.loads(resp.read())
            except Exception as exc:
                first_result["error"] = exc

        t = threading.Thread(target=_first_request, daemon=True)
        t.start()
        assert entered.wait(timeout=2), "first sync request did not reach run_sync"

        second_req = Request(
            f"http://127.0.0.1:{TEST_PORT}/api/metadata/sync",
            data=json.dumps({"source": "local"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(HTTPError) as exc_info:
            urlopen(second_req, timeout=5)
        assert exc_info.value.code == 409
        err_body = json.loads(exc_info.value.read())
        assert err_body["error_code"] == "sync_in_progress"

        release.set()
        t.join(timeout=5)
        assert "error" not in first_result
        assert first_result.get("status") == 200




class TestDemoPathGuard:
    def test_is_safe_demo_dir_rejects_sibling_prefix(self, tmp_path):
        """root=/tmp/dx-app, candidate=/tmp/dx-app-evil 은 거부되어야 한다."""
        sys.path.insert(0, str(MODULE_DIR))
        try:
            from server import _is_safe_demo_dir
        finally:
            sys.path.remove(str(MODULE_DIR))
        root = tmp_path / "dx-app"
        root.mkdir()
        evil = tmp_path / "dx-app-evil"
        evil.mkdir()
        assert _is_safe_demo_dir(root / "subdir", root) is True
        assert _is_safe_demo_dir(evil, root) is False

    def test_is_safe_demo_dir_rejects_symlink_escape(self, tmp_path):
        sys.path.insert(0, str(MODULE_DIR))
        try:
            from server import _is_safe_demo_dir
        finally:
            sys.path.remove(str(MODULE_DIR))
        root = tmp_path / "dx-app"
        root.mkdir()
        link = root / "escape"
        link.symlink_to(tmp_path)
        assert _is_safe_demo_dir(link, root) is False

    def test_empty_demo_paths_do_not_serve_root_files(self, tmp_path):
        """demo path가 빈 문자열일 때 DX_APP_ROOT 파일이 서빙되지 않아야 한다."""
        (tmp_path / "leak.cpp").write_text("// leaked cpp")
        (tmp_path / "leak.py").write_text("# leaked py")

        sys.path.insert(0, str(MODULE_DIR))
        try:
            import server as srv_mod
            old_root = srv_mod.DX_APP_ROOT
            srv_mod.DX_APP_ROOT = tmp_path
            try:
                demo = {"cpp_example": "", "python_example": ""}
                if hasattr(srv_mod, '_collect_demo_files'):
                    cpp, py = srv_mod._collect_demo_files(demo)
                else:
                    # 기존 인라인 로직 재현 (버그 포함)
                    cpp = py = ""
                    cpp_dir = srv_mod.DX_APP_ROOT / demo.get("cpp_example", "")
                    if cpp_dir.is_dir():
                        if srv_mod._is_safe_demo_dir(cpp_dir, srv_mod.DX_APP_ROOT):
                            for f in sorted(cpp_dir.glob("*.cpp")):
                                cpp += f"// === {f.name} ===\n{f.read_text()}\n\n"
                    py_dir = srv_mod.DX_APP_ROOT / demo.get("python_example", "")
                    if py_dir.is_dir():
                        if srv_mod._is_safe_demo_dir(py_dir, srv_mod.DX_APP_ROOT):
                            for f in sorted(py_dir.glob("*.py")):
                                py += f"# === {f.name} ===\n{f.read_text()}\n\n"
                assert cpp == "", f"cpp should be empty but got: {cpp!r}"
                assert py == "", f"py should be empty but got: {py!r}"
            finally:
                srv_mod.DX_APP_ROOT = old_root
        finally:
            sys.path.remove(str(MODULE_DIR))

    def test_collect_demo_files_reads_utf8_korean_text(self, tmp_path):
        cpp_dir = tmp_path / "src" / "cpp_example" / "classification" / "utf_model"
        cpp_dir.mkdir(parents=True)
        (cpp_dir / "main.cpp").write_text('// 한글 주석\nint main(){return 0;}\n', encoding="utf-8")

        sys.path.insert(0, str(MODULE_DIR))
        try:
            import server as srv_mod
            old_root = srv_mod.DX_APP_ROOT
            srv_mod.DX_APP_ROOT = tmp_path
            try:
                cpp, py = srv_mod._collect_demo_files({
                    "cpp_example": "src/cpp_example/classification/utf_model",
                    "python_example": "",
                })
                assert "한글 주석" in cpp
                assert py == ""
            finally:
                srv_mod.DX_APP_ROOT = old_root
        finally:
            sys.path.remove(str(MODULE_DIR))




class TestSyncUpdatesCatalog:
    def test_sync_post_updates_live_catalog(self):
        """POST sync 후 in-memory 카탈로그가 갱신되어야 한다."""
        sys.path.insert(0, str(MODULE_DIR))
        try:
            # 깨끗한 모듈 import
            for mod_name in list(sys.modules):
                if mod_name.startswith("core.catalog") or mod_name == "core.catalog":
                    del sys.modules[mod_name]
            from core import catalog as catalog_mod
            from core.catalog import apply_generated_catalog

            # 초기 카탈로그 설정: 모델 1개
            initial_models = [{"id": "BaseModel", "name": "BaseModel", "category": "cls",
                               "processor": {"status": "metadata_pending"}, "specification": {}}]
            catalog_mod._catalog_cache = {
                "models": initial_models,
                "categories": {"cls": {"name": "Classification"}},
                "count": 1,
            }

            # apply_generated_catalog 로 enriched 데이터 적용
            gen_catalog = {
                "schema_version": "2.0",
                "models": [{
                    "id": "BaseModel",
                    "performance": {"fps": 100},
                    "artifacts": {"qlite_dxnn": {"local_path": "models/Base.dxnn"}},
                }],
            }
            apply_generated_catalog(gen_catalog)

            cat = catalog_mod.get_catalog()
            model = next(m for m in cat["models"] if m["id"] == "BaseModel")
            assert model.get("performance") == {"fps": 100}
            assert "qlite_dxnn" in model.get("artifacts", {})
        finally:
            sys.path.remove(str(MODULE_DIR))
            catalog_mod._catalog_cache = None

    def test_apply_generated_catalog_attaches_metadata_source(self):
        """generated catalog의 source_profile/generated_at은 각 모델에 전달되어야 한다."""
        sys.path.insert(0, str(MODULE_DIR))
        try:
            for mod_name in list(sys.modules):
                if mod_name.startswith("core.catalog") or mod_name == "core.catalog":
                    del sys.modules[mod_name]
            from core import catalog as catalog_mod
            from core.catalog import apply_generated_catalog

            catalog_mod._catalog_cache = {
                "models": [{"id": "BaseModel", "name": "BaseModel", "category": "cls"}],
                "categories": {"cls": {"name": "Classification"}},
                "count": 1,
            }

            gen_catalog = {
                "schema_version": "2.0",
                "source_profile": "internal",
                "generated_at": "2026-05-14T00:00:00+00:00",
                "models": [{"id": "BaseModel", "performance": {"fps": 100}}],
            }
            apply_generated_catalog(gen_catalog)

            model = catalog_mod.get_catalog()["models"][0]
            assert model["metadata_source"] == {
                "source_profile": "internal",
                "generated_at": "2026-05-14T00:00:00+00:00",
            }
        finally:
            sys.path.remove(str(MODULE_DIR))
            catalog_mod._catalog_cache = None

    def test_apply_generated_catalog_overwrites_empty_legacy_spec_values(self):
        """generated catalog 값은 legacy catalog의 빈 문자열 specification보다 우선해야 한다."""
        sys.path.insert(0, str(MODULE_DIR))
        try:
            for mod_name in list(sys.modules):
                if mod_name.startswith("core.catalog") or mod_name == "core.catalog":
                    del sys.modules[mod_name]
            from core import catalog as catalog_mod
            from core.catalog import apply_generated_catalog

            catalog_mod._catalog_cache = {
                "models": [{
                    "id": "3ddfa_v2_mobilnet0_5_120x120",
                    "name": "3Ddfa V2 Mobilnet0 5 120X120",
                    "category": "face_alignment",
                    "specification": {
                        "dataset": "",
                        "input_resolution": "",
                        "ops": "",
                        "params": "",
                        "metric": {},
                        "quantization": ["qlite"],
                    },
                }],
                "categories": {"face_alignment": {"name": "Face Alignment"}},
                "count": 1,
            }

            gen_catalog = {
                "schema_version": "2.0",
                "source_profile": "internal",
                "generated_at": "2026-05-14T00:00:00+00:00",
                "models": [{
                    "id": "3ddfa_v2_mobilnet0_5_120x120",
                    "specification": {
                        "dataset": "AFLW20003D",
                        "input_resolution": "120x120x3",
                        "operations": "0.07",
                        "parameters": "0.86",
                        "metric": {"name": "NME"},
                    },
                    "evaluation": {
                        "raw": {"accuracy": "3.499"},
                        "qlite": {"accuracy": "3.5906"},
                    },
                    "performance": {"fps": 15798.0, "fps_per_watt": 24849.0},
                }],
            }

            apply_generated_catalog(gen_catalog)

            model = catalog_mod.get_catalog()["models"][0]
            assert model["specification"]["dataset"] == "AFLW20003D"
            assert model["specification"]["input_resolution"] == "120x120x3"
            assert model["specification"]["operations"] == "0.07"
            assert model["specification"]["parameters"] == "0.86"
            assert model["specification"]["metric"] == {"name": "NME"}
            assert model["specification"]["quantization"] == ["qlite"]
            assert model["evaluation"]["qlite"]["accuracy"] == "3.5906"
            assert model["performance"]["fps"] == 15798.0
        finally:
            sys.path.remove(str(MODULE_DIR))
            catalog_mod._catalog_cache = None

    def test_metadata_sync_shared_state_updates_are_locked(self):
        """ThreadingHTTPServer에서 sync 상태와 catalog 갱신은 lock으로 보호되어야 한다."""
        server_src = (MODULE_DIR / "server.py").read_text(encoding="utf-8")
        catalog_src = (MODULE_DIR / "core" / "catalog.py").read_text(encoding="utf-8")
        assert "_sync_lock = threading.RLock()" in server_src
        assert "with _sync_lock:" in server_src
        assert "_catalog_lock = threading.RLock()" in catalog_src
        assert "with _catalog_lock:" in catalog_src

    def test_sync_generated_artifacts_are_gitignored(self):
        # generated_catalog.json is now a SHIPPED release artifact (produced by
        # dx_modelzoo/scripts/sync_release_catalog.sh in the general-net stage), so
        # it must NOT be gitignored — the offline/air-gapped build exposes official
        # accuracy/fps/onnx URLs only via this committed snapshot. The build-local
        # artifacts (per-run cache + sync report) stay ignored.
        gitignore = (MODULE_DIR.parent / ".gitignore").read_text(encoding="utf-8")
        # Only real ignore rules (strip comments/blank lines) count.
        rules = {
            ln.strip()
            for ln in gitignore.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")
        }
        assert "dx_modelzoo/data/generated_catalog.json" not in rules
        assert "dx_modelzoo/data/generated_catalog.cache.json" in rules
        assert "dx_modelzoo/data/sync_report.json" in rules

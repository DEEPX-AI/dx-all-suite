"""DX Benchmark server unit tests."""
import json
import threading
import time
import urllib.request
import urllib.error
import pytest
from pathlib import Path


def test_dx_benchmark_create_server_returns_http_server():
    """create_server(port) returns a usable HTTP server with expected attributes."""
    from dx_benchmark.server import create_server
    srv = create_server(port=28097)
    try:
        assert hasattr(srv, "serve_forever")
        assert hasattr(srv, "shutdown")
        assert hasattr(srv, "server_close")
        host, port = srv.server_address
        assert port == 28097
    finally:
        srv.server_close()


def _start_server(port=18097):
    """Start DX Benchmark server in background thread."""
    from dx_benchmark.server import DXBenchmarkHandler
    from http.server import ThreadingHTTPServer
    srv = ThreadingHTTPServer(("127.0.0.1", port), DXBenchmarkHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    time.sleep(1)
    return srv


@pytest.fixture(scope="module")
def server():
    srv = _start_server(18097)
    yield srv
    srv.shutdown()
    srv.server_close()


def _get(path, port=18097):
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


def _post(path, data, port=18097):
    url = f"http://127.0.0.1:{port}{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


def _post_raw(path, body: bytes, port=18097):
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=5)


def _get_bytes(path, port=18097):
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read(), resp.status, resp.headers.get("Content-Type", "")


def _get_raw(path, port=18097):
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read().decode(), resp.status


def _read_benchmark_file(relative: str) -> str:
    root = Path(__file__).resolve().parent.parent.parent / "dx_benchmark"
    return (root / relative).read_text(encoding="utf-8")



def test_health(server):
    data = _get("/api/health")
    assert data["status"] == "ok"


def test_hb(server):
    data = _get("/api/hb")
    assert data["ok"] is True



def test_dataset(server):
    data = _get("/api/dataset")
    assert "environments" in data



def test_results_list(server):
    data = _get("/api/results")
    assert isinstance(data, list)



def test_config_get(server):
    data = _get("/api/config")
    assert "model_dir" in data
    assert "results_dir" in data


def test_config_reports_canonical_results_dir_only(server):
    """GET /api/config results_dir must be canonical (outputs/benchmark), never legacy/core path."""
    data = _get("/api/config")
    results_dir = data["results_dir"]
    assert "core" not in results_dir, f"results_dir should not contain 'core': {results_dir}"
    assert results_dir.endswith("outputs/benchmark") or results_dir.endswith("outputs\\benchmark")


def test_config_post_returns_501_not_implemented(server):
    """POST /api/config must return 501 — settings are deployment-fixed."""
    url = f"http://127.0.0.1:18097/api/config"
    body = json.dumps({"cooldown_temp": 60}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(req, timeout=5)
    assert exc_info.value.code == 501


def test_config_post_body_says_deployment_fixed(server):
    """POST /api/config 501 body must contain deployment-fixed explanation."""
    url = f"http://127.0.0.1:18097/api/config"
    body = json.dumps({"cooldown_temp": 60}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
        pytest.fail("Expected HTTPError 501")
    except urllib.error.HTTPError as e:
        resp = json.loads(e.read())
        assert resp["ok"] is False
        assert "deployment" in resp.get("error", "").lower()


def test_config_post_malformed_json_returns_501_not_500(server):
    """POST /api/config with malformed JSON must return 501, not 500."""
    url = f"http://127.0.0.1:18097/api/config"
    body = b'{not valid json!!!'
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(req, timeout=5)
    err = exc_info.value
    assert err.code == 501, f"Expected 501 but got {err.code}"
    resp = json.loads(err.read())
    assert resp["ok"] is False
    assert "deployment" in resp.get("error", "").lower()


def test_config_get_includes_runtime_parameters(server):
    """GET /api/config must include thermal/benchmark runtime parameters."""
    data = _get("/api/config")
    for key in ["cooldown_temp", "wait_interval", "iterations",
                "warmup", "fps_threshold"]:
        assert key in data, f"GET /api/config missing key: {key}"
    # Values must be numeric
    for key in ["cooldown_temp", "wait_interval", "iterations",
                "warmup", "fps_threshold"]:
        assert isinstance(data[key], (int, float)), f"{key} must be numeric"




def test_index_serves_html(server):
    body, status = _get_raw("/")
    assert status == 200
    assert "<!DOCTYPE html>" in body or "<html" in body



def test_unknown_path_404(server):
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        _get("/api/nonexistent")
    assert exc_info.value.code == 404



def test_local_css_served(server):
    body, status = _get_raw("/static/css/style.css")
    assert status == 200
    assert ".top-bar" in body


def test_shared_foundation_css_served(server):
    body, status = _get_raw("/static/shared/dx-fonts.css")
    assert status == 200
    assert "/static/shared/fonts/inter-v20-latin-regular.woff2" in body


def test_shared_font_served(server):
    data, status, content_type = _get_bytes("/static/shared/fonts/inter-v20-latin-regular.woff2")
    assert status == 200
    assert data[:4] == b"wOF2"
    assert len(data) > 100
    assert "font" in content_type or content_type == "application/octet-stream"



def test_benchmark_top_level_tabs_are_preserved(server):
    body, status = _get_raw("/")
    assert status == 200
    for token in [
        'data-tab="dashboard"',
        'data-tab="results"',
        'data-tab="settings"',
    ]:
        assert token in body
    assert 'data-tab="run"' not in body



def test_benchmark_dashboard_workspace_contracts():
    dashboard_js = _read_benchmark_file("static/js/dashboard.js")
    style_css = _read_benchmark_file("static/css/style.css")
    for token in [
        "benchmark-workspace",
        "dashboard-workspace",
        "benchmark-segment-tabs",
        "dashboard-primary",
        "dashboard-detail-grid",
    ]:
        assert token in dashboard_js
        assert f".{token}" in style_css
    for token in [
        "E2E FPS Overview",
        "Full Metrics",
        "Detailed Data",
        "Version Trend",
    ]:
        assert token in dashboard_js


def test_benchmark_results_workspace_contracts():
    results_js = _read_benchmark_file("static/js/results.js")
    i18n_js = _read_benchmark_file("static/js/i18n.js")
    style_css = _read_benchmark_file("static/css/style.css")
    for token in [
        "results-workspace",
        "results-rail",
        "results-detail",
        "run-list",
        "run-detail",
    ]:
        assert token in results_js
        assert f".{token}" in style_css
    for token in [
        "View Report",
        "Raw Data",
        "environment",
        "model_results",
        "pipeline_results",
        "multi_stream_results",
    ]:
        assert token in results_js
    assert "'Raw Data':" in i18n_js
    assert "encodeURIComponent(hwId)" in results_js
    assert "encodeURIComponent(runId)" in results_js
    assert "_escHtml(JSON.stringify(data, null, 2))" in results_js



@pytest.fixture()
def legacy_results_env(tmp_path):
    """Set up canonical + legacy result dirs with distinct runs, patch server module."""
    import dx_benchmark.server as server
    canonical = tmp_path / "results"
    legacy = tmp_path / "core" / "results"

    # canonical run
    c_run = canonical / "hw-A" / "run-canon-001"
    c_run.mkdir(parents=True)
    (c_run / "environment.json").write_text(json.dumps({"board": "hw-A"}))
    (c_run / "model_results.json").write_text("[]")
    (c_run / "REPORT.md").write_text("# Canonical Report")

    # legacy-only run
    l_run = legacy / "hw-B" / "run-legacy-001"
    l_run.mkdir(parents=True)
    (l_run / "environment.json").write_text(json.dumps({"board": "hw-B"}))
    (l_run / "model_results.json").write_text("[]")
    (l_run / "REPORT.md").write_text("# Legacy Report")

    orig_results = server.RESULTS_DIR
    orig_legacy = server.LEGACY_RESULTS_DIR
    server.RESULTS_DIR = canonical
    server.LEGACY_RESULTS_DIR = legacy
    yield {"canonical": canonical, "legacy": legacy}
    server.RESULTS_DIR = orig_results
    server.LEGACY_RESULTS_DIR = orig_legacy


def test_results_list_includes_legacy_runs(legacy_results_env, server):
    """Results listing must include runs from legacy dir."""
    data = _get("/api/results")
    hw_ids = {r["hw_id"] for r in data}
    assert "hw-A" in hw_ids, "canonical hw missing"
    assert "hw-B" in hw_ids, "legacy hw missing from listing"


def test_result_detail_reads_from_legacy(legacy_results_env, server):
    """Result detail must be readable for a run only in legacy dir."""
    data = _get("/api/results/hw-B/run-legacy-001")
    assert "environment" in data or "model_results" in data

    report = _get("/api/results/hw-B/run-legacy-001/report")
    assert "Legacy Report" in report["markdown"]


def test_results_list_canonical_first_dedup(tmp_path, server):
    """When same hw/run exists in both, canonical wins (appears once)."""
    import dx_benchmark.server as server_mod
    canonical = tmp_path / "results"
    legacy = tmp_path / "core" / "results"

    for base in [canonical, legacy]:
        run_dir = base / "hw-X" / "run-dup-001"
        run_dir.mkdir(parents=True)
        (run_dir / "environment.json").write_text("{}")
        origin = "canonical" if base == canonical else "legacy"
        (run_dir / "REPORT.md").write_text(f"# {origin}")

    orig_r, orig_l = server_mod.RESULTS_DIR, server_mod.LEGACY_RESULTS_DIR
    server_mod.RESULTS_DIR = canonical
    server_mod.LEGACY_RESULTS_DIR = legacy
    try:
        data = _get("/api/results")
        hw_x_entries = [r for r in data if r["hw_id"] == "hw-X"]
        assert len(hw_x_entries) == 1
        runs = hw_x_entries[0]["runs"]
        dup_runs = [r for r in runs if r["run_id"] == "run-dup-001"]
        assert len(dup_runs) == 1, "duplicate hw/run should appear only once"

        # Detail should return canonical version
        report = _get("/api/results/hw-X/run-dup-001/report")
        assert "canonical" in report["markdown"]
    finally:
        server_mod.RESULTS_DIR = orig_r
        server_mod.LEGACY_RESULTS_DIR = orig_l


def test_results_list_sorted_newest_first(tmp_path, server):
    """Combined canonical+legacy runs should be sorted newest-first (descending)."""
    import dx_benchmark.server as server_mod
    canonical = tmp_path / "results"
    legacy = tmp_path / "core" / "results"

    # Canonical has an older run
    c_run = canonical / "hw-Z" / "2024-01-01_old"
    c_run.mkdir(parents=True)
    (c_run / "environment.json").write_text("{}")

    # Legacy has a newer run
    l_run = legacy / "hw-Z" / "2025-06-01_new"
    l_run.mkdir(parents=True)
    (l_run / "environment.json").write_text("{}")

    orig_r, orig_l = server_mod.RESULTS_DIR, server_mod.LEGACY_RESULTS_DIR
    server_mod.RESULTS_DIR = canonical
    server_mod.LEGACY_RESULTS_DIR = legacy
    try:
        data = _get("/api/results")
        hw_z = [r for r in data if r["hw_id"] == "hw-Z"]
        assert len(hw_z) == 1
        run_ids = [r["run_id"] for r in hw_z[0]["runs"]]
        assert run_ids == sorted(run_ids, reverse=True), \
            f"runs should be newest-first: {run_ids}"
    finally:
        server_mod.RESULTS_DIR = orig_r
        server_mod.LEGACY_RESULTS_DIR = orig_l


@pytest.mark.parametrize("bad_cl", ["abc", "", "-5", "3.14", "None"])
def test_config_save_malformed_content_length(bad_cl, server):
    """Malformed Content-Length must not crash _handle_config_save (returns 501)."""
    import http.client
    conn = http.client.HTTPConnection("127.0.0.1", 18097)
    conn.putrequest("POST", "/api/config")
    conn.putheader("Content-Type", "application/json")
    conn.putheader("Content-Length", bad_cl)
    conn.endheaders(b"")
    resp = conn.getresponse()
    assert resp.status == 501, f"Expected 501 for Content-Length={bad_cl!r}, got {resp.status}"
    conn.close()

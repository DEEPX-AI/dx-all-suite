import importlib.util
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "perf_audit.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("perf_audit_under_test", TOOL)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_static_report_covers_all_perf_domains():
    perf_audit = load_tool()
    report = perf_audit.run_static(ROOT)

    assert report["schema_version"] == "1.0.0"
    assert set(report["coverage"]) == {
        "static_assets",
        "frontend_inventory",
        "endpoint_latency",
        "sse_first_event",
        "process_state",
        "launcher_boot_benchmark",
        "asgi_comparison",
    }
    assert report["coverage"]["static_assets"]["status"] == "measured"
    assert report["coverage"]["frontend_inventory"]["status"] == "measured"
    assert report["coverage"]["endpoint_latency"]["status"] == "available_when_running"
    assert report["coverage"]["sse_first_event"]["status"] == "available_when_running"
    assert report["coverage"]["process_state"]["status"] == "available_when_running"
    assert report["coverage"]["launcher_boot_benchmark"]["status"] == "unsafe_by_default"
    assert report["coverage"]["asgi_comparison"]["status"] == "requires_prototype"


def test_static_report_finds_ports_assets_and_frontend_constructs():
    perf_audit = load_tool()
    report = perf_audit.run_static(ROOT)

    assert report["port_map"]["launcher"] == 8890
    assert report["port_map"]["app"] == 8080
    assert len(report["port_map"]) == 8
    assert "sandbox" not in report["port_map"]

    assets = report["static_assets"]
    assert any(item["path"].endswith("dx_benchmark/dataset.json") for item in assets)
    assert any(item["path"].endswith(".js") and item["gzip_bytes"] > 0 for item in assets)
    assert any(item["size_bytes"] > 100_000 for item in assets)

    templates = report["templates"]
    assert any(item["app"] == "dx_app" and item["blocking_scripts"] >= 10 for item in templates)

    frontend = report["frontend_inventory"]
    assert frontend["polling"]
    assert frontend["fetch_calls"]
    assert frontend["event_sources"]


def test_static_report_contains_safe_probe_policy_and_findings():
    perf_audit = load_tool()
    report = perf_audit.run_static(ROOT)

    allow_urls = {item["path"] for item in report["probe_policy"]["allowlist"]}
    avoid_paths = {item["path"] for item in report["probe_policy"]["avoidlist"]}

    assert "/api/health" in allow_urls
    assert "/api/hw_status" in allow_urls
    assert "/api/setup/diagnostics" in avoid_paths
    assert "/api/run" in avoid_paths
    assert any(f["severity"] in {"warning", "info"} for f in report["findings"])


def test_endpoint_probe_measures_latency_against_local_server():
    perf_audit = load_tool()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b'{"ok": true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_address[1]}/api/health"
        record = perf_audit.ProbeCollector().probe_endpoint(url, reps=3, timeout=3)
        assert record["status"] == 200
        assert record["latency_ms"]["reps"] == 3
        assert record["latency_ms"]["p50"] >= 0
    finally:
        server.shutdown()
        server.server_close()


def test_sse_probe_reads_first_event_and_closes():
    perf_audit = load_tool()

    class SSEHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            payload = b"data: {\"ok\": true}\n\n"
            chunk = f"{len(payload):x}\r\n".encode() + payload + b"\r\n0\r\n\r\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            self.wfile.write(chunk)
            self.wfile.flush()

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), SSEHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_address[1]}/api/sse"
        record = perf_audit.ProbeCollector().probe_sse_first_event(url, timeout=3)
        assert record["status"] == 200
        assert record["first_event_latency_ms"] >= 0
        assert record["first_event"].startswith("data:")
    finally:
        server.shutdown()
        server.server_close()


def test_static_report_includes_modelzoo_optimized_image_coverage():
    perf_audit = load_tool()
    report = perf_audit.run_static(ROOT)
    coverage = report["modelzoo_optimized_images"]
    assert "original_images" in coverage
    assert "optimized_images" in coverage
    assert "coverage_ratio" in coverage
    assert isinstance(coverage["original_images"], int)
    assert isinstance(coverage["optimized_images"], int)
    assert isinstance(coverage["coverage_ratio"], (int, float))
    assert coverage["coverage_ratio"] >= 0.0
    assert "manifest_present" in coverage
    assert isinstance(coverage["manifest_present"], bool)


def test_modelzoo_optimized_images_empty_dirs(tmp_path):
    """빈/누락 디렉터리 → 0 카운트, manifest_present=False."""
    perf_audit = load_tool()
    analyser = perf_audit.StaticAnalyser()
    result = analyser.analyse_modelzoo_optimized_images(tmp_path)
    assert result["original_images"] == 0
    assert result["optimized_images"] == 0
    assert result["coverage_ratio"] == 0.0
    assert result["manifest_present"] is False


def test_modelzoo_optimized_images_coverage_ratio(tmp_path):
    """원본 1 + 최적화 파생 1 → ratio 0.5 (divisor = originals * 2)."""
    perf_audit = load_tool()
    data = tmp_path / "dx_modelzoo" / "data"
    (data / "thumbnails").mkdir(parents=True)
    (data / "optimized" / "thumbnails").mkdir(parents=True)
    (data / "thumbnails" / "a.png").write_bytes(b"\x89PNG")
    (data / "optimized" / "thumbnails" / "a.webp").write_bytes(b"RIFF")
    analyser = perf_audit.StaticAnalyser()
    result = analyser.analyse_modelzoo_optimized_images(tmp_path)
    assert result["original_images"] == 1
    assert result["optimized_images"] == 1
    assert result["coverage_ratio"] == 0.5
    assert result["manifest_present"] is False


def test_modelzoo_optimized_images_manifest_present(tmp_path):
    """manifest.json 파일이 있으면 manifest_present=True."""
    perf_audit = load_tool()
    data = tmp_path / "dx_modelzoo" / "data" / "optimized"
    data.mkdir(parents=True)
    (data / "manifest.json").write_text("{}")
    analyser = perf_audit.StaticAnalyser()
    result = analyser.analyse_modelzoo_optimized_images(tmp_path)
    assert result["manifest_present"] is True


def test_cli_static_json_outputs_schema_keys(tmp_path):
    perf_audit = load_tool()
    out = tmp_path / "report.json"
    exit_code = perf_audit.main(["--root", str(ROOT), "--mode", "static", "--json", "--out", str(out)])

    assert exit_code == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert "static_assets" in report
    assert "frontend_inventory" in report
    assert "findings" in report

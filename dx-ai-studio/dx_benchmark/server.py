#!/usr/bin/env python3
"""DX Benchmark web server — port 8097.

Dashboard for YOLO26 hardware benchmarks (browse and compare results).
This server is a pure viewer: it serves the bundled dataset.json as-is and does no
aggregation at runtime. Benchmarks are run with the standalone dx-benchmark CLI
(`cd dx-benchmark && ./run.sh run`).
Built on DXBaseHandler.
"""

import json
from pathlib import Path

from shared.dx_server import DXBaseHandler, DXServer
from shared.chat import ChatEngine
from shared.chat import module_fallbacks as _module_fallbacks
from shared.paths import outputs_dir
from shared.shell import ShellSpec

DEFAULT_PORT = 8097
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
RESULTS_DIR = outputs_dir("benchmark")
LEGACY_RESULTS_DIR = BASE_DIR / "results"
DATASET_PATH = BASE_DIR / "dataset.json"
SERVER_NAME = "DX Benchmark"

# Static deployment config, inlined from the former BenchmarkConfig defaults.
# The studio is a pure viewer: these values are display-only (no runtime
# benchmark execution happens from the web server), and POST /api/config is
# rejected (settings are deployment-fixed).
CONFIG_THERMAL_COOLDOWN_ABS_CAP_C = 55.0
CONFIG_THERMAL_COOLDOWN_MAX_SEC = 1000.0
CONFIG_MODEL_LATENCY_LOOPS = 300
CONFIG_MODEL_WARMUP = 1
CONFIG_FPS_THRESHOLD = 30.0


def iter_result_dirs():
    """Yield result directories: canonical first, then legacy if it exists."""
    yield RESULTS_DIR
    if LEGACY_RESULTS_DIR.exists():
        yield LEGACY_RESULTS_DIR


_chat_engine = ChatEngine(
    app_name="dx_benchmark",
    fallback_rules=_module_fallbacks.rules("dx_benchmark")
)


def _check_bundled_dataset():
    """Sanity-check that the bundled dataset.json exists (no aggregation)."""
    if not DATASET_PATH.exists():
        print("  [Benchmark] Warning: bundled dataset.json not found at {}".format(DATASET_PATH))



# ── Shared App Shell ──────────────────────────────────────────
# The .top-bar + .main-tabs structure becomes the shell header and tab row.
# Labels are the English source text = i18n dictionary keys. Icon ids are in shared/static/dx-icons.svg.
DX_BENCHMARK_PAGES = (
    ("dashboard", "Dashboard", "dashboard"),
    ("results", "Results", "folder"),
    ("settings", "Settings", "setup"),
)

# The EdgeGuide button is specific to dx_benchmark, so it goes in the shared header's .toolbar slot.
_EDGEGUIDE_BTN = (
    '<button id="edgeguideBtn" class="dx-toolbar-btn" title="DX EdgeGuide" aria-label="DX EdgeGuide">'
    '<svg class="dx-ico" aria-hidden="true"><use href="/static/shared/dx-icons.svg#edge"></use></svg></button>'
)

DX_BENCHMARK_SHELL = ShellSpec(
    module_key="bench",
    pages=DX_BENCHMARK_PAGES,
    active_page="dashboard",
    toolbar_extra=_EDGEGUIDE_BTN,
)

class DXBenchmarkHandler(DXBaseHandler):
    """DX Benchmark HTTP request handler."""

    server_name = SERVER_NAME
    static_dir = STATIC_DIR
    templates_dir = TEMPLATES_DIR
    shell_spec = DX_BENCHMARK_SHELL
    log_silent = True

    def route(self):
        if self.handle_chat_routes(_chat_engine):
            return

        if self.route_common():
            return

        path = self.url_path

        if self.command == "GET":
            if path == "/api/health":
                return self.send_json({"status": "ok"})
            if path == "/api/hb":
                return self.send_json({"ok": True})
            if path == "/api/dataset":
                return self._serve_dataset()
            if path == "/api/results":
                return self._serve_results_list()
            if path.startswith("/api/results/"):
                return self._serve_result_detail(path)
            if path == "/api/config":
                return self._serve_config()

        if self.command == "POST":
            if path == "/api/config":
                return self._handle_config_save()

        self.route_legacy()

    def _serve_dataset(self):
        if DATASET_PATH.exists():
            return self.send_file(DATASET_PATH, "application/json")
        return self.send_json({"environments": [], "runs": [], "history": {}})

    def _serve_results_list(self):
        # Canonical-first deduplication: track seen (hw_id, run_id) pairs
        seen_runs = {}  # {hw_id: {run_id: run_info}}
        for results_dir in iter_result_dirs():
            if not results_dir.exists():
                continue
            for hw_dir in sorted(results_dir.iterdir()):
                if hw_dir.is_dir() and not hw_dir.name.startswith("."):
                    hw_id = hw_dir.name
                    if hw_id not in seen_runs:
                        seen_runs[hw_id] = {}
                    for run_dir in sorted(hw_dir.iterdir(), reverse=True):
                        if run_dir.is_dir() and not run_dir.name.startswith("."):
                            if run_dir.name not in seen_runs[hw_id]:
                                seen_runs[hw_id][run_dir.name] = {
                                    "run_id": run_dir.name,
                                    "has_report": (run_dir / "REPORT.md").exists(),
                                }
        results = []
        for hw_id in sorted(seen_runs):
            runs = sorted(seen_runs[hw_id].values(),
                          key=lambda r: r["run_id"], reverse=True)
            if runs:
                results.append({"hw_id": hw_id, "runs": runs})
        return self.send_json(results)

    def _serve_result_detail(self, path):
        parts = path.replace("/api/results/", "").strip("/").split("/")
        if len(parts) < 2:
            return self.send_error_json(400, "Need hw_id/run_id")
        hw_id, run_id = parts[0], parts[1]
        # Find first matching run across result dirs (canonical first)
        run_dir = None
        for results_dir in iter_result_dirs():
            candidate = results_dir / hw_id / run_id
            if candidate.exists():
                run_dir = candidate
                break
        if run_dir is None:
            return self.send_error_json(404, "Run not found")
        if len(parts) == 3 and parts[2] == "report":
            report_path = run_dir / "REPORT.md"
            if report_path.exists():
                return self.send_json({"markdown": report_path.read_text(errors="replace")})
            return self.send_error_json(404, "Report not found")
        detail = {}
        for fname in ["environment.json", "model_results.json", "pipeline_results.json", "multi_stream_results.json"]:
            fpath = run_dir / fname
            if fpath.exists():
                try:
                    detail[fname.replace(".json", "")] = json.loads(fpath.read_text())
                except json.JSONDecodeError:
                    detail[fname.replace(".json", "")] = None
        return self.send_json(detail)

    def _serve_config(self):
        return self.send_json({
            "model_dir": str(BASE_DIR / "assets" / "models"),
            "video_dir": str(BASE_DIR / "assets" / "videos"),
            "results_dir": str(RESULTS_DIR),
            "cooldown_temp": CONFIG_THERMAL_COOLDOWN_ABS_CAP_C,
            "wait_interval": CONFIG_THERMAL_COOLDOWN_MAX_SEC,
            "iterations": CONFIG_MODEL_LATENCY_LOOPS,
            "warmup": CONFIG_MODEL_WARMUP,
            "fps_threshold": CONFIG_FPS_THRESHOLD,
        })

    def _handle_config_save(self):
        # Settings are deployment-fixed; drain body without parsing, return 501.
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length < 0:
                length = 0
        except (ValueError, TypeError):
            length = 0
        if length > 0:
            self.rfile.read(length)
        return self.send_json(
            {"ok": False, "error": "Settings are deployment-fixed and cannot be changed at runtime"},
            501,
        )


def create_server(port=DEFAULT_PORT):
    """Server factory for tests: returns an HTTPServer instance."""
    from http.server import ThreadingHTTPServer
    srv = ThreadingHTTPServer(("127.0.0.1", port), DXBenchmarkHandler)
    srv.daemon_threads = True
    return srv


if __name__ == "__main__":
    _check_bundled_dataset()
    DXServer(DXBenchmarkHandler, SERVER_NAME, default_port=DEFAULT_PORT).start()

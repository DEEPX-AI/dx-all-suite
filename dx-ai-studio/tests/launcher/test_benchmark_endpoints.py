"""tests/launcher/test_benchmark_endpoints.py — dx_benchmark thin-viewer server contract.

server.py must serve the bundled dataset.json byte-for-byte and must never
import dx_benchmark.core.* (all runtime aggregation is dropped; the studio
is a pure viewer over the bundled snapshot).
"""
import importlib
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATASET_PATH = _REPO_ROOT / "dx_benchmark" / "dataset.json"


@pytest.fixture
def benchmark_server():
    """Start dx_benchmark.server's handler on an ephemeral port, self-contained."""
    sys.modules.pop("dx_benchmark.server", None)
    server_module = importlib.import_module("dx_benchmark.server")
    srv = server_module.create_server(port=0)
    port = srv.server_address[1]
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:{}".format(port)
    finally:
        srv.shutdown()
        srv.server_close()
        thread.join(timeout=5)


def test_dataset_served_matches_bundled_file_bytes(benchmark_server):
    """/api/dataset must return the bundled dataset.json bytes exactly (no aggregation)."""
    body = urllib.request.urlopen(benchmark_server + "/api/dataset", timeout=5).read()
    assert body == _DATASET_PATH.read_bytes()


def test_no_core_import():
    """Importing dx_benchmark.server must never pull in dx_benchmark.core.*."""
    for mod_name in list(sys.modules):
        if mod_name == "dx_benchmark.server" or mod_name.startswith("dx_benchmark.core"):
            sys.modules.pop(mod_name, None)
    importlib.import_module("dx_benchmark.server")
    assert not any(m.startswith("dx_benchmark.core") for m in sys.modules)


def test_config_served_static_no_core_import(benchmark_server):
    """/api/config must return a static dict without touching dx_benchmark.core.*."""
    body = urllib.request.urlopen(benchmark_server + "/api/config", timeout=5).read()
    payload = json.loads(body)
    for key in ("model_dir", "video_dir", "results_dir", "cooldown_temp",
                "wait_interval", "iterations", "warmup", "fps_threshold"):
        assert key in payload
    assert not any(m.startswith("dx_benchmark.core") for m in sys.modules)


def test_config_post_returns_501(benchmark_server):
    """POST /api/config remains rejected: settings are deployment-fixed."""
    req = urllib.request.Request(
        benchmark_server + "/api/config", data=b"{}", method="POST"
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        raise AssertionError("expected HTTPError 501")
    except urllib.error.HTTPError as exc:
        assert exc.code == 501

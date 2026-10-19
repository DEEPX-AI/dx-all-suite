"""Static server route contracts for DX App."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_app"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_dx_app_create_server_returns_http_server():
    """create_server(port) returns a usable HTTP server with expected attributes."""
    from dx_app.server import create_server
    srv = create_server(port=18080)
    try:
        assert hasattr(srv, "serve_forever")
        assert hasattr(srv, "shutdown")
        assert hasattr(srv, "server_close")
        host, port = srv.server_address
        assert port == 18080
    finally:
        srv.server_close()


def test_dx_app_server_uses_route_common_after_chat_routes():
    source = read_text(APP / "server.py")
    assert "static_dir = STATIC_DIR" in source
    assert "templates_dir = TEMPLATES_DIR" in source
    assert "server_name = SERVER_NAME" in source
    assert "if self.handle_chat_routes(_chat_engine):" in source
    assert "if self.route_common():" in source
    assert source.index("if self.handle_chat_routes(_chat_engine):") < source.index("if self.route_common():")
    assert 'path in ("/", "/index.html")' not in source
    assert "serve_shared_static" not in source
    assert "return self.send_file(SCRIPT_DIR/path.lstrip(\"/\"))" not in source
    assert "return self.route_legacy()" in source


def test_dx_app_main_does_not_access_private_create_server():
    source = read_text(APP / "server.py")
    assert "._create_server(" not in source


def test_dx_app_server_parses_save_output_boolean_explicitly():
    source = read_text(APP / "server.py")
    compact = source.replace(" ", "")
    assert "def _json_bool(" in source
    assert "'false'" in source or '"false"' in source
    assert "save_output=_json_bool(data.get(\"save_output\",True),default=True)" in compact


def test_dx_app_config_exports_shared_route_constants():
    source = read_text(APP / "core" / "config.py")
    assert 'SERVER_NAME = "DX App"' in source
    assert 'TEMPLATES_DIR  = SCRIPT_DIR/"templates"' in source or 'TEMPLATES_DIR = SCRIPT_DIR/"templates"' in source
    assert 'STATIC_DIR  = SCRIPT_DIR/"static"' in source or 'STATIC_DIR = SCRIPT_DIR/"static"' in source


def test_dx_app_scan_categories_keeps_hardcoded_baseline(tmp_path, monkeypatch):
    import config

    fake_cpp = tmp_path / "cpp_example"
    fake_cpp.mkdir()
    (fake_cpp / "object_detection").mkdir()
    fake_py = tmp_path / "python_example"
    fake_py.mkdir()

    monkeypatch.setattr(config, "CPP_DIR", fake_cpp)
    monkeypatch.setattr(config, "PY_DIR", fake_py)

    categories = config._scan_categories()

    assert "object_detection" in categories
    # In a per-model checkout the baseline also uses the new name (face_alignment → face_landmark)
    from shared.tasks import canonical
    expected = canonical("face_alignment") if config.LAYOUT == config._layout.PER_MODEL else "face_alignment"
    assert expected in categories


def test_dx_app_scan_categories_skips_the_multi_model_folders(tmp_path, monkeypatch):
    """multi_model (pipeline JSONs) and multi_model_graph (graph engine and graph JSONs) hold multi-model
    examples, not one task's models; they must not show up as a task (Lab's task list read them as one)."""
    import config

    fake_cpp = tmp_path / "cpp_example"
    for name in ("object_detection", "multi_model", "multi_model_graph"):
        (fake_cpp / name).mkdir(parents=True)
    fake_py = tmp_path / "python_example"
    (fake_py / "multi_model").mkdir(parents=True)
    monkeypatch.setattr(config, "CPP_DIR", fake_cpp)
    monkeypatch.setattr(config, "PY_DIR", fake_py)

    categories = config._scan_categories()

    assert "object_detection" in categories
    assert "multi_model" not in categories and "multi_model_graph" not in categories


def test_idle_shutdown_is_only_for_a_standalone_server(monkeypatch):
    """Only a standalone dx_app (opened in its own browser tab) shuts down when idle. Under the launcher, which owns
    module lifecycles, an idle shutdown ("No heartbeat — shutting down") would leave dx_app down until the port-only
    watchdog respawned it, and Model Zoo's Run Inference (proxied to dx_app) would fail meanwhile."""
    import server
    monkeypatch.delenv("DX_PORT_FILE", raising=False)
    assert server._idle_shutdown_enabled()
    monkeypatch.setenv("DX_PORT_FILE", "/tmp/dx_app.port")
    assert not server._idle_shutdown_enabled()


# The Run page's Live display: slots 0-7 only (slot 8 is the Graph Composer's Live), a local origin, and a few
# viewers per stream.

LOCAL = {"Origin": "http://localhost:8080"}


def _handler(method, path, query=None, payload=None, headers=None, frames=None):
    """Drive dx_app's real Handler.route() without a socket; `frames` feeds an MJPEG stream until it runs out."""
    import io
    from dx_app import server

    captured = {"headers": {}}

    class Pipe(io.BytesIO):
        def __init__(self, n):
            super().__init__()
            self.left = n

        def flush(self):
            self.left -= 1
            if self.left <= 0:
                raise BrokenPipeError

    h = object.__new__(server.Handler)
    h.command, h.url_path = method, path
    h.headers = dict(LOCAL) if headers is None else headers
    h.query = {k: [v] for k, v in (query or {}).items()}
    h.handle_chat_routes = lambda _engine: False
    h.read_json_body = lambda: payload if payload is not None else {}
    h.wfile = Pipe(frames or 1)
    h.send_json = lambda data, code=200: captured.update(data=data, code=code)
    h.send_error = lambda code, *a, **k: captured.update(code=code)
    h.send_response = lambda code: captured.update(code=code)
    h.send_header = lambda k, v: captured["headers"].update({k: v})
    h.end_headers = lambda: None
    h.route()
    captured["body"] = h.wfile.getvalue()
    return captured


def _frames(monkeypatch):
    from dx_app import server
    seen = []
    monkeypatch.setattr(server, "capture_live_frame", lambda slot=0: seen.append(slot) or b"JPEG%d" % slot)
    monkeypatch.setattr(server.time, "sleep", lambda _s: None)
    return seen


def test_the_run_page_live_frame_serves_only_its_own_slots(monkeypatch):
    seen = _frames(monkeypatch)
    ok = _handler("GET", "/api/live_frame", {"slot": "7"}, frames=2)
    assert ok["code"] == 200 and b"JPEG7" in ok["body"] and set(seen) == {7}
    for bad in ("8", "-1", "x", "99"):
        r = _handler("GET", "/api/live_frame", {"slot": bad})
        assert (r["code"], r["data"]["error_key"]) == (400, "invalid_slot"), bad
    assert set(seen) == {7}, "slot 8 is the graph Live's display"


def test_the_run_page_live_frame_refuses_another_origin(monkeypatch):
    seen = _frames(monkeypatch)
    r = _handler("GET", "/api/live_frame", {"slot": "0"}, headers={"Origin": "https://evil.example.com"})
    assert (r["code"], r["data"]["error"]) == (403, "Cross-origin access denied") and r["body"] == b"" and not seen
    r = _handler("GET", "/api/live_frame", {"slot": "0"}, headers={"Referer": "https://evil.example.com/x"})
    assert r["code"] == 403 and not seen


def test_run_live_and_live_stop_take_only_the_run_page_slots(monkeypatch):
    from dx_app import server
    calls = []
    monkeypatch.setattr(server, "run_inference_live", lambda **kw: calls.append(("run", kw["slot_idx"])) or {})
    monkeypatch.setattr(server, "stop_inference_live", lambda slot=None: calls.append(("stop", slot)) or {})
    monkeypatch.setattr(server, "_validate_inference_payload", lambda data, live=False: (None, None))
    for bad in (8, -1, "x", 1.5):
        r = _handler("POST", "/api/run_live", payload={"slot_idx": bad})
        assert (r["code"], r["data"]["error_key"]) == (400, "invalid_slot"), bad
        r = _handler("POST", "/api/live_stop", payload={"slot_idx": bad})
        assert (r["code"], r["data"]["error_key"]) == (400, "invalid_slot"), bad
    assert calls == []
    _handler("POST", "/api/run_live", payload={"slot_idx": 7})
    _handler("POST", "/api/run_live", payload={})
    _handler("POST", "/api/live_stop", payload={"slot_idx": "3"})
    _handler("POST", "/api/live_stop", payload={})
    assert calls == [("run", 7), ("run", 0), ("stop", 3), ("stop", None)]


def test_run_live_takes_a_slot_count_of_the_run_page_slots(monkeypatch):
    """n_total_slots sizes the camera fan-out (one ffmpeg UDP stream per slot): a whole number from 1 to RUN_SLOTS."""
    from dx_app import server
    calls = []
    monkeypatch.setattr(server, "run_inference_live", lambda **kw: calls.append(kw["n_total_slots"]) or {})
    monkeypatch.setattr(server, "_validate_inference_payload", lambda data, live=False: (None, None))
    for bad in (0, -1, server.RUN_SLOTS + 1, 10 ** 6, "x", 1.5, True, None, [2]):
        r = _handler("POST", "/api/run_live", payload={"slot_idx": 0, "n_total_slots": bad})
        assert (r["code"], r["data"]["error_key"]) == (400, "invalid_slot"), bad
    assert calls == []
    for good, want in ((1, 1), (server.RUN_SLOTS, server.RUN_SLOTS), ("3", 3)):
        _handler("POST", "/api/run_live", payload={"slot_idx": 0, "n_total_slots": good})
    _handler("POST", "/api/run_live", payload={"slot_idx": 0})
    assert calls == [1, server.RUN_SLOTS, 3, 1]


def test_a_live_stream_takes_a_few_viewers_at_a_time(monkeypatch):
    from dx_app import server
    from dx_app.core import graph_live
    _frames(monkeypatch)
    monkeypatch.setattr(graph_live, "frame_ok", lambda jid: jid == "L1")
    monkeypatch.setattr(graph_live, "frame", lambda jid: b"G")
    monkeypatch.setitem(server._viewers, "live:2", server.MAX_VIEWERS)
    r = _handler("GET", "/api/live_frame", {"slot": "2"})
    assert (r["code"], r["data"]["error_key"]) == (429, "too_many_viewers") and r["body"] == b""
    assert _handler("GET", "/api/live_frame", {"slot": "3"})["code"] == 200, "each slot counts its own viewers"
    assert server._viewers.get("live:3", 0) == 0, "a viewer that left is not counted"
    monkeypatch.setitem(server._viewers, "graph_live", server.MAX_VIEWERS)
    r = _handler("GET", "/api/graph/live/frame", {"id": "L1"})
    assert (r["code"], r["data"]["error_key"]) == (429, "too_many_viewers")
    monkeypatch.setitem(server._viewers, "graph_live", 0)
    assert _handler("GET", "/api/graph/live/frame", {"id": "L1"}, frames=2)["code"] == 200
    assert server._viewers["graph_live"] == 0


def test_shutdown_stops_the_graph_live_before_the_live_displays_go(monkeypatch):
    """The graph Live draws on an Xvfb display that shutdown_live_processes kills with the Run page's ones."""
    from dx_app import server
    from dx_app.core import graph_gallery, graph_live, graph_run
    order = []
    monkeypatch.setattr(server, "stop_inference", lambda: order.append("stop_inference"))
    monkeypatch.setattr(server, "shutdown_live_processes", lambda: order.append("live"))
    for mod in (graph_run, graph_live, graph_gallery):
        monkeypatch.setattr(mod, "stop_all", lambda m=mod.__name__: order.append(m.rsplit(".", 1)[1]))
    server._stop_children()
    assert order.index("graph_live") < order.index("live")
    assert set(order) == {"stop_inference", "live", "graph_run", "graph_live", "graph_gallery"}


def test_shutdown_live_processes_stops_a_graph_live_first(monkeypatch):
    """atexit runs shutdown_live_processes too: it ends a running graph Live before it kills the Xvfb displays."""
    from dx_app.core import camera, graph_live, live
    order = []

    class P:
        def poll(self):
            return None

        def terminate(self):
            order.append("xvfb")

        def wait(self, timeout=None):
            return 0
    monkeypatch.setattr(graph_live, "stop_all", lambda: order.append("graph_live"))
    monkeypatch.setattr(camera, "_xvfb_procs", {8: P()})
    monkeypatch.setattr(live, "stop_inference_live", lambda slot=None: None)
    live.shutdown_live_processes()
    assert order[:2] == ["graph_live", "xvfb"]

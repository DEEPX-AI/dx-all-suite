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
    assert "face_alignment" in categories

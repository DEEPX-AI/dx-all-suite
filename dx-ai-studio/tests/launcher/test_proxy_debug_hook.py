import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_proxy_wires_log_http_and_boot_export():
    src = (ROOT / "launcher" / "launcher.py").read_text(encoding="utf-8")
    assert 'os.environ["DX_STUDIO_BOOT"] = _LAUNCHER_BOOT_ID' in src
    assert "from shared import debug_log" in src or "import shared.debug_log" in src
    assert "debug_log.log_http(" in src
    assert "handler.command" in src and "handler.client_address[0]" in src

"""DXServer ephemeral (--port 0) bind + DX_PORT_FILE handshake (launcher discovery)."""
import socket


def _make_server(port, env_port_file=None, monkeypatch=None):
    from dx_server import DXServer, DXBaseHandler
    if env_port_file is not None:
        monkeypatch.setenv("DX_PORT_FILE", str(env_port_file))
    else:
        monkeypatch.delenv("DX_PORT_FILE", raising=False)
    srv = DXServer(DXBaseHandler, "Test", 0)
    s = srv.create_http_server(0)
    return srv, s


def test_ephemeral_binds_real_port_and_writes_file(tmp_path, monkeypatch):
    pf = tmp_path / "test.port"
    srv, s = _make_server(0, env_port_file=pf, monkeypatch=monkeypatch)
    try:
        assert s is not None
        actual = s.server_address[1]
        assert actual > 0                      # OS assigned a real port
        assert int(pf.read_text().strip()) == actual   # reported to the port file
        # it is actually bound: connecting to it succeeds
        with socket.create_connection(("127.0.0.1", actual), timeout=2):
            pass
    finally:
        s.server_close()


def test_no_port_file_env_does_not_crash(tmp_path, monkeypatch):
    srv, s = _make_server(0, env_port_file=None, monkeypatch=monkeypatch)
    try:
        assert s is not None and s.server_address[1] > 0
    finally:
        s.server_close()

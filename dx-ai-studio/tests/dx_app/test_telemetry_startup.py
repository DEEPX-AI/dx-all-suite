"""DX App stays up when NPU telemetry cannot start, and never reads fake values (S5).

Under the launcher DX App reads DX Monitor's telemetry (one NPU worker for the suite) instead
of starting a second worker; standalone it starts its own. Either way a failure leaves the
server serving and telemetry reads as unavailable with the error.
"""
import json
import threading
import urllib.request

import pytest

from dx_app import server as app_server
from shared import hardware


@pytest.fixture(autouse=True)
def _clean_bindings(monkeypatch):
    monkeypatch.delenv("DX_MONITOR_PORT_FILE", raising=False)
    monkeypatch.setenv("DX_MONITOR_EXPLICIT_MOCK", "1")   # must not leak mock values into DX App
    yield
    hardware.init_hw(telemetry=None, explicit_mock=False)


def _failing_start(monkeypatch):
    from dx_monitor.core import hardware_init

    def boom(self):
        raise RuntimeError("telemetry worker exploded")

    monkeypatch.setattr(hardware_init.TelemetrySupervisor, "start", boom)


def test_a_supervisor_that_fails_to_start_leaves_telemetry_unavailable_with_the_error(monkeypatch):
    _failing_start(monkeypatch)
    owned = app_server._start_telemetry()
    assert owned is None
    hw = hardware.get_hw()
    assert hw["available"] is False and hw["mock"] is False and hw["npus"] == []
    assert "telemetry worker exploded" in hw["telemetry"]["error"]


def test_the_server_still_serves_when_telemetry_start_raises(monkeypatch, tmp_path):
    _failing_start(monkeypatch)
    captured = {}
    real_create = app_server.DXServer.create_http_server

    def create(self, port):
        captured["srv"] = real_create(self, 0)
        return captured["srv"]

    monkeypatch.setattr(app_server.DXServer, "create_http_server", create)
    monkeypatch.setattr(app_server.DXServer, "register_signals", lambda self: None)
    monkeypatch.setattr(app_server, "_idle_shutdown_enabled", lambda: False)
    monkeypatch.setattr("sys.argv", ["server.py", "--port", "0", "--no-browser"])
    thread = threading.Thread(target=app_server.main, daemon=True)
    thread.start()
    for _ in range(100):
        if "srv" in captured:
            break
        threading.Event().wait(0.05)
    srv = captured["srv"]
    try:
        port = srv.server_address[1]
        for _ in range(40):
            if not thread.is_alive():
                break
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/category_labels", timeout=2) as response:
                    assert response.status == 200
                    break
            except OSError:
                threading.Event().wait(0.05)
        else:
            pytest.fail("DX App did not serve after a telemetry start failure")
        assert thread.is_alive()
    finally:
        if thread.is_alive():   # serve_forever never started when main() raised: shutdown() would block
            srv.shutdown()
        thread.join(timeout=10)
    assert not thread.is_alive()


def test_under_the_launcher_dx_app_reads_monitor_and_starts_no_worker(monkeypatch, tmp_path):
    from dx_monitor.core import hardware_init

    monkeypatch.setattr(hardware_init.TelemetrySupervisor, "start",
                        lambda self: pytest.fail("a second NPU worker must not start under the launcher"))
    port_file = tmp_path / "dx_monitor.port"
    port_file.write_text("1")   # nothing listens: Monitor not up yet
    monkeypatch.setenv("DX_MONITOR_PORT_FILE", str(port_file))
    assert app_server._start_telemetry() is None
    hw = hardware.get_hw()
    assert hw["available"] is False and hw["mock"] is False
    assert "DX Monitor telemetry unavailable" in hw["telemetry"]["error"]


def test_monitor_client_maps_real_data_and_refuses_monitor_mock(tmp_path):
    from shared.telemetry_client import MonitorTelemetry

    port_file = tmp_path / "p"
    port_file.write_text("8094")
    replies = {}

    class Reply:
        def __init__(self, body):
            self.body = json.dumps(body).encode()

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self, _n):
            return self.body

    def opener(request, timeout):
        replies["url"] = request.full_url
        return Reply(replies["body"])

    client = MonitorTelemetry(port_file, opener=opener)
    replies["body"] = {"available": True, "source_mode": "real", "mock": False,
                       "npus": [{"id": 0, "temp": 41}], "telemetry": {"diagnostics": []}}
    snap = client.snapshot()
    assert replies["url"] == "http://127.0.0.1:8094/api/hw_status"
    assert snap["available"] is True and snap["npus"] == [{"id": 0, "temp": 41}]
    replies["body"] = {"available": True, "source_mode": "mock", "mock": True, "npus": [{"id": 0}]}
    snap = client.snapshot()
    assert snap["available"] is False and snap["npus"] == [] and "not real hardware" in snap["error"]


def test_the_launcher_hands_children_the_monitor_port_file():
    """The one NPU worker is DX Monitor's; children find it through the launcher's port file."""
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2] / "launcher" / "launcher.py").read_text(encoding="utf-8")
    assert 'env["DX_MONITOR_PORT_FILE"] = str(PORTS_DIR / "dx_monitor.port")' in src

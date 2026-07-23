"""Contract tests for ModelZooGateway — DX App integration boundary."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_app"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")



class FakeModelZooAdapter:
    """Minimal fake implementing the modelzoo adapter protocol."""

    def __init__(self):
        self.calls = []

    def list_models(self, source="internal"):
        self.calls.append(("list_models", source))
        return {"ok": True, "models": [], "count": 0}

    def download(self, items, source="internal"):
        self.calls.append(("download", items, source))
        return {"ok": True, "total": len(items), "started": True}

    def status(self):
        self.calls.append("status")
        return {"running": False, "total": 0, "done": 0, "current": "",
                "results": [], "finished": False}

    def stop(self):
        self.calls.append("stop")
        return {"ok": True, "status": "cancelling"}


def _make_gateway(adapter=None):
    from dx_app.core.modelzoo_gateway import ModelZooGateway
    return ModelZooGateway(adapter or FakeModelZooAdapter())


def test_gateway_exposes_list_models():
    gw = _make_gateway()
    result = gw.list_models("internal")
    assert "ok" in result
    assert "models" in result


def test_gateway_delegates_list_models():
    adapter = FakeModelZooAdapter()
    gw = _make_gateway(adapter)
    gw.list_models("public")
    assert ("list_models", "public") in adapter.calls


def test_gateway_delegates_download():
    adapter = FakeModelZooAdapter()
    gw = _make_gateway(adapter)
    items = [{"name": "yolov8", "chip": "qlite", "dxnn_url": "http://x"}]
    result = gw.download(items, "internal")
    assert result["started"] is True
    assert adapter.calls[0][0] == "download"


def test_gateway_delegates_status():
    adapter = FakeModelZooAdapter()
    gw = _make_gateway(adapter)
    result = gw.status()
    assert "running" in result
    assert "status" in adapter.calls


def test_gateway_delegates_stop():
    adapter = FakeModelZooAdapter()
    gw = _make_gateway(adapter)
    result = gw.stop()
    assert result["ok"] is True
    assert "stop" in adapter.calls



def test_server_imports_modelzoo_gateway():
    source = read_text(APP / "server.py")
    assert "modelzoo_gateway" in source or "ModelZooGateway" in source


def test_server_uses_module_level_modelzoo_gateway():
    """server.py should have a module-level gateway instance for modelzoo routes."""
    source = read_text(APP / "server.py")
    assert "_modelzoo_gw" in source or "modelzoo_gw" in source


def test_server_modelzoo_list_route_uses_gateway():
    source = read_text(APP / "server.py")
    assert "modelzoo_gw.list_models(" in source or "_modelzoo_gw.list_models(" in source


def test_server_modelzoo_status_route_uses_gateway():
    source = read_text(APP / "server.py")
    assert "modelzoo_gw.status()" in source or "_modelzoo_gw.status()" in source


def test_server_modelzoo_download_route_uses_gateway():
    source = read_text(APP / "server.py")
    assert "modelzoo_gw.download(" in source or "_modelzoo_gw.download(" in source


def test_server_modelzoo_stop_route_uses_gateway():
    source = read_text(APP / "server.py")
    assert "modelzoo_gw.stop()" in source or "_modelzoo_gw.stop()" in source

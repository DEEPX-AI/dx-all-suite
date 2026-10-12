"""Model Zoo keeps reaching DX App after DX App restarts on a new port.

The launcher starts modules on ephemeral ports. When DX App restarts (by the watchdog after a crash, or from the
home), it comes back on another port; a DX_APP_PORT read once at start would make every Zoo 'Run Inference'
answer DX_APP_UNAVAILABLE until the Zoo restarts too."""
from __future__ import annotations

import importlib


def test_the_proxy_reads_the_current_port_from_the_launchers_port_file(tmp_path, monkeypatch):
    pf = tmp_path / "dx_app.port"
    pf.write_text("40001")
    monkeypatch.setenv("DX_APP_PORT_FILE", str(pf))
    monkeypatch.setenv("DX_APP_PORT", "8080")
    cfg = importlib.import_module("dx_modelzoo.core.config")
    assert cfg.dx_app_port() == 40001
    pf.write_text("40002\n")
    assert cfg.dx_app_port() == 40002, "a restart's new port is picked up without restarting the zoo"
    pf.unlink()
    assert cfg.dx_app_port() == 8080, "no port file: the env value"


def test_the_launcher_hands_children_the_port_file():
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2] / "launcher" / "launcher.py").read_text(encoding="utf-8")
    assert 'env["DX_APP_PORT_FILE"]' in src
    proxy = (Path(__file__).resolve().parents[2] / "dx_modelzoo" / "core" / "proxy.py").read_text(encoding="utf-8")
    assert "dx_app_port()" in proxy

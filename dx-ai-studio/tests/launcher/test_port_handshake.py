"""Launcher ↔ sub-server port handshake (ephemeral :0 discovery via port file)."""
import importlib
import sys
import threading
import time
from pathlib import Path

_STUDIO_ROOT = Path(__file__).resolve().parents[2]
if str(_STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDIO_ROOT))


def _launcher_mod():
    if "launcher" in sys.modules and not hasattr(sys.modules["launcher"], "__path__"):
        del sys.modules["launcher"]
    return importlib.import_module("launcher.launcher")


def test_await_reported_port_reads_int(tmp_path):
    launcher = _launcher_mod()
    pf = tmp_path / "dx_app.port"
    pf.write_text("54321")
    assert launcher._await_reported_port(str(pf), timeout=2) == 54321


def test_await_reported_port_waits_then_reads(tmp_path):
    launcher = _launcher_mod()
    pf = tmp_path / "dx_stream.port"

    def _writer():
        time.sleep(0.3)
        pf.write_text("49999")

    threading.Thread(target=_writer, daemon=True).start()
    assert launcher._await_reported_port(str(pf), timeout=3) == 49999


def test_await_reported_port_timeout_returns_none(tmp_path):
    launcher = _launcher_mod()
    pf = tmp_path / "missing.port"
    assert launcher._await_reported_port(str(pf), timeout=0.5) is None


def test_port_file_path_under_ports_dir():
    launcher = _launcher_mod()
    p = Path(launcher._port_file("dx_app"))
    assert p.name == "dx_app.port"
    assert p.parent.name == ".ports"


def test_referer_targets_are_server_ids_resolved_via_live_map():
    """A3: _SUBAPP_REFERER_TARGETS holds server_ids; the proxy resolves them through the
    live _LAUNCHER_PROXY_PORTS (ephemeral ports), not static constants."""
    launcher = _launcher_mod()
    targets = launcher.LauncherHandler._SUBAPP_REFERER_TARGETS
    ids = {sid for _prefix, sid, _inj in targets}
    assert {"dx_app", "dx_modelzoo", "dx_stream", "dx_compiler", "dx_agent_dev"} <= ids
    for _prefix, sid, _inj in targets:
        assert sid in launcher._LAUNCHER_PROXY_PORTS, f"{sid} not in proxy map"


def test_restart_updates_entry_to_new_ephemeral_port(monkeypatch):
    """A5/Part5: on restart the sub-server gets a NEW ephemeral port; _do_module_restart
    must update entry['port'] + the proxy map to it (not keep the stale port)."""
    launcher = _launcher_mod()

    class _DeadProc:
        pid = 999999

        def poll(self):
            return 0

    sid = "dx_stream"
    launcher._LAUNCHER_PROXY_PORTS[sid] = 41111
    entry = {
        "port": 41111,
        "cwd": str(launcher.STREAM_DIR),
        "proc": _DeadProc(),
        "status": "dead",
    }

    monkeypatch.setattr(launcher, "_is_port_open", lambda p: False)
    monkeypatch.setattr(launcher, "_force_free_port", lambda p: None)

    def _fake_start(name, directory, port=0, server_id=None):
        launcher._LAUNCHER_PROXY_PORTS[server_id] = 52222
        launcher._procs[name] = _DeadProc()
        return True

    monkeypatch.setattr(launcher, "start_sub_server", _fake_start)

    launcher._do_module_restart(sid, entry)
    assert entry["port"] == 52222
    assert launcher._LAUNCHER_PROXY_PORTS[sid] == 52222
    assert entry["status"] == "alive"

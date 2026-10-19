"""DX_LAUNCHER_RUN_DIR moves the launcher's run state (port handshake files, pid file) out of the checkout.

A second launcher started from the same checkout — the acceptance suite's own instance, while a user's studio or
another CI run is up — must not overwrite the other's `.ports/*.port` nor read its `.launcher_pids` and kill its
module servers at boot.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_PROBE = ("import json, launcher.launcher as L; "
          "print(json.dumps({'ports': str(L.PORTS_DIR), 'pids': str(L._PIDFILE), 'app': L._port_file('dx_app')}))")


def _probe(env_extra):
    env = {k: v for k, v in os.environ.items() if k != "DX_LAUNCHER_RUN_DIR"}
    env.update(env_extra)
    env["PYTHONPATH"] = str(ROOT)
    out = subprocess.run([sys.executable, "-c", _PROBE], cwd=str(ROOT), env=env,
                         capture_output=True, text=True, timeout=60, check=True).stdout
    return json.loads(out.strip().splitlines()[-1])


def test_default_run_state_stays_in_the_launcher_folder():
    got = _probe({})
    assert got["ports"] == str(ROOT / "launcher" / ".ports")
    assert got["pids"] == str(ROOT / "launcher" / ".launcher_pids")


def test_run_dir_env_moves_ports_and_pidfile(tmp_path):
    got = _probe({"DX_LAUNCHER_RUN_DIR": str(tmp_path)})
    assert got["ports"] == str(tmp_path / ".ports")
    assert got["pids"] == str(tmp_path / ".launcher_pids")
    assert got["app"] == str(tmp_path / ".ports" / "dx_app.port")

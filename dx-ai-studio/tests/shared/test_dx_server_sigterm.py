"""A module server exits promptly on SIGTERM.

The signal handler in shared/dx_server.py must not call shutdown() on the main thread that runs serve_forever():
shutdown() waits for serve_forever() to return, so the two wait on each other and hang. --port 0 servers started by
tests would then survive SIGTERM and pile up as orphans.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_a_module_server_exits_promptly_on_sigterm(tmp_path):
    port_file = tmp_path / "port"
    # repo root on PYTHONPATH, as launcher/launcher.py starts its servers
    env = dict(os.environ, DX_PORT_FILE=str(port_file), PYTHONUNBUFFERED="1",
               PYTHONPATH=str(ROOT) + (os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else ""))
    proc = subprocess.Popen([sys.executable, str(ROOT / "dx_planner" / "server.py"), "--port", "0", "--no-browser"],
                            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 20
        while not port_file.exists() and time.monotonic() < deadline:
            time.sleep(0.1)
        assert port_file.exists(), "서버가 뜨지 않았다"
        time.sleep(0.3)
        proc.send_signal(signal.SIGTERM)
        assert proc.wait(timeout=5) is not None
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()


def test_the_handler_does_not_call_shutdown_on_the_serving_thread():
    src = (ROOT / "shared" / "dx_server.py").read_text(encoding="utf-8")
    body = src[src.index("    def _register_signals(self):"):]
    body = body[:body.index("\n    def ", 10)]
    assert "threading.Thread(" in body and "target=self._server.shutdown" in body

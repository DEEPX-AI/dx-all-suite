"""NPU telemetry sources for modules other than DX Monitor — never native runtime imports.

DX Monitor owns the one NPU telemetry worker (dx_monitor/core/hardware_init.py). Under the
launcher every module runs as its own process, so another module reads Monitor's
``/api/hw_status`` over loopback (:class:`MonitorTelemetry`) instead of starting a second
worker that polls the same device. A source that cannot start is :class:`FailedTelemetry`:
telemetry then reads as unavailable with that error — never mock or invented values.

Both expose ``snapshot()`` in the supervisor's cache shape that ``shared.hardware`` consumes.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

_SOURCE_MODES = ("real", "stale", "unavailable")


def _unavailable(error, diagnostics=()):
    return {"available": False, "source_mode": "unavailable", "npus": [],
            "diagnostics": list(diagnostics), "error": str(error)}


class FailedTelemetry:
    """Telemetry that failed to start: every read is unavailable with the start error."""

    def __init__(self, error):
        self.error = "Telemetry failed to start: {}".format(error)

    def snapshot(self):
        return _unavailable(self.error)

    def stop(self):
        return None


class MonitorTelemetry:
    """Read DX Monitor's telemetry over loopback; the port is re-read per request (Monitor may restart)."""

    def __init__(self, port_file, timeout=1.0, opener=None):
        self.port_file = Path(port_file)
        self.timeout = timeout
        self._open = opener or urllib.request.urlopen

    def _url(self):
        text = self.port_file.read_text(encoding="utf-8").strip()
        if not text.isdigit() or not 0 < int(text) < 65536:
            raise ValueError("invalid port in {}".format(self.port_file))
        return "http://127.0.0.1:{}/api/hw_status".format(int(text))

    def snapshot(self):
        try:
            with self._open(urllib.request.Request(self._url()), timeout=self.timeout) as response:
                data = json.loads(response.read(256 * 1024).decode("utf-8"))
        except (OSError, ValueError) as error:
            return _unavailable("DX Monitor telemetry unavailable: {}".format(error))
        if not isinstance(data, dict):
            return _unavailable("DX Monitor telemetry unavailable: invalid response")
        telemetry = data.get("telemetry") if isinstance(data.get("telemetry"), dict) else {}
        mode = data.get("source_mode")
        diagnostics = telemetry.get("diagnostics") if isinstance(telemetry.get("diagnostics"), list) else []
        if data.get("mock") or mode not in _SOURCE_MODES:
            # Monitor's explicit demo mode (or an unknown mode) is not hardware data for this module.
            return _unavailable("DX Monitor telemetry is not real hardware data (source_mode={})".format(mode),
                                diagnostics)
        snapshot = {"available": bool(data.get("available")), "source_mode": mode,
                    "npus": data.get("npus") if isinstance(data.get("npus"), list) else [],
                    "diagnostics": diagnostics}
        if telemetry.get("error") is not None:
            snapshot["error"] = str(telemetry["error"])
        return snapshot

    def stop(self):
        return None


def monitor_port_file():
    """The launcher's DX Monitor port file, when this module runs under the launcher."""
    value = os.environ.get("DX_MONITOR_PORT_FILE", "").strip()
    return Path(value) if value else None

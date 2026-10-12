"""/api/pipeline/status reports what is running, whatever the output mode.

Checking only the WebRTC pipeline manager would show a demo running over MJPEG or fMP4 as Idle on the dashboard,
with no way to tell which demo it is.
"""
from __future__ import annotations

import json
import sys
import urllib.request

import pytest

from tests.server_helpers import start_module_server


@pytest.fixture()
def stream():
    srv, port = start_module_server("dx_stream")
    server = sys.modules["dx_stream.server"]
    yield server, port
    server._current_output_mode = None
    server._current_pipeline_id = None
    server._current_demo_id = None
    srv.shutdown()


def _status(port):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/pipeline/status", timeout=5) as r:
        return json.loads(r.read())


def test_idle_says_nothing_runs(stream):
    _, port = stream
    assert _status(port) == {"running": False, "pipeline_id": None, "output_mode": None, "demo_id": None}


def test_an_mjpeg_demo_is_running_and_named(stream, monkeypatch):
    server, port = stream
    from dx_stream.core import mjpeg
    monkeypatch.setattr(mjpeg, "is_streaming", lambda: True)
    server._current_output_mode = "mjpeg"
    server._current_pipeline_id = "mjpeg-demo-4"
    server._current_demo_id = 4
    assert _status(port) == {"running": True, "pipeline_id": "mjpeg-demo-4", "output_mode": "mjpeg", "demo_id": 4}


def test_a_stopped_mjpeg_stream_is_not_running(stream, monkeypatch):
    server, port = stream
    from dx_stream.core import mjpeg
    monkeypatch.setattr(mjpeg, "is_streaming", lambda: False)
    server._current_output_mode = "mjpeg"
    server._current_demo_id = 4
    assert _status(port)["running"] is False


def test_stopping_playback_forgets_the_demo(stream, monkeypatch):
    server, _ = stream
    server._current_demo_id = 2
    server._stop_all_playback()
    assert server._current_demo_id is None

"""Several live slots on one camera work when the camera has no MJPEG 640x480 mode (2026-10-11 real-use audit).

The ffmpeg fan-out always asked for -input_format mjpeg -video_size 640x480. A camera without that mode (YUYV-only
webcams, capture cards; here a v4l2loopback device at 1280x720 YUV) made ffmpeg exit at once and every multi-slot run
failed with "Failed to start camera multiplexer (ffmpeg). Is ffmpeg installed?". It now falls back to the camera's own
format scaled to 640x480, and a failure says what ffmpeg said.
"""
import io

from dx_app.core import camera


class _Proc:
    def __init__(self, cmd, alive, err=b""):
        self.cmd, self._alive, self.stderr, self.pid = cmd, alive, io.BytesIO(err), 1

    def poll(self):
        return None if self._alive else 1

    def terminate(self):
        self._alive = False

    def wait(self, timeout=None):
        return 0


def _patch(monkeypatch, outcomes):
    made = []

    def popen(cmd, **kw):
        alive, err = outcomes[len(made)]
        p = _Proc(cmd, alive, err)
        made.append(p)
        return p

    monkeypatch.setattr(camera.subprocess, "Popen", popen)
    monkeypatch.setattr(camera.time, "sleep", lambda s: None)
    monkeypatch.setattr(camera.Path, "exists", lambda self: True)
    monkeypatch.setattr(camera, "_cam_mux_proc", None)
    return made


def test_falls_back_to_the_cameras_own_format(monkeypatch):
    made = _patch(monkeypatch, [(False, b"Cannot find a proper format for codec 'mjpeg'"), (True, b"")])
    assert camera._start_cam_mux(0, 2) is True
    assert "-input_format" in made[0].cmd
    second = made[1].cmd
    assert "-input_format" not in second and "-video_size" not in second
    assert "scale=640:480" in " ".join(second)
    assert second[-1].count("udp://127.0.0.1:") == 2
    camera._stop_cam_mux()


def test_a_failure_keeps_ffmpegs_reason(monkeypatch):
    _patch(monkeypatch, [(False, b"no mjpeg"), (False, b"/dev/video0: Device or resource busy")])
    assert camera._start_cam_mux(0, 2) is False
    assert "Device or resource busy" in camera.cam_mux_last_error()

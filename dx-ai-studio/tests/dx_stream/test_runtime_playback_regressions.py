import io
import sys
from pathlib import Path

import dx_stream.core as _dx_stream_core


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dx_stream"))


def _install_fake_mjpeg(monkeypatch, name="fake_mjpeg_mod"):
    """Install a fresh empty fake ``mjpeg`` module so a test can stub individual
    functions on it.

    Now that server.py imports the module qualified (``from dx_stream.core import
    mjpeg`` / ``from dx_stream.core.mjpeg import ...``), interception requires BOTH:
      * the sys.modules["dx_stream.core.mjpeg"] entry — feeds
        ``from dx_stream.core.mjpeg import name``; and
      * the ``mjpeg`` attribute on the already-imported ``dx_stream.core`` package
        object — feeds ``from dx_stream.core import mjpeg`` (Python binds the parent
        package's existing attribute and never consults sys.modules for it).
    Patching only sys.modules (the pre-qualification behavior) silently misses the
    second form. Both are monkeypatched so they auto-revert after the test.
    """
    fake = type(sys)(name)
    monkeypatch.setitem(sys.modules, "dx_stream.core.mjpeg", fake)
    monkeypatch.setattr(_dx_stream_core, "mjpeg", fake)
    return fake


def test_pipeline_config_file_paths_are_resolved_from_configs_dir(tmp_path, monkeypatch):
    from core import config
    from core.pipeline import pipeline_json_to_gst

    cfg = tmp_path / "configs" / "DemoConfig" / "preprocess_config.json"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("{}")
    monkeypatch.setattr(config, "CONFIGS_DIR", tmp_path / "configs")

    gst = pipeline_json_to_gst({
        "nodes": [
            {
                "id": "pre",
                "type": "DxPreprocess",
                "props": {"config-file-path": "DemoConfig/preprocess_config.json"},
            }
        ],
        "edges": [],
    })

    assert f"config-file-path={cfg}" in gst


def test_demo_entries_include_default_video_uri_for_pipeline_presets():
    from core import demos

    entries = demos.list_demo_entries()

    assert entries
    assert entries[0]["default_video"].startswith("file://")


def test_mjpeg_start_drains_dxrt_message_queues_before_subprocess(monkeypatch):
    from core import mjpeg

    calls = []

    class FakeProc:
        pid = 12345

    class FakeThread:
        def __init__(self, target=None, daemon=None):
            self.target = target
            self.daemon = daemon

        def start(self):
            calls.append("thread")

    def fake_spawn(_cmd, _env):
        calls.append("spawn")
        return FakeProc()

    monkeypatch.setattr(mjpeg, "stop", lambda: calls.append("stop"))
    monkeypatch.setattr(mjpeg, "_drain_dxrt_msgqueues", lambda: calls.append("drain"), raising=False)
    monkeypatch.setattr(mjpeg, "_spawn_process", fake_spawn)
    monkeypatch.setattr(mjpeg.threading, "Thread", FakeThread)

    mjpeg.start("videotestsrc ! fakesink")

    assert calls[:3] == ["stop", "drain", "spawn"]


def test_mjpeg_wait_until_ready_reports_early_subprocess_failure(monkeypatch):
    from core import mjpeg

    class FailedProc:
        returncode = 255

        def poll(self):
            return self.returncode

        stderr = io.BytesIO(b"dxrt service is not running")

    monkeypatch.setattr(mjpeg, "_process", FailedProc())
    monkeypatch.setattr(mjpeg, "_streaming", True)
    monkeypatch.setattr(mjpeg, "_latest_frame", None)

    ready, error = mjpeg.wait_until_ready(timeout=0.01)

    assert ready is False
    assert "dxrt service is not running" in error
    assert mjpeg.is_streaming() is False


def test_mjpeg_wait_until_ready_can_require_first_frame(monkeypatch):
    from core import mjpeg

    class RunningProc:
        def poll(self):
            return None

    monkeypatch.setattr(mjpeg, "_process", RunningProc())
    monkeypatch.setattr(mjpeg, "_streaming", True)
    monkeypatch.setattr(mjpeg, "_latest_frame", None)
    monkeypatch.setattr(mjpeg, "_last_error", "")

    ready, error = mjpeg.wait_until_ready(timeout=0.01, require_frame=True)

    assert ready is False
    assert "No MJPEG frame produced" in error


def test_mjpeg_reader_preserves_specific_error_from_wait_until_ready(monkeypatch):
    from core import mjpeg

    class FailedProc:
        returncode = 255
        stdout = io.BytesIO(b"")
        stderr = io.BytesIO(b"")

        def poll(self):
            return self.returncode

    monkeypatch.setattr(mjpeg, "_process", FailedProc())
    monkeypatch.setattr(mjpeg, "_streaming", True)
    monkeypatch.setattr(mjpeg, "_last_error", "dxrt service is not running")
    monkeypatch.setattr(mjpeg, "_read_frames_from", lambda _proc: None)

    mjpeg._read_frames_loop()

    assert mjpeg.get_last_error() == "dxrt service is not running"




def test_webrtc_sink_uses_detected_encoder_and_sendrecv_name():
    from core.pipeline import get_webrtc_sink_str

    sink = get_webrtc_sink_str({
        "encoder": "x264enc tune=zerolatency",
        "payloader": "rtph264pay config-interval=-1",
        "payload_type": 96,
    })

    assert "videoconvert ! x264enc tune=zerolatency ! rtph264pay config-interval=-1 pt=96" in sink
    assert "webrtcbin name=sendrecv" in sink
    # No public STUN server: the board is air-gapped, so stun.l.google.com is unreachable and
    # its failed gathering stalls ICE (error 701). Same-LAN host candidates connect without it.
    assert "stun-server" not in sink


def test_demo_webrtc_sink_uses_browser_payload_type_before_pipeline_start():
    from core import demos

    sink = demos._get_sink({
        "encoder": "vp8enc deadline=1",
        "payloader": "rtpvp8pay",
        "payload_type": 120,
    })

    assert "vp8enc deadline=1 ! rtpvp8pay pt=120 ! webrtcbin" in sink


def test_server_applies_browser_payload_type_to_detected_encoder():
    import server

    encoder = {
        "encoder": "vp8enc deadline=1",
        "payloader": "rtpvp8pay",
        "encoding_name": "VP8",
        "payload_type": 96,
    }

    adjusted = server._apply_webrtc_payload_types(encoder, {"VP8": 120})

    assert adjusted["payload_type"] == 120
    assert encoder["payload_type"] == 96


def test_pipeline_manager_exposes_initial_error_waiter():
    from core.pipeline import PipelineManager

    mgr = PipelineManager()
    assert mgr.wait_for_initial_error(timeout=0.01) is None
    mgr._last_error = "bus failed"
    assert mgr.wait_for_initial_error(timeout=0.01) == "bus failed"


def test_pipeline_manager_start_source_checks_immediate_failure():
    source = (ROOT / "dx_stream" / "core" / "pipeline.py").read_text(encoding="utf-8")

    assert "self._last_error = None" in source
    assert "Gst.StateChangeReturn.FAILURE" in source
    assert "wait_for_initial_error" in source


def test_webrtc_start_failure_is_logged_before_fallback(monkeypatch, caplog):
    monkeypatch.setenv("DX_STREAM_WEBRTC", "1")  # webrtc is opt-in; enable for this test
    import logging
    import server

    class FakePipelineMgr:
        def start(self, pipeline, extra_env=None):
            raise RuntimeError("encoder missing")
        def stop(self):
            pass

    monkeypatch.setattr(server, "_pipeline_mgr", FakePipelineMgr())
    monkeypatch.setattr(server, "_webrtc_handler", object())
    monkeypatch.setattr(server, "_check_webrtc_available", lambda: True)

    with caplog.at_level(logging.WARNING):
        assert server._try_start_webrtc_pipeline("videotestsrc ! webrtcbin name=sendrecv") is None

    assert any(
        "WebRTC pipeline start failed" in message and "encoder missing" in message
        for message in caplog.messages
    )


def test_webrtc_start_uses_responsive_initial_error_window(monkeypatch):
    monkeypatch.setenv("DX_STREAM_WEBRTC", "1")  # webrtc is opt-in; enable for this test
    import server

    observed_timeouts = []

    class FakePipelineMgr:
        def start(self, pipeline, extra_env=None):
            return "webrtc-id"
        def get_webrtcbin(self):
            return object()
        def wait_for_initial_error(self, timeout=1.0):
            observed_timeouts.append(timeout)
            return None
        def stop(self):
            pass

    monkeypatch.setattr(server, "_pipeline_mgr", FakePipelineMgr())
    monkeypatch.setattr(server, "_webrtc_handler", object())
    monkeypatch.setattr(server, "_check_webrtc_available", lambda: True)

    assert server._try_start_webrtc_pipeline("videotestsrc ! webrtcbin name=sendrecv") == "webrtc-id"
    assert observed_timeouts
    assert 0 < observed_timeouts[0] <= 0.3




def test_demo_start_uses_webrtc_pipeline_without_mjpeg_conversion(monkeypatch):
    monkeypatch.setenv("DX_STREAM_WEBRTC", "1")  # webrtc is opt-in; enable for this test
    import server

    calls = []

    class FakePipelineMgr:
        def start(self, pipeline, extra_env=None):
            calls.append(("pipeline_start", pipeline, extra_env))
            return "webrtc-id"
        def get_webrtcbin(self):
            return object()
        def get_last_error(self):
            return None
        def wait_for_initial_error(self, timeout=1.0):
            return None
        def stop(self):
            calls.append(("pipeline_stop",))

    class FakeMjpeg:
        def stop(self):
            calls.append(("mjpeg_stop",))
        def build_mjpeg_pipeline(self, _pipeline):
            raise AssertionError("WebRTC success path must not build MJPEG pipeline")

    monkeypatch.setattr(server, "_pipeline_mgr", FakePipelineMgr())
    monkeypatch.setattr(server, "_webrtc_handler", object())
    monkeypatch.setattr(server, "_check_webrtc_available", lambda: True)
    monkeypatch.setattr(server, "demos", type(sys)("fake_demos"))
    server.demos.build_pipeline_str = lambda *_args, **_kwargs: "videotestsrc ! webrtcbin name=sendrecv"
    server.demos.DEMOS = [{"name": "test"}]
    _install_fake_mjpeg(monkeypatch, "fake_mjpeg")
    sys.modules["dx_stream.core.mjpeg"].stop = FakeMjpeg().stop
    sys.modules["dx_stream.core.mjpeg"].build_mjpeg_pipeline = FakeMjpeg().build_mjpeg_pipeline

    sent = {}
    handler = object.__new__(server.DXStreamHandler)
    handler._safe_read_json = lambda: {}
    handler.send_json = lambda payload, code=200: sent.update(payload=payload, code=code)
    handler._error = lambda code, error, message, detail="": sent.update(payload={"error": error, "message": message}, code=code)

    handler._handle_demo_start("/api/demos/0/start")

    assert sent["payload"]["output_mode"] == "webrtc"
    assert sent["payload"]["pipeline_id"] == "webrtc-id"
    assert ("pipeline_stop",) in calls
    assert ("mjpeg_stop",) in calls
    assert any(c[0] == "pipeline_start" and "webrtcbin name=sendrecv" in c[1] for c in calls)


def test_demo_start_falls_back_to_mjpeg_when_webrtc_start_fails(monkeypatch):
    import server

    calls = []
    lock_depths = []
    original_pipeline = "videotestsrc ! webrtcbin name=sendrecv"
    mjpeg_pipeline = "videotestsrc ! jpegenc ! fdsink fd=1"

    class FakePlaybackLock:
        def __init__(self):
            self.depth = 0
        def __enter__(self):
            self.depth += 1
            return self
        def __exit__(self, exc_type, exc, tb):
            self.depth -= 1

    class FakePipelineMgr:
        def start(self, pipeline, extra_env=None):
            calls.append(("pipeline_start", pipeline, extra_env))
            raise RuntimeError("webrtc failed")
        def stop(self):
            calls.append(("pipeline_stop",))

    class FakeMjpeg:
        def stop(self):
            calls.append(("mjpeg_stop",))
        def build_mjpeg_pipeline(self, pipeline):
            calls.append(("build_mjpeg", pipeline))
            return mjpeg_pipeline
        def start(self, pipeline, extra_env=None):
            lock_depths.append(playback_lock.depth)
            calls.append(("mjpeg_start", pipeline, extra_env))
        def wait_until_ready(self, timeout=5.0, require_frame=True):
            calls.append(("mjpeg_ready", timeout, require_frame))
            return True, ""

    playback_lock = FakePlaybackLock()
    monkeypatch.setattr(server, "_playback_lock", playback_lock, raising=False)
    monkeypatch.setattr(server, "_pipeline_mgr", FakePipelineMgr())
    monkeypatch.setattr(server, "_webrtc_handler", object())
    monkeypatch.setattr(server, "_check_webrtc_available", lambda: True)
    monkeypatch.setattr(server, "demos", type(sys)("fake_demos"))
    server.demos.build_pipeline_str = lambda *_args, **_kwargs: original_pipeline
    server.demos.DEMOS = [{"name": "test"}]
    fake_mjpeg = FakeMjpeg()
    _install_fake_mjpeg(monkeypatch)
    sys.modules["dx_stream.core.mjpeg"].stop = fake_mjpeg.stop
    sys.modules["dx_stream.core.mjpeg"].build_mjpeg_pipeline = fake_mjpeg.build_mjpeg_pipeline
    sys.modules["dx_stream.core.mjpeg"].start = fake_mjpeg.start
    sys.modules["dx_stream.core.mjpeg"].wait_until_ready = fake_mjpeg.wait_until_ready

    sent = {}
    handler = object.__new__(server.DXStreamHandler)
    handler._safe_read_json = lambda: {}
    handler.send_json = lambda payload, code=200: sent.update(payload=payload, code=code)
    handler._error = lambda code, error, message, detail="": sent.update(payload={"error": error, "message": message}, code=code)

    handler._handle_demo_start("/api/demos/0/start")

    assert sent["payload"]["output_mode"] == "mjpeg"
    assert server._current_output_mode == "mjpeg"
    assert server._current_pipeline_id == "mjpeg-demo-0"
    assert ("build_mjpeg", original_pipeline) in calls
    assert ("mjpeg_start", mjpeg_pipeline, None) in calls
    # MJPEG first-frame timeout was raised 5.0 -> 15.0 for slow ARM boards (commit 754631f).
    assert ("mjpeg_ready", 15.0, True) in calls
    assert lock_depths and lock_depths[0] > 0




import pytest


@pytest.mark.parametrize(
    ("source_pipeline", "expected_present", "expected_absent"),
    [
        ("videotestsrc", "webrtcbin name=sendrecv", None),
        ("videotestsrc ! fpsdisplaysink sync=false", "webrtcbin name=sendrecv", "fpsdisplaysink"),
        ("videotestsrc ! videoconvert ! vp8enc deadline=1 ! rtpvp8pay ! webrtcbin name=sendrecv", "webrtcbin name=sendrecv", None),
    ],
)
def test_pipeline_run_uses_webrtc_for_sink_cases(monkeypatch, source_pipeline, expected_present, expected_absent):
    monkeypatch.setenv("DX_STREAM_WEBRTC", "1")  # webrtc is opt-in; enable for this test
    import server

    calls = []

    class FakePipelineMgr:
        def start(self, pipeline, extra_env=None):
            calls.append(("pipeline_start", pipeline, extra_env))
            return "webrtc-pipeline-id"
        def get_webrtcbin(self):
            return object()
        def get_last_error(self):
            return None
        def wait_for_initial_error(self, timeout=1.0):
            return None
        def stop(self):
            calls.append(("pipeline_stop",))

    class FakeMjpeg:
        def stop(self):
            calls.append(("mjpeg_stop",))
        def build_mjpeg_pipeline(self, _pipeline):
            raise AssertionError("WebRTC success path must not build MJPEG pipeline")

    monkeypatch.setattr(server, "_pipeline_mgr", FakePipelineMgr())
    monkeypatch.setattr(server, "_webrtc_handler", object())
    monkeypatch.setattr(server, "_check_webrtc_available", lambda: True)
    monkeypatch.setattr(server, "pipeline_json_to_gst", lambda _body: source_pipeline)
    monkeypatch.setattr(server, "detect_encoder", lambda: {
        "encoder": "vp8enc deadline=1",
        "payloader": "rtpvp8pay",
    })
    fake_mjpeg = FakeMjpeg()
    _install_fake_mjpeg(monkeypatch)
    sys.modules["dx_stream.core.mjpeg"].stop = fake_mjpeg.stop
    sys.modules["dx_stream.core.mjpeg"].build_mjpeg_pipeline = fake_mjpeg.build_mjpeg_pipeline

    sent = {}
    handler = object.__new__(server.DXStreamHandler)
    handler._safe_read_json = lambda: {"nodes": [], "edges": []}
    handler.send_json = lambda payload, code=200: sent.update(payload=payload, code=code)
    handler._error = lambda code, error, message, detail="": sent.update(payload={"error": error, "message": message}, code=code)

    handler._handle_pipeline_run()

    assert sent["payload"]["output_mode"] == "webrtc"
    started = [c for c in calls if c[0] == "pipeline_start"][0][1]
    assert expected_present in started
    if expected_absent:
        assert expected_absent not in started


def test_pipeline_run_falls_back_to_mjpeg_when_webrtc_start_fails(monkeypatch):
    import server

    calls = []

    class FakePipelineMgr:
        def start(self, pipeline, extra_env=None):
            calls.append(("pipeline_start", pipeline, extra_env))
            raise RuntimeError("webrtc failed")
        def stop(self):
            calls.append(("pipeline_stop",))

    class FakeMjpeg:
        def stop(self):
            calls.append(("mjpeg_stop",))
        def build_mjpeg_pipeline(self, pipeline):
            calls.append(("build_mjpeg", pipeline))
            return "videotestsrc ! jpegenc ! fdsink fd=1"
        def start(self, pipeline, extra_env=None):
            calls.append(("mjpeg_start", pipeline, extra_env))
        def wait_until_ready(self, timeout=5.0, require_frame=True):
            calls.append(("mjpeg_ready", timeout, require_frame))
            return True, ""
        def get_sink_str(self):
            return "jpegenc ! fdsink fd=1"

    monkeypatch.setattr(server, "_pipeline_mgr", FakePipelineMgr())
    monkeypatch.setattr(server, "_webrtc_handler", object())
    monkeypatch.setattr(server, "_check_webrtc_available", lambda: True)
    # Use a pipeline with fpsdisplaysink so build_mjpeg_pipeline is used
    monkeypatch.setattr(server, "pipeline_json_to_gst", lambda _body: "videotestsrc ! fpsdisplaysink sync=false")
    monkeypatch.setattr(server, "detect_encoder", lambda: {
        "encoder": "vp8enc deadline=1",
        "payloader": "rtpvp8pay",
    })
    fake_mjpeg = FakeMjpeg()
    _install_fake_mjpeg(monkeypatch)
    sys.modules["dx_stream.core.mjpeg"].stop = fake_mjpeg.stop
    sys.modules["dx_stream.core.mjpeg"].build_mjpeg_pipeline = fake_mjpeg.build_mjpeg_pipeline
    sys.modules["dx_stream.core.mjpeg"].start = fake_mjpeg.start
    sys.modules["dx_stream.core.mjpeg"].wait_until_ready = fake_mjpeg.wait_until_ready
    sys.modules["dx_stream.core.mjpeg"].get_sink_str = fake_mjpeg.get_sink_str

    sent = {}
    handler = object.__new__(server.DXStreamHandler)
    handler._safe_read_json = lambda: {"nodes": [], "edges": []}
    handler.send_json = lambda payload, code=200: sent.update(payload=payload, code=code)
    handler._error = lambda code, error, message, detail="": sent.update(payload={"error": error, "message": message}, code=code)

    handler._handle_pipeline_run()

    assert sent["payload"]["output_mode"] == "mjpeg"
    assert server._current_output_mode == "mjpeg"
    assert server._current_pipeline_id == "mjpeg-pipeline"
    assert any(c[0] == "build_mjpeg" for c in calls)
    assert any(c[0] == "mjpeg_start" for c in calls)


def test_pipeline_run_logs_ineligible_sink_without_webrtc_unavailable(monkeypatch, caplog):
    import logging
    import server

    class FakePipelineMgr:
        def stop(self):
            pass

    class FakeMjpeg:
        def stop(self):
            pass
        def start(self, pipeline, extra_env=None):
            pass
        def wait_until_ready(self, timeout=5.0, require_frame=True):
            return True, ""
        def get_sink_str(self):
            return "jpegenc ! fdsink fd=1"
        def build_mjpeg_pipeline(self, pipeline):
            raise AssertionError("Ineligible sink fallback must preserve the pipeline")

    monkeypatch.setattr(server, "_pipeline_mgr", FakePipelineMgr())
    monkeypatch.setattr(server, "_webrtc_handler", object())
    monkeypatch.setattr(server, "_check_webrtc_available", lambda: True)
    monkeypatch.setattr(server, "pipeline_json_to_gst", lambda _body: "videotestsrc ! fakesink")
    monkeypatch.setattr(server, "detect_encoder", lambda: {
        "encoder": "vp8enc deadline=1",
        "payloader": "rtpvp8pay",
    })
    fake_mjpeg = FakeMjpeg()
    _install_fake_mjpeg(monkeypatch)
    sys.modules["dx_stream.core.mjpeg"].stop = fake_mjpeg.stop
    sys.modules["dx_stream.core.mjpeg"].start = fake_mjpeg.start
    sys.modules["dx_stream.core.mjpeg"].wait_until_ready = fake_mjpeg.wait_until_ready
    sys.modules["dx_stream.core.mjpeg"].get_sink_str = fake_mjpeg.get_sink_str
    sys.modules["dx_stream.core.mjpeg"].build_mjpeg_pipeline = fake_mjpeg.build_mjpeg_pipeline

    sent = {}
    handler = object.__new__(server.DXStreamHandler)
    handler._safe_read_json = lambda: {"nodes": [], "edges": []}
    handler.send_json = lambda payload, code=200: sent.update(payload=payload, code=code)
    handler._error = lambda code, error, message, detail="": sent.update(payload={"error": error, "message": message}, code=code)

    with caplog.at_level(logging.INFO):
        handler._handle_pipeline_run()

    assert sent["payload"]["output_mode"] == "mjpeg"
    assert any("no WebRTC-eligible sink" in message for message in caplog.messages)
    assert not any("WebRTC unavailable" in message for message in caplog.messages)




def test_demo_stop_stops_webrtc_and_mjpeg_backends(monkeypatch):
    import server
    calls = []

    class FakePipelineMgr:
        def stop(self):
            calls.append("pipeline_stop")

    class FakeMjpeg:
        def stop(self):
            calls.append("mjpeg_stop")

    monkeypatch.setattr(server, "_pipeline_mgr", FakePipelineMgr())
    fake_mjpeg = FakeMjpeg()
    _install_fake_mjpeg(monkeypatch)
    sys.modules["dx_stream.core.mjpeg"].stop = fake_mjpeg.stop

    sent = {}
    handler = object.__new__(server.DXStreamHandler)
    handler.send_json = lambda payload, code=200: sent.update(payload=payload, code=code)
    handler._error = lambda code, error, message, detail="": sent.update(payload={"error": error, "message": message}, code=code)
    handler._handle_demo_stop("/api/demos/0/stop")

    assert "pipeline_stop" in calls
    assert "mjpeg_stop" in calls
    assert sent["payload"]["stopped"] is True


def test_pipeline_stop_stops_webrtc_and_mjpeg_backends(monkeypatch):
    import server
    calls = []

    class FakePipelineMgr:
        def stop(self):
            calls.append("pipeline_stop")

    class FakeMjpeg:
        def stop(self):
            calls.append("mjpeg_stop")

    monkeypatch.setattr(server, "_pipeline_mgr", FakePipelineMgr())
    fake_mjpeg = FakeMjpeg()
    _install_fake_mjpeg(monkeypatch)
    sys.modules["dx_stream.core.mjpeg"].stop = fake_mjpeg.stop

    sent = {}
    handler = object.__new__(server.DXStreamHandler)
    handler.send_json = lambda payload, code=200: sent.update(payload=payload, code=code)
    handler._handle_pipeline_stop()

    assert "pipeline_stop" in calls
    assert "mjpeg_stop" in calls
    assert sent["payload"]["stopped"] is True


def test_pipeline_stop_sends_response_while_holding_playback_lock(monkeypatch):
    import server

    class FakePlaybackLock:
        def __init__(self):
            self.depth = 0
        def __enter__(self):
            self.depth += 1
            return self
        def __exit__(self, exc_type, exc, tb):
            self.depth -= 1

    class FakePipelineMgr:
        def stop(self):
            pass

    class FakeMjpeg:
        def stop(self):
            pass

    playback_lock = FakePlaybackLock()
    monkeypatch.setattr(server, "_playback_lock", playback_lock, raising=False)
    monkeypatch.setattr(server, "_pipeline_mgr", FakePipelineMgr())
    fake_mjpeg = FakeMjpeg()
    _install_fake_mjpeg(monkeypatch)
    sys.modules["dx_stream.core.mjpeg"].stop = fake_mjpeg.stop

    observed_depths = []
    handler = object.__new__(server.DXStreamHandler)
    handler.send_json = lambda payload, code=200: observed_depths.append(playback_lock.depth)

    handler._handle_pipeline_stop()

    assert observed_depths == [1]

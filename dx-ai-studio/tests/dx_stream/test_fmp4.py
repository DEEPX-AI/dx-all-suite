"""fMP4 (H264-over-HTTP) streaming module — box parsing + pipeline building."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dx_stream"))


def _box(btype: bytes, payload: bytes = b"") -> bytes:
    return struct.pack(">I", 8 + len(payload)) + btype + payload


def test_iter_boxes_parses_and_leaves_partial_tail():
    from core import fmp4
    stream = _box(b"ftyp", b"isom") + _box(b"moov", b"\x00" * 20) + _box(b"moof", b"a") + _box(b"mdat", b"bb")
    partial = stream + b"\x00\x00\x00\x40mdat"  # incomplete final box
    buf = bytearray(partial)
    boxes = list(fmp4._iter_boxes(buf))
    assert [t for t, _ in boxes] == [b"ftyp", b"moov", b"moof", b"mdat"]
    # incomplete tail must stay in the buffer for the next read
    assert bytes(buf) == b"\x00\x00\x00\x40mdat"


def test_iter_boxes_handles_64bit_largesize():
    from core import fmp4
    payload = b"x" * 4
    largebox = struct.pack(">I", 1) + b"mdat" + struct.pack(">Q", 16 + len(payload)) + payload
    buf = bytearray(largebox)
    boxes = list(fmp4._iter_boxes(buf))
    assert len(boxes) == 1 and boxes[0][0] == b"mdat"
    assert len(buf) == 0


def test_get_sink_str_muxes_h264_fragmented_mp4():
    from core import fmp4
    sink = fmp4.get_sink_str()
    assert "h264" in sink.lower()  # mpph264enc or x264enc
    assert "mp4mux" in sink and "fragment-duration" in sink and "streamable=true" in sink
    assert "fdsink" in sink
    # No width/height caps (SIGSEGVs the dxosd path) — same rule as the MJPEG sink.
    assert "width=" not in sink and "height=" not in sink


def test_build_fmp4_pipeline_replaces_sink_after_dxosd():
    from core import fmp4
    base = ("urisourcebin uri=file:///v.mp4 ! decodebin ! dxpreprocess ! dxinfer ! "
            "dxpostprocess ! dxosd ! videoconvert ! webrtcbin name=sendrecv")
    out = fmp4.build_fmp4_pipeline(base)
    assert "dxosd" in out                # inference chain preserved
    assert "webrtcbin" not in out        # original sink removed
    assert "mp4mux" in out               # fMP4 sink appended


def test_fmp4_subprocess_receives_augmented_plugin_environment(monkeypatch):
    from core import fmp4

    calls = []
    captured = {}

    class FakeGstEnv:
        @staticmethod
        def augmented_env(base):
            calls.append(dict(base))
            env = dict(base)
            env["GST_PLUGIN_PATH"] = "/plugins"
            return env

    class FakeProcess:
        pid = 1234

    class NoopThread:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            return None

    monkeypatch.setattr(fmp4, "gst_env", FakeGstEnv, raising=False)
    monkeypatch.setattr(fmp4, "stop", lambda: None)
    monkeypatch.setattr(fmp4, "_streaming", False)
    monkeypatch.setattr(fmp4, "_process", None)
    monkeypatch.setattr(fmp4, "_reader_thread", None)
    monkeypatch.setattr(
        fmp4,
        "_spawn_process",
        lambda command, env: captured.update(command=command, env=env) or FakeProcess(),
    )
    monkeypatch.setattr(fmp4.threading, "Thread", NoopThread)

    fmp4.start("videotestsrc ! fakesink", extra_env={"PIPELINE_FLAG": "1"})

    assert calls
    assert calls[0]["PIPELINE_FLAG"] == "1"
    assert captured["env"]["GST_PLUGIN_PATH"] == "/plugins"

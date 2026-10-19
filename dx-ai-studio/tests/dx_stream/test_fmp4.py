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


# ── Box parsing edge cases ──────────────────────────────────────────────────

import queue as _queue  # noqa: E402
import pytest  # noqa: E402


def _box64(btype: bytes, payload: bytes = b"") -> bytes:
    """A 64-bit (largesize) box: size==1, real length in the 8 bytes after the type."""
    return struct.pack(">I", 1) + btype + struct.pack(">Q", 16 + len(payload)) + payload


def test_iter_boxes_stops_on_size_zero_box():
    """size==0 means "extends to EOF". mp4mux streamable=true never emits one, so
    treating it as a complete box would mis-frame everything after it — the parser
    must stop and wait for more bytes instead."""
    from core import fmp4

    buf = bytearray(struct.pack(">I", 0) + b"mdat" + b"tail")
    assert list(fmp4._iter_boxes(buf)) == []
    assert bytes(buf).startswith(struct.pack(">I", 0)), "the box must stay buffered"


def test_iter_boxes_stops_on_size_smaller_than_header():
    """A size below the 8-byte header is corrupt; consuming it would loop forever."""
    from core import fmp4

    buf = bytearray(struct.pack(">I", 4) + b"moof" + b"junk")
    assert list(fmp4._iter_boxes(buf)) == []
    assert len(buf) == 12, "nothing may be consumed from a corrupt box"


def test_iter_boxes_waits_for_a_truncated_largesize_header():
    from core import fmp4

    buf = bytearray(struct.pack(">I", 1) + b"mdat" + b"\x00\x00")  # 64-bit len cut short
    assert list(fmp4._iter_boxes(buf)) == []
    assert len(buf) == 10


def test_iter_boxes_consumes_only_complete_boxes():
    from core import fmp4

    complete = _box(b"moof", b"a" * 4)
    partial = _box(b"mdat", b"b" * 100)[:20]
    buf = bytearray(complete + partial)
    got = [t for t, _ in fmp4._iter_boxes(buf)]
    assert got == [b"moof"]
    assert bytes(buf) == partial


def test_iter_boxes_mixes_32_and_64_bit_boxes():
    from core import fmp4

    buf = bytearray(_box(b"ftyp", b"x") + _box64(b"mdat", b"y" * 3) + _box(b"moof"))
    assert [t for t, _ in fmp4._iter_boxes(buf)] == [b"ftyp", b"mdat", b"moof"]
    assert buf == bytearray()


# ── Encoder selection ───────────────────────────────────────────────────────


@pytest.fixture()
def fresh_encoder(monkeypatch):
    """Clear the module-level encoder cache so each test re-detects."""
    from core import fmp4

    monkeypatch.setattr(fmp4, "_H264_ENCODER", None)
    return fmp4


def test_hardware_encoder_is_preferred_when_available(fresh_encoder, monkeypatch):
    fmp4 = fresh_encoder
    monkeypatch.setattr(fmp4.subprocess, "run",
                        lambda *a, **k: type("R", (), {"returncode": 0})())
    enc = fmp4._h264_encoder()
    assert enc.startswith("mpph264enc")
    # The bitrate cap is the whole point of this path — it must fit an SSH tunnel.
    assert "bps=3000000" in enc


def test_software_encoder_when_hardware_is_absent(fresh_encoder, monkeypatch):
    fmp4 = fresh_encoder
    monkeypatch.setattr(fmp4.subprocess, "run",
                        lambda *a, **k: type("R", (), {"returncode": 1})())
    assert fresh_encoder._h264_encoder().startswith("x264enc")


def test_encoder_detection_failure_falls_back_to_software(fresh_encoder, monkeypatch):
    """gst-inspect missing entirely must not crash the stream setup."""
    fmp4 = fresh_encoder

    def _boom(*a, **k):
        raise FileNotFoundError("gst-inspect-1.0")

    monkeypatch.setattr(fmp4.subprocess, "run", _boom)
    assert fmp4._h264_encoder().startswith("x264enc")


def test_encoder_result_is_cached(fresh_encoder, monkeypatch):
    fmp4 = fresh_encoder
    calls = []
    monkeypatch.setattr(fmp4.subprocess, "run",
                        lambda *a, **k: (calls.append(1), type("R", (), {"returncode": 0})())[1])
    fmp4._h264_encoder()
    fmp4._h264_encoder()
    assert len(calls) == 1, "gst-inspect must be probed once, not per stream"


# ── Pipeline rewriting ──────────────────────────────────────────────────────


def test_build_fmp4_pipeline_cuts_after_the_compositor_for_multi_stream():
    from core import fmp4

    base = ("dxpreprocess ! dxinfer ! compositor name=c sink_0::xpos=0 ! "
            "videoconvert ! fpsdisplaysink")
    out = fmp4.build_fmp4_pipeline(base)
    assert "compositor name=c sink_0::xpos=0" in out
    assert "fpsdisplaysink" not in out
    assert out.endswith("fdsink fd=1")


def test_build_fmp4_pipeline_cuts_after_the_last_dxosd():
    from core import fmp4

    base = "dxpreprocess ! dxosd ! queue ! dxosd ! videoconvert ! webrtcbin name=x"
    out = fmp4.build_fmp4_pipeline(base)
    assert out.count("dxosd") == 2, "both dxosd stages are kept"
    assert "webrtcbin" not in out
    assert out.endswith("fdsink fd=1")


def test_build_fmp4_pipeline_appends_when_no_marker_matches():
    from core import fmp4

    out = fmp4.build_fmp4_pipeline("videotestsrc ! videoconvert")
    assert out.startswith("videotestsrc ! videoconvert")
    assert out.endswith("fdsink fd=1")
    assert " !  ! " not in out, "no doubled separator when appending"


def test_split_pipeline_expands_bare_separators():
    from core import fmp4

    parts = fmp4._split_pipeline("a ! b prop=1!c")
    assert "!" in parts
    assert "b" in parts and "prop=1" in parts and "c" in parts


# ── The read loop: init capture + fragment broadcast ────────────────────────


class _FakeProc:
    """Feeds canned chunks, then EOF. poll() stays None while chunks remain."""

    def __init__(self, chunks):
        self._chunks = list(chunks)
        self.stdout = self

    def read(self, _n):
        return self._chunks.pop(0) if self._chunks else b""

    def poll(self):
        return None


@pytest.fixture()
def reader(monkeypatch):
    """Isolate the module's streaming globals for one _read_from run."""
    from core import fmp4

    monkeypatch.setattr(fmp4, "_streaming", True)
    monkeypatch.setattr(fmp4, "_init_segment", None)
    monkeypatch.setattr(fmp4, "_fragment_count", 0)
    monkeypatch.setattr(fmp4, "_subscribers", [])
    return fmp4


def test_read_from_captures_ftyp_plus_moov_as_the_init_segment(reader):
    """MSE refuses to start without ftyp+moov, so mis-assembling it means a
    permanently black player with no error."""
    fmp4 = reader
    ftyp, moov = _box(b"ftyp", b"isom"), _box(b"moov", b"m")
    fmp4._read_from(_FakeProc([ftyp + moov]))
    assert fmp4._init_segment == ftyp + moov
    assert fmp4.has_init() is True


def test_boxes_before_moov_stay_with_the_init_segment(reader):
    fmp4 = reader
    ftyp, free, moov = _box(b"ftyp"), _box(b"free", b"pad"), _box(b"moov")
    fmp4._read_from(_FakeProc([ftyp + free + moov]))
    assert fmp4._init_segment == ftyp + free + moov


def test_a_fragment_completes_at_its_mdat(reader):
    fmp4 = reader
    q = _queue.Queue(maxsize=4)
    fmp4._subscribers.append(q)
    moof, mdat = _box(b"moof", b"f"), _box(b"mdat", b"d")
    fmp4._read_from(_FakeProc([_box(b"ftyp") + _box(b"moov") + moof + mdat]))
    assert q.get_nowait() == moof + mdat
    assert fmp4.get_fragment_count() == 1


def test_moof_without_mdat_is_not_broadcast_yet(reader):
    """Emitting a moof alone would hand MSE a fragment with no media data."""
    fmp4 = reader
    q = _queue.Queue(maxsize=4)
    fmp4._subscribers.append(q)
    fmp4._read_from(_FakeProc([_box(b"ftyp") + _box(b"moov") + _box(b"moof")]))
    assert q.empty() and fmp4.get_fragment_count() == 0


def test_a_new_ftyp_restarts_the_init_segment(reader):
    """The pipeline auto-restarts to loop the sample video; the second ftyp must
    replace the init segment rather than append to the old one."""
    fmp4 = reader
    first = _box(b"ftyp", b"one") + _box(b"moov", b"1")
    second = _box(b"ftyp", b"two") + _box(b"moov", b"2")
    fmp4._read_from(_FakeProc([first, second]))
    assert fmp4._init_segment == second


def test_boxes_split_across_chunks_are_reassembled(reader):
    """65536-byte reads cut boxes arbitrarily; a fragment must not be lost at a
    chunk boundary."""
    fmp4 = reader
    q = _queue.Queue(maxsize=4)
    fmp4._subscribers.append(q)
    stream = _box(b"ftyp") + _box(b"moov") + _box(b"moof", b"x" * 40) + _box(b"mdat", b"y" * 40)
    fmp4._read_from(_FakeProc([stream[:20], stream[20:57], stream[57:]]))
    assert fmp4.get_fragment_count() == 1
    assert q.get_nowait() == _box(b"moof", b"x" * 40) + _box(b"mdat", b"y" * 40)


def test_slow_subscriber_drops_its_oldest_fragment(reader):
    """A client that stops reading must not stall the stream for everyone else."""
    fmp4 = reader
    q = _queue.Queue(maxsize=1)
    q.put_nowait(b"stale")
    fmp4._subscribers.append(q)
    fmp4._broadcast_fragment(b"fresh")
    assert q.get_nowait() == b"fresh", "the newest fragment wins the single slot"


def test_broadcast_counts_even_with_no_subscribers(reader):
    fmp4 = reader
    fmp4._broadcast_fragment(b"x")
    assert fmp4.get_fragment_count() == 1

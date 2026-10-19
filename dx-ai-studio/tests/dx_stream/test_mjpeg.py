"""MJPEG streaming module — JPEG framing, encoder choice, pipeline rewriting.

The reader turns a raw byte stream from gst-launch's stdout into whole JPEGs by
scanning for SOI/EOI markers. It is wrapped in a bare `except Exception` that only
logs, so a framing regression does not raise — the viewer just goes black or shows
torn frames. That is what these tests pin.
"""
import struct  # noqa: F401 - kept for symmetry with test_fmp4's box helpers
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dx_stream"))

SOI = b"\xff\xd8"
EOI = b"\xff\xd9"


def _jpeg(payload: bytes = b"body") -> bytes:
    return SOI + payload + EOI


class _FakeProc:
    def __init__(self, chunks):
        self._chunks = list(chunks)
        self.stdout = self

    def read(self, _n):
        return self._chunks.pop(0) if self._chunks else b""

    def poll(self):
        return None


@pytest.fixture()
def reader(monkeypatch):
    """Isolate the module's frame globals for one _read_frames_from run."""
    from core import mjpeg

    monkeypatch.setattr(mjpeg, "_streaming", True)
    monkeypatch.setattr(mjpeg, "_latest_frame", None)
    monkeypatch.setattr(mjpeg, "_frame_count", 0)
    return mjpeg


class TestJpegFraming:
    def test_single_frame_is_captured_whole(self, reader):
        reader._read_frames_from(_FakeProc([_jpeg(b"abc")]))
        assert reader.get_latest_frame() == _jpeg(b"abc")
        assert reader.get_frame_count() == 1

    def test_multiple_frames_in_one_chunk(self, reader):
        reader._read_frames_from(_FakeProc([_jpeg(b"1") + _jpeg(b"2") + _jpeg(b"3")]))
        assert reader.get_frame_count() == 3
        assert reader.get_latest_frame() == _jpeg(b"3"), "the newest frame wins"

    def test_frame_split_across_chunks_is_reassembled(self, reader):
        """65536-byte reads cut frames arbitrarily; losing one at a chunk boundary
        would show as a stutter with no error anywhere."""
        frame = _jpeg(b"x" * 50)
        reader._read_frames_from(_FakeProc([frame[:10], frame[10:30], frame[30:]]))
        assert reader.get_frame_count() == 1
        assert reader.get_latest_frame() == frame

    def test_leading_garbage_before_soi_is_discarded(self, reader):
        """gst-launch can emit banner text on the same fd before the first frame."""
        reader._read_frames_from(_FakeProc([b"gst noise here" + _jpeg(b"ok")]))
        assert reader.get_latest_frame() == _jpeg(b"ok")

    def test_incomplete_frame_is_held_until_its_eoi(self, reader):
        reader._read_frames_from(_FakeProc([SOI + b"partial"]))
        assert reader.get_frame_count() == 0
        assert reader.get_latest_frame() is None

    def test_marker_less_bytes_do_not_corrupt_a_later_frame(self, reader):
        """NOTE: the reader also CLEARS the buffer when no SOI is present, which
        bounds memory on a stream that never produces a marker. That branch is not
        observable from outside — output is identical either way — so this test
        only covers the part that is: the next real frame still arrives intact."""
        reader._read_frames_from(_FakeProc([b"\x00" * 1000, _jpeg(b"z")]))
        assert reader.get_latest_frame() == _jpeg(b"z")
        assert reader.get_frame_count() == 1

    def test_eoi_before_any_soi_does_not_produce_a_frame(self, reader):
        reader._read_frames_from(_FakeProc([EOI + b"junk"]))
        assert reader.get_frame_count() == 0

    def test_stray_eoi_before_a_frame_does_not_truncate_it(self, reader):
        """The EOI scan must start AFTER the SOI. Searching from offset 0 finds
        this stray marker first, yields eoi_pos < soi_pos, and emits an EMPTY
        frame while consuming the wrong number of bytes — a black viewer with a
        happily incrementing frame counter."""
        reader._read_frames_from(_FakeProc([EOI + _jpeg(b"real payload")]))
        frame = reader.get_latest_frame()
        assert frame == _jpeg(b"real payload")
        # The count is what exposes the bug: scanning from 0 emits an EMPTY frame
        # for the stray marker first and only then the real one, so the last frame
        # still looks right while the counter has silently double-counted.
        assert reader.get_frame_count() == 1, (
            "exactly one frame is present; a higher count means an empty frame was "
            "emitted for the stray EOI"
        )

    def test_reader_exits_when_streaming_is_cleared(self, reader, monkeypatch):
        monkeypatch.setattr(reader, "_streaming", False)
        reader._read_frames_from(_FakeProc([_jpeg(b"never read")]))
        assert reader.get_frame_count() == 0

    def test_reader_swallows_exceptions(self, reader):
        """A crash here must not take the reader thread — and the server — down."""
        class _Boom:
            stdout = property(lambda self: (_ for _ in ()).throw(OSError("pipe died")))

            def poll(self):
                return None

        reader._read_frames_from(_Boom())  # must not raise
        assert reader.get_frame_count() == 0


class TestEncoderSelection:
    @pytest.fixture()
    def fresh(self, monkeypatch):
        from core import mjpeg

        monkeypatch.setattr(mjpeg, "_JPEG_ENCODER", None)
        return mjpeg

    def test_hardware_encoder_pins_nv12_input(self, fresh, monkeypatch):
        """The historical corruption was an unconstrained input format, not the HW
        encoder — dropping the NV12 caps brings the torn JPEGs back."""
        monkeypatch.setattr(fresh.subprocess, "run",
                            lambda *a, **k: type("R", (), {"returncode": 0})())
        enc = fresh._jpeg_encoder()
        assert "mppjpegenc" in enc
        assert "video/x-raw,format=NV12" in enc

    def test_software_fallback_when_absent(self, fresh, monkeypatch):
        monkeypatch.setattr(fresh.subprocess, "run",
                            lambda *a, **k: type("R", (), {"returncode": 1})())
        assert fresh._jpeg_encoder() == "jpegenc quality=80"

    def test_probe_failure_falls_back(self, fresh, monkeypatch):
        def _boom(*a, **k):
            raise FileNotFoundError("gst-inspect-1.0")

        monkeypatch.setattr(fresh.subprocess, "run", _boom)
        assert fresh._jpeg_encoder() == "jpegenc quality=80"

    def test_result_is_cached(self, fresh, monkeypatch):
        calls = []
        monkeypatch.setattr(fresh.subprocess, "run",
                            lambda *a, **k: (calls.append(1),
                                             type("R", (), {"returncode": 1})())[1])
        fresh._jpeg_encoder()
        fresh._jpeg_encoder()
        assert len(calls) == 1


class TestPipelineRewriting:
    def test_compositor_pipeline_cuts_after_the_compositor(self):
        from core import mjpeg

        out = mjpeg.build_mjpeg_pipeline(
            "a ! compositor name=comp sink_0::xpos=0 ! videoconvert ! fpsdisplaysink")
        assert "compositor name=comp sink_0::xpos=0" in out
        assert "fpsdisplaysink" not in out
        assert out.endswith("fdsink fd=1")

    def test_single_stream_cuts_after_the_last_dxosd(self):
        from core import mjpeg

        out = mjpeg.build_mjpeg_pipeline("a ! dxosd ! b ! dxosd ! videoconvert ! webrtcbin")
        assert out.count("dxosd") == 2
        assert "webrtcbin" not in out

    def test_known_sink_markers_are_replaced_without_dxosd(self):
        from core import mjpeg

        out = mjpeg.build_mjpeg_pipeline("videotestsrc ! videoconvert ! x264enc ! sink")
        assert "x264enc" not in out
        assert out.startswith("videotestsrc")
        assert out.endswith("fdsink fd=1")

    def test_no_marker_appends_the_sink(self):
        from core import mjpeg

        out = mjpeg.build_mjpeg_pipeline("videotestsrc ! fakesink")
        assert out.endswith("fdsink fd=1")
        assert " !  ! " not in out

    def test_sink_never_forces_a_resolution(self):
        """A forced width/height caps here SIGSEGVs the dxosd -> videoscale path."""
        from core import mjpeg

        for produced in (mjpeg.get_sink_str(),
                         mjpeg.build_mjpeg_pipeline("a ! dxosd ! fpsdisplaysink")):
            assert "width=" not in produced and "height=" not in produced
            assert "videoscale" in produced

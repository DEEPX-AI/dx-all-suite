"""graph_frame: the frame zones and lines are drawn on (an image, or a video's first frame)."""
from __future__ import annotations

import base64
import io
import shutil
import subprocess

import pytest

from dx_app.core import config, graph_frame

PIL = pytest.importorskip("PIL.Image")


@pytest.fixture
def root(tmp_path, monkeypatch):
    r = tmp_path / "dx_app"
    (r / "sample" / "img").mkdir(parents=True)
    (r / "assets" / "videos").mkdir(parents=True)
    for name, value in (("DX_APP_ROOT", r), ("SAMPLE_DIR", r / "sample"), ("ASSETS_DIR", r / "assets"),
                        ("OUTPUTS_DIR", tmp_path / "outputs")):
        monkeypatch.setattr(config, name, value)
    return r


def _size_of(data_url):
    raw = base64.b64decode(data_url.split(",", 1)[1])
    return PIL.open(io.BytesIO(raw)).size


def test_an_image_comes_back_with_its_real_size_and_a_smaller_copy(root):
    PIL.new("RGB", (2000, 1000), (10, 20, 30)).save(root / "sample" / "img" / "wide.jpg")
    body, code = graph_frame.first_frame("sample/img/wide.jpg")
    assert code == 200 and (body["width"], body["height"]) == (2000, 1000)
    assert body["image"].startswith("data:image/jpeg;base64,") and _size_of(body["image"]) == (1280, 640)


def test_a_video_gives_its_first_frame(root):
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg is needed for a video frame")
    v = root / "assets" / "videos" / "clip.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=320x240:rate=5:duration=1",
                    "-pix_fmt", "yuv420p", str(v)], check=True, timeout=60)
    body, code = graph_frame.first_frame("assets/videos/clip.mp4")
    assert code == 200 and (body["width"], body["height"]) == (320, 240) and _size_of(body["image"]) == (320, 240)


@pytest.mark.parametrize("uri, code, key", [
    ("camera:0", 409, "live_source"), ("rtsp://10.0.0.2/s", 409, "live_source"),
    ("/etc/passwd", 400, "invalid_input"), ("sample/img/none.jpg", 400, "invalid_input"), ("", 400, "invalid_input"),
])
def test_inputs_without_a_readable_frame_say_why(root, uri, code, key):
    body, got = graph_frame.first_frame(uri)
    assert (got, body["error_key"]) == (code, key)


def test_a_file_that_is_not_an_image_is_unreadable(root):
    (root / "sample" / "img" / "fake.jpg").write_bytes(b"not a jpeg")
    body, code = graph_frame.first_frame("sample/img/fake.jpg")
    assert (code, body["error_key"]) == (422, "frame_unreadable")


def test_a_file_too_large_to_show_is_refused_before_it_is_read(root, monkeypatch):
    img = root / "sample" / "img" / "big.png"
    PIL.new("RGB", (8, 8)).save(img)
    vid = root / "assets" / "videos" / "big.mp4"
    vid.write_bytes(b"\0" * 64)
    monkeypatch.setattr(graph_frame, "MAX_IMAGE_BYTES", 16)
    monkeypatch.setattr(graph_frame, "MAX_VIDEO_BYTES", 32)
    monkeypatch.setattr(graph_frame, "_video_frame", lambda p: pytest.fail("a large video is not decoded"))
    for uri in ("sample/img/big.png", "assets/videos/big.mp4"):
        body, code = graph_frame.first_frame(uri)
        assert (code, body["error_key"]) == (413, "frame_too_large"), uri
    assert graph_frame.MAX_IMAGE_BYTES < graph_frame.MAX_VIDEO_BYTES


def test_an_image_with_too_many_pixels_is_not_decoded(root, monkeypatch):
    """A small file can declare a huge canvas (a decompression bomb); its header is enough to refuse it."""
    PIL.new("RGB", (400, 300)).save(root / "sample" / "img" / "wide.png")
    monkeypatch.setattr(graph_frame, "MAX_PIXELS", 100_000)
    body, code = graph_frame.first_frame("sample/img/wide.png")
    assert (code, body["error_key"]) == (413, "frame_too_large") and "pixels" in body["error"]
    assert PIL.MAX_IMAGE_PIXELS != 100_000, "Pillow's process-wide limit is left alone"
    assert graph_frame.MAX_PIXELS <= 50_000_000 < (PIL.MAX_IMAGE_PIXELS or 10 ** 12)


def test_ffmpeg_reads_no_terminal_input(root, monkeypatch):
    seen = {}

    def run(cmd, **kw):
        seen.update(cmd=cmd, **kw)
        return subprocess.CompletedProcess(cmd, 1, stdout=b"", stderr=b"boom")
    monkeypatch.setattr(graph_frame.shutil, "which", lambda name: "/usr/bin/" + name)
    monkeypatch.setattr(graph_frame.subprocess, "run", run)
    (root / "assets" / "videos" / "clip.mp4").write_bytes(b"\0")
    body, code = graph_frame.first_frame("assets/videos/clip.mp4")
    assert code == 422 and seen["stdin"] == subprocess.DEVNULL and "-nostdin" in seen["cmd"]

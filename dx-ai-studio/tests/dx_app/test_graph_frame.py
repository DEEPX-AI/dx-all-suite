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


# Results view: "Layers for this frame" runs the graph again on one frame of a run's video, with --output-layers.

FANOUT = {"version": 1, "name": "adas-fanout",
          "nodes": [{"id": "cam", "type": "source", "uri": "assets/videos/clip.mp4"},
                    {"id": "od", "model": "yolov8-n_640x640"}, {"id": "seg", "model": "bisenetv2_1024x2048"},
                    {"id": "depth", "model": "fastdepth_224x224"}],
          "edges": [{"from": "cam", "to": "od"}, {"from": "cam", "to": "seg"}, {"from": "cam", "to": "depth"}]}
TWO = {"version": 1, "name": "two-cameras",
       "nodes": [{"id": "cam1", "type": "source", "uri": "assets/videos/clip.mp4"},
                 {"id": "cam2", "type": "source", "uri": "sample/img/a.jpg"},
                 {"id": "od", "model": "yolov8-n_640x640"}],
       "edges": [{"from": "cam1", "to": "od"}, {"from": "cam2", "to": "od"}]}


@pytest.fixture
def runs(root, tmp_path, monkeypatch):
    """A fake dx_app with --output-layers, a video and an image input, and frames grabbed without ffmpeg."""
    from dx_app.core import graph_run, npu_jobs
    from tests.dx_app import graph_fakes
    npu_jobs._reset()
    graph_run._jobs.clear()
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.LAYERS_RUNNER)
    (root / "assets" / "videos" / "clip.mp4").write_bytes(b"\0")
    PIL.new("RGB", (8, 6)).save(root / "sample" / "img" / "a.jpg")
    grabbed = []

    def grab(path, t):
        grabbed.append((path.name, t))
        buf = io.BytesIO()
        PIL.new("RGB", (16, 12)).save(buf, format="PNG")
        return buf.getvalue()
    monkeypatch.setattr(graph_frame, "_frame_png", grab)
    monkeypatch.setattr(graph_run, "video_fps", lambda p: 10.0)
    yield {"tmp": tmp_path, "grabbed": grabbed}
    for job in list(graph_run._jobs.values()):
        if job["proc"] is not None and job["proc"].poll() is None:
            job["proc"].kill()
    graph_run._jobs.clear()
    npu_jobs._reset()


def _video_run(graph=FANOUT):
    from dx_app.core import graph_run
    body, code = graph_run.start(graph)
    assert code == 200, body
    r = graph_run.wait(body["job_id"], timeout=10)
    assert r["run_id"] == body["job_id"]
    return r["run_id"]


def test_a_paused_video_frame_runs_again_with_each_node_s_layer(runs):
    from tests.dx_app import graph_fakes
    rid = _video_run()
    assert "--output-layers" not in graph_fakes.calls(runs["tmp"])[-1], "the video run itself has no layers"
    body, code = graph_frame.inspect({"run_id": rid, "stream": "cam", "time_s": 1.25})
    assert code == 200 and body["ok"] is True, body
    assert runs["grabbed"] == [("clip.mp4", 1.25)]
    args = graph_fakes.calls(runs["tmp"])[-1]
    assert "input_cam.png" in args and "--output-layers" in args and "clip.mp4" not in args
    assert body["stream"] == "cam" and body["time_s"] == 1.25 and body["run_id"] != rid
    out = body["output"]
    assert out["kind"] == "image" and out["stream"] == "cam"
    assert [x["node"] for x in out["layers"]["layers"]] == ["seg", "depth", "od"]
    assert out["layers"]["base"].endswith("/layers/result_000000_base.png")


def test_a_frame_number_is_found_at_the_middle_of_that_frame(runs):
    rid = _video_run()
    body, code = graph_frame.inspect({"run_id": rid, "stream": "cam", "frame": 12})
    assert code == 200 and runs["grabbed"] == [("clip.mp4", 1.25)] and body["time_s"] == 1.25


def test_with_two_sources_the_other_video_is_taken_at_the_same_time_and_an_image_as_it_is(runs):
    from tests.dx_app import graph_fakes
    rid = _video_run(TWO)
    body, code = graph_frame.inspect({"run_id": rid, "stream": "cam2", "time_s": 0.5})
    assert code == 200 and body["output"]["stream"] == "cam2"
    assert [x["node"] for x in body["output"]["layers"]["layers"]] == ["od", "reid"]
    assert runs["grabbed"] == [("clip.mp4", 0.5)]
    args = graph_fakes.calls(runs["tmp"])[-1]
    assert "cam1=" in args and "input_cam1.png" in args and "cam2=" in args and "a.jpg" in args


def test_a_graph_and_its_inputs_stand_in_for_a_run(runs):
    body, code = graph_frame.inspect({"graph": FANOUT, "inputs": {"cam": "assets/videos/clip.mp4"},
                                      "stream": "cam", "time_s": 0})
    assert code == 200 and body["ok"] is True and runs["grabbed"] == [("clip.mp4", 0.0)]


@pytest.mark.parametrize("data, code, key", [
    ({"run_id": "0" * 32, "stream": "cam", "time_s": 1}, 404, "run_gone"),
    ({"run_id": "../x", "stream": "cam", "time_s": 1}, 400, "invalid_payload"),
    ({"stream": "cam", "time_s": 1}, 400, "invalid_payload"),
    ({"graph": FANOUT, "stream": "cam2", "time_s": 1}, 400, "invalid_stream"),
    ({"graph": FANOUT, "stream": "cam"}, 400, "invalid_payload"),
    ({"graph": FANOUT, "stream": "cam", "time_s": -1}, 400, "invalid_payload"),
    ({"graph": FANOUT, "stream": "cam", "frame": "x"}, 400, "invalid_payload"),
    ({"graph": FANOUT, "inputs": {"cam": "camera:0"}, "stream": "cam", "time_s": 1}, 400, "live_source"),
])
def test_a_frame_request_that_cannot_be_answered_says_why(runs, data, code, key):
    body, got = graph_frame.inspect(data)
    assert (got, body["error_key"]) == (code, key), body
    assert runs["grabbed"] == []


def test_a_frame_waits_for_the_npu_like_any_run(runs):
    from dx_app.core import npu_jobs
    npu_jobs.acquire("graph_live", "a-graph-live")
    body, code = graph_frame.inspect({"graph": FANOUT, "stream": "cam", "time_s": 0})
    assert (code, body["error_key"]) == (409, "graph_live_busy")


def test_a_build_without_layers_cannot_show_a_frame_s_layers(runs, tmp_path, monkeypatch):
    from tests.dx_app import graph_fakes
    graph_fakes.install(tmp_path, monkeypatch, 'case "$1" in --help) cat "$FIX/help_p2.txt"; exit 0 ;; esac\nexit 0')
    body, code = graph_frame.inspect({"graph": FANOUT, "stream": "cam", "time_s": 0})
    assert (code, body["error_key"]) == (409, "layers_unsupported") and runs["grabbed"] == []


def test_ffmpeg_takes_the_frame_at_a_time(root):
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg is needed for a video frame")
    v = root / "assets" / "videos" / "clip.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=64x48:rate=10:duration=2",
                    "-pix_fmt", "yuv420p", str(v)], check=True, timeout=60)
    a, b = graph_frame._frame_png(v, 0.05), graph_frame._frame_png(v, 1.55)
    assert PIL.open(io.BytesIO(a)).size == (64, 48) and a[:8] == b"\x89PNG\r\n\x1a\n" and a != b
    with pytest.raises(RuntimeError):
        graph_frame._frame_png(v, 60)

"""The live (continuous run) view as captured from Xvfb.

1. Window: dx_app's C++ runner opens its OpenCV window at Qt's default size (400x300); the per-model DisplayPump never
   calls setInitialWindowSize. The studio captures the whole 1280x720 Xvfb screen, so the video would sit small in
   the top-left corner on black → the window is fitted to the screen (libX11, no new dependency).
2. Border: the Qt window's toolbar, status bar and the grey margins left by aspect-ratio fitting are cropped.
3. Stats: the runner prints per-frame lines such as [DET] only with --show-log; without them the poll reports
   frames 0 and FPS 0.
"""
import shutil
import subprocess
import time

import pytest
from PIL import Image, ImageDraw

from dx_app.core import camera

_CHROME = (239, 239, 239)


def _qt_window(w=1280, h=720, img=(43, 1237, 28, 700)):
    """Shaped like x_fit.png: grey background, toolbar text on top, video in the middle."""
    im = Image.new("RGB", (w, h), _CHROME)
    d = ImageDraw.Draw(im)
    # long text like a real Qt toolbar — that row is only about half grey (measured 0.44–0.53)
    for y in range(10, 20):
        for x0 in range(8, w - 40, 14):
            d.line([x0, y, x0 + 6, y], fill=(20, 20, 20))
    x0, x1, y0, y1 = img
    d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=(12, 12, 16))
    d.rectangle([x0 + 100, y0 + 200, x0 + 300, y0 + 500], outline=(0, 0, 255), width=3)
    return im


def test_the_qt_chrome_is_cropped_away():
    box = camera._content_box(_qt_window())
    assert box is not None
    x0, y0, x1, y1 = box
    assert abs(x0 - 43) <= 6 and abs(x1 - 1237) <= 6, box
    assert abs(y0 - 28) <= 6 and abs(y1 - 700) <= 6, box


def test_a_portrait_video_keeps_its_wide_margins_out():
    """A portrait video (480x640) leaves side margins wider than half the screen, so even video rows are mostly grey."""
    box = camera._content_box(_qt_window(img=(371, 909, 28, 700)))
    assert box is not None
    x0, y0, x1, y1 = box
    assert abs(x0 - 371) <= 6 and abs(x1 - 909) <= 6, box
    assert abs(y0 - 28) <= 6 and abs(y1 - 700) <= 6, box


def test_a_frame_without_chrome_is_left_alone():
    im = Image.new("RGB", (1280, 720), (30, 60, 90))
    assert camera._content_box(im) in (None, (0, 0, 1280, 720))


def test_the_live_frame_keeps_its_aspect():
    out = camera._frame_jpeg(_qt_window())
    w, h = Image.open(__import__("io").BytesIO(out)).size
    assert w <= 960 and h <= 540
    assert abs(w / h - (1194 / 672)) < 0.03, (w, h)


@pytest.mark.skipif(not shutil.which("Xvfb"), reason="Xvfb 없음")
def test_the_window_is_fitted_to_the_virtual_screen():
    import ctypes
    display = ":131"
    xvfb = subprocess.Popen(["Xvfb", display, "-screen", "0", "1280x720x24", "-ac"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1)
        x = camera._xlib()
        if x is None:
            pytest.skip("libX11 없음")
        d = x.XOpenDisplay(display.encode())
        assert d
        win = x.XCreateSimpleWindow(d, x.XDefaultRootWindow(d), 0, 0, 400, 300, 0, 0, 0)
        x.XMapWindow(d, win)
        x.XSync(d, 0)
        assert camera._fit_windows(display, 1280, 720) >= 1
        x.XSync(d, 0)
        root, gx, gy = ctypes.c_ulong(), ctypes.c_int(), ctypes.c_int()
        gw, gh, bw, depth = ctypes.c_uint(), ctypes.c_uint(), ctypes.c_uint(), ctypes.c_uint()
        x.XGetGeometry(d, win, ctypes.byref(root), ctypes.byref(gx), ctypes.byref(gy),
                       ctypes.byref(gw), ctypes.byref(gh), ctypes.byref(bw), ctypes.byref(depth))
        assert (gw.value, gh.value) == (1280, 720)
        x.XCloseDisplay(d)
    finally:
        xvfb.terminate()
        xvfb.wait(timeout=5)


def test_live_cpp_runs_print_per_frame_lines(tmp_path, monkeypatch):
    from dx_app.core import live

    model = tmp_path / "m.dxnn"
    model.write_bytes(b"DXNN")
    video = tmp_path / "v.mp4"
    video.write_bytes(b"v")
    build = tmp_path / "build"
    build.mkdir()
    (build / "demo_async").write_text("")
    captured = {}

    class FakeProc:
        pid = 1

        def __init__(self, cmd, **kw):
            captured["cmd"] = cmd

        def poll(self):
            return None

    monkeypatch.setattr(live, "BUILD_DIR", build)
    monkeypatch.setattr(live, "resolve_model_path", lambda f, r: model)
    monkeypatch.setattr(live, "_ensure_xvfb", lambda s: None)
    monkeypatch.setattr(live.shutil if hasattr(live, "shutil") else shutil, "which", lambda n: "/usr/bin/" + n)
    monkeypatch.setattr(live.subprocess, "Popen", FakeProc)
    monkeypatch.setattr(live, "_video_frame_count", lambda p: None)   # ffprobe uses Popen too
    r = live.run_inference_live("demo", "object_detection", "m.dxnn", lang="cpp", variant="async",
                                input_type="video", video_path=str(video), slot_idx=7)
    live._live_procs.pop(7, None)
    assert r.get("status") == "started", r
    assert "--show-log" in captured["cmd"]


def test_det_frames_are_counted_as_frames_not_detections():
    """[DET] is one line per detection, with no frame number. Counting lines as frames gave 470 FPS (yolov12-n, really
    ~60). A frame's detections are printed in descending confidence, so a rise in confidence starts a new frame; on
    real logs this counted yolov12-n 478/478 and RT-DETR r18 190/190 frames. Frames without detections cannot be
    counted, so it is a lower bound."""
    from dx_app.core import live
    log = "\n".join([
        "[DET] person 0.91 1 2 3 4 1920 1080", "[DET] person 0.72 1 2 3 4 1920 1080", "[DET] bag 0.30 1 2 3 4 1920 1080",
        "[DET] person 0.88 1 2 3 4 1920 1080", "[DET] person 0.40 1 2 3 4 1920 1080",
        "[DET] person 0.95 1 2 3 4 1920 1080",
    ])
    t = live._parse_task_tags(log)
    assert t["tag"] == "DET" and len(t["lines"]) == 6
    assert t["frame_count"] == 3


# ── Live runs across all tasks ──────────────────────────────────────────────────────────────────────────────────────

def test_interleaved_classification_lines_never_break_the_poll(tmp_path):
    """Async callbacks write to stdout concurrently, so lines interleave ('3.50273.5913'). Parsing must not crash in
    float() and turn /api/live_poll into a 500 (resnet50 live)."""
    from dx_app.core import live
    log = "\n".join([
        "[CLS]  4.8052  4.6978  4.3400  4.2734  4.2368",
        "  1. (class 23): 4.8052", "  2. (class 7): 4.6978",
        "[CLS]  4.5051  4.4895  4.3400  3.9384  3.7679",
        "  1. (class 23): 3.50273.5913", "  2. (class 7): 4.4895",
    ])
    t = live._parse_task_tags(log)
    assert t["tag"] == "CLS" and t["frame_count"] == 2
    f = tmp_path / "x.log"
    f.write_text(log)

    class P:
        def poll(self):
            return None
    live._live_jobs["t1"] = {"proc": P(), "log_file": str(f), "start_time": __import__("time").time() - 2,
                             "model_name": "m", "category": "image_classification", "slot_idx": 0}
    try:
        r = live.poll_inference("t1")
    finally:
        live._live_jobs.pop("t1", None)
    assert r["frames"] == 2 and "error" not in r


def test_obb_and_instance_seg_frames_are_frames_not_objects():
    """[OBB] and [ISEG] are one line per object like [DET]; counting lines gave OBB 1244 'FPS' (really 38.8). On a
    real log the OBB frame count matched 621/621."""
    from dx_app.core import live
    obb = "\n".join(["[OBB] car 0.51 48.9", "[OBB] car 0.42 28.2", "[OBB] car 0.60 10.0", "[OBB] car 0.30 1.0"])
    iseg = "\n".join(["[ISEG] dog 0.85 1 2 3 4", "[ISEG] dog 0.81 1 2 3 4", "[ISEG] cow 0.90 1 2 3 4"])
    assert live._parse_task_tags(obb)["frame_count"] == 2
    assert live._parse_task_tags(iseg)["frame_count"] == 2


def _poll_with(tmp_path, log, elapsed=10.0):
    import time
    from dx_app.core import live
    f = tmp_path / "u.log"
    f.write_text(log)

    class P:
        def poll(self):
            return None
    live._live_jobs["u1"] = {"proc": P(), "log_file": str(f), "start_time": time.time() - elapsed,
                             "model_name": "m", "category": "semantic_segmentation", "slot_idx": 0}
    try:
        return live.poll_inference("u1")
    finally:
        live._live_jobs.pop("u1", None)


def test_untagged_tasks_do_not_invent_fps_from_the_source_rate(tmp_path):
    """segmentation, depth, denoise, SR, matting and anomaly runners print no per-frame lines. 'source FPS × elapsed'
    must not be reported as frames — PP-Matting really runs at 0.2 FPS but would show 24 FPS."""
    head = ("[DXAPP] [INFO] Input source FPS: 24.00\n[DXAPP] [INFO] Total frames: 478\n"
            "[DXAPP] [INFO] Starting async inference...\n[DXAPP] [INFO] Loop 1/999999\n")
    r = _poll_with(tmp_path, head)
    assert r["frames"] is None and r["fps_est"] is None and r["frame_basis"] == "none"
    # 'Loop k/N' after each pass over the video — finished passes × total frames is a lower bound on frames processed
    r = _poll_with(tmp_path, head + "[DXAPP] [INFO] Loop 2/999999\n[DXAPP] [INFO] Loop 3/999999\n", elapsed=10.0)
    assert r["frames"] == 956 and r["frame_basis"] == "loop"
    assert abs(r["fps_est"] - 95.6) < 0.2


def test_tagged_tasks_say_their_basis(tmp_path):
    r = _poll_with(tmp_path, "[POSE] 1 0.9\n[POSE] 1 0.8\n")
    assert r["frames"] == 2 and r["frame_basis"] == "tag"


def test_the_live_ui_shows_a_dash_when_frames_are_unknown():
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2] / "dx_app/static/js/inference.js").read_text(encoding="utf-8")
    body = src[src.index("function _updateSlotStats("):src.index("function _updateSlotStats(") + 2500]
    assert "poll.frames==null" in body, "frames 를 모르면 '—' (null - n = -n 이 FPS 로 보였다)"
    assert "frame_basis" in body, "Loop 기준이면 구간 FPS 대신 평균 (Loop 마다 계단으로 뛴다)"


def test_live_refuses_an_image_only_model(tmp_path, monkeypatch):
    """Some runners refuse -v (arcface, CLIP, ReID, VPR, DOPE, SFA3D, DeepMAR, CAS-ViT) and exit at once, leaving a
    black screen. The UI does not block camera or RTSP for continuous runs, so the server refuses them with a reason."""
    from dx_app.core import live
    monkeypatch.setattr(live.config, "model_image_only", lambda cat, name: True)
    r = live.run_inference_live("arcface_mobilefacenet_112x112", "face_recognition", "m.dxnn",
                                input_type="camera", slot_idx=5)
    assert r.get("error_key") == "live_image_only", r


def test_image_only_comes_from_the_model_config_then_the_task():
    from dx_app.core import config
    from shared import dx_app_layout as layout
    if layout.detect(config.DX_APP_ROOT) != layout.PER_MODEL:
        pytest.skip("per-model checkout 에서 본다")
    assert config.model_image_only("face_recognition", "arcface_mobilefacenet_112x112") is True
    assert config.model_image_only("image_classification", "casvit-t_224x224") is True   # not in the task table
    assert config.model_image_only("image_classification", "resnet50_224x224") is False
    assert config.model_image_only("embedding", "no_such_model") is True                  # legacy task table


def test_the_loop_basis_uses_the_video_length_when_the_runner_does_not_print_it(tmp_path):
    """Many runners (segmentation and others) never print 'Total frames', so the studio measures the video length when
    it starts."""
    import time
    from dx_app.core import live
    f = tmp_path / "s.log"
    f.write_text("[DXAPP] [INFO] Loop 1/999999\n[DXAPP] [INFO] Loop 2/999999\n[DXAPP] [INFO] Loop 3/999999\n")

    class P:
        def poll(self):
            return None
    live._live_jobs["s1"] = {"proc": P(), "log_file": str(f), "start_time": time.time() - 10, "total_frames": 478,
                             "model_name": "m", "category": "semantic_segmentation", "slot_idx": 0}
    try:
        r = live.poll_inference("s1")
    finally:
        live._live_jobs.pop("s1", None)
    assert r["frames"] == 956 and r["frame_basis"] == "loop"


@pytest.mark.skipif(not shutil.which("ffprobe"), reason="ffprobe 없음")
def test_the_video_length_is_measured(tmp_path):
    from dx_app.core import live
    v = tmp_path / "v.mp4"
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=64x48:rate=10", "-frames:v", "37",
                        "-pix_fmt", "yuv420p", str(v)], capture_output=True)
    if r.returncode != 0:
        pytest.skip("ffmpeg 로 시험 영상을 만들지 못했다")
    assert live._video_frame_count(v) == 37
    assert live._video_frame_count(tmp_path / "none.mp4") is None


def _result_with(tmp_path, log, rc):
    import time
    from dx_app.core import live
    f = tmp_path / "r.log"
    f.write_text(log)

    class P:
        returncode = rc

        def poll(self):
            return rc

        def wait(self, timeout=None):
            return rc
    live._live_jobs["r1"] = {"proc": P(), "log_file": str(f), "start_time": time.time() - 3,
                             "model_name": "m", "category": "zero_shot_image_classification", "slot_idx": 3}
    return live.get_inference_result("r1")


def test_a_runner_that_refuses_video_is_reported_not_called_complete(tmp_path):
    """CLIP ViT-B/32 zero-shot has image_only false in config.json, yet its C++ example refuses -v (inconsistent data).
    That cannot be blocked up front, so the runner puts the reason it ended in the result, not just 'live done'."""
    r = _result_with(tmp_path, "Option 'v' does not exist\n[HINT] This example is image-only: video/camera/RTSP "
                               "input (-v/--video, -c/--camera, -r/--rtsp) is not supported.\n", 1)
    assert r["run_error_key"] == "live_image_only" and "image-only" in r["run_error"]
    assert "error" not in r, "error 는 API 오류 자리 — UI 가 합성 결과로 덮는다"


def test_a_runner_crash_is_reported(tmp_path):
    r = _result_with(tmp_path, "[DXAPP] [INFO] Task: hand\n[DXAPP] [ERROR] Failed to load model: bad header\n", -6)
    assert r["run_error_key"] == "live_runner_failed" and "Failed to load model" in r["run_error"]


def test_a_stopped_run_is_not_an_error(tmp_path):
    r = _result_with(tmp_path, "[DXAPP] [INFO] Interrupted by user (Ctrl+C)\n Overall FPS         :   9.8 FPS\n", 0)
    assert not r.get("run_error_key")


def test_frames_take_the_larger_of_the_tag_and_the_loop_count(tmp_path):
    """The hand detector prints [HAND] only while a hand is visible — on a video with few hands that read 1.6 FPS
    (really 151.5)."""
    import time
    from dx_app.core import live
    f = tmp_path / "h.log"
    f.write_text("[HAND] 1 0.9\n" * 35 + "[DXAPP] [INFO] Loop 1/9\n[DXAPP] [INFO] Loop 2/9\n[DXAPP] [INFO] Loop 3/9\n")

    class P:
        def poll(self):
            return None
    live._live_jobs["h1"] = {"proc": P(), "log_file": str(f), "start_time": time.time() - 10, "total_frames": 478,
                             "model_name": "m", "category": "hand_detection", "slot_idx": 0}
    try:
        r = live.poll_inference("h1")
    finally:
        live._live_jobs.pop("h1", None)
    assert r["frames"] == 956 and r["frame_basis"] == "loop"


def test_the_live_ui_reports_a_runner_that_ended_by_itself():
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2] / "dx_app/static/js/inference.js").read_text(encoding="utf-8")
    body = src[src.index("async function contFinishLiveSlot("):src.index("function contShowSummary(")]
    assert "run_error_key" in body and "'err'" in body


# ── dx_app prints [PROGRESS] ────────────────────────────────────────────────────────────────────────────────────────

def test_progress_lines_are_the_frame_count_when_present(tmp_path):
    """With DXAPP_PROGRESS=1 the dx_app runner prints '[PROGRESS] frames=N' every second, and that wins over the
    estimates (tags, Loop). Runners without it fall back to the estimates."""
    log = ("[DET] person 0.9 1 2 3 4 5 6\n[DET] person 0.8 1 2 3 4 5 6\n[PROGRESS] frames=120\n"
           "[DET] person 0.9 1 2 3 4 5 6\n[PROGRESS] frames=95\n[PROGRESS] frames=240\n")
    r = _poll_with(tmp_path, log)
    assert r["frames"] == 240 and r["frame_basis"] == "progress"


def test_the_runner_measured_rates_and_stage_latency_are_shown_as_is(tmp_path):
    """dx_app's [PROGRESS] line also carries what the runner measured: fps (the last second), avg_fps (since the first
    frame -- process start and model load are not in it) and the stage averages. frames / process time read low for
    the first seconds and differed from the runner's own Overall FPS, so the runner's numbers win."""
    log = ("[PROGRESS] frames=1\n"
           "[PROGRESS] frames=11 fps=10.0 avg_fps=10.0 read_ms=1.10 pre_ms=2.00 infer_ms=20.00 post_ms=3.00\n"
           "[PROGRESS] frames=31 fps=20.0 avg_fps=15.0 read_ms=1.00 pre_ms=2.00 infer_ms=18.40 post_ms=3.00\n")
    r = _poll_with(tmp_path, log, elapsed=10.0)
    assert r["frames"] == 31 and r["frame_basis"] == "progress"
    assert r["runner_fps"] == 20.0, "the live rate is the last line's fps"
    assert r["fps_est"] == 15.0, "the average is the runner's avg_fps, not 31 frames / 10 s of process time"
    assert r["stage_ms"] == {"read": 1.0, "pre": 2.0, "infer": 18.4, "post": 3.0}


def test_progress_without_measurements_keeps_the_old_estimate(tmp_path):
    """An older dx_app prints '[PROGRESS] frames=N' only: frames / elapsed as before, no runner fps or stages."""
    r = _poll_with(tmp_path, "[PROGRESS] frames=240\n", elapsed=10.0)
    assert r["frames"] == 240 and r["fps_est"] == 24.0
    assert r["runner_fps"] is None and r["stage_ms"] is None


def test_the_live_ui_uses_the_runner_rate_and_shows_the_stage_latency():
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2] / "dx_app/static/js/inference.js").read_text(encoding="utf-8")
    body = src[src.index("function _updateSlotStats("):src.index("function _buildLiveSparklineGeometry(")]
    assert "poll.runner_fps" in body, "the runner's own fps is the FPS pill when it is there"
    assert "poll.stage_ms" in body and "c-ls-lat-" in body, "the stage latency line is filled from stage_ms"
    slot = src[src.index("function _makeLiveSlotEl("):src.index("async function contStartLive(")]
    assert "c-ls-lat-" in slot, "each slot has a latency line (hidden until the runner reports stages)"


def test_live_runs_ask_for_progress_and_a_screen_the_window_fills(tmp_path, monkeypatch):
    from dx_app.core import live
    model = tmp_path / "m.dxnn"
    model.write_bytes(b"DXNN")
    video = tmp_path / "v.mp4"
    video.write_bytes(b"v")
    build = tmp_path / "build"
    build.mkdir()
    (build / "demo_async").write_text("")
    captured = {}

    class FakeProc:
        pid = 1

        def __init__(self, cmd, **kw):
            captured["env"] = kw.get("env", {})

        def poll(self):
            return None

    monkeypatch.setattr(live, "BUILD_DIR", build)
    monkeypatch.setattr(live, "resolve_model_path", lambda f, r: model)
    monkeypatch.setattr(live, "_ensure_xvfb", lambda s: None)
    monkeypatch.setattr(live, "_video_frame_count", lambda p: None)
    monkeypatch.setattr(shutil, "which", lambda n: "/usr/bin/" + n)
    monkeypatch.setattr(live.subprocess, "Popen", FakeProc)
    live.run_inference_live("demo", "object_detection", "m.dxnn", lang="cpp", variant="async",
                            input_type="video", video_path=str(video), slot_idx=6)
    live._live_procs.pop(6, None)
    env = captured["env"]
    assert env.get("DXAPP_PROGRESS") == "1"
    # dx_app opens its window at half the screen size — report twice the Xvfb size so the window fills Xvfb
    from dx_app.core.camera import _XVFB_RES
    w, h = (int(v) for v in _XVFB_RES.split("x")[:2])
    assert (env.get("DXAPP_SCREEN_W"), env.get("DXAPP_SCREEN_H")) == (str(2 * w), str(2 * h))


def _live_cmd(tmp_path, monkeypatch, **kw):
    from dx_app.core import live

    model = tmp_path / "m.dxnn"
    model.write_bytes(b"DXNN")
    build = tmp_path / "build"
    build.mkdir(exist_ok=True)
    (build / "demo_sync").write_text("")
    captured = {}

    class FakeProc:
        pid = 1

        def __init__(self, cmd, **kw):
            captured["cmd"] = cmd

        def poll(self):
            return None

    monkeypatch.setattr(live, "BUILD_DIR", build)
    monkeypatch.setattr(live, "resolve_model_path", lambda f, r: model)
    monkeypatch.setattr(live, "_ensure_xvfb", lambda s: None)
    monkeypatch.setattr(live, "_start_cam_mux", lambda idx, n: True)
    monkeypatch.setattr(live.subprocess, "Popen", FakeProc)
    monkeypatch.setattr(live, "_video_frame_count", lambda p: None)
    slot = kw.pop("slot_idx", 6)
    r = live.run_inference_live("demo", "object_detection", "m.dxnn", lang="cpp", variant="sync", slot_idx=slot, **kw)
    live._live_procs.pop(slot, None)
    assert r.get("status") == "started", r
    return captured["cmd"]


def test_live_rtsp_goes_in_as_rtsp(tmp_path, monkeypatch):
    """Live RTSP must not end at once with "[DXAPP] [ERROR] Input file not found: rtsp://…" (exit 255, a black
    screen): the runner requires a -v path to exist, so the URL goes in as -r (the C++ rtsp_url)."""
    url = "rtsp://127.0.0.1:8554/cam"
    cmd = _live_cmd(tmp_path, monkeypatch, input_type="rtsp", rtsp_url=url)
    assert cmd[cmd.index(url) - 1] == "-r"


def test_multi_slot_camera_streams_go_in_as_urls(tmp_path, monkeypatch):
    """Several live slots on one camera read the ffmpeg fan-out (udp://…), which -v refused the same way; -r opens it
    (verified: 110 frames at 12.2 FPS from an mpegts UDP stream)."""
    cmd = _live_cmd(tmp_path, monkeypatch, input_type="camera", camera_id=0, n_total_slots=2, slot_idx=1)
    url = next(a for a in cmd if a.startswith("udp://"))
    assert cmd[cmd.index(url) - 1] == "-r"

"""_parse_perf — the only source of the FPS/latency numbers the studio reports.

Every inference result's perf card, the A/B compare table, the benchmark ranking
and the E2E triple gate's third layer all read what this function returns from a
runner's stdout. It sat at 4.7% coverage: a parser regression here does not crash
anything, it just quietly reports the wrong throughput.

Three shapes exist in the wild and are handled by different branches:
  Type A  "Inference Throughput : N FPS" summary line
  Type B  async pipeline — every latency is 0 and only the FPS column is real
  Type C  full pipeline with real per-step latencies (bottleneck analysis)
plus the Python sync image runner's separate IMAGE PROCESSING SUMMARY block.
"""
from __future__ import annotations

import subprocess

import pytest

from dx_app.core.performance import _cvt_video, _parse_perf


PERF_C = """\
noise before the block
===== PERFORMANCE SUMMARY =====
  Read           2.10 ms    476.2 FPS
  Preprocess     1.40 ms    714.3 FPS
  Inference      6.35 ms    157.5 FPS
  Postprocess    1.05 ms    952.4 FPS
  Total Frames : 300
  Total Time : 3.240 s
  Overall FPS : 92.6 FPS
===============================
trailing noise
"""


def test_ignores_everything_before_the_summary_header():
    p = _parse_perf("random log\nnot a summary\n")
    assert p == {"pipeline": []}, "no summary block means no numbers, not partial ones"


def test_type_c_full_pipeline():
    p = _parse_perf(PERF_C)
    assert p["overall_fps"] == "92.6"
    assert p["total_frames"] == "300"
    assert p["inference_latency"] == "6.35"
    assert p["inference_fps"] == "157.5"
    assert [r["step"] for r in p["pipeline"]] == ["Read", "Preprocess", "Inference", "Postprocess"]
    assert p["pipeline"][0]["latency_ms"] == 2.10
    assert p["pipeline"][0]["is_async"] is False


def test_type_c_reports_the_slowest_step_as_the_bottleneck():
    p = _parse_perf(PERF_C)
    assert p["bottleneck"] == "Inference"
    assert p["total_pipeline_ms"] == pytest.approx(2.10 + 1.40 + 6.35 + 1.05)


def test_total_time_drops_the_unit_suffix():
    """The UI appends its own unit; a stored '3.240 s' would render '3.240 ss'."""
    assert _parse_perf(PERF_C)["total_time"] == "3.240"


def test_overall_fps_drops_the_fps_word():
    """'92.6 FPS' stored verbatim breaks float() in the benchmark ranking."""
    p = _parse_perf(PERF_C)
    assert p["overall_fps"] == "92.6"
    float(p["overall_fps"])  # must not raise


def test_closing_rule_ends_the_block_so_later_noise_cannot_leak_in():
    stdout = PERF_C + "  Overall FPS : 1.0 FPS\n"
    assert _parse_perf(stdout)["overall_fps"] == "92.6", (
        "a second summary-shaped line after the closing ===== must be ignored"
    )


def test_type_b_async_pipeline_keeps_only_the_throughput():
    """Async rows report 0 ms by design; rendering them as a latency table is a lie."""
    stdout = """\
===== PERFORMANCE SUMMARY =====
  Read           0 ms    0 FPS
  Inference      0 ms    568.5 FPS*
  Postprocess    0 ms    0 FPS
===============================
"""
    p = _parse_perf(stdout)
    assert p["pipeline_async_only"] is True
    assert p["pipeline"] == [], "0-latency rows must not be rendered as a pipeline table"
    assert p["inference_fps"] == "568.5"
    assert "bottleneck" not in p, "there is no bottleneck to compute when every row is 0 ms"


def test_async_marker_is_recorded_on_the_row():
    stdout = """\
===== PERFORMANCE SUMMARY =====
  Inference      6.35 ms    157.5 FPS*
  Read           2.00 ms    500.0 FPS
===============================
"""
    rows = {r["step"]: r for r in _parse_perf(stdout)["pipeline"]}
    assert rows["Inference"]["is_async"] is True
    assert rows["Read"]["is_async"] is False


def test_type_a_inference_throughput_line():
    stdout = """\
===== PERFORMANCE SUMMARY =====
  Inference Throughput : 568.5 FPS
  Total Frames : 100
===============================
"""
    assert _parse_perf(stdout)["inference_fps"] == "568.5"


def test_inflight_and_completed_counters():
    stdout = """\
===== PERFORMANCE SUMMARY =====
  Infer Completed : 1024
  Infer Inflight Avg : 3.2
  Infer Inflight Max : 8
  Total Frames : 1024
===============================
"""
    p = _parse_perf(stdout)
    assert p["infer_completed"] == "1024"
    assert p["inflight_avg"] == "3.2"
    assert p["inflight_max"] == "8"


# --------------------------------------------------------------------------
# IMAGE PROCESSING SUMMARY — the Python sync image runner (single frame)
# --------------------------------------------------------------------------

IMAGE_SUMMARY = """\
===== IMAGE PROCESSING SUMMARY =====
  Read           2.00 ms
  Preprocess     4.00 ms
  Inference      50.00 ms
  Postprocess    4.00 ms
  Total Time : 60.00 ms
====================================
"""


def test_image_summary_derives_fps_from_latency():
    """This runner prints no FPS column, so throughput must be computed."""
    p = _parse_perf(IMAGE_SUMMARY)
    rows = {r["step"]: r for r in p["pipeline"]}
    assert rows["Inference"]["latency_ms"] == 50.0
    assert rows["Inference"]["throughput_fps"] == 20.0, "1000/50ms = 20 FPS"
    assert p["inference_latency"] == "50.00"
    assert p["inference_fps"] == "20.0"


def test_image_summary_total_time_is_converted_to_seconds():
    """The block reports ms; total_time is a seconds string everywhere else."""
    p = _parse_perf(IMAGE_SUMMARY)
    assert p["total_time"] == "0.06", "60.00 ms must become 0.06 s, not stay 60.0"
    assert p["overall_fps"] == "16.7"
    assert p["total_frames"] == "1"
    assert p["single_frame_mode"] is True


def test_image_summary_survives_a_zero_latency_row():
    """A 0 ms step must not raise ZeroDivisionError and kill the whole result."""
    stdout = """\
===== IMAGE PROCESSING SUMMARY =====
  Display        0.00 ms
  Inference      50.00 ms
  Total Time : 50.00 ms
====================================
"""
    p = _parse_perf(stdout)
    rows = {r["step"]: r for r in p["pipeline"]}
    assert rows["Display"]["throughput_fps"] == 0.0, "1000/0 must degrade to 0, not raise"
    assert rows["Inference"]["throughput_fps"] == 20.0


def test_an_all_zero_image_summary_is_misfiled_as_an_async_pipeline():
    """Pins a real divergence rather than papering over it.

    The Type B heuristic treats "every latency is 0" as proof of an async pipeline
    and discards the rows. On the SYNC image path 0.00 ms means "faster than the
    timer's resolution", not "async" — so a run fast enough to round to zero comes
    back flagged `pipeline_async_only` while ALSO carrying `single_frame_mode`, a
    contradiction, with its pipeline table emptied.

    Asserting the current shape means a fix (e.g. skipping the Type B collapse when
    single_frame_mode is set) fails this test on purpose rather than slipping by.
    """
    stdout = """\
===== IMAGE PROCESSING SUMMARY =====
  Display        0.00 ms
  Inference      0.00 ms
  Total Time : 0.00 ms
====================================
"""
    p = _parse_perf(stdout)
    assert p["single_frame_mode"] is True
    assert p["pipeline_async_only"] is True, "current behaviour — see docstring"
    assert p["pipeline"] == []
    assert p["overall_fps"] == "0.0"


def test_image_summary_block_closes_on_the_rule():
    stdout = IMAGE_SUMMARY + "  Inference      999.00 ms\n"
    p = _parse_perf(stdout)
    assert p["inference_latency"] == "50.00", (
        "rows after the closing ===== belong to no block and must be ignored"
    )


# --------------------------------------------------------------------------
# _cvt_video
# --------------------------------------------------------------------------


def test_cvt_video_reports_ffmpeg_success(tmp_path, monkeypatch):
    src, dst = tmp_path / "in.mp4", tmp_path / "out.mp4"
    src.write_bytes(b"x")
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0)
    )
    assert _cvt_video(src, dst) is True


def test_cvt_video_reports_ffmpeg_failure_without_falling_back(tmp_path, monkeypatch):
    """A non-zero ffmpeg means a bad transcode; copying the source would ship a
    file the browser cannot play while reporting success."""
    src, dst = tmp_path / "in.mp4", tmp_path / "out.mp4"
    src.write_bytes(b"x")
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1)
    )
    assert _cvt_video(src, dst) is False
    assert not dst.exists()


def test_cvt_video_falls_back_to_a_copy_when_ffmpeg_is_absent(tmp_path, monkeypatch):
    """Hosts without ffmpeg still get a playable file if the source is already H.264."""
    src, dst = tmp_path / "in.mp4", tmp_path / "out.mp4"
    src.write_bytes(b"payload")

    def _no_ffmpeg(*a, **k):
        raise FileNotFoundError("ffmpeg")

    monkeypatch.setattr(subprocess, "run", _no_ffmpeg)
    assert _cvt_video(src, dst) is True
    assert dst.read_bytes() == b"payload"


def test_cvt_video_returns_false_when_even_the_copy_fails(tmp_path, monkeypatch):
    src, dst = tmp_path / "missing.mp4", tmp_path / "out.mp4"

    def _no_ffmpeg(*a, **k):
        raise FileNotFoundError("ffmpeg")

    monkeypatch.setattr(subprocess, "run", _no_ffmpeg)
    assert _cvt_video(src, dst) is False

"""Fix A — stale multi-stream sc=1 'error' rows must be rescued from the ok
single-stream result during backfill (no re-measurement).

Background: after "total e2e failure then `resume --retry-failed`", the retry
boundary-search starts at sc>=2 for capacity>=2 models and never revisits sc=1,
so the attempt-1 `sc=1 error` row survives even though single-stream is now ok.
Since sc=1 == single-stream by design, the post-hoc backfill must rebuild such
rows from the single-stream result. See spec 2026-07-20-dx-benchmark-sc1-*.
"""
from benchmark.__main__ import _backfill_sc1_from_single_stream


def _multi_sc1_error(model="yolo.dxnn", ort=False):
    return {"model": model, "use_ort": ort, "task": "object_detection", "size": "n",
            "stream_count": 1, "status": "error", "runs": 0, "requested_runs": 3,
            "avg_e2e_fps": 0.0, "avg_per_channel_fps": 0.0,
            "reason": "5/3 measured runs were unparsable"}


def _single_ok(model="yolo.dxnn", ort=False, fps=48.0, status="ok"):
    return {"model": model, "use_ort": ort, "task": "object_detection", "size": "n",
            "stream_count": 1, "status": status, "runs": 3, "requested_runs": 3,
            "avg_e2e_fps": fps, "fps_std": 0.5, "avg_time_sec": (100.0 / fps) if fps else 0.0,
            "decoder": "h264", "frame_count": 100, "max_rss_mib": 150.0,
            "npu_total_avg_pct": 50.0, "npu_total_max_pct": 90.0,
            "npu_temp_min_c": 60, "npu_temp_max_c": 65}


def test_sc1_error_rescued_from_ok_single_stream():
    """A failed sc=1 with a matching ok single-stream is rebuilt as ok."""
    multi = [_multi_sc1_error()]
    n = _backfill_sc1_from_single_stream(multi, [_single_ok(fps=48.0)])
    assert n == 1
    row = multi[0]
    assert row["status"] == "ok"
    assert row["avg_e2e_fps"] == 48.0
    assert row["avg_per_channel_fps"] == 48.0          # sc=1 per-channel == single-stream e2e
    assert row["runs"] == 3
    assert row.get("source") == "single_stream"


def test_sc1_ok_row_not_overwritten():
    """An already-ok sc=1 row must be left untouched (no clobber)."""
    multi = [{"model": "yolo.dxnn", "use_ort": False, "stream_count": 1, "status": "ok",
              "runs": 3, "requested_runs": 3, "avg_e2e_fps": 60.0,
              "avg_per_channel_fps": 60.0, "source": "single_stream"}]
    _backfill_sc1_from_single_stream(multi, [_single_ok(fps=99.0)])
    assert multi[0]["avg_e2e_fps"] == 60.0             # unchanged, not overwritten by 99.0
    assert multi[0]["status"] == "ok"


def test_sc1_error_not_rescued_when_single_also_failed():
    """Never fabricate: a failed single-stream cannot rescue a failed sc=1."""
    multi = [_multi_sc1_error()]
    _backfill_sc1_from_single_stream(multi, [_single_ok(fps=0.0, status="error")])
    assert multi[0]["status"] == "error"               # stays error, never rescued from a failed single
    assert (multi[0]["avg_e2e_fps"] or 0.0) == 0.0


def test_sc1_error_left_alone_when_no_matching_single():
    """No matching single-stream row → genuine, unrescuable failure stays."""
    multi = [_multi_sc1_error(model="only-in-multi.dxnn")]
    n = _backfill_sc1_from_single_stream(multi, [_single_ok(model="different.dxnn")])
    assert multi[0]["status"] == "error"
    assert n == 0

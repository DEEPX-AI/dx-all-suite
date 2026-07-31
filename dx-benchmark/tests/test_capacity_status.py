"""Max-channel capacity summary must surface measurement failures.

Capacity is derived from the best *ok* stream count, so a run whose sweep had
error/partial rows (e.g. an unparsable sc=1 baseline) can still show a valid
channel number. Without a status on the summary, the dashboard's Max Channel
Capacity table shows a normal number and the failure is invisible. The summary
therefore carries the worst status across the model's multi-stream rows.
"""
from benchmark.aggregator import _build_capacity_summary


def _row(sc, status, pcfps, model="yolo.dxnn", ort=False, runs=3):
    return {"model": model, "use_ort": ort, "task": "object_detection", "size": "n",
            "stream_count": sc, "status": status, "avg_per_channel_fps": pcfps,
            "runs": runs, "requested_runs": runs}


def test_capacity_valid_but_status_surfaces_error():
    # sc=1 unparsable, but sc=2/3 ok and meet threshold → capacity=3, status=error.
    rows = [_row(1, "error", 0.0), _row(2, "ok", 50.0), _row(3, "ok", 35.0)]
    s = _build_capacity_summary("r", "e", rows, 30.0)
    assert len(s) == 1
    assert s[0]["capacity_streams"] == 3
    assert s[0]["status"] == "error"


def test_capacity_status_ok_when_all_ok():
    rows = [_row(1, "ok", 60.0), _row(2, "ok", 40.0)]
    s = _build_capacity_summary("r", "e", rows, 30.0)
    assert s[0]["status"] == "ok"


def test_capacity_status_on_zero_sentinel():
    # nothing meets threshold → 0-capacity sentinel still carries worst status.
    rows = [_row(1, "error", 0.0), _row(2, "partial", 10.0)]
    s = _build_capacity_summary("r", "e", rows, 30.0)
    assert s[0]["capacity_streams"] == 0
    assert s[0]["status"] == "error"


def test_capacity_partial_ranks_above_ok():
    rows = [_row(1, "ok", 60.0), _row(2, "partial", 40.0)]
    s = _build_capacity_summary("r", "e", rows, 30.0)
    assert s[0]["status"] == "partial"


# ── Fix B: status must be self-explanatory (reason + which sc failed) ──────

def test_capacity_status_reason_and_failed_sc_surfaced():
    # sc=1 error (hidden from report), sc=2/3 ok → status=error must carry WHY.
    rows = [_row(1, "error", 0.0), _row(2, "ok", 50.0), _row(3, "ok", 35.0)]
    rows[0]["reason"] = "5/3 measured runs were unparsable"
    s = _build_capacity_summary("r", "e", rows, 30.0)
    assert s[0]["status"] == "error"
    assert s[0]["status_reason"] == "5/3 measured runs were unparsable"
    assert s[0]["failed_stream_counts"] == [1]


def test_capacity_status_reason_null_when_all_ok():
    rows = [_row(1, "ok", 60.0), _row(2, "ok", 40.0)]
    s = _build_capacity_summary("r", "e", rows, 30.0)
    assert s[0]["status_reason"] is None
    assert s[0]["failed_stream_counts"] == []

"""G7 — timing_history must survive resume/interruption.

Bug: fp["timing_history"] was only attached at finalization, and only a
completed attempt appended an entry. So on resume the prior attempt's row could
be dropped (env written without history until finalization), and an attempt that
was killed before finalization left NO Test Timing row at all.

Fix: `_init_timing_history` loads prior history AND appends a provisional
'interrupted' entry for the current attempt (persisted in every env write);
`_finalize_timing_entry` upgrades that entry in place (never appends a duplicate).
"""
from benchmark.__main__ import _init_timing_history, _finalize_timing_entry
from benchmark.config import BenchmarkConfig


def _cfg():
    return BenchmarkConfig()


_PRIOR_RUN = {
    "mode": "run", "start": "2026-07-16 08:40:33", "end": "2026-07-16 20:00:00",
    "duration_sec": 40767.0, "families": ["all"], "task": "all",
    "sizes": ["n", "s", "m", "l", "x"], "retry_failed": False, "outcome": "completed",
}


def test_fresh_run_gets_provisional_interrupted_entry():
    # A run that hasn't finalized yet must still leave a row (outcome=interrupted).
    hist, idx = _init_timing_history({}, _cfg(), ["all"], None, False, "2026-07-20 10:00:00")
    assert idx == 0
    assert len(hist) == 1
    assert hist[0]["mode"] == "run"
    assert hist[0]["outcome"] == "interrupted"


def test_resume_preserves_prior_attempt_and_adds_current():
    # The reported bug: prior attempt must NOT disappear on resume.
    hist, idx = _init_timing_history(
        {"timing_history": [dict(_PRIOR_RUN)]}, _cfg(), ["all"],
        resume_dir=object(), retry_failed=True, start_iso="2026-07-18 09:01:57")
    assert len(hist) == 2                    # prior + current
    assert idx == 1
    assert hist[0] == _PRIOR_RUN             # prior untouched
    assert hist[1]["mode"] == "retry-failed"
    assert hist[1]["outcome"] == "interrupted"


def test_finalize_replaces_current_in_place_not_append():
    hist, idx = _init_timing_history(
        {"timing_history": [dict(_PRIOR_RUN)]}, _cfg(), ["all"],
        resume_dir=object(), retry_failed=True, start_iso="2026-07-18 09:01:57")
    _finalize_timing_entry(
        hist, idx, cfg=_cfg(), families=["all"], resume_dir=object(), retry_failed=True,
        start_iso="2026-07-18 09:01:57", end_iso="2026-07-19 02:07:06",
        duration_sec=61509.0, outcome="completed")
    assert len(hist) == 2                    # replaced in place, NOT duplicated
    assert hist[0] == _PRIOR_RUN             # prior still intact
    assert hist[1]["outcome"] == "completed"
    assert hist[1]["end"] == "2026-07-19 02:07:06"
    assert hist[1]["duration_sec"] == 61509.0


def test_finalize_records_failure_fields():
    hist, idx = _init_timing_history({}, _cfg(), ["all"], None, False, "2026-07-20 10:00:00")
    _finalize_timing_entry(
        hist, idx, cfg=_cfg(), families=["all"], resume_dir=None, retry_failed=False,
        start_iso="2026-07-20 10:00:00", end_iso="2026-07-20 10:30:00", duration_sec=1800.0,
        outcome="failed", failure_stage="multi", failure_model="yolo26x.dxnn",
        failure_ort="OFF", failure_reason="device init failed")
    assert hist[0]["outcome"] == "failed"
    assert hist[0]["failure_stage"] == "multi"
    assert hist[0]["failure_reason"] == "device init failed"

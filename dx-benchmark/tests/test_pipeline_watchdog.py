from benchmark.config import BenchmarkConfig
from benchmark.model_catalog import ModelEntry
from benchmark import runner_pipeline as rp
from benchmark.runner_pipeline import (
    PipeOutcome, _build_single_pipeline, _build_multi_pipeline, _watchdog_decision,
)


def test_watchdog_config_defaults():
    c = BenchmarkConfig()
    assert c.e2e_stall_timeout == 90.0
    assert c.e2e_hard_cap == 1800.0


def test_protocol_metadata_includes_watchdog_thresholds():
    # The watchdog thresholds must be recorded in the run's protocol metadata so
    # each run captures which stall/hard-cap values were active (reproducibility).
    from benchmark.config import BenchmarkConfig, get_protocol_metadata
    md = get_protocol_metadata(BenchmarkConfig())
    assert md["e2e_stall_timeout"] == 90.0
    assert md["e2e_hard_cap"] == 1800.0


def test_pipeoutcome_values():
    assert PipeOutcome.OK.value == "ok"
    assert PipeOutcome.HANG.value == "hang"
    assert PipeOutcome.RUNAWAY.value == "runaway"


def test_pipelines_have_progressreport():
    sp = _build_single_pipeline("m.dxnn", True, "/v.mp4", "pp.json")
    mp = _build_multi_pipeline("m.dxnn", True, "/v.mp4", "pp.json", 2)
    assert "progressreport" in sp
    assert "progressreport" in mp
    # heartbeat sits right before the terminal fakesink
    assert sp.index("progressreport") < sp.index("fakesink")
    assert mp.index("progressreport") < mp.index("fakesink")


def test_watchdog_progressing_returns_none():
    assert _watchdog_decision(False, now=100.0, last_progress_ts=95.0, start_ts=0.0,
                              stall_timeout=90.0, hard_cap=1800.0) is None


def test_watchdog_exit_returns_ok():
    assert _watchdog_decision(True, now=100.0, last_progress_ts=95.0, start_ts=0.0,
                              stall_timeout=90.0, hard_cap=1800.0) is PipeOutcome.OK


def test_watchdog_stall_returns_hang():
    assert _watchdog_decision(False, now=100.0, last_progress_ts=5.0, start_ts=0.0,
                              stall_timeout=90.0, hard_cap=1800.0) is PipeOutcome.HANG


def test_watchdog_hardcap_returns_runaway():
    assert _watchdog_decision(False, now=2000.0, last_progress_ts=1999.0, start_ts=0.0,
                              stall_timeout=90.0, hard_cap=1800.0) is PipeOutcome.RUNAWAY


def test_watchdog_exit_wins_over_stall_and_hardcap():
    # A finished process must classify OK even if it also looks stalled / over cap.
    assert _watchdog_decision(True, now=5000.0, last_progress_ts=0.0, start_ts=0.0,
                              stall_timeout=90.0, hard_cap=1800.0) is PipeOutcome.OK


# ── measured-run PipeOutcome branching (behavioral) ────────────────────────
#
# run_single_stream's measured loop does:
#   outcome, log = _run_gst_pipeline(...)
#   if outcome is not PipeOutcome.OK: timeout_runs += 1; continue
#   else: parse _parse_execution_time(log) -> record fps
# with a backfill budget of e2e_runs + model_run_retries attempts. These tests
# mirror the mocking style of tests/test_backfill.py's _install_pipeline_mocks,
# but drive _run_gst_pipeline with raw (PipeOutcome, log) tuples so both HANG
# and slow-but-OK outcomes can be scripted directly.


class _FakeStats:
    raw_log = ""


class _FakeMonitor:
    def __init__(self, *a, **kw):
        pass

    def start(self):
        pass

    def stop(self):
        return _FakeStats()


class _FakeMerged:
    def as_dict(self, ids):
        return {}


def _model():
    return ModelEntry(name="m.dxnn", path="/tmp/m.dxnn", task="object_detection",
                      task_suffix="", size="n")


def _cfg_pipeline(run_retries, e2e_runs=3):
    return BenchmarkConfig(e2e_runs=e2e_runs, model_warmup=1,
                           model_warmup_retries=1, model_run_retries=run_retries)


def _install_wd_pipeline_mocks(monkeypatch, outcome_seq, exec_time=1.0):
    """Mock the pipeline runner to return a scripted (PipeOutcome, log) sequence.

    Reuses the fakes from test_backfill.py's _install_pipeline_mocks for the
    surrounding helpers (NpuMonitor, frame count, decoder, etc.); only
    _run_gst_pipeline (raw tuples) and _parse_execution_time (fixed value)
    differ, so OK vs HANG/RUNAWAY outcomes can be scripted independently of
    whether the execution-time parse would itself succeed.
    """
    monkeypatch.setattr(rp, "NpuMonitor", _FakeMonitor)
    monkeypatch.setattr(rp, "_get_frame_count", lambda *a, **kw: 100)
    monkeypatch.setattr(rp, "get_postprocess_config_path", lambda *a, **kw: "pp")
    monkeypatch.setattr(rp, "get_task_preprocess", lambda *a, **kw: "pre")
    monkeypatch.setattr(rp, "get_task_inference", lambda *a, **kw: "inf")
    monkeypatch.setattr(rp, "_build_single_pipeline", lambda *a, **kw: ["gst"])
    monkeypatch.setattr(rp, "_parse_cpu_pct", lambda *a, **kw: 10.0)
    monkeypatch.setattr(rp, "_parse_max_rss_kb", lambda *a, **kw: 1000)
    monkeypatch.setattr(rp, "_detect_decoder", lambda *a, **kw: "h264")
    monkeypatch.setattr(rp, "_extract_pipeline_caps", lambda *a, **kw: None)
    monkeypatch.setattr(rp, "_merge_npu_stats", lambda *a, **kw: _FakeMerged())
    monkeypatch.setattr(rp, "_parse_execution_time", lambda *a, **kw: exec_time)

    seq = iter(outcome_seq)
    monkeypatch.setattr(rp, "_run_gst_pipeline", lambda *a, **kw: next(seq))


def test_slow_ok_run_is_recorded_not_discarded(monkeypatch):
    # warmup OK + 3 slow-but-OK measured runs (large exec_time) -> status ok,
    # 3 runs recorded, no retry needed. A slow-but-completed run must be
    # recorded honestly, not discarded as if it had hung.
    _install_wd_pipeline_mocks(
        monkeypatch,
        [(PipeOutcome.OK, "w"), (PipeOutcome.OK, "a"), (PipeOutcome.OK, "b"), (PipeOutcome.OK, "c")],
        exec_time=300.0)
    r = rp.run_single_stream(_model(), use_ort=False, cfg=_cfg_pipeline(2), save_dir=None)
    assert r.status == "ok"
    assert r.runs == 3
    # 300s over 100 frames -> ~0.33 fps recorded (slow value honestly kept)
    assert r.avg_e2e_fps < 1.0


def test_multi_slow_ok_run_is_recorded_not_discarded(monkeypatch):
    # Multi-stream analogue of test_slow_ok_run_is_recorded_not_discarded.
    # run_multi_stream holds the multi measured loop with the same PipeOutcome
    # branching that run_multi_stream_sweep drives per stream count. A slow-but-OK
    # run (large exec_time) must be recorded honestly, not discarded as a timeout.
    # warmup OK + 3 slow-but-OK measured runs -> status ok, 3 runs recorded.
    _install_wd_pipeline_mocks(
        monkeypatch,
        [(PipeOutcome.OK, "w"), (PipeOutcome.OK, "a"), (PipeOutcome.OK, "b"), (PipeOutcome.OK, "c")],
        exec_time=300.0)
    monkeypatch.setattr(rp, "_build_multi_pipeline", lambda *a, **kw: ["gst"])
    r = rp.run_multi_stream(_model(), use_ort=False, stream_count=2,
                            cfg=_cfg_pipeline(2), save_dir=None)
    assert r.status == "ok"
    assert r.runs == 3
    assert r.timeout_runs == 0
    # 300s over 2*100 frames -> ~0.67 total fps recorded (slow value honestly kept)
    assert r.avg_e2e_fps < 1.0
    assert r.avg_e2e_fps > 0.0


def test_hang_retried_within_budget_then_partial(monkeypatch):
    # warmup OK; measured: HANG, OK, HANG, HANG, OK (budget e2e_runs=3 + retries=2 = 5)
    # -> only 2 OK of target 3 reached before the attempt budget is exhausted
    # -> partial, runs=2. Confirms HANG is retried (not fatal) within budget.
    _install_wd_pipeline_mocks(
        monkeypatch,
        [(PipeOutcome.OK, "w"),
         (PipeOutcome.HANG, ""), (PipeOutcome.OK, "a"),
         (PipeOutcome.HANG, ""), (PipeOutcome.HANG, ""), (PipeOutcome.OK, "b")],
        exec_time=1.0)
    r = rp.run_single_stream(_model(), use_ort=False, cfg=_cfg_pipeline(2), save_dir=None)
    assert r.status == "partial"
    assert r.runs == 2


from benchmark.__main__ import _should_remeasure, _is_failed_result


def test_should_remeasure_partial():
    assert _should_remeasure({"status": "partial"}, True) is True
    assert _should_remeasure({"status": "ok"}, True) is False
    assert _should_remeasure({"status": "partial"}, False) is False
    assert _should_remeasure(None, True) is False


def test_is_failed_result_unchanged():
    # multi-stream logic must still treat partial as NOT-failed
    assert _is_failed_result({"status": "partial"}) is False
    assert _is_failed_result({"status": "no_fps"}) is True
    assert _is_failed_result({"status": "ok"}) is False

"""Backfill-retry behaviour for measured runs (runner_model.run_throughput).

Verifies that transient measured-run failures are retried up to the attempt
budget (num_runs + model_run_retries) to reach the target success count, and
that exhausting the budget yields an honest ``partial`` status.
"""
import types

import pytest

from benchmark import runner_model
from benchmark.config import BenchmarkConfig
from benchmark.model_catalog import ModelEntry
from benchmark.runner_pipeline import PipeOutcome


class _FakeProc:
    stdout = "fake-stdout"
    stderr = "fake-stderr"
    returncode = 0


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


def _install_common_mocks(monkeypatch, fps_sequence):
    """subprocess.run never raises (warmup + measured); FPS parse is scripted."""
    monkeypatch.setattr(runner_model.subprocess, "run", lambda *a, **kw: _FakeProc())
    monkeypatch.setattr(runner_model, "NpuMonitor", _FakeMonitor)
    monkeypatch.setattr(runner_model, "_cleanup_run_model", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_parse_cpu_pct", lambda *a, **kw: 10.0)
    monkeypatch.setattr(runner_model, "_parse_npu_memory_bytes", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_parse_input_tensor_shape", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_merge_npu_stats", lambda *a, **kw: _FakeMerged())
    # Stub the buffer-count probe so these tests exercise ONLY measured-run backfill
    # (the probe would otherwise consume fps_sequence entries before the measured runs).
    monkeypatch.setattr(runner_model, "select_buffer_count", lambda *a, **kw: (6, {6: 0.0}, False))

    seq = iter(fps_sequence)
    monkeypatch.setattr(runner_model, "_parse_fps_from_log", lambda *a, **kw: next(seq))


def _model():
    return ModelEntry(name="m.dxnn", path="/tmp/m.dxnn", task="object_detection",
                      task_suffix="", size="n")


def _cfg(run_retries):
    return BenchmarkConfig(model_throughput_runs=3, model_warmup=1,
                           model_warmup_retries=1, model_run_retries=run_retries)


def test_backfill_reaches_target_with_retries(monkeypatch):
    # 1 transient failure then 3 good; retries=2 → budget 5 → should reach 3/3.
    _install_common_mocks(monkeypatch, [None, 5.0, 5.0, 5.0])
    r = runner_model.run_throughput(_model(), use_ort=False, cfg=_cfg(2), save_dir=None)
    assert r.status == "ok"
    assert "3/3" in r.reason
    assert r.fps == pytest.approx(5.0)


def test_backfill_exhausted_is_partial(monkeypatch):
    # retries=0 → budget 3; only 2 of 3 attempts parse → honest partial.
    _install_common_mocks(monkeypatch, [5.0, None, 5.0])
    r = runner_model.run_throughput(_model(), use_ort=False, cfg=_cfg(0), save_dir=None)
    assert r.status == "partial"
    assert "2/3" in r.reason


def test_no_success_is_no_fps(monkeypatch):
    # Every attempt fails to parse → no_fps (never crashes the run).
    _install_common_mocks(monkeypatch, [None, None, None, None, None, None])
    r = runner_model.run_throughput(_model(), use_ort=False, cfg=_cfg(2), save_dir=None)
    assert r.status == "no_fps"


# ── latency backfill (profiler path) ──────────────────────────────────────

class _ProfilerScript:
    """Scripts (_parse_profiler_metric) per attempt: list of (npu_task, cpu_0).

    'npu task' query advances to the next attempt; 'cpu_0' returns that attempt's
    second value. (None, None) marks an attempt whose profiler parse fails.
    """
    def __init__(self, attempts):
        self.attempts = list(attempts)
        self.idx = -1

    def __call__(self, path, metric):
        if "npu" in metric:
            self.idx += 1
            return self.attempts[self.idx][0]
        return self.attempts[self.idx][1]


def _install_latency_mocks(monkeypatch, profiler_attempts):
    monkeypatch.setattr(runner_model.subprocess, "run", lambda *a, **kw: _FakeProc())
    monkeypatch.setattr(runner_model, "NpuMonitor", _FakeMonitor)
    monkeypatch.setattr(runner_model, "_cleanup_run_model", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_parse_cpu_pct", lambda *a, **kw: 10.0)
    monkeypatch.setattr(runner_model, "_parse_npu_memory_bytes", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_merge_npu_stats", lambda *a, **kw: _FakeMerged())
    monkeypatch.setattr(runner_model, "_parse_fps_from_log", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_parse_profiler_metric", _ProfilerScript(profiler_attempts))


def _cfg_latency(run_retries, latency_runs=2):
    return BenchmarkConfig(model_latency_runs=latency_runs, model_warmup=1,
                           model_warmup_retries=1, model_run_retries=run_retries)


def test_latency_backfill_reaches_target(monkeypatch):
    # 1 transient profiler-parse failure; retries=2 → should reach 2/2.
    _install_latency_mocks(monkeypatch, [(10.0, 2.0), (None, None), (10.0, 2.0), (10.0, 2.0)])
    r = runner_model.run_latency(_model(), use_ort=False, cfg=_cfg_latency(2), save_dir=None)
    assert r.status == "ok"
    assert "2/2" in r.reason


def test_latency_backfill_exhausted_is_partial(monkeypatch):
    # retries=0 → budget 2; only 1 of 2 attempts parse → partial.
    _install_latency_mocks(monkeypatch, [(10.0, 2.0), (None, None)])
    r = runner_model.run_latency(_model(), use_ort=False, cfg=_cfg_latency(0), save_dir=None)
    assert r.status == "partial"
    assert "1/2" in r.reason


# ── pipeline e2e (single-stream) backfill ─────────────────────────────────

from benchmark import runner_pipeline


def _install_pipeline_mocks(monkeypatch, gst_sequence):
    seq = iter(gst_sequence)

    def _fake_run_gst_pipeline(*a, **kw):
        item = next(seq)
        if item == "__TIMEOUT__":
            return PipeOutcome.HANG, item
        return PipeOutcome.OK, item

    monkeypatch.setattr(runner_pipeline, "_run_gst_pipeline", _fake_run_gst_pipeline)
    monkeypatch.setattr(runner_pipeline, "NpuMonitor", _FakeMonitor)
    monkeypatch.setattr(runner_pipeline, "_get_frame_count", lambda *a, **kw: 100)
    monkeypatch.setattr(runner_pipeline, "get_postprocess_config_path", lambda *a, **kw: "pp")
    monkeypatch.setattr(runner_pipeline, "get_task_preprocess", lambda *a, **kw: "pre")
    monkeypatch.setattr(runner_pipeline, "get_task_inference", lambda *a, **kw: "inf")
    monkeypatch.setattr(runner_pipeline, "_build_single_pipeline", lambda *a, **kw: ["gst"])
    monkeypatch.setattr(runner_pipeline, "_parse_execution_time", lambda log: 1.0 if "OK" in log else None)
    monkeypatch.setattr(runner_pipeline, "_parse_cpu_pct", lambda *a, **kw: 10.0)
    monkeypatch.setattr(runner_pipeline, "_parse_max_rss_kb", lambda *a, **kw: 1000)
    monkeypatch.setattr(runner_pipeline, "_detect_decoder", lambda *a, **kw: "h264")
    monkeypatch.setattr(runner_pipeline, "_extract_pipeline_caps", lambda *a, **kw: None)
    monkeypatch.setattr(runner_pipeline, "_merge_npu_stats", lambda *a, **kw: _FakeMerged())


def _cfg_pipeline(run_retries, e2e_runs=3):
    return BenchmarkConfig(e2e_runs=e2e_runs, model_warmup=1,
                           model_warmup_retries=1, model_run_retries=run_retries)


def test_e2e_backfill_ok_after_transient_timeout(monkeypatch):
    # warmup OK, then 1 measured timeout + 3 OK; retries=2 → 3/3 → status ok.
    _install_pipeline_mocks(monkeypatch, ["OK", "__TIMEOUT__", "OK", "OK", "OK"])
    r = runner_pipeline.run_single_stream(_model(), use_ort=False, cfg=_cfg_pipeline(2), save_dir=None)
    assert r.status == "ok"
    assert r.runs == 3
    assert "backfilled" in r.reason


def test_e2e_backfill_exhausted_is_partial(monkeypatch):
    # retries=0 → budget 3; warmup OK, measured timeout+OK+OK → 2/3 → partial.
    _install_pipeline_mocks(monkeypatch, ["OK", "__TIMEOUT__", "OK", "OK"])
    r = runner_pipeline.run_single_stream(_model(), use_ort=False, cfg=_cfg_pipeline(0), save_dir=None)
    assert r.status == "partial"
    assert r.runs == 2

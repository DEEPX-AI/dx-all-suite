"""Backfill-retry behaviour for measured runs (runner_model.run_throughput).

Verifies that transient measured-run failures are retried up to the attempt
budget (num_runs + model_run_retries) to reach the target success count, and
that exhausting the budget yields an honest ``partial`` status.
"""
import types

import pytest

from benchmark import runner_model
from benchmark.config import BenchmarkConfig, effective_sweep_timeout_sec
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
    # Stub the buffer-count sweep so these tests exercise ONLY measured-run backfill
    # (the sweep would otherwise consume fps_sequence entries before the measured runs).
    monkeypatch.setattr(runner_model, "_parse_sweep", lambda *a, **kw: (6, {6: 100.0}))

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


# ── buffer-count sweep failure branches ───────────────────────────────────

def _run_with_sweep(monkeypatch, *, returncode, sweep_result, save_dir=None,
                    stdout="sweep-stdout"):
    """Drive run_throughput with a scripted sweep outcome."""
    class _Proc:
        stderr = ""
    _Proc.stdout = stdout
    _Proc.returncode = returncode
    monkeypatch.setattr(runner_model.subprocess, "run", lambda *a, **kw: _Proc())
    monkeypatch.setattr(runner_model, "NpuMonitor", _FakeMonitor)
    monkeypatch.setattr(runner_model, "_cleanup_run_model", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_maybe_collect_dxrt_incident", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_parse_sweep", lambda *a, **kw: sweep_result)
    return runner_model.run_throughput(_model(), use_ort=False, cfg=_cfg(0), save_dir=save_dir)


def test_sweep_no_round_reports_load_failure(monkeypatch):
    """Empty curve means nothing ran -- a model load failure, not a dead device."""
    r = _run_with_sweep(monkeypatch, returncode=255, sweep_result=(None, {}))
    assert r.status == "no_fps"
    assert r.buffer_count is None
    assert "model load or launch failed" in r.reason


def test_sweep_all_zero_reports_device_unresponsive(monkeypatch):
    """Rounds ran but every one measured 0 fps -- the device really is unresponsive."""
    r = _run_with_sweep(monkeypatch, returncode=255, sweep_result=(None, {3: 0.0, 4: 0.0}))
    assert r.status == "no_fps"
    assert "device unresponsive" in r.reason
    assert r.buffer_count_curve == "3:0.0 4:0.0"


def test_sweep_without_recommendation_reports_format_drift(monkeypatch):
    """Real measurements but no winner line -- dxrun output changed under us."""
    r = _run_with_sweep(monkeypatch, returncode=0, sweep_result=(None, {3: 100.0, 4: 120.0}))
    assert r.status == "no_fps"
    assert "output format may have changed" in r.reason


def test_sweep_timeout_reports_hang_not_load_failure(monkeypatch):
    """A killed sweep is a hang -- it must not be reported as a load failure."""
    def _raise(*a, **kw):
        raise runner_model.subprocess.TimeoutExpired(cmd="run_model", timeout=300)
    monkeypatch.setattr(runner_model.subprocess, "run", _raise)
    monkeypatch.setattr(runner_model, "NpuMonitor", _FakeMonitor)
    monkeypatch.setattr(runner_model, "_cleanup_run_model", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_maybe_collect_dxrt_incident", lambda *a, **kw: None)
    r = runner_model.run_throughput(_model(), use_ort=False, cfg=_cfg(0), save_dir=None)
    assert r.status == "no_fps"
    assert "hung" in r.reason
    assert "load or launch failed" not in r.reason


def test_sweep_nonzero_exit_with_winner_is_discarded(monkeypatch):
    """A recommendation from a failed process is untrustworthy, and says so."""
    r = _run_with_sweep(monkeypatch, returncode=3, sweep_result=(7, {6: 100.0, 7: 120.0}))
    assert r.status == "no_fps"
    assert r.buffer_count is None
    assert "exited rc=3" in r.reason
    assert "output format may have changed" not in r.reason


def test_sweep_timeout_preserves_partial_curve(monkeypatch):
    """Rounds that finished before the kill must survive -- they name what hung."""
    partial = ("[max-throughput] buffer-count=3 fps=100.83 loops=205\n"
               "[max-throughput] buffer-count=4 fps=115.55 loops=236\n"
               "[max-throughput] Measuring buffer-count=5 for 10s ...\n")

    def _raise(*a, **kw):
        raise runner_model.subprocess.TimeoutExpired(
            cmd="run_model", timeout=300, output=partial, stderr="")

    monkeypatch.setattr(runner_model.subprocess, "run", _raise)
    monkeypatch.setattr(runner_model, "NpuMonitor", _FakeMonitor)
    monkeypatch.setattr(runner_model, "_cleanup_run_model", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_maybe_collect_dxrt_incident", lambda *a, **kw: None)
    r = runner_model.run_throughput(_model(), use_ort=False, cfg=_cfg(0), save_dir=None)
    assert r.status == "no_fps"
    assert "hung" in r.reason
    # The curve pins the last buffer count that completed before the hang.
    # 115.5, not 115.6: 115.55 is stored as 115.5499..., and the curve uses the
    # same "%.1f" formatting as every other bc_curve_str assertion.
    assert r.buffer_count_curve == "3:100.8 4:115.5"


def test_sweep_timeout_partial_output_may_be_undecoded_bytes(monkeypatch):
    """A REAL timeout carries bytes, not str.

    subprocess.run skips its decode step when it raises TimeoutExpired, so
    text=True does not apply to the captured output. A constructed exception
    (the test above) hands back str, which is why only this test catches the
    bytes path -- the one that actually occurs on a hung device.
    """
    def _raise(*a, **kw):
        raise runner_model.subprocess.TimeoutExpired(
            cmd="run_model", timeout=300,
            output=b"[max-throughput] buffer-count=3 fps=100.83 loops=205\n", stderr=None)

    monkeypatch.setattr(runner_model.subprocess, "run", _raise)
    monkeypatch.setattr(runner_model, "NpuMonitor", _FakeMonitor)
    monkeypatch.setattr(runner_model, "_cleanup_run_model", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_maybe_collect_dxrt_incident", lambda *a, **kw: None)
    r = runner_model.run_throughput(_model(), use_ort=False, cfg=_cfg(0), save_dir=None)
    assert r.status == "no_fps"
    assert "hung" in r.reason
    assert r.buffer_count_curve == "3:100.8"


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


# ── sweep timeout wiring + raw-log persistence ────────────────────────────

def test_sweep_is_given_the_effective_timeout_not_the_floor(monkeypatch):
    """The runner must enforce the EFFECTIVE sweep timeout, not the raw floor.

    ``bc_sweep_timeout_sec`` is only a floor; ``effective_sweep_timeout_sec``
    widens it so the whole candidate range fits at the configured probe time.
    Asserting on the ``timeout=`` kwarg actually handed to subprocess.run tests
    the wiring itself rather than a message string, so it still catches a
    regression to ``cfg.bc_sweep_timeout_sec`` if the reason text ever changes.
    The reason is checked too: it is the operator-facing copy of the same value.
    """
    cfg = _cfg(0)
    floor, effective = cfg.bc_sweep_timeout_sec, effective_sweep_timeout_sec(cfg)
    # Guard the fixture: with equal values this test could not tell them apart.
    assert (floor, effective) == (300, 340)

    seen = {}

    def _raise(*a, **kw):
        seen["timeout"] = kw.get("timeout")
        raise runner_model.subprocess.TimeoutExpired(cmd="run_model", timeout=kw.get("timeout"))

    monkeypatch.setattr(runner_model.subprocess, "run", _raise)
    monkeypatch.setattr(runner_model, "NpuMonitor", _FakeMonitor)
    monkeypatch.setattr(runner_model, "_cleanup_run_model", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_maybe_collect_dxrt_incident", lambda *a, **kw: None)
    r = runner_model.run_throughput(_model(), use_ort=False, cfg=cfg, save_dir=None)

    assert seen["timeout"] == effective
    assert f"exceeded {effective}s" in r.reason


def test_sweep_failure_saves_raw_log(monkeypatch, tmp_path):
    """A failed sweep keeps its raw output -- the only evidence of format drift."""
    r = _run_with_sweep(monkeypatch, returncode=255, sweep_result=(None, {}),
                        save_dir=tmp_path)
    assert r.status == "no_fps"
    # Name comes from _save_raw: "<model>.<family>.<ort_tag>.log".
    saved = tmp_path / "m.dxnn.throughput.bcsweep.ort_off.log"
    assert [p.name for p in tmp_path.iterdir()] == [saved.name]
    assert "sweep-stdout" in saved.read_text()


def test_sweep_hang_without_output_saves_nothing(monkeypatch, tmp_path):
    """The other half of the guard: no output means no empty placeholder file."""
    def _raise(*a, **kw):
        raise runner_model.subprocess.TimeoutExpired(cmd="run_model", timeout=340)

    monkeypatch.setattr(runner_model.subprocess, "run", _raise)
    monkeypatch.setattr(runner_model, "NpuMonitor", _FakeMonitor)
    monkeypatch.setattr(runner_model, "_cleanup_run_model", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_maybe_collect_dxrt_incident", lambda *a, **kw: None)
    r = runner_model.run_throughput(_model(), use_ort=False, cfg=_cfg(0), save_dir=tmp_path)

    assert r.status == "no_fps"
    assert list(tmp_path.iterdir()) == []


# Real `dxrun --max-throughput` output (v3.5.0 format), truncated right after the
# recommendation. The trailing "- FPS :" result block is left out on purpose: with
# it the scripted measured runs would parse an FPS and pull in the whole NPU mock
# stack, and what this test is about is the sweep text, not the measured runs.
SUCCESSFUL_SWEEP_LOG = """\
Searching I/O Buffer Count range=3-6
Max-throughput sweep: start=3 step=1 cap=6 round-time=2s peak-drop-threshold=3% (patience 2, stall 3)
[max-throughput] buffer-count=3 fps=100.83 loops=205
[max-throughput] buffer-count=4 fps=115.55 loops=236 improvement=14.59% peak-drop=0.00% stall=0
[max-throughput] buffer-count=5 fps=132.68 loops=271 improvement=14.83% peak-drop=0.00% stall=0
[max-throughput] buffer-count=6 fps=141.66 loops=290 improvement=6.76% peak-drop=0.00% stall=0
  Stop reason : reached buffer-count cap (6)
  => Recommended buffer-count : 6
     Max FPS                  : 141.66  (loops=290)
"""


def test_successful_sweep_log_is_persisted(monkeypatch, tmp_path):
    """A successful sweep must leave its raw dxrun output behind.

    Protocol v2 delegates the buffer-count decision to an external tool we do
    not control. On success only the derived curve survives, so dxrun's own
    decision signals (improvement / peak-drop / stall / loops, and the Max FPS
    line) are lost -- and a format change that still parses but means something
    different becomes invisible after the fact. A measured campaign showed why
    that matters: two identical sweeps minutes apart on one host and binary
    picked buffer counts 12 and 14 off a flat plateau, and nothing but the raw
    text can explain that after the fact.
    """
    r = _run_with_sweep(monkeypatch, returncode=0, sweep_result=(6, {3: 100.83, 6: 141.66}),
                        save_dir=tmp_path, stdout=SUCCESSFUL_SWEEP_LOG)
    # buffer_count survives only on the success path -- the failure branch nulls it.
    assert r.buffer_count == 6
    assert r.buffer_count_curve == "3:100.8 6:141.7"

    # Name comes from _save_raw: "<model>.<family>.<ort_tag>.log".
    saved = tmp_path / "m.dxnn.throughput.bcsweep.ort_off.log"
    # The failure branch returns, so one cell saves the sweep at most once.
    assert [p.name for p in tmp_path.glob("*bcsweep*")] == [saved.name]
    text = saved.read_text()
    for signal in ("improvement=", "peak-drop=", "stall=", "loops=", "Max FPS"):
        assert signal in text, f"{signal!r} missing from the saved sweep log"

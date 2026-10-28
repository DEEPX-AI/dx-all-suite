"""Thermal protocol: one cool-down target shared by dx-benchmark and dxrun.

dxrun --max-throughput (dx_rt staging b17e68f) waits until ``temp < --cool-down-temp``
before every sweep repeat and *fails the whole sweep* if it cannot. dx-benchmark's own
rule is ``temp <= target`` with ``target = min(idle + delta, cap)``. These tests pin that
both sides mean the same temperature, that the idle baseline is a settled value, and that
an unreachable target costs a retry instead of the cell.
"""
import math
import types

import pytest

from benchmark import runner_model, thermal
from benchmark.config import BenchmarkConfig, effective_sweep_timeout_sec, get_protocol_metadata
from benchmark.model_catalog import ModelEntry


# ── pure helpers ──────────────────────────────────────────────────────────

def test_target_is_idle_plus_delta_capped():
    assert thermal.cooldown_target_c(40.0, 10.0, 55.0) == 50.0
    assert thermal.cooldown_target_c(50.0, 10.0, 55.0) == 55.0


@pytest.mark.parametrize("target,arg", [(50.0, 51), (50.4, 51), (55.0, 56)])
def test_dxrun_arg_makes_its_strict_less_than_mean_less_or_equal(target, arg):
    assert thermal.dxrun_cool_down_arg(target) == arg


class _Clock:
    def __init__(self):
        self.t = 0.0

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += s


def _settle(samples, **kw):
    it = iter(samples)
    c = _Clock()
    last = {"v": None}

    def read():
        try:
            last["v"] = next(it)
        except StopIteration:
            pass
        return last["v"]

    return thermal.settle_idle_temp(read, sleep=c.sleep, now=c.now, poll_sec=15,
                                    window=4, tol_c=1.0, max_wait_sec=600, **kw)


def test_settle_waits_out_a_cooling_device_and_returns_the_flat_value():
    # A device that was just used reads 53 and keeps falling: the old single read
    # recorded 53 as "idle" and set the whole campaign's target ~8 C too high.
    assert _settle([53, 51, 49, 47, 46, 46, 46, 46]) == 46.0


def test_settle_gives_up_on_a_device_that_never_levels_off():
    c = _Clock()
    n = {"i": 0}

    def read():
        n["i"] += 1
        return 100.0 - 2.0 * n["i"]          # keeps falling 2 C per poll, forever

    assert thermal.settle_idle_temp(read, sleep=c.sleep, now=c.now, poll_sec=15, window=4,
                                    tol_c=1.0, max_wait_sec=600) is None


def test_settle_gives_up_when_the_sensor_is_unreadable():
    assert thermal.settle_idle_temp(lambda: None, sleep=lambda s: None, now=lambda: 0.0,
                                    poll_sec=1, window=4, tol_c=1.0, max_wait_sec=10) is None


def test_start_gate_passes_a_cool_device():
    ok, override, _ = thermal.start_gate(41.0, cap_c=55.0, hot_block_c=60.0, allow_hot_start=False)
    assert ok and override is None


def test_start_gate_refuses_an_idle_at_or_above_the_cap():
    ok, _, msg = thermal.start_gate(56.0, cap_c=55.0, hot_block_c=60.0, allow_hot_start=False)
    assert not ok and "55" in msg and "--allow-hot-start" in msg


def test_start_gate_override_uses_a_reachable_target_and_says_so():
    ok, override, msg = thermal.start_gate(56.0, cap_c=55.0, hot_block_c=60.0, allow_hot_start=True)
    assert ok and override == 59.0 and "hot" in msg.lower()


def test_start_gate_never_allows_a_device_above_the_hot_block():
    ok, _, _ = thermal.start_gate(62.0, cap_c=55.0, hot_block_c=60.0, allow_hot_start=True)
    assert not ok


def test_override_wins_over_the_computed_target():
    cfg = BenchmarkConfig()
    cfg.thermal_idle_temp_c = 56.0
    cfg.thermal_target_override_c = 59.0
    assert thermal.target_for(cfg) == 59.0
    cfg.thermal_target_override_c = None
    assert thermal.target_for(cfg) == 55.0   # min(66, cap)


# ── config / protocol ─────────────────────────────────────────────────────

def test_sweep_timeout_budgets_the_cool_down_between_repeats():
    cfg = BenchmarkConfig()
    # 25 rounds x (3 x 10 s probe + 3 s setup + 3 repeats x 90 s cool-down allowance)
    assert effective_sweep_timeout_sec(cfg) == 25 * (10 * 3 + 3 + 3 * 90)


def test_protocol_metadata_records_the_cool_down_scheme():
    md = get_protocol_metadata(BenchmarkConfig())
    assert md["bc_sweep_cooldown"] == "dxrun --cool-down-temp, before every repeat"
    assert md["cooldown_before_each_run"] is True
    assert md["bc_cooldown_allowance_sec"] == 90


# ── run_throughput integration ────────────────────────────────────────────

class _Proc:
    def __init__(self, stdout="", rc=0):
        self.stdout, self.stderr, self.returncode = stdout, "", rc


OK_SWEEP = ("[max-throughput] buffer-count=3 avg-fps=60.00 total-loops=1\n"
            "[max-throughput] buffer-count=4 avg-fps=75.00 total-loops=1\n"
            "  => Recommended buffer-count : 4\n")
COOL_FAIL = ("[max-throughput] buffer-count=3 avg-fps=60.00 total-loops=1\n"
             "[INFO] NPU temperature 48'C >= 46'C, waiting to cool down... (300/300s)\n"
             "[ERR] NPU temperature 48'C did not drop below 46'C within 300s.\n"
             "[ERR] Max-throughput sweep invalidated: NPU did not cool below 46'C within 300s "
             "before buffer-count 4 repeat 2. No buffer count is recommended from this sweep.\n")


def _model():
    return ModelEntry(name="m.dxnn", path="/tmp/m.dxnn", task="object_detection",
                      task_suffix="", size="m")


def _cfg(runs=1, run_retries=0, **kw):
    cfg = BenchmarkConfig(model_throughput_runs=runs, model_warmup=1, model_warmup_retries=0,
                          model_run_retries=run_retries, **kw)
    cfg.thermal_idle_temp_c = 40.0
    return cfg


class _Monitor:
    def __init__(self, *a, **kw):
        pass

    def start(self):
        pass

    def stop(self):
        return types.SimpleNamespace(raw_log="")


RUN_OK = "  - FPS : 80.0\n"


def _drive(monkeypatch, procs, cooldown=None, save_dir=None, runs=1, run_retries=0, wakes=None):
    calls = []
    events = []
    seq = iter(procs)

    def fake_run(cmd, *a, **kw):
        calls.append(list(cmd))
        proc = next(seq)
        events.append("sweep" if "--max-throughput" in cmd else "run")
        return proc

    monkeypatch.setattr(runner_model.subprocess, "run", fake_run)
    monkeypatch.setattr(runner_model, "NpuMonitor", _Monitor)
    monkeypatch.setattr(runner_model, "_merge_npu_stats",
                        lambda *a, **kw: types.SimpleNamespace(as_dict=lambda ids: {}))
    monkeypatch.setattr(runner_model, "_cleanup_run_model", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_maybe_collect_dxrt_incident", lambda *a, **kw: None)
    monkeypatch.setattr(runner_model, "_warmup_with_retries",
                        lambda cmd, *a, **kw: events.append("warmup") or
                        (wakes.append(list(cmd)) if wakes is not None else None) or True)

    def hook():
        events.append("cooldown")
        if isinstance(cooldown, Exception):
            raise cooldown
        return (49.0, 12.0)

    r = runner_model.run_throughput(_model(), use_ort=True, cfg=_cfg(runs, run_retries), save_dir=save_dir,
                                    cooldown=hook if cooldown is not None else None)
    return r, calls, events


def test_sweep_receives_the_shared_target_as_cool_down_temp(monkeypatch):
    _, calls, _ = _drive(monkeypatch, [_Proc(OK_SWEEP), _Proc(RUN_OK)], cooldown=True)
    cmd = calls[0]
    # idle 40 + 10 = 50 C target -> dxrun needs "< 51"
    assert cmd[cmd.index("--cool-down-temp") + 1] == "51"
    assert "--max-throughput" in cmd


def test_every_measured_run_is_cooled_then_woken_up_right_before_it_starts(monkeypatch):
    # After minutes idle the first run_model process is ~2.4 % slower (BIOSTAR172:
    # 499 vs 511 FPS, whatever --warmup-runs says); a short throw-away process right
    # before the run removes it, and 2 s is too short to undo the cool-down.
    _, _, events = _drive(monkeypatch, [_Proc(OK_SWEEP)] + [_Proc(RUN_OK)] * 3,
                          cooldown=True, runs=3)
    assert events == ["sweep", "cooldown", "warmup", "run", "cooldown", "warmup", "run",
                      "cooldown", "warmup", "run"]


def test_the_wake_up_is_a_short_run_of_the_same_command(monkeypatch):
    wake = []
    _, calls, _ = _drive(monkeypatch, [_Proc(OK_SWEEP), _Proc(RUN_OK)], cooldown=True, wakes=wake)
    run_cmd = calls[1]
    assert wake and wake[0][wake[0].index("-t") + 1] == "2"
    assert run_cmd[run_cmd.index("-t") + 1] == "30"
    strip = lambda c: [a for i, a in enumerate(c) if c[i - 1] != "-t" and a != "-t"]
    assert strip(wake[0]) == strip(run_cmd)            # same model, buffer count, --use-ort


def test_a_retried_run_is_cooled_down_too(monkeypatch):
    # first attempt yields no FPS, the backfill attempt must not start hot either
    r, _, events = _drive(monkeypatch, [_Proc(OK_SWEEP), _Proc(""), _Proc(RUN_OK)],
                          cooldown=True, run_retries=1)
    assert events == ["sweep", "cooldown", "warmup", "run", "cooldown", "warmup", "run"]
    assert r.status == "ok"


def test_cool_down_is_recorded_for_the_cell(monkeypatch):
    r, _, _ = _drive(monkeypatch, [_Proc(OK_SWEEP)] + [_Proc(RUN_OK)] * 2, cooldown=True, runs=2)
    d = r.as_dict()
    assert d["pre_run_cooled"] is True
    assert d["pre_run_cooldown_sec"] == 24.0             # 2 x 12 s
    assert d["pre_run_start_temp_max_c"] == 49.0
    assert d["sweep_cooldown_target_c"] == 50.0
    assert "post_sweep_cooled" not in d


def test_a_cool_down_that_times_out_is_recorded_not_fatal(monkeypatch):
    r, _, events = _drive(monkeypatch, [_Proc(OK_SWEEP)] + [_Proc(RUN_OK)] * 2,
                          cooldown=RuntimeError("stuck"), runs=2)
    assert events.count("run") == 2                       # the cell still measures
    assert r.status == "ok" and r.as_dict()["pre_run_cooled"] is False


def test_unreachable_cool_down_target_is_retried_once_above_the_stuck_temperature(monkeypatch):
    r, calls, _ = _drive(monkeypatch, [_Proc(COOL_FAIL, rc=255), _Proc(OK_SWEEP), _Proc(RUN_OK)],
                         cooldown=True)
    assert len(calls) == 3
    # stuck at 48 C -> "< 50" i.e. <= 49 C: reachable, and still close to the target
    assert calls[1][calls[1].index("--cool-down-temp") + 1] == "50"
    d = r.as_dict()
    assert d["sweep_cooldown_raised"] is True and d["buffer_count"] == 4
    assert d["sweep_cooldown_target_c"] == 49.0


def test_no_retry_when_the_stuck_temperature_is_already_too_hot(monkeypatch):
    hot = COOL_FAIL.replace("48'C", "61'C")
    r, calls, _ = _drive(monkeypatch, [_Proc(hot, rc=255)], cooldown=True)
    assert len(calls) == 1
    assert r.status == "no_fps" and "cool the NPU" in r.reason
    assert "output format may have changed" not in r.reason


def test_a_second_cool_down_failure_fails_the_cell_with_the_real_reason(monkeypatch):
    r, calls, _ = _drive(monkeypatch, [_Proc(COOL_FAIL, rc=255), _Proc(COOL_FAIL, rc=255)],
                         cooldown=True)
    assert len(calls) == 2
    assert r.status == "no_fps" and "cool the NPU" in r.reason


# ── campaign baseline (cmd_run) ───────────────────────────────────────────

def _baseline(**kw):
    from benchmark import __main__ as m
    cfg = BenchmarkConfig()
    fp = {}
    args = dict(existing_fp={}, resume_dir=None, allow_hot_start=False,
                read=lambda: 40.0, settle=lambda: 46.0)
    args.update(kw)
    ok = m._establish_thermal_baseline(cfg, fp, **args)
    return ok, cfg, fp


def test_baseline_records_the_settled_idle_and_the_target():
    ok, cfg, fp = _baseline(settle=lambda: 46.0)
    assert ok and cfg.thermal_idle_temp_c == 46.0
    assert fp["thermal"]["idle_temp_c"] == 46.0
    assert fp["thermal"]["cooldown_target_c"] == 55.0          # min(46 + 10, cap)
    assert fp["thermal"]["hot_start_override"] is False


def test_baseline_refuses_a_device_that_never_settles():
    ok, cfg, _ = _baseline(settle=lambda: None)
    assert not ok and cfg.thermal_idle_temp_c is None


def test_baseline_refuses_a_hot_idle_unless_allowed():
    assert _baseline(settle=lambda: 56.0)[0] is False
    ok, cfg, fp = _baseline(settle=lambda: 56.0, allow_hot_start=True)
    assert ok and cfg.thermal_target_override_c == 59.0
    assert fp["thermal"]["hot_start_override"] is True and fp["thermal"]["cooldown_target_c"] == 59.0


def test_resume_reuses_the_recorded_baseline_instead_of_measuring_again():
    """A resumed campaign must cool to the same temperature as the first attempt, even if
    the room is warmer today."""
    def boom():
        raise AssertionError("must not re-measure on resume")

    existing = {"thermal": {"idle_temp_c": 41.0, "cooldown_target_c": 51.0,
                            "hot_start_override": False}}
    ok, cfg, fp = _baseline(existing_fp=existing, resume_dir="results/x", settle=boom)
    assert ok and cfg.thermal_idle_temp_c == 41.0
    assert fp["thermal"]["idle_temp_c"] == 41.0


def test_resume_keeps_an_allowed_hot_start_target():
    existing = {"thermal": {"idle_temp_c": 56.0, "cooldown_target_c": 59.0,
                            "hot_start_override": True}}
    ok, cfg, _ = _baseline(existing_fp=existing, resume_dir="results/x", settle=lambda: 1 / 0)
    assert ok and cfg.thermal_target_override_c == 59.0


def test_baseline_without_a_readable_sensor_does_not_block():
    ok, cfg, fp = _baseline(read=lambda: None, settle=lambda: 1 / 0)
    assert ok and cfg.thermal_idle_temp_c is None
    assert fp["thermal"]["idle_temp_c"] is None


def test_report_protocol_table_shows_the_thermal_baseline_and_cool_down_scheme():
    from benchmark.reporter import _add_protocol_section
    fp = {"protocol": get_protocol_metadata(BenchmarkConfig()),
          "thermal": {"idle_temp_c": 41.0, "cooldown_target_c": 51.0, "hot_start_override": False}}
    lines = []
    _add_protocol_section(lines, fp)
    out = "\n".join(lines)
    assert "| NPU Idle Temp (settled) | 41.0 °C |" in out
    assert "| Cool-down Target | ≤ 51.0 °C |" in out
    assert "| Sweep Cool-down | dxrun --cool-down-temp, before every repeat |" in out
    assert "| Cool-down Before Each Throughput Run | yes |" in out

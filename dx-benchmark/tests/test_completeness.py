"""A run must not silently lose NPU telemetry: checked at preflight and in the results audit."""
from benchmark import env_fingerprint as ef
from benchmark import npu_monitor
from benchmark.completeness import audit_results


def _row(**kw):
    base = {"model": "m.dxnn", "status": "ok", "npu_clock_mhz_min": 1000.0,
            "npu_clock_mhz_max": 1000.0, "npu_throttled": False,
            "npu_temp_max_c": 60.0, "npu_total_avg_pct": 80.0}
    base.update(kw)
    return base


def test_audit_is_silent_for_complete_results():
    assert audit_results([_row()], [_row()], [_row()]) == []


def test_audit_flags_rows_without_clock_data_and_names_the_cause():
    bad = _row(npu_clock_mhz_min=None, npu_clock_mhz_max=None, npu_throttled=None)
    warnings = audit_results([bad, _row()], [bad], [])
    assert len(warnings) == 2
    assert any("1/2" in w and "model" in w for w in warnings)
    assert all("dxtop" in w and "TERM" in w for w in warnings)


def test_audit_ignores_rows_that_did_not_measure_anything():
    failed = _row(status="no_fps", npu_clock_mhz_min=None, npu_clock_mhz_max=None)
    assert audit_results([failed], [], []) == []


def test_probe_reports_ok_when_dxtop_yields_clocks(monkeypatch):
    stats = npu_monitor.NpuStats()
    stats.core_clock_min_mhz[0] = 1000.0
    stats.core_clock_max_mhz[0] = 1000.0
    stats.sample_count = 3

    class _Mon:
        def __init__(self, *a, **k): pass
        available = True
        def start(self): pass
        def stop(self): return stats

    monkeypatch.setattr(npu_monitor, "NpuMonitor", _Mon)
    monkeypatch.setattr(npu_monitor.time, "sleep", lambda s: None)
    assert npu_monitor.probe_npu_monitor()["ok"] is True


def test_probe_reports_failure_when_dxtop_yields_nothing(monkeypatch):
    class _Mon:
        def __init__(self, *a, **k): pass
        available = True
        def start(self): pass
        def stop(self): return npu_monitor.NpuStats()

    monkeypatch.setattr(npu_monitor, "NpuMonitor", _Mon)
    monkeypatch.setattr(npu_monitor.time, "sleep", lambda s: None)
    res = npu_monitor.probe_npu_monitor()
    assert res["ok"] is False and "dxtop" in res["reason"]


def test_preflight_blocks_when_the_npu_monitor_is_dead():
    fp = {"missing_required": [], "outdated_required": [],
          "npu_monitor": {"ok": False, "reason": "dxtop produced no clock samples"}}
    ok, errors = ef.check_preflight(fp)
    assert ok is False
    assert any("NPU monitor" in e and "dxtop" in e for e in errors)


def test_preflight_passes_when_the_npu_monitor_is_healthy_or_absent():
    assert ef.check_preflight({"missing_required": [], "outdated_required": [],
                               "npu_monitor": {"ok": True, "reason": ""}})[0] is True
    assert ef.check_preflight({"missing_required": [], "outdated_required": []})[0] is True


# ── raw-log backfills ─────────────────────────────────────────────────────

def test_apply_raw_backfills_runs_every_backfill_with_the_right_categories(monkeypatch, tmp_path):
    from benchmark import __main__ as m
    calls = []
    monkeypatch.setattr(m, "_backfill_from_raw_logs",
                        lambda rs, d, cat: calls.append(("npu", cat)) or 1)
    monkeypatch.setattr(m, "_backfill_fps_std",
                        lambda rs, d, cat: calls.append(("std", cat)) or 2)
    monkeypatch.setattr(m, "_backfill_sc1_from_single_stream", lambda mu, pi: 3)
    (tmp_path / "raw").mkdir()
    counts = m._apply_raw_backfills([], [], [], tmp_path / "raw")
    assert ("npu", "throughput") in calls and ("npu", "latency") in calls
    assert ("npu", "e2e.single") in calls and ("npu", "e2e.multi") in calls
    assert ("std", "throughput") in calls and ("std", "e2e.single") in calls
    assert ("std", "e2e.multi") in calls
    assert counts == {"npu": 4, "fps_std": 6, "sc1": 3}


def test_apply_raw_backfills_tolerates_a_missing_raw_dir(monkeypatch, tmp_path):
    from benchmark import __main__ as m
    monkeypatch.setattr(m, "_backfill_sc1_from_single_stream", lambda mu, pi: 0)
    assert m._apply_raw_backfills([], [], [], tmp_path / "nope") == \
        {"npu": 0, "fps_std": 0, "sc1": 0}


# ── latency rows must not inherit the throughput sigma ────────────────────

def _throughput_logs(raw):
    raw.mkdir()
    (raw / "m.dxnn.throughput.run1.ort_on.log").write_text("  - FPS : 1000.00\n")
    (raw / "m.dxnn.throughput.run2.ort_on.log").write_text("  - FPS : 1010.00\n")


def test_backfill_gives_the_throughput_sigma_to_throughput_rows_only(tmp_path):
    """Latency and throughput rows share (model, ORT); only throughput rows get the sigma."""
    from benchmark import __main__ as m
    raw = tmp_path / "raw"
    _throughput_logs(raw)
    thr = {"model": "m.dxnn", "use_ort": True, "family": "throughput", "fps": 1005.0, "fps_std": None}
    lat = {"model": "m.dxnn", "use_ort": True, "family": "latency", "fps": 95.0, "fps_std": None}
    assert m._backfill_fps_std([lat, thr], raw, "throughput") == 1
    assert thr["fps_std"] is not None
    assert lat["fps_std"] is None


def test_backfill_still_fills_rows_that_carry_no_family(tmp_path):
    """E2E / multi-stream rows have no `family` and must keep being filled."""
    from benchmark import __main__ as m
    raw = tmp_path / "raw"
    _throughput_logs(raw)
    row = {"model": "m.dxnn", "use_ort": True, "fps_std": None}
    assert m._backfill_fps_std([row], raw, "throughput") == 1

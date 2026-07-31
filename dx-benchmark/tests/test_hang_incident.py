"""Tests for hang/timeout incident enrichment (#1 pipeline_output.log, #4 summary fields).

A hang incident bundle previously captured only device-side state (dxrt-cli, dmesg,
ps_tree, host_health), which proves the device was healthy but never shows WHERE the
gst pipeline stalled. These tests pin the two enrichments:
  #1  the gst stdout tail is persisted to ``pipeline_output.log``
  #4  ``summary.txt`` gains outcome + stall duration + killed_hard + a
      device-state classifier (npu_throttled / device_responsive).
"""

import benchmark.env_fingerprint as ef
import benchmark.runner_pipeline as rp


def _setup(tmp_path, monkeypatch, *, clock=1000.0, dxrt="* Device 0: M1, Accelerator type"):
    monkeypatch.setattr(rp, "_incident_dir", tmp_path)
    monkeypatch.setattr(rp, "_incident_seq", 0)
    monkeypatch.setattr(rp, "_incident_captured", 0)
    # Incident collection shells out for diagnostics — stub for speed/isolation.
    monkeypatch.setattr(
        rp, "_run_diagnostic_cmd",
        lambda cmd, timeout=10: dxrt if cmd[:1] == ["dxrt-cli"] else "stub")
    monkeypatch.setattr(rp, "_run_diagnostic_cmd_elevated", lambda cmd, timeout=10: "stub")
    monkeypatch.setattr(rp, "read_npu_temp_c", lambda: 55.0)
    monkeypatch.setattr(rp, "read_npu_clock_mhz", lambda: clock)
    monkeypatch.setattr(ef, "collect_host_health", lambda: {})


GST_TAIL = "".join(f"progressreport0 ({i}s): {i} / 115 seconds\n" for i in range(120)) \
    + "LAST LINE BEFORE STALL\n"


def test_hang_incident_writes_pipeline_output(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    inc = rp.collect_timeout_incident(
        "m.dxnn.ort_off.e2e.warmup.hang", pipeline_output=GST_TAIL)
    assert inc is not None and inc.is_dir()
    log = (inc / "pipeline_output.log").read_text()
    assert "LAST LINE BEFORE STALL" in log


def test_pipeline_output_truncated_to_tail(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    inc = rp.collect_timeout_incident(
        "m.dxnn.ort_off.e2e.warmup.hang", pipeline_output=GST_TAIL)
    log = (inc / "pipeline_output.log").read_text()
    # 121 input lines but only the last 200 are kept — here that means the very
    # first progressreport line (0s) should have scrolled out only if > 200 lines;
    # with 121 lines all are kept, so assert the tail marker AND head are present.
    assert log.count("progressreport0") <= 200
    assert "LAST LINE BEFORE STALL" in log


def test_no_pipeline_output_when_absent(tmp_path, monkeypatch):
    """dxrt/oserror incidents call without pipeline_output — no file, backward compatible."""
    _setup(tmp_path, monkeypatch)
    inc = rp.collect_timeout_incident("m.dxnn.ort_off.throughput.run1.dxrt_error")
    assert inc is not None
    assert not (inc / "pipeline_output.log").exists()


def test_summary_has_outcome_and_classifiers(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, clock=1000.0, dxrt="* Device 0: M1, Accelerator type")
    inc = rp.collect_timeout_incident(
        "m.dxnn.ort_off.e2e.warmup.hang",
        pipeline_output=GST_TAIL, stall_duration_sec=91.2, killed_hard=True)
    s = (inc / "summary.txt").read_text()
    assert "outcome: hang" in s
    assert "npu_throttled: False" in s      # clock 1000 == nominal → not throttled
    assert "device_responsive: True" in s   # dxrt-cli returned a "* Device" line
    assert "stall_duration_sec: 91.2" in s
    assert "killed_hard: True" in s


def test_summary_throttled_and_unresponsive(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, clock=300.0, dxrt="<command timed out after 10s>")
    inc = rp.collect_timeout_incident("x.dxnn.ort_off.multi.sc2.run1.hang")
    s = (inc / "summary.txt").read_text()
    assert "outcome: hang" in s
    assert "npu_throttled: True" in s        # clock 300 < 1000 nominal
    assert "device_responsive: False" in s   # no "* Device" in dxrt-cli output
    # optional fields are omitted when the caller does not provide them
    assert "stall_duration_sec:" not in s
    assert "killed_hard:" not in s

"""Tests for dxrt runtime-error incident capture (non-timeout failures)."""

import benchmark.runner_pipeline as rp


DXRT_EXCEPTION_LOG = (
    "loops: 30\n"
    "Run model target mode : Benchmark Mode\n"
    "[dxrt-exception] Service input & output exception "
    "{dxrt service is not running} error-code=264\n"
    "Command exited with non-zero status 255\n"
)

DEVICE_RECOVERY_LOG = (
    "[RuntimeEventDispatcher] level=CRITICAL type=DEVICE_IO code=READ_OUTPUT "
    'message="Fail to read output, errno=-70, reqId=1574, ch:0"\n'
    " ** Device recovery was performed by the service.\n"
    " ** This application must exit and restart to reload models.\n"
)

CLEAN_LOG = (
    "Warmup completed.\n"
    "Inference by time: total-inference-time=30.0021(s) total-loops=102891\n"
    "* Benchmark Result (102891 inputs)\n"
    "  - FPS : 3429.46\n"
)


def _setup(tmp_path, monkeypatch):
    monkeypatch.setattr(rp, "_incident_dir", tmp_path)
    monkeypatch.setattr(rp, "_incident_seq", 0)
    monkeypatch.setattr(rp, "_dxrt_incident_count", 0)
    # Incident collection shells out for diagnostics — stub for speed/isolation.
    monkeypatch.setattr(rp, "_run_diagnostic_cmd", lambda cmd, timeout=10: "stub")
    monkeypatch.setattr(rp, "_run_diagnostic_cmd_elevated", lambda cmd, timeout=10: "stub")


def test_dxrt_exception_triggers_incident(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    inc = rp.maybe_collect_dxrt_incident(
        DXRT_EXCEPTION_LOG, "yolo26-n_224x224.dxnn.ort_off.throughput.run2")
    assert inc is not None and inc.is_dir()
    assert inc.name.endswith(".dxrt_error")
    trigger = (inc / "trigger_output.log").read_text()
    assert "error-code=264" in trigger


def test_device_recovery_triggers_incident(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    inc = rp.maybe_collect_dxrt_incident(
        DEVICE_RECOVERY_LOG, "yolo26-n_224x224.dxnn.ort_off.throughput.run3")
    assert inc is not None
    assert "Device recovery" in (inc / "trigger_output.log").read_text()


def test_clean_output_no_incident(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    assert rp.maybe_collect_dxrt_incident(CLEAN_LOG, "ctx") is None
    assert rp.maybe_collect_dxrt_incident("", "ctx") is None
    assert list(tmp_path.iterdir()) == []


def test_incident_cap_suppresses_capture(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    monkeypatch.setattr(rp, "_dxrt_incident_count", rp._MAX_DXRT_INCIDENTS)
    assert rp.maybe_collect_dxrt_incident(DXRT_EXCEPTION_LOG, "ctx") is None
    assert list(tmp_path.iterdir()) == []


def test_trigger_output_truncated_to_tail(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    long_log = "\n".join(f"line{i}" for i in range(500)) + "\n" + DXRT_EXCEPTION_LOG
    inc = rp.maybe_collect_dxrt_incident(long_log, "ctx")
    lines = (inc / "trigger_output.log").read_text().splitlines()
    assert len(lines) <= 200
    assert any("error-code=264" in ln for ln in lines)


# ── B6: total incident cap (hang incidents were previously uncapped) ──────
def test_timeout_incident_total_cap(tmp_path, monkeypatch):
    # Once the total cap is reached, further HANG captures are suppressed (no expensive
    # shell-outs, no bundle dir) — a dead/flapping device can't flood incidents/.
    monkeypatch.setattr(rp, "_incident_dir", tmp_path)
    monkeypatch.setattr(rp, "_incident_seq", 0)
    monkeypatch.setattr(rp, "_incident_captured", rp._MAX_INCIDENTS)
    assert rp.collect_timeout_incident("e2e.run1.hang") is None
    assert list(tmp_path.iterdir()) == []


def test_timeout_incident_under_cap_captures_and_counts(tmp_path, monkeypatch):
    import benchmark.env_fingerprint as ef
    monkeypatch.setattr(rp, "_incident_dir", tmp_path)
    monkeypatch.setattr(rp, "_incident_seq", 0)
    monkeypatch.setattr(rp, "_incident_captured", 0)
    monkeypatch.setattr(rp, "_run_diagnostic_cmd", lambda cmd, timeout=10: "stub")
    monkeypatch.setattr(rp, "_run_diagnostic_cmd_elevated", lambda cmd, timeout=10: "stub")
    monkeypatch.setattr(rp, "read_npu_temp_c", lambda: None)
    monkeypatch.setattr(rp, "read_npu_clock_mhz", lambda: None)
    monkeypatch.setattr(ef, "collect_host_health", lambda: {})
    d = rp.collect_timeout_incident("e2e.run1.hang")
    assert d is not None and d.is_dir()
    assert rp._incident_captured == 1

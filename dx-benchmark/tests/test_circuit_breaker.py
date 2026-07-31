"""Conservative device-death circuit breaker.

Abort the run ONLY when a device-liveness probe deterministically confirms the NPU
is unrecoverable (DEAD). A device that still probes ALIVE never aborts the run — a
failed cell is recorded and the run continues, exactly as before. A high-threshold
consecutive-fatal-models backstop is the only count-based abort (anti-runaway).
"""
from benchmark.config import BenchmarkConfig, get_protocol_metadata


# ── Task 1: config ────────────────────────────────────────────────────────
def test_circuit_breaker_config_defaults():
    cfg = BenchmarkConfig()
    assert cfg.enable_circuit_breaker is True
    assert cfg.device_probe_timeout_sec == 15
    assert cfg.circuit_breaker_backstop_models == 2


def test_circuit_breaker_config_in_protocol_metadata():
    meta = get_protocol_metadata(BenchmarkConfig())
    assert meta["circuit_breaker_backstop_models"] == 2
    assert meta["enable_circuit_breaker"] is True


# ── Task 3: pure decision helpers ─────────────────────────────────────────
from benchmark.__main__ import _is_fatal_status, circuit_breaker_decision


def test_is_fatal_status():
    for s in ("timeout", "error", "no_fps"):
        assert _is_fatal_status(s) is True
    for s in ("ok", "partial"):
        assert _is_fatal_status(s) is False


def test_cb_good_model_resets_counter():
    # a model with a good model-level result resets the run-level counter
    assert circuit_breaker_decision(False, "alive", 5, 2) == ("continue", 0)


def test_cb_dead_aborts_immediately():
    assert circuit_breaker_decision(True, "dead", 0, 2) == ("abort_dead", 0)


def test_cb_alive_failure_increments_but_continues():
    # device ALIVE but this model fully failed → keep going (user's over-abort guard)
    assert circuit_breaker_decision(True, "alive", 0, 2) == ("continue", 1)


def test_cb_backstop_trips_at_threshold():
    assert circuit_breaker_decision(True, "alive", 1, 2) == ("abort_backstop", 2)


def test_cb_unknown_never_aborts_alone():
    # UNKNOWN verdict only counts toward the high backstop, never a lone abort
    assert circuit_breaker_decision(True, "unknown", 0, 2) == ("continue", 1)

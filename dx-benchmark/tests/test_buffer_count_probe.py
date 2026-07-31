"""Adaptive buffer-count sweep (protocol v1).

Phase 1 always probes the floor range start..floor_max (default 3..8) so the
default buffer-count (6) and its neighborhood are ALWAYS measured. Phase 2
continues by +1 only while throughput is still highest at floor_max (still
rising), stopping at the knee (decline / plateau / cap). Winner = the buffer-count
with the highest measured throughput; a smaller one wins only on an EXACT tie.
"""
from benchmark.runner_model import select_buffer_count


def _curve(mapping):
    seen = []

    def probe(c):
        seen.append(c)
        return mapping[c]

    probe.seen = seen
    return probe


def test_floor_always_probed_covers_default_6():
    # Peak is at 5, but the floor (3..8) is still fully probed → default 6 measured.
    p = _curve({3: 200.0, 4: 250.0, 5: 255.0, 6: 254.0, 7: 253.0, 8: 252.0})
    win, curve, edge = select_buffer_count(p, start=3, floor_max=8)
    assert {3, 4, 5, 6, 7, 8}.issubset(set(p.seen))   # whole floor probed
    assert 6 in curve                                  # default covered
    assert win == 5                                    # argmax
    assert edge is False


def test_continues_past_floor_when_still_rising():
    # Still rising at 8 → keep going; 10 declines → stop. Winner = 9 (max).
    p = _curve({3: 200.0, 4: 250.0, 5: 280.0, 6: 300.0, 7: 315.0, 8: 325.0,
                9: 330.0, 10: 320.0})
    win, curve, edge = select_buffer_count(p, start=3, floor_max=8, decline_eps=0.02)
    assert 9 in p.seen and win == 9
    assert edge is False


def test_no_continue_when_floor_already_peaked():
    # Peak within the floor (7); 8 lower → do NOT probe past 8.
    p = _curve({3: 200.0, 4: 260.0, 5: 300.0, 6: 320.0, 7: 330.0, 8: 325.0})
    win, curve, edge = select_buffer_count(p, start=3, floor_max=8)
    assert 9 not in p.seen
    assert win == 7


def test_winner_exact_tie_prefers_smaller():
    p = _curve({3: 200.0, 4: 305.0, 5: 305.0, 6: 300.0, 7: 299.0, 8: 298.0})
    win, curve, edge = select_buffer_count(p, start=3, floor_max=8)
    assert win == 4


def test_edge_flag_when_rising_at_cap():
    p = _curve({c: c * 10.0 for c in range(2, 17)})   # monotonic rise
    win, curve, edge = select_buffer_count(p, start=3, floor_max=8, max_probe=16)
    assert win == 16 and edge is True


def test_winner_equals_start_probes_below_once():
    # Highest across the floor is the start floor → probe one below; 2 is better.
    p = _curve({3: 300.0, 4: 298.0, 5: 297.0, 6: 296.0, 7: 295.0, 8: 294.0, 2: 305.0})
    win, curve, edge = select_buffer_count(p, start=3, floor_max=8)
    assert 2 in p.seen and win == 2


def _flaky_curve(mapping, zero_on_first=()):
    """Probe returns 0.0 on the FIRST call for c in *zero_on_first* (a transient
    device stall), then the real value on any retry."""
    calls = {}

    def probe(c):
        calls[c] = calls.get(c, 0) + 1
        if c in zero_on_first and calls[c] == 1:
            return 0.0
        return mapping[c]

    probe.calls = calls
    return probe


def test_transient_zero_probe_is_retried():
    # c=7 stalls to 0 on the first probe, returns the real 315 on retry.
    p = _flaky_curve({3: 200., 4: 250., 5: 280., 6: 300., 7: 315., 8: 325., 9: 330., 10: 320.},
                     zero_on_first=(7,))
    win, curve, edge = select_buffer_count(p, start=3, floor_max=8, zero_retries=1)
    assert curve[7] == 315.0     # retry recovered the real value (no stray 0 in the curve)
    assert p.calls[7] == 2       # probed twice: 0 then retry


def test_all_zero_returns_none_winner():
    # Every probe is 0 (device unresponsive) → no winner, so the caller can short-circuit
    # instead of "picking" the smallest buffer-count.
    p = _curve({c: 0.0 for c in range(1, 17)})
    win, curve, edge = select_buffer_count(p, start=3, floor_max=8, zero_retries=1)
    assert win is None


def test_transient_zero_at_floor_max_still_continues():
    # floor_max (8) stalls to 0 on first probe; retry recovers 325 → Phase 2 still continues.
    p = _flaky_curve({3: 200., 4: 250., 5: 280., 6: 300., 7: 315., 8: 325., 9: 330., 10: 320.},
                     zero_on_first=(8,))
    win, curve, edge = select_buffer_count(p, start=3, floor_max=8, zero_retries=1)
    assert curve[8] == 325.0
    assert 9 in p.calls and win == 9


def test_buffer_count_probe_retries_config_default():
    from benchmark.config import BenchmarkConfig
    assert BenchmarkConfig().buffer_count_probe_retries == 1


def test_aggregator_flattens_buffer_count():
    """buffer_count flows into the flattened dataset row."""
    from benchmark.aggregator import _flatten_model_results
    rows = [{"task": "object_detection", "size": "n", "model": "m", "use_ort": False,
             "family": "throughput", "fps": 300.0, "buffer_count": 5, "status": "ok"}]
    assert _flatten_model_results("r", "e", rows)[0]["buffer_count"] == 5

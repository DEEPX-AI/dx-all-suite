"""Throttle-flag semantics for NpuStats.as_dict.

`npu_throttled` means "the NPU clock ran below its nominal rated clock during
the measurement" — i.e. DVFS reduced frequency (thermal / power / etc.). The
reference is the *nominal* clock (DX-M1/M1M/H1 = 1000 MHz), NOT the peak clock
observed in that run — otherwise a chip pinned at a low clock the whole run
(clearly throttled) would go undetected.
"""
from benchmark.npu_monitor import NpuStats


def _stats(clock_min, clock_max, cores=(0,)):
    s = NpuStats()
    for c in cores:
        s.core_clock_min_mhz[c] = clock_min
        s.core_clock_max_mhz[c] = clock_max
        s.core_avg_pct[c] = 50.0
        s.core_max_pct[c] = 60.0
    return s


def test_throttled_when_clock_stuck_below_nominal():
    # Clock pinned at 800 MHz for the whole run — throttled vs 1000 nominal.
    # Old formula (min < 0.95*max) misses this (800 < 760 is False).
    d = _stats(800.0, 800.0).as_dict([0])
    assert d["npu_throttled"] is True


def test_not_throttled_at_full_clock():
    d = _stats(1000.0, 1000.0).as_dict([0])
    assert d["npu_throttled"] is False


def test_throttled_on_dip_below_nominal():
    d = _stats(900.0, 1000.0).as_dict([0])
    assert d["npu_throttled"] is True


def test_null_clock_stays_none():
    d = NpuStats().as_dict([0])  # no clock samples collected
    assert d["npu_throttled"] is None


def test_custom_nominal_clock_not_flagged():
    # A part rated at 800 MHz running at 800 is NOT throttled.
    d = _stats(800.0, 800.0).as_dict([0], nominal_clock_mhz=800)
    assert d["npu_throttled"] is False

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


# ── dxtop needs a terminal type ───────────────────────────────────────────

def _capture_popen_env(monkeypatch, term):
    from benchmark import npu_monitor

    seen = {}

    class _FakeProc:
        pid = 1

        def wait(self, timeout=None):
            return 0

    def _popen(cmd, **kw):
        seen["env"] = kw.get("env")
        return _FakeProc()

    if term is None:
        monkeypatch.delenv("TERM", raising=False)
    else:
        monkeypatch.setenv("TERM", term)
    monkeypatch.setattr(npu_monitor.shutil, "which", lambda n: f"/stub/{n}")
    monkeypatch.setattr(npu_monitor.subprocess, "Popen", _popen)
    monkeypatch.setattr(npu_monitor.time, "sleep", lambda s: None)
    mon = npu_monitor.NpuMonitor([0, 1, 2])
    mon.start()
    return seen["env"]


def test_dxtop_gets_a_terminal_type_when_launched_without_one(monkeypatch):
    """dxtop (ncurses) dies without a TERM, as in detached runs, so the monitor supplies one."""
    env = _capture_popen_env(monkeypatch, term=None)
    assert env is not None and env["TERM"] == "xterm"


def test_dxtop_replaces_a_dumb_terminal(monkeypatch):
    assert _capture_popen_env(monkeypatch, term="dumb")["TERM"] == "xterm"


def test_dxtop_keeps_a_real_terminal_type(monkeypatch):
    assert _capture_popen_env(monkeypatch, term="xterm-256color")["TERM"] == "xterm-256color"

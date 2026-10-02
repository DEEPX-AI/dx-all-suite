"""Unit tests for the `dxrun --max-throughput` output parser."""

from benchmark.runner_model import _parse_sweep, _parse_fps_from_log

# Real v3.5.0 output (staging a918c3da). yolo26-n, --buffer-count 3-6 --probe-time 2
SWEEP_LOG = """\
Searching I/O Buffer Count range=3-6
Runtime Framework Version: v3.5.0
Run model target mode : Max-Throughput Mode
Max-throughput sweep: start=3 step=1 cap=6 round-time=2s peak-drop-threshold=3% (patience 2, stall 3)
=== Model File: /path/yolo26-n_640x640.dxnn ===
[max-throughput] Measuring buffer-count=3 for 2s ...
[max-throughput] buffer-count=3 fps=100.83 loops=205
[max-throughput] Measuring buffer-count=4 for 2s ...
[max-throughput] buffer-count=4 fps=115.55 loops=236 improvement=14.59% peak-drop=0.00% stall=0
[max-throughput] Measuring buffer-count=5 for 2s ...
[max-throughput] buffer-count=5 fps=132.68 loops=271 improvement=14.83% peak-drop=0.00% stall=0
[max-throughput] Measuring buffer-count=6 for 2s ...
[max-throughput] buffer-count=6 fps=141.66 loops=290 improvement=6.76% peak-drop=0.00% stall=0
====================================================
* Max-Throughput Sweep Result
  Stop reason : reached buffer-count cap (6)

   buffer-count |        FPS |  improvement
  --------------+------------+-------------
              3 |     100.83 |          --
              4 |     115.55 |     +14.59%
              5 |     132.68 |     +14.83%
              6 |     141.66 |      +6.76%  <== best

  => Recommended buffer-count : 6
     Max FPS                  : 141.66  (loops=290)
====================================================

[max-throughput] Final run with buffer-count=6 ...
=============================================
* Benchmark Result (429 inputs)
  - FPS : 141.21
=============================================
"""

FAILED_LOG = """\
Searching I/O Buffer Count range=3-16
[max-throughput] Measuring buffer-count=3 for 10s ...
[max-throughput] buffer-count=3 fps=0.00 loops=0
[max-throughput] Measuring buffer-count=4 for 10s ...
[max-throughput] buffer-count=4 fps=0.00 loops=0 improvement=0.00% peak-drop=0.00% stall=1
[max-throughput] Measuring buffer-count=5 for 10s ...
[max-throughput] buffer-count=5 fps=0.00 loops=0 improvement=0.00% peak-drop=0.00% stall=2

[ERR] Max-throughput sweep completed but every round measured 0 fps; no buffer count can be recommended.
"""


def test_parse_sweep_extracts_winner_and_curve(capsys):
    winner, curve = _parse_sweep(SWEEP_LOG)
    assert winner == 6
    assert curve == {3: 100.83, 4: 115.55, 5: 132.68, 6: 141.66}
    # A healthy sweep must not trip the format-drift warning.
    assert "[WARN]" not in capsys.readouterr().out


def test_parse_sweep_returns_none_when_no_recommendation():
    winner, curve = _parse_sweep(FAILED_LOG)
    assert winner is None
    assert curve == {3: 0.0, 4: 0.0, 5: 0.0}


def test_parse_sweep_handles_empty_log():
    winner, curve = _parse_sweep("")
    assert winner is None
    assert curve == {}


# dxrun prints this when the very first round fails before any measurement.
# Distinct from FAILED_LOG: there are no round lines at all.
NO_ROUND_LOG = """\
Searching I/O Buffer Count range=3-16
[max-throughput] Measuring buffer-count=3 for 10s ...

[ERR] Max-throughput sweep produced no successful round: engine creation/run failed at buffer-count 3 (device open failed)
"""

# Hypothetical format drift: an extra field between buffer-count and fps.
# The winner line still parses, so the round lines silently vanish.
DRIFTED_LOG = """\
[max-throughput] buffer-count=3 core=0 fps=100.83 loops=205
  => Recommended buffer-count : 3
"""


def test_parse_sweep_handles_sweep_with_no_successful_round():
    """No round ever ran — distinct from 'ran but measured 0 fps'."""
    winner, curve = _parse_sweep(NO_ROUND_LOG)
    assert winner is None
    assert curve == {}


def test_parse_sweep_warns_when_winner_present_without_rounds(capsys):
    """A recommendation with zero parsed rounds can only mean format drift."""
    winner, curve = _parse_sweep(DRIFTED_LOG)
    assert winner == 3
    assert curve == {}
    assert "output format changed" in capsys.readouterr().out


def test_parse_sweep_does_not_crash_on_malformed_fps():
    """A malformed fps token must not raise — drift degrades, never crashes."""
    winner, curve = _parse_sweep("[max-throughput] buffer-count=3 fps=115.55.\n")
    assert winner is None
    assert curve == {3: 115.55}


def test_parse_fps_ignores_sweep_peak_line():
    """Max FPS (the sweep peak) must be ignored; only the result block counts."""
    assert _parse_fps_from_log(SWEEP_LOG) == 141.21


def test_parse_fps_reads_verbose_padded_form():
    """The space-padded form emitted by -v must parse too."""
    log = "  - NPU Processing Time  : 3.576 ms\n  - FPS                  : 98.40\n"
    assert _parse_fps_from_log(log) == 98.40


def test_parse_fps_averages_multiple_result_blocks():
    """Several result blocks average together (unchanged behaviour)."""
    log = "  - FPS : 100.00\n  - FPS : 120.00\n"
    assert _parse_fps_from_log(log) == 110.00


def test_parse_fps_returns_none_without_result_block():
    assert _parse_fps_from_log("no fps here") is None


def test_parse_fps_does_not_crash_on_malformed_token():
    """A trailing dot must degrade, not raise -- same hardening as _parse_sweep."""
    assert _parse_fps_from_log("  - FPS : 141.21.5\n") == 141.21


def test_parse_fps_returns_none_for_sweep_peak_only():
    """Sweep peak without a result block yields nothing -- proves the exclusion works."""
    assert _parse_fps_from_log("     Max FPS                  : 141.66  (loops=290)\n") is None

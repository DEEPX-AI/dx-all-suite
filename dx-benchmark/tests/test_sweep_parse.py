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


# dxrun v3.5.0 final output: each round repeats 3x; only the `avg-fps=` round line is a curve point.
AUTO_STOP_LOG = """\
Searching I/O Buffer Count range=3-100

[max-throughput] Measuring buffer-count=3 for 10s x 3 repeats ...
[max-throughput] buffer-count=3 repeat=1/3 fps=904.88 loops=9061
[max-throughput] buffer-count=3 repeat=2/3 fps=903.25 loops=9045
[max-throughput] buffer-count=3 repeat=3/3 fps=913.33 loops=9145
[max-throughput] buffer-count=3 avg-fps=907.15 total-loops=27251

[max-throughput] Measuring buffer-count=4 for 10s x 3 repeats ...
[max-throughput] buffer-count=4 repeat=1/3 fps=1082.14 loops=10837
[max-throughput] buffer-count=4 repeat=2/3 fps=1073.95 loops=10754
[max-throughput] buffer-count=4 repeat=3/3 fps=1086.07 loops=10877
[max-throughput] buffer-count=4 avg-fps=1080.72 total-loops=32468 improvement=19.13% peak-drop=0.00% stall=0

[max-throughput] Measuring buffer-count=5 for 10s x 3 repeats ...
[max-throughput] buffer-count=5 repeat=1/3 fps=1071.23 loops=10731
[max-throughput] buffer-count=5 repeat=2/3 fps=1053.81 loops=10556
[max-throughput] buffer-count=5 repeat=3/3 fps=1088.65 loops=10905
[max-throughput] buffer-count=5 avg-fps=1071.23 total-loops=32192 improvement=-0.88% peak-drop=0.88% stall=1

[max-throughput] Measuring buffer-count=6 for 10s x 3 repeats ...
[max-throughput] buffer-count=6 repeat=1/3 fps=1074.87 loops=10770
[max-throughput] buffer-count=6 repeat=2/3 fps=1101.95 loops=11041
[max-throughput] buffer-count=6 repeat=3/3 fps=1097.05 loops=10992
[max-throughput] buffer-count=6 avg-fps=1091.29 total-loops=32803 improvement=1.87% peak-drop=0.00% stall=2

[max-throughput] Measuring buffer-count=7 for 10s x 3 repeats ...
[max-throughput] buffer-count=7 repeat=1/3 fps=1069.84 loops=10723
[max-throughput] buffer-count=7 repeat=2/3 fps=1086.08 loops=10886
[max-throughput] buffer-count=7 repeat=3/3 fps=1062.95 loops=10653
[max-throughput] buffer-count=7 avg-fps=1072.95 total-loops=32262 improvement=-1.68% peak-drop=1.68% stall=3

==================================================
* Max-Throughput Sweep Result
  Stop reason : no gain above 1.00% for 3 consecutive rounds (peak 1091.29 fps at buffer-count 6)

  => Recommended buffer-count : 4
     Recommended FPS          : 1080.72
     Max FPS                  : 1091.29  (buffer-count=6, loops=32803)
==================================================
"""

# Killed mid-round: the half-measured round must not appear in the curve.
AUTO_STOP_PARTIAL_LOG = """\
[max-throughput] Measuring buffer-count=3 for 10s x 3 repeats ...
[max-throughput] buffer-count=3 repeat=1/3 fps=904.88 loops=9061
[max-throughput] buffer-count=3 repeat=2/3 fps=903.25 loops=9045
[max-throughput] buffer-count=3 repeat=3/3 fps=913.33 loops=9145
[max-throughput] buffer-count=3 avg-fps=907.15 total-loops=27251
[max-throughput] Measuring buffer-count=4 for 10s x 3 repeats ...
[max-throughput] buffer-count=4 repeat=1/3 fps=1082.14 loops=10837
"""


def test_parse_sweep_reads_round_average_from_final_v350_format(capsys):
    """The final build prints avg-fps per round; the curve is built from it."""
    winner, curve = _parse_sweep(AUTO_STOP_LOG)
    assert winner == 4  # smallest buffer count within tolerance of the peak, not the peak (6)
    assert curve == {3: 907.15, 4: 1080.72, 5: 1071.23, 6: 1091.29, 7: 1072.95}
    assert "[WARN]" not in capsys.readouterr().out


def test_parse_sweep_partial_final_format_keeps_only_completed_rounds():
    winner, curve = _parse_sweep(AUTO_STOP_PARTIAL_LOG)
    assert winner is None
    assert curve == {3: 907.15}

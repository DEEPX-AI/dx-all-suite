"""G1: CPU governor capture + neutral informational note.

The CPU frequency governor is recorded in the fingerprint for reproducibility.
We do NOT prescribe a governor: the benchmark reports whatever governor the host
actually uses (the representative, as-deployed number). The note, when present,
is purely factual — it must never nudge the user toward 'performance' mode.
"""
from benchmark.env_fingerprint import (
    _get_cpu_governors, check_cpu_governor, collect_fingerprint,
)


def _mk_cpu(base, gov_by_cpu):
    for cpu, gov in gov_by_cpu.items():
        d = base / cpu / "cpufreq"
        d.mkdir(parents=True)
        (d / "scaling_governor").write_text(gov + "\n")


def test_get_cpu_governors_counts_per_governor(tmp_path):
    _mk_cpu(tmp_path, {"cpu0": "performance", "cpu1": "performance"})
    assert _get_cpu_governors(str(tmp_path)) == {"performance": 2}


def test_get_cpu_governors_mixed(tmp_path):
    _mk_cpu(tmp_path, {"cpu0": "performance", "cpu1": "schedutil"})
    assert _get_cpu_governors(str(tmp_path)) == {"performance": 1, "schedutil": 1}


def test_get_cpu_governors_no_cpufreq_returns_empty(tmp_path):
    (tmp_path / "cpu0").mkdir(parents=True)   # no cpufreq/ subdir
    assert _get_cpu_governors(str(tmp_path)) == {}


def _assert_no_nudge(msg):
    """A governor note must never prescribe a governor / suggest a command."""
    assert "cpupower" not in msg
    assert "Set:" not in msg
    assert "-g performance" not in msg


def test_check_governor_note_is_neutral_for_performance():
    # Non-empty governors yield a factual note; even for 'performance' it must
    # not read as a prescription.
    msg = check_cpu_governor({"host": {"cpu_governors": {"performance": 8}}})
    if msg is not None:
        _assert_no_nudge(msg)


def test_check_governor_note_neutral_when_not_performance():
    msg = check_cpu_governor({"host": {"cpu_governors": {"schedutil": 8}}})
    assert msg is not None
    assert "schedutil" in msg
    _assert_no_nudge(msg)


def test_check_governor_note_when_mixed():
    assert check_cpu_governor({"host": {"cpu_governors": {"performance": 4, "powersave": 4}}}) is not None


def test_check_governor_none_when_unknown():
    # cpufreq unavailable → empty → nothing to report.
    assert check_cpu_governor({"host": {"cpu_governors": {}}}) is None
    assert check_cpu_governor({"host": {}}) is None


def test_fingerprint_host_carries_cpu_governors():
    fp = collect_fingerprint()
    assert "cpu_governors" in fp["host"]
    assert isinstance(fp["host"]["cpu_governors"], dict)

from pathlib import Path
from benchmark.aggregator import _build_snapshot, _build_environment_summary


def test_environment_summary_carries_version():
    fp = {"dx_all_suite_version": "v2.4.0", "host": {}, "npu": {}, "software": {}}
    env = _build_environment_summary("hw1", "run1", fp)
    assert env["dx_all_suite_version"] == "v2.4.0"


def test_snapshot_carries_version():
    fp = {"dx_all_suite_version": "v2.4.0", "host": {}, "npu": {},
          "software": {}, "timestamp": "2026-04-21T00:00:00"}
    snap = _build_snapshot("hw1", "run1", fp, [], [], [], 30.0, Path("/tmp"))
    assert snap["dx_all_suite_version"] == "v2.4.0"
    assert snap["environment"]["dx_all_suite_version"] == "v2.4.0"


def test_snapshot_version_none_when_absent():
    fp = {"host": {}, "npu": {}, "software": {}, "timestamp": "t"}
    snap = _build_snapshot("hw1", "run1", fp, [], [], [], 30.0, Path("/tmp"))
    assert snap["dx_all_suite_version"] is None


def test_snapshot_carries_protocol_version():
    """The Version Trend snapshot must carry the protocol block.

    Without it a v1 run and a v2 run look identical in the trend, so a
    protocol change reads as a performance change.
    """
    fp = {
        "dx_all_suite_version": "v2.5.0",
        "timestamp": "2026-09-29T10:00:00",
        "host": {}, "npu": {}, "software": {},
        "protocol": {"version": "v2", "bc_range_lo": 3, "bc_range_hi": 16},
    }
    snap = _build_snapshot("hw1", "run1", fp, [], [], [], 30.0, Path("/tmp"))
    assert snap["protocol"]["version"] == "v2"

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

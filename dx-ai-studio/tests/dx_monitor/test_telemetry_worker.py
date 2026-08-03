"""Unit tests for the isolated DX Monitor telemetry worker."""
import ast
import io
import json
import sys
from pathlib import Path

import pytest


_WORKER_PATH = (
    Path(__file__).resolve().parents[2]
    / "dx_monitor"
    / "core"
    / "telemetry_worker.py"
)


def _worker():
    """Import the worker only after asserting the TDD implementation target exists."""
    assert _WORKER_PATH.is_file(), "telemetry worker implementation is missing"
    from core import telemetry_worker
    return telemetry_worker


class _FakeStatus(object):
    def __init__(self, valid=True):
        self._valid = valid

    def get_id(self):
        return 7

    def is_valid(self):
        return self._valid

    def get_temperature(self, channel):
        return [41, 43, 45, -32768][channel]

    def get_npu_voltage(self, channel):
        return [700, 710, 720][channel]

    def get_npu_clock(self, channel):
        return [900, 950, 1000][channel]

    def get_core_utilization(self, channel):
        return [25, -1, 75][channel]

    def get_memory_used(self):
        return 64 * 1024 * 1024

    def get_memory_free(self):
        return 192 * 1024 * 1024


class _FakeDeviceStatus(object):
    def __init__(self, valid=True):
        self._status = _FakeStatus(valid=valid)

    def get_device_count(self):
        return 1

    def get_current_status(self, device_id):
        assert device_id == 0
        return self._status


class _FakeDeviceStatusAPI(object):
    """Match the runtime's class-method API used by ``main``."""

    _status = _FakeStatus()

    @classmethod
    def get_device_count(cls):
        return 1

    @classmethod
    def get_current_status(cls, device_id):
        assert device_id == 0
        return cls._status


class _NoVoltageStatus(_FakeStatus):
    def get_npu_voltage(self, channel):
        return [None, -1, float("nan")][channel]


class _NoVoltageDeviceStatus(_FakeDeviceStatus):
    def __init__(self):
        self._status = _NoVoltageStatus()


class _FakeConfiguration(object):
    def __init__(self):
        self.calls = 0

    def get_version(self):
        self.calls += 1
        return "sdk-1"

    def get_driver_version(self):
        self.calls += 1
        return "driver-2"

    def get_pcie_driver_version(self):
        self.calls += 1
        return "pcie-3"


def _frame(line, worker):
    assert line.startswith(worker.FRAME_PREFIX)
    assert line.endswith("\n")
    assert line.count("\n") == 1
    return json.loads(line[len(worker.FRAME_PREFIX):-1])


def test_build_snapshot_normalizes_real_device_status_without_sentinels():
    worker = _worker()

    snapshot = worker.build_snapshot(_FakeDeviceStatus(), timestamp=123.5)

    assert snapshot["schema_version"] == worker.SCHEMA_VERSION
    assert snapshot["kind"] == "snapshot"
    assert snapshot["available"] is True
    assert snapshot["timestamp"] == 123.5
    assert snapshot["ts"] == 123.5
    assert snapshot["source"] == "device_status"
    assert snapshot["source_mode"] == "real"
    assert snapshot["stale"] is False
    assert snapshot["sequence"] == 0
    assert snapshot["count"] == 1
    assert len(snapshot["npus"]) == 1

    npu = snapshot["npus"][0]
    assert npu["id"] == 0
    assert npu["device_id"] == 7
    assert npu["cores"] == 3
    assert npu["temperatures"] == [41, 43, 45]
    assert npu["voltages_mV"] == [700, 710, 720]
    assert npu["clocks_MHz"] == [900, 950, 1000]
    assert npu["utilization"] == [25.0, 75.0]
    assert npu["temp_avg"] == 43.0
    assert npu["voltage_avg"] == 710.0
    assert npu["clock_avg"] == 950.0
    assert npu["power_est_mW"] == 355.0
    assert npu["dram_used_bytes"] == 64 * 1024 * 1024
    assert npu["dram_free_bytes"] == 192 * 1024 * 1024
    assert npu["dram_total_bytes"] == 256 * 1024 * 1024
    assert npu["dram_used_mb"] == 64.0
    assert npu["dram_total_mb"] == 256.0
    assert npu["dram_pct"] == 25.0
    assert worker.INVALID_TEMPERATURE not in npu["temperatures"]
    assert all(value >= 0 for value in npu["utilization"])


def test_build_snapshot_marks_invalid_status_as_stale():
    worker = _worker()

    snapshot = worker.build_snapshot(_FakeDeviceStatus(valid=False), timestamp=5.0)

    assert snapshot["available"] is True
    assert snapshot["source"] == "device_status"
    assert snapshot["source_mode"] == "stale"
    assert snapshot["stale"] is True
    assert snapshot["npus"][0]["temperatures"] == [41, 43, 45]


def test_build_snapshot_sequence_is_explicit_and_has_no_hidden_global_state():
    worker = _worker()

    first = worker.build_snapshot(_FakeDeviceStatus(), timestamp=1.0, sequence=4)
    second = worker.build_snapshot(_FakeDeviceStatus(), timestamp=2.0, sequence=5)
    default_first = worker.build_snapshot(_FakeDeviceStatus(), timestamp=3.0)
    default_second = worker.build_snapshot(_FakeDeviceStatus(), timestamp=4.0)

    assert first["sequence"] == 4
    assert second["sequence"] == 5
    assert default_first["sequence"] == 0
    assert default_second["sequence"] == 0


def test_build_snapshot_preserves_no_data_power_semantics_without_valid_voltage():
    worker = _worker()

    npu = worker.build_snapshot(
        _NoVoltageDeviceStatus(), timestamp=1.0
    )["npus"][0]

    assert npu["voltages_mV"] == []
    assert npu["voltage_avg"] == 0.0
    assert npu["power_est_mW"] is None


def test_emit_writes_one_compact_framed_json_record():
    worker = _worker()
    stream = io.StringIO()

    worker.emit(
        "snapshot",
        {
            "source": "device_status",
            "source_mode": "real",
            "npus": [],
        },
        stream=stream,
    )

    record = _frame(stream.getvalue(), worker)
    assert record == {
        "schema_version": worker.SCHEMA_VERSION,
        "kind": "snapshot",
        "source": "device_status",
        "source_mode": "real",
        "npus": [],
    }
    assert ", " not in stream.getvalue()


def test_emit_flushes_the_framed_record():
    worker = _worker()

    class _FlushTrackingStream(object):
        def __init__(self):
            self.value = ""
            self.flush_calls = 0

        def write(self, value):
            self.value += value

        def flush(self):
            self.flush_calls += 1

    stream = _FlushTrackingStream()
    worker.emit("hello", {"npus": []}, stream=stream)

    assert _frame(stream.value, worker)["kind"] == "hello"
    assert stream.flush_calls == 1


def test_collect_system_info_caches_only_version_fields(monkeypatch):
    worker = _worker()
    configuration = _FakeConfiguration()

    monkeypatch.setattr(worker, "_SYSTEM_INFO_CACHE", None)

    first = worker.collect_system_info(configuration)
    second = worker.collect_system_info(configuration)

    assert first == {
        "sdk_version": "sdk-1",
        "driver_version": "driver-2",
        "pcie_driver_version": "pcie-3",
    }
    assert second == first
    assert first is not second
    assert configuration.calls == 3


@pytest.mark.parametrize(
    ("method_name", "missing_field"),
    [
        ("get_version", "sdk_version"),
        ("get_driver_version", "driver_version"),
        ("get_pcie_driver_version", "pcie_driver_version"),
    ],
)
def test_collect_system_info_keeps_other_versions_when_optional_getter_fails(
    monkeypatch, method_name, missing_field
):
    worker = _worker()

    def fail_optional_version(_self):
        raise RuntimeError("optional version unavailable")

    monkeypatch.setattr(worker, "_SYSTEM_INFO_CACHE", None)
    monkeypatch.setattr(_FakeConfiguration, method_name, fail_optional_version)

    system_info = worker.collect_system_info(_FakeConfiguration())

    assert system_info[missing_field] == "N/A"
    assert system_info["sdk_version"] == (
        "N/A" if missing_field == "sdk_version" else "sdk-1"
    )
    assert system_info["driver_version"] == (
        "N/A" if missing_field == "driver_version" else "driver-2"
    )
    assert system_info["pcie_driver_version"] == (
        "N/A" if missing_field == "pcie_driver_version" else "pcie-3"
    )


@pytest.mark.parametrize(
    ("method_name", "missing_field"),
    [
        ("get_version", "sdk_version"),
        ("get_driver_version", "driver_version"),
        ("get_pcie_driver_version", "pcie_driver_version"),
    ],
)
def test_main_emits_hello_and_snapshot_when_optional_version_getter_fails(
    monkeypatch, method_name, missing_field
):
    worker = _worker()
    stream = io.StringIO()

    class _NoOpDispatcher(object):
        def register_event_handler(self, _handler):
            pass

    class _OptionalFailureConfiguration(_FakeConfiguration):
        pass

    def fail_optional_version(_self):
        raise RuntimeError("optional version unavailable")

    def stop_after_first_snapshot(_interval):
        raise KeyboardInterrupt()

    monkeypatch.setattr(worker, "_SYSTEM_INFO_CACHE", None)
    monkeypatch.setattr(
        _OptionalFailureConfiguration, method_name, fail_optional_version
    )
    monkeypatch.setattr(
        worker,
        "_load_runtime_api",
        lambda: (_FakeDeviceStatusAPI, _OptionalFailureConfiguration, _NoOpDispatcher),
    )
    monkeypatch.setattr(worker.sys, "stdout", stream)
    monkeypatch.setattr(worker.time, "sleep", stop_after_first_snapshot)

    assert worker.main([]) == 0

    records = [_frame(line, worker) for line in stream.getvalue().splitlines(True)]
    assert [record["kind"] for record in records] == [
        "hello",
        "snapshot",
        "stopped",
    ]
    assert records[0]["system_info"][missing_field] == "N/A"
    assert records[1]["available"] is True


def test_main_frames_unavailable_error_when_runtime_import_fails(monkeypatch):
    worker = _worker()
    stream = io.StringIO()

    def fail_runtime_import():
        raise ImportError("runtime API unavailable")

    monkeypatch.setattr(worker, "_load_runtime_api", fail_runtime_import)
    monkeypatch.setattr(worker.sys, "stdout", stream)

    assert worker.main([]) == 1

    record = _frame(stream.getvalue(), worker)
    assert record["schema_version"] == worker.SCHEMA_VERSION
    assert record["kind"] == "error"
    assert record["available"] is False
    assert record["source"] == "device_status"
    assert record["source_mode"] == "unavailable"
    assert "runtime API unavailable" in record["error"]


@pytest.mark.parametrize("value", ["inf", "nan"])
def test_main_rejects_non_finite_interval_before_runtime_setup(monkeypatch, capsys, value):
    worker = _worker()

    def unexpected_runtime_import():
        raise AssertionError("runtime imports must not run for invalid arguments")

    monkeypatch.setattr(worker, "_load_runtime_api", unexpected_runtime_import)

    with pytest.raises(SystemExit) as error:
        worker.main(["--interval", value])

    assert error.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "argument --interval:" in captured.err


def test_main_clamps_interval_and_emits_framed_hello_event_snapshot_and_stopped(monkeypatch):
    worker = _worker()
    stream = io.StringIO()
    emitted_kinds = []
    original_emit = worker.emit

    class _EventDispatcher(object):
        def register_event_handler(self, handler):
            handler("warning", "thermal", 7, "threshold", 9.0)

    def capture_emit(kind, payload, stream=None):
        emitted_kinds.append(kind)
        original_emit(kind, payload, stream=stream_output)

    def stop_after_first_sleep(interval):
        assert interval == 1.0
        raise KeyboardInterrupt()

    stream_output = stream
    monkeypatch.setattr(
        worker,
        "_load_runtime_api",
        lambda: (_FakeDeviceStatusAPI, _FakeConfiguration, _EventDispatcher),
    )
    monkeypatch.setattr(worker, "_SYSTEM_INFO_CACHE", None)
    monkeypatch.setattr(worker, "emit", capture_emit)
    monkeypatch.setattr(worker.time, "sleep", stop_after_first_sleep)

    assert worker.main(["--interval", "0.01"]) == 0

    records = [_frame(line, worker) for line in stream.getvalue().splitlines(True)]
    assert emitted_kinds == ["hello", "event", "snapshot", "stopped"]
    assert [record["kind"] for record in records] == emitted_kinds
    assert records[2]["sequence"] == 0
    assert records[2]["stale"] is False


def test_main_tolerates_event_registration_failure(monkeypatch):
    worker = _worker()
    emitted_kinds = []

    class _BrokenEventDispatcher(object):
        def register_event_handler(self, handler):
            raise RuntimeError("event registration unavailable")

    def capture_emit(kind, payload, stream=None):
        emitted_kinds.append(kind)

    monkeypatch.setattr(
        worker,
        "_load_runtime_api",
        lambda: (_FakeDeviceStatusAPI, _FakeConfiguration, _BrokenEventDispatcher),
    )
    monkeypatch.setattr(worker, "_SYSTEM_INFO_CACHE", None)
    monkeypatch.setattr(worker, "emit", capture_emit)
    monkeypatch.setattr(
        worker.time, "sleep", lambda interval: (_ for _ in ()).throw(KeyboardInterrupt())
    )

    assert worker.main([]) == 0
    assert emitted_kinds == ["hello", "snapshot", "stopped"]


def test_main_emits_error_then_continues_sampling(monkeypatch):
    worker = _worker()
    emitted = []
    snapshots = []
    sleep_calls = []

    class _NoopEventDispatcher(object):
        def register_event_handler(self, handler):
            return None

    def capture_emit(kind, payload, stream=None):
        emitted.append((kind, payload))

    def sample(device_status, timestamp, sequence=0):
        snapshots.append(sequence)
        if len(snapshots) == 1:
            raise RuntimeError("sample failed")
        return {
            "available": True,
            "source": "device_status",
            "source_mode": "real",
            "stale": False,
            "sequence": sequence,
            "npus": [],
        }

    def sleep_then_stop(interval):
        sleep_calls.append(interval)
        if len(sleep_calls) == 2:
            raise KeyboardInterrupt()

    monkeypatch.setattr(
        worker,
        "_load_runtime_api",
        lambda: (_FakeDeviceStatusAPI, _FakeConfiguration, _NoopEventDispatcher),
    )
    monkeypatch.setattr(worker, "_SYSTEM_INFO_CACHE", None)
    monkeypatch.setattr(worker, "build_snapshot", sample)
    monkeypatch.setattr(worker, "emit", capture_emit)
    monkeypatch.setattr(worker.time, "sleep", sleep_then_stop)

    assert worker.main([]) == 0

    assert [kind for kind, _ in emitted] == ["hello", "error", "snapshot", "stopped"]
    assert "sample failed" in emitted[1][1]["error"]
    assert snapshots == [0, 0]
    assert sleep_calls == [1.0, 1.0]


def test_native_runtime_imports_are_deferred_until_worker_helper_execution():
    tree = ast.parse(_WORKER_PATH.read_text(encoding="utf-8"))

    top_level_imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            top_level_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top_level_imports.append(node.module)

    assert not any(name.startswith("dx_engine") for name in top_level_imports)
    runtime_loader = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_load_runtime_api"
    )
    assert any(
        isinstance(node, ast.ImportFrom) and node.module.startswith("dx_engine")
        for node in ast.walk(runtime_loader)
    )
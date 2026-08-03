"""Unit tests for the Studio-side isolated telemetry supervisor."""
import ast
import errno
import io
import json
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path


_SUPERVISOR_PATH = (
    Path(__file__).resolve().parents[2]
    / "dx_monitor"
    / "core"
    / "telemetry_supervisor.py"
)


def _supervisor_module():
    """Import only after proving the TDD implementation target is absent/present."""
    assert _SUPERVISOR_PATH.is_file(), "telemetry supervisor implementation is missing"
    from core import telemetry_supervisor
    return telemetry_supervisor


def _frame(kind, **payload):
    record = {
        "schema_version": 1,
        "kind": kind,
    }
    record.update(payload)
    return "__DXTELEMETRY__" + json.dumps(record) + "\n"


class _FakeProcess(object):
    def __init__(self, lines=(), returncode=0, pid=43210, wait_results=()):
        self.stdout = io.StringIO("".join(lines))
        self.returncode = returncode
        self.pid = pid
        self.wait_calls = []
        self._wait_results = list(wait_results)

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        self.wait_calls.append(timeout)
        if self._wait_results:
            result = self._wait_results.pop(0)
            if isinstance(result, BaseException):
                raise result
            return result
        if self.returncode is None:
            raise subprocess.TimeoutExpired("telemetry-worker", timeout)
        return self.returncode


class _FakeTrackedProcessGroup(object):
    """Model a process group whose child survives the leader's exit."""

    def __init__(self, process):
        self._process = process
        self.signals = []
        self.descendant_alive = True

    def killpg(self, group_id, sig):
        assert group_id == self._process.pid
        self.signals.append((group_id, sig))
        if sig == signal.SIGKILL:
            self.descendant_alive = False


class _FakeThread(object):
    def __init__(self):
        self.join_calls = []

    def join(self, timeout=None):
        self.join_calls.append(timeout)


class _FakeTimer(object):
    created = []

    def __init__(self, delay, callback):
        self.delay = delay
        self.callback = callback
        self.cancelled = False
        self.started = False
        self.__class__.created.append(self)

    def start(self):
        self.started = True

    def cancel(self):
        self.cancelled = True

    def fire(self):
        self.callback()


class _PopenFactory(object):
    def __init__(self, processes):
        self.processes = list(processes)
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        return self.processes.pop(0)


class _BlockingPopenFactory(object):
    def __init__(self, process):
        self.process = process
        self.calls = []
        self.entered = threading.Event()
        self.release = threading.Event()

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        self.entered.set()
        assert self.release.wait(timeout=1.0)
        return self.process


class _BoundedReadStream(object):
    """Text stream that rejects iterator-based or oversized reads."""

    def __init__(self, data, maximum_read):
        self._data = data
        self._maximum_read = maximum_read
        self._position = 0
        self.read_sizes = []

    def read(self, size=-1):
        assert 0 <= size <= self._maximum_read
        self.read_sizes.append(size)
        chunk = self._data[self._position:self._position + size]
        self._position += len(chunk)
        return chunk

    def readline(self, size=-1):
        assert 0 <= size <= self._maximum_read
        self.read_sizes.append(size)
        if self._position >= len(self._data):
            return ""
        end = min(self._position + size, len(self._data))
        newline = self._data.find("\n", self._position, end)
        if newline >= 0:
            end = newline + 1
        chunk = self._data[self._position:end]
        self._position = end
        return chunk

    def __iter__(self):
        raise AssertionError("reader must use bounded read() calls")


def _worker_script(tmp_path):
    script = tmp_path / "telemetry_worker.py"
    script.write_text("# fake worker path\n", encoding="utf-8")
    return script


def test_unstarted_system_info_uses_unavailable_version_defaults():
    """An unstarted supervisor preserves the shared hardware N/A contract."""
    supervisor_module = _supervisor_module()
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )

    info = supervisor.system_info()

    assert info["available"] is False
    assert info["npu_count"] == 0
    assert info["sdk_version"] == "N/A"
    assert info["driver_version"] == "N/A"
    assert info["pcie_driver_version"] == "N/A"


def test_parse_frame_rejects_invalid_protocol_without_raising():
    supervisor_module = _supervisor_module()
    parse_frame = supervisor_module.TelemetrySupervisor.parse_frame

    invalid_lines = [
        "ordinary worker stderr\n",
        "__DXTELEMETRY__{not-json}\n",
        _frame(
            "snapshot",
            schema_version=2,
            available=True,
            source="device_status",
            source_mode="real",
            timestamp=1.0,
            ts=1.0,
            stale=False,
            sequence=0,
            npus=[],
        ),
        "__DXTELEMETRY__" + json.dumps({"schema_version": 1}) + "\n",
        _frame("unknown", available=True, source_mode="real", npus=[]),
        _frame("hello", available=True, source_mode="real", npus=[], system_info=[]),
        _frame(
            "snapshot",
            available=True,
            source=1,
            source_mode="real",
            timestamp=1.0,
            ts=1.0,
            stale=False,
            sequence=0,
            npus=[],
        ),
        _frame(
            "snapshot",
            available=True,
            source="device_status",
            source_mode="real",
            timestamp="1.0",
            ts=1.0,
            stale=False,
            sequence=0,
            npus=[],
        ),
        _frame(
            "snapshot",
            available=True,
            source="device_status",
            source_mode="real",
            timestamp=1.0,
            ts=True,
            stale=False,
            sequence=0,
            npus=[],
        ),
        _frame(
            "snapshot",
            available=True,
            source="device_status",
            source_mode="real",
            timestamp=1.0,
            ts=1.0,
            stale=0,
            sequence=0,
            npus=[],
        ),
        _frame(
            "snapshot",
            available=True,
            source="device_status",
            source_mode="real",
            timestamp=1.0,
            ts=1.0,
            stale=False,
            sequence=True,
            npus=[],
        ),
        _frame(
            "snapshot",
            available=True,
            source="device_status",
            source_mode="real",
            timestamp=1.0,
            ts=1.0,
            stale=False,
            sequence=0,
            npus={},
        ),
        _frame("hello", available=True, source_mode="real", npus=[], system_info=[]),
        _frame(
            "event",
            available=True,
            source_mode="real",
            npus=[],
            event={"timestamp": "not-a-number", "level": "warning", "message": "hot"},
        ),
        _frame(
            "event",
            available=True,
            source_mode="real",
            npus=[],
            event={"timestamp": 1.0, "level": True, "message": "hot"},
        ),
        _frame(
            "event",
            available=True,
            source_mode="real",
            npus=[],
            event={"timestamp": 1.0, "level": "warning", "message": 1},
        ),
        _frame("error", available=False, source_mode="real", npus=[], error="bad state"),
        _frame(
            "error", available=False, source_mode="unavailable", npus=[], error=1
        ),
        _frame(
            "stopped", available=True, source_mode="real", npus=[], message=[]
        ),
    ]

    for line in invalid_lines:
        assert parse_frame(line) is None


def test_parse_frame_requires_string_source_for_all_worker_frame_kinds():
    supervisor_module = _supervisor_module()
    parse_frame = supervisor_module.TelemetrySupervisor.parse_frame

    records = [
        {
            "schema_version": 1,
            "kind": "hello",
            "available": True,
            "source": "device_status",
            "source_mode": "real",
            "npus": [],
            "system_info": {},
        },
        {
            "schema_version": 1,
            "kind": "event",
            "available": True,
            "source": "runtime_event_dispatcher",
            "source_mode": "real",
            "npus": [],
            "event": {"timestamp": 1.0, "level": "info", "message": "ready"},
        },
        {
            "schema_version": 1,
            "kind": "error",
            "available": False,
            "source": "device_status",
            "source_mode": "stale",
            "npus": [],
            "error": "sampling failed",
        },
        {
            "schema_version": 1,
            "kind": "stopped",
            "available": True,
            "source": "device_status",
            "source_mode": "real",
            "npus": [],
        },
    ]

    for record in records:
        missing_source = dict(record)
        del missing_source["source"]
        wrong_source = dict(record)
        wrong_source["source"] = 1
        assert parse_frame("__DXTELEMETRY__" + json.dumps(missing_source)) is None
        assert parse_frame("__DXTELEMETRY__" + json.dumps(wrong_source)) is None


def test_parse_frame_requires_non_boolean_non_negative_snapshot_count():
    supervisor_module = _supervisor_module()
    parse_frame = supervisor_module.TelemetrySupervisor.parse_frame
    snapshot = {
        "schema_version": 1,
        "kind": "snapshot",
        "available": True,
        "source": "device_status",
        "source_mode": "real",
        "timestamp": 1.0,
        "ts": 1.0,
        "stale": False,
        "sequence": 0,
        "count": 0,
        "npus": [],
    }

    missing_count = dict(snapshot)
    del missing_count["count"]
    assert parse_frame("__DXTELEMETRY__" + json.dumps(missing_count)) is None
    for invalid_count in (True, -1, 1.0, "1"):
        invalid_snapshot = dict(snapshot)
        invalid_snapshot["count"] = invalid_count
        assert parse_frame("__DXTELEMETRY__" + json.dumps(invalid_snapshot)) is None


def test_parse_frame_accepts_complete_worker_records():
    supervisor_module = _supervisor_module()
    parse_frame = supervisor_module.TelemetrySupervisor.parse_frame

    records = [
        {
            "schema_version": 1,
            "kind": "hello",
            "available": True,
            "source": "device_status",
            "source_mode": "real",
            "npus": [],
            "system_info": {"sdk_version": "1.0"},
        },
        {
            "schema_version": 1,
            "kind": "snapshot",
            "available": True,
            "source": "device_status",
            "source_mode": "stale",
            "timestamp": 10.0,
            "ts": 10.0,
            "stale": True,
            "sequence": 2,
            "count": 1,
            "npus": [{"id": 0}],
        },
        {
            "schema_version": 1,
            "kind": "event",
            "available": True,
            "source": "runtime_event_dispatcher",
            "source_mode": "real",
            "npus": [],
            "event": {"timestamp": 11.0, "level": "warning", "message": "hot"},
        },
        {
            "schema_version": 1,
            "kind": "error",
            "available": False,
            "source": "device_status",
            "source_mode": "unavailable",
            "npus": [],
            "error": "runtime API unavailable",
        },
        {
            "schema_version": 1,
            "kind": "error",
            "available": False,
            "source": "device_status",
            "source_mode": "stale",
            "npus": [],
            "error": "sampling failed",
        },
        {
            "schema_version": 1,
            "kind": "stopped",
            "available": True,
            "source": "device_status",
            "source_mode": "real",
            "npus": [],
        },
    ]

    for record in records:
        assert parse_frame("__DXTELEMETRY__" + json.dumps(record)) == record


def test_reader_stream_updates_snapshot_events_and_system_info(monkeypatch, tmp_path):
    supervisor_module = _supervisor_module()
    worker = _worker_script(tmp_path)
    process = _FakeProcess(lines=[
        _frame(
            "hello",
            available=True,
            source="device_status",
            source_mode="real",
            npus=[],
            system_info={"sdk_version": "sdk-1", "driver_version": "driver-2"},
        ),
        _frame(
            "snapshot",
            available=True,
            source_mode="stale",
            timestamp=10.0,
            ts=10.0,
            source="device_status",
            stale=True,
            sequence=0,
            count=1,
            npus=[{"id": 0, "temperatures": [42]}],
        ),
        _frame(
            "event",
            available=True,
            source="runtime_event_dispatcher",
            source_mode="real",
            npus=[],
            event={
                "timestamp": 11.0,
                "level": "warning",
                "type": "thermal",
                "message": "warning",
            },
        ),
    ])
    popen = _PopenFactory([process])
    worker_env = {"WORKER_ONLY": "1"}

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", popen)
    monkeypatch.setattr(
        supervisor_module.runtime, "telemetry_worker_env", lambda python: worker_env
    )

    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script=worker, interval=1.5
    )
    supervisor._schedule_restart = lambda: None
    supervisor.start()
    supervisor._reader.join(timeout=1)

    command, kwargs = popen.calls[0]
    assert command == ["/runtime/python", str(worker), "--interval", "1.5"]
    assert kwargs == {
        "stdout": supervisor_module.subprocess.PIPE,
        "stderr": supervisor_module.subprocess.STDOUT,
        "env": worker_env,
        "start_new_session": True,
    }

    snapshot = supervisor.snapshot()
    assert snapshot["available"] is False
    assert snapshot["source_mode"] == "unavailable"
    assert snapshot["npus"] == []
    assert supervisor.events(since=0) == [
        {
            "timestamp": 11.0,
            "time": 11.0,
            "level": "warning",
            "type": "thermal",
            "message": "warning",
        }
    ]
    assert supervisor.system_info()["sdk_version"] == "sdk-1"
    assert supervisor.system_info()["driver_version"] == "driver-2"

    snapshot["npus"].append({"id": "mutated"})
    returned_events = supervisor.events(since=0)
    returned_events[0]["message"] = "mutated"
    returned_info = supervisor.system_info()
    returned_info["sdk_version"] = "mutated"
    assert supervisor.snapshot()["npus"] == []
    assert supervisor.events(since=0)[0]["message"] == "warning"
    assert supervisor.system_info()["sdk_version"] == "sdk-1"


def test_error_frame_exposes_unavailable_without_mock_np_us(monkeypatch, tmp_path):
    supervisor_module = _supervisor_module()
    worker = _worker_script(tmp_path)
    process = _FakeProcess(lines=[
        _frame(
            "error",
            available=False,
            source="device_status",
            source_mode="unavailable",
            npus=[],
            error="runtime API unavailable",
        ),
    ])

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", _PopenFactory([process]))
    monkeypatch.setattr(
        supervisor_module.runtime, "telemetry_worker_env", lambda python: {}
    )
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script=worker
    )
    supervisor._schedule_restart = lambda: None
    supervisor.start()
    supervisor._reader.join(timeout=1)

    snapshot = supervisor.snapshot()
    assert snapshot["available"] is False
    assert snapshot["source_mode"] == "unavailable"
    assert snapshot["npus"] == []
    assert "mock" not in snapshot
    assert any(
        "runtime API unavailable" in item for item in snapshot["diagnostics"]
    )

    for number in range(150):
        supervisor._record_diagnostic("diagnostic-{0}".format(number))
    diagnostics = supervisor.snapshot()["diagnostics"]
    assert len(diagnostics) == 100
    assert diagnostics[0] == "diagnostic-50"
    assert diagnostics[-1] == "diagnostic-149"


def test_stale_error_frame_caches_unavailable_snapshot_with_origin_diagnostic():
    supervisor_module = _supervisor_module()
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    frame = {
        "schema_version": 1,
        "kind": "error",
        "available": False,
        "source": "device_status",
        "source_mode": "stale",
        "npus": [],
        "error": "sampling failed",
    }

    assert supervisor_module.TelemetrySupervisor.parse_frame(
        "__DXTELEMETRY__" + json.dumps(frame)
    ) == frame
    supervisor._handle_frame(frame)

    snapshot = supervisor.snapshot()
    assert snapshot["available"] is False
    assert snapshot["source_mode"] == "unavailable"
    assert snapshot["npus"] == []
    assert snapshot["source"] == "device_status"
    assert any("sampling failed" in item for item in snapshot["diagnostics"])
    assert any("source_mode=stale" in item for item in snapshot["diagnostics"])


def test_events_are_bounded_and_filtered_by_timestamp():
    supervisor_module = _supervisor_module()
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )

    for number in range(205):
        supervisor._handle_frame({
            "schema_version": 1,
            "kind": "event",
            "available": True,
            "source_mode": "real",
            "npus": [],
            "event": {
                "timestamp": float(number),
                "level": "info",
                "message": "event-{0}".format(number),
            },
        })

    events = supervisor.events(since=100.0, limit=3)
    assert len(supervisor.events(since=0, limit=500)) == 200
    assert events == [
        {"timestamp": 101.0, "time": 101.0, "level": "info", "message": "event-101"},
        {"timestamp": 102.0, "time": 102.0, "level": "info", "message": "event-102"},
        {"timestamp": 103.0, "time": 103.0, "level": "info", "message": "event-103"},
    ]


def test_start_without_runtime_does_not_spawn_and_reports_unavailable(monkeypatch, tmp_path):
    supervisor_module = _supervisor_module()
    popen = _PopenFactory([])
    monkeypatch.setattr(supervisor_module.runtime, "telemetry_python", lambda: None)
    monkeypatch.setattr(supervisor_module.subprocess, "Popen", popen)

    supervisor = supervisor_module.TelemetrySupervisor(worker_script=_worker_script(tmp_path))
    supervisor.start()

    assert popen.calls == []
    snapshot = supervisor.snapshot()
    assert snapshot["available"] is False
    assert snapshot["source_mode"] == "unavailable"
    assert snapshot["npus"] == []
    assert "No telemetry-compatible runtime Python" in snapshot["diagnostics"]


def test_start_copies_worker_environment_without_mutating_parent(monkeypatch, tmp_path):
    supervisor_module = _supervisor_module()
    worker = _worker_script(tmp_path)
    process = _FakeProcess(returncode=None)
    popen = _PopenFactory([process])
    supplied_environment = {"WORKER_ONLY": "1"}
    parent_environment = dict(os.environ)

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", popen)
    monkeypatch.setattr(
        supervisor_module.runtime,
        "telemetry_worker_env",
        lambda python: supplied_environment,
    )

    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script=worker, interval=1.5
    )
    supervisor._start_reader = lambda unused_process: None
    supervisor.start()

    command, kwargs = popen.calls[0]
    assert command == ["/runtime/python", str(worker), "--interval", "1.5"]
    assert kwargs["env"] == supplied_environment
    assert kwargs["env"] is not supplied_environment
    assert "preexec_fn" not in kwargs
    kwargs["env"]["CHILD_MUTATION"] = "only-child"
    assert "CHILD_MUTATION" not in supplied_environment
    assert os.environ == parent_environment


def test_unexpected_exit_schedules_one_restart_only_after_start(monkeypatch, tmp_path):
    supervisor_module = _supervisor_module()
    worker = _worker_script(tmp_path)
    _FakeTimer.created = []
    first = _FakeProcess(returncode=None, pid=43211)
    replacement = _FakeProcess(returncode=None, pid=43212)
    popen = _PopenFactory([first, replacement])

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", popen)
    monkeypatch.setattr(supervisor_module.threading, "Timer", _FakeTimer)
    monkeypatch.setattr(
        supervisor_module.runtime, "telemetry_worker_env", lambda python: {}
    )

    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script=worker, restart_delay=3.0
    )
    supervisor._start_reader = lambda process: None
    supervisor._worker_exited(first, 1)
    assert _FakeTimer.created == []

    supervisor.start()
    supervisor._worker_exited(first, 1)
    supervisor._worker_exited(first, 1)

    assert len(_FakeTimer.created) == 1
    timer = _FakeTimer.created[0]
    assert timer.delay == 3.0
    assert timer.started is True
    assert len(popen.calls) == 1

    timer.fire()
    assert len(popen.calls) == 2
    assert supervisor._restart_timer is None

    next_timer = _FakeTimer(3.0, lambda: None)
    supervisor._restart_timer = next_timer
    supervisor.stop()
    assert next_timer.cancelled is True
    assert supervisor._restart_timer is None


def test_unexpected_restarts_are_capped_and_publish_unavailable(monkeypatch, tmp_path):
    supervisor_module = _supervisor_module()
    worker = _worker_script(tmp_path)
    _FakeTimer.created = []
    first = _FakeProcess(returncode=None, pid=43211)
    second = _FakeProcess(returncode=None, pid=43212)
    third = _FakeProcess(returncode=None, pid=43213)
    fourth = _FakeProcess(returncode=None, pid=43214)
    popen = _PopenFactory([first, second, third, fourth])

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", popen)
    monkeypatch.setattr(supervisor_module.threading, "Timer", _FakeTimer)
    monkeypatch.setattr(
        supervisor_module.runtime, "telemetry_worker_env", lambda python: {}
    )

    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python",
        worker_script=worker,
        restart_delay=3.0,
        max_restarts=3,
    )
    supervisor._start_reader = lambda process: None
    supervisor.start()

    for crash_number, process in enumerate((first, second, third)):
        supervisor._worker_exited(process, 1)
        timer = _FakeTimer.created[crash_number]
        assert timer.started is True
        timer.fire()

    supervisor._worker_exited(fourth, 1)

    assert len(popen.calls) == 4
    assert len(_FakeTimer.created) == 3
    assert supervisor._restart_timer is None
    assert supervisor._restart_attempts == 3
    snapshot = supervisor.snapshot()
    assert snapshot["available"] is False
    assert snapshot["source_mode"] == "unavailable"
    assert snapshot["npus"] == []
    assert any(
        "restart limit exhausted" in item for item in snapshot["diagnostics"]
    )


def test_valid_snapshot_and_new_start_cycle_reset_restart_budget(monkeypatch, tmp_path):
    supervisor_module = _supervisor_module()
    worker = _worker_script(tmp_path)
    _FakeTimer.created = []
    first = _FakeProcess(returncode=None, pid=43221)
    replacement = _FakeProcess(returncode=None, pid=43222)
    next_cycle = _FakeProcess(returncode=0, pid=43223)
    popen = _PopenFactory([first, replacement, next_cycle])

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", popen)
    monkeypatch.setattr(supervisor_module.threading, "Timer", _FakeTimer)
    monkeypatch.setattr(
        supervisor_module.runtime, "telemetry_worker_env", lambda python: {}
    )

    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python",
        worker_script=worker,
        restart_delay=3.0,
        max_restarts=1,
    )
    supervisor._start_reader = lambda process: None
    supervisor.start()
    supervisor._worker_exited(first, 1)
    _FakeTimer.created[0].fire()
    assert supervisor._restart_attempts == 1

    supervisor._handle_frame({
        "schema_version": 1,
        "kind": "snapshot",
        "available": True,
        "source": "device_status",
        "source_mode": "real",
        "timestamp": 1.0,
        "ts": 1.0,
        "stale": False,
        "sequence": 0,
        "count": 0,
        "npus": [],
    })
    assert supervisor._restart_attempts == 0

    supervisor._worker_exited(replacement, 1)
    assert len(_FakeTimer.created) == 2
    assert supervisor._restart_attempts == 1

    supervisor.stop()
    supervisor.start()
    assert supervisor._restart_attempts == 0


def test_stop_signals_only_tracked_process_group_and_reaps_reader(monkeypatch):
    supervisor_module = _supervisor_module()
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    process = _FakeProcess(returncode=None, pid=73210)
    reader = _FakeThread()
    signals = []
    environment_before = dict(os.environ)

    def killpg(group_id, sig):
        signals.append((group_id, sig))
        process.returncode = 0

    monkeypatch.setattr(supervisor_module.os, "killpg", killpg)
    supervisor._desired_running = True
    supervisor._process = process
    supervisor._reader = reader

    supervisor.stop()

    assert signals == [
        (process.pid, signal.SIGTERM),
        (process.pid, signal.SIGKILL),
    ]
    assert process.wait_calls == [1.0]
    assert process.stdout.closed is True
    assert reader.join_calls == [1.0]
    assert supervisor._process is None
    assert os.environ == environment_before


def test_stop_kills_surviving_descendant_after_leader_exits_cleanly(monkeypatch):
    supervisor_module = _supervisor_module()
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    process = _FakeProcess(returncode=None, pid=73216, wait_results=[0])
    process_group = _FakeTrackedProcessGroup(process)

    monkeypatch.setattr(supervisor_module.os, "killpg", process_group.killpg)
    supervisor._desired_running = True
    supervisor._process = process

    supervisor.stop()

    assert process.wait_calls == [1.0]
    assert process_group.signals == [
        (process.pid, signal.SIGTERM),
        (process.pid, signal.SIGKILL),
    ]
    assert process_group.descendant_alive is False


def test_terminate_process_group_kills_descendants_after_successful_term_wait(monkeypatch):
    supervisor_module = _supervisor_module()
    process = _FakeProcess(returncode=None, pid=73211, wait_results=[0])
    signals = []

    monkeypatch.setattr(
        supervisor_module.os,
        "killpg",
        lambda group_id, sig: signals.append((group_id, sig)),
    )

    supervisor_module.TelemetrySupervisor._terminate_process_group(process)

    assert signals == [
        (process.pid, signal.SIGTERM),
        (process.pid, signal.SIGKILL),
    ]
    assert process.wait_calls == [1.0]


def test_terminate_process_group_kills_only_after_term_wait_timeout(monkeypatch):
    supervisor_module = _supervisor_module()
    process = _FakeProcess(
        returncode=None,
        pid=73212,
        wait_results=[
            subprocess.TimeoutExpired("telemetry-worker", 1.0),
            0,
        ],
    )
    signals = []

    monkeypatch.setattr(
        supervisor_module.os,
        "killpg",
        lambda group_id, sig: signals.append((group_id, sig)),
    )

    supervisor_module.TelemetrySupervisor._terminate_process_group(process)

    assert signals == [
        (process.pid, signal.SIGTERM),
        (process.pid, signal.SIGKILL),
    ]
    assert process.wait_calls == [1.0, 1.0]


def test_terminate_process_group_tolerates_group_vanishing_after_leader_reap(monkeypatch):
    supervisor_module = _supervisor_module()
    process = _FakeProcess(returncode=None, pid=73213, wait_results=[0])
    signals = []

    def killpg(group_id, sig):
        signals.append((group_id, sig))
        if sig == signal.SIGKILL:
            raise ProcessLookupError()

    monkeypatch.setattr(supervisor_module.os, "killpg", killpg)

    supervisor_module.TelemetrySupervisor._terminate_process_group(process)

    assert signals == [
        (process.pid, signal.SIGTERM),
        (process.pid, signal.SIGKILL),
    ]
    assert process.wait_calls == [1.0]


def test_worker_exit_cleans_tracked_group_after_leader_already_exited(monkeypatch):
    supervisor_module = _supervisor_module()
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    process = _FakeProcess(returncode=7, pid=73214)
    signals = []

    monkeypatch.setattr(
        supervisor_module.os,
        "killpg",
        lambda group_id, sig: signals.append((group_id, sig)),
    )
    supervisor._desired_running = True
    supervisor._process = process
    supervisor._schedule_restart = lambda: None

    supervisor._worker_exited(process, 7)

    assert signals == [
        (process.pid, signal.SIGTERM),
        (process.pid, signal.SIGKILL),
    ]
    assert process.wait_calls == [1.0]
    assert supervisor._process is None


def test_worker_stdout_eof_tolerates_vanished_tracked_group(monkeypatch):
    supervisor_module = _supervisor_module()
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    process = _FakeProcess(returncode=0, pid=73215)
    signals = []

    def killpg(group_id, sig):
        signals.append((group_id, sig))
        raise OSError(errno.ESRCH, "No such process group")

    monkeypatch.setattr(supervisor_module.os, "killpg", killpg)
    supervisor._desired_running = True
    supervisor._process = process
    supervisor._schedule_restart = lambda: None

    supervisor._worker_stdout_eof(process)

    assert signals == [(process.pid, signal.SIGTERM)]
    assert process.wait_calls == [1.0]
    assert supervisor._process is None


def test_supervisor_avoids_native_imports_worker_imports_and_global_killers():
    source = _SUPERVISOR_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_SUPERVISOR_PATH), feature_version=(3, 8))
    imports = []
    dynamic_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Call):
            function = node.func
            is_dunder_import = isinstance(function, ast.Name) and function.id == "__import__"
            is_import_module = (
                isinstance(function, ast.Attribute) and function.attr == "import_module"
            )
            if (is_dunder_import or is_import_module) and node.args:
                argument = node.args[0]
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    dynamic_imports.append(argument.value)

    assert not any(name.startswith("dx_engine") for name in imports)
    assert not any(name.startswith("dx_engine") for name in dynamic_imports)
    assert "telemetry_worker" not in imports
    assert "telemetry_worker" not in dynamic_imports
    assert "pkill" not in source
    assert "killall" not in source


def test_default_worker_script_is_the_sibling_worker_module():
    supervisor_module = _supervisor_module()

    supervisor = supervisor_module.TelemetrySupervisor(runtime_python="/runtime/python")

    assert Path(supervisor._worker_script) == _SUPERVISOR_PATH.with_name(
        "telemetry_worker.py"
    )


def test_concurrent_start_reserves_one_launch_slot(monkeypatch, tmp_path):
    supervisor_module = _supervisor_module()
    worker = _worker_script(tmp_path)
    process = _FakeProcess(returncode=None, pid=73220)
    popen = _BlockingPopenFactory(process)

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", popen)
    monkeypatch.setattr(
        supervisor_module.runtime, "telemetry_worker_env", lambda python: {}
    )

    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script=worker
    )
    supervisor._start_reader = lambda unused_process: None

    first_start = threading.Thread(target=supervisor.start)
    first_start.start()
    assert popen.entered.wait(timeout=1.0)

    second_start = threading.Thread(target=supervisor.start)
    second_start.start()
    second_start.join(timeout=1.0)

    assert second_start.is_alive() is False
    assert len(popen.calls) == 1

    popen.release.set()
    first_start.join(timeout=1.0)
    assert first_start.is_alive() is False
    assert supervisor._process is process


def test_failed_spawn_releases_launch_reservation(monkeypatch, tmp_path):
    supervisor_module = _supervisor_module()
    worker = _worker_script(tmp_path)
    process = _FakeProcess(returncode=None, pid=73221)
    calls = []

    def popen(command, **kwargs):
        calls.append((command, kwargs))
        if len(calls) == 1:
            raise OSError("spawn failed")
        return process

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", popen)
    monkeypatch.setattr(
        supervisor_module.runtime, "telemetry_worker_env", lambda python: {}
    )
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script=worker
    )
    supervisor._start_reader = lambda unused_process: None

    supervisor.start()
    supervisor.start()

    assert len(calls) == 2
    assert supervisor._process is process


def test_parse_frame_rejects_oversized_nonfinite_and_pathological_records():
    supervisor_module = _supervisor_module()
    parse_frame = supervisor_module.TelemetrySupervisor.parse_frame

    nested = []
    for unused_index in range(supervisor_module.MAX_NESTING + 2):
        nested = [nested]

    invalid_lines = [
        supervisor_module.FRAME_PREFIX
        + "x" * (supervisor_module.MAX_FRAME_BYTES + 1),
        _frame(
            "hello",
            available=True,
            source="device_status",
            source_mode="real",
            npus=[],
            system_info={"detail": "x" * (supervisor_module.MAX_STRING_BYTES + 1)},
        ),
        _frame(
            "hello",
            available=True,
            source="device_status",
            source_mode="real",
            npus=[{}] * (supervisor_module.MAX_CONTAINER_ITEMS + 1),
            system_info={},
        ),
        _frame(
            "hello",
            available=True,
            source="device_status",
            source_mode="real",
            npus=[],
            system_info={"nested": nested},
        ),
        _frame(
            "snapshot",
            available=True,
            source="device_status",
            source_mode="real",
            timestamp=float("nan"),
            ts=1.0,
            stale=False,
            sequence=0,
            count=0,
            npus=[],
        ),
        _frame(
            "event",
            available=True,
            source="runtime_event_dispatcher",
            source_mode="real",
            npus=[],
            event={"ts": float("inf"), "level": "warning", "message": "hot"},
        ),
    ]

    for line in invalid_lines:
        assert parse_frame(line) is None


def test_reader_continues_after_malformed_frame_and_bounds_diagnostic():
    supervisor_module = _supervisor_module()
    malformed = supervisor_module.FRAME_PREFIX + "x" * (
        supervisor_module.MAX_FRAME_BYTES + 1
    ) + "\n"
    valid_snapshot = _frame(
        "snapshot",
        available=True,
        source="device_status",
        source_mode="real",
        timestamp=9.0,
        ts=9.0,
        stale=False,
        sequence=0,
        count=0,
        npus=[],
    )
    process = _FakeProcess(lines=[malformed, valid_snapshot], returncode=0)
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    supervisor._process = process
    supervisor._restart_attempts = 1

    supervisor._read_output(process)

    assert supervisor._restart_attempts == 0
    assert supervisor.snapshot()["available"] is False
    diagnostics = supervisor.snapshot()["diagnostics"]
    assert any("overlong stdout line" in item for item in diagnostics)
    assert all(
        len(item.encode("utf-8")) <= supervisor_module.MAX_DIAGNOSTIC_BYTES
        for item in diagnostics
    )


def test_reader_discards_overlong_stdout_line_with_bounded_reads():
    supervisor_module = _supervisor_module()
    valid_snapshot = _frame(
        "snapshot",
        available=True,
        source="device_status",
        source_mode="real",
        timestamp=10.0,
        ts=10.0,
        stale=False,
        sequence=0,
        count=0,
        npus=[],
    )
    process = _FakeProcess(returncode=0)
    process.stdout = _BoundedReadStream(
        "x" * (supervisor_module.MAX_FRAME_BYTES * 2) + "\n" + valid_snapshot,
        supervisor_module.MAX_FRAME_BYTES + 1,
    )
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    supervisor._process = process
    supervisor._restart_attempts = 1

    supervisor._read_output(process)

    assert process.stdout.read_sizes
    assert max(process.stdout.read_sizes) <= supervisor_module.MAX_FRAME_BYTES + 1
    assert supervisor._restart_attempts == 0
    assert supervisor.snapshot()["available"] is False
    assert any(
        "overlong stdout line" in diagnostic
        for diagnostic in supervisor.snapshot()["diagnostics"]
    )


def test_bounded_reader_yields_complete_frame_before_pipe_close():
    """A live worker frame must not wait for a 64 KiB buffer fill or EOF."""
    supervisor_module = _supervisor_module()
    reader_fd, writer_fd = os.pipe()
    reader = os.fdopen(reader_fd, "rb")
    writer = os.fdopen(writer_fd, "wb", buffering=0)
    received = []
    frame_ready = threading.Event()

    def consume_once():
        received.append(
            next(supervisor_module.TelemetrySupervisor._iter_bounded_stdout_lines(reader))
        )
        frame_ready.set()

    thread = threading.Thread(target=consume_once, daemon=True)
    thread.start()
    frame = _frame(
        "snapshot",
        available=True,
        source="device_status",
        source_mode="real",
        timestamp=12.0,
        ts=12.0,
        stale=False,
        sequence=0,
        count=0,
        npus=[],
    )
    try:
        writer.write(frame.encode("utf-8"))
        assert frame_ready.wait(timeout=1.0), (
            "newline-delimited frame was held until the worker pipe closed or filled"
        )
        assert received == [(frame.rstrip("\n"), False)]
    finally:
        writer.close()
        thread.join(timeout=1.0)
        reader.close()


def test_bounded_reader_rejects_multibyte_frame_by_utf8_byte_length():
    """The worker pipe limit applies to bytes, not decoded character count."""
    supervisor_module = _supervisor_module()
    payload = "é" * (supervisor_module.MAX_FRAME_BYTES // 2 + 1)
    valid_snapshot = _frame(
        "snapshot",
        available=True,
        source="device_status",
        source_mode="real",
        timestamp=13.0,
        ts=13.0,
        stale=False,
        sequence=0,
        count=0,
        npus=[],
    )
    stream = io.BytesIO(
        payload.encode("utf-8") + b"\n" + valid_snapshot.encode("utf-8")
    )

    frames = list(
        supervisor_module.TelemetrySupervisor._iter_bounded_stdout_lines(stream)
    )

    assert frames[0] == ("", True)
    assert frames[1] == (valid_snapshot.rstrip("\n"), False)


def test_current_worker_exit_invalidates_snapshot_before_restart_scheduling():
    supervisor_module = _supervisor_module()
    process = _FakeProcess(returncode=1, pid=73224)
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    supervisor._process = process
    supervisor._desired_running = True
    supervisor._snapshot = {
        "available": True,
        "source_mode": "stale",
        "npus": [{"id": 0}],
    }
    scheduled = []
    supervisor._schedule_restart = lambda: scheduled.append(True)

    supervisor._worker_exited(process, 1)

    snapshot = supervisor.snapshot()
    assert snapshot["available"] is False
    assert snapshot["source_mode"] == "unavailable"
    assert snapshot["npus"] == []
    assert any("exited with code 1" in item for item in snapshot["diagnostics"])
    assert supervisor._process is None
    assert scheduled == [True]


def test_current_worker_eof_terminates_live_process_and_invalidates_snapshot():
    supervisor_module = _supervisor_module()
    process = _FakeProcess(
        lines=[
            _frame(
                "snapshot",
                available=True,
                source="device_status",
                source_mode="real",
                timestamp=11.0,
                ts=11.0,
                stale=False,
                sequence=0,
                count=0,
                npus=[{"id": 0}],
            ),
        ],
        returncode=None,
        pid=73225,
        wait_results=[subprocess.TimeoutExpired("telemetry-worker", 0.1)],
    )
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    supervisor._process = process
    supervisor._desired_running = True
    terminated = []
    scheduled = []
    supervisor._terminate_process_group = (
        lambda target, cleanup_exited_group=False: terminated.append(target)
    )
    supervisor._schedule_restart = lambda: scheduled.append(True)

    supervisor._read_output(process)

    snapshot = supervisor.snapshot()
    assert snapshot["available"] is False
    assert snapshot["source_mode"] == "unavailable"
    assert snapshot["npus"] == []
    assert any("stdout reached EOF" in item for item in snapshot["diagnostics"])
    assert terminated == [process]
    assert supervisor._process is None
    assert scheduled == [True]


def test_handler_catches_recursive_direct_frame_without_raising():
    supervisor_module = _supervisor_module()
    recursive_npus = []
    recursive_npus.append(recursive_npus)
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )

    supervisor._handle_frame({"kind": "snapshot", "npus": recursive_npus})

    assert any(
        "Telemetry frame handling failed" in diagnostic
        for diagnostic in supervisor.snapshot()["diagnostics"]
    )


def test_old_reader_frames_exit_and_eof_cannot_affect_replacement_worker():
    supervisor_module = _supervisor_module()
    old_process = _FakeProcess(
        returncode=None,
        pid=73222,
        wait_results=[subprocess.TimeoutExpired("telemetry-worker", 0.1)],
    )
    replacement = _FakeProcess(returncode=None, pid=73223)
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    terminated = []
    supervisor._terminate_process_group = lambda process: terminated.append(process)
    initial_frame = {
        "kind": "snapshot",
        "available": True,
        "source": "device_status",
        "source_mode": "real",
        "timestamp": 1.0,
        "ts": 1.0,
        "stale": False,
        "sequence": 0,
        "count": 0,
        "npus": [],
    }
    late_frame = dict(initial_frame)
    late_frame["timestamp"] = 2.0
    late_frame["ts"] = 2.0

    supervisor._process = old_process
    supervisor._desired_running = True
    supervisor._handle_frame(initial_frame, old_process)
    supervisor._process = replacement
    supervisor._handle_frame(late_frame, old_process)
    supervisor._read_output(old_process)
    supervisor._worker_exited(old_process, 1)

    assert supervisor.snapshot()["timestamp"] == 1.0
    assert supervisor._process is replacement
    assert supervisor._restart_timer is None
    assert terminated == []


def test_events_canonicalize_time_aliases_and_reject_nonpositive_limits():
    supervisor_module = _supervisor_module()
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )

    for event in (
        {"time": 11.0, "level": "info", "message": "time"},
        {"timestamp": 12.0, "level": "info", "message": "timestamp"},
        {"ts": 13.0, "level": "info", "message": "ts"},
    ):
        supervisor._handle_frame({"kind": "event", "event": event})

    events = supervisor.events(since=10.0)
    assert [event["time"] for event in events] == [11.0, 12.0, 13.0]
    assert events[1]["timestamp"] == 12.0
    assert events[2]["ts"] == 13.0
    assert supervisor.events(since=11.0) == events[1:]
    assert supervisor.events(since=0.0, limit=0) == []
    assert supervisor.events(since=0.0, limit=-1) == []


def test_events_reject_unsafe_query_values_before_numeric_conversion():
    supervisor_module = _supervisor_module()
    supervisor = supervisor_module.TelemetrySupervisor(
        runtime_python="/runtime/python", worker_script="/worker.py"
    )
    for timestamp in (1.0, 2.0, 3.0):
        supervisor._handle_frame({
            "kind": "event",
            "event": {
                "timestamp": timestamp,
                "level": "info",
                "message": "event-{0}".format(timestamp),
            },
        })

    assert [event["time"] for event in supervisor.events(since="1", limit="2")] == [
        2.0,
        3.0,
    ]
    overlong_value = "9" * (supervisor_module.MAX_QUERY_VALUE_CHARS + 1)
    for since, limit in (
        (overlong_value, 100),
        (0, overlong_value),
        (None, 100),
        (0, None),
        (True, 100),
        (0, True),
        (float("nan"), 100),
        (float("inf"), 100),
    ):
        assert supervisor.events(since=since, limit=limit) == []


def test_supervisor_import_isolated_from_dx_engine_in_clean_subprocess():
    studio_root = _SUPERVISOR_PATH.parents[2]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(studio_root)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json, sys; import dx_monitor.core.telemetry_supervisor; "
            "print(json.dumps(sorted(sys.modules)))",
        ],
        cwd=str(studio_root),
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    modules = json.loads(result.stdout)
    assert not any(name == "dx_engine" or name.startswith("dx_engine.") for name in modules)
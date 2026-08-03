"""Studio-side supervisor for the isolated DX Monitor telemetry worker.

This module deliberately imports neither the native runtime nor the worker
module.  The worker receives the runtime-specific interpreter and environment;
the Studio process only consumes validated framed JSON from its stdout.
"""
import copy
import errno
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import threading

from shared import runtime


FRAME_PREFIX = "__DXTELEMETRY__"
SCHEMA_VERSION = 1
SOURCE_MODES = ("real", "stale", "unavailable", "mock")
FRAME_KINDS = ("hello", "snapshot", "event", "error", "stopped")
MAX_DIAGNOSTICS = 100
MAX_EVENTS = 200
MAX_FRAME_BYTES = 64 * 1024
MAX_STRING_BYTES = 8 * 1024
MAX_CONTAINER_ITEMS = 256
MAX_NESTING = 32
MAX_DIAGNOSTIC_BYTES = 1024
MAX_QUERY_VALUE_CHARS = 32


def _is_number(value):
    """Return whether a JSON value is numeric without accepting booleans."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def _is_event_level(value):
    """Accept worker event levels as the runtime emits them."""
    return value is None or (
        isinstance(value, (int, str)) and not isinstance(value, bool)
    )


def _event_time(event):
    """Return the first valid worker event timestamp using protocol aliases."""
    for key in ("time", "timestamp", "ts"):
        if key in event:
            value = event[key]
            if _is_number(value):
                return value
    return None


def _is_bounded_json_value(value):
    """Validate decoded JSON without recursive traversal or unbounded values."""
    pending = [(value, 0)]
    seen_containers = set()

    while pending:
        current, depth = pending.pop()
        if isinstance(current, str):
            if len(current.encode("utf-8", "replace")) > MAX_STRING_BYTES:
                return False
        elif current is None or isinstance(current, bool):
            continue
        elif _is_number(current):
            continue
        elif isinstance(current, dict):
            if depth >= MAX_NESTING or len(current) > MAX_CONTAINER_ITEMS:
                return False
            container_id = id(current)
            if container_id in seen_containers:
                return False
            seen_containers.add(container_id)
            for key, item in current.items():
                if not isinstance(key, str):
                    return False
                if len(key.encode("utf-8", "replace")) > MAX_STRING_BYTES:
                    return False
                pending.append((item, depth + 1))
        elif isinstance(current, list):
            if depth >= MAX_NESTING or len(current) > MAX_CONTAINER_ITEMS:
                return False
            container_id = id(current)
            if container_id in seen_containers:
                return False
            seen_containers.add(container_id)
            pending.extend((item, depth + 1) for item in current)
        else:
            return False

    return True


def _bounded_diagnostic(value):
    """Return a short, printable diagnostic without retaining hostile input."""
    try:
        message = value if isinstance(value, str) else str(value)
    except (RecursionError, TypeError, ValueError):
        message = "Telemetry diagnostic unavailable"
    message = message.strip()
    encoded = message.encode("utf-8", "replace")
    if len(encoded) > MAX_DIAGNOSTIC_BYTES:
        message = encoded[:MAX_DIAGNOSTIC_BYTES].decode("utf-8", "ignore")
    return message


def _coerce_event_since(value):
    """Return a finite event timestamp filter without parsing hostile input."""
    if type(value) is str:
        if len(value) > MAX_QUERY_VALUE_CHARS:
            return None
    elif type(value) not in (int, float):
        return None
    try:
        value = float(value)
    except (OverflowError, TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _coerce_event_limit(value):
    """Return a finite, bounded event limit without parsing hostile input."""
    if type(value) is str:
        if len(value) > MAX_QUERY_VALUE_CHARS:
            return None
    elif type(value) not in (int, float):
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    try:
        return max(0, min(int(value), MAX_EVENTS))
    except (OverflowError, TypeError, ValueError):
        return None


class TelemetrySupervisor(object):
    """Own one telemetry child process and expose its bounded cached state."""

    def __init__(
        self,
        runtime_python=None,
        worker_script=None,
        interval=1.0,
        restart_delay=2.0,
        max_restarts=3,
    ):
        self._runtime_python = runtime_python
        self._worker_script = str(
            worker_script or Path(__file__).resolve().with_name("telemetry_worker.py")
        )
        self._interval = interval
        self._restart_delay = restart_delay
        if type(max_restarts) is not int or max_restarts < 0:
            raise ValueError("max_restarts must be a non-negative integer")
        self._max_restarts = max_restarts
        self._restart_attempts = 0
        self._lock = threading.RLock()
        self._process = None
        self._launching = False
        self._reader = None
        self._restart_timer = None
        self._desired_running = False
        self._diagnostics = []
        self._events = []
        self._system_info = {}
        self._snapshot = self._new_unavailable_snapshot()

    @staticmethod
    def parse_frame(line):
        """Return a validated worker record, or ``None`` for invalid stdout."""
        if not isinstance(line, str) or not line.startswith(FRAME_PREFIX):
            return None
        if len(line.encode("utf-8", "replace")) > MAX_FRAME_BYTES:
            return None

        try:
            record = json.loads(line[len(FRAME_PREFIX):])
        except (RecursionError, TypeError, ValueError):
            return None

        if not isinstance(record, dict) or not _is_bounded_json_value(record):
            return None
        if type(record.get("schema_version")) is not int:
            return None
        if record.get("schema_version") != SCHEMA_VERSION:
            return None
        if record.get("kind") not in FRAME_KINDS:
            return None
        if type(record.get("available")) is not bool:
            return None
        if not isinstance(record.get("source"), str):
            return None
        if record.get("source_mode") not in SOURCE_MODES:
            return None
        if not isinstance(record.get("npus"), list):
            return None

        kind = record["kind"]
        if kind == "hello":
            system_info = record.get("system_info")
            if not isinstance(system_info, dict):
                return None
        elif kind == "snapshot":
            if not _is_number(record.get("timestamp")):
                return None
            if not _is_number(record.get("ts")):
                return None
            if type(record.get("stale")) is not bool:
                return None
            if type(record.get("sequence")) is not int:
                return None
            if type(record.get("count")) is not int or record["count"] < 0:
                return None
        elif kind == "event":
            event = record.get("event")
            if not isinstance(event, dict):
                return None
            if _event_time(event) is None:
                return None
            if not isinstance(event.get("message"), str):
                return None
            if not _is_event_level(event.get("level")):
                return None
        elif kind == "error":
            if record.get("available") or record.get("source_mode") not in (
                "unavailable",
                "stale",
            ):
                return None
            message = record.get("message")
            error = record.get("error")
            if message is None and error is None:
                return None
            if message is not None and not isinstance(message, str):
                return None
            if error is not None and not isinstance(error, str):
                return None
        elif kind == "stopped":
            message = record.get("message")
            if message is not None and not isinstance(message, str):
                return None

        return record

    def start(self):
        """Request worker operation and start it if no worker is currently live."""
        with self._lock:
            starting_new_cycle = not self._desired_running
            self._desired_running = True
            if starting_new_cycle:
                self._restart_attempts = 0
            process = self._process
            if self._launching or (process is not None and self._poll(process) is None):
                return

        self._start_worker()

    def stop(self):
        """Stop and reap only this supervisor's tracked process group."""
        with self._lock:
            self._desired_running = False
            restart_timer = self._restart_timer
            self._restart_timer = None
            process = self._process
            reader = self._reader
            self._process = None
            self._reader = None

        if restart_timer is not None:
            try:
                restart_timer.cancel()
            except Exception:
                pass

        if process is not None:
            self._terminate_process_group(process)
            stdout = getattr(process, "stdout", None)
            if stdout is not None:
                try:
                    stdout.close()
                except (OSError, ValueError):
                    pass

        if reader is not None:
            try:
                reader.join(timeout=1.0)
            except RuntimeError:
                pass

    def snapshot(self):
        """Return a defensive copy of the latest valid worker snapshot."""
        with self._lock:
            snapshot = copy.deepcopy(self._snapshot)
            snapshot["diagnostics"] = list(self._diagnostics)
            return snapshot

    def system_info(self):
        """Return cached worker version data with safe unavailable defaults."""
        with self._lock:
            info = copy.deepcopy(self._system_info)
            snapshot = self._snapshot
            diagnostics = list(self._diagnostics)

        info.setdefault("sdk_version", "N/A")
        info.setdefault("driver_version", "N/A")
        info.setdefault("pcie_driver_version", "N/A")
        info.setdefault("npu_count", len(snapshot.get("npus", [])))
        info.setdefault("available", snapshot.get("available", False))
        info.setdefault("source_mode", snapshot.get("source_mode", "unavailable"))
        info.setdefault("diagnostics", diagnostics)
        return info

    def events(self, since=0.0, limit=100):
        """Return bounded defensive copies of events strictly newer than ``since``."""
        since_value = _coerce_event_since(since)
        limit_value = _coerce_event_limit(limit)
        if since_value is None or limit_value is None or limit_value <= 0:
            return []

        with self._lock:
            events = copy.deepcopy(self._events)

        selected = []
        for event in events:
            timestamp = _event_time(event)
            if timestamp is None:
                timestamp = 0.0
            if timestamp > since_value:
                selected.append(event)
            if len(selected) >= limit_value:
                break
        return selected

    def _start_worker(self):
        with self._lock:
            if not self._desired_running or self._launching:
                return
            process = self._process
            if process is not None and self._poll(process) is None:
                return
            self._launching = True
            selected_python = self._runtime_python

        if selected_python is None:
            try:
                selected_python = runtime.telemetry_python()
            except Exception as error:
                self._launch_failed(
                    "Unable to select telemetry runtime: {0}".format(error)
                )
                return
            if not selected_python:
                self._launch_failed("No telemetry-compatible runtime Python")
                return

        if not os.path.isfile(self._worker_script):
            self._launch_failed(
                "Telemetry worker script is missing: {0}".format(self._worker_script)
            )
            return

        try:
            child_environment = dict(runtime.telemetry_worker_env(selected_python))
            process = subprocess.Popen(
                [selected_python, self._worker_script, "--interval", str(self._interval)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=child_environment,
                start_new_session=True,
            )
        except Exception as error:
            self._launch_failed("Unable to start telemetry worker: {0}".format(error))
            return

        with self._lock:
            self._launching = False
            if not self._desired_running:
                should_stop = True
            else:
                self._process = process
                self._runtime_python = selected_python
                should_stop = False

        if should_stop:
            self._terminate_process_group(process)
            return
        self._start_reader(process)

    def _launch_failed(self, diagnostic):
        """Publish a launch failure before releasing the reserved spawn slot."""
        self._set_unavailable(diagnostic)
        with self._lock:
            self._launching = False

    def _start_reader(self, process):
        reader = threading.Thread(
            target=self._read_output,
            args=(process,),
            name="dx-monitor-telemetry-reader",
            daemon=True,
        )
        with self._lock:
            if self._process is not process:
                return
            self._reader = reader
        reader.start()

    def _read_output(self, process):
        stdout = getattr(process, "stdout", None)
        if stdout is None:
            if self._is_current_process(process):
                self._record_diagnostic("Telemetry worker has no stdout stream")
        else:
            try:
                for line, overlong in self._iter_bounded_stdout_lines(stdout):
                    if overlong:
                        if self._is_current_process(process):
                            self._record_diagnostic(
                                "Telemetry worker emitted overlong stdout line"
                            )
                        continue
                    record = self.parse_frame(line)
                    if record is None:
                        if self._is_current_process(process):
                            self._record_diagnostic(line)
                    else:
                        self._handle_frame(record, process)
            except (OSError, RecursionError, TypeError, ValueError) as error:
                if self._is_current_process(process):
                    self._record_diagnostic(
                        "Telemetry reader failed: {0}".format(error)
                    )

        exit_code = self._poll(process)
        if exit_code is None:
            try:
                exit_code = process.wait(timeout=0.1)
            except (subprocess.TimeoutExpired, OSError):
                exit_code = None
        if exit_code is not None:
            self._worker_exited(process, exit_code)
        else:
            self._worker_stdout_eof(process)

    @staticmethod
    def _iter_bounded_stdout_lines(stream):
        """Yield bounded newline-delimited worker frames without delayed reads."""
        while True:
            line = stream.readline(MAX_FRAME_BYTES + 1)
            if not line:
                return
            is_binary = isinstance(line, bytes)
            newline = b"\n" if is_binary else "\n"
            if line.endswith(newline):
                payload = line[:-1]
                if is_binary:
                    payload = payload.decode("utf-8", "replace")
                if len(payload.encode("utf-8", "replace")) > MAX_FRAME_BYTES:
                    yield "", True
                    continue
                yield payload, False
                continue

            # A bounded readline without its newline means this logical frame is
            # overlong. Drain only bounded chunks until the next frame boundary;
            # retaining or parsing this hostile record would defeat the limit.
            while line and not line.endswith(newline):
                line = stream.readline(MAX_FRAME_BYTES + 1)
            yield "", True

    def _worker_stdout_eof(self, process):
        """Recover a current worker whose stdout closed before it exited."""
        if not self._is_current_process(process):
            return
        self._terminate_process_group(process)
        desired_running = self._retire_current_worker(
            process,
            "Telemetry worker stdout reached EOF before worker exit",
        )
        if desired_running:
            self._schedule_restart()

    def _worker_exited(self, process, exit_code):
        if not self._is_current_process(process):
            return
        self._terminate_process_group(process)
        desired_running = self._retire_current_worker(
            process,
            "Telemetry worker exited with code {0}".format(exit_code),
        )
        if desired_running:
            self._schedule_restart()

    def _retire_current_worker(self, process, diagnostic):
        """Atomically invalidate telemetry cached from a current worker only."""
        with self._lock:
            if self._process is not process:
                return None
            snapshot = self._new_unavailable_snapshot()
            snapshot["error"] = _bounded_diagnostic(diagnostic)
            self._append_diagnostic_locked(diagnostic)
            self._snapshot = snapshot
            self._process = None
            desired_running = self._desired_running
        return desired_running

    def _schedule_restart(self):
        """Schedule at most one delayed restart for an unexpectedly exited worker."""
        holder = {}

        def restart():
            with self._lock:
                if self._restart_timer is not holder.get("timer"):
                    return
                self._restart_timer = None
                desired_running = self._desired_running
            if desired_running:
                self._start_worker()

        with self._lock:
            if not self._desired_running or self._process is not None:
                return
            if self._restart_timer is not None:
                return
            if self._restart_attempts >= self._max_restarts:
                exhausted = True
            else:
                self._restart_attempts += 1
                exhausted = False
            if exhausted:
                timer = None
            else:
                timer = threading.Timer(self._restart_delay, restart)
                holder["timer"] = timer
                if hasattr(timer, "daemon"):
                    timer.daemon = True
                self._restart_timer = timer

        if exhausted:
            self._set_unavailable(
                "Telemetry worker restart limit exhausted ({0})".format(
                    self._max_restarts
                )
            )
            return

        timer.start()

    def _handle_frame_for_process(self, frame, process):
        """Apply a frame only if it came from the current worker process."""
        if not self._is_current_process(process):
            return

        try:
            if not isinstance(frame, dict) or not _is_bounded_json_value(frame):
                raise ValueError("invalid frame payload")
            kind = frame.get("kind")
            if kind == "snapshot":
                snapshot = copy.deepcopy(frame)
                with self._lock:
                    if process is not None and self._process is not process:
                        return
                    self._snapshot = snapshot
                    self._restart_attempts = 0
                return

            if kind == "hello":
                system_info = frame.get("system_info")
                if isinstance(system_info, dict):
                    system_info = copy.deepcopy(system_info)
                    with self._lock:
                        if process is not None and self._process is not process:
                            return
                        self._system_info.update(system_info)
                return

            if kind == "event":
                event = frame.get("event")
                event_time = _event_time(event) if isinstance(event, dict) else None
                if event_time is not None:
                    event = copy.deepcopy(event)
                    event["time"] = event_time
                    with self._lock:
                        if process is not None and self._process is not process:
                            return
                        self._events.append(event)
                        del self._events[:-MAX_EVENTS]
                return

            if kind == "error":
                message = frame.get(
                    "error", frame.get("message", "Telemetry worker error")
                )
                self._set_unavailable(
                    "Telemetry worker error (source_mode={0}): {1}".format(
                        frame.get("source_mode"), message
                    ),
                    frame,
                    process,
                )
                return

            if kind == "stopped" and self._is_current_process(process):
                self._record_diagnostic("Telemetry worker stopped")
        except (RecursionError, TypeError, ValueError) as error:
            if self._is_current_process(process):
                self._record_diagnostic("Telemetry frame handling failed: {0}".format(error))

    def _handle_frame(self, frame, process=None):
        """Update cache state from a frame, optionally tied to a worker process."""
        return self._handle_frame_for_process(frame, process)

    def _set_unavailable(self, diagnostic, frame=None, process=None):
        snapshot = self._new_unavailable_snapshot()
        try:
            if isinstance(frame, dict):
                for key in ("timestamp", "ts", "source", "sequence"):
                    if key in frame:
                        snapshot[key] = copy.deepcopy(frame[key])
                snapshot["error"] = str(diagnostic)
        except (RecursionError, TypeError, ValueError):
            snapshot["error"] = "Telemetry worker error"
        with self._lock:
            if process is not None and self._process is not process:
                return
            self._append_diagnostic_locked(diagnostic)
            self._snapshot = snapshot

    def _record_diagnostic(self, line):
        with self._lock:
            self._append_diagnostic_locked(line)

    def _append_diagnostic_locked(self, line):
        if line is None:
            return
        message = _bounded_diagnostic(line)
        if not message:
            return
        self._diagnostics.append(message)
        del self._diagnostics[:-MAX_DIAGNOSTICS]

    def _is_current_process(self, process):
        with self._lock:
            return process is None or self._process is process

    @staticmethod
    def _new_unavailable_snapshot():
        return {
            "available": False,
            "source_mode": "unavailable",
            "npus": [],
        }

    @staticmethod
    def _poll(process):
        try:
            return process.poll()
        except (AttributeError, OSError):
            return None

    @staticmethod
    def _signal_process_group(process_id, sig):
        """Signal one known process group; a vanished group is already clean."""
        try:
            os.killpg(process_id, sig)
        except ProcessLookupError:
            return False
        except OSError as error:
            if error.errno == errno.ESRCH:
                return False
            raise
        return True

    @staticmethod
    def _terminate_process_group(process):
        """Reap a leader and clear descendants in its tracked process group."""
        process_id = getattr(process, "pid", None)
        if not isinstance(process_id, int) or process_id <= 0:
            return
        group_known = TelemetrySupervisor._signal_process_group(
            process_id, signal.SIGTERM
        )

        try:
            process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            timed_out = True
        except OSError:
            timed_out = False
        else:
            timed_out = False

        if group_known:
            TelemetrySupervisor._signal_process_group(process_id, signal.SIGKILL)
        if timed_out:
            try:
                process.wait(timeout=1.0)
            except (subprocess.TimeoutExpired, OSError):
                pass
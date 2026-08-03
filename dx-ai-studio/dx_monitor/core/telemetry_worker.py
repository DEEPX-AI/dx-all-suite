"""Isolated stdout-only DX Monitor telemetry worker.

This module is run with the runtime-compatible Python interpreter selected by
``shared.runtime.telemetry_python()``.  It deliberately imports no DX runtime
modules until :func:`main` begins setup, so it remains importable and testable
from the Studio interpreter.
"""
import argparse
import json
import math
import sys
import threading
import time


FRAME_PREFIX = "__DXTELEMETRY__"
SCHEMA_VERSION = 1
INVALID_TEMPERATURE = -32768

_MAX_SENSOR_CHANNELS = 4
_MEBIBYTE = 1024 * 1024
_EMIT_LOCK = threading.Lock()
_SYSTEM_INFO_CACHE = None


def _finite_float(value):
    """Parse a finite command-line float for the worker polling interval."""
    try:
        result = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a number")
    if not math.isfinite(result):
        raise argparse.ArgumentTypeError("must be a finite number")
    return result


def _load_runtime_api():
    """Load native runtime APIs only in the worker process setup path."""
    from dx_engine.configuration import Configuration
    from dx_engine.device_status import DeviceStatus
    from dx_engine.runtime_event_dispatcher import RuntimeEventDispatcher
    return DeviceStatus, Configuration, RuntimeEventDispatcher


def _number(value):
    """Return a finite JSON-safe number, or ``None`` when the value is invalid."""
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _average(values):
    return sum(values) / len(values) if values else 0.0


def _power_estimate(voltages):
    """Return the legacy voltage-only power estimate, or no-data when absent."""
    if not voltages:
        return None
    return round(_average(voltages) * 0.5, 1)


def _device_snapshot(status, index):
    """Normalize a single DeviceStatus result into the Monitor NPU schema."""
    temperatures = []
    voltages = []
    clocks = []
    utilization = []

    for channel in range(_MAX_SENSOR_CHANNELS):
        try:
            temperature = _number(status.get_temperature(channel))
        except Exception:
            break
        if temperature is None:
            break
        if temperature == INVALID_TEMPERATURE:
            break

        temperatures.append(temperature)
        try:
            voltage = _number(status.get_npu_voltage(channel))
            if voltage is not None and voltage >= 0:
                voltages.append(voltage)
        except Exception:
            pass
        try:
            clock = _number(status.get_npu_clock(channel))
            if clock is not None and clock >= 0:
                clocks.append(clock)
        except Exception:
            pass
        try:
            core_utilization = _number(status.get_core_utilization(channel))
            if core_utilization is not None and core_utilization >= 0:
                utilization.append(core_utilization)
        except Exception:
            pass

    device_id = index
    try:
        device_id = status.get_id()
    except Exception:
        pass

    dram_used = 0
    dram_free = 0
    try:
        used = int(status.get_memory_used())
        free = int(status.get_memory_free())
        if used >= 0 and free >= 0:
            dram_used = used
            dram_free = free
    except Exception:
        pass
    dram_total = dram_used + dram_free

    return {
        "id": index,
        "device_id": device_id,
        "cores": len(temperatures),
        "temperatures": temperatures,
        "voltages_mV": voltages,
        "clocks_MHz": clocks,
        "temp_avg": _average(temperatures),
        "voltage_avg": _average(voltages),
        "clock_avg": _average(clocks),
        "power_est_mW": _power_estimate(voltages),
        "dram_used_bytes": dram_used,
        "dram_free_bytes": dram_free,
        "dram_total_bytes": dram_total,
        "dram_used_mb": round(dram_used / float(_MEBIBYTE), 1),
        "dram_total_mb": round(dram_total / float(_MEBIBYTE), 1),
        "dram_pct": round(100.0 * dram_used / dram_total, 1) if dram_total else 0.0,
        "utilization": utilization,
    }


def build_snapshot(device_status, timestamp, sequence=0):
    """Read DeviceStatus directly and return a Monitor-compatible snapshot."""
    count = int(device_status.get_device_count())
    if count < 0:
        count = 0

    npus = []
    stale = False
    for index in range(count):
        status = device_status.get_current_status(index)
        try:
            if not status.is_valid():
                stale = True
        except Exception:
            stale = True
        npus.append(_device_snapshot(status, index))

    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "snapshot",
        "available": True,
        "timestamp": timestamp,
        "ts": timestamp,
        "source": "device_status",
        "source_mode": "stale" if stale else "real",
        "stale": stale,
        "sequence": sequence,
        "count": count,
        "npus": npus,
    }


def emit(kind, payload, stream=sys.stdout):
    """Write one compact, prefixed JSON record to stdout-compatible ``stream``."""
    record = dict(payload)
    record["schema_version"] = SCHEMA_VERSION
    record["kind"] = kind
    encoded = json.dumps(record, separators=(",", ":"), ensure_ascii=False)
    with _EMIT_LOCK:
        stream.write(FRAME_PREFIX + encoded + "\n")
        stream.flush()


def collect_system_info(configuration):
    """Return cached runtime version metadata without collecting host information."""
    global _SYSTEM_INFO_CACHE
    if _SYSTEM_INFO_CACHE is None:
        def optional_version(getter):
            try:
                return getter()
            except Exception:
                return "N/A"

        _SYSTEM_INFO_CACHE = {
            "sdk_version": optional_version(configuration.get_version),
            "driver_version": optional_version(configuration.get_driver_version),
            "pcie_driver_version": optional_version(
                configuration.get_pcie_driver_version
            ),
        }
    return dict(_SYSTEM_INFO_CACHE)


def _error_payload(error, source_mode="stale"):
    return {
        "available": False,
        "source": "device_status",
        "source_mode": source_mode,
        "npus": [],
        "error": str(error),
    }


def _register_event_handler(dispatcher_type):
    """Best-effort event subscription; dispatcher failures cannot stop sampling."""
    def on_event(*args):
        try:
            event = {
                "level": args[0] if len(args) > 0 else None,
                "type": args[1] if len(args) > 1 else None,
                "code": args[2] if len(args) > 2 else None,
                "message": str(args[3]) if len(args) > 3 else "",
                "timestamp": args[4] if len(args) > 4 else time.time(),
            }
            emit("event", {
                "available": True,
                "source": "runtime_event_dispatcher",
                "source_mode": "real",
                "npus": [],
                "event": event,
            }, stream=sys.stdout)
        except Exception:
            return

    try:
        dispatcher = dispatcher_type()
        dispatcher.register_event_handler(on_event)
    except Exception:
        pass


def main(argv=None):
    """Run the polling loop and emit framed telemetry records until interrupted."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--interval", type=_finite_float, default=1.0)
    arguments = parser.parse_args(argv)
    interval = max(1.0, arguments.interval)

    try:
        DeviceStatus, Configuration, RuntimeEventDispatcher = _load_runtime_api()
        configuration = Configuration()
        system_info = collect_system_info(configuration)
    except Exception as error:
        emit("error", _error_payload(error, source_mode="unavailable"), stream=sys.stdout)
        return 1

    emit("hello", {
        "available": True,
        "source": "device_status",
        "source_mode": "real",
        "npus": [],
        "system_info": system_info,
    }, stream=sys.stdout)
    _register_event_handler(RuntimeEventDispatcher)

    sequence = 0
    try:
        while True:
            try:
                snapshot = build_snapshot(DeviceStatus, time.time(), sequence=sequence)
                emit("snapshot", snapshot, stream=sys.stdout)
                sequence += 1
            except Exception as error:
                emit("error", _error_payload(error), stream=sys.stdout)
            time.sleep(interval)
    except KeyboardInterrupt:
        emit("stopped", {
            "available": True,
            "source": "device_status",
            "source_mode": "real",
            "npus": [],
        }, stream=sys.stdout)
        return 0


if __name__ == "__main__":
    sys.exit(main())
import ast
import copy
import inspect
import sys
import threading
from pathlib import Path

import pytest


class _FakeDeviceStatus:
    def get_temperature(self, ch: int) -> int:
        return [40, 42, 44, -32768][ch]

    def get_npu_voltage(self, ch: int) -> int:
        return [700, 710, 720, 0][ch]

    def get_npu_clock(self, ch: int) -> int:
        return [900, 910, 920, 0][ch]

    def get_id(self) -> int:
        return 123

    def get_core_utilization(self, ch: int) -> float:
        return [12.5, 25.0, 37.5, -1][ch]

    def get_memory_used(self) -> int:
        return 512 * 1024 * 1024

    def get_memory_free(self) -> int:
        return 512 * 1024 * 1024


class _FakeDS:
    @staticmethod
    def get_device_count() -> int:
        return 1

    @staticmethod
    def get_current_status(device_id: int) -> _FakeDeviceStatus:
        assert device_id == 0
        return _FakeDeviceStatus()


class _FakeTelemetrySupervisor:
    """Small cache-only supervisor fake; it must never expose a native SDK."""

    def __init__(self, snapshot, system_info=None, events=None):
        self._snapshot = snapshot
        self._system_info = system_info or {}
        self._events = events or []
        self.event_calls = []

    def snapshot(self):
        return copy.deepcopy(self._snapshot)

    def system_info(self):
        return copy.deepcopy(self._system_info)

    def events(self, since=0.0, limit=100):
        self.event_calls.append((since, limit))
        return copy.deepcopy(self._events[:limit])


_MISSING = object()


@pytest.fixture(autouse=True)
def _restore_hardware_state():
    """Keep legacy DeviceStatus tests and cache-backed tests independent."""
    import hardware

    names = (
        "_DS", "_dx_ok", "_NPU_STATS_BIN", "_APP_ROOT", "_TELEMETRY",
        "_TELEMETRY_EPOCH", "_TELEMETRY_ACTIVE", "_EXPLICIT_MOCK", "_hw_cache",
        "_prev_cpu",
    )
    original = {name: getattr(hardware, name, _MISSING) for name in names}
    hardware._hw_cache = {"d": None, "t": 0.0}
    hardware._prev_cpu = None
    try:
        yield
    finally:
        for name, value in original.items():
            if value is _MISSING:
                if hasattr(hardware, name):
                    delattr(hardware, name)
            else:
                setattr(hardware, name, value)


def _telemetry_snapshot(source_mode="real", available=True, npus=None, **extra):
    data = {
        "available": available,
        "source_mode": source_mode,
        "npus": [] if npus is None else npus,
        "diagnostics": ["worker cache healthy"],
    }
    data.update(extra)
    return data


def test_get_hw_merges_real_telemetry_cache_with_host_metrics(tmp_path):
    import hardware

    npu = {
        "id": 0,
        "device_id": 7,
        "cores": 2,
        "temperatures": [41.0, 43.0],
        "voltages_mV": [710.0, 720.0],
        "clocks_MHz": [900.0, 910.0],
        "temp_avg": 42.0,
        "voltage_avg": 715.0,
        "clock_avg": 905.0,
        "power_est_mW": 357.5,
        "dram_used_bytes": 768 * 1024 * 1024,
        "dram_free_bytes": 256 * 1024 * 1024,
        "dram_total_bytes": 1024 * 1024 * 1024,
        "dram_used_mb": 768.0,
        "dram_total_mb": 1024.0,
        "dram_pct": 75.0,
        "utilization": [12.5, 87.5],
    }
    supervisor = _FakeTelemetrySupervisor(
        _telemetry_snapshot(npus=[npu], sequence=3)
    )
    hardware.init_hw(telemetry=supervisor, app_root=tmp_path)

    data = hardware.get_hw()

    assert data["available"] is True
    assert data["mock"] is False
    assert data["source_mode"] == "real"
    assert data["telemetry"]["source_mode"] == "real"
    assert data["telemetry"]["available"] is True
    assert data["npus"][0]["utilization"] == [12.5, 87.5]
    assert data["npus"][0]["dram_used_bytes"] == 768 * 1024 * 1024
    assert data["npus"][0]["dram_free_bytes"] == 256 * 1024 * 1024
    assert data["npus"][0]["dram_pct"] == 75.0
    assert "cpu_load" in data
    assert "mem_total_mb" in data
    assert "disk_total_gb" in data


def test_get_hw_preserves_stale_cached_npu_values(tmp_path):
    import hardware

    supervisor = _FakeTelemetrySupervisor(
        _telemetry_snapshot(
            source_mode="stale",
            available=False,
            npus=[{"id": 0, "utilization": [55.0], "dram_used_mb": 512.0}],
        )
    )
    hardware.init_hw(telemetry=supervisor, app_root=tmp_path)

    data = hardware.get_hw()

    assert data["available"] is False
    assert data["mock"] is False
    assert data["source_mode"] == "stale"
    assert data["telemetry"]["source_mode"] == "stale"
    assert data["npus"] == [{"id": 0, "utilization": [55.0], "dram_used_mb": 512.0}]


def test_get_hw_unavailable_cache_never_generates_synthetic_npu(tmp_path, monkeypatch):
    import hardware

    supervisor = _FakeTelemetrySupervisor(
        _telemetry_snapshot(
            source_mode="unavailable",
            available=False,
            npus=[{"id": 0, "utilization": [99.0]}],
            diagnostics=["worker unavailable"],
            error="worker stopped",
        )
    )
    hardware.init_hw(telemetry=supervisor, app_root=tmp_path)

    def unexpected_mock():
        raise AssertionError("normal unavailable telemetry must not call _mock_npu")

    monkeypatch.setattr(hardware, "_mock_npu", unexpected_mock)
    data = hardware.get_hw()

    assert data["available"] is False
    assert data["mock"] is False
    assert data["source_mode"] == "unavailable"
    assert data["npus"] == []
    assert data["telemetry"]["diagnostics"] == ["worker unavailable"]
    assert data["telemetry"]["error"] == "worker stopped"


def test_get_hw_generates_synthetic_npu_only_for_explicit_mock(tmp_path):
    import hardware

    supervisor = _FakeTelemetrySupervisor(
        _telemetry_snapshot(source_mode="unavailable", available=False)
    )
    hardware.init_hw(
        telemetry=supervisor,
        explicit_mock=True,
        app_root=tmp_path,
    )

    data = hardware.get_hw()

    assert data["available"] is False
    assert data["mock"] is True
    assert data["source_mode"] == "mock"
    assert data["telemetry"]["source_mode"] == "mock"
    assert data["telemetry"]["available"] is False
    assert data["npus"]
    assert all(npu["mock"] is True for npu in data["npus"])


def test_get_hw_normalizes_untrusted_worker_mock_to_unavailable(tmp_path):
    import hardware

    supervisor = _FakeTelemetrySupervisor(
        _telemetry_snapshot(
            source_mode="mock",
            available=True,
            npus=[{"id": 0, "utilization": [99.0], "mock": True}],
        )
    )
    hardware.init_hw(telemetry=supervisor, app_root=tmp_path)

    data = hardware.get_hw()

    assert data["available"] is False
    assert data["mock"] is False
    assert data["source_mode"] == "unavailable"
    assert data["npus"] == []
    assert data["telemetry"]["source_mode"] == "unavailable"


def test_get_hw_cache_returns_independent_nested_data(tmp_path):
    import hardware

    supervisor = _FakeTelemetrySupervisor(
        _telemetry_snapshot(
            npus=[
                {
                    "id": 0,
                    "utilization": [41.0],
                    "details": {"temperature": 42.0},
                }
            ],
            diagnostics=["worker cache healthy"],
        )
    )
    hardware.init_hw(telemetry=supervisor, app_root=tmp_path)

    first = hardware.get_hw()
    first["npus"][0]["utilization"][0] = -1.0
    first["npus"][0]["details"]["temperature"] = -1.0
    first["telemetry"]["diagnostics"].append("mutated by caller")

    cached = hardware.get_hw()

    assert cached["npus"][0]["utilization"] == [41.0]
    assert cached["npus"][0]["details"] == {"temperature": 42.0}
    assert cached["telemetry"]["diagnostics"] == ["worker cache healthy"]


def test_refresh_after_telemetry_rebind_snapshots_outside_lock_and_discards_second_rebind(
    tmp_path,
):
    import hardware

    class _SnapshotSupervisor:
        def __init__(self, snapshot, on_snapshot=None):
            self._snapshot = snapshot
            self._on_snapshot = on_snapshot
            self.lock_was_available = None
            self.snapshot_calls = 0

        def snapshot(self):
            self.snapshot_calls += 1
            acquired = hardware._hw_lock.acquire(blocking=False)
            self.lock_was_available = acquired
            if acquired:
                hardware._hw_lock.release()
                if self._on_snapshot is not None:
                    self._on_snapshot()
            return copy.deepcopy(self._snapshot)

    replacement = _SnapshotSupervisor(
        _telemetry_snapshot(npus=[{"id": 2, "utilization": [20.0]}])
    )
    refreshing = _SnapshotSupervisor(
        _telemetry_snapshot(npus=[{"id": 1, "utilization": [10.0]}]),
        on_snapshot=lambda: hardware.init_hw(telemetry=replacement, app_root=tmp_path),
    )
    hardware.init_hw(telemetry=refreshing, app_root=tmp_path)

    refreshed = hardware._refresh_after_telemetry_rebind({"ts": 1.0})

    assert refreshing.lock_was_available is True
    assert refreshing.snapshot_calls == 1
    assert replacement.snapshot_calls == 0
    assert refreshed["available"] is False
    assert refreshed["source_mode"] == "unavailable"
    assert refreshed["npus"] == []
    assert hardware._hw_cache["d"] is None


def test_get_hw_retries_when_telemetry_binds_during_legacy_host_probe(
    tmp_path, monkeypatch,
):
    import hardware

    started_host_probe = threading.Event()
    release_host_probe = threading.Event()
    original_add_host_metrics = hardware._add_host_metrics
    supervisor = _FakeTelemetrySupervisor(
        _telemetry_snapshot(npus=[{"id": 7, "utilization": [87.5]}])
    )
    result = []

    def block_host_probe(data):
        started_host_probe.set()
        assert release_host_probe.wait(timeout=1.0)
        original_add_host_metrics(data)

    def read_hardware():
        result.append(hardware.get_hw())

    hardware.init_hw(telemetry=None, app_root=tmp_path)
    monkeypatch.setattr(hardware, "_add_host_metrics", block_host_probe)
    reader = threading.Thread(target=read_hardware)
    try:
        reader.start()
        assert started_host_probe.wait(timeout=1.0)

        hardware.init_hw(telemetry=supervisor, app_root=tmp_path)
        release_host_probe.set()
        reader.join(timeout=1.0)

        assert not reader.is_alive()
        assert result[0]["available"] is True
        assert result[0]["source_mode"] == "real"
        assert result[0]["npus"] == [{"id": 7, "utilization": [87.5]}]

        cached = hardware.get_hw()
        assert cached["available"] is True
        assert cached["source_mode"] == "real"
        assert cached["npus"] == [{"id": 7, "utilization": [87.5]}]
    finally:
        release_host_probe.set()
        reader.join(timeout=1.0)


def test_hardware_init_serializes_singleton_lifecycle_without_sys_path_mutation(
    monkeypatch,
):
    from dx_monitor.core import events, hardware_init

    class _Supervisor:
        instances = []

        def __init__(self):
            self.start_calls = 0
            self.stop_calls = 0
            self.event_calls = 0
            self.__class__.instances.append(self)

        def start(self):
            self.start_calls += 1

        def stop(self):
            self.stop_calls += 1

        def events(self, since=0.0, limit=100):
            self.event_calls += 1
            return []

    init_hw_calls = []
    original_supervisor = hardware_init._SUPERVISOR
    monkeypatch.setattr(hardware_init, "TelemetrySupervisor", _Supervisor)
    from shared import hardware as shared_hardware

    monkeypatch.setattr(
        shared_hardware,
        "init_hw",
        lambda **kwargs: init_hw_calls.append(kwargs),
    )
    hardware_init._SUPERVISOR = None
    events.set_provider(None)

    try:
        sys_path_before = list(sys.path)
        first = hardware_init.init()
        assert hardware_init.init() is first

        barrier = threading.Barrier(3)
        initialized = []

        def initialize_in_thread():
            barrier.wait()
            initialized.append(hardware_init.init())

        threads = [threading.Thread(target=initialize_in_thread) for _ in range(2)]
        for thread in threads:
            thread.start()
        barrier.wait()
        for thread in threads:
            thread.join(timeout=1.0)

        assert all(not thread.is_alive() for thread in threads)
        assert initialized == [first, first]
        assert _Supervisor.instances == [first]
        assert first.start_calls == 1
        assert len(init_hw_calls) == 1
        assert events.get_events() == []
        assert first.event_calls == 1
        assert sys.path == sys_path_before

        replacement_provider = object()
        events.set_provider(replacement_provider)
        hardware_init.shutdown()

        assert first.stop_calls == 1
        assert events.clear_provider_if(replacement_provider) is True
    finally:
        events.set_provider(None)
        hardware_init._SUPERVISOR = original_supervisor


def test_hardware_init_waits_for_shutdown_stop_before_replacing_supervisor(
    monkeypatch,
):
    from dx_monitor.core import events, hardware_init

    class _BlockingSupervisor:
        instances = []
        stop_started = threading.Event()
        release_stop = threading.Event()
        replacement_constructed = threading.Event()

        def __init__(self):
            self.start_calls = 0
            self.stop_calls = 0
            if self.__class__.instances:
                self.__class__.replacement_constructed.set()
            self.__class__.instances.append(self)

        def start(self):
            self.start_calls += 1

        def stop(self):
            self.stop_calls += 1
            if self is self.__class__.instances[0]:
                self.__class__.stop_started.set()
                assert self.__class__.release_stop.wait(timeout=1.0)

        def events(self, since=0.0, limit=100):
            return []

    original_supervisor = hardware_init._SUPERVISOR
    original_stopping = getattr(hardware_init, "_STOPPING", _MISSING)
    monkeypatch.setattr(hardware_init, "TelemetrySupervisor", _BlockingSupervisor)
    from shared import hardware as shared_hardware

    monkeypatch.setattr(shared_hardware, "init_hw", lambda **kwargs: None)
    with hardware_init._LOCK:
        hardware_init._SUPERVISOR = None
        if hasattr(hardware_init, "_STOPPING"):
            hardware_init._STOPPING = False
    events.set_provider(None)

    shutdown_errors = []
    init_errors = []
    initialized = []

    def shutdown_in_thread():
        try:
            hardware_init.shutdown()
        except BaseException as error:
            shutdown_errors.append(error)

    def initialize_in_thread():
        try:
            initialized.append(hardware_init.init())
        except BaseException as error:
            init_errors.append(error)

    shutdown_thread = None
    init_thread = None
    try:
        first = hardware_init.init()

        shutdown_thread = threading.Thread(target=shutdown_in_thread)
        shutdown_thread.start()
        assert _BlockingSupervisor.stop_started.wait(timeout=1.0)

        init_thread = threading.Thread(target=initialize_in_thread)
        init_thread.start()

        assert not _BlockingSupervisor.replacement_constructed.wait(timeout=0.2)
        assert _BlockingSupervisor.instances == [first]
        assert first.start_calls == 1

        _BlockingSupervisor.release_stop.set()
        shutdown_thread.join(timeout=1.0)
        init_thread.join(timeout=1.0)

        assert not shutdown_thread.is_alive()
        assert not init_thread.is_alive()
        assert shutdown_errors == []
        assert init_errors == []
        assert len(_BlockingSupervisor.instances) == 2
        replacement = _BlockingSupervisor.instances[1]
        assert initialized == [replacement]
        assert replacement.start_calls == 1
        assert first.stop_calls == 1
    finally:
        _BlockingSupervisor.release_stop.set()
        if shutdown_thread is not None:
            shutdown_thread.join(timeout=1.0)
        if init_thread is not None:
            init_thread.join(timeout=1.0)
        events.set_provider(None)
        with hardware_init._LOCK:
            hardware_init._SUPERVISOR = original_supervisor
            if original_stopping is not _MISSING:
                hardware_init._STOPPING = original_stopping


def test_hardware_shutdown_detaches_telemetry_without_losing_host_metrics(
    monkeypatch,
):
    from dx_monitor.core import events, hardware_init
    from shared import hardware as shared_hardware

    class _Supervisor:
        def __init__(self):
            self.snapshot_calls = 0
            self.system_info_calls = 0
            self.stop_calls = 0

        def start(self):
            return None

        def stop(self):
            self.stop_calls += 1

        def snapshot(self):
            self.snapshot_calls += 1
            return _telemetry_snapshot(npus=[{"id": 0}])

        def system_info(self):
            self.system_info_calls += 1
            return {"available": True, "npu_count": 1}

        def events(self, since=0.0, limit=100):
            return []

    original_supervisor = hardware_init._SUPERVISOR
    original_stopping = hardware_init._STOPPING
    monkeypatch.setattr(hardware_init, "TelemetrySupervisor", _Supervisor)
    monkeypatch.delenv("DX_MONITOR_EXPLICIT_MOCK", raising=False)
    with hardware_init._LOCK:
        hardware_init._SUPERVISOR = None
        hardware_init._STOPPING = False
    events.set_provider(None)

    try:
        supervisor = hardware_init.init()
        assert shared_hardware._TELEMETRY is supervisor

        hardware_init.shutdown()
        snapshot_calls = supervisor.snapshot_calls
        system_info_calls = supervisor.system_info_calls

        def unexpected_mock():
            raise AssertionError("detached telemetry must not generate mock NPU data")

        monkeypatch.setattr(shared_hardware, "_mock_npu", unexpected_mock)
        hardware = shared_hardware.get_hw()
        system_info = shared_hardware.get_sysinfo()

        assert supervisor.stop_calls == 1
        assert shared_hardware._TELEMETRY is None
        assert hardware["available"] is False
        assert hardware["mock"] is False
        assert hardware["source_mode"] == "unavailable"
        assert hardware["npus"] == []
        assert hardware["telemetry"]["source_mode"] == "unavailable"
        assert "cpu_load" in hardware
        assert "mem_total_mb" in hardware
        assert system_info["dx_engine_available"] is False
        assert system_info["npu_count"] == 0
        assert supervisor.snapshot_calls == snapshot_calls
        assert supervisor.system_info_calls == system_info_calls
    finally:
        events.set_provider(None)
        with hardware_init._LOCK:
            hardware_init._SUPERVISOR = original_supervisor
            hardware_init._STOPPING = original_stopping


def test_hardware_shutdown_invalidates_cached_telemetry_before_stop(monkeypatch):
    from dx_monitor.core import events, hardware_init
    from shared import hardware as shared_hardware

    class _BlockingSupervisor:
        stop_started = threading.Event()
        release_stop = threading.Event()

        def start(self):
            return None

        def stop(self):
            self.__class__.stop_started.set()
            assert self.__class__.release_stop.wait(timeout=1.0)

        def snapshot(self):
            return _telemetry_snapshot(npus=[{"id": 0, "utilization": [99.0]}])

        def events(self, since=0.0, limit=100):
            return []

    original_supervisor = hardware_init._SUPERVISOR
    original_stopping = hardware_init._STOPPING
    monkeypatch.setattr(hardware_init, "TelemetrySupervisor", _BlockingSupervisor)
    monkeypatch.delenv("DX_MONITOR_EXPLICIT_MOCK", raising=False)
    with hardware_init._LOCK:
        hardware_init._SUPERVISOR = None
        hardware_init._STOPPING = False
    events.set_provider(None)

    shutdown_thread = None
    try:
        supervisor = hardware_init.init()
        assert shared_hardware.get_hw()["source_mode"] == "real"

        shutdown_thread = threading.Thread(target=hardware_init.shutdown)
        shutdown_thread.start()
        assert _BlockingSupervisor.stop_started.wait(timeout=1.0)

        during_stop = shared_hardware.get_hw()

        assert during_stop["available"] is False
        assert during_stop["source_mode"] == "unavailable"
        assert during_stop["npus"] == []

        _BlockingSupervisor.release_stop.set()
        shutdown_thread.join(timeout=1.0)
        assert not shutdown_thread.is_alive()
        assert supervisor is not None
    finally:
        _BlockingSupervisor.release_stop.set()
        if shutdown_thread is not None:
            shutdown_thread.join(timeout=1.0)
        events.set_provider(None)
        with hardware_init._LOCK:
            hardware_init._SUPERVISOR = original_supervisor
            hardware_init._STOPPING = original_stopping


def test_hardware_shutdown_does_not_detach_replacement_telemetry_binding(
    monkeypatch,
):
    from dx_monitor.core import events, hardware_init
    from shared import hardware as shared_hardware

    class _ReplacementSupervisor:
        def __init__(self):
            self.snapshot_calls = 0

        def snapshot(self):
            self.snapshot_calls += 1
            return _telemetry_snapshot(npus=[{"id": 1}])

        def events(self, since=0.0, limit=100):
            return [{"message": "replacement"}]

    replacement = _ReplacementSupervisor()

    class _Supervisor:
        def __init__(self):
            self.stop_calls = 0

        def start(self):
            return None

        def stop(self):
            self.stop_calls += 1
            shared_hardware.init_hw(telemetry=replacement)
            events.set_provider(replacement)

        def snapshot(self):
            return _telemetry_snapshot(npus=[{"id": 0}])

        def events(self, since=0.0, limit=100):
            return []

    original_supervisor = hardware_init._SUPERVISOR
    original_stopping = hardware_init._STOPPING
    monkeypatch.setattr(hardware_init, "TelemetrySupervisor", _Supervisor)
    with hardware_init._LOCK:
        hardware_init._SUPERVISOR = None
        hardware_init._STOPPING = False
    events.set_provider(None)

    try:
        supervisor = hardware_init.init()
        hardware_init.shutdown()

        assert supervisor.stop_calls == 1
        assert shared_hardware._TELEMETRY is replacement
        assert shared_hardware.get_hw()["npus"] == [{"id": 1}]
        assert replacement.snapshot_calls == 1
        assert events.get_events() == [{"message": "replacement"}]
    finally:
        events.set_provider(None)
        with hardware_init._LOCK:
            hardware_init._SUPERVISOR = original_supervisor
            hardware_init._STOPPING = original_stopping


def test_hardware_init_exception_after_binding_detaches_candidate(monkeypatch):
    from dx_monitor.core import events, hardware_init
    from shared import hardware as shared_hardware

    class _Supervisor:
        instances = []

        def __init__(self):
            self.snapshot_calls = 0
            self.stop_calls = 0
            self.__class__.instances.append(self)

        def start(self):
            return None

        def stop(self):
            self.stop_calls += 1

        def snapshot(self):
            self.snapshot_calls += 1
            return _telemetry_snapshot(npus=[{"id": 0}])

    def raise_after_bind(provider):
        raise RuntimeError("provider bind failed")

    original_supervisor = hardware_init._SUPERVISOR
    original_stopping = hardware_init._STOPPING
    monkeypatch.setattr(hardware_init, "TelemetrySupervisor", _Supervisor)
    monkeypatch.setattr(events, "set_provider", raise_after_bind)
    with hardware_init._LOCK:
        hardware_init._SUPERVISOR = None
        hardware_init._STOPPING = False

    try:
        with pytest.raises(RuntimeError, match="provider bind failed"):
            hardware_init.init()

        supervisor = _Supervisor.instances[0]
        snapshot_calls = supervisor.snapshot_calls

        def unexpected_mock():
            raise AssertionError("failed initialization must not retain mock telemetry")

        monkeypatch.setattr(shared_hardware, "_mock_npu", unexpected_mock)
        hardware = shared_hardware.get_hw()

        assert supervisor.stop_calls == 1
        assert hardware_init._SUPERVISOR is None
        assert shared_hardware._TELEMETRY is None
        assert hardware["available"] is False
        assert hardware["mock"] is False
        assert hardware["source_mode"] == "unavailable"
        assert hardware["npus"] == []
        assert supervisor.snapshot_calls == snapshot_calls
    finally:
        with hardware_init._LOCK:
            hardware_init._SUPERVISOR = original_supervisor
            hardware_init._STOPPING = original_stopping


def test_get_sysinfo_uses_supervisor_system_cache_when_unavailable(tmp_path):
    import hardware

    supervisor = _FakeTelemetrySupervisor(
        _telemetry_snapshot(source_mode="unavailable", available=False),
        system_info={
            "npu_count": "2",
            "sdk_version": "sdk-cache",
            "driver_version": "driver-cache",
            "pcie_driver_version": "pcie-cache",
            "available": False,
        },
    )
    hardware.init_hw(telemetry=supervisor, app_root=tmp_path)

    info = hardware.get_sysinfo()

    assert info["dx_engine_available"] is False
    assert info["npu_count"] == 2
    assert info["sdk_version"] == "sdk-cache"
    assert info["driver_version"] == "driver-cache"
    assert info["pcie_driver_version"] == "pcie-cache"


def test_get_sysinfo_does_not_query_invalidated_stopping_telemetry(tmp_path):
    import hardware

    class _StoppingSupervisor:
        def __init__(self):
            self.system_info_calls = 0

        def snapshot(self):
            return _telemetry_snapshot(npus=[{"id": 0}])

        def system_info(self):
            self.system_info_calls += 1
            raise AssertionError("stopping telemetry must not be queried")

    supervisor = _StoppingSupervisor()
    hardware.init_hw(telemetry=supervisor, app_root=tmp_path)
    assert hardware.invalidate_telemetry_if(supervisor) is True

    info = hardware.get_sysinfo()

    assert info["dx_engine_available"] is False
    assert info["npu_count"] == 0
    assert info["sdk_version"] == "N/A"
    assert info["driver_version"] == "N/A"
    assert info["pcie_driver_version"] == "N/A"
    assert supervisor.system_info_calls == 0


def test_get_sysinfo_recognizes_deepx_vendor_device_pci_line(monkeypatch):
    import hardware

    original_check_output = hardware.subprocess.check_output

    def lspci_output(args, **kwargs):
        if args == ["lspci"]:
            return "03:00.0 Processing accelerators: Device 1ff4:0000\n"
        return original_check_output(args, **kwargs)

    monkeypatch.setattr(hardware.subprocess, "check_output", lspci_output)

    info = hardware.get_sysinfo()

    assert info["npu_pci"] == [
        "03:00.0 Processing accelerators: Device 1ff4:0000"
    ]


def test_get_sysinfo_discards_telemetry_rebound_during_host_probe(tmp_path, monkeypatch):
    import hardware

    class _Supervisor(_FakeTelemetrySupervisor):
        def __init__(self, system_info):
            super().__init__(
                _telemetry_snapshot(npus=[{"id": 0}]),
                system_info=system_info,
            )
            self.system_info_calls = 0

        def system_info(self):
            self.system_info_calls += 1
            return super().system_info()

    original = _Supervisor(
        {
            "available": True,
            "npu_count": 1,
            "sdk_version": "old-sdk",
            "driver_version": "old-driver",
            "pcie_driver_version": "old-pcie-driver",
        }
    )
    replacement = _Supervisor(
        {
            "available": True,
            "npu_count": 2,
            "sdk_version": "new-sdk",
            "driver_version": "new-driver",
            "pcie_driver_version": "new-pcie-driver",
        }
    )
    hardware.init_hw(telemetry=original, app_root=tmp_path)
    monkeypatch.setitem(
        sys.modules,
        "cv2",
        type("_FakeCV2", (), {"__version__": "test"}),
    )
    original_check_output = hardware.subprocess.check_output

    def invalidate_and_rebind(*args, **kwargs):
        if args[0] != ["lspci"]:
            return original_check_output(*args, **kwargs)
        assert hardware.invalidate_telemetry_if(original) is True
        hardware.init_hw(telemetry=replacement, app_root=tmp_path)
        return "00:00.0 DeepX NPU"

    monkeypatch.setattr(hardware.subprocess, "check_output", invalidate_and_rebind)

    info = hardware.get_sysinfo()

    assert original.system_info_calls == 1
    assert replacement.system_info_calls == 0
    assert info["dx_engine_available"] is False
    assert info["npu_count"] == 0
    assert info["sdk_version"] == "N/A"
    assert info["driver_version"] == "N/A"
    assert info["pcie_driver_version"] == "N/A"
    assert info["npu_pci"] == ["00:00.0 DeepX NPU"]
    assert "uptime_seconds" in info
    assert "cpu_model" in info


def test_events_provider_routes_to_supervisor_without_native_dispatcher():
    from dx_monitor.core import events

    supervisor = _FakeTelemetrySupervisor(
        _telemetry_snapshot(),
        events=[{"time": 11.0, "message": "worker event"}],
    )
    try:
        events.set_provider(supervisor)

        result = events.get_events(since=10.0, limit=5)

        assert result == [{"time": 11.0, "message": "worker event"}]
        assert supervisor.event_calls == [(10.0, 5)]
    finally:
        events.set_provider(None)


def test_events_provider_result_is_deeply_isolated_from_caller_mutation():
    from dx_monitor.core import events

    provider_events = [
        {
            "time": 11.0,
            "metadata": {"tags": ["provider-owned"]},
        }
    ]

    class _Provider:
        def events(self, since=0.0, limit=100):
            return provider_events

    try:
        events.set_provider(_Provider())

        result = events.get_events()
        result[0]["metadata"]["tags"].append("caller-mutated")

        assert provider_events == [
            {
                "time": 11.0,
                "metadata": {"tags": ["provider-owned"]},
            }
        ]
    finally:
        events.set_provider(None)


def test_events_discards_result_when_provider_is_replaced_while_blocked():
    from dx_monitor.core import events

    class _BlockingProvider:
        started = threading.Event()
        release = threading.Event()

        def events(self, since=0.0, limit=100):
            self.__class__.started.set()
            assert self.__class__.release.wait(timeout=1.0)
            return [{"message": "old provider event"}]

    provider = _BlockingProvider()
    replacement = _FakeTelemetrySupervisor(_telemetry_snapshot())
    result = []
    reader = None
    try:
        events.set_provider(provider)

        reader = threading.Thread(target=lambda: result.extend(events.get_events()))
        reader.start()
        assert _BlockingProvider.started.wait(timeout=1.0)

        events.set_provider(replacement)
        _BlockingProvider.release.set()
        reader.join(timeout=1.0)

        assert not reader.is_alive()
        assert result == []
    finally:
        _BlockingProvider.release.set()
        if reader is not None:
            reader.join(timeout=1.0)
        events.set_provider(None)


def test_monitor_hardware_paths_do_not_import_native_runtime_modules():
    studio_root = Path(__file__).resolve().parents[2]
    paths = (
        studio_root / "dx_monitor" / "core" / "hardware_init.py",
        studio_root / "shared" / "hardware.py",
        studio_root / "dx_monitor" / "core" / "events.py",
    )

    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
                assert not any(name == "dx_engine" or name.startswith("dx_engine.") for name in imported)
                assert "RuntimeEventDispatcher" not in imported
            elif isinstance(node, ast.ImportFrom):
                assert node.module is None or not (
                    node.module == "dx_engine" or node.module.startswith("dx_engine.")
                )
                assert all(alias.name != "RuntimeEventDispatcher" for alias in node.names)


def test_get_hw_ignores_invalid_temperature_sentinel_when_averaging(tmp_path):
    import hardware

    original_state = (
        hardware._DS,
        hardware._dx_ok,
        hardware._NPU_STATS_BIN,
        hardware._APP_ROOT,
        hardware._hw_cache,
        hardware._prev_cpu,
    )
    try:
        hardware._hw_cache = {"d": None, "t": 0.0}
        hardware.init_hw(
            ds=_FakeDS,
            dx_ok=True,
            npu_stats_bin=tmp_path / "missing-npu-stats",
            app_root=tmp_path,
        )

        data = hardware.get_hw()
        npu = data["npus"][0]

        assert npu["cores"] == 3
        assert npu["temperatures"] == [40, 42, 44]
        assert npu["voltages_mV"] == [700, 710, 720]
        assert npu["clocks_MHz"] == [900, 910, 920]
        assert npu["temp_avg"] == pytest.approx(42.0)
        assert npu["voltage_avg"] == pytest.approx(710.0)
        assert npu["clock_avg"] == pytest.approx(910.0)
        assert npu["utilization"] == [12.5, 25.0, 37.5]
        assert npu["dram_used_mb"] == pytest.approx(512.0)
        assert npu["dram_total_mb"] == pytest.approx(1024.0)
    finally:
        (
            hardware._DS,
            hardware._dx_ok,
            hardware._NPU_STATS_BIN,
            hardware._APP_ROOT,
            hardware._hw_cache,
            hardware._prev_cpu,
        ) = original_state


def test_get_hw_includes_metadata_from_optional_npu_stats_binary(tmp_path):
    import hardware

    assert "npu_stats_bin" in inspect.signature(hardware.init_hw).parameters

    helper = tmp_path / "dx_npu_stats"
    helper.write_text(
        "#!/usr/bin/env python3\n"
        'print(\'{"firmware_version":"1.2.3","device_type":"DX-M1",'
        '"device_variant":"Q1","board_type":"EVB","memory_type":"LPDDR5",'
        '"memory_size_bytes":4294967296,"memory_freq_mhz":3200,'
        '"ddr_status":[0,0,0,0],"ddr_sbe_cnt":[0,0,0,0],'
        '"ddr_dbe_cnt":[0,0,0,0]}\')\n',
        encoding="utf-8",
    )
    helper.chmod(0o755)

    original_state = (
        hardware._DS,
        hardware._dx_ok,
        hardware._NPU_STATS_BIN,
        hardware._APP_ROOT,
        hardware._hw_cache,
    )
    try:
        hardware._hw_cache = {"d": None, "t": 0.0}
        hardware.init_hw(ds=_FakeDS, dx_ok=True, npu_stats_bin=helper, app_root=tmp_path)

        npu = hardware.get_hw()["npus"][0]

        assert npu["firmware_version"] == "1.2.3"
        assert npu["device_type"] == "DX-M1"
        assert npu["board_type"] == "EVB"
        assert npu["memory_type"] == "LPDDR5"
        assert npu["ddr_status"] == [0, 0, 0, 0]
    finally:
        (
            hardware._DS,
            hardware._dx_ok,
            hardware._NPU_STATS_BIN,
            hardware._APP_ROOT,
            hardware._hw_cache,
        ) = original_state


def test_get_sysinfo_reads_runtime_release_versions_from_suite_root(tmp_path):
    """F-16: dx_rt/dx_app versions must resolve to <SUITE_ROOT>/dx-runtime/{dx_rt,dx_app}/release.ver,
    not to the studio's own dx_app dir (which has no release.ver -> always N/A)."""
    import hardware

    # Canonical layout: <suite>/dx-ai-studio/dx_app is the app_root the monitor passes.
    app_root = tmp_path / "dx-ai-studio" / "dx_app"
    app_root.mkdir(parents=True)
    rt = tmp_path / "dx-runtime"
    (rt / "dx_rt").mkdir(parents=True)
    (rt / "dx_app").mkdir(parents=True)
    (rt / "dx_rt" / "release.ver").write_text("v9.9.9\n", encoding="utf-8")
    (rt / "dx_app" / "release.ver").write_text("v8.8.8\n", encoding="utf-8")

    original = (hardware._DS, hardware._dx_ok, hardware._APP_ROOT)
    try:
        hardware.init_hw(ds=None, dx_ok=False, app_root=app_root)
        info = hardware.get_sysinfo()
        assert info["dx_rt_version"] == "v9.9.9"
        assert info["dx_app_version"] == "v8.8.8"
    finally:
        hardware._DS, hardware._dx_ok, hardware._APP_ROOT = original

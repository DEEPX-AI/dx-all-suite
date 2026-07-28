import inspect
import sys
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

"""Tests for env_fingerprint host power / PCIe health capture (G5)."""

import benchmark.env_fingerprint as ef
from benchmark.env_fingerprint import (
    _decode_throttled,
    _parse_pmic_volts,
    collect_host_health,
)


def test_decode_throttled_clean():
    flags = _decode_throttled("throttled=0x0")
    assert flags is not None
    assert set(flags) == {
        "under_voltage_now", "freq_capped_now", "throttled_now", "soft_temp_limit_now",
        "under_voltage_occurred", "freq_capped_occurred", "throttled_occurred",
        "soft_temp_limit_occurred",
    }
    assert not any(flags.values())


def test_decode_throttled_past_events():
    # 0x50005 = under-voltage now + throttled now + both "occurred" bits
    flags = _decode_throttled("throttled=0x50005")
    assert flags["under_voltage_now"] is True
    assert flags["throttled_now"] is True
    assert flags["under_voltage_occurred"] is True
    assert flags["throttled_occurred"] is True
    assert flags["freq_capped_now"] is False
    assert flags["soft_temp_limit_occurred"] is False


def test_decode_throttled_garbage():
    assert _decode_throttled("vcgencmd: command not found") is None
    assert _decode_throttled("") is None


def test_parse_pmic_volts():
    raw = "VDD_CORE_V volt(16)=0.72000000V\nEXT5V_V volt(24)=5.10370000V\n"
    v = _parse_pmic_volts(raw)
    assert v is not None
    assert abs(v - 5.1037) < 1e-6


def test_parse_pmic_volts_missing():
    assert _parse_pmic_volts("") is None
    assert _parse_pmic_volts("no adc channels here") is None


def test_collect_host_health_no_tools(monkeypatch):
    """Non-RPi host without vcgencmd/lspci: degrades gracefully, never raises."""
    monkeypatch.setattr(ef.shutil, "which", lambda name: None)
    h = collect_host_health()
    assert h["available"] is False
    assert h["throttled"] is None
    assert h["throttled_flags"] is None
    assert h["pmic_ext5v_v"] is None
    assert h["pcie_links"] == []


def test_collect_host_health_rpi_like(monkeypatch):
    """Simulated RPi: vcgencmd present, values parsed into structured fields."""
    monkeypatch.setattr(ef.shutil, "which",
                        lambda name: "/usr/bin/" + name if name == "vcgencmd" else None)

    def fake_run(cmd, default="unknown"):
        if cmd[:2] == ["vcgencmd", "get_throttled"]:
            return "throttled=0x50000"
        if cmd[:2] == ["vcgencmd", "pmic_read_adc"]:
            return "EXT5V_V volt(24)=4.79000000V"
        return default

    monkeypatch.setattr(ef, "_run", fake_run)
    h = collect_host_health()
    assert h["available"] is True
    assert h["throttled"] == "throttled=0x50000"
    assert h["throttled_flags"]["under_voltage_occurred"] is True
    assert h["throttled_flags"]["under_voltage_now"] is False
    assert abs(h["pmic_ext5v_v"] - 4.79) < 1e-6
    assert h["pcie_links"] == []

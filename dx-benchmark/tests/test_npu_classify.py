from benchmark.npu_catalog import (
    classify_device, classify_devices, classify_from_raw, format_sku, format_badge,
)

RAW_H1 = """
 * Device 0: M1, Accelerator type
 * Memory : LPDDR5x 6000 Mbps, 3.92GiB
 * Board  : H1, Rev 0.0
 * Device 1: M1, Accelerator type
 * Memory : LPDDR5x 6000 Mbps, 3.92GiB
 * Board  : H1, Rev 0.0
 * Device 2: M1, Accelerator type
 * Memory : LPDDR5x 6000 Mbps, 3.92GiB
 * Board  : H1, Rev 0.0
 * Device 3: M1, Accelerator type
 * Memory : LPDDR5x 6000 Mbps, 3.92GiB
 * Board  : H1, Rev 0.0
"""

RAW_M1M = """
 * Device 0: M1, Accelerator type
 * Memory : LPDDR4 4200 Mbps, 1.92GiB
 * Board  : M.2, Rev 0.0
"""


def test_classify_device_m1_vs_m1m():
    assert classify_device("M.2, Rev 1.0", "LPDDR5 5600 Mbps, 3.92GiB") == ("M1", 1)
    assert classify_device("M.2, Rev 0.0", "LPDDR4 4200 Mbps, 1.92GiB") == ("M1M", 1)


def test_classify_device_h1_chip():
    assert classify_device("H1, Rev 0.0", "LPDDR5x 6000 Mbps, 3.92GiB") == ("H1-Quattro", 4)


def test_classify_device_m2_with_lpddr5x_is_still_an_m1():
    """An M1 M.2 card shipped with LPDDR5x 6000 (dxrt-cli: "Device 0: M1", Board M.2 Rev 1.0).
    The memory type alone must not turn it into an H1 -- that named a real M1 Raspberry Pi
    result folder "<host>_H1"."""
    assert classify_device("M.2, Rev 1.0", "LPDDR5x 6000 Mbps, 3.92GiB") == ("M1", 1)
    assert classify_device("M.2, Rev 1.0", "LPDDR5x 6000 Mbps, 3.92GiB", "M1") == ("M1", 1)


def test_classify_device_uses_the_reported_chip_when_it_names_an_h1_m2():
    assert classify_device("M.2, Rev 1.0", "LPDDR5x 6000 Mbps, 3.92GiB", "H1") == ("H1", 1)
    assert classify_device("M.2, Rev 0.0", "LPDDR4 4200 Mbps, 1.92GiB", "M1M") == ("M1M", 1)


def test_classify_devices_accepts_signals_with_or_without_the_chip():
    mixed = [("M.2, Rev 1.0", "LPDDR5 5600 Mbps"), ("M.2, Rev 1.0", "LPDDR5 5600 Mbps", "M1")]
    assert classify_devices(mixed) == [{"product": "M1", "count": 2}]


RAW_M1_LPDDR5X = """DXRT v3.5.0 (build: 4.d2bed77)
=======================================================
 * Device 0: M1, Accelerator type
---------------------   Version   ---------------------
 * RT Driver version   : v2.7.0
 * PCIe Driver version : v2.7.0
-------------------------------------------------------
 * FW version          : v2.7.6 (build: 5.974f823)
--------------------- Device Info ---------------------
 * Memory : LPDDR5x 6000 Mbps, 3.92GiB
 * Board  : M.2, Rev 1.0
 * Chip Offset : 0
 * PCIe   : Gen3 X1 [01:00:00]
NPU 0: voltage 0 mV, clock 1000 MHz, temperature 42'C
NPU 1: voltage 0 mV, clock 1000 MHz, temperature 42'C
NPU 2: voltage 0 mV, clock 1000 MHz, temperature 41'C
=======================================================
"""


def test_classify_from_raw_m1_with_lpddr5x_memory():
    assert classify_from_raw(RAW_M1_LPDDR5X) == [{"product": "M1", "count": 1}]


def test_m1_raspberry_pi_with_lpddr5x_gets_an_m1_folder(monkeypatch):
    """The reported bug end to end: fingerprint -> result folder name."""
    from benchmark import env_fingerprint as ef
    from benchmark.result_layout import make_hw_id
    monkeypatch.setattr(ef.shutil, "which", lambda name: "/usr/bin/dxrt-cli")
    monkeypatch.setattr(ef, "_run", lambda cmd, default="unknown":
                        RAW_M1_LPDDR5X if cmd == ["dxrt-cli", "-s"] else default)
    info = ef._get_npu_info()
    assert info["sku"] == "M1" and info["modules"] == [{"product": "M1", "count": 1}]
    fp = {"host": {"hostname": "do-rt-raspberry-06"}, "npu": info}
    assert make_hw_id(fp) == "do-rt-raspberry-06_M1"


def test_classify_device_unknown():
    assert classify_device(None, None) == ("unknown", 1)


def test_classify_devices_h1_quattro_from_four_chips():
    devs = [("H1, Rev 0.0", "LPDDR5x 6000")] * 4
    assert classify_devices(devs) == [{"product": "H1-Quattro", "count": 1}]


def test_classify_devices_two_m1():
    devs = [("M.2, Rev 1.0", "LPDDR5 5600")] * 2
    assert classify_devices(devs) == [{"product": "M1", "count": 2}]


def test_format_sku_and_badge():
    assert format_sku([{"product": "M1", "count": 1}]) == "M1"
    assert format_sku([{"product": "M1", "count": 2}]) == "M1x2"
    assert format_sku([{"product": "H1-Quattro", "count": 1}]) == "H1-Quattro"
    assert format_badge([{"product": "M1", "count": 2}]) == "M1 ×2"


def test_classify_from_raw_h1_and_m1m():
    assert classify_from_raw(RAW_H1) == [{"product": "H1-Quattro", "count": 1}]
    assert classify_from_raw(RAW_M1M) == [{"product": "M1M", "count": 1}]


from benchmark.env_fingerprint import _stamp_npu_products


def test_stamp_npu_products_m1m():
    npu = {"raw": RAW_M1M, "device_count": 1}
    _stamp_npu_products(npu, [("M.2, Rev 0.0", "LPDDR4 4200 Mbps, 1.92GiB")])
    assert npu["sku"] == "M1M"
    assert npu["product"] == "M1M"
    assert npu["modules"] == [{"product": "M1M", "count": 1}]


def test_get_npu_info_multi_device_end_to_end(monkeypatch):
    from benchmark import env_fingerprint as ef
    monkeypatch.setattr(ef.shutil, "which", lambda name: "/usr/bin/dxrt-cli")
    monkeypatch.setattr(ef, "_run",
                        lambda cmd, default="unknown": RAW_H1 if cmd == ["dxrt-cli", "-s"] else default)
    info = ef._get_npu_info()
    assert info["device_count"] == 4
    assert info["modules"] == [{"product": "H1-Quattro", "count": 1}]
    assert info["sku"] == "H1-Quattro"
    assert info["product"] == "H1-Quattro"

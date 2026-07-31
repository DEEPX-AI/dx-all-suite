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


def test_classify_device_m2_lpddr5x_matches_before_lpddr5():
    # LPDDR5X on an M.2 board must resolve before the LPDDR5 substring rule.
    assert classify_device("M.2, Rev 1.0", "LPDDR5x 6000 Mbps, 3.92GiB") == ("H1", 1)


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

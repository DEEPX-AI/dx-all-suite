from benchmark.result_layout import make_hw_id


def test_make_hw_id_uses_stamped_sku_m1m():
    fp = {"product_name": "RPi5B",
          "npu": {"modules": [{"product": "M1M", "count": 1}], "sku": "M1M"}}
    assert make_hw_id(fp) == "RPi5B_M1M"


def test_make_hw_id_backfills_from_raw_h1():
    raw = ("\n".join([" * Device %d: M1, Accelerator type\n"
                      " * Memory : LPDDR5x 6000 Mbps, 3.92GiB\n"
                      " * Board  : H1, Rev 0.0" % i for i in range(4)]))
    fp = {"product_name": "BIOSTAR", "npu": {"raw": raw}}
    assert make_hw_id(fp) == "BIOSTAR_H1-Quattro"


def test_make_hw_id_uses_sku_when_present():
    fp = {"product_name": "acme",
          "npu": {"modules": [{"product": "M1", "count": 2}], "sku": "M1x2"}}
    assert make_hw_id(fp) == "acme_M1x2"


def test_make_hw_id_recomputes_from_modules_when_sku_unknown():
    # sku is "unknown" -> must fall through to modules recompute.
    fp = {"product_name": "acme",
          "npu": {"sku": "unknown", "modules": [{"product": "M1", "count": 2}]}}
    assert make_hw_id(fp) == "acme_M1x2"


def test_make_hw_id_falls_back_to_device_count():
    # No sku, no modules, no raw -> last-resort device_count heuristic.
    fp = {"product_name": "acme", "npu": {"device_count": 2}}
    assert make_hw_id(fp) == "acme_M1x2"

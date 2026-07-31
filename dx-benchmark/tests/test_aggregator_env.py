import json
from pathlib import Path

from benchmark.aggregator import aggregate_result_directories, _build_environment_summary

RAW_M1 = (" * Device 0: M1, Accelerator type\n"
          " * Memory : LPDDR5 5600 Mbps, 3.92GiB\n"
          " * Board  : M.2, Rev 1.0\n")
RAW_M1M = (" * Device 0: M1, Accelerator type\n"
           " * Memory : LPDDR4 4200 Mbps, 1.92GiB\n"
           " * Board  : M.2, Rev 0.0\n")


def _write_run(root: Path, folder: str, run_id: str, product, raw):
    d = root / folder / run_id
    d.mkdir(parents=True)
    fp = {"host": {"hostname": "raspberrypi"},
          "npu": {"raw": raw, "device_count": 1},
          "software": {}, "timestamp": run_id, "product_name": product}
    (d / "environment.json").write_text(json.dumps(fp))
    (d / "model_results.json").write_text("[]")


def test_distinct_folders_do_not_collide(tmp_path):
    # Two physically distinct boards + one run missing product_name.
    _write_run(tmp_path, "RPi5B_M1",  "20260707_1", "RPi5B", RAW_M1)
    _write_run(tmp_path, "RPi5B_M1M", "20260701_1", "RPi5B", RAW_M1M)
    _write_run(tmp_path, "RPi5B_M1M", "20260702_1", None,    RAW_M1M)  # no product_name

    ds = aggregate_result_directories(tmp_path)
    env_ids = sorted(e["env_id"] for e in ds["environments"])
    # env identity is the folder name — exactly two, no phantom 'raspberrypi_M1'.
    assert env_ids == ["RPi5B_M1", "RPi5B_M1M"]
    assert ds["meta"]["environment_count"] == 2


def test_env_summary_exposes_npu_product(tmp_path):
    _write_run(tmp_path, "RPi5B_M1M", "20260701_1", "RPi5B", RAW_M1M)
    ds = aggregate_result_directories(tmp_path)
    env = ds["environments"][0]
    assert env["npu_product"] == "M1M"
    assert env["npu_sku"] == "M1M"


def test_build_environment_summary_backfills_product():
    fp = {"host": {}, "npu": {"raw": RAW_M1M}, "software": {}}
    env = _build_environment_summary("RPi5B_M1M", "run1", fp)
    assert env["npu_product"] == "M1M"


def test_guard_warns_on_mixed_real_products(tmp_path):
    # Same folder, two runs classifying to DIFFERENT real products -> warn.
    _write_run(tmp_path, "MixedFolder", "run1", "X", RAW_M1)
    _write_run(tmp_path, "MixedFolder", "run2", "X", RAW_M1M)
    ds = aggregate_result_directories(tmp_path)
    assert ds["meta"]["warnings"]
    assert "MixedFolder" in ds["meta"]["warnings"][0]


def test_guard_ignores_unknown_only_run(tmp_path):
    # One good run + one run missing raw/modules (dxrt-cli absent) -> must NOT warn.
    _write_run(tmp_path, "FolderX", "run1", "X", RAW_M1)
    d = tmp_path / "FolderX" / "run2"
    d.mkdir(parents=True)
    fp = {"host": {}, "npu": {"device_count": 1}, "software": {},
          "timestamp": "run2", "product_name": "X"}
    (d / "environment.json").write_text(json.dumps(fp))
    (d / "model_results.json").write_text("[]")
    ds = aggregate_result_directories(tmp_path)
    assert ds["meta"]["warnings"] == []


def test_runs_carry_suite_version(tmp_path):
    _write_run(tmp_path, "RPi5B_M1", "20260707_1", "RPi5B", RAW_M1)
    ds = aggregate_result_directories(tmp_path)
    assert ds["runs"], "expected at least one run"
    assert all("dx_all_suite_version" in r for r in ds["runs"])


def test_guard_warns_on_mixed_hostnames(tmp_path):
    # Same folder, two runs from different hostnames -> warn.
    _write_run(tmp_path, "FolderH", "run1", "X", RAW_M1)
    d = tmp_path / "FolderH" / "run2"
    d.mkdir(parents=True)
    fp = {"host": {"hostname": "other-host"}, "npu": {"raw": RAW_M1, "device_count": 1},
          "software": {}, "timestamp": "run2", "product_name": "X"}
    (d / "environment.json").write_text(json.dumps(fp))
    (d / "model_results.json").write_text("[]")
    ds = aggregate_result_directories(tmp_path)
    assert any("different hostnames" in w for w in ds["meta"]["warnings"])

"""Product classification checked against real `dxrt-cli -s` output from the benchmark fleet.

The signals are Board (form factor), the chip named on the "Device N:" line and the memory
the card ships with. Memory is a description of the card, not its identity: the M1 M.2 card
exists with LPDDR5 5600 and with LPDDR5x 6000, and an M1 Raspberry Pi was once named
"<host>_H1" because LPDDR5x was taken to mean H1.
"""
import json

import pytest

from benchmark import env_fingerprint as ef
from benchmark.aggregator import _resolve_modules, aggregate_result_directories
from benchmark.npu_catalog import classify_from_raw, format_sku, parse_devices
from benchmark.reporter import _add_environment_section  # noqa: F401  (name check)


def _device(n, chip, memory, board, offset=0, pcie="Gen3 X1 [01:00:00]"):
    return f""" * Device {n}: {chip}, Accelerator type
---------------------   Version   ---------------------
 * RT Driver version   : v2.7.0
 * PCIe Driver version : v2.7.0
-------------------------------------------------------
 * FW version          : v2.7.6 (build: 4.90f4a6f)
--------------------- Device Info ---------------------
 * Memory : {memory}
 * Board  : {board}
 * Chip Offset : {offset}
 * PCIe   : {pcie}
NPU 0: voltage 0 mV, clock 1000 MHz, temperature 42'C
NPU 1: voltage 0 mV, clock 1000 MHz, temperature 42'C
NPU 2: voltage 0 mV, clock 1000 MHz, temperature 41'C
=======================================================
"""


def _raw(*devices):
    return "DXRT v3.5.0 (build: 4.d2bed77)\n=======================================================\n" + "".join(devices)


# (label, raw, expected sku) -- the first six are the actual fleet hosts.
FLEET = [
    ("BIOSTAR172 H1 Quattro", _raw(*[_device(i, "M1", "LPDDR5x 6000 Mbps, 3.92GiB", "H1, Rev 0.0", i,
                                           f"Gen3 X4 [0{i+1}:00:00]") for i in range(4)]), "H1-Quattro"),
    ("aibox251 M1 (N97)", _raw(_device(0, "M1", "LPDDR5 5600 Mbps, 3.92GiB", "M.2, Rev 1.0",
                                      pcie="Gen3 X2 [03:00:00]")), "M1"),
    ("rpi24 M1M", _raw(_device(0, "M1M", "LPDDR4 4200 Mbps, 1.92GiB", "M.2, Rev 0.0")), "M1M"),
    ("rpi135 M1", _raw(_device(0, "M1", "LPDDR5 5600 Mbps, 3.92GiB", "M.2, Rev 1.0")), "M1"),
    ("orange127 M1", _raw(_device(0, "M1", "LPDDR5 5600 Mbps, 3.92GiB", "M.2, Rev 1.0",
                                 pcie="Gen3 X4 [01:00:00]")), "M1"),
    ("rock246 M1", _raw(_device(0, "M1", "LPDDR5 5600 Mbps, 3.92GiB", "M.2, Rev 1.0",
                               pcie="Gen3 X2 [01:00:00]")), "M1"),
    # The reported bug: an M1 M.2 Rev 1.0 card with LPDDR5x memory (Raspberry Pi, FW 5.974f823).
    ("do-rt-raspberry-06 M1 LPDDR5x", _raw(_device(0, "M1", "LPDDR5x 6000 Mbps, 3.92GiB",
                                                   "M.2, Rev 1.0")), "M1"),
    # Older runtimes named the chip "M1" on an M1M card too; memory is the only tell there.
    ("older runtime M1M", _raw(_device(0, "M1", "LPDDR4 4200 Mbps, 1.92GiB", "M.2, Rev 0.0")), "M1M"),
    ("two M1 cards", _raw(_device(0, "M1", "LPDDR5 5600 Mbps, 3.92GiB", "M.2, Rev 1.0"),
                         _device(1, "M1", "LPDDR5 5600 Mbps, 3.92GiB", "M.2, Rev 1.0", 0)), "M1x2"),
    ("M1 + M1M mixed", _raw(_device(0, "M1", "LPDDR5 5600 Mbps, 3.92GiB", "M.2, Rev 1.0"),
                           _device(1, "M1M", "LPDDR4 4200 Mbps, 1.92GiB", "M.2, Rev 0.0")), "M1-M1M"),
    # Not a product we know: the chip is the best identity, never a bare "unknown".
    ("future H1 M.2", _raw(_device(0, "H1", "LPDDR5x 6000 Mbps, 3.92GiB", "M.2, Rev 1.0")), "H1"),
    ("unfamiliar board, known chip", _raw(_device(0, "M1", "LPDDR5 5600 Mbps", "PCIe, Rev 2.0")), "M1"),
]


@pytest.mark.parametrize("label,raw,sku", FLEET, ids=[f[0] for f in FLEET])
def test_fleet_output_is_classified_correctly(label, raw, sku):
    assert format_sku(classify_from_raw(raw)) == sku


@pytest.mark.parametrize("label,raw,sku", FLEET, ids=[f[0] for f in FLEET])
def test_fingerprint_and_result_folder_agree_with_the_catalog(monkeypatch, label, raw, sku):
    from benchmark.result_layout import make_hw_id
    monkeypatch.setattr(ef.shutil, "which", lambda name: "/usr/bin/dxrt-cli")
    monkeypatch.setattr(ef, "_run", lambda cmd, default="unknown": raw if cmd == ["dxrt-cli", "-s"] else default)
    info = ef._get_npu_info()
    assert info["sku"] == sku
    assert make_hw_id({"host": {"hostname": "host"}, "npu": info}) == f"host_{sku}"


def test_no_device_is_unknown_not_a_guess():
    assert classify_from_raw("DXRT v3.5.0\n(no devices)\n") == []
    assert format_sku([]) == "unknown"


# ── per-device record ─────────────────────────────────────────────────────

def test_parse_devices_returns_every_signal_of_every_device():
    devices = parse_devices(FLEET[0][1])
    assert [d["chip_offset"] for d in devices] == [0, 1, 2, 3]
    assert all(d["chip"] == "M1" and d["board"].startswith("H1") for d in devices)
    assert devices[0]["memory"].startswith("LPDDR5x 6000 Mbps")
    assert devices[3]["pcie"].startswith("Gen3 X4")


def test_fingerprint_records_each_devices_chip_board_and_memory(monkeypatch):
    raw = FLEET[6][1]
    monkeypatch.setattr(ef.shutil, "which", lambda name: "/usr/bin/dxrt-cli")
    monkeypatch.setattr(ef, "_run", lambda cmd, default="unknown": raw if cmd == ["dxrt-cli", "-s"] else default)
    info = ef._get_npu_info()
    assert info["devices"] == [{"chip": "M1", "board": "M.2, Rev 1.0",
                                "memory": "LPDDR5x 6000 Mbps, 3.92GiB",
                                "chip_offset": 0, "pcie": "Gen3 X1 [01:00:00]"}]


# ── aggregation of results classified by an older catalog ─────────────────

def test_aggregator_reclassifies_from_raw_instead_of_trusting_a_stale_stamp():
    stale = {"modules": [{"product": "H1", "count": 1}], "raw": FLEET[6][1]}
    assert _resolve_modules(stale) == [{"product": "M1", "count": 1}]


def test_aggregator_falls_back_to_the_stamp_when_there_is_no_raw():
    assert _resolve_modules({"modules": [{"product": "M1M", "count": 1}]}) == \
        [{"product": "M1M", "count": 1}]


def _write_run(root, folder, raw, stamped_sku):
    run = root / folder / "20261022_000000"
    run.mkdir(parents=True)
    fp = {"host": {"hostname": "h"}, "timestamp": "2026-10-22T00:00:00", "protocol": {},
          "npu": {"raw": raw, "sku": stamped_sku,
                  "modules": [{"product": stamped_sku, "count": 1}]}}
    (run / "environment.json").write_text(json.dumps(fp))
    return run


def test_aggregate_flags_a_folder_whose_name_disagrees_with_its_hardware(tmp_path):
    _write_run(tmp_path, "do-rt-raspberry-06_H1", FLEET[6][1], "H1")
    warnings = aggregate_result_directories(tmp_path)["meta"]["warnings"]
    assert any("do-rt-raspberry-06_H1" in w and "_M1" in w for w in warnings)


def test_aggregate_is_quiet_when_the_folder_name_matches(tmp_path):
    _write_run(tmp_path, "RPi5B_M1", FLEET[3][1], "M1")
    assert aggregate_result_directories(tmp_path)["meta"]["warnings"] == []


def test_report_environment_names_the_chip_and_board(monkeypatch):
    from benchmark.reporter import _add_environment_section
    lines = []
    monkeypatch.setattr(ef.shutil, "which", lambda name: "/usr/bin/dxrt-cli")
    monkeypatch.setattr(ef, "_run", lambda cmd, default="unknown": FLEET[6][1] if cmd == ["dxrt-cli", "-s"] else default)
    info = ef._get_npu_info()
    _add_environment_section(lines, {"host": {}, "npu": info})
    out = "\n".join(lines)
    assert "| NPU Chip / Board | M1 · M.2, Rev 1.0 |" in out

"""npu.json DRAM for DX-M1 / DX-M1M / DX-H1 Quattro = what `dxrt-cli -s` measured on those boards.

The measured strings live in dx_benchmark/results/<platform>/<run>/environment.json (npu.memory, or one per chip
under npu.devices for multi-chip cards). They used to be 1024 MB / 33.6 GB/s for both M1 and M1M.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

STUDIO = Path(__file__).resolve().parents[2]
NPU = {e["id"]: e for e in json.loads((STUDIO / "dx_planner/data/npu.json").read_text(encoding="utf-8"))}
_MEM = re.compile(r"^(LPDDR\w+) (\d+) Mbps, ([\d.]+)GiB$")


def _measured(platform):
    """(dram type with speed, MiB per chip, chips, Mbps) — every run must report the same memory; the chip count comes
    from runs that list npu.devices (older environment.json files carry only the single npu.memory string)."""
    seen, chips = set(), 1
    for env in sorted((STUDIO / "dx_benchmark/results" / platform).glob("*/environment.json")):
        npu = json.loads(env.read_text(encoding="utf-8"))["npu"]
        mems = [d["memory"] for d in npu.get("devices") or []] or [npu["memory"]]
        chips = max(chips, len(mems))
        for mem in mems:
            m = _MEM.match(mem)
            assert m, mem
            seen.add((f"{m.group(1)} {m.group(2)} Mbps", round(float(m.group(3)) * 1024), int(m.group(2))))
    assert len(seen) == 1, (platform, seen)
    dram_type, mib, mbps = seen.pop()
    return dram_type, mib, chips, mbps


@pytest.mark.parametrize("npu_id,platform", [("dx-m1", "RPi5B_M1"), ("dx-m1m", "RPi5B_M1M"),
                                             ("dx-h1-quattro", "BIOSTAR_H1-Quattro")])
def test_dram_matches_dxrt_cli(npu_id, platform):
    dram_type, mib, chips, mbps = _measured(platform)
    e = NPU[npu_id]
    assert e["dram_type"] == dram_type
    assert e["dram_mb"] == mib * chips
    # bandwidth per chip = data rate × 64-bit bus ÷ 8 (M1M's long-standing 33.6 = 4200 × 64 / 8)
    assert e["dram_bandwidth_gbps"] == pytest.approx(mbps * 64 / 8 / 1000)
    assert e["_dram_source"].startswith("dxrt-cli -s")


def test_m1_and_m1m_are_no_longer_the_same():
    assert NPU["dx-m1"]["dram_mb"] != NPU["dx-m1m"]["dram_mb"]
    assert NPU["dx-m1"]["dram_bandwidth_gbps"] != NPU["dx-m1m"]["dram_bandwidth_gbps"]


def test_edgeguide_shows_the_measured_dram():
    from dx_planner.core.aggregator import _format_dram
    assert _format_dram(NPU["dx-m1"]) == "3.9GB LPDDR5 5600 Mbps"
    assert _format_dram(NPU["dx-m1m"]) == "1.9GB LPDDR4 4200 Mbps"
    assert _format_dram(NPU["dx-h1-quattro"]) == "15.7GB LPDDR5x 6000 Mbps"


def test_generated_planner_data_is_current():
    data = json.loads((STUDIO / "dx_planner/static/data/benchmarks.json").read_text(encoding="utf-8"))
    dram = {p["id"]: p["npu"]["dram"] for p in data["platforms"]}
    assert dram["rpi5b-m1"] == "3.9GB LPDDR5 5600 Mbps"
    assert dram["rpi5b-m1m"] == "1.9GB LPDDR4 4200 Mbps"
    assert dram["biostar-h1-quattro"] == "15.7GB LPDDR5x 6000 Mbps"

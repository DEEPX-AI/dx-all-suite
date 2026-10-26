"""REPORT.md must carry the provenance / environment facts needed to reproduce a run."""
import json
from pathlib import Path

import pytest

from benchmark.reporter import (
    _add_environment_section,
    _add_model_info_section,
    _add_pipeline_section,
    generate_markdown_report,
)

RESULTS = Path(__file__).resolve().parents[1] / "results"

_PCIE_RAW_4 = "\n".join(f" * PCIe   : Gen3 X4 [0{i}:00:00]" for i in range(1, 5))


def _model(**kw):
    base = {"name": "yolo26-n_640x640.dxnn", "task": "object_detection", "size": "n",
            "format_version": "v9", "dxcom_version": "v2.5.0-rc.1+c6ae2e3",
            "sha256": "ab" * 32}
    base.update(kw)
    return base


def _fp(**kw):
    fp = {
        "host": {"hostname": "h", "os": "Ubuntu", "kernel": "6.8", "cpu": "AMD Ryzen 5",
                 "cpu_count": 12, "ram_gb": 30.5, "cpu_governors": {"powersave": 12}},
        "npu": {"sku": "H1-Quattro", "device_count": 4, "rt_version": "v3.5.0",
                "memory": "LPDDR5x 6000 Mbps, 3.92GiB", "pcie": "Gen3 X4 [04:00:00]",
                "raw": _PCIE_RAW_4},
        "software": {"dx_stream": "3.2.0"},
        "tools": {},
        "tool_commit": "abc1234-dirty",
        "benchmarked_models": [_model()],
        "model_source": "https://example.com/models/2_5_0",
    }
    fp.update(kw)
    return fp


def _env(fp):
    lines = []
    _add_environment_section(lines, fp)
    return "\n".join(lines)


def test_models_table_carries_dxcom_format_sha_and_source():
    lines = []
    _add_model_info_section(lines, _fp(), [])
    out = "\n".join(lines)
    assert "| Format | DX-COM | SHA256 |" in out
    assert "v2.5.0-rc.1+c6ae2e3" in out and "abababababab" in out
    assert "Model source: https://example.com/models/2_5_0" in out


def test_env_multi_device_host():
    out = _env(_fp())
    assert "| NPU Devices | 4 (H1-Quattro) |" in out
    assert "| NPU Memory (per device) |" in out
    assert "| NPU PCIe | Gen3 X4 ×4 |" in out
    assert "| CPU Governor | powersave |" in out
    assert "| DX-Stream | 3.2.0 |" in out
    assert "| Tool commit | abc1234-dirty |" in out


def test_env_single_device_host_degrades_gracefully():
    fp = _fp()
    fp["npu"].update(sku="M1M", device_count=1, raw=" * PCIe   : Gen3 X1 [01:00:00]",
                     pcie="Gen3 X1 [01:00:00]")
    fp["host"].update(cpu="-", cpu_governors={"ondemand": 2, "performance": 2})
    assert "Host Health" not in _env(fp)
    fp["host_health"] = {"throttled": "throttled=0x0", "pmic_ext5v_v": 5.18714}
    out = _env(fp)
    assert "| NPU Devices | 1 (M1M) |" in out and "per device" not in out
    assert "| NPU PCIe | Gen3 X1 [01:00:00] |" in out
    assert "| CPU | N/A |" in out
    assert "| CPU Governor | ondemand ×2, performance ×2 |" in out
    assert "| Host Health | throttled=0x0, EXT5V 5.19 V |" in out


def _pipe(model, task, size, ort):
    return {"model": model, "task": task, "size": size, "use_ort": ort,
            "avg_e2e_fps": 400.0, "frame_count": 10, "runs": 3, "requested_runs": 3,
            "status": "ok", "decoder": "vaapidecodebin"}


def test_ort_comparison_only_where_a_cpu_part_exists():
    """Classification has no CPU part: ON/OFF is the same model, so a comparison table
    would present measurement noise as an effect."""
    cls = [_pipe(f"yolo26-cls-{s}_224x224.dxnn", "classification", s, o)
           for s in "nsmlx" for o in (True, False)]
    det = [_pipe("yolo26-n_640x640.dxnn", "object_detection", "n", o) for o in (True, False)]
    lines = []
    _add_pipeline_section(lines, cls)
    assert "ORT Comparison" not in "\n".join(lines) and "no CPU part" in "\n".join(lines)
    lines = []
    _add_pipeline_section(lines, det)
    assert "ORT Comparison" in "\n".join(lines)


# One representative per NPU class: H1-Quattro (4 devices), M1 (1 device, SW/HW decode
# variants), M1M (LPDDR4, host_health). The latest tracked run of each is enough.
_SKU_HOSTS = ["BIOSTAR_H1-Quattro", "DX-AIPlayer-N97_M1", "RPi5B_M1M"]


def _latest_run(host):
    runs = sorted(p.parent for p in (RESULTS / host).glob("*/model_results.json"))
    return runs[-1] if runs else None


@pytest.mark.parametrize("host", _SKU_HOSTS)
def test_report_generates_from_tracked_results(host, tmp_path):
    run_dir = _latest_run(host)
    if run_dir is None:
        pytest.skip(f"no tracked results for {host}")
    load = lambda n: json.loads((run_dir / n).read_text())
    fp = load("environment.json")
    out_path = tmp_path / "REPORT.md"
    generate_markdown_report(fp, load("model_results.json"), load("pipeline_results.json"),
                             load("multi_stream_results.json"), out_path,
                             video_infos=fp.get("video_infos"))
    out = out_path.read_text()
    for needle in ("## Glossary", "NPU Devices", "| Format | DX-COM | SHA256 |"):
        assert needle in out, needle
    assert ("per device" in out) == (fp["npu"].get("device_count", 1) > 1)

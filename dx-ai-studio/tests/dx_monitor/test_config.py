"""Unit tests for dx_monitor core/config.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_monitor"))


def test_constants_defined():
    """The core constants must be defined."""
    from core.config import DEFAULT_PORT, STATIC_DIR, TEMPLATES_DIR, SERVER_NAME
    assert DEFAULT_PORT == 8098
    assert SERVER_NAME == "DX Monitor"
    assert STATIC_DIR.is_dir()
    assert TEMPLATES_DIR.is_dir()


def test_paths_exist():
    """SCRIPT_DIR and STUDIO_DIR must exist on disk."""
    from core.config import SCRIPT_DIR, STUDIO_DIR
    assert SCRIPT_DIR.is_dir()
    assert STUDIO_DIR.is_dir()
    assert SCRIPT_DIR.name == "dx_monitor"


def test_thresholds_defined():
    """The THRESHOLDS dict must have the expected structure."""
    from core.config import THRESHOLDS
    assert isinstance(THRESHOLDS, dict)
    for key in ("npu_temp", "core_temp", "npu_dram", "memory", "cpu_load"):
        assert key in THRESHOLDS, f"THRESHOLDS에 '{key}' 키 누락"
    for key in ("npu_temp", "core_temp", "npu_dram", "memory"):
        t = THRESHOLDS[key]
        assert "warn" in t and "crit" in t and "unit" in t
        assert t["warn"] < t["crit"], f"{key}: warn({t['warn']}) >= crit({t['crit']})"
    cpu = THRESHOLDS["cpu_load"]
    assert "warn_factor" in cpu and "crit_factor" in cpu
    assert cpu["warn_factor"] < cpu["crit_factor"]

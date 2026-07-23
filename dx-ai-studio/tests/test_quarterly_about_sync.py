"""Tests for scripts/quarterly_about_sync.py (offline, no network)."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/quarterly_about_sync.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("quarterly_about_sync", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_extract_model_zoo_from_fixture():
    mod = _load_module()
    html = """
    Total Models Available: 271
    SDK Version: dx-com v2.3.0, dx-rt v3.3.0
    Generated on 2026-04-21 07:06:17
    """
    out = mod.extract_model_zoo(html)
    assert out["count"] == "271"
    assert out["asOf"] == "2026-04-21"
    assert out["dxCom"] == "v2.3.0"
    assert out["dxRt"] == "v3.3.0"


def test_extract_sdk_release_from_fixture():
    mod = _load_module()
    html = """
    <h2>DX-All-Suite v2.3.0 Release Update</h2>
    <p>This major release focuses on Runtime Efficiency, Security Hardening.</p>
    """
    out = mod.extract_sdk_release(html)
    assert out["version"] == "v2.3.0"


def test_offline_mode_exits_zero():
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--offline"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert result.returncode == 0
    assert "offline" in result.stdout

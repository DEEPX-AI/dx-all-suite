"""NPU Driver version = the dxrt_driver kernel module's version, never the DX-RT (dxrt-cli) version.

`dxrt-cli --version` prints "DXRT v3.5.0 (build: …)" — that is the runtime. The Setup cards showed it under
"NPU Driver" (DX App Version Info, DX Stream Setup) while the driver was v2.7.0.
"""
from __future__ import annotations

import subprocess

import pytest

from shared import dxrt


@pytest.fixture
def no_cli(monkeypatch):
    """Any dxrt-cli call is a bug here; modinfo answers only when a test says so."""
    calls = []

    def run(argv, *a, **k):
        calls.append(argv)
        if argv[0] == "dxrt-cli":
            raise AssertionError("driver version must not come from dxrt-cli")
        return subprocess.CompletedProcess(argv, 1, "", "")

    monkeypatch.setattr(dxrt.subprocess, "run", run)
    return calls


def test_loaded_module_version_wins(tmp_path, monkeypatch, no_cli):
    f = tmp_path / "version"
    f.write_text("2.7.0\n")
    monkeypatch.setattr(dxrt, "_SYS_DRIVER_VERSION", f)
    assert dxrt.npu_driver_version() == "v2.7.0"
    assert no_cli == []


def test_installed_but_not_loaded_falls_back_to_modinfo(tmp_path, monkeypatch, no_cli):
    monkeypatch.setattr(dxrt, "_SYS_DRIVER_VERSION", tmp_path / "missing")

    def run(argv, *a, **k):
        assert argv == ["modinfo", "-F", "version", "dxrt_driver"]
        return subprocess.CompletedProcess(argv, 0, "v2.7.0\n", "")

    monkeypatch.setattr(dxrt.subprocess, "run", run)
    assert dxrt.npu_driver_version() == "v2.7.0"


def test_no_driver_is_none(tmp_path, monkeypatch, no_cli):
    monkeypatch.setattr(dxrt, "_SYS_DRIVER_VERSION", tmp_path / "missing")
    assert dxrt.npu_driver_version() is None


def test_dx_app_version_info_shows_the_driver(tmp_path, monkeypatch, no_cli):
    from dx_app.core import setup_steps
    f = tmp_path / "version"
    f.write_text("2.7.0\n")
    monkeypatch.setattr(dxrt, "_SYS_DRIVER_VERSION", f)
    assert setup_steps._get_npu_driver_version() == "v2.7.0"
    monkeypatch.setattr(dxrt, "_SYS_DRIVER_VERSION", tmp_path / "missing")
    assert setup_steps._get_npu_driver_version() == "--"


def test_dx_stream_setup_shows_the_driver(tmp_path, monkeypatch, no_cli):
    from dx_stream.core import status
    f = tmp_path / "version"
    f.write_text("2.7.0\n")
    monkeypatch.setattr(dxrt, "_SYS_DRIVER_VERSION", f)
    assert status._get_npu_driver_version() == "v2.7.0"


def test_bug_report_keeps_driver_and_runtime_apart(tmp_path, monkeypatch):
    from dx_app.core import developer
    f = tmp_path / "version"
    f.write_text("2.7.0\n")
    monkeypatch.setattr(dxrt, "_SYS_DRIVER_VERSION", f)
    monkeypatch.setattr(developer, "OUTPUTS_DIR", tmp_path)

    real_check_output = subprocess.check_output

    def check_output(argv, *a, **k):
        if argv[0] == "dxrt-cli":
            return "DXRT v3.5.0 (build: 5.502926e)\n"
        return real_check_output(argv, *a, **k)

    monkeypatch.setattr(developer.subprocess, "check_output", check_output)
    r = developer.bug_report()
    assert r["npu_driver"] == "v2.7.0"
    assert r["dx_runtime"].startswith("DXRT v3.5.0")

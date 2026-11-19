"""Setup steps behind Model Zoo's Build C++ runner and the Maintenance card (clean build, runtime reset)."""
import sys

import pytest

from dx_app.core import config, setup_steps
from shared.paths import host_arch


def test_model_build_targets_only_examples_with_a_cpp_source(monkeypatch, tmp_path):
    from shared import dx_app_layout as layout
    monkeypatch.setattr(layout, "example_name", lambda root, t, n, mf="": "alexnet_224x224")
    monkeypatch.setattr(layout, "cpp_source", lambda root, t, n, v: tmp_path / f"{n}_{v}.cpp")
    assert setup_steps._model_build_targets({"model_name": "alexnet", "category": "classification"}) == []
    (tmp_path / "alexnet_224x224_sync.cpp").write_text("")
    (tmp_path / "alexnet_224x224_async.cpp").write_text("")
    assert setup_steps._model_build_targets({"model_name": "alexnet", "category": "classification"}) == [
        "alexnet_224x224_sync", "alexnet_224x224_async"]


@pytest.mark.parametrize("bad", ["../x", "a b", "", "x;rm"])
def test_model_build_rejects_unsafe_names(bad):
    assert setup_steps._model_build_targets({"model_name": bad, "category": "classification"}) == []


def test_model_build_argv_is_native_and_targeted(monkeypatch):
    monkeypatch.setattr(setup_steps, "_model_build_targets", lambda p: ["m_sync"])
    argv, _ = setup_steps.step_argv("model-build", {"model_name": "m", "category": "c"})
    assert argv[0] == "bash" and argv[1].endswith("build.sh")
    assert argv[2:] == ["--target", "m_sync", "--type", "Release", "--arch", host_arch()]
    assert not setup_steps.SETUP_STEPS["model-build"].get("needs_sudo")


def test_maintenance_steps_need_sudo_and_run_the_studio_module():
    for step in ("clean-build", "runtime-reset"):
        cfg = setup_steps.SETUP_STEPS[step]
        assert cfg["needs_sudo"]
        argv, _ = setup_steps.step_argv(step, {})
        assert argv[:3] == [sys.executable, "-m", "dx_app.core.maintenance"] and argv[3] == step


def test_runtime_reset_requires_the_typed_word_server_side():
    r = setup_steps.setup_run("runtime-reset", {"password": "x", "confirm": "reset"})
    assert r["ok"] is False and r.get("code") == "confirm_required"


def test_model_build_endpoints_only_touch_model_build(monkeypatch):
    monkeypatch.setattr(config, "_comp_step", "dx-driver")
    monkeypatch.setattr(config, "_comp_done", False)
    monkeypatch.setattr(config, "_comp_proc", setup_steps._Starting())   # a driver install is running
    assert setup_steps.model_build_log()["busy"] is True
    assert setup_steps.model_build_stop()["ok"] is False


def test_status_exposes_commands_and_reset_word():
    st = setup_steps.setup_status()
    assert st["commands"]["dx-app-build"].endswith(f"--arch {host_arch()}")
    assert st["runtime-reset"]["confirm"] == "RESET"


def test_clean_build_removes_only_other_arch_build_dirs(tmp_path, monkeypatch):
    from dx_app.core import maintenance
    for a in ("x86_64", "aarch64"):
        (tmp_path / f"build_{a}").mkdir()
    (tmp_path / "src").mkdir()
    monkeypatch.setattr(maintenance, "DX_APP_ROOT", tmp_path)
    removed = maintenance.remove_other_arch_builds()
    assert removed == [tmp_path / f"build_{a}" for a in ("x86_64", "aarch64") if a != host_arch()]
    assert (tmp_path / f"build_{host_arch()}").exists() and (tmp_path / "src").exists()


def test_only_one_setup_job_runs_at_a_time(monkeypatch):
    """config._comp_proc was never assigned, so the server-side guard never fired; with Model Zoo starting
    builds from another page, a second job would clobber the first one's log and process."""
    import threading
    gate = threading.Event()

    class SlowProc:
        returncode = 0
        stdin = None
        def __init__(self, *a, **k):
            import io, os
            r, w = os.pipe(); os.close(w)
            self.stdout = io.FileIO(r, "rb")
        def poll(self):
            return 0 if gate.is_set() else None
        def wait(self, timeout=None):
            gate.wait(5); return 0
    monkeypatch.setattr(setup_steps.subprocess, "Popen", SlowProc)
    monkeypatch.setattr(config, "_comp_proc", None)
    assert setup_steps.setup_run("dx-app-setup", {}).get("started")
    second = setup_steps.setup_run("dx-app-setup", {})
    gate.set()
    assert second["ok"] is False and "already running" in second["error"]


def test_driver_loaded_but_uninstalled_is_not_ok(monkeypatch):
    """Reset removes the DKMS package while the module stays loaded until reboot: /dev/dxrt0 still exists,
    but the next boot has no driver, so Quick Start must reinstall it."""
    monkeypatch.setattr(setup_steps, "_dx_device_nodes", lambda: ["dxrt0"])
    monkeypatch.setattr(setup_steps, "_driver_installed", lambda: False)
    st = setup_steps._driver_status()
    assert st["ok"] is False and st["detail"] == "Loaded, but not installed for the next boot"
    monkeypatch.setattr(setup_steps, "_driver_installed", lambda: True)
    assert setup_steps._driver_status() == {"ok": True, "detail": "dxrt0"}
    monkeypatch.setattr(setup_steps, "_dx_device_nodes", lambda: [])
    assert setup_steps._driver_status()["ok"] is False


def test_driver_installed_reads_the_module_on_disk(monkeypatch):
    import subprocess as sp
    calls = []
    def fake(argv, **k):
        calls.append(argv)
        return sp.CompletedProcess(argv, 1 if argv[-1] == "dxrt_driver" else 0, "", "")
    monkeypatch.setattr(setup_steps.subprocess, "run", fake)
    assert setup_steps._driver_installed() is False
    assert calls[0][:2] == ["modinfo", "-n"]

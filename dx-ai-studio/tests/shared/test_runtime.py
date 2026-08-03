import importlib
import os
import sys
from pathlib import Path
from types import SimpleNamespace


def test_lib_dirs_include_dx_rt():
    import shared.runtime as r
    importlib.reload(r)
    libs = [str(p) for p in r.runtime_lib_dirs()]
    assert any(p.endswith("dx_rt/build_x86_64/lib") for p in libs)
    assert any(p.endswith("dx_rt/lib") for p in libs)
    assert "/usr/local/lib" in libs
    assert "/usr/lib" in libs
    # Order matters: system dirs first, dx_rt build lib before dx_rt lib — this is the
    # exact order the two duplicate _lib_dirs lists in dx_app/core/inference.py used.
    assert libs[0] == "/usr/local/lib"
    assert libs[1] == "/usr/lib"
    assert libs[2].endswith("dx_rt/build_x86_64/lib")
    assert libs[3].endswith("dx_rt/lib")


def test_installed_runtime_lib_dirs_exclude_checkout_runtime():
    import shared.runtime as runtime
    from shared.paths import DX_RUNTIME_ROOT

    assert hasattr(runtime, "installed_runtime_lib_dirs")
    assert all(
        not path.resolve().is_relative_to(DX_RUNTIME_ROOT.resolve())
        for path in runtime.installed_runtime_lib_dirs()
    )


def test_runtime_python_is_str():
    import shared.runtime as r
    assert isinstance(r.runtime_python(), str) and r.runtime_python()


def test_runtime_python_returns_none_without_a_complete_interpreter(monkeypatch):
    import shared.runtime as r

    monkeypatch.setattr(r, "runtime_venv_roots", lambda: [])
    monkeypatch.setattr(r.sys, "executable", "/studio/python")
    monkeypatch.setattr(r.shutil, "which", lambda name: None)
    monkeypatch.setattr(r, "_has_numpy_cv2_dxengine", lambda python: False)

    assert r.runtime_python() is None


def test_dx_engine_search_paths_type():
    import shared.runtime as r
    assert isinstance(r.dx_engine_search_paths(), list)


def test_ld_library_path_prepends_existing_env(monkeypatch):
    import shared.runtime as r
    monkeypatch.setenv("LD_LIBRARY_PATH", "/some/custom/lib")
    ld = r.ld_library_path()
    assert ld.startswith("/some/custom/lib:")


def test_ld_library_path_no_env_still_returns_existing_dirs(monkeypatch):
    import shared.runtime as r
    monkeypatch.delenv("LD_LIBRARY_PATH", raising=False)
    ld = r.ld_library_path()
    # /usr/lib and /usr/local/lib exist on any dev box; at minimum system dirs show up.
    assert isinstance(ld, str)


def test_runtime_venv_roots_are_suite_relative():
    import shared.runtime as r
    from shared.paths import SUITE_ROOT, DX_RUNTIME_ROOT
    roots = r.runtime_venv_roots()
    assert roots == [DX_RUNTIME_ROOT / "venv-dx-runtime", SUITE_ROOT / "venv-dx-runtime"]


def test_dx_engine_pythonpath_dirs_shadow_fix_skips_when_python_has_dx_engine(monkeypatch):
    """The _pydxrt shadow fix: if the target python already has a WORKING dx_engine,
    do NOT add the uncompiled dx_rt/python_package/src tree — that would shadow it and
    break with ImportError: _pydxrt."""
    import shared.runtime as r
    monkeypatch.setattr(r, "runtime_python_has_dx_engine", lambda python=None: True)
    assert r.dx_engine_pythonpath_dirs(python="/fake/python3") == []


def test_dx_engine_pythonpath_dirs_falls_back_when_python_lacks_dx_engine(monkeypatch):
    import shared.runtime as r
    monkeypatch.setattr(r, "runtime_python_has_dx_engine", lambda python=None: False)
    dirs = [str(p) for p in r.dx_engine_pythonpath_dirs(python="/fake/python3")]
    assert any(p.endswith("python_package/src") for p in dirs)
    assert any(p.endswith("python_package") and not p.endswith("python_package/src") for p in dirs)


def test_dx_rt_cli_python_and_pythonpath():
    import shared.runtime as r
    py = r.dx_rt_cli_python()
    assert isinstance(py, str) and py
    pp = r.dx_rt_cli_pythonpath()
    assert str(pp).endswith("dx_rt/python_package") or str(pp).endswith("dx_rt/python_package/")


def test_telemetry_python_probe_requires_device_status_and_configuration(monkeypatch, tmp_path):
    import shared.runtime as r

    root = tmp_path / "runtime"
    candidate = root / "bin" / "python3"
    candidate.parent.mkdir(parents=True)
    candidate.touch()
    monkeypatch.setattr(r, "runtime_venv_roots", lambda: [root])
    monkeypatch.setattr(r.sys, "executable", "/studio/python")
    monkeypatch.setattr(r.shutil, "which", lambda name: None)
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(r.subprocess, "run", fake_run)

    assert r.telemetry_python() == str(candidate)
    assert calls == [(
        [str(candidate), "-c",
         "from dx_engine.device_status import DeviceStatus; "
         "from dx_engine.configuration import Configuration; "
         "print(DeviceStatus.get_device_count())"],
        {"capture_output": True, "text": True, "timeout": 20},
    )]


def test_telemetry_python_does_not_mutate_sys_path(monkeypatch, tmp_path):
    import shared.runtime as r

    root = tmp_path / "runtime"
    candidate = root / "bin" / "python3"
    candidate.parent.mkdir(parents=True)
    candidate.touch()
    monkeypatch.setattr(r, "runtime_venv_roots", lambda: [root])
    monkeypatch.setattr(r.sys, "executable", "/studio/python")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(
        r.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0),
    )
    original_sys_path = sys.path.copy()

    assert r.telemetry_python() == str(candidate)
    assert sys.path == original_sys_path


def test_telemetry_python_skips_failed_candidates_and_deduplicates(monkeypatch, tmp_path):
    import shared.runtime as r

    root = tmp_path / "runtime"
    runtime_python3 = root / "bin" / "python3"
    runtime_python = root / "bin" / "python"
    runtime_python3.parent.mkdir(parents=True)
    runtime_python3.touch()
    runtime_python.touch()
    monkeypatch.setattr(r, "runtime_venv_roots", lambda: [root])
    monkeypatch.setattr(r.sys, "executable", "/studio/python")
    monkeypatch.setattr(
        r.shutil,
        "which",
        lambda name: {"python3": "/path/python3", "python": "/path/python"}[name],
    )
    attempted = []

    def fake_run(command, **kwargs):
        attempted.append(command[0])
        return SimpleNamespace(returncode=int(command[0] != "/path/python"))

    monkeypatch.setattr(r.subprocess, "run", fake_run)

    assert r.telemetry_python() == "/path/python"
    assert attempted == [
        str(runtime_python3), str(runtime_python), "/studio/python", "/path/python3", "/path/python",
    ]
    assert len(attempted) == len(set(attempted))


def test_telemetry_python_returns_none_when_no_candidate_is_compatible(monkeypatch, tmp_path):
    import shared.runtime as r

    root = tmp_path / "runtime"
    candidate = root / "bin" / "python3"
    candidate.parent.mkdir(parents=True)
    candidate.touch()
    monkeypatch.setattr(r, "runtime_venv_roots", lambda: [root])
    monkeypatch.setattr(r.sys, "executable", "/studio/python")
    monkeypatch.setattr(r.shutil, "which", lambda name: None)
    monkeypatch.setattr(r.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=1))

    assert r.telemetry_python() is None


def test_telemetry_worker_env_is_child_copy_with_runtime_ld_and_fallback_pythonpath(monkeypatch):
    import shared.runtime as r

    monkeypatch.setenv("LD_LIBRARY_PATH", "/parent/lib")
    monkeypatch.setenv("PYTHONPATH", "/parent/python")
    monkeypatch.setattr(r, "ld_library_path", lambda: "/runtime/lib:/parent/lib")
    monkeypatch.setattr(r, "runtime_python_has_dx_engine", lambda python: False)
    monkeypatch.setattr(
        r,
        "dx_engine_pythonpath_dirs",
        lambda python: [Path("/runtime/python/src"), Path("/runtime/python")],
    )

    worker_env = r.telemetry_worker_env("/runtime/python3")

    assert worker_env is not os.environ
    assert worker_env["LD_LIBRARY_PATH"] == "/runtime/lib:/parent/lib"
    assert worker_env["PYTHONPATH"] == "/runtime/python/src:/runtime/python:/parent/python"
    assert os.environ["LD_LIBRARY_PATH"] == "/parent/lib"
    assert os.environ["PYTHONPATH"] == "/parent/python"


def test_telemetry_worker_env_skips_pythonpath_fallback_for_working_dx_engine(monkeypatch):
    import shared.runtime as r

    monkeypatch.setenv("PYTHONPATH", "/parent/python")
    monkeypatch.setattr(r, "ld_library_path", lambda: "/runtime/lib")
    monkeypatch.setattr(r, "runtime_python_has_dx_engine", lambda python: True)

    def fail_if_called(python):
        raise AssertionError("source fallback must not be added")

    monkeypatch.setattr(r, "dx_engine_pythonpath_dirs", fail_if_called)

    worker_env = r.telemetry_worker_env("/runtime/python3")

    assert worker_env["PYTHONPATH"] == "/parent/python"
    assert os.environ["PYTHONPATH"] == "/parent/python"

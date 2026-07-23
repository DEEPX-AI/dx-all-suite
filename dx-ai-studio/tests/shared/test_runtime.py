import importlib
import os
import sys


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


def test_runtime_python_is_str():
    import shared.runtime as r
    assert isinstance(r.runtime_python(), str) and r.runtime_python()


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

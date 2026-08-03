"""Tests for deterministic Studio child-process environments."""
from pathlib import Path
from types import SimpleNamespace


def _ready_profile(tmp_path):
    studio_venv = tmp_path / "studio-infer"
    return SimpleNamespace(
        python_executable=studio_venv / "bin" / "python3",
        venv_root=studio_venv,
        library_dirs=(tmp_path / "runtime" / "lib",),
        plugin_dir=tmp_path / "runtime" / "gst",
        postprocess_lib_dir=tmp_path / "runtime" / "postprocess",
    )


def test_child_environment_does_not_inherit_broken_python_or_gst_paths(tmp_path):
    from shared.runtime_environment import build_child_environment

    profile = _ready_profile(tmp_path)
    parent = {
        "HOME": "/home/tester",
        "LANG": "C.UTF-8",
        "PATH": "/broken/venv/bin:/usr/local/bin:/usr/bin",
        "VIRTUAL_ENV": "/broken/venv",
        "PYTHONPATH": "/broken/python",
        "LD_LIBRARY_PATH": "/broken/lib",
        "GST_PLUGIN_PATH": "/broken/gst",
    }

    env = build_child_environment(profile=profile, parent=parent)

    assert env["VIRTUAL_ENV"] == str(profile.venv_root)
    assert "/broken/venv" not in env["PATH"]
    assert "PYTHONPATH" not in env
    assert env["LD_LIBRARY_PATH"] == str(profile.library_dirs[0])
    assert env["GST_PLUGIN_PATH"].split(":")[0] == str(profile.plugin_dir)
    assert env["DXSTREAM_POSTPROCESS_LIB_PATH"] == str(profile.postprocess_lib_dir)
    assert env["HOME"] == "/home/tester"
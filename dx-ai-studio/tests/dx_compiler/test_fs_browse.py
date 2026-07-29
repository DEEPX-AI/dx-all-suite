"""Folder-picker backend: safe server-side directory listing + mkdir.

Backs the Output Directory 📁 browse button in the compiler UI. Logic lives in
dx_compiler.core.fs_browse (pure functions) so it is testable without a running
server; the HTTP handlers are thin wrappers.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dx_compiler.core import fs_browse


def test_list_directory_returns_only_subdirs(tmp_path):
    (tmp_path / "alpha").mkdir()
    (tmp_path / "beta").mkdir()
    (tmp_path / "note.txt").write_text("x")
    res = fs_browse.list_directory(str(tmp_path))
    assert res["ok"] is True
    assert res["path"] == str(tmp_path.resolve())
    assert "alpha" in res["dirs"] and "beta" in res["dirs"]
    assert "note.txt" not in res["dirs"]          # files excluded
    assert res["files"] == []                      # folder-only mode: no files
    assert res["parent"] == str(tmp_path.resolve().parent)


def test_list_directory_file_mode_filters_by_ext(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.json").write_text("{}")
    (tmp_path / "b.JSON").write_text("{}")   # case-insensitive match
    (tmp_path / "c.onnx").write_text("x")    # other ext excluded
    (tmp_path / ".hidden.json").write_text("{}")  # dotfiles hidden
    res = fs_browse.list_directory(str(tmp_path), ".json")
    assert res["dirs"] == ["sub"]                  # dirs still listed
    assert "a.json" in res["files"] and "b.JSON" in res["files"]
    assert "c.onnx" not in res["files"]
    assert ".hidden.json" not in res["files"]


def test_list_directory_ext_normalized_and_folder_only_default(tmp_path):
    (tmp_path / "x.json").write_text("{}")
    # no ext → folder-only (backward compatible)
    assert fs_browse.list_directory(str(tmp_path))["files"] == []
    # ext given → file appears
    assert "x.json" in fs_browse.list_directory(str(tmp_path), ".json")["files"]


def test_list_directory_empty_path_uses_safe_default():
    res = fs_browse.list_directory("")
    assert res["ok"] is True
    assert isinstance(res["dirs"], list)
    assert Path(res["path"]).is_dir()


def test_list_directory_rejects_unsafe_root():
    with pytest.raises(ValueError):
        fs_browse.list_directory("/etc")


def test_list_directory_rejects_nonexistent(tmp_path):
    with pytest.raises(ValueError):
        fs_browse.list_directory(str(tmp_path / "does-not-exist"))


def test_make_directory_creates_under_safe_root(tmp_path):
    res = fs_browse.make_directory(str(tmp_path), "new_output")
    assert res["ok"] is True
    assert (tmp_path / "new_output").is_dir()
    assert res["path"] == str((tmp_path / "new_output").resolve())


def test_make_directory_rejects_traversal(tmp_path):
    with pytest.raises(ValueError):
        fs_browse.make_directory(str(tmp_path), "../evil")


def test_make_directory_rejects_separator(tmp_path):
    with pytest.raises(ValueError):
        fs_browse.make_directory(str(tmp_path), "a/b")


def test_server_wires_folder_browser_routes():
    src = (ROOT / "dx_compiler/server.py").read_text(encoding="utf-8")
    assert "/api/listdir" in src
    assert "/api/mkdir" in src

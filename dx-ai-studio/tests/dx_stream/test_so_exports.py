"""function-name candidates are functions the library actually exports."""
from __future__ import annotations

import _ctypes
from pathlib import Path

import pytest

from dx_stream.core.so_exports import exported_functions

PPU_LIB = Path("/usr/local/share/gstdxstream/lib/libpostprocess_ppu.so")
JS = Path(__file__).resolve().parents[2] / "dx_stream/static/js/stream-pipeline-renderer.js"


def test_reads_exported_function_of_a_shared_object():
    assert exported_functions(_ctypes.__file__) == ["PyInit__ctypes"]


def test_non_elf_and_missing_files_give_nothing(tmp_path):
    text = tmp_path / "x.so"
    text.write_text("not an elf")
    assert exported_functions(text) == []
    assert exported_functions(tmp_path / "missing.so") == []


@pytest.mark.skipif(not PPU_LIB.exists(), reason="dx_stream postprocess libraries not installed")
def test_ppu_library_offers_the_functions_the_ppu_demos_use():
    fns = exported_functions(PPU_LIB)
    assert {"SCRFD500M_PPU", "YOLOV5Pose_PPU"} <= set(fns)
    assert "PostProcess" not in fns


def test_property_panel_takes_function_names_from_the_selected_library():
    js = JS.read_text(encoding="utf-8")
    body = js[js.index("if (propName === 'function-name')"):]
    body = body[:body.index("if (propName === 'config-file-path')")]
    assert "a.functions[lib]" in body
    assert "_getDropdownOptions(entry[0], node.type, node.properties)" in js

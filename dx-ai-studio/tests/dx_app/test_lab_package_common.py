"""Composer export — a per-model package runs outside the Studio (2026-10-11 audit).

extract_model_package.sh trims common/ to static imports, but per-model examples name their
processors in config.json; the exported yolo26n package died with "processor class
'LetterboxPreprocessor' is exported by neither common.processors nor common.visualizers".
"""
from __future__ import annotations

import json

import pytest

from dx_app.core import lab_package


def _tree(root, exports):
    common = root / "runtime/python/object_detection/m/common"
    (common / "processors").mkdir(parents=True)
    (common / "visualizers").mkdir(parents=True)
    (common / "processors/__init__.py").write_text("\n".join(f"from .x import {e}" for e in exports))
    (common / "visualizers/__init__.py").write_text("from .v import DetectionVisualizer\n")
    (root / "runtime/python/object_detection/m/config.json").write_text(json.dumps({
        "preprocessor": {"class": "LetterboxPreprocessor"},
        "postprocessor": {"class": "YOLOv8Postprocessor"},
        "visualizer": {"class": "DetectionVisualizer"}}))
    return common


def test_a_trimmed_common_is_caught_before_export(tmp_path):
    _tree(tmp_path, ["YOLOv8Postprocessor"])
    missing = lab_package._unresolvable_processor_classes(tmp_path)
    assert missing == ["runtime/python/object_detection/m/config.json: LetterboxPreprocessor"]


def test_the_full_common_is_vendored_next_to_the_runner(tmp_path):
    pkg = tmp_path / "pkg"
    common = _tree(pkg, ["YOLOv8Postprocessor"])
    src = tmp_path / "dx_app/src/python_example/common/processors"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("from .letterbox_preprocessor import LetterboxPreprocessor\n"
                                     "from .yolo import YOLOv8Postprocessor\n")
    (src / "letterbox_preprocessor.py").write_text("class LetterboxPreprocessor: ...\n")
    lab_package._complete_python_common(tmp_path / "dx_app", common.parent)
    assert (common / "processors/letterbox_preprocessor.py").is_file()
    assert lab_package._unresolvable_processor_classes(pkg) == []


def test_export_model_package_tars_the_per_model_folder_with_a_full_common(tmp_path, monkeypatch):
    """/api/extract made outputs/py/<task>/<family>/<stem>/ but looked for a folder named after the model
    directly under outputs/, so download_url was empty; and the folder had the trimmed common/ (2026-10-11)."""
    import subprocess
    import tarfile

    from dx_app.core import developer

    root = tmp_path / "dx_app"
    ex = root / "src/python_example/object_detection/yolo26/yolo26-n_640x640"
    ex.mkdir(parents=True)
    full = root / "src/python_example/common/processors"
    full.mkdir(parents=True)
    (full / "letterbox_preprocessor.py").write_text("class LetterboxPreprocessor: ...\n")
    (root / "scripts").mkdir()
    (root / "scripts/extract_model_package.sh").write_text("")
    out = tmp_path / "outputs"

    def fake_run(cmd, **kw):
        d = out / "py" / "object_detection/yolo26/yolo26-n_640x640"
        (d / "common/processors").mkdir(parents=True)
        (d / "yolo26-n_640x640_sync.py").write_text("")
        return subprocess.CompletedProcess(cmd, 0, "ok", "")

    for name, value in (("SCRIPTS_DIR", root / "scripts"), ("PY_DIR", root / "src/python_example"),
                        ("CPP_DIR", root / "src/cpp_example"), ("OUTPUTS_DIR", out), ("DX_APP_ROOT", root)):
        monkeypatch.setattr(developer, name, value)
    monkeypatch.setattr(developer.subprocess, "run", fake_run)
    out.mkdir()
    res = developer.extract_model_package("object_detection/yolo26/yolo26-n_640x640", "py")
    assert res["ok"] and res["download_url"], res
    with tarfile.open(out / res["download_url"].rsplit("/", 1)[-1]) as tar:
        names = tar.getnames()
    assert "py/yolo26-n_640x640/yolo26-n_640x640_sync.py" in names
    assert "py/yolo26-n_640x640/common/processors/letterbox_preprocessor.py" in names

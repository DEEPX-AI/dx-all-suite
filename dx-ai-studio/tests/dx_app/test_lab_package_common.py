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

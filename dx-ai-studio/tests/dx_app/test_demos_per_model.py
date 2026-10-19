"""run_demo.sh on the per-model layout.

There ``DEMO_PY_DIR`` is ``task/family`` and the run path is built from the stem of ``DEMO_MODEL``
(``bin/<stem>_sync``, ``python_example/<py_dir>/<stem>/<stem>_sync.py``). The studio's model name is the stem too.
"""
from __future__ import annotations

import json
from pathlib import Path

RUN_DEMO = '''#!/bin/bash
DEMO_LABELS=(
    "Object Detection         (YOLOv7)"
    "Image Retrieval          (CLIP RN50)"
)
DEMO_GROUPS=(
    "Detection" "Recognition"
)
DEMO_CPP_BASE=(
    "yolov7" "clip-img_resnet50_224x224_openai"
)
DEMO_PY_DIR=(
    "object_detection/yolov7"
    "image_retrieval/clip_rn50"
)
DEMO_PY_BASE=(
    "yolov7" "clip-img_resnet50_224x224_openai"
)
DEMO_MODEL=(
    yolov7_640x640.dxnn clip-img_resnet50_224x224_openai.dxnn
)
DEMO_VIDEO=(
    "assets/videos/snowboard.mp4" ""
)
DEMO_IMAGE=(
    "sample/img/sample_street.jpg" "sample/img/sample_person_a2.jpg"
)
DEMO_PY_ASYNC=(
    "full" "none"
)
DEMO_IMAGE_ONLY=(
    0 1
)
'''


def test_per_model_demos_are_named_by_the_model_stem(tmp_path):
    from shared import dx_app_layout as layout
    from dx_app.core.demos import parse_run_demo

    root = tmp_path / "dx_app"
    (root / "config").mkdir(parents=True)
    (root / "config/model_registry.json").write_text(json.dumps(
        [{"variant": "yolov7_640x640", "family": "yolov7", "task": "object_detection"}]))
    (root / "run_demo.sh").write_text(RUN_DEMO)
    layout.clear_cache()
    demos = parse_run_demo(root / "run_demo.sh")
    assert [(d["category"], d["family"], d["model_name"]) for d in demos] == [
        ("object_detection", "yolov7", "yolov7_640x640"),
        ("image_retrieval", "clip_rn50", "clip-img_resnet50_224x224_openai")]
    assert demos[1]["default_video"] == "" and demos[1]["image_only"] is True


def test_legacy_demos_keep_the_example_dir_name(tmp_path):
    from shared import dx_app_layout as layout
    from dx_app.core.demos import parse_run_demo

    root = tmp_path / "dx_app"
    root.mkdir()
    (root / "run_demo.sh").write_text(RUN_DEMO.replace('"object_detection/yolov7"', '"object_detection/yolov7"'))
    layout.clear_cache()
    demos = parse_run_demo(root / "run_demo.sh")
    assert demos[0]["model_name"] == "yolov7" and demos[0].get("family") is None

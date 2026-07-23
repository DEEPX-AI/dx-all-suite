"""Sample-image mapping must be model-aware and not show unrelated images.

Before this fix the inference Sample tab was dead for every model: the catalog never
set `sample_dir` (so `hasSampleMetadata` was always false → tab disabled), the server
never returned `sample_dir`, and it ignored `model_id` so MODEL_IMAGE_OVERRIDE never
applied (a face detector got the ppu default street shot). Pair/gallery tasks (reid,
embedding) have no flat sample file and must stay unmapped rather than mis-point.
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "dx_modelzoo"))


def _catalog_models():
    from core import catalog as C
    return {m["id"]: m for m in C.get_catalog()["models"]}


def test_single_image_task_gets_sample_dir():
    ms = _catalog_models()
    m = ms["yolov7_w6"]  # object_detection
    assert m.get("sample_dir") == "sample/img"
    assert m.get("sample_image") == "sample_street.jpg"


def test_model_image_override_wins_over_task_default():
    # scrfd500m_ppu is a face detector in the "ppu" category; the override must map it
    # to a face sample, not the ppu default (sample_street.jpg).
    ms = _catalog_models()
    assert ms["scrfd500m_ppu"].get("sample_image") == "sample_face.jpg"
    assert ms["yolov5pose_ppu"].get("sample_image") == "sample_people.jpg"


def test_pair_task_has_no_flat_sample():
    # reid (person_pair dir) / embedding (face_pair dir) cannot be a single flat file →
    # sample_dir stays None so the UI honestly disables the tab. (casvit_t is a reid model;
    # casvit_xs was removed from the staging catalog.)
    ms = _catalog_models()
    assert ms["casvit_t"].get("sample_dir") is None
    assert ms["casvit_t"].get("sample_image") is None


def test_demo_input_is_representative_image_for_file_tasks():
    # "Use Default" must run the demo on the same image the thumbnail was made from,
    # not dx_app's divergent per-category default.
    ms = _catalog_models()
    assert ms["yolov7_w6"].get("demo_input") == "sample/img/sample_street.jpg"
    assert ms["scrfd500m_ppu"].get("demo_input") == "sample/img/sample_face.jpg"  # override
    assert ms["yolo26n_obb"].get("demo_input") == "sample/dota8_test/P0284.png"   # cross-dir file


def test_demo_input_is_pair_dir_for_reid_embedding():
    # reid/embedding demos take a directory of image pairs; the sync runner expands it
    # and renders the pair comparison, exactly like dx_app run_demo.sh.
    ms = _catalog_models()
    assert ms["casvit_t"].get("demo_input") == "sample/img/person_pair"
    assert ms["arcface_r50"].get("demo_input") == "sample/img/face_pair"


def test_js_reid_embedding_default_to_python_variant():
    # C++ reid/embedding runners emit no comparison image; python must be the default
    # exec path so "Use Default" produces a visible pair-comparison result.
    src = (REPO_ROOT / "dx_modelzoo" / "static" / "js" / "inference.js").read_text(encoding="utf-8")
    assert "'reid'" in src and "'embedding'" in src
    assert "['python', 'cpp']" in src, "reid/embedding must offer python first (default)"


def test_js_default_run_passes_demo_input():
    src = (REPO_ROOT / "dx_modelzoo" / "static" / "js" / "inference.js").read_text(encoding="utf-8")
    assert "data-demo-input=" in src, "Use Default button must carry the representative image path"
    assert "d.demoInput" in src, "default-run handler must read the demo_input data attr"


def test_server_endpoint_honors_model_id_and_returns_sample_dir():
    src = (REPO_ROOT / "dx_modelzoo" / "server.py").read_text(encoding="utf-8")
    block = src.split('if path == "/api/sample-images":', 1)[1].split("if path", 1)[0]
    assert "model_id" in block, "server must read the model_id query param"
    assert "MODEL_IMAGE_OVERRIDE" in block, "server must apply the per-model override"
    assert '"sample_dir"' in block, "server must return sample_dir so the grid renders"

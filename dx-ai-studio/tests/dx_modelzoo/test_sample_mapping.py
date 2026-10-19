"""Sample-image mapping must be model-aware and not show unrelated images.

The inference Sample tab needs the catalog to set `sample_dir` (else `hasSampleMetadata`
is false and the tab is disabled), the server to return `sample_dir`, and the server to
honour `model_id` so MODEL_IMAGE_OVERRIDE applies (a face detector must not get the ppu
default street shot). Pair/gallery tasks (reid, embedding) have no flat sample file and
must stay unmapped rather than mis-point.
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


def _overridden(ms):
    """MODEL_IMAGE_OVERRIDE entries whose model this dx_app has (the per-model dx_app no longer ships
    scrfd500m_ppu and yolov5pose_ppu as examples)."""
    from core.config import MODEL_IMAGE_OVERRIDE
    found = {mid: path for mid, path in MODEL_IMAGE_OVERRIDE.items() if mid in ms}
    assert found, "no MODEL_IMAGE_OVERRIDE model is in the catalog"
    return found


def test_model_image_override_wins_over_task_default():
    # e.g. scrfd500m_ppu, a face detector in the old "ppu" category, maps to a face sample, not the ppu
    # default (sample_street.jpg); handlandmarklite_1 to a hand.
    ms = _catalog_models()
    for mid, path in _overridden(ms).items():
        assert ms[mid].get("sample_image") == Path(path).name, mid


def _per_model():
    from core.config import DX_APP_ROOT
    from shared import dx_app_layout as layout
    return layout.detect(DX_APP_ROOT) == layout.PER_MODEL


def test_pair_task_has_no_flat_sample():
    # reid (person_pair dir) / embedding (face_pair dir) cannot be a single flat file →
    # sample_dir stays None so the UI honestly disables the tab.
    ms = _catalog_models()
    assert ms["arcface_r50"].get("sample_dir") is None
    assert ms["arcface_r50"].get("sample_image") is None
    if not _per_model():
        # In main dx_app casvit_t is reid; the per-model dx_app files it under image_classification.
        assert ms["casvit_t"].get("sample_dir") is None
        assert ms["casvit_t"].get("sample_image") is None


def test_demo_input_is_representative_image_for_file_tasks():
    # "Use Default" must run the demo on the same image the thumbnail was made from,
    # not dx_app's divergent per-category default.
    ms = _catalog_models()
    assert ms["yolov7_w6"].get("demo_input") == "sample/img/sample_street.jpg"
    for mid, path in _overridden(ms).items():
        assert ms[mid].get("demo_input") == path, mid                            # override
    # dx_app's OBB sample is sample_airport_satellite_view.png, and the obb thumbnails were
    # made from it on the NPU, so the demo runs on the same image as the thumbnail.
    assert ms["yolo26n_obb"].get("demo_input") == "sample/img/sample_airport_satellite_view.png"


def test_demo_input_is_pair_dir_for_reid_embedding():
    # reid/embedding demos take a directory of image pairs; the sync runner expands it
    # and renders the pair comparison, exactly like dx_app run_demo.sh.
    ms = _catalog_models()
    assert ms["arcface_r50"].get("demo_input") == "sample/img/face_pair"
    if _per_model():
        # Per-model person ReID takes one query plus a gallery: the example's config.json default_image
        assert ms["repvgg_a0_reid_256x128"]["category"] == "reid"
        assert ms["repvgg_a0_reid_256x128"].get("demo_input") == "sample/reid/queries/sample_person_a2.jpg"
    else:
        assert ms["casvit_t"].get("demo_input") == "sample/img/person_pair"


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

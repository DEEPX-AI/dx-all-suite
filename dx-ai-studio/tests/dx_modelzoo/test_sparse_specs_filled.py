"""The 11 models the source left sparse now carry params/ops/accuracy, researched from
upstream (GitHub/HF/papers) or mirrored from an exact DEEPX sibling. Guards the values and
the CAS-ViT license correction (was wrongly Apache-2.0; the repo LICENSE is MIT)."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "dx_modelzoo"))


def _ms():
    from core import catalog as C
    return {m["id"]: m for m in C.get_catalog()["models"]}


def _raw(m):
    return ((m.get("evaluation") or {}).get("raw") or {}).get("accuracy")


def test_casvit_license_is_mit_not_apache():
    ms = _ms()
    # casvit_xs / casvit_s were dropped from the staging catalog; casvit_t / casvit_m remain.
    for v in ("casvit_t", "casvit_m"):
        assert ms[v]["legal"]["license"] == "MIT", f"{v} license must be MIT (repo LICENSE)"


def test_sparse_cluster_has_params_ops_accuracy():
    ms = _ms()
    # params/ops are curated specification values (stable); accuracy is now sourced
    # from the OFFICIAL publish-site snapshot (generated_catalog.json) at load, so it
    # is dynamic and legitimately differs from the old hand-derived numbers
    # (e.g. casvit_t 82.3 → official 83.026, efficientformerv2_l 83.5 → 83.522).
    # Assert accuracy PRESENCE + plausible format/range, not an exact pinned value.
    expect = {
        "casvit_t": ("21.76", "3.6"),
        "vitb32": ("88.22", "4.41"),
        "efficientformerv2_l": ("26.1", "5.12"),
        "yolov7_w6": ("70.4", "180"),
    }
    for mid, (p, o) in expect.items():
        s = ms[mid].get("specification") or {}
        assert s.get("parameters") == p and s.get("operations") == o, mid
        raw = _raw(ms[mid])
        assert raw not in (None, ""), f"{mid} missing accuracy"
        acc = float(raw)  # must parse as a number
        assert 0.0 < acc <= 100.0, f"{mid} accuracy out of plausible range: {raw}"


def test_yolov5pose_source_corrected_to_ti():
    # upstream is TI edgeai-yolov5 (yolo-pose), not ultralytics
    assert "TexasInstruments/edgeai-yolov5" in _ms()["yolov5pose_ppu"]["legal"]["source_url"]

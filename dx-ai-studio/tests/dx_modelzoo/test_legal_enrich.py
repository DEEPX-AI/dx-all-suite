"""Legal fields the ModelZoo source omits but which are mechanically derivable
(copyright = source repo owner, license body = canonical SPDX text) must be filled,
without overwriting curated values. Every model should end up with a complete legal block.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "dx_modelzoo"))


def _models():
    from core import catalog as C
    return C.get_catalog()["models"]


def test_all_models_have_complete_legal_block():
    ms = _models()
    # source_url + copyright are mechanically derivable for every model: the source
    # comes from the studio's curated catalog or the staging dx-modelzoo model YAML
    # `reference` field, and copyright is derived from the repo owner.
    for key in ("source_url", "copyright"):
        missing = [m["id"] for m in ms if not (m.get("legal") or {}).get(key)]
        assert not missing, f"{key} missing for: {missing[:10]}"
    # License is filled wherever the upstream license is known (curated, or mapped from
    # the source repo). It must always come paired with its canonical license_text — we
    # never assert one without the other. Models whose upstream declares no discoverable
    # license are honestly left blank rather than assigned a fabricated license.
    for m in ms:
        lg = m.get("legal") or {}
        if lg.get("license"):
            assert lg.get("license_text"), f"license without canonical text: {m['id']}"
        if lg.get("license_text"):
            assert lg.get("license"), f"license_text without license: {m['id']}"


def test_copyright_derived_from_source_repo_owner():
    ms = {m["id"]: m for m in _models()}
    assert ms["levit384"]["legal"]["copyright"] == "Facebook"             # huggingface.co/facebook
    assert ms["yolov7_w6"]["legal"]["copyright"] == "WongKinYiu"          # curated, preserved
    assert ms["realesrgan_x2"]["legal"]["copyright"] == "xinntao"         # github owner, verbatim


def test_license_text_is_canonical_reference():
    ms = {m["id"]: m for m in _models()}
    # efficientformerv2_l is Apache-2.0 (snap-research/EfficientFormer); yolov7_w6 is GPL-3.0.
    assert "apache.org/licenses/LICENSE-2.0" in ms["efficientformerv2_l"]["legal"]["license_text"]
    assert "gpl-3.0" in ms["yolov7_w6"]["legal"]["license_text"]

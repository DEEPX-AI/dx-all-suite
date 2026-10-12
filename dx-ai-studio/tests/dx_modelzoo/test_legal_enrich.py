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


def _no_reference_ids():
    import json
    gen = json.loads((REPO_ROOT / "dx_modelzoo" / "data" / "generated_catalog.json").read_text(encoding="utf-8"))
    return {g["id"] for g in gen["models"]
            if str(((g.get("legal") or {}).get("source_url") or "")).strip().lower() in ("no reference", "-")}


def test_no_reference_is_never_shown_as_a_source():
    """A model whose page gives its source as "No Reference" gets an empty source, whether it is publish_only
    or a conf row; that text never stands in the URL slot."""
    from core import catalog as C
    m = {"legal": {"source_url": "No Reference", "license": "Apache-2.0"}}
    C._enrich_legal(m)
    assert m["legal"]["source_url"] == "" and m["legal"]["license_text"]
    shown = [x["id"] for x in _models() if str((x.get("legal") or {}).get("source_url") or "").lower() == "no reference"]
    assert not shown, shown[:10]


def test_all_models_have_complete_legal_block():
    ms = _models()
    # source_url + copyright are mechanically derivable for every model: the source
    # comes from the studio's curated catalog or the staging dx-modelzoo model YAML
    # `reference` field, and copyright is derived from the repo owner.
    # Models whose page gives the source as "No Reference" are left empty, never made up. In a per-model
    # dx_app such models are conf rows rather than publish_only, so they are identified by the page text.
    no_ref = _no_reference_ids()
    for key in ("source_url", "copyright"):
        missing = [m["id"] for m in ms if not (m.get("legal") or {}).get(key)
                   and not (m["id"] in no_ref and not (m.get("legal") or {}).get("source_url"))]
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


# The yolo26_depth family needs both a current generated_catalog.json and a working id match
# (studio `yolo26_depth_n` vs generated `yolo26_depth_n_768x768`) to carry its legal block.
#
# test_all_models_have_complete_legal_block only checks "not empty". A sync that blanks the
# values or points at the wrong repository would still pass it, so the real values are pinned here.
# The ids follow the publish page's .dxnn name (yolo26-depth-n_768x768) so main and per-model
# dx_app share them.
_YOLO26_DEPTH_IDS = (
    "yolo26_depth_n_768x768",
    "yolo26_depth_s_768x768",
    "yolo26_depth_m_768x768",
    "yolo26_depth_l_768x768",
    "yolo26_depth_x_768x768",
)


def test_yolo26_depth_carries_its_upstream_legal():
    by_id = {m["id"]: m for m in _models()}
    for mid in _YOLO26_DEPTH_IDS:
        assert mid in by_id, f"{mid} 가 카탈로그에서 사라졌다"
        lg = by_id[mid].get("legal") or {}
        assert lg.get("source_url") == "https://github.com/ultralytics/ultralytics", (
            f"{mid}: source_url={lg.get('source_url')!r}"
        )
        assert lg.get("license") == "AGPL-3.0", f"{mid}: license={lg.get('license')!r}"
        # With the license known as AGPL, _LICENSE_COMMERCIAL must give "copyleft", not the
        # unknown-license fallback "restricted": both mean "use with care", but for different
        # reasons, and the UI shows the reason.
        assert lg.get("commercial_use") == "copyleft", (
            f"{mid}: commercial_use={lg.get('commercial_use')!r}"
        )
        assert lg.get("copyright"), f"{mid}: copyright 가 저장소 소유자에서 파생되지 않았다"

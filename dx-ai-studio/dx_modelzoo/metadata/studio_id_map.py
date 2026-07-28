"""Map public Model Zoo artifact/display keys to dx-ai-studio catalog model IDs.

The public site keys models by ONNX/DXNN filename stems (e.g. ``deit_b_224x224``)
while the studio catalog uses ``test_models.conf`` ids (e.g. ``deit_base``).
General-network sync remaps public adapter output onto studio ids before merge.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from dx_modelzoo.metadata.normalization import canonical_model_id

# Public display labels that signature matching alone cannot disambiguate.
_DISPLAY_TO_STUDIO: dict[str, str] = {
    canonical_model_id("DeiT-Base (distilled, 384x384)"): "deit_base384_distilled",
    canonical_model_id("DeiT-Base (384x384)"): "deitbase384",
    canonical_model_id("DeiT-Base (distilled, 224x224)"): "deit_base_distilled_1",
    canonical_model_id("DeiT-Base (224x224)"): "deit_base",
    canonical_model_id("DeiT-Small (distilled)"): "deit_small_distilled",
    canonical_model_id("DeiT-Tiny (distilled)"): "deit_tiny_distilled",
    canonical_model_id("YOLOv7 (PPU)"): "yolov7_ppu",
    canonical_model_id("YOLOX-l-leaky"): "yolox_l_leaky",
    canonical_model_id("YOLOX-s-leaky"): "yolox_s_leaky",
    canonical_model_id("YOLOX-s-wide-leaky"): "yolox_s_wide_leaky",
    canonical_model_id("DAMO-YOLO TinyNAS-L20M"): "damoyolo_tinynasl20_m",
    canonical_model_id("DAMO-YOLO TinyNAS-L20T"): "damoyolo_tinynasl20_t",
    canonical_model_id("DAMO-YOLO TinyNAS-L25S"): "damoyolo_tinynasl25_s",
}

# Public ONNX release suffixes (-1 legacy, -2 TinyNAS) share GFLOPs/params with the
# classic DAMO-YOLO line — signature matching alone maps TinyNAS rows to damoyolom/s/t.
_ARTIFACT_STEM_TO_STUDIO: dict[str, str] = {
    canonical_model_id("DamoYoloM-2"): "damoyolo_tinynasl20_m",
    canonical_model_id("DamoYoloT-2"): "damoyolo_tinynasl20_t",
    canonical_model_id("DamoYoloS-2"): "damoyolo_tinynasl25_s",
    canonical_model_id("DamoYoloM-1"): "damoyolom",
    canonical_model_id("DamoYoloT-1"): "damoyolot",
    canonical_model_id("DamoYoloS-1"): "damoyolos",
    canonical_model_id("DamoYoloL-1"): "damoyolol",
    canonical_model_id("SCRFD500M_PPU"): "scrfd500m_ppu",
    canonical_model_id("YOLOV5Pose_PPU"): "yolov5pose_ppu",
    canonical_model_id("deit_b_384x384_distilled"): "deit_base384_distilled",
    canonical_model_id("deit-b_384x384_distilled"): "deit_base384_distilled",
}

_ARTIFACT_URL_FIELDS = (
    "artifacts.onnx.remote_url",
    "artifacts.qlite_dxnn.remote_url",
    "artifacts.qpro_dxnn.remote_url",
    "artifacts.qmaster_dxnn.remote_url",
)


def _studio_data_dir(suite_root: Path) -> Path:
    """Return dx_modelzoo/data regardless of cwd depth."""
    suite_root = Path(suite_root)
    candidate = suite_root / "dx-ai-studio" / "dx_modelzoo" / "data"
    if candidate.is_dir():
        return candidate
    candidate = suite_root / "dx_modelzoo" / "data"
    if candidate.is_dir():
        return candidate
    raise FileNotFoundError(f"dx_modelzoo/data not found under {suite_root}")


def _norm_resolution(value) -> str | None:
    if not value:
        return None
    parts = [p for p in str(value).lower().split("x") if p.isdigit()]
    if len(parts) >= 3 and int(parts[1]) <= 4:
        # Public site typo: 256x3x256 → 256x256x3
        w, c, h = parts[0], parts[1], parts[2]
        parts = [w, h, c]
    elif len(parts) >= 2:
        parts = parts[:3] if len(parts) >= 3 else parts + ["3"]
    if len(parts) >= 2:
        return "x".join(parts[:3] if len(parts) >= 3 else (*parts, "3"))
    return str(value).lower().strip()


def _norm_metric(value) -> str | None:
    if value in (None, ""):
        return None
    try:
        return f"{float(str(value).replace(',', '')):.4f}"
    except ValueError:
        return str(value).strip().lower()


def _model_signature(resolution, parameters, operations) -> tuple | None:
    res = _norm_resolution(resolution)
    params = _norm_metric(parameters)
    ops = _norm_metric(operations)
    if not res or not params or not ops:
        return None
    return (res, params, ops)


def load_studio_index(suite_root) -> dict:
    """Build lookup tables from bundled model_catalog.json (+ enrichment)."""
    data_dir = _studio_data_dir(Path(suite_root))
    catalog_path = data_dir / "model_catalog.json"
    enrich_path = data_dir / "model_enrichment.json"

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    enrichment = {}
    if enrich_path.is_file():
        enrichment = json.loads(enrich_path.read_text(encoding="utf-8"))

    by_key: dict[str, str] = {}
    by_signature: dict[tuple, str] = {}
    studio_ids: set[str] = set()

    def _register(studio_id: str, key: str | None) -> None:
        if not key:
            return
        canon = canonical_model_id(key)
        if not canon or canon in by_key:
            return
        by_key[canon] = studio_id

    for model in catalog.get("models", []):
        studio_id = model.get("id")
        if not studio_id:
            continue
        studio_ids.add(studio_id)
        _register(studio_id, studio_id)
        _register(studio_id, model.get("class_name"))
        model_file = model.get("model_file") or ""
        if model_file:
            _register(studio_id, Path(model_file).name)
            _register(studio_id, Path(model_file).stem)

        enrich = enrichment.get(studio_id) or {}
        spec = {**(model.get("specification") or {}), **{
            k: enrich[k] for k in ("input_resolution", "parameters", "operations") if enrich.get(k)
        }}
        sig = _model_signature(
            spec.get("input_resolution"),
            spec.get("parameters"),
            spec.get("operations"),
        )
        if sig:
            existing = by_signature.get(sig)
            if existing and existing != studio_id:
                # Ambiguous spec (e.g. damoyolom vs damoyolo_tinynasl20_m) — drop fallback.
                by_signature.pop(sig, None)
            elif sig not in by_signature:
                by_signature[sig] = studio_id

    return {
        "by_key": by_key,
        "by_signature": by_signature,
        "studio_ids": studio_ids,
    }


def resolve_studio_id(public_key: str, fields: dict, index: dict) -> str | None:
    """Resolve a public adapter key to a studio catalog id, if possible."""
    if public_key in index["studio_ids"]:
        return public_key

    by_key = index["by_key"]
    if public_key in by_key:
        return by_key[public_key]
    pub_canon = canonical_model_id(public_key)
    if pub_canon in _ARTIFACT_STEM_TO_STUDIO:
        return _ARTIFACT_STEM_TO_STUDIO[pub_canon]

    display = fields.get("display.class_name") or ""
    if display:
        canon = canonical_model_id(display)
        if canon in _DISPLAY_TO_STUDIO:
            return _DISPLAY_TO_STUDIO[canon]
        if canon in by_key:
            return by_key[canon]
        base = re.sub(r"\s*\([^)]*\)", "", display).strip()
        canon = canonical_model_id(base)
        if canon in by_key:
            return by_key[canon]

    for url_field in _ARTIFACT_URL_FIELDS:
        url = fields.get(url_field)
        if not url or url in ("-", ""):
            continue
        stem = url.rstrip("/").split("/")[-1]
        stem_key = canonical_model_id(Path(stem).stem if "." in stem else stem)
        if stem_key in _ARTIFACT_STEM_TO_STUDIO:
            return _ARTIFACT_STEM_TO_STUDIO[stem_key]
        canon = canonical_model_id(stem)
        if canon in by_key:
            return by_key[canon]

    sig = _model_signature(
        fields.get("specification.input_resolution"),
        fields.get("specification.parameters"),
        fields.get("specification.operations"),
    )
    if sig and sig in index["by_signature"]:
        return index["by_signature"][sig]

    return None


def remap_public_models(public_models: dict, index: dict) -> tuple[dict, list[str]]:
    """Re-key public adapter output from artifact ids to studio catalog ids."""
    remapped: dict[str, dict] = {}
    warnings: list[str] = []

    for pub_key, fields in public_models.items():
        studio_id = resolve_studio_id(pub_key, fields, index)
        target = studio_id or pub_key
        if studio_id is None and pub_key not in index["studio_ids"]:
            warnings.append(f"unmapped public model key: {pub_key!r} ({fields.get('display.class_name', '')})")
        if target in remapped:
            remapped[target].update(fields)
        else:
            remapped[target] = dict(fields)

    return remapped, warnings

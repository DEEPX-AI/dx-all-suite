#!/usr/bin/env python3
"""test_models.conf → model_catalog.json 자동 생성."""
import sys, json
from pathlib import Path

from dx_modelzoo.core.config import (CONFIG_FILE, CATEGORIES, EXAMPLE_TYPES, SAMPLE_IMAGES,
                          DX_APP_ROOT, DATA_DIR, CPP_DIR, PY_DIR)
from dx_modelzoo.core.catalog import parse_test_models_conf


ENRICHMENT_FILE = DATA_DIR / "model_enrichment.json"


def _load_enrichment():
    """Curated per-model enrichment (legal/spec) table.

    The generated skeleton only knows what test_models.conf carries (id, task,
    dxnn file). Legal source_url + license, exact input_resolution, params/ops
    and reference accuracy are *derived from present data* and stored here so
    they survive regeneration:
      - source_url:  the studio's own curated catalog, else the staging
                     dx-modelzoo model YAML `reference` field.
      - license:     curated catalog, else the upstream repo's license mapped
                     from the curated (source_url -> license) table.
      - resolution:  curated catalog, else dx-runtime model_registry dims,
                     else the dxnn filename.
    copyright + canonical license_text are still derived at serve time by
    core.catalog._enrich_legal from source_url + license. Models whose upstream
    declares no discoverable license are left without one (honestly unknown)
    rather than being assigned a fabricated license.
    """
    if not ENRICHMENT_FILE.exists():
        return {}
    try:
        return json.loads(ENRICHMENT_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _apply_enrichment(entry, e):
    """Merge one curated enrichment record into a generated catalog entry."""
    spec = entry["specification"]
    if e.get("input_resolution"):
        res = e["input_resolution"]
        spec["input_resolution"] = res
        parts = res.split("x")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            spec["input_width"] = int(parts[0])
            spec["input_height"] = int(parts[1])
    if e.get("parameters"):
        spec["parameters"] = e["parameters"]
    if e.get("operations"):
        spec["operations"] = e["operations"]
    if e.get("dataset"):
        spec["dataset"] = e["dataset"]
    if e.get("metric_name"):
        spec["metric"] = {"name": e["metric_name"]}
    if e.get("source_url"):
        entry["legal"]["source_url"] = e["source_url"]
    if e.get("license"):
        entry["legal"]["license"] = e["license"]
    if e.get("accuracy"):
        entry["evaluation"] = {"raw": {"accuracy": e["accuracy"]}}


def generate():
    models = parse_test_models_conf()
    if not models:
        print("[ERROR] No models found. Check CONFIG_FILE path.")
        sys.exit(1)

    enrichment = _load_enrichment()
    catalog_models = []
    for m in models:
        cat = m["category"]
        cpp_path = f"src/cpp_example/{cat}/{m['id']}/"
        py_path = f"src/python_example/{cat}/{m['id']}/"
        cpp_exists = (DX_APP_ROOT / cpp_path).is_dir() if DX_APP_ROOT.exists() else False
        py_exists = (DX_APP_ROOT / py_path).is_dir() if DX_APP_ROOT.exists() else False

        qpro_file = m["model_file"].replace("assets/models/", "assets/models/q-pro/")
        qpro_exists = (DX_APP_ROOT / qpro_file).exists() if DX_APP_ROOT.exists() else False

        entry = {
            "id": m["id"],
            "name": m["id"].replace("_", " ").title(),
            "class_name": m["id"],
            "category": cat,
            "description": {
                "en": f"{m['id']} is a {cat.replace('_', ' ')} model optimized for DEEPX NPU.",
                "ko": f"{m['id']}은(는) DEEPX NPU에 최적화된 {CATEGORIES.get(cat, {}).get('label_ko', cat)} 모델입니다.",
                "ja": f"{m['id']} は DEEPX NPU に最適化された{CATEGORIES.get(cat, {}).get('label_ja', cat)}モデルです。",
                "es": f"{m['id']} es un modelo de {CATEGORIES.get(cat, {}).get('label_es', cat).lower()} optimizado para la NPU de DEEPX.",
                "zh-CN": f"{m['id']} 是针对 DEEPX NPU 优化的{CATEGORIES.get(cat, {}).get('label_zh-CN', cat)}模型。",
                "zh-TW": f"{m['id']} 是針對 DEEPX NPU 最佳化的{CATEGORIES.get(cat, {}).get('label_zh-TW', cat)}模型。"
            },
            "specification": {
                "input_resolution": "", "ops": "", "params": "", "dataset": "",
                "metric": {}, "quantization": ["qlite"],
                "fps": "", "fps_per_watt": ""
            },
            "compile_guide": {
                "onnx_url": "", "recommended_quant": "qlite",
                "notes": {"en": "Use dxcom default settings.", "ko": "dxcom 기본 설정 사용.",
                          "ja": "dxcom のデフォルト設定を使用します。", "es": "Use la configuración predeterminada de dxcom.",
                          "zh-CN": "使用 dxcom 默认设置。", "zh-TW": "使用 dxcom 預設設定。"}
            },
            "demo": {
                "cpp_example": cpp_path if cpp_exists else "",
                "python_example": py_path if py_exists else "",
                "cli_command": f"./{m['id']}_sync -m {m['model_file']} -i {SAMPLE_IMAGES.get(cat, 'sample/img/sample_street.jpg')}"
            },
            "legal": {
                "license": "", "copyright": "", "source_url": ""
            },
            "thumbnail": f"thumbnails/{m['id']}.jpg",
            "example_images": {
                "type": EXAMPLE_TYPES.get(cat, "single"),
                "result": f"examples/{m['id']}_result.jpg",
                "original": f"examples/{m['id']}_original.jpg"
                    if EXAMPLE_TYPES.get(cat) in ("before_after", "overlay") else ""
            },
            "model_file": m["model_file"],
            "model_file_qpro": qpro_file if qpro_exists else ""
        }
        if m["id"] in enrichment:
            _apply_enrichment(entry, enrichment[m["id"]])
        catalog_models.append(entry)

    catalog = {
        "version": "1.0",
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "categories": CATEGORIES,
        "models": catalog_models
    }

    out = DATA_DIR / "model_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    print(f"[OK] Generated {out} with {len(catalog_models)} models")


if __name__ == "__main__":
    generate()

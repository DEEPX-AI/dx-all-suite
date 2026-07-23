"""DX Model Zoo — 모델 카탈로그 로드, 검색, 필터."""
import copy
import json
import re
import threading
from pathlib import Path
from collections import defaultdict

from dx_modelzoo.core.config import (CATALOG_FILE, CONFIG_FILE, CATEGORIES, EXAMPLE_TYPES,
                         DX_APP_ROOT, MODELS_DIR, CPP_DIR, PY_DIR, BUILD_DIR, DATA_DIR,
                         SAMPLE_IMAGES, MODEL_IMAGE_OVERRIDE, SAMPLE_IMG_DIR)
from shared.catalog_sources import parse_test_models_conf as _shared_parse_test_models_conf


def _resolve_sample(model_id, category):
    """Map a model to its inference sample input.

    Single-image tasks resolve to a concrete file in dx_app's sample/img (per-model
    override wins over the task default). Pair/gallery tasks (reid, embedding) and
    cross-dir configs (obb → sample/dota8_test/...) have no flat sample file, so we
    return (None, None) and the UI honestly disables the Sample tab instead of
    showing an unrelated image. Returns (sample_dir_relative, sample_filename).
    """
    raw = MODEL_IMAGE_OVERRIDE.get(model_id) or SAMPLE_IMAGES.get(category, "")
    if not raw:
        return None, None
    fname = Path(raw).name
    if (SAMPLE_IMG_DIR / fname).is_file():
        return "sample/img", fname
    return None, None


# Canonical license text reference (the source ModelZoo rarely ships the full body, but
# it's the standard SPDX text — link to the authoritative copy rather than store 280 copies).
_LICENSE_TEXT_REF = {
    "Apache-2.0": "Apache License 2.0 — https://www.apache.org/licenses/LICENSE-2.0",
    "MIT": "MIT License — https://opensource.org/license/mit",
    "GPL-3.0": "GNU General Public License v3.0 — https://www.gnu.org/licenses/gpl-3.0.html",
    "AGPL-3.0": "GNU Affero General Public License v3.0 — https://www.gnu.org/licenses/agpl-3.0.html",
    "LGPL-3.0": "GNU Lesser General Public License v3.0 — https://www.gnu.org/licenses/lgpl-3.0.html",
    "BSD-3-Clause": "BSD 3-Clause License — https://opensource.org/license/bsd-3-clause",
    "BSD 3-Clause": "BSD 3-Clause License — https://opensource.org/license/bsd-3-clause",
    "Unlicense": "The Unlicense — https://unlicense.org/",
    "CC BY-NC 4.0": "Creative Commons Attribution-NonCommercial 4.0 — https://creativecommons.org/licenses/by-nc/4.0/",
    "Non-commercial": "Non-commercial use only — see the source repository for terms",
    "No License": "No license declared by the source repository (all rights reserved by default)",
    "Public Domain": "Public domain dedication — Darknet \"YOLO LICENSE\" (no rights reserved)",
    "Apple ML Research License": "Apple proprietary research license — use/reproduce/modify/redistribute with notice retention; see the source repository LICENSE",
}

# Commercial-use classification per license, so the UI can flag models that cannot be
# used commercially. "allowed" = permissive; "copyleft" = commercial OK but share-alike
# obligations; "non-commercial" = commercial use prohibited; "restricted" = proprietary/
# custom or no declared license (all rights reserved) — review before any use.
_LICENSE_COMMERCIAL = {
    "Apache-2.0": "allowed", "MIT": "allowed", "BSD-3-Clause": "allowed",
    "BSD 3-Clause": "allowed", "Unlicense": "allowed", "Public Domain": "allowed",
    "GPL-3.0": "copyleft", "AGPL-3.0": "copyleft", "LGPL-3.0": "copyleft",
    "CC BY-NC 4.0": "non-commercial", "Non-commercial": "non-commercial",
    "Apple ML Research License": "restricted", "No License": "restricted",
}

# source-host org slug → display copyright holder (else the slug verbatim = repo owner).
_COPYRIGHT_ORG = {
    "ultralytics": "Ultralytics", "deepinsight": "InsightFace", "facebook": "Facebook",
    "facebookresearch": "Facebook",
    "google": "Google", "meituan": "Meituan", "megvii-basedetection": "Megvii",
    "thu-mig": "THU-MIG", "tinyvision": "Alibaba DAMO Academy", "snap-research": "Snap Research",
    "tianfang-zhang": "Tianfang Zhang", "wongkinyiu": "WongKinYiu",
}

# non-repo doc hosts → copyright holder (torchvision/gluon/tf/mediapipe pages).
_COPYRIGHT_HOST = {
    "pytorch.org": "PyTorch (Torch Contributors)", "cv.gluon.ai": "GluonCV",
    "www.tensorflow.org": "Google", "tensorflow.org": "Google", "ai.google.dev": "Google",
    "google.github.io": "Google",
}


def _enrich_legal(model):
    """Fill copyright + license-text reference that the ModelZoo source omitted but which are
    mechanically derivable: copyright from the source repo owner, license body from the SPDX
    id. Never overwrites already-curated values."""
    lg = model.get("legal")
    if not isinstance(lg, dict):
        return
    if not lg.get("copyright") and lg.get("source_url"):
        url = lg["source_url"]
        m = re.search(r"(?:github\.com|huggingface\.co|gitlab\.com)/([^/]+)/", url)
        if m:
            org = m.group(1)
            lg["copyright"] = _COPYRIGHT_ORG.get(org.lower(), org)
        else:
            host = re.search(r"https?://([^/]+)", url)
            if host and host.group(1).lower() in _COPYRIGHT_HOST:
                lg["copyright"] = _COPYRIGHT_HOST[host.group(1).lower()]
    if not lg.get("license_text") and lg.get("license"):
        ref = _LICENSE_TEXT_REF.get(lg["license"])
        if ref:
            lg["license_text"] = ref
    # Commercial-use classification (derived from the license) so the UI can flag models
    # whose license restricts commercial use. Unknown/undeclared license → "restricted".
    if not lg.get("commercial_use"):
        lic = lg.get("license")
        lg["commercial_use"] = _LICENSE_COMMERCIAL.get(lic, "restricted") if lic else "restricted"


_I18N_LANGS = ("en", "ko", "ja", "zh-CN", "zh-TW", "es")


def _enrich_summary(model):
    """Populate display.summary / content.use_case in all 6 languages from the model's
    curated `description` (which is fully localized). The source ModelZoo only shipped an
    English one-line summary, so cards/hero fell back to English (or blank) for ja/zh/es."""
    desc = model.get("description")
    if not isinstance(desc, dict) or not desc:
        return
    disp = model.setdefault("display", {})
    summary = disp.get("summary")
    if not isinstance(summary, dict):
        summary = {}
    for lang in _I18N_LANGS:
        if desc.get(lang):
            summary[lang] = desc[lang]
    disp["summary"] = summary


def _enrich_input_shape(model):
    """Derive technical.input_shape (NHWC, matching the .dxnn input tensor) from the
    resolved input_resolution. Done at serve time because the merge overwrites `technical`
    with the generated catalog's copy, which lacks it."""
    tech = model.get("technical")
    if not isinstance(tech, dict):
        tech = model.setdefault("technical", {})
    if tech.get("input_shape"):
        return
    res = (model.get("specification") or {}).get("input_resolution")
    if res and re.match(r"^\d+x\d+x\d+$", str(res)):
        w, h, c = (int(x) for x in str(res).split("x"))
        tech["input_shape"] = [1, h, w, c]


def _representative_input(model_id, category):
    """Full path of the input the model's representative thumbnail was generated from,
    so "Use Default" runs the demo on exactly what the catalog shows (dx_app's own
    no-image default diverges per category, so we pass this explicitly). This is a file
    for most tasks and a directory of image pairs for reid (person_pair) / embedding
    (face_pair) — the sync runner expands directories and renders the pair comparison
    (cosine similarity + SAME/DIFFERENT), exactly like dx_app's run_demo.sh.
    """
    return MODEL_IMAGE_OVERRIDE.get(model_id) or SAMPLE_IMAGES.get(category) or None


GENERATED_CATALOG_CACHE = DATA_DIR / "generated_catalog.cache.json"
GENERATED_CATALOG_JSON = DATA_DIR / "generated_catalog.json"


def parse_test_models_conf(conf_path=None):
    """test_models.conf 파싱 → [{id, name, category, model_file}, ...].

    Thin wrapper over the shared parser (shared/catalog_sources.py) — kept
    here so existing callers/imports (`from core.catalog import
    parse_test_models_conf` / `dx_modelzoo.core.catalog.parse_test_models_conf`)
    keep working, and so the missing-file warning stays dx_modelzoo-specific.
    """
    conf_path = Path(conf_path or CONFIG_FILE)
    if not conf_path.exists():
        print(f"[WARNING] test_models.conf not found: {conf_path}")
    return _shared_parse_test_models_conf(conf_path)


def load_catalog_json(catalog_path=None):
    """model_catalog.json 로드. 없으면 빈 구조 반환."""
    catalog_path = Path(catalog_path or CATALOG_FILE)
    if not catalog_path.exists():
        return {"version": "1.0", "categories": {}, "models": []}
    try:
        return json.loads(catalog_path.read_text())
    except Exception as e:
        print(f"[WARNING] Failed to load catalog: {e}")
        return {"version": "1.0", "categories": {}, "models": []}


def merge_conf_and_catalog(conf_models, catalog_data):
    """test_models.conf 기반 모델 목록에 catalog JSON 메타데이터 머지.
    conf가 source of truth (340개 모델), catalog은 부가 정보 제공."""
    catalog_map = {m["id"]: m for m in catalog_data.get("models", [])}
    merged = []
    for cm in conf_models:
        _sample_dir, _sample_img = _resolve_sample(cm["id"], cm["category"])
        base = {
            "id": cm["id"],
            "name": cm["name"],
            "class_name": cm["id"],
            "category": cm["category"],
            "description": {"en": "", "ko": ""},
            "specification": {},
            "compile_guide": {},
            "demo": _build_demo_info(cm["id"], cm["category"]),
            "variants": _detect_inference_variants(cm["id"], cm["category"]),
            "legal": {},
            "thumbnail": f"thumbnails/{cm['id']}.jpg",
            "example_images": {
                "type": EXAMPLE_TYPES.get(cm["category"], "single"),
                "result": f"examples/{cm['id']}_result.jpg",
            },
            "model_file": cm["model_file"],
            "sample_dir": _sample_dir,
            "sample_image": _sample_img,
            "demo_input": _representative_input(cm["id"], cm["category"]),
            "model_file_qpro": "",
            "downloaded": (DX_APP_ROOT / cm["model_file"]).exists() if DX_APP_ROOT.exists() else False,
            "downloaded_qlite": (DX_APP_ROOT / cm["model_file"]).exists() if DX_APP_ROOT.exists() else False,
            "downloaded_qpro": False,
        }
        if cm["id"] in catalog_map:
            cat_entry = catalog_map[cm["id"]]
            for key in ("description", "specification", "compile_guide", "legal",
                        "thumbnail", "example_images", "model_file_qpro", "evaluation"):
                if cat_entry.get(key):
                    base[key] = cat_entry[key]
            if cat_entry.get("name"):
                base["name"] = cat_entry["name"]
            if cat_entry.get("class_name"):
                base["class_name"] = cat_entry["class_name"]
        if base.get("model_file_qpro"):
            base["downloaded_qpro"] = (DX_APP_ROOT / base["model_file_qpro"]).exists() if DX_APP_ROOT.exists() else False
        merged.append(base)
    return merged


def _catalog_models_as_conf(catalog_data):
    """외부 runtime manifest가 없을 때 bundled catalog를 source of truth로 사용."""
    conf_models = []
    for model in catalog_data.get("models", []):
        model_id = model.get("id")
        if not model_id:
            continue
        conf_models.append({
            "id": model_id,
            "name": model.get("name") or model_id,
            "category": model.get("category", "unknown"),
            "model_file": model.get("model_file", ""),
        })
    return conf_models


def load_generated_catalog(cache_path=None, json_path=None):
    """생성된 카탈로그 로드. schema_version 2.0 호환성 검사."""
    for path in (cache_path or GENERATED_CATALOG_CACHE, json_path or GENERATED_CATALOG_JSON):
        path = Path(path)
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        if data.get("schema_version") != "2.0":
            continue
        return data
    return None


def _metadata_source_from_generated(generated_catalog):
    """generated catalog의 동기화 메타데이터를 모델 단위 표시용으로 변환."""
    source = {}
    if generated_catalog.get("source_profile"):
        source["source_profile"] = generated_catalog["source_profile"]
    if generated_catalog.get("generated_at"):
        source["generated_at"] = generated_catalog["generated_at"]
    return source


def _has_metadata_value(value):
    if value is None or value == "":
        return False
    if isinstance(value, (dict, list, tuple, set)):
        return bool(value)
    return True


def _merge_generated_with_legacy(generated, legacy):
    """generated 값을 기본으로 하되 legacy의 실제 값만 보존한다."""
    merged = copy.deepcopy(generated) if isinstance(generated, dict) else {}
    for key, value in (legacy or {}).items():
        if (
            isinstance(value, dict)
            and isinstance(merged.get(key), dict)
            and (_has_metadata_value(value) or _has_metadata_value(merged.get(key)))
        ):
            merged[key] = _merge_generated_with_legacy(merged[key], value)
        elif _has_metadata_value(value):
            merged[key] = value
    return merged


def _enrich_model_entry(base, enriched, metadata_source=None):
    """enriched 스키마 2.0 모델을 legacy 모델 항목에 additive merge."""
    # enriched 필드를 추가 키로 복사 (기존 legacy 키 유지)
    additive_keys = ("display", "evaluation", "performance", "artifacts",
                     "processor", "provenance", "missing", "metadata_source",
                     "content", "technical")
    for key in additive_keys:
        if key in enriched:
            base[key] = enriched[key]
    if metadata_source and "metadata_source" not in enriched:
        base["metadata_source"] = metadata_source

    # specification: enriched가 더 풍부하면 머지
    if enriched.get("specification") and not base.get("specification"):
        base["specification"] = enriched["specification"]
    elif enriched.get("specification") and base.get("specification"):
        base["specification"] = _merge_generated_with_legacy(
            enriched["specification"],
            base["specification"],
        )

    # legal: enriched와 base를 스마트 머지 (빈 문자열 필드 무시)
    # base["legal"]에 키가 있지만 값이 빈 문자열인 경우도 enriched 값으로 채워야 한다.
    if enriched.get("legal"):
        if not base.get("legal"):
            base["legal"] = enriched["legal"]
        else:
            base["legal"] = _merge_generated_with_legacy(enriched["legal"], base["legal"])

    # demo: enriched에 있으면 머지
    if enriched.get("demo"):
        if not base.get("demo"):
            base["demo"] = enriched["demo"]
        else:
            for k, v in enriched["demo"].items():
                if k not in base["demo"] or not base["demo"][k]:
                    base["demo"][k] = v

    return base


def _build_demo_info(model_id, category):
    """모델의 C++/Python 예제 경로 확인."""
    cpp_path = f"src/cpp_example/{category}/{model_id}/"
    py_path = f"src/python_example/{category}/{model_id}/"
    cpp_exists = (DX_APP_ROOT / cpp_path).is_dir() if DX_APP_ROOT.exists() else False
    py_exists = (DX_APP_ROOT / py_path).is_dir() if DX_APP_ROOT.exists() else False
    return {
        "cpp_example": cpp_path if cpp_exists else "",
        "python_example": py_path if py_exists else "",
        "cli_command": f"./{model_id}_sync -m {{}}/assets/models/{model_id}.dxnn -i sample/img/sample_street.jpg",
    }


# Python execution variants, in order, mapped to the run_inference `variant` suffix.
# cpp_postprocess variants run the Python app but offload postprocessing to the C++
# dx_postprocess pybind extension.
_PY_VARIANTS = ("sync", "async", "sync_cpp_postprocess", "async_cpp_postprocess")
_CPP_VARIANTS = ("sync", "async")


def _detect_inference_variants(model_id, category):
    """Detect which (lang, variant) execution paths actually exist for a model.

    Mirrors dx_app run_inference resolution exactly so the UI never offers a path the
    backend can't run:
      - cpp:    BUILD_DIR/<model>_<variant>                       (compiled binary)
      - python: PY_DIR/<category>/<model>/<model>_<variant>.py    (script)
    Returns e.g. {"cpp": ["sync", "async"], "python": ["sync", "async", "sync_cpp_postprocess"]}.
    Langs with no available variant are omitted.
    """
    if not DX_APP_ROOT.exists():
        return {}
    variants = {}
    cpp = [v for v in _CPP_VARIANTS if (BUILD_DIR / f"{model_id}_{v}").exists()]
    if cpp:
        variants["cpp"] = cpp
    py_dir = PY_DIR / category / model_id
    py = [v for v in _PY_VARIANTS if (py_dir / f"{model_id}_{v}.py").exists()]
    if py:
        variants["python"] = py
    return variants


MAX_PAGE_SIZE = 200
DEFAULT_PAGE_SIZE = 60
ALLOWED_SORT_FIELDS = {"name", "category", "fps", "id"}


def _parse_fps(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def sort_models(models, sort="name", direction="asc"):
    """모델 목록을 지정 필드 기준으로 정렬."""
    sort = sort if sort in ALLOWED_SORT_FIELDS else "name"
    reverse = direction == "desc"
    if sort == "fps":
        return sorted(models, key=lambda m: _parse_fps((m.get("specification") or {}).get("fps")), reverse=reverse)

    def _sort_key(m):
        val = m.get(sort)
        if val is None:
            val = m.get("id")
        if val is None:
            val = ""
        return str(val).lower()

    return sorted(models, key=_sort_key, reverse=reverse)


def paginate_models(models, page=1, page_size=DEFAULT_PAGE_SIZE):
    """모델 목록을 페이지 단위로 분할하여 반환."""
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(page_size)
    except (TypeError, ValueError):
        page_size = DEFAULT_PAGE_SIZE
    page = max(1, page)
    page_size = min(MAX_PAGE_SIZE, max(1, page_size))
    total = len(models)
    pages = max(1, (total + page_size - 1) // page_size)
    page = min(page, pages)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "models": models[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1,
    }


def query_catalog(models, category=None, search=None, sort="name", direction="asc", page=1, page_size=DEFAULT_PAGE_SIZE):
    """카테고리/검색/정렬/페이지네이션을 조합한 통합 조회."""
    filtered = filter_models(models, category=category, search=search)
    sorted_models = sort_models(filtered, sort=sort, direction="desc" if direction == "desc" else "asc")
    return paginate_models(sorted_models, page=page, page_size=page_size)


def _unique_model_key(model_id):
    """모델 ID에서 variant suffix(-숫자) 제거한 unique key를 반환."""
    value = str(model_id or "").strip()
    if not value:
        return ""
    if "-" in value:
        prefix, suffix = value.rsplit("-", 1)
        if suffix.isdigit() and prefix:
            return prefix
    return value


def catalog_stats(models):
    """카탈로그 variant/unique 개수 계산."""
    variant_count = len(models or [])
    unique_keys = {
        _unique_model_key(model.get("id"))
        for model in (models or [])
        if isinstance(model, dict) and model.get("id")
    }
    unique_model_count = len(unique_keys) if unique_keys else variant_count
    return {
        "variant_count": variant_count,
        "unique_model_count": unique_model_count,
    }


def build_catalog_view_payload(models, categories, view, **query):
    """카탈로그 card/list 응답 payload 생성."""
    filtered = filter_models(
        models,
        category=query.get("category"),
        search=query.get("search"),
    )
    stats = catalog_stats(filtered)
    result = query_catalog(
        models,
        category=query.get("category"),
        search=query.get("search"),
        sort=query.get("sort", "name"),
        direction=query.get("direction", "asc"),
        page=query.get("page", 1),
        page_size=query.get("page_size", DEFAULT_PAGE_SIZE),
    )
    return {
        "ok": True,
        "view": view,
        "models": result["models"],
        "categories": categories,
        "count": result["total"],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "pages": result["pages"],
        "has_next": result["has_next"],
        "has_prev": result["has_prev"],
        "variant_count": stats["variant_count"],
        "unique_model_count": stats["unique_model_count"],
    }


def filter_models(models, category=None, search=None):
    """카테고리 + 검색어로 필터."""
    result = models
    if category:
        cats = [c.strip() for c in category.split(",")]
        result = [m for m in result if m.get("category") in cats]
    if search:
        q = search.lower()
        result = [m for m in result if q in m.get("id", "").lower()
                  or q in m.get("name", "").lower()
                  or q in m.get("class_name", "").lower()]
    return result


def get_model(models, model_id):
    """ID로 모델 조회."""
    for m in models:
        if m.get("id") == model_id:
            return m
    return None


def count_by_category(models):
    """카테고리별 모델 수."""
    counts = defaultdict(int)
    for m in models:
        counts[m.get("category", "unknown")] += 1
    return dict(counts)


_catalog_cache = None
_catalog_lock = threading.RLock()


def get_catalog():
    """캐시된 카탈로그 반환. 없으면 로드. RLock으로 동시 reload 방지."""
    global _catalog_cache
    with _catalog_lock:
        if _catalog_cache is None:
            reload_catalog()  # RLock은 재진입 가능 — 같은 스레드에서 안전
        return _catalog_cache


def reload_catalog():
    """카탈로그 다시 로드. 생성된 카탈로그가 있으면 enriched 필드 추가."""
    global _catalog_cache
    catalog_data = load_catalog_json()
    conf_models = parse_test_models_conf()
    if not conf_models:
        conf_models = _catalog_models_as_conf(catalog_data)
    merged = merge_conf_and_catalog(conf_models, catalog_data)

    # 생성된 카탈로그(schema 2.0) 로드 및 enriched 필드 병합
    generated = load_generated_catalog()
    if generated is not None:
        gen_map = {m["id"]: m for m in generated.get("models", [])}
        metadata_source = _metadata_source_from_generated(generated)
        for model in merged:
            enriched = gen_map.get(model["id"])
            if enriched:
                _enrich_model_entry(model, enriched, metadata_source=metadata_source)
        # 기본 processor/specification 보장 (생성된 카탈로그에 없는 모델용)
        for model in merged:
            model.setdefault("processor", {"supported_devices": [], "status": "metadata_pending"})
            model.setdefault("specification", {})
    else:
        # 생성된 카탈로그 없어도 기본 processor/specification 보장
        for model in merged:
            model.setdefault("processor", {"supported_devices": [], "status": "metadata_pending"})
            model.setdefault("specification", {})

    for model in merged:
        _enrich_legal(model)
        _enrich_input_shape(model)
        _enrich_summary(model)
    next_cache = {
        "models": merged,
        "categories": CATEGORIES,
        "count": len(merged),
    }
    with _catalog_lock:
        _catalog_cache = next_cache
    print(f"[{__name__}] Loaded {len(merged)} models, {len(CATEGORIES)} categories"
          + (", enriched from generated catalog" if generated else ""))
    return next_cache


def apply_generated_catalog(generated_catalog):
    """생성된 카탈로그를 현재 in-memory 카탈로그에 적용 (파일 I/O 없이)."""
    global _catalog_cache
    if not isinstance(generated_catalog, dict) or generated_catalog.get("schema_version") != "2.0":
        return
    gen_map = {m["id"]: m for m in generated_catalog.get("models", [])}
    metadata_source = _metadata_source_from_generated(generated_catalog)
    with _catalog_lock:
        if _catalog_cache is None:
            return
        next_models = []
        for model in _catalog_cache["models"]:
            next_model = copy.deepcopy(model)
            enriched = gen_map.get(next_model["id"])
            if enriched:
                _enrich_model_entry(next_model, enriched, metadata_source=metadata_source)
            _enrich_legal(next_model)
            _enrich_input_shape(next_model)
            _enrich_summary(next_model)
            next_models.append(next_model)
        _catalog_cache = {
            **_catalog_cache,
            "models": next_models,
            "count": len(next_models),
        }

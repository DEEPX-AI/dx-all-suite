"""DX Model Zoo — 모델 카탈로그 로드, 검색, 필터."""
import copy
import json
import re
import threading
import time
from pathlib import Path
from collections import defaultdict

from dx_modelzoo.core.config import (CATALOG_FILE, CONFIG_FILE, CATEGORIES, EXAMPLE_TYPES,
                         DX_APP_ROOT, MODELS_DIR, CPP_DIR, PY_DIR, BUILD_DIR, DATA_DIR,
                         SAMPLE_IMAGES, MODEL_IMAGE_OVERRIDE, SAMPLE_IMG_DIR)
from dx_modelzoo.core.postprocessor_paths import resolve_postprocessor_path
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
    p = Path(raw)
    fname = p.name
    # Pair/gallery tasks and cross-dir inputs have no flat sample/img file.
    if not p.suffix:
        return None, None
    if str(raw).startswith("sample/img/"):
        return "sample/img", fname
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
    "Apple Sample Code License": "Apple Sample Code License — see https://developer.apple.com/sample-code/ (permissive sample redistribution with attribution)",
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
    "Apple Sample Code License": "allowed",
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
    "paddle-imagenet-models-name.bj.bcebos.com": "PaddlePaddle (Baidu)",
    "docs.ultralytics.com": "Ultralytics",
}


_LICENSE_ALIASES = {"Apache 2.0": "Apache-2.0", "Apache License 2.0": "Apache-2.0", "MIT License": "MIT"}


def _enrich_legal(model):
    """Fill copyright + license-text reference that the ModelZoo source omitted but which are
    mechanically derivable: copyright from the source repo owner, license body from the SPDX
    id. Never overwrites already-curated values."""
    lg = model.get("legal")
    if not isinstance(lg, dict):
        return
    # page 가 출처를 "No Reference" 로 적은 model — 지어내지 않고 비워 둔다 (화면은 'Not provided by source').
    # publish_only row 든 per-model conf row 든 (계약: test_legal_enrich.py)
    if str(lg.get("source_url") or "").strip().lower() in ("no reference", "-"):
        lg["source_url"] = ""
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
    # publish page 는 같은 license 를 다른 글자로 적기도 한다 ("Apache 2.0") — SPDX id 로
    if lg.get("license") in _LICENSE_ALIASES:
        lg["license"] = _LICENSE_ALIASES[lg["license"]]
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


def _enrich_input_resolution(model):
    """Fill specification.input_{width,height} from the .dxnn filename when the
    official sync carried no spec at all.

    Source-derived models (present in the dx_app tree but not yet in the ModelZoo
    sync snapshot — e.g. the yolo26-depth family) arrive with `specification: {}`,
    so the catalog showed no resolution for them. The resolution is right there in
    the artifact name: `yolo26-depth-n_768x768.dxnn`.

    Only width/height are derived. The channel count is NOT guessed: the other 347
    models report `WxHxC` because dx_engine read the real input tensor, and inventing
    a `x3` here would fabricate a fact rather than fill a gap. Once dx_engine can
    introspect the .dxnn at sync time, this fallback becomes redundant.
    """
    spec = model.get("specification")
    if not isinstance(spec, dict):
        spec = model.setdefault("specification", {})
    if spec.get("input_resolution") or spec.get("input_width"):
        return
    match = re.search(r"_(\d+)x(\d+)(?:[._]|$)", model.get("model_file") or "")
    if not match:
        return
    spec["input_width"] = int(match.group(1))
    spec["input_height"] = int(match.group(2))


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


def _enrich_postprocessor(model):
    """Fill technical.postprocessor with a dx_app source path when official sync has none."""
    tech = model.setdefault("technical", {})
    current = tech.get("postprocessor")
    if isinstance(current, str) and current.startswith("dx_app/"):
        return
    path = resolve_postprocessor_path(model)
    if path:
        tech["postprocessor"] = path


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
    rows = _shared_parse_test_models_conf(conf_path)
    # per-model dx_app: conf 의 task 와 예제 폴더가 다를 때가 있다 (repvgg-a0-reid — conf image_classification,
    # 예제 · registry person_reid). 돌아가는 방식은 예제 폴더가 정한다 (계약: test_catalog.py).
    if any(r.get("variant") for r in rows) and DX_APP_ROOT.exists():
        from shared import dx_app_layout as _layout
        task_of = {e.name: e.task for e in _layout.examples(DX_APP_ROOT)} \
            if _layout.detect(DX_APP_ROOT) == _layout.PER_MODEL else {}
        for r in rows:
            t = task_of.get(r.get("variant"))
            if t and t != r["category"]:
                r["category"] = t
    return rows


def conf_ids_from_generated(conf_models, generated, curated_ids=(), unpublished=()):
    """per-model test_models.conf 의 줄 (id = variant = .dxnn 이름) 을 Model Zoo 의 id 로 — 같은 .dxnn 을 가리키는
    generated catalog 항목의 id (curated id 또는 stem key). task 는 짝이 있으면 옛 key (Model Zoo 의 무리와 같이)."""
    from shared.tasks import legacy

    def key(name):   # 파일 이름의 stem → 비교용 key (확장자 · 대소문자 · 구분 기호를 접는다)
        name = re.sub(r"\.(dxnn|onnx|json)$", "", str(name or "").rsplit("/", 1)[-1], flags=re.I)
        return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")

    by_key = {}
    for gm in (generated or {}).get("models", []):
        gid = gm.get("id")
        for art in (gm.get("artifacts") or {}).values():      # .dxnn 이 없고 onnx 만 있는 model 도 (BEiT …)
            url = (art or {}).get("remote_url") or ""
            if url.endswith((".dxnn", ".onnx")):
                by_key.setdefault(key(url), gid)
        by_key.setdefault(key(gid), gid)
    for cid in curated_ids:                                    # SCRFD500M_PPU.dxnn ↔ scrfd500m_ppu (page 에 없다)
        by_key.setdefault(key(cid), cid)
    curated = set(curated_ids)
    out = []
    for cm in conf_models:
        if not cm.get("variant"):
            # main 의 3 열 줄: curated catalog 에 없는 id (yolo26_depth_n …) 는 같은 .dxnn 의 id 로 — dx_app 판에 따라
            # id 가 달라지면 그림 (thumbnails/<id>.jpg) 을 찾지 못한다
            mid = by_key.get(key(cm.get("model_file"))) if cm["id"] not in curated else None
            out.append(dict(cm, id=mid, name=mid) if mid else cm)
            continue
        if cm["variant"] in unpublished:                       # 아직 받을 수 없는 model (registry published:false)
            continue
        mid = by_key.get(key(cm.get("model_file"))) or cm["id"]
        out.append(dict(cm, id=mid, name=mid if mid != cm["id"] else cm["name"], category=legacy(cm["category"])))
    return out


def _unpublished_variants():
    """per-model dx_app registry 의 published:false (지금은 vit-l-p16_512x512_swag 하나)."""
    try:
        rows = json.loads((DX_APP_ROOT / "config" / "model_registry.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {r.get("variant") for r in rows if isinstance(r, dict) and r.get("variant") and r.get("published") is False}


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
            "demo": _build_demo_info(cm["id"], cm["category"], cm.get("model_file", ""),
                                     _representative_input(cm["id"], cm["category"])),
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


# Public ModelZoo ids carry quant / instance suffixes (_q_lite / _q_pro / _q_master / _1) that
# the local catalog ids don't, so an exact-id merge left many models unenriched ("update
# pending" for fps, fps/watt, artifacts, …). Match exact first, then the local id + a KNOWN
# suffix — directional so meaningful resolution variants (e.g. *_1280) are never collapsed.
_GEN_ID_SUFFIXES = ("_q_lite", "_q_pro", "_q_master", "_1")

# 해상도 접미사(768x768 등)는 위 화이트리스트에 없다. 그래서 studio 의
# `yolo26_depth_n` 이 생성 카탈로그의 `yolo26_depth_n_768x768` 을 못 찾아 legal 이
# 통째로 비어 있었다. 화이트리스트에 해상도를 하나씩 더하는 대신, 후보가 **유일할
# 때만** 접는다 — 위 주석이 지키려던 것은 "foo 와 foo_1280 을 섞지 않는다" 이고,
# 후보가 둘 이상이면 그 위험이 실재하므로 그때는 매칭하지 않는다.
# 계약: tests/dx_modelzoo/test_generated_id_match.py
_RES_SUFFIX = re.compile(r"^\d+x\d+$")

def _match_generated(model_id, gen_map):
    g = gen_map.get(model_id)
    if g is not None:
        return g
    for suf in _GEN_ID_SUFFIXES:
        g = gen_map.get(model_id + suf)
        if g is not None:
            return g
    prefix = model_id + "_"
    cands = [
        k for k in gen_map
        if k.startswith(prefix) and _RES_SUFFIX.match(k[len(prefix):])
    ]
    if len(cands) == 1:
        return gen_map[cands[0]]
    return None


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
    # 사람이 정한 이름 — model_catalog.json 의 이름은 id 를 기계적으로 펼친 것이라 'Regnety16Gf' ·
    # '3Ddfa V2 Mobilnet0 5 120X120' 처럼 깨졌다 (2026-10-11 matrix). generated 의 display.name 이 있으면 그것.
    display_name = (enriched.get("display") or {}).get("name")
    if display_name:
        base["name"] = display_name

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

    # Model Zoo 2_5_0 만 있는 model 은 container v9 — 이 PC 의 DX-RT 가 못 읽으면 필요한 판을 단다
    # (spec 2026-10-01 dx_app per-model layout 결정 5). 2_4_0 이 있는 model 의 URL 은 local manifest 의 2_4_0 이다.
    from shared import dxrt as _dxrt
    qlite_url = ((base.get("artifacts") or {}).get("qlite_dxnn") or {}).get("remote_url") or ""
    need = _dxrt.needs_for(9) if _dxrt.is_v9_only(qlite_url) else None
    if need:
        base["requires_dxrt"] = need
    else:
        base.pop("requires_dxrt", None)

    return base


def _build_demo_info(model_id, category, model_file="", demo_input=None):
    """모델의 dx_app C++/Python 예제 경로와, 그대로 돌아가는 CLI 명령 (dx_app 폴더에서).

    예전에는 카탈로그 id 로 './yolo26n_sync -m {}/assets/models/yolo26n.dxnn -i sample/img/sample_street.jpg'
    를 모든 모델에 만들었다 — 글자 그대로의 '{}', 없는 binary · 모델 이름, 점구름 · ReID 모델에도 거리 사진
    (2026-10-02 release audit Z-4). 예제를 layout resolver 로 찾고, 없으면 명령을 내지 않는다 (탭이 숨는다)."""
    out = {"cpp_example": "", "python_example": "", "cli_command": ""}
    if not DX_APP_ROOT.exists():
        return out
    from shared import dx_app_layout as _layout
    name = _layout.example_name(DX_APP_ROOT, category, model_id, model_file)
    ex = _layout.find(DX_APP_ROOT, category, name)
    if ex is None:
        hits = [e for e in _layout.examples(DX_APP_ROOT) if e.name == name]
        ex = hits[0] if len(hits) == 1 else None
    if ex is None:
        return out
    for lang, key in (("cpp", "cpp_example"), ("python", "python_example")):
        d = ex.dir(lang)
        if d is not None and d.is_dir():
            out[key] = str(d.relative_to(DX_APP_ROOT)) + "/"
    mf = model_file if str(model_file).startswith("assets/") else f"assets/models/{Path(model_file).name or ex.name + '.dxnn'}"
    run = f"./bin/{ex.name}_sync -m {mf}" + (f" -i {demo_input}" if demo_input else "")
    # bin/ 에 없을 수 있다 (build.sh --minimal 은 run_demo 대상만) — 그 모델만 빌드하는 줄을 먼저 보인다
    out["cli_command"] = (f"cd dx-runtime/dx_app\n"
                          f"./build.sh --target {ex.name}_sync   # once, if bin/ has no {ex.name}_sync\n"
                          f"{run}")
    return out


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


_flags_checked_at = 0.0
_FLAGS_TTL_S = 2.0


def _model_on_disk(model_file):
    if not model_file:
        return False
    try:
        from shared.dx_app_layout import find_model
        from shared.paths import SUITE_ROOT
        return find_model(model_file, DX_APP_ROOT, SUITE_ROOT) is not None
    except Exception:
        return False


def _refresh_download_flags(catalog):
    """downloaded* 는 디스크를 따른다 — 예전에는 처음 읽을 때 한 번 계산해 영원히 캐시해서, 상세 화면에서 받은 모델이
    다시 불러도 '먼저 다운로드' 로 남고 Run Inference 가 잠겨 있었다 (2026-10-02 release audit Z-2).
    assets/models 와 workspace/res/models 를 dx_app 과 같은 규칙 (shared.dx_app_layout.find_model) 으로 본다."""
    for m in (catalog or {}).get("models", []):
        qlite = _model_on_disk(m.get("model_file"))
        m["downloaded"] = m["downloaded_qlite"] = qlite
        m["downloaded_qpro"] = _model_on_disk(m.get("model_file_qpro"))


def get_catalog():
    """캐시된 카탈로그 반환. 없으면 로드. RLock으로 동시 reload 방지. 다운로드 여부는 2초마다 다시 본다."""
    global _catalog_cache, _flags_checked_at
    with _catalog_lock:
        if _catalog_cache is None:
            reload_catalog()  # RLock은 재진입 가능 — 같은 스레드에서 안전
        now = time.time()
        if now - _flags_checked_at >= _FLAGS_TTL_S:
            _flags_checked_at = now
            _refresh_download_flags(_catalog_cache)
        return _catalog_cache


# 같은 모델이 다른 이름으로 찍혀 있는 그림 (BEiT-L/16 384 = beit_large_patch16). 다른 모델의 그림은 빌리지 않는다.
_MEDIA_ALIAS = {"beit_l_p16_384x384": "beit_large_patch16"}


def _settle_media(model):
    """있는 그림만 가리킨다 — 없는 파일을 가리키면 목록을 열 때마다 모델마다 404 가 세 번 났다 (2026-10-02 Z-5).
    그림이 없으면 카드는 task 아이콘, 상세는 'Run inference' 안내를 보인다."""
    alias = _MEDIA_ALIAS.get(model.get("id"))
    thumb = model.get("thumbnail")
    if thumb and not (DATA_DIR / thumb).is_file():
        alt = f"thumbnails/{alias}.jpg" if alias else None
        model["thumbnail"] = alt if alt and (DATA_DIR / alt).is_file() else None
    ex = model.get("example_images")
    if isinstance(ex, dict):
        for key in ("result", "original"):
            path = ex.get(key)
            if path and not (DATA_DIR / path).is_file():
                alt = f"examples/{alias}_{key}.jpg" if alias else None
                if alt and (DATA_DIR / alt).is_file():
                    ex[key] = alt
                else:
                    ex.pop(key, None)


def reload_catalog():
    """카탈로그 다시 로드. 생성된 카탈로그가 있으면 enriched 필드 추가."""
    global _catalog_cache
    catalog_data = load_catalog_json()
    conf_models = parse_test_models_conf()
    if not conf_models:
        conf_models = _catalog_models_as_conf(catalog_data)
    generated = load_generated_catalog()
    conf_models = conf_ids_from_generated(conf_models, generated,
                                          curated_ids=[m.get("id") for m in catalog_data.get("models", [])],
                                          unpublished=_unpublished_variants())
    merged = merge_conf_and_catalog(conf_models, catalog_data)

    # 생성된 카탈로그(schema 2.0) 로드 및 enriched 필드 병합
    if generated is not None:
        gen_map = {m["id"]: m for m in generated.get("models", [])}
        metadata_source = _metadata_source_from_generated(generated)
        used = set()
        for model in merged:
            enriched = _match_generated(model["id"], gen_map)
            if enriched:
                used.add(enriched.get("id"))
                _enrich_model_entry(model, enriched, metadata_source=metadata_source)
        # publish page 에만 있는 model (dx_app per-model layout 과 함께 온 새 model, spec 2026-10-01 결정 8) 도 목록에 —
        # 예전에는 curated catalog 에 없는 model 은 보강만 되고 목록에 들지 않았다. 아는 task 인 것만.
        merged.extend(_generated_only_models(generated, used, metadata_source))
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
        _enrich_input_resolution(model)
        _enrich_input_shape(model)
        _enrich_postprocessor(model)
        _enrich_summary(model)
    for model in merged:
        _settle_media(model)
    next_cache = {
        "models": merged,
        "categories": CATEGORIES,
        "count": len(merged),
    }
    # 이 목록이 언제·무엇으로부터 만들어졌는지. 값은 늘 파일에 있었지만 개별 모델의
    # 상세 화면에만 닿았다 — 정작 "이 목록 전체가 낡았나" 를 묻는 자리인 목록 화면은
    # 알 수 없었고, 그래서 8일 묵은 카탈로그가 조용히 서빙됐다(2026-09-16).
    # 계약: tests/dx_modelzoo/test_catalog_freshness.py
    if generated:
        for key in ("generated_at", "source_profile"):
            if generated.get(key):
                next_cache[key] = generated[key]
    with _catalog_lock:
        _catalog_cache = next_cache
    print(f"[{__name__}] Loaded {len(merged)} models, {len(CATEGORIES)} categories"
          + (", enriched from generated catalog" if generated else ""))
    return next_cache


def _generated_only_models(generated, used_ids, metadata_source):
    """generated catalog 에만 있는 model → 목록 항목 (curated 항목과 같은 모양)."""
    out = []
    for gm in generated.get("models", []):
        mid = gm.get("id")
        task = (gm.get("display") or {}).get("task") or ""
        if not mid or mid in used_ids or task not in CATEGORIES:
            continue
        url = ((gm.get("artifacts") or {}).get("qlite_dxnn") or {}).get("remote_url") or ""
        fname = url.rstrip("/").rsplit("/", 1)[-1] if url.endswith(".dxnn") else f"{mid}.dxnn"
        entry = merge_conf_and_catalog([{"id": mid, "name": (gm.get("display") or {}).get("name") or mid,
                                         "category": task, "model_file": f"assets/models/{fname}"}],
                                       {"models": []})[0]
        _enrich_model_entry(entry, gm, metadata_source=metadata_source)
        # 출처 'No Reference' 는 _enrich_legal 이 비운다
        entry["publish_only"] = True     # 지금의 dx_app 에는 예제가 없다 — per-model layout 과 함께 온다
        out.append(entry)
    return out


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
            enriched = _match_generated(next_model["id"], gen_map)
            if enriched:
                _enrich_model_entry(next_model, enriched, metadata_source=metadata_source)
            _enrich_legal(next_model)
            _enrich_input_shape(next_model)
            _enrich_postprocessor(next_model)
            _enrich_summary(next_model)
            _settle_media(next_model)
            next_models.append(next_model)
        _catalog_cache = {
            **_catalog_cache,
            "models": next_models,
            "count": len(next_models),
        }

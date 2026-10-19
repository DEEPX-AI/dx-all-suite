"""DX Model Zoo — load, search and filter the model catalog."""
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
    # The publish page marks some sources "No Reference" — leave the field empty rather than invent one
    # (the UI shows 'Not provided by source'). Applies to publish_only and per-model conf rows alike.
    # Contract: tests/dx_modelzoo/test_legal_enrich.py
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
    # The publish page sometimes spells a license differently ("Apache 2.0") — normalize to the SPDX id
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
    # Descriptions open with the id ('3ddfa_v2_mobilnet0_5_120x120 is a …') — use the published name, as on the card
    mid, name = model.get("id") or "", model.get("name") or ""
    for lang in _I18N_LANGS:
        text = desc.get(lang)
        if text:
            if mid and name and name != mid and text.startswith(mid):
                text = name + text[len(mid):]
                desc[lang] = text
            summary[lang] = text
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
    """Parse test_models.conf → [{id, name, category, model_file}, ...].

    Thin wrapper over the shared parser (shared/catalog_sources.py) — kept
    here so existing callers/imports (`from core.catalog import
    parse_test_models_conf` / `dx_modelzoo.core.catalog.parse_test_models_conf`)
    keep working, and so the missing-file warning stays dx_modelzoo-specific.
    """
    conf_path = Path(conf_path or CONFIG_FILE)
    if not conf_path.exists():
        print(f"[WARNING] test_models.conf not found: {conf_path}")
    rows = _shared_parse_test_models_conf(conf_path)
    # Per-model dx_app: the conf task can differ from the example folder (repvgg-a0-reid — conf says
    # image_classification, example and registry say person_reid). The example folder decides how it runs.
    # Contract: tests/dx_modelzoo/test_catalog.py
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
    """Map per-model test_models.conf rows (id = variant = .dxnn name) to Model Zoo ids — the id of the generated
    catalog entry that points at the same .dxnn (curated id or stem key). The task becomes the legacy key when one
    exists, so the model groups with the rest of the Model Zoo."""
    from shared.tasks import legacy

    def key(name):   # file stem → comparison key (folds extension, case and separators)
        name = re.sub(r"\.(dxnn|onnx|json)$", "", str(name or "").rsplit("/", 1)[-1], flags=re.I)
        return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")

    by_key = {}
    for gm in (generated or {}).get("models", []):
        gid = gm.get("id")
        for art in (gm.get("artifacts") or {}).values():      # also models with only an onnx, no .dxnn (BEiT …)
            url = (art or {}).get("remote_url") or ""
            if url.endswith((".dxnn", ".onnx")):
                by_key.setdefault(key(url), gid)
        by_key.setdefault(key(gid), gid)
    for cid in curated_ids:                                    # SCRFD500M_PPU.dxnn ↔ scrfd500m_ppu (not on the page)
        by_key.setdefault(key(cid), cid)
    curated = set(curated_ids)
    out = []
    for cm in conf_models:
        if not cm.get("variant"):
            # 3-column conf row: an id missing from the curated catalog (yolo26_depth_n …) takes the id of the same
            # .dxnn — otherwise an id that differs between dx_app versions loses its thumbnail (thumbnails/<id>.jpg)
            mid = by_key.get(key(cm.get("model_file"))) if cm["id"] not in curated else None
            out.append(dict(cm, id=mid, name=mid) if mid else cm)
            continue
        if cm["variant"] in unpublished:                       # not downloadable yet (registry published:false)
            continue
        mid = by_key.get(key(cm.get("model_file"))) or cm["id"]
        out.append(dict(cm, id=mid, name=mid if mid != cm["id"] else cm["name"], category=legacy(cm["category"])))
    return out


def _unpublished_variants():
    """Variants marked published:false in the per-model dx_app registry."""
    try:
        rows = json.loads((DX_APP_ROOT / "config" / "model_registry.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {r.get("variant") for r in rows if isinstance(r, dict) and r.get("variant") and r.get("published") is False}


def load_catalog_json(catalog_path=None):
    """Load model_catalog.json; return an empty structure if it is missing."""
    catalog_path = Path(catalog_path or CATALOG_FILE)
    if not catalog_path.exists():
        return {"version": "1.0", "categories": {}, "models": []}
    try:
        return json.loads(catalog_path.read_text())
    except Exception as e:
        print(f"[WARNING] Failed to load catalog: {e}")
        return {"version": "1.0", "categories": {}, "models": []}


def merge_conf_and_catalog(conf_models, catalog_data):
    """Merge catalog JSON metadata into the model list from test_models.conf.
    The conf is the source of truth for which models exist; the catalog adds detail."""
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
            "variants": _detect_inference_variants(cm["id"], cm["category"], cm.get("model_file", "")),
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
    """Use the bundled catalog as the source of truth when there is no external runtime manifest."""
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
    """Load the generated catalog (schema_version 2.0 only).

    When both the cache and the JSON exist, the most recently written one wins: a stale cache must not hide a
    newer generated_catalog.json (e.g. one with corrected display names). Sync writes both, so after a sync
    either one gives the same result."""
    found = []
    for path in (cache_path or GENERATED_CATALOG_CACHE, json_path or GENERATED_CATALOG_JSON):
        path = Path(path)
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            mtime = path.stat().st_mtime
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        if data.get("schema_version") != "2.0":
            continue
        found.append((mtime, data))
    if not found:
        return None
    return max(found, key=lambda item: item[0])[1]


def _metadata_source_from_generated(generated_catalog):
    """Turn the generated catalog's sync metadata into a per-model display block."""
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

# Resolution suffixes (768x768 etc.) are not in the list above, so `yolo26_depth_n` would not find
# `yolo26_depth_n_768x768` in the generated catalog and its legal block stayed empty. Instead of listing
# resolutions, fold a resolution suffix only when the candidate is UNIQUE — the rule above exists to keep
# foo and foo_1280 apart, and with more than one candidate that risk is real, so no match is made.
# Contract: tests/dx_modelzoo/test_generated_id_match.py
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
    """Take the generated values as the base, keeping only legacy values that are actually set."""
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
    """Additively merge an enriched schema 2.0 model into a legacy model entry."""
    # Copy enriched fields as extra keys (existing legacy keys stay)
    additive_keys = ("display", "evaluation", "performance", "artifacts",
                     "processor", "provenance", "missing", "metadata_source",
                     "content", "technical")
    for key in additive_keys:
        if key in enriched:
            base[key] = enriched[key]
    if metadata_source and "metadata_source" not in enriched:
        base["metadata_source"] = metadata_source
    # Human-chosen name — model_catalog.json names are mechanically expanded ids and come out broken
    # ('Regnety16Gf', '3Ddfa V2 Mobilnet0 5 120X120'). Prefer the generated display.name when present.
    display_name = (enriched.get("display") or {}).get("name")
    if display_name:
        base["name"] = display_name

    # specification: merge when the enriched copy is richer
    if enriched.get("specification") and not base.get("specification"):
        base["specification"] = enriched["specification"]
    elif enriched.get("specification") and base.get("specification"):
        base["specification"] = _merge_generated_with_legacy(
            enriched["specification"],
            base["specification"],
        )

    # legal: merge enriched and base, ignoring empty-string fields — a key present in base["legal"]
    # with an empty value must still be filled from enriched.
    if enriched.get("legal"):
        if not base.get("legal"):
            base["legal"] = enriched["legal"]
        else:
            base["legal"] = _merge_generated_with_legacy(enriched["legal"], base["legal"])

    # demo: merge when enriched has one
    if enriched.get("demo"):
        if not base.get("demo"):
            base["demo"] = enriched["demo"]
        else:
            for k, v in enriched["demo"].items():
                if k not in base["demo"] or not base["demo"][k]:
                    base["demo"][k] = v

    # Models published only as Model Zoo 2_5_0 are container v9 — if this PC's DX-RT cannot read them, attach
    # the DX-RT version they need. Models that also have 2_4_0 use the 2_4_0 URL from the local manifest.
    from shared import dxrt as _dxrt
    qlite_url = ((base.get("artifacts") or {}).get("qlite_dxnn") or {}).get("remote_url") or ""
    need = _dxrt.needs_for(9) if _dxrt.is_v9_only(qlite_url) else None
    if need:
        base["requires_dxrt"] = need
    else:
        base.pop("requires_dxrt", None)

    return base


def _build_demo_info(model_id, category, model_file="", demo_input=None):
    """The model's dx_app C++/Python example paths and a CLI command that runs as-is (from the dx_app folder).

    The example is found with the layout resolver; if there is none, no command is produced (the tab hides)
    rather than guessing a binary, model name or input image."""
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
    # The binary may be missing from bin/ (build.sh --minimal builds only run_demo targets), so the
    # command starts with the line that builds just this model
    out["cli_command"] = (f"cd dx-runtime/dx_app\n"
                          f"./build.sh --target {ex.name}_sync   # once, if bin/ has no {ex.name}_sync\n"
                          f"{run}")
    return out


# Python execution variants, in order, mapped to the run_inference `variant` suffix.
# cpp_postprocess variants run the Python app but offload postprocessing to the C++
# dx_postprocess pybind extension.
_PY_VARIANTS = ("sync", "async", "sync_cpp_postprocess", "async_cpp_postprocess")
_CPP_VARIANTS = ("sync", "async")


def _detect_inference_variants(model_id, category, model_file=""):
    """Detect which (lang, variant) execution paths actually exist for a model.

    Mirrors dx_app run_inference resolution exactly so the UI never offers a path the
    backend can't run:
      - cpp:    BUILD_DIR/<example>_<variant>                     (compiled binary)
      - python: <example dir>/<example>_<variant>.py              (script)
    <example> is resolved like dx_app does (shared.dx_app_layout): the catalog id, else the
    .dxnn stem, else the registry variant. A flat PY_DIR/<category>/<id> lookup finds
    nothing in the per-model layout (object_detection/yolo26/yolo26-n_640x640/) and would
    leave only an unbuilt C++ binary ("Binary not found").
    Returns e.g. {"cpp": ["sync", "async"], "python": ["sync", "async", "sync_cpp_postprocess"]}.
    Langs with no available variant are omitted.
    """
    if not DX_APP_ROOT.exists():
        return {}
    from shared import dx_app_layout as _layout
    name = _layout.example_name(DX_APP_ROOT, category, model_id, model_file or "")
    variants = {}
    cpp = [v for v in _CPP_VARIANTS if _layout.cpp_binary(BUILD_DIR, name, v).exists()]
    if cpp:
        variants["cpp"] = cpp
    py = [v for v in _PY_VARIANTS if _layout.python_script(DX_APP_ROOT, category, name, v).is_file()]
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
    """Sort models by the given field."""
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
    """Return one page of the model list."""
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
    """Combined lookup: category, search, sort and pagination."""
    filtered = filter_models(models, category=category, search=search)
    sorted_models = sort_models(filtered, sort=sort, direction="desc" if direction == "desc" else "asc")
    return paginate_models(sorted_models, page=page, page_size=page_size)


def _unique_model_key(model_id):
    """Return the unique key of a model id: the id without a numeric variant suffix (-N)."""
    value = str(model_id or "").strip()
    if not value:
        return ""
    if "-" in value:
        prefix, suffix = value.rsplit("-", 1)
        if suffix.isdigit() and prefix:
            return prefix
    return value


def catalog_stats(models):
    """Count catalog variants and unique models."""
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
    """Build the catalog card/list response payload."""
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
    """Filter by category and search text."""
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
    """Look up a model by id."""
    for m in models:
        if m.get("id") == model_id:
            return m
    return None


def count_by_category(models):
    """Model count per category."""
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
    """The downloaded* flags follow the disk, so a model downloaded from the detail page unlocks Run Inference
    on the next load instead of staying "download first" for the life of the cache.
    Looks in assets/models and workspace/res/models with the same rule as dx_app (shared.dx_app_layout.find_model)."""
    for m in (catalog or {}).get("models", []):
        qlite = _model_on_disk(m.get("model_file"))
        m["downloaded"] = m["downloaded_qlite"] = qlite
        m["downloaded_qpro"] = _model_on_disk(m.get("model_file_qpro"))


def get_catalog():
    """Return the cached catalog, loading it if needed. The RLock prevents concurrent reloads; download flags are
    re-checked every 2 seconds."""
    global _catalog_cache, _flags_checked_at
    with _catalog_lock:
        if _catalog_cache is None:
            reload_catalog()  # the RLock is re-entrant — safe from the same thread
        now = time.time()
        if now - _flags_checked_at >= _FLAGS_TTL_S:
            _flags_checked_at = now
            _refresh_download_flags(_catalog_cache)
        return _catalog_cache


# Images published under another name for the same model (BEiT-L/16 384 = beit_large_patch16). Never borrow
# another model's images.
_MEDIA_ALIAS = {"beit_l_p16_384x384": "beit_large_patch16"}


def _media_exists(path):
    source = DATA_DIR / path
    if source.is_file():
        return True
    relative = Path(path)
    extension = relative.suffix[1:].lower() or "img"
    stem = relative.with_suffix("") if relative.suffix else relative
    return any(
        (DATA_DIR / "optimized" / f"{stem}-{extension}.{kind}").is_file()
        for kind in ("webp", "jpg")
    )


def _settle_media(model):
    """Point only at images that exist — a missing file meant three 404s per model each time the list opened.
    Without an image the card shows the task icon and the detail page shows the 'Run inference' hint."""
    alias = _MEDIA_ALIAS.get(model.get("id"))
    thumb = model.get("thumbnail")
    if thumb and not _media_exists(thumb):
        alt = f"thumbnails/{alias}.jpg" if alias else None
        model["thumbnail"] = alt if alt and _media_exists(alt) else None
    ex = model.get("example_images")
    if isinstance(ex, dict):
        for key in ("result", "original"):
            path = ex.get(key)
            if path and not _media_exists(path):
                alt = f"examples/{alias}_{key}.jpg" if alias else None
                if alt and _media_exists(alt):
                    ex[key] = alt
                else:
                    ex.pop(key, None)


def reload_catalog():
    """Reload the catalog, adding enriched fields when a generated catalog exists."""
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

    # Load the generated catalog (schema 2.0) and merge its enriched fields
    if generated is not None:
        gen_map = {m["id"]: m for m in generated.get("models", [])}
        metadata_source = _metadata_source_from_generated(generated)
        used = set()
        for model in merged:
            enriched = _match_generated(model["id"], gen_map)
            if enriched:
                used.add(enriched.get("id"))
                _enrich_model_entry(model, enriched, metadata_source=metadata_source)
        # Models that exist only on the publish page (new models from the dx_app per-model layout) are listed too,
        # not just used for enrichment — but only for known tasks.
        merged.extend(_generated_only_models(generated, used, metadata_source))
        # Ensure default processor/specification (for models absent from the generated catalog)
        for model in merged:
            model.setdefault("processor", {"supported_devices": [], "status": "metadata_pending"})
            model.setdefault("specification", {})
    else:
        # Ensure default processor/specification even without a generated catalog
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
    # When and from what this list was built. The list view is where "is this whole list stale?" gets asked,
    # so the values go on the list too, not only on each model's detail page.
    # Contract: tests/dx_modelzoo/test_catalog_freshness.py
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
    """Model only in the generated catalog → list entry (same shape as a curated entry)."""
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
        # A 'No Reference' source is cleared by _enrich_legal
        entry["publish_only"] = True     # the current dx_app has no example yet — it comes with the per-model layout
        out.append(entry)
    return out


def apply_generated_catalog(generated_catalog):
    """Apply the generated catalog to the in-memory catalog (no file I/O)."""
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

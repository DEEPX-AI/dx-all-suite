"""ModelZoo 소스 어댑터 – 로컬 런타임, dx-modelzoo 리포, 내부 테이블, 벤치마크 캐시."""

import json
import re
import ssl
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from dx_modelzoo.metadata._protocol import AdapterResult
from dx_modelzoo.metadata.normalization import canonical_model_id, normalize_source_value




def _utcnow_iso():
    return datetime.now(timezone.utc).isoformat()


def _adapter_result(adapter, profile="default") -> AdapterResult:
    return {
        "adapter": adapter,
        "profile": profile,
        "fetched_at": _utcnow_iso(),
        "ok": True,
        "models": {},
        "errors": [],
        "warnings": [],
    }




def _find_example_dir(base, task_dir_name, model_dir_name):
    """example 디렉토리에서 모델별 예제 경로를 확인하고 DX_APP_ROOT 기준 상대경로로 반환.

    Return a path RELATIVE to DX_APP_ROOT (e.g. 'src/cpp_example/<task>/<model>/'), NOT the
    absolute build path — str(candidate) baked the build machine's /home/... into the shipped
    generated_catalog.json (544 leaks + non-portable). base is .../dx_app/src/{cpp,python}_example,
    so base.name gives the example type. Matches core.catalog._build_demo_info's format.
    """
    candidate = base / task_dir_name / model_dir_name
    if candidate.is_dir():
        return f"src/{base.name}/{task_dir_name}/{model_dir_name}/"
    return None


def _task_to_example_dir(task):
    """add_model_task → example 디렉토리명 매핑."""
    mapping = {
        "classification": "classification",
        "object_detection": "object_detection",
        "semantic_segmentation": "semantic_segmentation",
        "face_detection": "face_detection",
        "pose_estimation": "pose_estimation",
        "depth_estimation": "depth_estimation",
        "embedding": "embedding",
        "image_denoising": "image_denoising",
        "image_enhancement": "image_enhancement",
        "instance_segmentation": "instance_segmentation",
        "super_resolution": "super_resolution",
        "reid": "reid",
        "face_alignment": "face_alignment",
        "hand_landmark": "hand_landmark",
        "attribute_recognition": "attribute_recognition",
        "obb_detection": "obb_detection",
        "ppu": "ppu",
    }
    return mapping.get(task)


def local_runtime_adapter(suite_root) -> AdapterResult:
    """dx-runtime의 model_registry.json, manifest, example을 읽어 메타데이터 구성."""
    suite_root = Path(suite_root)
    result = _adapter_result("local_runtime")

    registry_path = suite_root / "dx-runtime" / "dx_app" / "config" / "model_registry.json"
    manifest_path = suite_root / "dx-runtime" / "dx_app" / "scripts" / "modelzoo_manifest.json"

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        result["ok"] = False
        result["errors"].append(f"registry load failed: {exc}")
        return result

    manifest_by_name = {}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest:
            name = entry.get("name")
            if not name:
                result["warnings"].append(
                    f"manifest entry missing 'name': {entry!r}"
                )
                continue
            manifest_by_name[name] = entry
            manifest_by_name[canonical_model_id(name)] = entry
    except Exception as exc:
        result["warnings"].append(f"manifest load failed: {exc}")

    cpp_example_root = suite_root / "dx-runtime" / "dx_app" / "src" / "cpp_example"
    py_example_root = suite_root / "dx-runtime" / "dx_app" / "src" / "python_example"

    for reg in registry:
        model_name = reg.get("model_name", "")
        original_name = reg.get("original_name", model_name)
        dxnn_file = reg.get("dxnn_file", "")
        cid = canonical_model_id(model_name or original_name or dxnn_file)
        if not cid:
            continue

        task = reg.get("add_model_task", "")
        entry = {
            "display.name": original_name,
            "display.class_name": model_name,
            "display.task": task,
            "specification.input_width": reg.get("input_width"),
            "specification.input_height": reg.get("input_height"),
            "technical.postprocessor": reg.get("postprocessor"),
            "technical.config": reg.get("config"),
        }

        manifest_entry = (
            manifest_by_name.get(original_name)
            or manifest_by_name.get(model_name)
            or manifest_by_name.get(Path(dxnn_file).stem)
            or manifest_by_name.get(canonical_model_id(original_name))
            or manifest_by_name.get(canonical_model_id(model_name))
            or manifest_by_name.get(canonical_model_id(dxnn_file))
            or {}
        )
        dxnn_url = manifest_entry.get("dxnn_url")
        if dxnn_url:
            entry["artifacts.qlite_dxnn.remote_url"] = dxnn_url
        json_url = manifest_entry.get("json_url")
        if json_url:
            entry["artifacts.qlite_json.remote_url"] = json_url

        if dxnn_file:
            dxnn_rel = str(dxnn_file).lstrip("/\\")
            local_rel_path = Path("models") / dxnn_rel
            local_path = suite_root / "dx-runtime" / "dx_app" / local_rel_path
            entry["artifacts.qlite_dxnn.local_path"] = local_rel_path.as_posix()
            entry["artifacts.qlite_dxnn.local_exists"] = local_path.exists()

        example_dir = _task_to_example_dir(task)
        if example_dir:
            cpp_ex = _find_example_dir(cpp_example_root, example_dir, model_name)
            if cpp_ex:
                entry["demo.cpp_example"] = cpp_ex
            py_ex = _find_example_dir(py_example_root, example_dir, model_name)
            if py_ex:
                entry["demo.python_example"] = py_ex

        result["models"][cid] = entry

    return result



from dx_modelzoo.metadata._html_parser import (  # noqa: E402
    _ARTIFACT_JOIN_SCORES,
    _LINK_FIELDS,
    _TABLE_FIELD_MAP,
    _ACCURACY_FIELDS,
    _FLOAT_FIELDS,
    _TableParser,
    clean_cell_text as _clean_cell_text,
    html_span as _html_span,
    expand_table_headers as _expand_table_headers,
    parse_internal_table_models,
    _is_suspicious_accuracy,
    _table_cell_value,
    _table_model_id,
    _artifact_model_id,
    _table_model_id_aliases,
    _add_join_candidate,
    _table_join_candidates,
    _table_float,
    _parse_internal_table_rows,
)

_INTERNAL_PUBLISH_URL = "https://modelzoo-publish-api.devops.dpx.ai/publish/html"


def _set_accuracy_or_suspect(fields, field, value):
    """accuracy 값이 suspicious이면 suspect로 격리, 아니면 정상 저장."""
    if _is_suspicious_accuracy(field, value):
        base = field.rsplit(".", 1)[0]
        fields[f"{base}.source_status"] = "suspect"
        fields[f"{base}.suspect_value"] = str(value)
    else:
        fields[field] = value


def parse_internal_table_html(html):
    """내부 HTML 테이블을 파싱하여 모델 메타데이터 dict 반환 (호환성 래퍼)."""
    result = _adapter_result("internal_table")
    result["models"] = parse_internal_table_models(html)
    return result


def _fetch_url_text(url, *, verify_tls=True, timeout=30):
    request = Request(url, headers={"User-Agent": "DX-ModelZoo-Metadata/1.0"})
    context = None
    if not verify_tls:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    with urlopen(request, timeout=timeout, context=context) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise RuntimeError(f"HTTP {status}")
        encoding = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(encoding, errors="replace")


def internal_modelzoo_adapter(suite_root, publish_url=_INTERNAL_PUBLISH_URL, fetch_text=None, verify_tls=True) -> AdapterResult:
    """내부 ModelZoo publish HTML을 가져와 정규화된 메타데이터로 변환."""
    result = _adapter_result("internal_modelzoo", profile="internal")
    fetch_text = fetch_text or (lambda url: _fetch_url_text(url, verify_tls=verify_tls))
    try:
        html = fetch_text(publish_url)
        parsed = parse_internal_table_html(html)
    except Exception as exc:
        result["ok"] = False
        result["errors"].append(f"internal publish fetch/parse failed: {exc}")
        return result

    result["models"] = parsed.get("models", {})
    if not result["models"]:
        result["warnings"].append("internal publish page parsed zero models")
    return result


_PUBLIC_MODELZOO_URL = "https://developer.deepx.ai/modelzoo/"


def public_modelzoo_adapter(suite_root, publish_url=_PUBLIC_MODELZOO_URL, fetch_text=None, verify_tls=True) -> AdapterResult:
    """공개 ModelZoo(developer.deepx.ai/modelzoo)의 서버 렌더 HTML 테이블을 파싱해
    정규화된 메타데이터로 변환. (일반망 사용자가 보는 데이터에 맞춤)"""
    result = _adapter_result("public_modelzoo", profile="public")
    fetch_text = fetch_text or (lambda url: _fetch_url_text(url, verify_tls=verify_tls))
    try:
        html = fetch_text(publish_url)
        from dx_modelzoo.metadata._public_parser import parse_public_modelzoo_html
        models, warns = parse_public_modelzoo_html(html)
    except Exception as exc:
        result["ok"] = False
        result["errors"].append(f"public modelzoo fetch/parse failed: {exc}")
        return result
    result["models"] = models
    result["warnings"].extend(warns)
    if not models:
        result["warnings"].append("public modelzoo parsed zero models")
    return result




def benchmark_cache_adapter(cache_path) -> AdapterResult:
    """벤치마크 캐시 JSON(스펙 포맷)을 읽어 정규화된 모델 메타데이터 반환."""
    cache_path = Path(cache_path)
    result = _adapter_result("benchmark_cache")

    if not cache_path.exists():
        result["warnings"].append(f"cache file not found: {cache_path}")
        return result

    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception as exc:
        result["ok"] = False
        result["errors"].append(f"cache load failed: {exc}")
        return result

    device = data.get("device")
    models = data.get("models", {})

    for model_id, entry in models.items():
        cid = canonical_model_id(model_id)
        if not cid:
            result["warnings"].append(f"skipped empty canonical id for: {model_id!r}")
            continue
        fields = {}
        if "fps" in entry and entry["fps"] is not None:
            fields["performance.fps"] = entry["fps"]
        fps_per_watt = entry.get("fps_per_watt")
        if fps_per_watt is not None:
            fields["performance.fps_per_watt"] = fps_per_watt
        if entry.get("source"):
            fields["performance.source"] = entry["source"]
        if entry.get("measured_at"):
            fields["performance.measured_at"] = entry["measured_at"]
        if device:
            fields["performance.device"] = device
        result["models"][cid] = fields

    return result



# DatasetType enum → 사람이 읽을 수 있는 값 매핑
_DATASET_TYPE_MAP = {
    "imagenet": "ImageNet",
    "coco": "COCO",
    "voc_seg": "VOCSegmentation",
    "voc_od": "VOC2007Detection",
    "bsd68": "BSD68",
    "bsd100": "BSD100",
    "city": "CitySpace",
    "widerface": "WiderFace",
    "nyu": "NYU",
    "coco_pose": "COCOPose",
}

# EvaluationType enum → metric 문자열 매핑
_EVALUATION_METRIC_MAP = {
    "image_classification": "TopK1, TopK5",
    "coco": "mAP, mAP50",
    "segmentation": "mIoU",
    "voc": "mAP50",
    "bsd68": "PSNR, SSIM",
    "bsd100": "PSNR, SSIM",
    "widerface": "AP",
    "depth_estimation": "RMSE",
    "instance_segmentation": "mAP",
    "zeroshot_classification": "TopK1, TopK5",
    "coco_pose": "mAP, mAP50",
}

# ModelInfo 텍스트 파싱용 정규식
_RE_FIELD_STR = re.compile(
    r'(\w+)\s*=\s*"([^"]*)"'
)
_RE_FIELD_ENUM = re.compile(
    r'(\w+)\s*=\s*(\w+)\.(\w+)'
)
_RE_FIELD_NONE = re.compile(
    r'(\w+)\s*=\s*None'
)
_RE_NAME_POSITIONAL = re.compile(
    r'name\s*=\s*"([^"]*)"'
)

_RE_MODELINFO_START = re.compile(r"ModelInfo\s*\(")


def _find_modelinfo_blocks(text):
    """Quote-aware balanced-parentheses scanner로 ModelInfo(...) 블록 내부를 추출."""
    blocks = []
    for m in _RE_MODELINFO_START.finditer(text):
        start = m.end()  # '(' 다음 위치
        depth = 1
        i = start
        length = len(text)
        while i < length and depth > 0:
            ch = text[i]
            if ch in ('"', "'"):
                # 문자열 내부 스킵
                quote = ch
                i += 1
                while i < length:
                    if text[i] == '\\':
                        i += 2
                        continue
                    if text[i] == quote:
                        break
                    i += 1
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            i += 1
        if depth == 0:
            blocks.append(text[start:i - 1])
    return blocks


def parse_modelzoo_model_file(file_path):
    """dx-modelzoo 모델 .py 파일에서 ModelInfo 필드를 텍스트 파싱으로 추출.

    항상 {canonical_id: fields} dict를 반환.
    """
    file_path = Path(file_path)
    text = file_path.read_text(encoding="utf-8")
    return _extract_all_model_infos(text)


from dx_modelzoo.metadata._yaml_parser import (  # noqa: E402
    yaml_scalar as _yaml_scalar,
    yaml_top_level_value as _yaml_top_level_value,
    yaml_nested_value as _yaml_nested_value,
    yaml_first_shape as _yaml_first_shape,
    parse_modelzoo_yaml_file,
)


def _extract_all_model_infos(text):
    """텍스트에서 모든 ModelInfo(...) 블록을 파싱하여 {cid: fields} 반환."""
    models = {}
    for block in _find_modelinfo_blocks(text):
        fields = _parse_modelinfo_block(block)
        name = fields.pop("_name", None)
        if not name:
            continue
        cid = canonical_model_id(name)
        if not cid:
            continue
        models[cid] = fields
    return models


def _parse_modelinfo_block(block):
    """ModelInfo(...) 내부 블록에서 필드 추출."""
    fields = {}

    name_m = _RE_NAME_POSITIONAL.search(block)
    if name_m:
        fields["_name"] = name_m.group(1)

    for m in _RE_FIELD_STR.finditer(block):
        key, val = m.group(1), m.group(2)
        if key == "name":
            fields["_name"] = val
        elif key == "raw_performance":
            _set_accuracy_or_suspect(fields, "evaluation.raw.accuracy", val)
        elif key == "q_lite_performance":
            _set_accuracy_or_suspect(fields, "evaluation.qlite.accuracy", val)
        elif key == "q_pro_performance":
            _set_accuracy_or_suspect(fields, "evaluation.qpro.accuracy", val)
        elif key == "q_master_performance":
            _set_accuracy_or_suspect(fields, "evaluation.qmaster.accuracy", val)
        elif key == "source":
            fields["legal.source_url"] = val

    for m in _RE_FIELD_NONE.finditer(block):
        key = m.group(1)
        if key == "q_pro_performance":
            fields.setdefault("evaluation.qpro.accuracy", None)
        elif key == "q_master_performance":
            fields.setdefault("evaluation.qmaster.accuracy", None)
        elif key == "source":
            fields.setdefault("legal.source_url", None)

    for m in _RE_FIELD_ENUM.finditer(block):
        key, enum_cls, enum_val = m.group(1), m.group(2), m.group(3)
        if key == "dataset" and enum_cls == "DatasetType":
            resolved = _DATASET_TYPE_MAP.get(enum_val, enum_val)
            fields["specification.dataset"] = resolved
        elif key == "evaluation" and enum_cls == "EvaluationType":
            metric = _EVALUATION_METRIC_MAP.get(enum_val)
            if metric:
                fields["specification.metric.name"] = metric

    return fields


def local_modelzoo_repo_adapter(suite_root) -> AdapterResult:
    """dx-modelzoo 리포에서 모든 모델 파일을 텍스트 파싱하여 메타데이터 수집."""
    suite_root = Path(suite_root)
    result = _adapter_result("local_modelzoo_repo")

    models_dir = suite_root / "dx-modelzoo" / "src" / "dx_modelzoo" / "models"
    if not models_dir.is_dir():
        result["ok"] = False
        result["errors"].append(f"models directory not found: {models_dir}")
        return result

    py_files = sorted(models_dir.rglob("*.py"))
    for py_file in py_files:
        if py_file.name.startswith("_"):
            continue
        try:
            text = py_file.read_text(encoding="utf-8")
        except Exception as exc:
            result["warnings"].append(f"read failed {py_file.name}: {exc}")
            continue

        if "ModelInfo" not in text:
            continue

        try:
            extracted = _extract_all_model_infos(text)
            for cid, fields in extracted.items():
                if cid in result["models"]:
                    result["models"][cid].update(fields)
                else:
                    result["models"][cid] = fields
        except Exception as exc:
            result["warnings"].append(f"parse failed {py_file.name}: {exc}")

    yaml_files = sorted(models_dir.rglob("*.yaml"))
    for yaml_file in yaml_files:
        try:
            extracted = parse_modelzoo_yaml_file(yaml_file)
            for cid, fields in extracted.items():
                if cid in result["models"]:
                    result["models"][cid].update(fields)
                else:
                    result["models"][cid] = fields
        except Exception as exc:
            result["warnings"].append(f"parse failed {yaml_file.name}: {exc}")

    return result

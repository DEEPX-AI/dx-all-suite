"""메타데이터 병합 엔진 – 다중 어댑터 결과를 단일 카탈로그로 통합."""

from datetime import datetime, timezone

from dx_modelzoo.metadata.normalization import normalize_source_value
from dx_modelzoo.metadata.schema import SCHEMA_VERSION, ARTIFACT_IDS


# 필드 우선순위: 뒤에 오는 어댑터가 같은 필드를 덮어씀.
# local_runtime은 model list 기준(baseline)을 제공하고,
# 이후 어댑터들이 accuracy/performance/legal 등을 보강.

# editorial 텍스트 (task → 기본 use_case)
_EDITORIAL_BY_TASK = {
    "classification": "Image classification model for visual recognition tasks.",
    "object_detection": "Object detection model for identifying and localizing objects.",
    "semantic_segmentation": "Semantic segmentation model for pixel-level classification.",
    "face_detection": "Face detection model for detecting facial regions.",
    "pose_estimation": "Pose estimation model for detecting body keypoints.",
    "depth_estimation": "Depth estimation model for predicting depth maps.",
    "super_resolution": "Super resolution model for image upscaling.",
    "instance_segmentation": "Instance segmentation model for per-object pixel masks.",
}

_REQUIRED_PERF_FIELDS = {"fps", "fps_per_watt"}
_ARTIFACT_PRESENT_KEYS = {"remote_url", "local_path", "download_endpoint", "available"}


def merge_adapter_results(results, source_profile="local"):
    """여러 어댑터 결과를 병합하여 스키마 2.0 카탈로그를 생성.

    baseline 모델 목록은 local_runtime 어댑터에서 가져옴.
    다른 어댑터들은 baseline에 있는 모델만 보강함.
    """
    baseline_ids = set()
    for r in results:
        if r.get("adapter") == "local_runtime":
            baseline_ids = set(r.get("models", {}).keys())
            break

    # baseline이 없으면 첫 번째 ok 어댑터의 모델 목록 사용
    if not baseline_ids:
        for r in results:
            if r.get("ok") and r.get("models"):
                baseline_ids = set(r["models"].keys())
                break

    # flat field 병합 (순서대로 덮어씀)
    merged_flat = {}  # model_id -> {flat_field: value}
    provenance = {}   # model_id -> {flat_field: {"source": adapter_name}}

    for r in results:
        adapter_name = r.get("adapter", "unknown")
        if not r.get("ok"):
            continue
        for mid, fields in r.get("models", {}).items():
            if mid not in baseline_ids:
                continue
            if mid not in merged_flat:
                merged_flat[mid] = {}
                provenance[mid] = {}
            for k, v in fields.items():
                v = normalize_source_value(v)
                if v is not None:
                    merged_flat[mid][k] = v
                    provenance[mid][k] = {"source": adapter_name}

    models = []
    for mid in sorted(baseline_ids):
        flat = merged_flat.get(mid, {})
        prov = provenance.get(mid, {})
        model = _build_structured_model(mid, flat, prov)
        models.append(model)

    return {
        "schema_version": SCHEMA_VERSION,
        "source_profile": source_profile,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "models": models,
    }


def _build_structured_model(mid, flat, prov):
    """flat 필드를 중첩 구조로 변환."""
    model = {"id": mid}

    model["display"] = {
        "name": flat.get("display.name", mid),
        "task": flat.get("display.task", ""),
    }
    if "display.class_name" in flat:
        model["display"]["class_name"] = flat["display.class_name"]

    spec = {}
    for k, v in flat.items():
        if k.startswith("specification."):
            parts = k.split(".", 1)[1]
            _nested_set(spec, parts, v)
    if spec:
        model["specification"] = spec

    evaluation = {}
    for k, v in flat.items():
        if k.startswith("evaluation."):
            parts = k.split(".", 1)[1]
            _nested_set(evaluation, parts, v)
    if evaluation:
        model["evaluation"] = evaluation

    perf = {}
    for k, v in flat.items():
        if k.startswith("performance."):
            field = k.split(".", 1)[1]
            perf[field] = v

    # I4: deterministic performance defaults
    for field in _REQUIRED_PERF_FIELDS:
        perf.setdefault(field, None)

    has_fps = perf.get("fps") is not None
    if has_fps:
        perf.setdefault("source_status", "provided")
    else:
        perf["source_status"] = "benchmark_required"
    model["performance"] = perf

    legal = {}
    for k, v in flat.items():
        if k.startswith("legal."):
            field = k.split(".", 1)[1]
            if v is not None:
                legal[field] = v
    if legal:
        model["legal"] = legal

    artifacts = {}
    for k, v in flat.items():
        if k.startswith("artifacts."):
            parts = k.split(".", 1)[1]
            _nested_set(artifacts, parts, v)
    if artifacts:
        model["artifacts"] = artifacts

    processor_devices = []
    for k, v in flat.items():
        if k.startswith("processor."):
            field = k.split(".", 1)[1]
            if field == "supported_devices" and isinstance(v, list):
                processor_devices = v
    model["processor"] = {
        "supported_devices": processor_devices,
        "status": "metadata_pending" if not processor_devices else "provided",
    }

    missing = []
    # I2: _REQUIRED_PERF_FIELDS 활용 (performance. 접두사로 정규화)
    for pf in sorted(_REQUIRED_PERF_FIELDS):
        if perf.get(pf) is None or (pf == "fps" and perf.get("source_status") == "benchmark_required"):
            missing.append(f"performance.{pf}")
    if not legal:
        missing.append("license")
    # I4: 누락 아티팩트 분석
    for aid in sorted(ARTIFACT_IDS):
        art_data = artifacts.get(aid, {})
        present = any(art_data.get(k) for k in _ARTIFACT_PRESENT_KEYS)
        if not present:
            missing.append(aid)
    model["missing"] = missing

    task = flat.get("display.task", "")
    editorial = _EDITORIAL_BY_TASK.get(task, f"AI model for {task} tasks." if task else "AI model.")
    category_label = task.replace("_", " ").title() if task else "Unknown"
    model["display"]["summary"] = {"en": editorial}
    model["display"]["category_label"] = category_label

    model["content"] = {
        "use_case": {"en": editorial},
    }

    model["provenance"] = prov

    demo = {}
    for k, v in flat.items():
        if k.startswith("demo."):
            field = k.split(".", 1)[1]
            demo[field] = v
    if demo:
        model["demo"] = demo

    technical = {}
    for k, v in flat.items():
        if k.startswith("technical."):
            field = k.split(".", 1)[1]
            if v is not None:
                technical[field] = v
    if technical:
        model["technical"] = technical

    return model


def _nested_set(d, dotpath, value):
    """점 구분 경로로 중첩 dict에 값 설정."""
    parts = dotpath.split(".")
    current = d
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value

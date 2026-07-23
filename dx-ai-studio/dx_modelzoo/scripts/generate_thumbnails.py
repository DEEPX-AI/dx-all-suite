#!/usr/bin/env python3
"""dx_app inference API로 340개 모델 썸네일/예제 이미지 생성.

사전 조건: dx_app 서버가 localhost:8080에서 실행 중이어야 함.
Usage: python3 generate_thumbnails.py [--dry-run] [--model MODEL_ID]
"""
import sys, json, base64, os, time, shutil
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

from dx_modelzoo.core.config import (DX_APP_PORT, DX_APP_ROOT, DATA_DIR,
                          SAMPLE_IMAGES, MODEL_IMAGE_OVERRIDE, EXAMPLE_TYPES)
from dx_modelzoo.core.catalog import parse_test_models_conf
from dx_modelzoo.core.proxy import is_dx_app_alive

THUMB_DIR = DATA_DIR / "thumbnails"
EXAMPLE_DIR = DATA_DIR / "examples"
DX_APP_URL = f"http://127.0.0.1:{DX_APP_PORT}"

# The C++ sync runners for these tasks do NOT honor DXAPP_SAVE_IMAGE (dx_app v3.2.0 gap),
# so a cpp run yields no result image. The python runners save uniformly → force python.
PY_LANG_CATEGORIES = {
    "pose_estimation", "keypoint_detection",
    "object_pose_estimation", "panoptic_driving_perception",
}


def run_inference_api(model_name, category, model_file):
    """dx_app /api/run 엔드포인트 호출."""
    image_path = MODEL_IMAGE_OVERRIDE.get(model_name, SAMPLE_IMAGES.get(category, ""))
    payload_d = {
        "model_name": model_name,
        "category": category,
        "model_file": model_file,
        "input_type": "image",
        "image_path": image_path,
    }
    if category in PY_LANG_CATEGORIES:
        payload_d["lang"] = "python"
    payload = json.dumps(payload_d).encode("utf-8")
    req = Request(f"{DX_APP_URL}/api/run", data=payload,
                  headers={"Content-Type": "application/json"})
    try:
        resp = urlopen(req, timeout=120)
        return json.loads(resp.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def save_base64_image(b64_str, path):
    """base64 문자열을 이미지 파일로 저장."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = base64.b64decode(b64_str)
    path.write_bytes(data)


def generate(dry_run=False, single_model=None, only_missing=False):
    if not is_dx_app_alive():
        print(f"[ERROR] dx_app is not running at port {DX_APP_PORT}. Aborting.")
        print("Start dx_app first: cd dx-ai-studio && python3 dx_app/server.py")
        sys.exit(1)

    models = parse_test_models_conf()
    if single_model:
        models = [m for m in models if m["id"] == single_model]
        if not models:
            print(f"[ERROR] Model '{single_model}' not found")
            sys.exit(1)
    if only_missing:
        models = [m for m in models if not (THUMB_DIR / f"{m['id']}.jpg").exists()]
        print(f"[only-missing] {len(models)} models without a thumbnail")

    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    EXAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    total = len(models)
    success = 0
    failed = []

    for i, m in enumerate(models):
        mid = m["id"]
        cat = m["category"]
        ex_type = EXAMPLE_TYPES.get(cat, "single")

        print(f"[{i+1}/{total}] {mid} ({cat}) ...", end=" ", flush=True)

        if dry_run:
            print("SKIP (dry-run)")
            continue

        result = run_inference_api(mid, cat, m["model_file"])

        if result.get("error"):
            print(f"FAIL: {result['error']}")
            failed.append(mid)
            continue

        img_b64 = result.get("result_image") or result.get("image", "")
        if not img_b64:
            print("FAIL: no image in response")
            failed.append(mid)
            continue

        # 썸네일 (결과 이미지 = 썸네일)
        save_base64_image(img_b64, THUMB_DIR / f"{mid}.jpg")
        save_base64_image(img_b64, EXAMPLE_DIR / f"{mid}_result.jpg")

        # before_after/overlay: 원본 이미지도 복사
        if ex_type in ("before_after", "overlay"):
            sample = SAMPLE_IMAGES.get(cat, "")
            src = DX_APP_ROOT / sample
            if src.exists():
                shutil.copy2(src, EXAMPLE_DIR / f"{mid}_original.jpg")

        success += 1
        print("OK")
        time.sleep(0.1)

    print(f"\n[DONE] {success}/{total} succeeded, {len(failed)} failed")
    if failed:
        print(f"[FAILED] {', '.join(failed[:20])}{'...' if len(failed) > 20 else ''}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--model", type=str, default=None, help="Single model ID")
    p.add_argument("--only-missing", action="store_true", help="Only models lacking a thumbnail")
    args = p.parse_args()
    generate(dry_run=args.dry_run, single_model=args.model, only_missing=args.only_missing)

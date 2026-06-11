#!/usr/bin/env python3
"""evaluate.py — Measure accuracy (mAP50-95, mAP50, per-class) and speed (FPS) for the
four comparison points and write results.json:

  1. base      .pt   fp32  GPU   (general COCO model on the wildlife domain)
  2. base      .dxnn INT8  DX-M1 NPU
  3. retrained .pt   fp32  GPU
  4. retrained .dxnn INT8  DX-M1 NPU

FPS = 1000 / speed["inference"] (single-image latency). All points evaluate on the
SAME african-wildlife val split (225 images, imgsz=640, batch=1) for a fair comparison.
"""
import json
import sys
from pathlib import Path

from ultralytics import YOLO

HERE = Path(__file__).resolve().parent
DATA = "african-wildlife.yaml"
IMGSZ = 640
SPLIT = "val"
NAMES = ["buffalo", "elephant", "rhino", "zebra"]

POINTS = [
    # key, model path/dir, form, device
    ("base_fp32_gpu",      HERE / "yolo26n.pt",                          "pt",   0),
    ("base_int8_npu",      HERE / "base_yolo26n_deepx_model",            "dxnn", "cpu"),
    ("retrained_fp32_gpu", HERE / "runs" / "train" / "weights" / "best.pt", "pt", 0),
    ("retrained_int8_npu", HERE / "retrained_yolo26n_deepx_model",       "dxnn", "cpu"),
]


def eval_one(model_path: Path, device) -> dict:
    """Run model.val() and extract mAP + speed. device: 0 (GPU) for .pt, 'cpu' for
    .dxnn (the DeepX backend drives the NPU; CPU just runs host-side pre/post)."""
    m = YOLO(str(model_path))
    metrics = m.val(data=DATA, split=SPLIT, imgsz=IMGSZ, batch=1, device=device, verbose=False)
    inf_ms = float(metrics.speed["inference"])
    per_class = {}
    try:
        maps = list(metrics.box.maps)  # per-class mAP50-95, indexed by dataset class id
        for i, name in enumerate(NAMES):
            if i < len(maps):
                per_class[name] = round(float(maps[i]), 4)
    except Exception:
        pass
    return {
        "map50_95": round(float(metrics.box.map), 4),
        "map50": round(float(metrics.box.map50), 4),
        "per_class_map50_95": per_class,
        "inference_ms": round(inf_ms, 3),
        "fps": round(1000.0 / inf_ms, 2) if inf_ms > 0 else None,
        "speed_ms": {k: round(float(v), 3) for k, v in metrics.speed.items()},
    }


def main() -> int:
    results = {}
    for key, path, form, device in POINTS:
        if not path.exists():
            print(f"[eval] SKIP {key}: not found at {path}")
            results[key] = {"status": "missing", "path": str(path)}
            continue
        print(f"[eval] {key}: {form} on device={device} ({path.name})")
        try:
            r = eval_one(path, device)
            r["status"] = "ok"; r["form"] = form; r["device"] = str(device)
            results[key] = r
            print(f"[eval] {key}: mAP50-95={r['map50_95']} mAP50={r['map50']} "
                  f"FPS={r['fps']} ({r['inference_ms']} ms/img)")
        except Exception as e:
            print(f"[eval] ERROR {key}: {type(e).__name__}: {e}")
            results[key] = {"status": "error", "error": f"{type(e).__name__}: {e}"}

    out = HERE / "results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"[eval] wrote {out}")
    # Success if at least the two retrained points succeeded (the deployable result).
    ok = all(results.get(k, {}).get("status") == "ok"
             for k in ("retrained_fp32_gpu", "retrained_int8_npu"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

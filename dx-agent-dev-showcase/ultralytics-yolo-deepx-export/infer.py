#!/usr/bin/env python3
"""
Run inference on bus.jpg using the exported yolo26n_deepx_model/.
Uses Ultralytics YOLO backend — dx_engine provides NPU inference.
"""
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_DIR = SCRIPT_DIR / "yolo26n_deepx_model"

if not MODEL_DIR.exists():
    print(f"ERROR: {MODEL_DIR} not found. Run export.py first.", file=sys.stderr)
    sys.exit(1)

# Find bus.jpg: prefer bundled sample/, then ultralytics assets
BUS_IMG = SCRIPT_DIR / "sample" / "bus.jpg"
if not BUS_IMG.exists():
    import ultralytics
    BUS_IMG = Path(ultralytics.__file__).parent / "assets" / "bus.jpg"

if not BUS_IMG.exists():
    print("ERROR: bus.jpg not found in sample/ or ultralytics assets", file=sys.stderr)
    sys.exit(1)

print(f"[infer] Model: {MODEL_DIR}")
print(f"[infer] Image: {BUS_IMG}")

from ultralytics import YOLO
model = YOLO(str(MODEL_DIR))

print("[infer] Running inference on bus.jpg ...")
results = model(str(BUS_IMG), verbose=True)

total = 0
for r in results:
    n = len(r.boxes) if r.boxes is not None else 0
    total += n
    print(f"[infer] Detected {n} object(s) in image")
    if r.boxes is not None and n > 0:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names.get(cls_id, str(cls_id))
            xyxy = box.xyxy[0].tolist()
            print(f"  [{cls_id:3d}] {label:<20s}  conf={conf:.3f}  bbox=[{xyxy[0]:.0f},{xyxy[1]:.0f},{xyxy[2]:.0f},{xyxy[3]:.0f}]")

if total == 0:
    print("[infer] WARN: zero detections on bus.jpg — check model or thresholds", file=sys.stderr)
    sys.exit(1)

print(f"[infer] Total detections: {total}")
print("[infer] PASS")

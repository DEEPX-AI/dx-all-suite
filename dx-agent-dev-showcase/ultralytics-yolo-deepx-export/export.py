#!/usr/bin/env python3
"""
Export yolo26n.pt to DeepX NPU format using Ultralytics format=deepx.

Ultralytics writes the output next to the .pt file, so yolo26n.pt is
copied into the session directory first, and the export then produces:
  yolo26n_deepx_model/
    yolo26n.dxnn    (compiled NPU binary)
    config.json     (calibration + preprocessing config)
    metadata.yaml   (class names, image size, task)
"""
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_PT = SCRIPT_DIR / "yolo26n.pt"
MODEL_DIR_EXPECTED = SCRIPT_DIR / "yolo26n_deepx_model"

# If already exported, skip
if MODEL_DIR_EXPECTED.exists() and (MODEL_DIR_EXPECTED / "yolo26n.dxnn").exists():
    print(f"[export] yolo26n_deepx_model/ already exists — skipping export")
    for fname in ["yolo26n.dxnn", "config.json", "metadata.yaml"]:
        p = MODEL_DIR_EXPECTED / fname
        print(f"[export] ✓ {fname}  ({p.stat().st_size:,} bytes)")
    sys.exit(0)

# Ultralytics writes the DeepX output next to the .pt file, so keep the .pt in
# SCRIPT_DIR. If it is not present, Ultralytics auto-downloads it on YOLO("yolo26n.pt").
from ultralytics import YOLO
if not LOCAL_PT.exists():
    print(f"[export] yolo26n.pt not found — auto-downloading into {SCRIPT_DIR}")
    os.chdir(SCRIPT_DIR)            # YOLO() downloads weights into the cwd
    YOLO("yolo26n.pt")             # triggers the download → SCRIPT_DIR/yolo26n.pt
print(f"[export] Loading model: {LOCAL_PT}")
model = YOLO(str(LOCAL_PT))

print("[export] Starting format=deepx export ...")
print("[export]   INT8 calibration with coco128.yaml (enforced by Ultralytics)")
print("[export]   This may take several minutes.")
result = model.export(
    format="deepx",
    data="coco128.yaml",
    imgsz=640,
    batch=1,
)
print(f"[export] Export returned: {result}")

# Verify output — Ultralytics writes to parent(model_file)/modelname_deepx_model/
# Since LOCAL_PT is in SCRIPT_DIR, the output should be SCRIPT_DIR/yolo26n_deepx_model/
expected_files = ["yolo26n.dxnn", "config.json", "metadata.yaml"]
missing = []
for fname in expected_files:
    fpath = MODEL_DIR_EXPECTED / fname
    if fpath.exists():
        print(f"[export] ✓ {fname}  ({fpath.stat().st_size:,} bytes)")
    else:
        print(f"[export] ✗ MISSING: {fname}", file=sys.stderr)
        missing.append(fname)

if missing:
    print(f"[export] FAIL — missing files: {missing}", file=sys.stderr)
    sys.exit(1)

print("[export] DONE — yolo26n_deepx_model/ is ready for inference")

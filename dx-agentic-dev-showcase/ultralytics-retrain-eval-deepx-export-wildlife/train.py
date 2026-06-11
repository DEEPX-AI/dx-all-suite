#!/usr/bin/env python3
"""train.py — Fine-tune (retrain) the COCO-pretrained yolo26n on the Ultralytics
african-wildlife dataset (nc=4: buffalo, elephant, rhino, zebra) on the local GPU.

Produces a domain-optimized model. Best weights → <session>/runs/train/weights/best.pt.
Base yolo26n.pt auto-downloads from Ultralytics on first use.
"""
import sys
from pathlib import Path

from ultralytics import YOLO

HERE = Path(__file__).resolve().parent
BASE_PT = HERE / "yolo26n.pt"          # base weights (auto-download to here)
RUNS_DIR = HERE / "runs"               # keep all run artifacts inside the session dir

EPOCHS = 40
IMGSZ = 640
BATCH = 16
DEVICE = 0                              # local GPU; set "cpu" if no CUDA


def main() -> int:
    print(f"[train] base weights: {BASE_PT} (auto-downloads if absent)")
    model = YOLO(str(BASE_PT) if BASE_PT.exists() else "yolo26n.pt")
    results = model.train(
        data="african-wildlife.yaml",   # built-in dataset, auto-downloads ~100 MB
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        device=DEVICE,
        project=str(RUNS_DIR),
        name="train",
        exist_ok=True,
        verbose=True,
    )
    best = RUNS_DIR / "train" / "weights" / "best.pt"
    print(f"[train] DONE. best weights: {best} (exists={best.exists()})")
    print(f"[train] save_dir: {getattr(results, 'save_dir', RUNS_DIR / 'train')}")
    return 0 if best.exists() else 1


if __name__ == "__main__":
    sys.exit(main())

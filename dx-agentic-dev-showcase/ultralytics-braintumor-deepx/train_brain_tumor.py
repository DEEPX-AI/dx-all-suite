#!/usr/bin/env python3
"""Fine-tune (retrain) yolo26n on the Ultralytics brain-tumor dataset on the local GPU.

Adapts the COCO-pretrained general detector into a brain-tumor screening detector for a
medical edge device (MRI/CT scans). The built-in dataset auto-downloads on first use
(~4.21 MB, 893 train / 223 val; classes: negative, positive). Best weights land in
``<session>/runs/retrained/weights/best.pt``.

Run inside venv-dx-runtime (ultralytics + torch-cuda).
"""
import sys
from pathlib import Path

from ultralytics import YOLO

SESSION_DIR = Path(__file__).resolve().parent
EPOCHS = 40
IMGSZ = 640
BATCH = 16
DATA = "brain-tumor.yaml"   # built-in; auto-downloads. nc=2: negative, positive


def main() -> int:
    base = SESSION_DIR / "yolo26n.pt"      # cached weights if already downloaded
    model = YOLO(str(base) if base.exists() else "yolo26n.pt")
    model.train(
        data=DATA,
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        device=0,                          # local GPU
        project=str(SESSION_DIR / "runs"),
        name="retrained",
        exist_ok=True,
        verbose=True,
    )
    best = SESSION_DIR / "runs" / "retrained" / "weights" / "best.pt"
    if not best.exists():
        print(f"ERROR: expected best weights not found at {best}", file=sys.stderr)
        return 1
    print(f"RETRAIN_DONE best={best}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

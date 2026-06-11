#!/usr/bin/env python3
"""Fine-tune (retrain) yolo26n on the Ultralytics medical-pills dataset on the local GPU.

Adapts the COCO-pretrained general detector into a dedicated pharmaceutical
pill detector (single class: ``pill``) for a pill identification/counting station.
The stock yolo26n has no ``pill`` class, so domain fine-tuning rebuilds the head.

Built-in dataset auto-downloads on first use (~8.2 MB, 92 train / 23 val).
Best weights land in ``<session>/runs/retrained/weights/best.pt``.

Run inside venv-dx-runtime (ultralytics + torch-cuda).
"""
import sys
from pathlib import Path

from ultralytics import YOLO

SESSION_DIR = Path(__file__).resolve().parent
EPOCHS = 40
IMGSZ = 640
BATCH = 16
DATA = "medical-pills.yaml"   # built-in; auto-downloads. nc=1, names={0: pill}


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

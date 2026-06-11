#!/usr/bin/env python3
"""train.py — fine-tune yolo26n on the Ultralytics construction-ppe dataset (local GPU).

Per dx-compiler/.deepx/toolsets/ultralytics-train-eval.md §2. Produces best.pt and
records its path in train_result.json. The construction-ppe dataset auto-downloads
on first use.
"""
import json
import os
from pathlib import Path

from ultralytics import YOLO

WORK = Path(__file__).resolve().parent
DATA = "construction-ppe.yaml"   # built-in Ultralytics dataset (auto-downloads)
BASE = "yolo26n.pt"              # COCO-pretrained base (auto-downloads)
EPOCHS = 40
IMGSZ = 640
BATCH = 16


def main():
    # Keep all run artifacts inside the session dir.
    os.chdir(WORK)
    model = YOLO(BASE)
    results = model.train(
        data=DATA,
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        device=0,
        project=str(WORK / "runs"),
        name="train",
        exist_ok=True,
        verbose=True,
    )
    save_dir = Path(results.save_dir)
    best = save_dir / "weights" / "best.pt"
    out = {
        "base_model": BASE,
        "data": DATA,
        "epochs": EPOCHS,
        "imgsz": IMGSZ,
        "batch": BATCH,
        "save_dir": str(save_dir),
        "best_pt": str(best),
        "best_exists": best.exists(),
    }
    (WORK / "train_result.json").write_text(json.dumps(out, indent=2))
    print("TRAIN_RESULT:", json.dumps(out))
    if not best.exists():
        raise SystemExit("ERROR: best.pt not produced")
    print(f"Retrained weights: {best}")


if __name__ == "__main__":
    main()

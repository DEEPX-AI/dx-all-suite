#!/usr/bin/env python3
"""Retrain yolo26n on the Ultralytics african-wildlife dataset on the local GPU.
Modest epoch count (40) for a prompt finish. Writes best.pt under runs/train/weights/."""
import os
import sys

SD = os.path.dirname(os.path.abspath(__file__))
EPOCHS = int(os.environ.get("EPOCHS", "40"))


def main():
    from ultralytics import YOLO
    model = YOLO(os.path.join(SD, "yolo26n.pt"))
    results = model.train(
        data="african-wildlife.yaml",
        epochs=EPOCHS,
        imgsz=640,
        batch=16,
        device=0,
        project=os.path.join(SD, "runs"),
        name="train",
        exist_ok=True,
        verbose=True,
        plots=False,
    )
    best = os.path.join(SD, "runs", "train", "weights", "best.pt")
    print(f"[train] save_dir={getattr(results, 'save_dir', '?')}")
    print(f"[train] best.pt exists={os.path.exists(best)} -> {best}")
    if not os.path.exists(best):
        sys.exit(1)
    print("[train] OK")


if __name__ == "__main__":
    main()

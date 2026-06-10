#!/usr/bin/env python3
"""Acquire base yolo26n.pt into the session dir and ensure the african-wildlife
dataset is downloaded (so both training and NPU val have it). Real artifacts only."""
import os
import shutil
import sys

SD = os.path.dirname(os.path.abspath(__file__))
PT = os.path.join(SD, "yolo26n.pt")


def get_base_model():
    if os.path.exists(PT):
        print(f"[acquire] base model already present: {PT}")
        return
    # Try Ultralytics auto-download (writes to cwd); fall back to a sibling-repo copy.
    try:
        from ultralytics import YOLO
        cwd = os.getcwd()
        os.chdir(SD)
        try:
            YOLO("yolo26n.pt")  # triggers download into SD if online
        finally:
            os.chdir(cwd)
        if os.path.exists(PT):
            print(f"[acquire] downloaded base model -> {PT}")
            return
    except Exception as e:  # noqa: BLE001
        print(f"[acquire] auto-download failed ({e}); trying local copy")
    # Fallback: copy a base yolo26n.pt from a sibling repo (base weights, not a session artifact).
    candidates = []  # portable: rely on Ultralytics auto-download above
    for c in candidates:
        if os.path.exists(c):
            shutil.copy2(c, PT)
            print(f"[acquire] copied base model from {c} -> {PT}")
            return
    raise SystemExit("[acquire] FATAL: could not obtain yolo26n.pt (offline and no local copy)")


def get_dataset():
    from ultralytics.data.utils import check_det_dataset
    info = check_det_dataset("african-wildlife.yaml")
    print(f"[acquire] dataset ready: names={info.get('names')} "
          f"train={info.get('train')} val={info.get('val')}")


if __name__ == "__main__":
    get_base_model()
    get_dataset()
    assert os.path.exists(PT), "yolo26n.pt missing after acquire"
    print("[acquire] OK")
    sys.exit(0)

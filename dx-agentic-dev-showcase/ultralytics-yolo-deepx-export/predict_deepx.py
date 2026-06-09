#!/usr/bin/env python3
"""Run inference on the exported Ultralytics→DeepX model.

Loads the `yolo26n_deepx_model/` directory produced by `export_deepx.sh` and runs
detection through the Ultralytics `dx_engine` backend. The backend converts each
input from normalized-float BCHW [0,1] to uint8 HWC [0,255] before the NPU runtime.
"""
import sys
from pathlib import Path

MODEL_DIR = sys.argv[1] if len(sys.argv) > 1 else "yolo26n_deepx_model"
SOURCE = sys.argv[2] if len(sys.argv) > 2 else "https://ultralytics.com/images/bus.jpg"


def main() -> int:
    if not Path(MODEL_DIR).exists():
        print(f"ERROR: model directory '{MODEL_DIR}' not found. Run export_deepx.sh first.")
        return 1

    try:
        from ultralytics import YOLO
    except ImportError:
        print("ERROR: ultralytics not installed. Activate the venv from export_deepx.sh:")
        print("       source venv/bin/activate")
        return 1

    # Load the exported DeepX model directory (dx_engine runtime loads the .dxnn).
    model = YOLO(MODEL_DIR)
    results = model(SOURCE)

    total = 0
    for r in results:
        n = len(r.boxes)
        total += n
        print(f"Detected {n} objects")
        names = getattr(r, "names", {}) or {}
        for b in r.boxes:
            cls = int(b.cls[0])
            conf = float(b.conf[0])
            print(f"  - {names.get(cls, cls)}: {conf:.2f}")
    print(f"RESULT: {total} detections on {SOURCE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

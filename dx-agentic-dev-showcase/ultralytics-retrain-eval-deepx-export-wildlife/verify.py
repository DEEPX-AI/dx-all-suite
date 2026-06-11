#!/usr/bin/env python3
"""verify.py — Post-compilation verification for the exported DeepX models.

Confirms each <name>_deepx_model/ directory:
  (a) contains a .dxnn binary,
  (b) loads on the dx_engine runtime and runs INT8 inference on a sample wildlife
      image without error, returning a valid Results object.

Exits 0 and prints "RESULT: PASS" only if every present model verifies; exits 1 on any
failure (missing .dxnn, dx_engine import error, inference error). At least the retrained
model must verify for PASS.
"""
import sys
from pathlib import Path

from ultralytics import YOLO

HERE = Path(__file__).resolve().parent
MODEL_DIRS = ["base_yolo26n_deepx_model", "retrained_yolo26n_deepx_model"]


def find_sample() -> str:
    """A wildlife val image from the Ultralytics datasets dir, else a stock URL."""
    try:
        from ultralytics.utils import SETTINGS
        val = Path(SETTINGS["datasets_dir"]) / "african-wildlife" / "images" / "val"
        if val.is_dir():
            imgs = sorted(val.glob("*.jpg"))
            if imgs:
                return str(imgs[0])
    except Exception:
        pass
    return "https://ultralytics.com/images/zidane.jpg"


def main() -> int:
    sample = find_sample()
    print(f"[verify] sample image: {sample}")
    any_present = False
    all_ok = True
    retrained_ok = False

    for name in MODEL_DIRS:
        d = HERE / name
        if not d.is_dir():
            print(f"[verify] SKIP {name}: directory absent")
            continue
        any_present = True
        dxnn = list(d.glob("*.dxnn"))
        if not dxnn:
            print(f"[verify] FAIL {name}: no .dxnn binary in {d}")
            all_ok = False
            continue
        try:
            model = YOLO(str(d))
            results = model(sample, verbose=False)
            n = len(results[0].boxes)
            print(f"[verify] PASS {name}: {dxnn[0].name} loaded; {n} detections on sample")
            if name.startswith("retrained"):
                retrained_ok = True
        except Exception as e:
            print(f"[verify] FAIL {name}: {type(e).__name__}: {e}")
            all_ok = False

    if not any_present:
        print("[verify] FAIL: no exported model directories found")
        print("RESULT: FAIL")
        return 1
    if all_ok and retrained_ok:
        print("RESULT: PASS")
        return 0
    print("RESULT: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())

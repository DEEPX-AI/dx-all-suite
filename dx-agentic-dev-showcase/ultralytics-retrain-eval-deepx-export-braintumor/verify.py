#!/usr/bin/env python3
"""
Verification: fp32 PyTorch vs INT8 DeepX (.dxnn) numerical agreement for the
retrained brain-tumor model on a representative validation image.

Mirrors the dx-compiler "ONNX vs DXNN" verify contract, adapted to the Ultralytics
DeepX path (the fp32 reference is the PyTorch model; the quantized target is the
.dxnn run by the dx_engine backend). PASS requires both backends to run inference
successfully and to agree within tolerance on detection count, with overlapping
predicted classes (or both empty). Exit 0 = PASS, 1 = FAIL.
"""
import os
import sys
import json

SESS = os.path.dirname(os.path.abspath(__file__))
os.chdir(SESS)

RETRAINED_PT = "yolo26n_braintumor.pt"
RETRAINED_DEEPX = "yolo26n_braintumor_deepx_model"
IMGSZ = 640


def fail(msg):
    print(f"VERIFY ERROR: {msg}")
    print("RESULT: FAIL")
    sys.exit(1)


def pick_image():
    # Prefer the sample image recorded by the pipeline; else find a val image.
    mj = os.path.join(SESS, "metrics.json")
    if os.path.exists(mj):
        try:
            src = json.load(open(mj)).get("meta", {}).get("sample_image_source")
            if src and os.path.exists(src):
                return src
        except Exception:
            pass
    try:
        from ultralytics.utils import SETTINGS
        ddir = SETTINGS.get("datasets_dir", ".")
        vd = os.path.join(ddir, "brain-tumor", "images", "val")
        imgs = sorted(f for f in os.listdir(vd)
                      if f.lower().endswith((".jpg", ".jpeg", ".png")))
        if imgs:
            return os.path.join(vd, imgs[0])
    except Exception as e:
        fail(f"could not locate a validation image: {e}")
    fail("no validation image available")


def run(weights, img):
    from ultralytics import YOLO
    res = YOLO(weights)(img, imgsz=IMGSZ, verbose=False)
    boxes = res[0].boxes
    n = int(len(boxes))
    cls = sorted({int(c) for c in boxes.cls.tolist()}) if n else []
    return n, cls


def main():
    if not os.path.exists(RETRAINED_PT):
        fail(f"{RETRAINED_PT} missing (run pipeline.py first)")
    if not os.path.isdir(RETRAINED_DEEPX):
        fail(f"{RETRAINED_DEEPX}/ missing (export step did not complete)")

    img = pick_image()
    print(f"verify image: {img}")

    try:
        n_fp32, cls_fp32 = run(RETRAINED_PT, img)
    except Exception as e:
        fail(f"fp32 PyTorch inference failed: {e}")
    print(f"fp32 PyTorch : {n_fp32} boxes, classes={cls_fp32}")

    try:
        n_int8, cls_int8 = run(RETRAINED_DEEPX, img)
    except Exception as e:
        fail(f"INT8 DeepX inference failed: {e}")
    print(f"INT8 DeepX   : {n_int8} boxes, classes={cls_int8}")

    # Tolerance: detection count within max(2, 60% of fp32 count); classes overlap
    # (or both empty). INT8 quantization can shift marginal/low-confidence boxes.
    tol = max(2, int(round(0.6 * n_fp32)))
    count_ok = abs(n_fp32 - n_int8) <= tol
    class_ok = (not cls_fp32 and not cls_int8) or bool(set(cls_fp32) & set(cls_int8))

    print(f"count_diff={abs(n_fp32 - n_int8)} (tol={tol}) -> {'OK' if count_ok else 'FAIL'}")
    print(f"class_overlap -> {'OK' if class_ok else 'FAIL'}")

    if count_ok and class_ok:
        print("RESULT: PASS")
        sys.exit(0)
    print("RESULT: FAIL")
    sys.exit(1)


if __name__ == "__main__":
    main()

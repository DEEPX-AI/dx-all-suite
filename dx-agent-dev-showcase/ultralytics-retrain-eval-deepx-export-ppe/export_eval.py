#!/usr/bin/env python3
"""export_eval.py — export base + retrained yolo26n to DeepX and run the 4-way eval.

Per dx-compiler/.deepx/toolsets/ultralytics-train-eval.md §3-§5 and
ultralytics-deepx-export.md. Measures (mAP50-95, mAP50, FPS) for four points:
  base .pt (fp32 GPU), base .dxnn (INT8 NPU),
  retrained .pt (fp32 GPU), retrained .dxnn (INT8 NPU).
Also exports a representative annotated detection -> sample_detect.jpg.
Results are written incrementally to results.json.
"""
import json
import shutil
from pathlib import Path

import cv2
from ultralytics import YOLO
from ultralytics.data.utils import check_det_dataset

WORK = Path(__file__).resolve().parent
DATA = "construction-ppe.yaml"
IMGSZ = 640
BASE_PT = WORK / "yolo26n.pt"            # downloaded by train.py
RESULTS = WORK / "results.json"

results = {"data": DATA, "imgsz": IMGSZ}


def save_results():
    RESULTS.write_text(json.dumps(results, indent=2))


def eval_model(ref, device, label):
    """Run model.val and return accuracy + speed metrics."""
    print(f"\n=== EVAL [{label}] ref={ref} device={device} ===", flush=True)
    m = YOLO(str(ref))
    metrics = m.val(data=DATA, imgsz=IMGSZ, device=device, verbose=False, plots=False)
    inf_ms = float(metrics.speed.get("inference", 0.0))
    rec = {
        "map": float(metrics.box.map),       # mAP50-95
        "map50": float(metrics.box.map50),
        "map75": float(metrics.box.map75),
        "inference_ms": inf_ms,
        "fps": (1000.0 / inf_ms) if inf_ms > 0 else 0.0,
    }
    print(f"[{label}] mAP50-95={rec['map']:.4f} mAP50={rec['map50']:.4f} "
          f"inf={inf_ms:.2f}ms FPS={rec['fps']:.1f}", flush=True)
    return rec


def export_deepx(pt_path, out_name):
    """Export a .pt to a DeepX model dir (INT8 enforced); return the dir path."""
    print(f"\n=== EXPORT deepx [{out_name}] from {pt_path} ===", flush=True)
    exported = YOLO(str(pt_path)).export(format="deepx", imgsz=IMGSZ, data=DATA)
    src = Path(exported)
    if src.is_file():            # some versions return the .dxnn path
        src = src.parent
    dst = WORK / out_name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.move(str(src), str(dst))
    dxnn = list(dst.glob("*.dxnn"))
    print(f"[{out_name}] dir={dst} dxnn={[p.name for p in dxnn]}", flush=True)
    return dst


def make_sample(retrained_pt):
    """Run retrained model on a representative val image; save annotated jpg."""
    print("\n=== SAMPLE detection (retrained .pt) ===", flush=True)
    d = check_det_dataset(DATA)
    val_dir = Path(d["val"])
    imgs = sorted(p for p in val_dir.rglob("*")
                  if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    m = YOLO(str(retrained_pt))
    best_img, best_n, best_res = None, -1, None
    for p in imgs[:25]:                       # pick the image with the most detections
        r = m(str(p), imgsz=IMGSZ, verbose=False)[0]
        n = len(r.boxes)
        if n > best_n:
            best_img, best_n, best_res = p, n, r
        if best_n >= 4:
            break
    annotated = best_res.plot()               # BGR ndarray with boxes + labels
    out = WORK / "sample_detect.jpg"
    cv2.imwrite(str(out), annotated)
    print(f"[sample] image={best_img.name} detections={best_n} -> {out}", flush=True)
    results["sample"] = {"image": str(best_img), "num_detections": int(best_n)}
    save_results()


def main():
    tr = json.loads((WORK / "train_result.json").read_text())
    retrained_pt = Path(tr["best_pt"])
    assert retrained_pt.exists(), f"retrained best.pt missing: {retrained_pt}"
    assert BASE_PT.exists(), f"base yolo26n.pt missing: {BASE_PT}"

    # 1-2. fp32 GPU eval
    results["base_pt"] = eval_model(BASE_PT, 0, "base .pt fp32 GPU"); save_results()
    results["retrained_pt"] = eval_model(retrained_pt, 0, "retrained .pt fp32 GPU"); save_results()

    # 3-4. DeepX export (INT8)
    base_dir = export_deepx(BASE_PT, "base_deepx_model")
    retr_dir = export_deepx(retrained_pt, "retrained_deepx_model")
    results["base_dxnn_dir"] = str(base_dir)
    results["retrained_dxnn_dir"] = str(retr_dir); save_results()

    # 5-6. INT8 NPU eval (device=None -> dx_engine backend)
    results["base_dxnn"] = eval_model(base_dir, None, "base .dxnn INT8 NPU"); save_results()
    results["retrained_dxnn"] = eval_model(retr_dir, None, "retrained .dxnn INT8 NPU"); save_results()

    # 7. annotated sample
    make_sample(retrained_pt)

    print("\nALL_RESULTS:", json.dumps(results), flush=True)


if __name__ == "__main__":
    main()

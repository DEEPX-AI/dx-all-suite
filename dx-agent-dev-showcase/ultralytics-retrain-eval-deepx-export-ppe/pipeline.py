#!/usr/bin/env python3
"""
pipeline.py — YOLO26n Construction-PPE domain retrain + DeepX 4-way benchmark.

Adapts the COCO-pretrained yolo26n general detector into a construction/factory
site-safety PPE-compliance detector and measures accuracy + speed in 4 forms.

Stages (all artifacts land in this session directory, which is the cwd):
  1. Train  yolo26n.pt on construction-ppe (helmet/gloves/vest/boots/goggles + negation
     classes, nc=11) for 40 epochs on the local GPU.
  2. Export BOTH base yolo26n.pt and the retrained best.pt with format=deepx
     -> <stem>_deepx_model/ (INT8 enforced, EMA calibration on construction-ppe images).
  3. Evaluate FOUR points with model.val() (mAP50-95 + single-image FPS):
        base .pt (fp32, GPU)      | base .dxnn (INT8, DX-M1 NPU)
        retrained .pt (fp32, GPU) | retrained .dxnn (INT8, DX-M1 NPU)
  4. Save an annotated detection sample from the retrained model on a val image.
  5. Dump results.json (written incrementally so partial progress survives).

FPS = 1000 / speed['inference']  (single-image inference latency, batch=1).
Relocatable: weights are copied into this dir under stable relative names; all paths
are resolved against HERE = the script's own directory.
"""
import json
import shutil
import sys
from pathlib import Path

from ultralytics import YOLO
from ultralytics.data.utils import check_det_dataset

HERE = Path(__file__).resolve().parent
DATA = "construction-ppe.yaml"          # built-in; auto-downloads (nc=11)
IMGSZ = 640
EPOCHS = 40
BATCH_TRAIN = 16
RESULTS_JSON = HERE / "results.json"
RESULTS = {"data": DATA, "imgsz": IMGSZ, "epochs": EPOCHS}


def save_results():
    RESULTS_JSON.write_text(json.dumps(RESULTS, indent=2))
    print(f"[results] wrote {RESULTS_JSON}")


def record(key, metrics):
    """Pull mAP + per-image speed from an Ultralytics val() metrics object."""
    inf_ms = float(metrics.speed["inference"])
    fps = 1000.0 / inf_ms if inf_ms > 0 else 0.0
    names = metrics.names if hasattr(metrics, "names") else {}
    per_class = {}
    try:
        for i, ap in enumerate(metrics.box.maps):   # per-class mAP50-95
            per_class[names.get(i, str(i))] = round(float(ap), 4)
    except Exception:
        pass
    RESULTS[key] = {
        "map5095": round(float(metrics.box.map), 4),
        "map50": round(float(metrics.box.map50), 4),
        "map75": round(float(metrics.box.map75), 4),
        "inference_ms": round(inf_ms, 3),
        "fps": round(fps, 1),
        "per_class_map5095": per_class,
    }
    print(f"[eval] {key}: mAP50-95={RESULTS[key]['map5095']} "
          f"mAP50={RESULTS[key]['map50']} FPS={RESULTS[key]['fps']} "
          f"({RESULTS[key]['inference_ms']} ms/img)")
    save_results()


def main():
    print("=" * 70)
    print("STAGE 1 — Train yolo26n on construction-ppe (40 epochs, GPU)")
    print("=" * 70)
    base_pt = HERE / "yolo26n.pt"
    model = YOLO("yolo26n.pt")            # auto-downloads base COCO weights
    # keep the downloaded base weights in the session dir for export
    if not base_pt.exists() and model.ckpt_path and Path(model.ckpt_path).exists():
        shutil.copy(model.ckpt_path, base_pt)
    train_res = model.train(
        data=DATA, epochs=EPOCHS, imgsz=IMGSZ, batch=BATCH_TRAIN,
        device=0, project=str(HERE / "runs"), name="train", exist_ok=True,
        verbose=True,
    )
    best_pt = Path(train_res.save_dir) / "weights" / "best.pt"
    print(f"[train] best weights: {best_pt}")
    retrained_pt = HERE / "ppe_yolo26n.pt"        # stable relative name (relocatable)
    shutil.copy(best_pt, retrained_pt)
    if not base_pt.exists():
        shutil.copy(YOLO("yolo26n.pt").ckpt_path, base_pt)

    print("=" * 70)
    print("STAGE 2 — Export base + retrained to DeepX (format=deepx, INT8)")
    print("=" * 70)
    # Export lands <stem>_deepx_model/ next to the .pt (i.e. in this session dir).
    base_dir = HERE / "yolo26n_deepx_model"
    retrained_dir = HERE / "ppe_yolo26n_deepx_model"
    print("[export] base yolo26n.pt -> DeepX")
    YOLO(str(base_pt)).export(format="deepx", data=DATA, imgsz=IMGSZ)
    print("[export] retrained ppe_yolo26n.pt -> DeepX")
    YOLO(str(retrained_pt)).export(format="deepx", data=DATA, imgsz=IMGSZ)
    print(f"[export] base dir     : {base_dir} exists={base_dir.exists()}")
    print(f"[export] retrained dir: {retrained_dir} exists={retrained_dir.exists()}")
    RESULTS["base_dxnn_dir"] = base_dir.name
    RESULTS["retrained_dxnn_dir"] = retrained_dir.name
    save_results()

    print("=" * 70)
    print("STAGE 3 — Evaluate 4 points (mAP50-95 + FPS)")
    print("=" * 70)
    # (a) base .pt fp32 GPU
    print("[eval] base .pt fp32 GPU ...")
    record("base_pt_fp32_gpu",
           YOLO(str(base_pt)).val(data=DATA, split="val", imgsz=IMGSZ,
                                  device=0, batch=1, verbose=False))
    # (b) base .dxnn INT8 NPU
    print("[eval] base .dxnn INT8 DX-M1 NPU ...")
    record("base_dxnn_int8_npu",
           YOLO(str(base_dir)).val(data=DATA, split="val", imgsz=IMGSZ,
                                   device="cpu", batch=1, verbose=False))
    # (c) retrained .pt fp32 GPU
    print("[eval] retrained .pt fp32 GPU ...")
    record("retrained_pt_fp32_gpu",
           YOLO(str(retrained_pt)).val(data=DATA, split="val", imgsz=IMGSZ,
                                       device=0, batch=1, verbose=False))
    # (d) retrained .dxnn INT8 NPU
    print("[eval] retrained .dxnn INT8 DX-M1 NPU ...")
    record("retrained_dxnn_int8_npu",
           YOLO(str(retrained_dir)).val(data=DATA, split="val", imgsz=IMGSZ,
                                        device="cpu", batch=1, verbose=False))

    print("=" * 70)
    print("STAGE 4 — Annotated detection sample (retrained model, best-detections image)")
    print("=" * 70)
    d = check_det_dataset(DATA)
    val_path = Path(d["val"])
    imgs = sorted([p for p in val_path.rglob("*.jpg")] +
                  [p for p in val_path.rglob("*.png")])
    if not imgs:
        raise RuntimeError(f"No validation images found under {val_path}")
    # Pick the val image with the MOST detections (deterministic given fixed weights +
    # val set) — a busy, representative scene reads far better as a showcase image than a
    # fixed/middle index. (Scan once on the retrained model, then re-predict with save.)
    sample_model = YOLO(str(retrained_pt))
    sample_src, best_n = imgs[0], -1
    for p in imgs:
        nb = len(sample_model.predict(source=str(p), imgsz=IMGSZ, conf=0.25,
                                      device=0, save=False, verbose=False)[0].boxes)
        if nb > best_n:
            sample_src, best_n = p, nb
    print(f"[sample] best-detections val image: {sample_src} ({best_n} detections)")
    pred = sample_model.predict(
        source=str(sample_src), imgsz=IMGSZ, conf=0.25, device=0,
        save=True, project=str(HERE / "runs"), name="predict", exist_ok=True,
    )
    saved = Path(pred[0].save_dir) / Path(sample_src).name
    out = HERE / "sample_detect.jpg"
    if not saved.exists():
        cand = list(Path(pred[0].save_dir).glob("*"))
        saved = cand[0] if cand else saved
    shutil.copy(saved, out)
    ndet = len(pred[0].boxes)
    RESULTS["sample"] = {"source": Path(sample_src).name, "detections": int(ndet),
                         "output": out.name}
    save_results()
    print(f"[sample] {ndet} detections drawn -> {out}")

    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print(json.dumps(RESULTS, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

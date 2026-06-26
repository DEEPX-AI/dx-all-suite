#!/usr/bin/env python3
"""
YOLO26n pharmaceutical-pill domain retrain + 4-way evaluation pipeline.

Adapts the COCO-pretrained yolo26n general detector into a single-class `pill`
detector for a pharmaceutical pill identification / counting station, then produces a
fair comparison of accuracy (mAP50-95) and speed (FPS) for the base and the retrained
model, each in two forms:
  (a) PyTorch fp32 on the local GPU,
  (b) DeepX export (.dxnn, INT8) on the DX-M1 NPU (via format=deepx).

All stages run sequentially; metrics.json is rewritten after every stage so a late
failure never discards earlier results. Stdout/stderr is captured to session.log by
the launcher (tee). Follows dx-compiler KB toolsets ultralytics-train-eval.md and
ultralytics-deepx-export.md.
"""
import os
import sys
import json
import time
import shutil
import traceback

# Run everything from this script's own directory (the session dir) so that
# auto-downloaded weights and *_deepx_model/ export dirs land here.
SESS = os.path.dirname(os.path.abspath(__file__))
os.chdir(SESS)

DATA = "medical-pills.yaml"   # Ultralytics built-in; auto-downloads on first use
IMGSZ = 640
EPOCHS = 40
BATCH = 16
SEED = 0

BASE_PT = "yolo26n.pt"                  # auto-downloads from Ultralytics if absent
RETRAINED_PT = "yolo26n_pill.pt"        # copied from training best.pt
BASE_DEEPX = "yolo26n_deepx_model"      # export output dir (from BASE_PT stem)
RETRAINED_DEEPX = "yolo26n_pill_deepx_model"
METRICS_JSON = os.path.join(SESS, "metrics.json")

metrics = {
    "meta": {
        "dataset": DATA, "classes": ["pill"],
        "imgsz": IMGSZ, "epochs": EPOCHS, "batch": BATCH, "seed": SEED,
    },
    "points": {},   # key -> {model, form, device, map, map50, map75, inference_ms, fps, ...}
    "stages": {},   # stage name -> status / error
}


def save():
    with open(METRICS_JSON, "w") as f:
        json.dump(metrics, f, indent=2)


def banner(msg):
    print("\n" + "=" * 78, flush=True)
    print(f"=== {msg}", flush=True)
    print("=" * 78, flush=True)


def eval_model(key, weights, model_label, form, device):
    """Run model.val() and record mAP + FPS. device=None lets the DeepX backend
    pick the NPU; device=0 forces the GPU for fp32 PyTorch eval."""
    from ultralytics import YOLO
    banner(f"EVAL [{key}] {model_label} ({form}) on {'NPU' if device is None else 'GPU'}")
    kwargs = dict(data=DATA, imgsz=IMGSZ, verbose=True)
    if device is not None:
        kwargs["device"] = device
    m = YOLO(weights).val(**kwargs)
    inf_ms = float(m.speed["inference"])
    point = {
        "model": model_label,
        "form": form,
        "device": "DX-M1 NPU (INT8)" if device is None else "RTX 5060 Ti GPU (fp32)",
        "weights": str(weights),
        "map": round(float(m.box.map), 5),       # mAP50-95
        "map50": round(float(m.box.map50), 5),
        "map75": round(float(m.box.map75), 5),
        "inference_ms": round(inf_ms, 4),
        "fps": round(1000.0 / inf_ms, 2) if inf_ms > 0 else None,
        "speed_ms": {k: round(float(v), 4) for k, v in m.speed.items()},
    }
    try:
        names = m.names if hasattr(m, "names") else None
        maps = [round(float(x), 5) for x in list(m.box.maps)]
        point["per_class_map"] = (
            {names[i]: maps[i] for i in range(len(maps))} if isinstance(names, dict)
            else maps
        )
    except Exception as e:
        point["per_class_map"] = f"n/a: {e}"
    metrics["points"][key] = point
    print(f"[{key}] mAP50-95={point['map']}  mAP50={point['map50']}  "
          f"FPS={point['fps']}  ({point['inference_ms']} ms/img)", flush=True)
    save()
    return point


def export_deepx(weights):
    from ultralytics import YOLO
    banner(f"EXPORT format=deepx : {weights}")
    out = YOLO(weights).export(format="deepx", data=DATA, imgsz=IMGSZ)
    print(f"exported -> {out}", flush=True)
    return out


def stage(name, fn):
    try:
        fn()
        metrics["stages"][name] = "ok"
    except Exception as e:
        metrics["stages"][name] = f"FAILED: {type(e).__name__}: {e}"
        print(f"!!! STAGE {name} FAILED: {e}", flush=True)
        traceback.print_exc()
    save()


# ---------------------------------------------------------------------------
# Stage 1 — base yolo26n fp32 on GPU (expected ~0 mAP: never saw the pill class)
# ---------------------------------------------------------------------------
def s1_base_fp32():
    eval_model("base_fp32", BASE_PT, "base yolo26n", "PyTorch fp32", device=0)


# ---------------------------------------------------------------------------
# Stage 2 — fine-tune on medical-pills (40 epochs, GPU)
# ---------------------------------------------------------------------------
def s2_train():
    from ultralytics import YOLO
    banner(f"TRAIN yolo26n on {DATA}  epochs={EPOCHS} imgsz={IMGSZ} batch={BATCH}")
    model = YOLO(BASE_PT)
    res = model.train(
        data=DATA, epochs=EPOCHS, imgsz=IMGSZ, batch=BATCH,
        device=0, seed=SEED, project=os.path.join(SESS, "runs"),
        name="train_pill", exist_ok=True, plots=True,
    )
    best = os.path.join(str(res.save_dir), "weights", "best.pt")
    if not os.path.exists(best):
        raise FileNotFoundError(f"best.pt not found at {best}")
    shutil.copy(best, os.path.join(SESS, RETRAINED_PT))
    print(f"best.pt -> {RETRAINED_PT}", flush=True)
    metrics["meta"]["train_save_dir"] = str(res.save_dir)


# ---------------------------------------------------------------------------
# Stage 3 — retrained fp32 on GPU
# ---------------------------------------------------------------------------
def s3_retrained_fp32():
    eval_model("retrained_fp32", RETRAINED_PT, "retrained yolo26n",
               "PyTorch fp32", device=0)


# ---------------------------------------------------------------------------
# Stage 4/5 — export both to DeepX (.dxnn, INT8)
# ---------------------------------------------------------------------------
def s4_export_base():
    export_deepx(BASE_PT)


def s5_export_retrained():
    export_deepx(RETRAINED_PT)


# ---------------------------------------------------------------------------
# Stage 6/7 — INT8 .dxnn evals on DX-M1 NPU
# ---------------------------------------------------------------------------
def s6_base_int8():
    eval_model("base_int8", BASE_DEEPX, "base yolo26n", "DeepX INT8", device=None)


def s7_retrained_int8():
    eval_model("retrained_int8", RETRAINED_DEEPX, "retrained yolo26n",
               "DeepX INT8", device=None)


# ---------------------------------------------------------------------------
# Stage 8 — annotated sample detection image (retrained model, val image)
# ---------------------------------------------------------------------------
def s8_sample_image():
    import cv2
    from ultralytics import YOLO
    from ultralytics.utils import SETTINGS
    banner("SAMPLE annotated detection (retrained .pt on a val image)")
    ddir = SETTINGS.get("datasets_dir", ".")
    val_img_dir = os.path.join(ddir, "medical-pills", "images", "val")
    val_lbl_dir = os.path.join(ddir, "medical-pills", "labels", "val")
    imgs = sorted(
        f for f in os.listdir(val_img_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )
    if not imgs:
        raise FileNotFoundError(f"no val images under {val_img_dir}")

    # Prefer an image whose label file has at least one box so the annotated sample
    # clearly shows a pill detection (single-class dataset: class 0 = pill).
    chosen = imgs[0]
    for f in imgs:
        lbl = os.path.join(val_lbl_dir, os.path.splitext(f)[0] + ".txt")
        if os.path.exists(lbl) and os.path.getsize(lbl) > 0:
            chosen = f
            break
    img_path = os.path.join(val_img_dir, chosen)
    print(f"sample source image: {img_path}", flush=True)

    res = YOLO(RETRAINED_PT)(img_path, imgsz=IMGSZ)
    plotted = res[0].plot()   # BGR ndarray with boxes + class labels
    out = os.path.join(SESS, "sample_detect.jpg")
    cv2.imwrite(out, plotted)
    metrics["meta"]["sample_image_source"] = img_path
    metrics["meta"]["sample_detect"] = out
    metrics["meta"]["sample_num_boxes"] = int(len(res[0].boxes))
    print(f"sample_detect.jpg written ({len(res[0].boxes)} boxes) -> {out}", flush=True)


def main():
    t0 = time.time()
    banner("PIPELINE START")
    stage("1_base_fp32", s1_base_fp32)
    stage("2_train", s2_train)
    stage("3_retrained_fp32", s3_retrained_fp32)
    stage("4_export_base", s4_export_base)
    stage("5_export_retrained", s5_export_retrained)
    stage("6_base_int8", s6_base_int8)
    stage("7_retrained_int8", s7_retrained_int8)
    stage("8_sample_image", s8_sample_image)
    metrics["meta"]["wall_clock_sec"] = round(time.time() - t0, 1)
    save()
    banner(f"PIPELINE DONE in {metrics['meta']['wall_clock_sec']}s")
    print(json.dumps(metrics["stages"], indent=2), flush=True)
    # Non-zero exit if any stage failed, so the launcher/log reflects it.
    failed = [k for k, v in metrics["stages"].items() if v != "ok"]
    if failed:
        print(f"FAILED STAGES: {failed}", flush=True)
        sys.exit(1)
    print("ALL STAGES OK", flush=True)


if __name__ == "__main__":
    main()

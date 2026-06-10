# YOLO26n African-Wildlife — DeepX NPU Showcase Report

**Baseline (stock COCO `yolo26n`) vs Improved (domain-retrained `yolo26n`)** — both
exported to DeepX with `format=deepx` (INT8) and measured on the **DX-M1 NPU** over the
Ultralytics `african-wildlife` validation split.

- **Date:** 2026-06-10
- **Export path:** Ultralytics one-shot `format=deepx` (ONNX → INT8 EMA calibration → `dx_com` → package)
- **Runtime:** `dx_engine` on DX-M1 (firmware v2.5.6, runtime 3.3.2) — sanity check PASSED
- **Eval set:** `african-wildlife` val split — 225 images / 379 instances, 4 classes (buffalo, elephant, rhino, zebra)
- **Inference config:** `imgsz=640`, `batch=1`, INT8

## Results

| Metric | Baseline (stock `yolo26n`, COCO 80-cls) | Improved (retrained, 4-cls) | Δ |
|---|---|---|---|
| **mAP50-95** | 0.0010 | **0.7907** | **+0.7897** |
| **mAP50** | 0.0015 | **0.9432** | +0.9417 |
| **mAP75** | 0.0010 | **0.8581** | +0.8571 |
| **NPU inference FPS** | 56.99 | **80.55** | +23.56 (+41%) |
| NPU inference (ms/img) | 17.55 | 12.42 | −5.13 |

### Per-class mAP50-95 (improved)

| Class | mAP50-95 |
|---|---|
| buffalo | 0.777 |
| elephant | 0.800 |
| rhino | 0.856 |
| zebra | 0.729 |

## Analysis

**Accuracy.** The stock `yolo26n` is COCO-pretrained (80 classes) and is effectively
useless on this domain: **mAP50-95 ≈ 0.001**. The African-wildlife classes
(buffalo/elephant/rhino/zebra) either don't exist in COCO or sit at different class
indices, so the generic model's predictions don't match the domain ground truth at all.
After **40 epochs** of fine-tuning on the African-wildlife train split (~4.1 min on a
single RTX 5060 Ti), the domain model reaches **mAP50-95 = 0.791 / mAP50 = 0.943** on the
NPU — a near-total recovery of detection quality on the target domain.

**Quantization is effectively lossless here.** The retrained model scored
**mAP50-95 = 0.792** in fp32 on the GPU (Ultralytics `train` final validation) and
**0.791** in INT8 on the DX-M1 NPU — a difference of ~0.001. The DeepX INT8 EMA
calibration (run on the domain images) preserved accuracy.

**The domain model is also faster on the NPU (+41% FPS).** Both models share the same
`yolo26n` backbone and were compiled identically, yet the retrained model runs at
**80.6 FPS** vs the baseline's **57.0 FPS** (re-measured on an idle host to rule out
contention). The cause is architectural: the retrained head has `nc=4` while the stock
COCO head has `nc=80`, so the final detection-head convolutions and the on-device decode
process far fewer class channels and candidate outputs per image. Domain specialization
therefore buys **both** higher accuracy **and** lower latency.

## Conclusion

Domain fine-tuning + DeepX export turns a generic detector that is unusable on the target
domain (mAP50-95 0.001) into a deployable DX-M1 NPU model at **mAP50-95 0.79 / mAP50 0.94
and 80 FPS**, with INT8 quantization preserving fp32-level accuracy. This is the core
value proposition of the Ultralytics→DeepX `format=deepx` path for on-device, domain-
optimized detection.

## Artifacts

| Artifact | Path |
|---|---|
| Baseline DeepX model | `yolo26n_baseline_deepx_model/` (`yolo26n.dxnn`, `config.json`, `metadata.yaml`) |
| Improved DeepX model | `yolo26n_improved_deepx_model/` (`best.dxnn`, `config.json`, `metadata.yaml`) |
| Retrained weights | `runs/train/weights/best.pt` |
| Baseline metrics | `metrics_baseline.json` |
| Improved metrics | `metrics_improved.json` |
| Build log | `session.log` |

> Numbers above are read from `metrics_baseline.json` / `metrics_improved.json`, produced
> by `measure.py` running NPU inference through the Ultralytics DeepX backend.

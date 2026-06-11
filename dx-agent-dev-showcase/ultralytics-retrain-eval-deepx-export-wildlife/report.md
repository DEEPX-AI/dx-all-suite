# YOLO26n African-Wildlife — Domain Retrain + DeepX 4-Way Benchmark Report

**Date:** 2026-06-11 · **Session:** `20260611-104801_claude_opus48_yolo26n_retrain_eval`
**Scenario:** wildlife-monitoring / safari camera — detect buffalo, elephant, rhino, zebra.

## Setup

| Item | Value |
|------|-------|
| Base model | `yolo26n.pt` (COCO-pretrained, 80 classes, NMS-free) |
| Dataset | Ultralytics `african-wildlife` (nc=4: buffalo, elephant, rhino, zebra) — 1052 train / 225 val images |
| Fine-tune | 40 epochs, imgsz=640, batch=16, AdamW (auto), GPU = RTX 5060 Ti |
| DeepX export | `format=deepx` (Ultralytics one-shot) → INT8, EMA calibration on domain images, batch=1 |
| NPU | DX-M1 (`dx_engine` 3.3.2, dx_com 2.3.0-rc.5) |
| Eval | `model.val(split=val, imgsz=640, batch=1)`; FPS = 1000 / `speed['inference']` (single-image latency) |

## Results — all four points

| # | Model | Form | Device | mAP50-95 | mAP50 | Inference (ms/img) | FPS |
|---|-------|------|--------|---------:|------:|-------------------:|----:|
| 1 | base `yolo26n` | `.pt` fp32 | GPU | **0.0007** | 0.0010 | 4.338 | 230.5 |
| 2 | base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | **0.0008** | 0.0012 | 16.914 | 59.1 |
| 3 | retrained | `.pt` fp32 | GPU | **0.7928** | 0.9425 | 3.038 | 329.2 |
| 4 | retrained | `.dxnn` INT8 | DX-M1 NPU | **0.7912** | 0.9441 | 12.511 | 79.9 |

### Per-class mAP50-95 (retrained)

| Class | fp32 (GPU) | INT8 (NPU) |
|-------|-----------:|-----------:|
| buffalo | 0.7927 | 0.7851 |
| elephant | 0.7930 | 0.7987 |
| rhino | 0.8387 | 0.8538 |
| zebra | 0.7467 | 0.7271 |

## Analysis

### 1. Accuracy gain from domain fine-tuning

Fine-tuning lifts mAP50-95 from **0.0007 → 0.7928** (fp32 GPU) — effectively from "cannot
detect the domain at all" to a strong **0.79** detector. The base COCO model scores
near-zero because its 80-class head was never trained on these wildlife labels: the
per-class table for the base model shows a flat ~0.0007 smeared across all 80 COCO
classes (the dataset's 4 class indices simply do not line up with COCO's), confirming the
score is noise, not signal. This is exactly why a general detector must be domain-adapted
before deployment on a safari camera. The same gain holds on the NPU: **0.0008 → 0.7912**
INT8. mAP50 reaches **0.94**, so at the looser IoU threshold the retrained model is highly
reliable; the gap to mAP50-95 is the usual tighter-localization penalty.

### 2. INT8 quantization effect (fp32 → DeepX INT8)

The DeepX INT8 export is **effectively lossless** on this domain model:

- retrained mAP50-95: **0.7928 (fp32) → 0.7912 (INT8)** — Δ = **−0.0016** (≈ **0.2 %** relative).
- retrained mAP50: **0.9425 → 0.9441** — actually **+0.0016** (within run-to-run noise).
- Per class the INT8 model is within ±0.02 of fp32, and even *higher* on rhino/elephant.

EMA calibration on representative domain images keeps the quantization error far below the
model's own localization variance, so deploying the INT8 `.dxnn` costs essentially no
accuracy versus the fp32 PyTorch model. (The base model's INT8 vs fp32 numbers are both
noise — 0.0007 vs 0.0008 — and not meaningful to compare.)

### 3. Speed

- **On the NPU**, the retrained `nc=4` model runs **79.9 FPS** vs the stock `nc=80` model's
  **59.1 FPS** (12.5 vs 16.9 ms/img) on the same yolo26n backbone. Fewer detection-head
  class channels ⇒ lighter on-device decode ⇒ **the domain model is ~35 % faster on the
  NPU than the stock model**, independent of accuracy.
- GPU fp32 latency (3–4 ms) is lower than NPU latency in absolute terms, but that is a
  GPU-vs-NPU hardware comparison, not the deployment question. The DX-M1 delivers a
  real-time **~80 FPS** single-stream INT8 detector at essentially fp32 accuracy — the
  deployable result for an embedded safari camera.

## Conclusion

Domain fine-tuning is mandatory (0.0007 → 0.79 mAP50-95). The DeepX INT8 export preserves
that accuracy (−0.2 % relative) while running at ~80 FPS on the DX-M1 NPU, and the smaller
4-class head makes the domain model *faster* on the NPU than the stock 80-class model.
Deployable artifact: `wildlife_yolo26n_deepx_model/wildlife_yolo26n.dxnn`. See
`sample_detect.jpg` for a qualitative detection example.

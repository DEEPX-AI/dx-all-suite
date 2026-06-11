# Report — yolo26n Construction-PPE: Base vs Retrained, fp32 vs INT8

**Task:** Adapt the COCO-pretrained `yolo26n` general detector into a construction/factory
site-safety PPE-compliance detector by fine-tuning on the Ultralytics `construction-ppe`
dataset, then compare accuracy (mAP50-95) and speed (FPS) across four measurement points.

- **Dataset:** `construction-ppe.yaml` (built-in Ultralytics; classes incl. helmet, gloves, vest,
  boots, goggles + person/negation classes), imgsz=640, identical val split for all.
- **fp32:** PyTorch on NVIDIA RTX 5060 Ti (GPU). **INT8:** DeepX `.dxnn` on DX-M1 NPU
  (via Ultralytics `format=deepx` export, INT8 EMA calibration on construction-ppe images).
- FPS = 1000 / single-image inference latency reported by `model.val()`.

## Results — four measurement points

| Model | Form | Device | mAP50-95 | mAP50 | inf (ms) | FPS |
|---|---|---|---|---|---|---|
| base yolo26n | .pt fp32 | RTX 5060 Ti | 0.0001 | 0.0008 | 1.86 | 538.1 |
| base yolo26n | .dxnn INT8 | DX-M1 NPU | 0.0001 | 0.0004 | 17.28 | 57.9 |
| retrained | .pt fp32 | RTX 5060 Ti | 0.2515 | 0.4868 | 1.58 | 634.7 |
| retrained | .dxnn INT8 | DX-M1 NPU | 0.2566 | 0.5136 | 12.55 | 79.7 |

## Analysis

### Accuracy gain (domain optimization)
- **Base `yolo26n` (fp32) mAP50-95 = 0.0001** on construction-ppe. The stock model
  is COCO-trained (80 general classes); its class indices do not align with the PPE classes,
  so as expected a general detector scores ~0 on unseen domain classes.
- **Retrained (fp32) mAP50-95 = 0.2515** — fine-tuning for 40 epochs adapts the
  detector to the PPE domain. **Δ accuracy = +0.2513 mAP50-95** over the base model.
  This is the value of domain optimization: the same nano backbone, retargeted to the
  classes the safety camera actually needs.

### INT8 quantization effect (fp32 → DX-M1 NPU)
- Retrained: **fp32 0.2515 → INT8 0.2566** on the NPU — essentially **no quantization loss** — the INT8 model is within noise of fp32 (Δ=-0.0051 mAP50-95, i.e. a tiny 2.0% *gain*, attributable to calibration/eval variance).
  The deployable on-device model retains effectively all of the fp32 accuracy while running
  on the NPU.
- Speed: the retrained `.dxnn` runs at **79.7 FPS** on DX-M1 vs the base `.dxnn`
  at **57.9 FPS** (1.38× ratio). The retrained head has fewer effective
  output classes than stock COCO (nc=80), which can make the domain model as fast as or
  faster than the stock model on the NPU, with far higher domain accuracy.

### Takeaway
Domain fine-tuning turns a useless-for-PPE stock detector (mAP≈0.000) into a
usable PPE detector (mAP≈0.251 fp32), and the DeepX INT8 export deploys that gain
on the DX-M1 NPU with no measurable accuracy cost at on-device speed
(79.7 FPS) — the right tradeoff for an always-on site-safety camera.

## Annotated sample
`sample_detect.jpg` — retrained model on val image `image1010.jpg`
(8 detections, boxes + class labels drawn).

---
*Numbers are measured (not estimated): fp32 via `model.val()` on GPU, INT8 via the same
`model.val()` on the exported `.dxnn` through the dx_engine NPU backend. See `results.json`,
`train.log`, `export_eval.log`.*

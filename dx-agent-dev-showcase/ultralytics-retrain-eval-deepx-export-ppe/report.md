# Report — yolo26n Construction-PPE: Base vs Retrained, fp32 vs INT8

**Task:** Adapt the COCO-pretrained `yolo26n` general detector into a construction/factory site-safety PPE-compliance detector by fine-tuning on the Ultralytics `construction-ppe` dataset, then compare accuracy (mAP50-95) and speed (FPS) across four measurement points.

- **Dataset:** `construction-ppe.yaml` (built-in Ultralytics; classes: helmet, gloves, vest, boots, goggles + none/Person/no_* negation classes), imgsz=640, identical val split for all four points.
- **Training:** 40 epochs fine-tune from base COCO weights on the local GPU.
- **fp32:** PyTorch on NVIDIA RTX 5060 Ti (GPU). **INT8:** DeepX `.dxnn` on DX-M1 NPU (via Ultralytics `format=deepx` export, INT8 EMA calibration on construction-ppe images).
- FPS = 1000 / single-image inference latency reported by `model.val()`.

## Results — four measurement points

| Model | Form | Device | mAP50-95 | mAP50 | inf (ms) | FPS |
|---|---|---|---|---|---|---|
| base yolo26n | .pt fp32 | RTX 5060 Ti | 0.0001 | 0.0008 | 4.56 | 219.4 |
| base yolo26n | .dxnn INT8 | DX-M1 NPU | 0.0001 | 0.0005 | 21.50 | 46.5 |
| retrained | .pt fp32 | RTX 5060 Ti | 0.2519 | 0.4892 | 2.97 | 336.3 |
| retrained | .dxnn INT8 | DX-M1 NPU | 0.2533 | 0.5058 | 16.05 | 62.3 |

## Analysis

### Accuracy gain (domain optimization)
- **Base `yolo26n` (fp32) mAP50-95 = 0.0001** on construction-ppe. The stock model is COCO-trained (80 general classes); its class indices do not align with the PPE classes, so a general detector scores ~0 on these unseen domain classes.
- **Retrained (fp32) mAP50-95 = 0.2519** — fine-tuning for 40 epochs adapts the detector to the PPE domain. **Δ accuracy = +0.2518 mAP50-95** over the base model. Same nano backbone, retargeted to the classes the safety camera needs.

### INT8 quantization effect (fp32 GPU → INT8 DX-M1 NPU)
- Retrained: **fp32 0.2519 → INT8 0.2533** on the NPU — essentially no quantization loss (Δ = +0.0014 mAP50-95). The DeepX EMA calibration on the domain images preserves accuracy, so the deployable on-device model retains effectively all of the fp32 accuracy.
- Speed: the retrained `.dxnn` runs at **62.3 FPS** on DX-M1 vs the base `.dxnn` at **46.5 FPS** (1.34× ratio). A domain head with fewer effective output classes than stock COCO (nc=80) can make the domain model as fast as or faster than the stock model on the NPU, with far higher domain accuracy.

### Takeaway
Domain fine-tuning turns a useless-for-PPE stock detector (mAP≈0.000) into a usable PPE detector (mAP≈0.252 fp32), and the DeepX INT8 export deploys that gain on the DX-M1 NPU at on-device speed (62.3 FPS) with negligible accuracy cost — the right tradeoff for an always-on site-safety camera.

## Annotated sample
`sample_detect.jpg` — retrained model on val image `image804.jpg` (27 detections, boxes + class labels drawn) — the busiest val scene (5 workers in hi-vis + helmets), selected as the best-detections image.

---
*Numbers are measured (not estimated): fp32 via `model.val()` on GPU, INT8 via the same `model.val()` on the exported `.dxnn` through the dx_engine NPU backend. See `results.json`, `session.log`.*

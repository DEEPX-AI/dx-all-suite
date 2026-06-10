# Pharmaceutical Pill Detection — YOLO26n Domain Retrain & DeepX INT8 Benchmark

**Task:** adapt the COCO-pretrained `yolo26n` general detector into a pharmaceutical **pill identification / counting** model by fine-tuning on the Ultralytics `medical-pills` dataset (single class `pill`), then compare accuracy and speed across four model forms.

- **Base model:** `yolo26n.pt` (COCO, 80 classes) — general detector with **no** `pill` class
- **Retrained model:** `yolo26n` fine-tuned 40 epochs on `medical-pills` (`nc=1`: `pill`)
- **Dataset:** `medical-pills` (92 train / 23 val), imgsz 640
- **DeepX export:** `format=deepx` one-shot — ONNX → INT8 EMA calibration → `dx_com` → `.dxnn`, run on **DX-M1** NPU
- **Metric:** mAP50-95 / mAP50 via `model.val()`; FPS = 1000 / inference-ms/img


## Results — base vs retrained × fp32 (GPU) vs INT8 (DX-M1 NPU)

| # | Model | Form | Device | mAP50-95 | mAP50 | Inf ms/img | FPS |
|---|-------|------|--------|---------:|------:|-----------:|----:|
| 1 | base yolo26n | .pt (fp32) | RTX 5060 Ti GPU | 0.0010 | 0.0041 | 2.75 | 363.98 |
| 2 | base yolo26n | .dxnn (INT8) | DX-M1 NPU | 0.0058 | 0.0142 | 17.74 | 56.37 |
| 3 | retrained yolo26n-pills | .pt (fp32) | RTX 5060 Ti GPU | 0.7583 | 0.9698 | 2.70 | 370.42 |
| 4 | retrained yolo26n-pills | .dxnn (INT8) | DX-M1 NPU | 0.7502 | 0.9690 | 12.90 | 77.52 |

## Analysis

### Accuracy gain from domain retraining

- **fp32 (GPU):** base mAP50-95 = **0.0010** → retrained = **0.7583** (Δ = **+0.7573**).
- **INT8 (DX-M1 NPU):** base mAP50-95 = **0.0058** → retrained = **0.7502** (Δ = **+0.7444**).
- The stock `yolo26n` is COCO-trained and has **never seen** a `pill` class, so its mAP on this domain is effectively zero — it cannot localize/identify pills at all. Fine-tuning rebuilds the detection head for the single `pill` class, which is the entire accuracy gain shown above and what makes a reliable pill-counting station possible.

### INT8 quantization effect (fp32 → DeepX INT8)

- **Retrained:** fp32 = **0.7583** vs INT8 = **0.7502** → quantization loss = **+0.0081** (**1.1%** relative). EMA INT8 calibration on the DX-M1 typically keeps this gap small — a near-lossless deploy.
- **Speed (NPU):** base 80-class `.dxnn` = **56.37 FPS** vs retrained 1-class `.dxnn` = **77.52 FPS** (Δ = **+21.15 FPS**). The single-class (`nc=1`) head has a much lighter on-device decode than the 80-class COCO head, so the domain model is at least as fast — usually faster — on the NPU.

### Takeaway

Domain fine-tuning turns a pill-blind general detector into a working single-class pill detector, and the DeepX INT8 export deploys it on the DX-M1 NPU with only a small accuracy trade-off. The deployable result (#4, retrained INT8 on DX-M1) is the model to ship to a pill identification / counting station.


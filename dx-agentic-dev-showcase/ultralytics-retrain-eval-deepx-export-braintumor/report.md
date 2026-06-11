# Brain-Tumor Screening — YOLO26n Domain Retrain & DeepX INT8 Benchmark

**Task:** adapt the COCO-pretrained `yolo26n` general detector into a brain-tumor screening detector for a medical edge device (MRI/CT scans) by fine-tuning on the Ultralytics `brain-tumor` dataset, then compare accuracy and speed across four model forms.

- **Base model:** `yolo26n.pt` (COCO, 80 classes) — general detector, has never seen brain tumors
- **Retrained model:** `yolo26n` fine-tuned 40 epochs on `brain-tumor` (`nc=2`: negative, positive)
- **Dataset:** `brain-tumor` (893 train / 223 val), imgsz 640
- **DeepX export:** `format=deepx` one-shot — ONNX → INT8 EMA calibration → `dx_com` → `.dxnn`, run on **DX-M1** NPU
- **Metric:** mAP50-95 / mAP50 via `model.val()`; FPS = 1000 / inference-ms/img


## Results — base vs retrained × fp32 (GPU) vs INT8 (DX-M1 NPU)

| # | Model | Form | Device | mAP50-95 | mAP50 | Inf ms/img | FPS |
|---|-------|------|--------|---------:|------:|-----------:|----:|
| 1 | base yolo26n | .pt (fp32) | RTX 5060 Ti GPU | 0.0005 | 0.0010 | 1.80 | 554.83 |
| 2 | base yolo26n | .dxnn (INT8) | DX-M1 NPU | 0.0003 | 0.0009 | 17.20 | 58.14 |
| 3 | retrained yolo26n-brain-tumor | .pt (fp32) | RTX 5060 Ti GPU | 0.4068 | 0.5588 | 1.64 | 609.15 |
| 4 | retrained yolo26n-brain-tumor | .dxnn (INT8) | DX-M1 NPU | 0.4007 | 0.5504 | 12.81 | 78.06 |

## Analysis

### Accuracy gain from domain retraining

- **fp32 (GPU):** base mAP50-95 = **0.0005** → retrained = **0.4068** (Δ = **+0.4063**).
- **INT8 (DX-M1 NPU):** base mAP50-95 = **0.0003** → retrained = **0.4007** (Δ = **+0.4003**).
- The stock `yolo26n` is COCO-trained and has **never seen** brain-tumor classes (`negative`/`positive`), so its mAP on this medical domain is near zero — its 80 COCO classes do not include tumor findings. Fine-tuning rebuilds the detection head for the two tumor classes, which is the entire accuracy gain shown above.

### INT8 quantization effect (fp32 → DeepX INT8)

- **Retrained:** fp32 = **0.4068** vs INT8 = **0.4007** → quantization loss = **+0.0061** (**1.5%** relative). EMA INT8 calibration on the DX-M1 typically keeps this gap small.
- **Speed (NPU):** base 80-class `.dxnn` = **58.14 FPS** vs retrained 2-class `.dxnn` = **78.06 FPS** (Δ = **+19.92 FPS**). A smaller `nc` head usually makes the domain model at least as fast on the NPU as the stock detector.

### Takeaway

Domain fine-tuning turns a useless-on-tumors general detector into a working brain-tumor screening model, and the DeepX INT8 export deploys it on the DX-M1 NPU with only a small accuracy trade-off — the deployable (#4) result is the one to ship to the medical edge device.


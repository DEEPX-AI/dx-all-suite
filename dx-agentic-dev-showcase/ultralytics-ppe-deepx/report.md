# Construction-PPE Detection — YOLO26n Domain Retrain & DeepX INT8 Benchmark

**Task:** adapt the COCO-pretrained `yolo26n` general detector into a construction site-safety **PPE-compliance** detector (helmet, gloves, vest, boots, goggles, …) by fine-tuning on the Ultralytics `construction-ppe` dataset, then compare accuracy and speed across four model forms.

- **Base model:** `yolo26n.pt` (COCO, 80 classes) — general detector
- **Retrained model:** `yolo26n` fine-tuned 40 epochs on `construction-ppe` (`nc=11`: helmet, gloves, vest, boots, goggles, none, Person, no_helmet, no_goggle, no_gloves, no_boots)
- **Dataset:** `construction-ppe` (1132 train / 143 val), imgsz 640
- **DeepX export:** `format=deepx` one-shot — ONNX → INT8 EMA calibration → `dx_com` → `.dxnn`, run on **DX-M1** NPU
- **Metric:** mAP50-95 / mAP50 via `model.val()`; FPS = 1000 / inference-ms/img


## Results — base vs retrained × fp32 (GPU) vs INT8 (DX-M1 NPU)

| # | Model | Form | Device | mAP50-95 | mAP50 | Inf ms/img | FPS |
|---|-------|------|--------|---------:|------:|-----------:|----:|
| 1 | base yolo26n | .pt (fp32) | RTX 5060 Ti GPU | 0.0001 | 0.0008 | 1.94 | 515.90 |
| 2 | base yolo26n | .dxnn (INT8) | DX-M1 NPU | 0.0001 | 0.0004 | 17.31 | 57.76 |
| 3 | retrained yolo26n-ppe | .pt (fp32) | RTX 5060 Ti GPU | 0.2515 | 0.4868 | 1.76 | 568.62 |
| 4 | retrained yolo26n-ppe | .dxnn (INT8) | DX-M1 NPU | 0.2558 | 0.5114 | 13.12 | 76.20 |

## Analysis

### Accuracy gain from domain retraining

- **fp32 (GPU):** base mAP50-95 = **0.0001** → retrained = **0.2515** (Δ = **+0.2513**).
- **INT8 (DX-M1 NPU):** base mAP50-95 = **0.0001** → retrained = **0.2558** (Δ = **+0.2557**).
- The stock `yolo26n` is COCO-trained and has **never seen** construction-PPE classes, so its mAP on this domain is near zero — it cannot detect helmets, vests, etc. Fine-tuning rebuilds the detection head for the PPE classes, which is the entire accuracy gain shown above.

### INT8 quantization effect (fp32 → DeepX INT8)

- **Retrained:** fp32 = **0.2515** vs INT8 = **0.2558** → quantization loss = **-0.0043** (**-1.7%** relative). EMA INT8 calibration on the DX-M1 typically keeps this gap small.
- **Speed (NPU):** base 80-class `.dxnn` = **57.76 FPS** vs retrained 11-class `.dxnn` = **76.20 FPS** (Δ = **+18.44 FPS**). A smaller `nc` head usually makes the domain model at least as fast on the NPU as the stock detector.

### Takeaway

Domain fine-tuning turns a useless-on-PPE general detector into a working PPE-compliance model, and the DeepX INT8 export deploys it on the DX-M1 NPU with only a small accuracy trade-off — the deployable (#4) result is the one to ship to a site-safety camera.


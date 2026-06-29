# Brain-Tumor Edge Detector — YOLO26n Domain Retrain + DeepX 4-Way Evaluation

**Task:** adapt the COCO-pretrained `yolo26n` general detector into a brain-tumor
screening model for a medical edge device (MRI/CT), then compare accuracy and speed
for the base and retrained models in fp32 (GPU) and INT8 `.dxnn` (DX-M1 NPU).

| Item | Value |
|------|-------|
| Dataset | Ultralytics `brain-tumor` — 893 train / 223 val, classes `negative`, `positive` |
| Fine-tune | 40 epochs, imgsz 640, batch 16, seed 0, NVIDIA RTX 5060 Ti |
| fp32 eval device | RTX 5060 Ti GPU (PyTorch) |
| INT8 eval device | DX-M1 NPU via Ultralytics `format=deepx` (INT8 EMA calibration → `dx_com`) |
| Stack | ultralytics 8.4.63 · dx_com 2.3.0-rc.5 · dx_engine 3.3.2 · torch 2.12.0+cu130 |
| Pipeline wall-clock | 349.8 s (~5.8 min) |

## Results — all four points (measured)

| # | Model | Form | Device | mAP50-95 | mAP50 | mAP75 | Latency (ms/img) | FPS |
|---|-------|------|--------|----------|-------|-------|------------------|-----|
| 1 | base `yolo26n` | PyTorch fp32 | RTX 5060 Ti | **0.0005** | 0.0010 | 0.0006 | 1.89 | 529.3 |
| 2 | base `yolo26n` | DeepX **INT8** | DX-M1 NPU | **0.0004** | 0.0011 | 0.0003 | 16.94 | 59.0 |
| 3 | retrained | PyTorch fp32 | RTX 5060 Ti | **0.4068** | 0.5589 | 0.4766 | 1.72 | 582.2 |
| 4 | retrained | DeepX **INT8** | DX-M1 NPU | **0.3980** | 0.5441 | 0.4708 | 11.99 | 83.4 |

Per-class mAP50-95 (retrained): `negative` 0.448, `positive` 0.348 (fp32) →
`negative` 0.448, `positive` 0.348 (INT8 — effectively unchanged).

> Note on FPS: the fp32 numbers are single-image inference latency on the RTX 5060 Ti
> GPU; the INT8 numbers are on-device DX-M1 NPU latency. They are **not** the same
> hardware — the GPU column shows the fp32 reference, the NPU column shows the
> **deployable edge** result. The meaningful edge metric is row 4: **83 FPS at INT8 on
> the NPU**, comfortably real-time for a screening device.

## Analysis

### 1. Accuracy gain from domain retraining (rows 1 → 3, fp32)

The base `yolo26n` is COCO-trained on 80 everyday-object classes and has **never seen a
brain scan**. On the brain-tumor val set it scores **mAP50-95 ≈ 0.0005** — essentially
zero (its 80 COCO classes don't correspond to `negative`/`positive`; the few non-zero
per-class values are matching noise). Fine-tuning for 40 epochs rebuilds the head for the
2 domain classes and lifts accuracy to **mAP50-95 = 0.4068 / mAP50 = 0.5589** — a gain of
**+0.406 mAP50-95** over the base (≈800× higher). This is the core result: the general
detector is unusable for tumor screening, and domain fine-tuning makes it viable.

### 2. INT8 quantization effect (rows 3 → 4, retrained fp32 vs DeepX INT8)

Exporting the retrained model with `format=deepx` (INT8, DX-M1) costs very little
accuracy:

| Metric | fp32 (GPU) | INT8 (NPU) | Δ absolute | Δ relative |
|--------|-----------|-----------|-----------|-----------|
| mAP50-95 | 0.4068 | 0.3980 | −0.0088 | −2.2 % |
| mAP50 | 0.5589 | 0.5441 | −0.0148 | −2.6 % |
| mAP75 | 0.4766 | 0.4708 | −0.0058 | −1.2 % |

The INT8 `.dxnn` retains **~98 % of the fp32 mAP50-95**. EMA calibration on the
brain-tumor images keeps the quantization loss within the small range expected for
detection, so the deployable on-device model is essentially as accurate as the GPU
reference. The verify gate confirms fp32 and INT8 agree on the sample image (both detect
one `positive` box).

### 3. Speed — the smaller domain head is faster on the NPU

On the DX-M1 NPU the **retrained model runs at 83.4 FPS vs the base model's 59.0 FPS**
(11.99 ms vs 16.94 ms/img) — **~41 % faster**. The retrained head has `nc=2` instead of
COCO's `nc=80`, which also shrinks the compiled binary (6.3 MB vs 6.9 MB `.dxnn`). This
matches the KB observation that a smaller domain head makes the domain `.dxnn` faster
on-device than the 80-class stock model — domain optimization improves **both** accuracy
and edge throughput here.

## Conclusion

Domain fine-tuning turns an unusable general detector (mAP50-95 ≈ 0.0005) into a working
brain-tumor screener (**0.4068 fp32 / 0.3980 INT8**), and the DeepX INT8 export deploys on
the DX-M1 NPU at **83 FPS** while keeping **~98 % of the fp32 accuracy**. The deployable
artifact is `yolo26n_braintumor_deepx_model/` (`yolo26n_braintumor.dxnn`). See
`sample_detect.jpg` for an annotated detection (a `positive` tumor box at 0.90 confidence)
and `metrics.json` for the raw measurements.

## Artifacts

- `yolo26n_deepx_model/` — base DeepX INT8 export (`yolo26n.dxnn`)
- `yolo26n_braintumor_deepx_model/` — **retrained** DeepX INT8 export (`yolo26n_braintumor.dxnn`, deployable)
- `yolo26n_braintumor.pt` — retrained fp32 weights; `runs/train_braintumor/` — training run
- `metrics.json` — all four measured points; `sample_detect.jpg` — annotated retrained detection
- `pipeline.py` · `setup.sh` · `run.sh` · `verify.py` · `session.log`

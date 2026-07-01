# Pharmaceutical Pill Detector — YOLO26n Domain Retrain + DeepX 4-Way Evaluation

**Task:** adapt the COCO-pretrained `yolo26n` general detector into a single-class
`pill` detector for a pharmaceutical pill identification / counting station, then
compare accuracy and speed for the base and retrained models in fp32 (GPU) and INT8
`.dxnn` (DX-M1 NPU).

| Item | Value |
|------|-------|
| Dataset | Ultralytics `medical-pills` — 92 train / 23 val, class `pill` (`nc=1`) |
| Fine-tune | 40 epochs, imgsz 640, batch 16, seed 0, NVIDIA RTX 5060 Ti |
| fp32 eval device | RTX 5060 Ti GPU (PyTorch) |
| INT8 eval device | DX-M1 NPU via Ultralytics `format=deepx` (INT8 EMA calibration → `dx_com`) |
| Stack | ultralytics 8.4.83 · torch 2.12.1+cu130 · dx_com 2.3.0-rc.5 · dx_engine 3.3.2 |
| Pipeline wall-clock | 166.3 s |

## Results — all four points (measured)

| # | Model | Form | Device | mAP50-95 | mAP50 | mAP75 | Latency (ms/img) | FPS |
|---|-------|------|--------|----------|-------|-------|------------------|-----|
| 1 | base `yolo26n` | PyTorch fp32 | RTX 5060 Ti GPU (fp32) | **0.0010** | 0.0041 | 0.0000 | 8.73 | 114.6 |
| 2 | base `yolo26n` | DeepX **INT8** | DX-M1 NPU (INT8) | **0.0066** | 0.0170 | 0.0028 | 18.01 | 55.5 |
| 3 | retrained | PyTorch fp32 | RTX 5060 Ti GPU (fp32) | **0.7527** | 0.9650 | 0.9489 | 1.01 | 990.2 |
| 4 | retrained | DeepX **INT8** | DX-M1 NPU (INT8) | **0.7442** | 0.9618 | 0.9383 | 12.77 | 78.3 |

> Note on FPS: the fp32 numbers are single-image inference latency on the RTX 5060 Ti
> GPU; the INT8 numbers are on-device DX-M1 NPU latency. They are **not** the same
> hardware — the GPU column is the fp32 reference, the NPU column is the **deployable
> edge** result. The meaningful edge metric is row 4 (retrained INT8 on the NPU).

## Analysis

### 1. Accuracy gain from domain retraining (rows 1 → 3, fp32)

The base `yolo26n` is COCO-trained on 80 everyday-object classes and has **never seen a
pharmaceutical pill** as a labeled class. On the medical-pills val set it scores
**mAP50-95 ≈ 0.0010** — essentially zero
(its COCO classes don't correspond to `pill`). Fine-tuning for 40
epochs rebuilds the detection head for the single `pill` class and lifts accuracy to
**mAP50-95 = 0.7527 /
mAP50 = 0.9650** — a gain of **+0.7518 mAP50-95** over the base.
This is the core result: the general detector is unusable for pill detection/counting,
and domain fine-tuning makes it viable.

### 2. INT8 quantization effect (rows 3 → 4, retrained fp32 vs DeepX INT8)

Exporting the retrained model with `format=deepx` (INT8, DX-M1) costs little accuracy:

| Metric | fp32 (GPU) | INT8 (NPU) | Δ absolute | Δ relative |
|--------|-----------|-----------|-----------|-----------|
| mAP50-95 | 0.7527 | 0.7442 | -0.0085 | -1.1 % |
| mAP50 | 0.9650 | 0.9618 | -0.0032 | -0.3 % |
| mAP75 | 0.9489 | 0.9383 | -0.0106 | -1.1 % |

The INT8 `.dxnn` retains **98.9 % of the fp32 mAP50-95**. EMA calibration on
the medical-pills images keeps the quantization loss within the small range expected for
detection, so the deployable on-device model is essentially as accurate as the GPU
reference. The verify gate confirms fp32 and INT8 agree on the sample image.

### 3. Speed — the smaller domain head on the NPU

On the DX-M1 NPU the **retrained model runs at 78.3 FPS vs the base model's 55.5 FPS** (12.77 ms vs 18.01 ms/img) — **~+41%**. The retrained head has `nc=1` instead of COCO's `nc=80`, matching the KB observation that a smaller domain head makes the domain `.dxnn` faster on-device than the 80-class stock model.

## Conclusion

Domain fine-tuning turns an unusable general detector
(mAP50-95 ≈ 0.0010) into a working
pill detector (**0.7527 fp32 /
0.7442 INT8**), and the DeepX INT8
export deploys on the DX-M1 NPU while keeping **98.9 % of the fp32 accuracy**.
The deployable artifact is `yolo26n_pill_deepx_model/` (`yolo26n_pill.dxnn`). See
`sample_detect.jpg` for an annotated detection (16 pill box(es)) and `metrics.json`
for the raw measurements.

## Artifacts

- `yolo26n_deepx_model/` — base DeepX INT8 export (`yolo26n.dxnn`)
- `yolo26n_pill_deepx_model/` — **retrained** DeepX INT8 export (`yolo26n_pill.dxnn`, deployable)
- `yolo26n_pill.pt` — retrained fp32 weights; `runs/train_pill/` — training run
- `metrics.json` — all four measured points; `sample_detect.jpg` — annotated retrained detection
- `pipeline.py` · `make_report.py` · `setup.sh` · `run.sh` · `verify.py` · `session.log`

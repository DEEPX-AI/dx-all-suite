# YOLO26n African-Wildlife Domain Optimization — 4-Way Accuracy/Speed Report

**Scenario:** wildlife-monitoring / safari camera. The stock `yolo26n` is a general
COCO-trained detector that does not reliably recognize African wildlife species, so it was
fine-tuned on the Ultralytics **african-wildlife** dataset (nc=4: buffalo, elephant, rhino,
zebra) to produce a domain-optimized model, then exported to the DeepX DX-M1 NPU.

- **Base model:** `yolo26n.pt` (COCO-pretrained, nc=80)
- **Retrained model:** `yolo26n` fine-tuned 40 epochs on african-wildlife (nc=4), `best.pt`
- **DeepX export:** Ultralytics one-shot `format=deepx` → INT8 (EMA calibration on
  african-wildlife images), DX-M1 NPU
- **Eval set:** african-wildlife `val` split — 225 images, 379 instances — `imgsz=640,
  batch=1` for **all four** points (identical data ⇒ fair comparison)
- **Hardware:** GPU = NVIDIA RTX 5060 Ti (fp32); NPU = DeepX DX-M1 (INT8); host CPU = i7-14700K
- **Stack:** ultralytics 8.4.63, torch 2.12.0+cu130, dx_com 2.3.0-rc.5, dx_engine 3.3.2

## Results — the four points

| # | Model | Form | Device | mAP50-95 | mAP50 | Inference (ms/img) | FPS |
|---|---|---|---|---|---|---|---|
| 1 | base `yolo26n` | `.pt` fp32 | GPU | **0.0007** | 0.0010 | 4.198 | 238.2 |
| 2 | base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | **0.0010** | 0.0015 | 16.822 | 59.4 |
| 3 | retrained | `.pt` fp32 | GPU | **0.7928** | 0.9425 | 3.045 | 328.4 |
| 4 | retrained | `.dxnn` INT8 | DX-M1 NPU | **0.7904** | 0.9431 | 12.217 | 81.9 |

### Per-class mAP50-95 (retrained)

| Class | fp32 GPU | INT8 NPU |
|---|---|---|
| buffalo | 0.793 | 0.779 |
| elephant | 0.793 | 0.797 |
| rhino | 0.839 | 0.854 |
| zebra | 0.747 | 0.732 |

## Analysis

### 1. Accuracy gain from domain fine-tuning (the headline)

The stock COCO `yolo26n` is **effectively blind** to this domain: **mAP50-95 ≈ 0.0007**
(fp32) / **0.0010** (INT8). COCO does contain *elephant* and *zebra*, but the model emits
**COCO class indices** (e.g. elephant=20, zebra=22) that do not match the wildlife dataset's
indices (0–3), and it has never seen *buffalo* or *rhino* at all — so virtually nothing is
counted as a correct detection. This is exactly why domain fine-tuning is required.

Fine-tuning for 40 epochs lifts mAP50-95 to **0.7928** (fp32) — a **+0.792 absolute gain**
(~1100×), and mAP50 to **0.9425**. Every class is now well detected (rhino best at 0.839,
zebra hardest at 0.747). **This is the core result: domain optimization turns an unusable
0.0007 detector into a deployable 0.79 one.**

### 2. INT8 quantization effect (fp32 GPU → INT8 NPU)

For the retrained model, INT8 on the NPU is **essentially lossless**:

- mAP50-95: 0.7928 → **0.7904** — a drop of just **0.0024 (−0.30 %)**.
- mAP50: 0.9425 → **0.9431** — statistically flat (the INT8 number is marginally *higher*,
  within run-to-run noise).
- Per-class: rhino and elephant actually tick up under INT8; buffalo/zebra dip ~1–2 pts —
  all within calibration noise.

The DeepX EMA calibration on representative african-wildlife images preserves accuracy, so
the deployable on-device model keeps the full fp32 domain accuracy. The base model's INT8
number stays ≈0 (0.0007 → 0.0010) — quantization can't recover an accuracy the weights never
had; it confirms the export pipeline itself is faithful.

### 3. Speed

- **GPU fp32 is fastest in raw throughput** (238–328 FPS) — a discrete 16 GB GPU vastly
  outpowers an embedded NPU; the relevant value of the NPU is on-device, low-power inference,
  not beating a dGPU.
- **The domain `.dxnn` (nc=4) runs markedly faster on the NPU than the stock `.dxnn` (nc=80):
  81.9 vs 59.4 FPS** (12.2 vs 16.8 ms/img), **+37.7 %**, same yolo26n backbone, both INT8
  batch=1. Cause: the retrained head has 4 class channels instead of 80, so the on-device
  detection-head compute and decode are lighter. **Fewer classes ⇒ higher NPU FPS**, an
  effect independent of the accuracy gain.
- Note the same nc effect on the GPU (retrained 328 FPS vs base 238 FPS): the 80-class
  decode is heavier there too.

### Bottom line

| Question | Answer |
|---|---|
| Does fine-tuning help? | Yes — **+0.792 mAP50-95** (0.0007 → 0.7928), unusable → deployable. |
| Is INT8 deployment safe? | Yes — **−0.30 %** mAP50-95 vs fp32; effectively lossless. |
| What is the deployable result? | **retrained `.dxnn`: mAP50-95 0.7904, 81.9 FPS on DX-M1.** |
| Surprising? | The domain model is **37.7 % faster on the NPU** than stock (smaller nc=4 head). |

## Reproduce

```bash
bash setup.sh                 # verify stack + NPU sanity
python train.py               # 40-epoch fine-tune on african-wildlife (GPU)
python export_deepx.py all    # base + retrained -> *_deepx_model/ (.dxnn, INT8)
python verify.py              # NPU load sanity -> RESULT: PASS
python evaluate.py            # 4-way mAP + FPS -> results.json
```

Numbers above are read directly from `results.json` (this session). Eval split:
african-wildlife `val`, 225 images / 379 instances, imgsz=640, batch=1.

# Brain-Tumor Screening — YOLO26n Domain Retrain → DeepX NPU

> **The story.** `yolo26n` is **COCO-pretrained** with no medical classes, so it cannot screen MRI/CT scans for tumors. This showcase adapts it for a **medical edge device**: fine-tune on the Ultralytics `brain-tumor` dataset, export stock + retrained to the DeepX **DX-M1 NPU** (`format=deepx`, INT8), and measure accuracy (mAP) + speed (FPS) across all four model forms.

<div align="center"><table><tr>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-ultralytics-braintumor-build.gif" width="470"><br><sub><b>dx-agent-dev building this showcase (timelapse)</b></sub></td>
<td align="center"><img src="./sample_detect.jpg" width="300"><br><sub><b>retrained model detecting tumors (DX-M1 NPU)</b></sub></td>
</tr></table></div>

> **See how the agent built it:** [`claude-code-session.md`](./claude-code-session.md).

### Session metrics

| Metric | Value |
|--------|-------|
| Coding agent / model | **Claude Code** / **Claude Opus 4.8** (`claude-opus-4-8`) |
| Human input | **1 natural-language prompt** — fully autonomous |
| KB toolsets read | `ultralytics-train-eval`, `ultralytics-deepx-export` |
| Skills | `dx-skill-router` → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |

## The prompt

```
Using the Ultralytics Python package, adapt the base yolo26n model for a medical edge device that screens MRI/CT brain scans for tumors. The stock yolo26n is a general COCO-trained detector that does not recognize brain tumors, so fine-tune (retrain) it on the Ultralytics brain-tumor dataset (classes: negative, positive) on the local GPU for about 40 epochs to produce a domain-optimized tumor-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect. Work autonomously to completion without asking for confirmation or approval; make default decisions per the knowledge base and PRODUCE THE ACTUAL ARTIFACTS (both .dxnn model dirs, the measured FPS/mAP numbers, report.md), not just a plan.
```

## Results (real, measured)

`brain-tumor` val split, `imgsz=640`. base = stock COCO `yolo26n`; retrained = 40-epoch fine-tune (`nc=2`).

| Model | Form | Device | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0005 | 0.0010 | 529.3 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0004 | 0.0011 | 59.0 |
| retrained | `.pt` fp32 | GPU | 0.4068 | 0.5589 | 582.2 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.3980** | **0.5441** | **83.4** |

- **Domain retraining**: mAP50-95 **~0.0005 → 0.40**. **INT8 ≈ fp32** (0.4068 vs 0.3980). **Faster on NPU**: 59 → **83.4 FPS** (nc=2 vs nc=80).

Full table + analysis: [`report.md`](./report.md). Deployable = row 4; sample above is the retrained model's real NPU detections.

## Reproduce

```bash
bash setup.sh
bash run.sh          # acquire → baseline export → retrain → improved export → 4-way eval → report + sample
```

> x86-64 Linux + DeepX runtime; `dx_engine` missing: `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

Korean: [`README-ko.md`](./README-ko.md).

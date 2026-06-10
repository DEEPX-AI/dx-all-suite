# Brain-Tumor Screening — YOLO26n Domain Retrain → DeepX NPU

> **The story.** `yolo26n` ships **COCO-pretrained** — a *general* 80-class detector
> whose classes contain no medical findings, so it **cannot screen MRI/CT scans for
> tumors**. This showcase adapts it for a **medical edge device** that flags brain
> tumors: it fine-tunes `yolo26n` on the Ultralytics `brain-tumor` dataset
> (`negative`/`positive`), exports both the stock and retrained model to the DeepX
> **DX-M1 NPU** (`format=deepx`, INT8), and measures **accuracy (mAP) + speed (FPS)**
> across all four model forms.

<div align="center">
<img src="../../docs/source/img/dx-agentic-dev-ultralytics-braintumor-build.gif" width="700"><br>
<sub><b>dx-agentic-dev building this showcase (timelapse) — baseline export → GPU retrain → improved export → 4-way GPU/NPU eval → report</b></sub>
</div>

> **See how the agent built it:** [`claude-code-session.md`](./claude-code-session.md).

### Session metrics

| Metric | Value |
|--------|-------|
| Coding agent / model | **Claude Code** (`claude` CLI) / **Claude Opus 4.8** (`claude-opus-4-8`) |
| Human input | **1 natural-language prompt** — fully autonomous |
| Build wall-clock | ~12 min (incl. a 40-epoch GPU retrain) |
| Skills used | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |

## The prompt

```
Using the Ultralytics Python package, adapt the base yolo26n model for a medical edge device that screens MRI/CT brain scans for tumors. The stock yolo26n is a general COCO-trained detector that does not recognize brain tumors, so fine-tune (retrain) it on the Ultralytics brain-tumor dataset (classes: negative, positive) on the local GPU for about 40 epochs to produce a domain-optimized tumor-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect.
```

## Results (real, measured)

`brain-tumor` val split (223 images), `imgsz=640`. base = stock COCO `yolo26n`; retrained = fine-tuned 40 epochs (`nc=2`).

| Model | Form | Device | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0005 | 0.0010 | 554.8 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0003 | 0.0009 | 58.14 |
| retrained | `.pt` fp32 | GPU | 0.4068 | 0.5588 | 609.2 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.4007** | **0.5504** | **78.06** |

- **Domain retraining** lifts mAP50-95 from **~0.0005 → 0.40** — the stock model has no
  medical classes and cannot detect tumors.
- **INT8 ≈ fp32**: retrained fp32 0.4068 vs DX-M1 INT8 0.4007 (~1.5% gap) — DeepX EMA
  calibration preserves accuracy.
- **Domain model is faster on the NPU**: 58.1 → **78.1 FPS** (`nc=2` head vs `nc=80`).

Full table + analysis: [`report.md`](./report.md). The deployable result is row 4.

## Reproduce

```bash
bash setup.sh        # verify the dx_rt venv (ultralytics + dx_engine + dx_com)
bash run.sh          # acquire → export baseline → retrain → export improved → 4-way eval → report
```

Agent-generated scripts: `train_brain_tumor.py`, `export_deepx.py`, `benchmark.py`,
`make_report.py`, `verify.py`. Binaries (`*.pt`/`*.onnx`/`*.dxnn`) + `runs/` are
regenerated, not committed.

> Needs an x86-64 Linux host with the DeepX runtime; if `dx_engine` is missing, build
> dx_rt: `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

Korean: [`README-ko.md`](./README-ko.md).

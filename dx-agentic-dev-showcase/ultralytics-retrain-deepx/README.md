# Wildlife Monitoring — YOLO26n Domain Retrain → DeepX NPU

> **The story.** `yolo26n` ships **COCO-pretrained** — a *general* 80-class detector
> that does not reliably recognize wildlife species, so it is a poor fit for a safari /
> conservation camera. This showcase adapts it for a **wildlife-monitoring scenario**:
> it fine-tunes `yolo26n` on the Ultralytics `african-wildlife` dataset (buffalo,
> elephant, rhino, zebra), exports both the stock and retrained model to the DeepX
> **DX-M1 NPU** (`format=deepx`, INT8), and measures **accuracy (mAP) + speed (FPS)**
> across all four model forms.

<div align="center">
<img src="../../docs/source/img/dx-agentic-dev-ultralytics-retrain-build.gif" width="700"><br>
<sub><b>dx-agentic-dev building this showcase (timelapse) — baseline export → GPU retrain → improved export → 4-way GPU/NPU eval → report</b></sub>
</div>

> **See how the agent built it:** [`claude-code-session.md`](./claude-code-session.md).

### Session metrics

| Metric | Value |
|--------|-------|
| Coding agent / model | **Claude Code** (`claude` CLI) / **Claude Opus 4.8** (`claude-opus-4-8`) |
| Human input | **1 natural-language prompt** — fully autonomous |
| Build wall-clock | ~17 min (incl. a 40-epoch GPU retrain) |
| Skills used | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |

## The prompt

```
Using the Ultralytics Python package, adapt the base yolo26n model for a wildlife-monitoring / safari camera scenario. The stock yolo26n is a general COCO-trained detector that does not reliably recognize African wildlife species, so fine-tune (retrain) it on the Ultralytics african-wildlife dataset (classes: buffalo, elephant, rhino, zebra) on the local GPU for about 40 epochs to produce a domain-optimized model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect.
```

## Results (real, measured)

`african-wildlife` val split, `imgsz=640`. base = stock COCO `yolo26n`; retrained = fine-tuned 40 epochs (`nc=4`).

| Model | Form | Device | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0007 | 0.0010 | 238.2 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0010 | 0.0015 | 59.4 |
| retrained | `.pt` fp32 | GPU | 0.7928 | 0.9425 | 328.4 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.7904** | **0.9431** | **81.9** |

- **Domain retraining** lifts mAP50-95 from **~0.001 → 0.79** (mAP50 **0.94**) — the stock
  model effectively cannot detect these species.
- **INT8 ≈ fp32**: retrained fp32 0.7928 vs DX-M1 INT8 0.7904 — DeepX EMA calibration is
  essentially lossless.
- **Domain model is faster on the NPU**: 59.4 → **81.9 FPS** (`nc=4` head vs `nc=80`).

Full table + per-class mAP + analysis: [`report.md`](./report.md). The deployable result
is row 4.

## Reproduce

```bash
bash setup.sh        # verify the dx_rt venv (ultralytics + dx_engine + dx_com)
bash run.sh          # acquire → export baseline → retrain → export improved → 4-way eval → report
```

Agent-generated scripts: `train.py`, `export_deepx.py`, `evaluate.py`, `verify.py`.
Binaries (`*.pt`/`*.onnx`/`*.dxnn`) + `runs/` are regenerated, not committed.

> Needs an x86-64 Linux host with the DeepX runtime; if `dx_engine` is missing, build
> dx_rt: `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

Korean: [`README-ko.md`](./README-ko.md).

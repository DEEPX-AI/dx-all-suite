# Construction-PPE Detection — YOLO26n Domain Retrain → DeepX NPU

> **The story.** `yolo26n` ships **COCO-pretrained** — a *general* 80-class detector
> (person, car, dog, …) that has **never seen** construction safety gear, so it cannot
> tell whether a worker is wearing a helmet or vest. This showcase adapts it for a
> **construction / factory site-safety camera** that checks **PPE compliance**: it
> fine-tunes `yolo26n` on the Ultralytics `construction-ppe` dataset, exports both the
> stock and the retrained model to the DeepX **DX-M1 NPU** (`format=deepx`, INT8), and
> measures **accuracy (mAP) + speed (FPS)** for all four model forms.

<div align="center">
<img src="../../docs/source/img/dx-agentic-dev-ultralytics-ppe-build.gif" width="700"><br>
<sub><b>dx-agentic-dev building this showcase (timelapse) — baseline export → GPU retrain → improved export → 4-way GPU/NPU eval → report</b></sub>
</div>

> **See how the agent built it:** [`claude-code-session.md`](./claude-code-session.md)
> (renders on GitHub; `.html` opens locally; `.jsonl` is the stream log).

### Session metrics

| Metric | Value |
|--------|-------|
| Coding agent / model | **Claude Code** (`claude` CLI) / **Claude Opus 4.8** (`claude-opus-4-8`) |
| Human input | **1 natural-language prompt** — fully autonomous |
| Build wall-clock | ~14 min (incl. a 40-epoch GPU retrain) |
| Skills used | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |

## The prompt

```
Using the Ultralytics Python package, adapt the base yolo26n model for a construction/factory site-safety camera that checks PPE (personal protective equipment) compliance. The stock yolo26n is a general COCO-trained detector that does not recognize construction PPE items, so fine-tune (retrain) it on the Ultralytics construction-ppe dataset (classes: helmet, gloves, vest, boots, goggles) on the local GPU for about 40 epochs to produce a domain-optimized PPE-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect.
```

## Results (real, measured)

`construction-ppe` val split (143 images), `imgsz=640`. base = stock COCO `yolo26n`; retrained = fine-tuned 40 epochs (`nc=11`).

| Model | Form | Device | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0001 | 0.0008 | 515.9 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0001 | 0.0004 | 57.76 |
| retrained | `.pt` fp32 | GPU | 0.2515 | 0.4868 | 568.6 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.2558** | **0.5114** | **76.20** |

- **Domain retraining** lifts mAP50-95 from **0.0001 → ~0.25** (the stock model cannot
  detect PPE at all).
- **INT8 ≈ fp32**: retrained fp32 0.2515 vs DX-M1 INT8 0.2558 — DeepX EMA calibration is
  effectively lossless here.
- **Domain model is faster on the NPU**: 57.8 → **76.2 FPS** — the `nc=11` head decodes
  far fewer channels than the stock `nc=80` head.

Full table + analysis: [`report.md`](./report.md). The deployable result is row 4 (the
retrained `.dxnn` on the DX-M1).

## Reproduce

```bash
bash setup.sh        # verify the dx_rt venv (ultralytics + dx_engine + dx_com)
bash run.sh          # acquire → export baseline → retrain → export improved → 4-way eval → report
```

Agent-generated scripts: `train_ppe.py` (retrain), `export_deepx.py` (`format=deepx`),
`benchmark.py` (mAP+FPS on GPU/NPU), `make_report.py`, `verify.py`. Model binaries
(`*.pt`/`*.onnx`/`*.dxnn`) and `runs/` are regenerated, not committed.

> Needs an x86-64 Linux host with the DeepX runtime; if `dx_engine` is missing, build
> dx_rt: `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

Korean: [`README-ko.md`](./README-ko.md).

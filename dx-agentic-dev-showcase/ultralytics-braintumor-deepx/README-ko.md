# 뇌종양 스크리닝 — YOLO26n 도메인 재학습 → DeepX NPU

> **스토리.** `yolo26n`은 **COCO 사전학습** — 의료 소견이 없는 *범용* 80클래스 detector라
> **MRI/CT에서 종양을 스크리닝할 수 없습니다**. 이 showcase는 그것을 **의료 edge
> 디바이스**(뇌종양 탐지)용으로 적응시킵니다: Ultralytics `brain-tumor` 데이터셋
> (`negative`/`positive`)으로 `yolo26n`을 fine-tune하고, stock·재학습 모델을 모두 DeepX
> **DX-M1 NPU**(`format=deepx`, INT8)로 export한 뒤 네 가지 형태 전부에 대해
> **정확도(mAP)+속도(FPS)**를 측정합니다.

<div align="center">
<img src="../../docs/source/img/dx-agentic-dev-ultralytics-braintumor-build.gif" width="700"><br>
<sub><b>dx-agentic-dev가 이 showcase를 만드는 과정 (timelapse) — baseline export → GPU 재학습 → improved export → 4-way GPU/NPU 평가 → report</b></sub>
</div>

> **에이전트가 만든 과정 보기:** [`claude-code-session.md`](./claude-code-session.md).

### 세션 메트릭

| 항목 | 값 |
|--------|-------|
| Coding agent / model | **Claude Code** (`claude` CLI) / **Claude Opus 4.8** (`claude-opus-4-8`) |
| 사람 입력 | **자연어 프롬프트 1개** — 완전 자율 |
| Build 소요 | ~12분 (40-epoch GPU 재학습 포함) |
| 사용 skill | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |

## 프롬프트

```
Using the Ultralytics Python package, adapt the base yolo26n model for a medical edge device that screens MRI/CT brain scans for tumors. The stock yolo26n is a general COCO-trained detector that does not recognize brain tumors, so fine-tune (retrain) it on the Ultralytics brain-tumor dataset (classes: negative, positive) on the local GPU for about 40 epochs to produce a domain-optimized tumor-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect.
```

## 결과 (실측)

`brain-tumor` val split(223장), `imgsz=640`. base = stock COCO `yolo26n`; retrained = 40-epoch fine-tune(`nc=2`).

| 모델 | 형태 | 디바이스 | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0005 | 0.0010 | 554.8 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0003 | 0.0009 | 58.14 |
| retrained | `.pt` fp32 | GPU | 0.4068 | 0.5588 | 609.2 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.4007** | **0.5504** | **78.06** |

- **도메인 재학습**: mAP50-95 **~0.0005 → 0.40**(stock은 의료 클래스가 없어 종양 탐지 불가).
- **INT8 ≈ fp32**: 재학습 fp32 0.4068 vs DX-M1 INT8 0.4007(~1.5% 차) — DeepX EMA calibration이 정확도 보존.
- **도메인 모델이 NPU에서 더 빠름**: 58.1 → **78.1 FPS**(`nc=2` vs `nc=80`).

전체 표·분석: [`report.md`](./report.md). 배포 대상은 row 4.

## 재현

```bash
bash setup.sh        # dx_rt venv 확인(ultralytics + dx_engine + dx_com)
bash run.sh          # acquire → baseline export → 재학습 → improved export → 4-way 평가 → report
```

에이전트 생성 스크립트: `train_brain_tumor.py`, `export_deepx.py`, `benchmark.py`,
`make_report.py`, `verify.py`. 바이너리(`*.pt`/`*.onnx`/`*.dxnn`)와 `runs/`는 재생성(미커밋).

> x86-64 Linux + DeepX runtime 필요; `dx_engine` 없으면 dx_rt 빌드:
> `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

English: [`README.md`](./README.md).

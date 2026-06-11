# 알약 탐지 — YOLO26n 도메인 재학습 → DeepX NPU

> **스토리.** `yolo26n`은 **COCO 사전학습** — `pill` 클래스가 없는 *범용* 80클래스
> detector라 약을 안정적으로 탐지/계수하지 못합니다. 이 showcase는 그것을 **제약 알약
> 식별/계수 스테이션**용으로 적응시킵니다: Ultralytics `medical-pills` 데이터셋으로
> `yolo26n`을 fine-tune하고, stock·재학습 모델을 모두 DeepX **DX-M1 NPU**(`format=deepx`,
> INT8)로 export한 뒤 네 가지 형태 전부에 대해 **정확도(mAP)+속도(FPS)**를 측정합니다.

<div align="center">
<img src="../../docs/source/img/dx-agentic-dev-ultralytics-pills-build.gif" width="700"><br>
<sub><b>dx-agentic-dev가 이 showcase를 만드는 과정 (timelapse) — baseline export → GPU 재학습 → improved export → 4-way GPU/NPU 평가 → report</b></sub>
</div>

> **에이전트가 만든 과정 보기:** [`claude-code-session.md`](./claude-code-session.md).

### 세션 메트릭

| 항목 | 값 |
|--------|-------|
| Coding agent / model | **Claude Code** (`claude` CLI) / **Claude Opus 4.8** (`claude-opus-4-8`) |
| 사람 입력 | **자연어 프롬프트 1개** — 완전 자율 |
| Build 소요 | ~9분 (40-epoch GPU 재학습 포함) |
| 사용 skill | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |

## 프롬프트

```
Using the Ultralytics Python package, adapt the base yolo26n model for a pharmaceutical pill identification/counting station. The stock yolo26n is a general COCO-trained detector that does not recognize medical pills as a dedicated class, so fine-tune (retrain) it on the Ultralytics medical-pills dataset (class: pill) on the local GPU for about 40 epochs to produce a domain-optimized pill-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect.
```

## 결과 (실측)

`medical-pills` val split, `imgsz=640`. base = stock COCO `yolo26n`; retrained = 40-epoch fine-tune(`nc=1`).

| 모델 | 형태 | 디바이스 | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0010 | 0.0041 | 364.0 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0058 | 0.0142 | 56.37 |
| retrained | `.pt` fp32 | GPU | 0.7583 | 0.9698 | 370.4 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.7502** | **0.9690** | **77.52** |

- **도메인 재학습**: mAP50-95 **~0.001 → 0.75**(mAP50 **0.97**) — 깔끔한 단일클래스 detector.
- **INT8 ≈ fp32**: 재학습 fp32 0.7583 vs DX-M1 INT8 0.7502 — DeepX EMA calibration 거의 무손실.
- **도메인 모델이 NPU에서 더 빠름**: 56.4 → **77.5 FPS**(`nc=1` vs `nc=80`).

전체 표·분석: [`report.md`](./report.md). 배포 대상은 row 4.

## 재현

```bash
bash setup.sh        # dx_rt venv 확인(ultralytics + dx_engine + dx_com)
bash run.sh          # acquire → baseline export → 재학습 → improved export → 4-way 평가 → report
```

에이전트 생성 스크립트: `train_pills.py`, `export_deepx.py`, `benchmark.py`,
`make_report.py`, `verify.py`. 바이너리와 `runs/`는 재생성(미커밋).

> x86-64 Linux + DeepX runtime 필요; `dx_engine` 없으면 dx_rt 빌드:
> `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

English: [`README.md`](./README.md).

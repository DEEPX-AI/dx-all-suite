# 야생동물 모니터링 — YOLO26n 도메인 재학습 → DeepX NPU

> **스토리.** `yolo26n`은 **COCO 사전학습** — 야생동물 종을 안정적으로 인식하지 못하는
> *범용* 80클래스 detector라 사파리/보전 카메라에 부적합합니다. 이 showcase는 그것을
> **야생동물 모니터링 시나리오**용으로 적응시킵니다: Ultralytics `african-wildlife`
> 데이터셋(buffalo, elephant, rhino, zebra)으로 `yolo26n`을 fine-tune하고, stock·재학습
> 모델을 모두 DeepX **DX-M1 NPU**(`format=deepx`, INT8)로 export한 뒤 네 가지 형태 전부에
> 대해 **정확도(mAP)+속도(FPS)**를 측정합니다.

<div align="center">
<img src="../../docs/source/img/dx-agentic-dev-ultralytics-retrain-build.gif" width="700"><br>
<sub><b>dx-agentic-dev가 이 showcase를 만드는 과정 (timelapse) — baseline export → GPU 재학습 → improved export → 4-way GPU/NPU 평가 → report</b></sub>
</div>

> **에이전트가 만든 과정 보기:** [`claude-code-session.md`](./claude-code-session.md).

### 세션 메트릭

| 항목 | 값 |
|--------|-------|
| Coding agent / model | **Claude Code** (`claude` CLI) / **Claude Opus 4.8** (`claude-opus-4-8`) |
| 사람 입력 | **자연어 프롬프트 1개** — 완전 자율 |
| Build 소요 | ~17분 (40-epoch GPU 재학습 포함) |
| 사용 skill | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |

## 프롬프트

```
Using the Ultralytics Python package, adapt the base yolo26n model for a wildlife-monitoring / safari camera scenario. The stock yolo26n is a general COCO-trained detector that does not reliably recognize African wildlife species, so fine-tune (retrain) it on the Ultralytics african-wildlife dataset (classes: buffalo, elephant, rhino, zebra) on the local GPU for about 40 epochs to produce a domain-optimized model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect.
```

## 결과 (실측)

`african-wildlife` val split, `imgsz=640`. base = stock COCO `yolo26n`; retrained = 40-epoch fine-tune(`nc=4`).

| 모델 | 형태 | 디바이스 | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0007 | 0.0010 | 238.2 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0010 | 0.0015 | 59.4 |
| retrained | `.pt` fp32 | GPU | 0.7928 | 0.9425 | 328.4 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.7904** | **0.9431** | **81.9** |

- **도메인 재학습**: mAP50-95 **~0.001 → 0.79**(mAP50 **0.94**) — stock은 해당 종을 사실상 탐지 불가.
- **INT8 ≈ fp32**: 재학습 fp32 0.7928 vs DX-M1 INT8 0.7904 — DeepX EMA calibration 사실상 무손실.
- **도메인 모델이 NPU에서 더 빠름**: 59.4 → **81.9 FPS**(`nc=4` vs `nc=80`).

전체 표·클래스별 mAP·분석: [`report.md`](./report.md). 배포 대상은 row 4.

## 재현

```bash
bash setup.sh        # dx_rt venv 확인(ultralytics + dx_engine + dx_com)
bash run.sh          # acquire → baseline export → 재학습 → improved export → 4-way 평가 → report
```

에이전트 생성 스크립트: `train.py`, `export_deepx.py`, `evaluate.py`, `verify.py`.
바이너리와 `runs/`는 재생성(미커밋).

> x86-64 Linux + DeepX runtime 필요; `dx_engine` 없으면 dx_rt 빌드:
> `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

English: [`README.md`](./README.md).

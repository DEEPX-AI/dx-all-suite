# 건설 PPE 탐지 — YOLO26n 도메인 재학습 → DeepX NPU

> **스토리.** `yolo26n`은 **COCO 사전학습** 모델 — person/car/dog 등 *범용* 80클래스
> detector라 건설 안전장비를 **본 적이 없어** 작업자가 헬멧/조끼를 착용했는지 판단하지
> 못합니다. 이 showcase는 그것을 **건설/공장 현장 안전 카메라(PPE 준수 점검)**용으로
> 적응시킵니다: Ultralytics `construction-ppe` 데이터셋으로 `yolo26n`을 fine-tune하고,
> stock·재학습 모델을 모두 DeepX **DX-M1 NPU**(`format=deepx`, INT8)로 export한 뒤
> 네 가지 형태 전부에 대해 **정확도(mAP)+속도(FPS)**를 측정합니다.

<div align="center">
<img src="../../docs/source/img/dx-agentic-dev-ultralytics-ppe-build.gif" width="700"><br>
<sub><b>dx-agentic-dev가 이 showcase를 만드는 과정 (timelapse) — baseline export → GPU 재학습 → improved export → 4-way GPU/NPU 평가 → report</b></sub>
</div>

> **에이전트가 만든 과정 보기:** [`claude-code-session.md`](./claude-code-session.md)
> (GitHub 렌더; `.html` 로컬; `.jsonl` stream log).

### 세션 메트릭

| 항목 | 값 |
|--------|-------|
| Coding agent / model | **Claude Code** (`claude` CLI) / **Claude Opus 4.8** (`claude-opus-4-8`) |
| 사람 입력 | **자연어 프롬프트 1개** — 완전 자율 |
| Build 소요 | ~14분 (40-epoch GPU 재학습 포함) |
| 사용 skill | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |

## 프롬프트

```
Using the Ultralytics Python package, adapt the base yolo26n model for a construction/factory site-safety camera that checks PPE (personal protective equipment) compliance. The stock yolo26n is a general COCO-trained detector that does not recognize construction PPE items, so fine-tune (retrain) it on the Ultralytics construction-ppe dataset (classes: helmet, gloves, vest, boots, goggles) on the local GPU for about 40 epochs to produce a domain-optimized PPE-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect.
```

## 결과 (실측)

`construction-ppe` val split(143장), `imgsz=640`. base = stock COCO `yolo26n`; retrained = 40-epoch fine-tune(`nc=11`).

| 모델 | 형태 | 디바이스 | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0001 | 0.0008 | 515.9 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0001 | 0.0004 | 57.76 |
| retrained | `.pt` fp32 | GPU | 0.2515 | 0.4868 | 568.6 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.2558** | **0.5114** | **76.20** |

- **도메인 재학습**: mAP50-95 **0.0001 → ~0.25**(stock은 PPE를 전혀 못 잡음).
- **INT8 ≈ fp32**: 재학습 fp32 0.2515 vs DX-M1 INT8 0.2558 — DeepX EMA calibration 사실상 무손실.
- **도메인 모델이 NPU에서 더 빠름**: 57.8 → **76.2 FPS** — `nc=11` head가 stock `nc=80`보다 채널이 적음.

전체 표·분석: [`report.md`](./report.md). 배포 대상은 row 4(재학습 `.dxnn`, DX-M1).

## 재현

```bash
bash setup.sh        # dx_rt venv 확인(ultralytics + dx_engine + dx_com)
bash run.sh          # acquire → baseline export → 재학습 → improved export → 4-way 평가 → report
```

에이전트 생성 스크립트: `train_ppe.py`(재학습), `export_deepx.py`(`format=deepx`),
`benchmark.py`(GPU/NPU mAP+FPS), `make_report.py`, `verify.py`. 모델 바이너리
(`*.pt`/`*.onnx`/`*.dxnn`)와 `runs/`는 재생성(미커밋).

> x86-64 Linux + DeepX runtime 필요; `dx_engine` 없으면 dx_rt 빌드:
> `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

English: [`README.md`](./README.md).

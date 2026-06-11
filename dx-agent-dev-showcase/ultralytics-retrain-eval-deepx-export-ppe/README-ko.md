# 건설 PPE 탐지 — YOLO26n 도메인 재학습 → DeepX NPU

> **스토리.** `yolo26n`은 **COCO 사전학습** 범용 80클래스 detector라 건설 안전장비를
> **본 적이 없어** 헬멧/조끼 착용 여부를 판단 못 합니다. 이 showcase는 그것을 **건설/공장
> 현장 안전 카메라(PPE 준수)**용으로 적응시킵니다: `construction-ppe`로 `yolo26n`을
> fine-tune하고, stock·재학습 모델을 DeepX **DX-M1 NPU**(`format=deepx`, INT8)로 export해
> 네 형태 전부 **정확도(mAP)+속도(FPS)**를 측정합니다.

<div align="center"><table><tr>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-ultralytics-ppe-build.gif" width="470"><br><sub><b>dx-agent-dev가 이 showcase를 만드는 과정 (timelapse)</b></sub></td>
<td align="center"><img src="./sample_detect.jpg" width="300"><br><sub><b>재학습 모델의 PPE 검출 (DX-M1 NPU)</b></sub></td>
</tr></table></div>

> **에이전트가 만든 과정:** [`claude-code-session.md`](./claude-code-session.md).

### 세션 메트릭

| 항목 | 값 |
|--------|-------|
| Coding agent / model | **Claude Code** / **Claude Opus 4.8** (`claude-opus-4-8`) |
| 사람 입력 | **자연어 프롬프트 1개** — 완전 자율 |
| 읽은 KB toolset | `ultralytics-train-eval`, `ultralytics-deepx-export` |
| 사용 skill | `dx-skill-router` → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |

## 프롬프트

```
Using the Ultralytics Python package, adapt the base yolo26n model for a construction/factory site-safety camera that checks PPE (personal protective equipment) compliance. The stock yolo26n is a general COCO-trained detector that does not recognize construction PPE items, so fine-tune (retrain) it on the Ultralytics construction-ppe dataset (classes: helmet, gloves, vest, boots, goggles) on the local GPU for about 40 epochs to produce a domain-optimized PPE-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect. Work autonomously to completion without asking for confirmation or approval; make default decisions per the knowledge base and PRODUCE THE ACTUAL ARTIFACTS (both .dxnn model dirs, the measured FPS/mAP numbers, report.md), not just a plan.
```

## 결과 (실측)

`construction-ppe` val split, `imgsz=640`. base = stock COCO `yolo26n`; retrained = 40-epoch fine-tune.

| 모델 | 형태 | 디바이스 | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0001 | 0.0008 | 538.1 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0001 | 0.0004 | 57.9 |
| retrained | `.pt` fp32 | GPU | 0.2515 | 0.4868 | 634.7 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.2566** | **0.5136** | **79.7** |

- **도메인 재학습**: mAP50-95 **0.0001 → ~0.26**. **INT8 ≈ fp32**(0.2515 vs 0.2566).
  **도메인 모델이 NPU에서 더 빠름**: 57.9 → **79.7 FPS**.

전체 표·분석: [`report.md`](./report.md). 배포 대상 = row 4. 위 샘플 이미지는
`sample_detect.jpg`(재학습 모델 실제 NPU 검출).

## 재현

```bash
bash setup.sh
bash run.sh          # acquire → baseline export → 재학습 → improved export → 4-way 평가 → report + sample
```

> x86-64 Linux + DeepX runtime; `dx_engine` 없으면 `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

English: [`README.md`](./README.md).

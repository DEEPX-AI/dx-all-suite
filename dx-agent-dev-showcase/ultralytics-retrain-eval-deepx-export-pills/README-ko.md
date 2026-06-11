# 의약품 알약 검사 — YOLO26n Domain Retrain → DeepX NPU

> **스토리.** `yolo26n`은 **COCO 사전학습** 모델이라 "사람", "자동차", "개"는 알아도 의약품 알약은 검출 못 합니다. 이 showcase는 **제약 검사/카운팅 edge 디바이스**용으로 적응시킵니다: `medical-pills`로 fine-tune하고 stock·재학습을 DeepX **DX-M1 NPU**(`format=deepx`, INT8)로 export해 네 형태 전부 정확도(mAP)+속도(FPS)를 측정.

<div align="center"><table><tr>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-ultralytics-pills-build.gif" width="470"><br><sub><b>dx-agent-dev가 이 showcase를 만드는 과정 (timelapse)</b></sub></td>
<td align="center"><img src="./sample_detect.jpg" width="300"><br><sub><b>재학습 모델의 알약 검출 (DX-M1 NPU)</b></sub></td>
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
Using the Ultralytics Python package, adapt the base yolo26n model for a pharmaceutical pill identification/counting station. The stock yolo26n is a general COCO-trained detector that does not recognize medical pills as a dedicated class, so fine-tune (retrain) it on the Ultralytics medical-pills dataset (class: pill) on the local GPU for about 40 epochs to produce a domain-optimized pill-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect. Work autonomously to completion without asking for confirmation or approval; make default decisions per the knowledge base and PRODUCE THE ACTUAL ARTIFACTS (both .dxnn model dirs, the measured FPS/mAP numbers, report.md), not just a plan. Before writing any code, READ the dx-compiler knowledge base toolsets dx-compiler/.deepx/toolsets/ultralytics-train-eval.md and dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md and follow them. Also, after evaluation, save an annotated detection SAMPLE IMAGE — the retrained model run on a representative validation image with bounding boxes + class labels drawn — as sample_detect.jpg in the session directory. Respond in English.
```

## 결과 (실측)

`medical-pills` val split, `imgsz=640`. base = stock COCO `yolo26n`; retrained = 40-epoch fine-tune.

| Model | Form | Device | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0010 | 0.0041 | 118.6 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0083 | 0.0195 | 55.1 |
| retrained | `.pt` fp32 | GPU | 0.7583 | 0.9698 | 986.8 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.7484** | **0.9690** | **78.2** |

- **도메인 재학습**: mAP50-95 **~0.001 → 0.75**, mAP50 **0.97**. **INT8 ≈ fp32**(0.7583 vs 0.7484). **NPU에서 더 빠름**: 55 → **78.2 FPS**(작은 알약 head vs nc=80).

전체 표·분석: [`report.md`](./report.md). 배포 대상 = row 4; 위 샘플은 재학습 모델 실제 NPU 검출.

## 재현

```bash
bash setup.sh
bash run.sh          # acquire → baseline export → retrain → improved export → 4-way eval → report + sample
```

> x86-64 Linux + DeepX runtime; `dx_engine` 없으면: `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

English: [`README.md`](./README.md).

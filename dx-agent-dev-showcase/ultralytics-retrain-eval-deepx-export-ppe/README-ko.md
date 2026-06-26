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
| Coding agent / model | **Claude Code** (`claude` CLI) / **Claude Opus 4.8** (`claude-opus-4-8`) |
| Build wall-clock | **≈ 17.4 min** |
| Agent turns | **102** |
| Output tokens | **≈ 93K** |
| 대략 비용 | **≈ $4.0** |
| Tools | `Bash`×18, `Read`×13, `Write`×8, `Skill`×5 |
| 사람 입력 | **자연어 프롬프트 1개** — 완전 자율 |
| 읽은 KB toolset | `ultralytics-train-eval` |
| 사용 skill | `dx-skill-router` → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |

## 프롬프트

```
Using the Ultralytics Python package, adapt the base yolo26n model for a construction/factory site-safety camera that checks PPE (personal protective equipment) compliance. The stock yolo26n is a general COCO-trained detector that does not recognize construction PPE items, so fine-tune (retrain) it on the Ultralytics construction-ppe dataset (classes: helmet, gloves, vest, boots, goggles) on the local GPU for about 40 epochs to produce a domain-optimized PPE-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect. Work autonomously to completion without asking for confirmation or approval; make default decisions per the knowledge base and PRODUCE THE ACTUAL ARTIFACTS (both .dxnn model dirs, the measured FPS/mAP numbers, report.md), not just a plan.
```

## 결과 (실측)

`construction-ppe` val split, `imgsz=640`. base = stock COCO `yolo26n`; retrained = 40-epoch fine-tune.

| 모델 | 형태 | 디바이스 | mAP50-95 | mAP50 | FPS |
|---|---|---|---:|---:|---:|
| base `yolo26n` | `.pt` fp32 | GPU | 0.0001 | 0.0008 | 219.4 |
| base `yolo26n` | `.dxnn` INT8 | DX-M1 NPU | 0.0001 | 0.0005 | 46.5 |
| retrained | `.pt` fp32 | GPU | 0.2519 | 0.4892 | 336.3 |
| **retrained** | **`.dxnn` INT8** | **DX-M1 NPU** | **0.2533** | **0.5058** | **62.3** |

- **도메인 재학습**: mAP50-95 **0.0001 → ~0.25**. **INT8 ≈ fp32**(0.2519 vs 0.2533).
  **도메인 모델이 NPU에서 더 빠름**: 46.5 → **62.3 FPS** (1.34×).

전체 표·분석: [`report.md`](./report.md). 배포 대상 = row 4. 위 샘플 이미지는
`sample_detect.jpg`(재학습 모델 실제 NPU 검출).

## 파일

| 파일 | 설명 |
|---|---|
| `pipeline.py` | train → export → 4-way 평가 → sample 단일 self-contained pipeline (HERE-relative 경로, 없으면 재생성) |
| `make_report.py` | `results.json`에서 `report.md` 렌더링 |
| `run.sh` | one-command 런처 (`setup.sh`가 정한 interpreter 사용, `session.log`로 tee) |
| `setup.sh` | dx_rt venv 확인 (ultralytics + dx_engine + dx_com) |
| `verify.py` | 생성 artifact 정합성 검사 |
| `report.md` | 4-way 비교 표 + 분석 |
| `results.json` | 실측 mAP/FPS 원본 (per-class mAP 포함) |
| `sample_detect.jpg` | 재학습 모델의 val 이미지 annotated 검출 (실제 NPU) |

이 build는 **self-contained / relocatable**입니다: 단일 `pipeline.py`가 모든 경로를 자기
디렉터리(`HERE = Path(__file__).resolve().parent`) 기준으로 resolve하고 누락된 weight/export를
재생성하므로 build-session absolute path가 박히지 않습니다. binary(`*.pt`, `*.onnx`,
`*_deepx_model/`, `runs/`)는 재생성되며 commit되지 않습니다.

## 재현

```bash
bash setup.sh        # dx_rt venv 확인 (ultralytics + dx_engine + dx_com)
bash run.sh          # acquire → baseline export → 재학습 → improved export → 4-way 평가 → report + sample
```

> x86-64 Linux + DeepX runtime; `dx_engine` 없으면 `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.

English: [`README.md`](./README.md).

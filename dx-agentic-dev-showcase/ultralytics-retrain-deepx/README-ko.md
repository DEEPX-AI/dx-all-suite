# Ultralytics 재학습 → DeepX NPU — dx-agentic-dev로 제작

> **Ultralytics × DEEPX, Option 1(로컬 Python 패키지).** 프롬프트 하나로 코딩 에이전트가
> `yolo26n`을 도메인 데이터셋으로 재학습(로컬 GPU)하고, stock·재학습 모델을 모두
> `format=deepx`로 DeepX export한 뒤 **DX-M1 NPU에서 FPS+정확도(mAP)**를 측정하고
> baseline-vs-improved 리포트를 작성합니다. **이 showcase 자체가
> `dx-agentic-showcase-build` skill + `dx-showcase-gen` 도구로 제작·녹화**되었습니다(자동화 실증).

<div align="center">
<img src="../../docs/source/img/dx-agentic-dev-ultralytics-retrain-build.gif" width="760"><br>
<sub><b>dx-agentic-dev가 이 showcase를 만드는 과정 (timelapse) — baseline export → GPU 재학습 → improved export → NPU FPS/mAP → report</b></sub>
</div>

> **에이전트가 만든 과정 보기:** [`claude-code-session.md`](./claude-code-session.md)
> (GitHub 렌더; `.html` 로컬; `.jsonl` stream log).

### 이 showcase 제작 메트릭

실제 build 세션 transcript(`claude-code-session.*`)에서 추출:

| 항목 | 값 |
|--------|-------|
| Coding agent | **Claude Code** (`claude` CLI, headless `-p`) |
| Model | **Claude Opus 4.8** (`claude-opus-4-8`) |
| 사람 입력 | **자연어 프롬프트 1개** — 완전 자율, 수기 코드 없음 |
| Build 소요 | **~18.5분** (40-epoch GPU 재학습 ≈ 4분 포함) |
| Agent turns | **72** |
| Cost (reported) | **$6.66** |
| 사용 skill | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |

## 프롬프트

> 에이전트에게 준 실제 자연어 프롬프트 (verbatim):

```
Build a domain-optimized YOLO26n detection showcase on DEEPX NPU using the Ultralytics local Python package (Option 1). Do ALL of: (1) BASELINE — take stock yolo26n.pt, export to DeepX with format=deepx, then measure NPU inference FPS and accuracy (mAP50-95) on the Ultralytics african-wildlife validation split; (2) RETRAIN yolo26n on the Ultralytics african-wildlife dataset on the local GPU with a modest epoch count (around 40); (3) IMPROVED — export the retrained model with format=deepx, then measure NPU FPS and accuracy the same way; (4) write report.md comparing baseline vs improved (FPS, mAP) with a short analysis.
```

## 결과 (DX-M1에서 실측)

`african-wildlife` val split — 225 images / 379 instances, 4 classes(buffalo, elephant, rhino, zebra), INT8, `imgsz=640`.

| 지표 | Baseline (stock `yolo26n`, COCO 80-cls) | Improved (재학습, 4-cls) | Δ |
|---|---|---|---|
| **mAP50-95** | 0.001 | **0.791** | **+0.790** |
| **mAP50** | 0.0015 | **0.943** | +0.942 |
| **NPU FPS** | 56.99 | **80.55** | **+41%** |
| NPU ms/img | 17.55 | 12.42 | −5.13 |

- **INT8 ≈ fp32**: 재학습 모델은 fp32(GPU) mAP50-95 0.792 vs INT8(NPU) 0.791 — DeepX EMA
  calibration이 정확도를 보존.
- **도메인 모델이 NPU에서 더 빠름(+41%)**: 같은 `yolo26n` backbone이지만 재학습 head는
  `nc=4`(stock은 `nc=80`)라 NPU가 처리할 class 채널이 훨씬 적음. 도메인 특화가 **정확도와
  지연 둘 다** 개선.

전체 분석·클래스별 mAP는 [`report.md`](./report.md) 참조.

## 파일 (모두 에이전트 생성)

| 파일 | 역할 |
|------|------|
| `acquire.py` | `yolo26n.pt` 획득(Ultralytics auto-download) |
| `train.py` | `african-wildlife`로 `yolo26n` 재학습(로컬 GPU, ~40 epoch) |
| `export_deepx.py` | `.pt` → one-shot `export(format="deepx")` → `*_deepx_model/` |
| `measure.py` | Ultralytics DeepX backend로 NPU FPS+mAP 측정 → `metrics_*.json` |
| `verify.py` | 두 DeepX 모델 존재 + metrics 채워짐 검증 |
| `setup.sh` / `run.sh` | 환경 설정 / 두 모델 재측정 |
| `report.md` | baseline-vs-improved 리포트 |
| `metrics_baseline.json` / `metrics_improved.json` | 측정 수치 |
| `session.log` | 빌드의 실제 명령 출력 |

> 모델 바이너리(`*.pt`/`*.onnx`/`*.dxnn`)와 `runs/` 학습 출력은 **커밋하지 않습니다** —
> 아래 파이프라인으로 재생성됩니다.

## 재현

```bash
bash setup.sh                 # dx_rt venv 확인(ultralytics + dx_engine + dx_com)
python acquire.py             # yolo26n.pt 다운로드
python export_deepx.py yolo26n.pt yolo26n_baseline_deepx_model    # baseline → DeepX
python train.py               # african-wildlife 재학습(GPU)
python export_deepx.py runs/train/weights/best.pt yolo26n_improved_deepx_model
bash run.sh                   # NPU에서 두 모델 측정 → metrics_*.json
```

(`run.sh`는 suite root를 auto-detect하고 `dx-runtime/venv-dx-runtime` 사용; `dx_engine`이
없으면 dx_rt 빌드: `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.)

English: [`README.md`](./README.md).

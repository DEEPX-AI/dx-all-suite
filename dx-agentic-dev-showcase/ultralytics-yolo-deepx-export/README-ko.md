# Ultralytics YOLO → DeepX Export — dx-agentic-dev로 제작

> **Ultralytics × DEEPX 기술 통합 showcase.** 자연어 프롬프트 하나로, 코딩 에이전트
> (Claude Code / Copilot / Cursor / OpenCode / Codex)가 DEEPX knowledge base로
> 라우팅하여 **one-shot `format=deepx` export**를 수행합니다 — Ultralytics YOLO `.pt`를
> 명령 한 번으로 배포 가능한 DeepX NPU 모델(`.dxnn`)로 변환하고 inference까지 실행합니다.

이 폴더는 **self-contained**입니다: 아래 두 스크립트는 `pip`이 있는 x86-64 Linux
호스트라면 dx-all-suite checkout 없이도 실행됩니다.

## 프롬프트

```
내 Ultralytics YOLO26n detection 모델을 DeepX NPU 포맷으로 export하고,
bus 샘플 이미지로 inference를 실행해줘.
```

## 에이전트의 동작 (KB 기반 워크플로)

`.deepx/`에 Ultralytics 통합 지식이 추가되어, 에이전트는 파이프라인을 지어내지 않고
이 프롬프트를 해결합니다:

1. **`/dx-skill-router`** → 모델 컴파일 task로 분류.
2. **Suite 라우팅** → `Ultralytics YOLO .pt → DeepX (format=deepx)` 행이
   `dx-compiler/CLAUDE.md`를 가리킴.
3. **dx-compiler 라우팅** → `Ultralytics, YOLO, .pt, format=deepx` 행 →
   [`.deepx/toolsets/ultralytics-deepx-export.md`](../../dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md).
4. **`/dx-agentic-compiler-convert` Phase 0** → YOLO **detection** 모델 + DeepX
   대상임을 인식하고, 수작업 PT→ONNX→`dxcom` 대신 **one-shot 경로**를 선택.
5. **Export** → `yolo export model=yolo26n.pt format=deepx` → `yolo26n_deepx_model/`.
6. **배포** → `YOLO("yolo26n_deepx_model")`로 `dx_engine` runtime에서 inference.

에이전트는 통합의 hard 제약을 KB에서 알고 있습니다: **x86-64 Linux 전용**,
**detection 모델 전용**, **INT8 강제**, 그리고 출력은 단일 `.dxnn`가 아니라
**디렉토리**(`*_deepx_model/`)라는 점.

## 실행 방법

```bash
# 1. YOLO .pt를 DeepX 모델 디렉토리로 export (x86-64 Linux 전용)
bash export_deepx.sh                 # ./yolo26n_deepx_model/ 생성

# 2. export된 DeepX 모델로 inference 실행
python3 predict_deepx.py             # bus 샘플에 대한 detection 출력
```

`export_deepx.sh`는 venv를 만들고 `ultralytics`(첫 export 시 `dx_com` 자동 설치)를
설치한 뒤 one-shot export를 실행합니다. `predict_deepx.py`는 export된
`yolo26n_deepx_model/`을 로드하여 Ultralytics bus 샘플로 detection을 수행합니다.

> **배포 전제조건 (NPU는 있지만 dx-runtime 미설치인 경우).** 1단계(export)는 `dx_com`을
> pip 자동설치합니다. 2단계(inference)는 **DeepX runtime**(`dxrt-cli` + `dx_engine`)이
> 필요하며, Ultralytics는 이를 **Debian Trixie/arm64에서만** 자동설치합니다. x86-64에서는
> 2단계가 `OSError: dx_engine is not installed. … Please install dx_engine manually and
> try again`를 raise하며, 여기서 "수동 설치"는 **`dx_rt` runtime 설치**를 의미합니다
> (`pip install dx_engine` 금지):
> ```bash
> bash dx-runtime/scripts/sanity_check.sh --dx_rt          # TEXT 출력으로 판정
> bash dx-runtime/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse
> # dx_rt가 dxrt-cli + dx_engine 제공; dx_app/dx_stream은 불필요(제외 → 더 빠름).
> ```
> NPU "Device initialization failed"는 **cold boot**(완전 전원 차단)가 필요합니다.
> `predict_deepx.py`도 이 에러를 감지해 동일한 복구 절차를 출력합니다.

## 예상 출력

생성되는 모델 디렉토리 트리와 detection 요약은
[`expected_output.txt`](./expected_output.txt)를 참고하세요.

## 이 showcase의 기반 지식

| KB 산출물 | 역할 |
|---|---|
| `dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md` | `format=deepx` 권위 reference (API, args, 제약, 배포). |
| `.deepx/templates/fragments/{en,ko}/ultralytics-deepx-export.md` | 모든 플랫폼 instruction에 노출되는 one-shot 경로 요약. |
| `dx-compiler/.deepx/skills/dx-agentic-compiler-convert` Phase 0 | YOLO-detection→DeepX를 one-shot 경로로 라우팅. |
| `dx-compiler/.deepx/memory/common_pitfalls.md` #25 | YOLO detection 모델을 수작업 PT→ONNX→dxcom으로 만들지 말 것. |
| Suite + dx-compiler 라우팅 테이블 | `Ultralytics / YOLO / format=deepx` → dx-compiler. |

권위 upstream 문서: `ultralytics/docs/en/integrations/deepx.md`.

English: [`README.md`](./README.md).

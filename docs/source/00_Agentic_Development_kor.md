# DEEPX Agentic Development - dx-agentic-dev (Beta)

> **베타 기능** — 에이전틱 개발 지원은 현재 활발히 개발 중입니다.
> 스킬 정의와 라우팅 동작은 릴리스 간에 변경될 수 있습니다.

## 소개

> **단 20분, 약 $10의 비용으로, 자연어를 통해 DEEPX NPU용 앱을 완전 자율형으로 만드세요.**

자연어 지시만으로 DEEPX AI 애플리케이션을 구축할 수 있습니다. AI 코딩 에이전트는
DEEPX SDK 생태계를 이해합니다 — GStreamer 파이프라인 구성, `.dxnn` 모델 해석,
InferenceEngine 설정, DxPreprocess/DxInfer 엘리먼트 연결 — 따라서 *무엇*을
원하는지 설명하면 에이전트가 구현 세부사항을 처리합니다.

지원되는 워크플로우:

- `IFactory`, `SyncRunner`, `AsyncRunner`를 사용한 독립형(Standalone) 추론 앱
- DEEPX의 13개 커스텀 엘리먼트를 사용한 6가지 카테고리의 GStreamer 비디오 파이프라인
- dx_app, dx_stream, dx-runtime에 걸친 크로스 프로젝트 빌드
- DX-COM을 통한 ONNX → DXNN 포맷 모델 컴파일 (dx-compiler)

## 데모: 프롬프트 하나로 만든 피트니스 게임 — 완전 자율, 약 20분, 약 $10

**단 20분, 약 $10의 비용으로, 자연어를 통해 DEEPX NPU용 피트니스 게임을 완전 자율형으로
개발할 수 있습니다.** 직접 작성한 코드는 없습니다 — 프롬프트 하나로 AI 코딩 에이전트가
brainstorm → plan → TDD → verify 전체 워크플로우를 스스로 수행하고, 실행 가능한 on-device
NPU 앱을 만들어 냅니다.

그 모습을 보여드리기 위해, 같은 방식으로 만든 **두 가지 미니게임**을 소개합니다. 각각은
전체 빌드 세션 transcript와 함께 suite에 실행 가능한 showcase로 포함되어 있습니다:

| Showcase | 내용 | 빌드 시간 | Agent turn | Output 토큰 | ~비용 |
|----------|------|-----------|------------|-------------|-------|
| **[스쿼트 카운팅 미니게임](../../dx-agentic-dev-showcase/squat-fitness-mini-game/)** | 무릎/엉덩이 각도로 스쿼트 횟수 카운트 + 아케이드 HUD(횟수/점수/DOWN·UP·GOOD!) | ≈ 20분 | 81 | ≈ 85K | ≈ $9.9 |
| **[스트레칭 coach 미니게임](../../dx-agentic-dev-showcase/stretching-coach-mini-game/)** | 애니메이션 **coach 아바타**가 각 목표 포즈를 시연하며 3가지 스트레칭 안내 | ≈ 21분 | 75 | ≈ 85K | ≈ $9.4 |

둘 다 **Claude Code**(모델 **Claude Opus 4.8**)가 **프롬프트 1개**로 완전 자율로,
`dx-skill-router → dx-agentic-brainstorm → dx-swe-writing-plans → dx-agentic-tdd →
dx-agentic-verify` 전체 시퀀스를 실행해 만들었고, 둘 다 **비디오 파일 input과 라이브
카메라 input**(`--video <file>` / `--camera <id>`)을 지원합니다. 앱별 메트릭 + transcript는
각 showcase의 `README.md`에 있습니다.

### Showcase 1 — 스쿼트 카운팅 미니게임

**사용한 프롬프트** (`dx_app` 디렉터리에서 Claude Code에 전달):

> DEEPX NPU에서 yolo26n-pose 모델을 사용해 간단한 스쿼트 카운팅 피트니스 미니게임을
> 만들어줘. 구현과 검증은 `sample/squat_demo.mp4` 샘플 영상으로 진행해줘. 생성된 앱은
> **비디오 파일 input과 라이브 카메라 input을 모두 지원**하고, **실행 시 CLI 옵션으로
> input 소스를 선택**할 수 있어야 해(예: `--video <file>` 또는 `--camera <id>`). 신체
> keypoint(무릎과 엉덩이 각도로 down 다음 up 동작을 인식)를 분석해 스쿼트 횟수를
> 실시간으로 세고, 각 프레임 위에 아케이드 스타일 피트니스 게임 UI(횟수, 목표 횟수,
> 점수, DOWN / UP / GOOD! 피드백 텍스트)를 오버레이해줘. 비디오 파일로 실행할 때는
> 결과를 확인할 수 있도록 주석이 표시된 출력 영상도 저장해줘.

에이전트는 게임 이름을 **"SQUAT CHALLENGE"**로 짓고 HUD에 `yolo26n-pose · DX-M1 NPU`
배지까지 추가했습니다 — 모두 이 프롬프트 하나에서 나온 결과입니다.

<div align="center">
<table>
<tr>
<td align="center"><img src="./img/dx-agentic-dev-squat-build.gif" width="520"><br><sub><b>앱을 빌드하는 에이전트 — brainstorm → plan → TDD → verify (타임랩스)</b></sub></td>
<td align="center"><img src="./img/dx-agentic-dev-squat-gameplay.gif" width="205"><br><sub><b>DX-M1 NPU에서 실행되는 생성된 앱</b></sub></td>
</tr>
</table>
</div>

### Showcase 2 — 스트레칭 coach 미니게임

세 가지 스트레칭을 한 단계씩 안내하는 아케이드 게임으로, 샘플 영상에서 유도한 애니메이션
스틱피겨 **coach 아바타**가 각 목표 포즈를 시연해 사용자가 따라할 수 있게 합니다.

**사용한 프롬프트** (`dx_app` 디렉터리에서 Claude Code에 전달):

> DEEPX NPU에서 yolo26n-pose 모델을 사용해 간단한 아케이드 스타일 스트레칭 미니게임을
> 만들어줘. 게임은 세 가지 스트레칭 포즈를 한 단계씩 안내해: (1) 양팔을 머리 위로 곧게 뻗기,
> (2) 허리를 앞으로 굽히는 forward fold, (3) 한 손으로 머리를 옆으로 당기는 목 스트레칭. 각
> 단계마다 화면 좌상단 패널에 현재 목표 스트레칭을 시연하는 작은 사람 모양 **"coach" 아바타**를
> 그려줘 — 목표 포즈를 취한 깔끔한 스틱피겨를 중립 자세와 목표 포즈 사이에서 **애니메이션**하고,
> 각 목표 형태는 **해당 샘플 영상에서 유도**해. 스트레칭 이름 + 짧은 안내와 HOLD 진행바를
> 표시하고, 사용자가 해당 포즈를 유지하면 다음 단계로, 셋 다 끝나면 클리어해. 앱은 **비디오
> 파일 input과 라이브 카메라 input을 모두 지원**해야 해(`--video <file>` 또는 `--camera <id>`).
> 비디오 파일로 실행하면 주석이 표시된 출력 영상을 저장해.

<div align="center">
<table>
<tr>
<td align="center"><img src="./img/dx-agentic-dev-stretch-build.gif" width="520"><br><sub><b>agent가 스트레칭 게임을 빌드하는 모습 (timelapse)</b></sub></td>
<td align="center"><img src="./img/dx-agentic-dev-stretch-gameplay.gif" width="205"><br><sub><b>생성된 앱이 DX-M1 NPU에서 실행 — coach 아바타 + 3단계</b></sub></td>
</tr>
</table>
</div>

### 에이전트가 수행한 작업

한 번의 프롬프트로, 에이전트는 전체 DEEPX 에이전틱 워크플로우를 스스로 실행했습니다:

1. **`dx-skill-router`** → **`dx-agentic-brainstorm`** — 기존 `yolo26n_pose`
   예제를 살펴보고, 모델과 framework API를 확인한 뒤 design spec을 작성.
2. **`dx-swe-writing-plans`** — 단계별 구현 plan 작성.
3. **`dx-agentic-tdd`** — 앱을 파일 단위로 생성하며 각각 검증.
4. **`dx-agentic-verify`** — framework validator와 새로운 on-NPU 실행을 수행하여,
   앱이 스쿼트를 세고 주석 영상을 저장하는 것을 확인한 후 완료 선언.

결과물은 격리된 session 디렉터리(`dx_app/dx-agentic-dev/<session>/`)에 생성되며
기존 소스에는 전혀 영향을 주지 않습니다.

### 생성된 앱의 구조

에이전트는 dx_app의 **skeleton-first + `IFactory`** 규칙을 따랐습니다 — standalone
스크립트를 작성하지 않았습니다. 생성된 앱은:

- framework의 표준 pose preprocessor/postprocessor를 **재사용**합니다 (DXNN
  모델이 입력 크기를 self-describe하고, YOLO-pose postprocessor가 COCO 17-point
  body keypoint를 출력);
- 게임 로직을 담은 **커스텀 visualizer만** 추가합니다 — 무릎 각도 기반
  **스쿼트 rep counter**(완전한 DOWN→UP 사이클마다 1회)와 프레임 위 HUD
  (횟수 / 목표 / 점수 / DOWN·UP·GOOD! 피드백);
- framework의 **`SyncRunner`**(단일 순차 비디오 → 순차·stateful 카운팅)로
  실행되며, 읽기 → NPU 추론 → visualize → 저장 루프를 처리합니다;
- 게임 튜닝 값(목표 횟수, 무릎 각도 임계값, rep당 점수)을 `config.json`에 두어
  코드 수정 없이 동작을 바꿀 수 있습니다;
- **self-contained & portable**합니다 — `setup.sh`가 공용 framework를 `./common`으로
  vendoring하고 entry 스크립트(`*_sync.py`)가 이 vendored `./common`을 **최우선**으로
  import하므로(`PYTHONPATH` 불필요), 폴더를 dx-all-suite **밖으로 통째로 복사해도**
  동작합니다. 외부 전제는 `dx_engine`(DEEPX 런타임) 하나뿐입니다.

실행은 `./setup.sh`(framework를 `./common`으로 vendoring + 샘플·모델 번들) 후 `./run.sh`로
합니다. `run.sh`는 **relocatable** 런처로 venv fallback chain, 모델 존재 가드,
bundled-sample-first input을 처리합니다. 생성된 `*_sync.py`를 직접 실행할 수도 있으며,
`.dxnn` 모델과 입력 영상을 `--save`와 함께 지정하면 주석이 표시된 출력 영상이 저장됩니다.

> **참고:** dx-agentic-dev는 매 실행마다 새 코드를 생성하므로, 정확한 클래스명·
> 파일명·config 값은 빌드마다 달라집니다. 변하지 않는 것은 위의 **패턴**
> (`IFactory` 재사용 + 커스텀 visualizer + `SyncRunner`)이며, 이 문서가 설명하는
> 것이 바로 그 패턴입니다.

> **재현성(reproducibility) 참고:** 이 빌드는 동일한 프롬프트로 여러 번 반복했으며,
> 매번 독립적으로 스쿼트를 정확히 세는 실행 가능한 앱이 생성되었습니다 — 코드 구조는
> 매번 달랐지만 모두 유효했고, 이는 결과가 암기된 것이 아니라 knowledge base에서
> 재유도(re-derive)됨을 확인해 줍니다.

### 생성된 샘플을 직접 실행해보기

이 데모의 대표 빌드 하나가 **suite에 그대로 포함**되어 있어, 재생성 없이 바로 실행할 수 있습니다:

📂 **[`dx-agentic-dev-showcase/squat-fitness-mini-game/`](../../dx-agentic-dev-showcase/squat-fitness-mini-game/)**
 — 먼저 **[README](../../dx-agentic-dev-showcase/squat-fitness-mini-game/README.md)**부터 보세요.

```bash
cd dx-agentic-dev-showcase/squat-fitness-mini-game

./setup.sh                       # dx_engine venv 탐지 + framework를 ./common으로 vendoring + 샘플·모델 번들
./run.sh                         # 동봉 샘플 비디오 데모 -> annotated output.mp4
./run.sh --camera 0              # 라이브 카메라 (display 필요)
./run.sh --video /path/clip.mp4 --save
```

이 폴더는 **self-contained & portable**합니다 — `setup.sh`가 공용 framework를 `./common`으로
vendoring하므로 dx-all-suite **밖으로 복사해도** 동작합니다(`dx_engine`이 유일한 외부 전제).
샘플 비디오는 showcase에 **동봉**되어 있고, `run.sh`는 venv fallback chain·모델 존재 가드를
갖춘 relocatable 런처라 `yolo26n-pose.dxnn` 모델을 아직 받아야 한다면 명확한 안내를 출력합니다.
dx-agentic-dev는 실행할 때마다 새 코드를 생성하므로, 이 디렉토리의 클래스명·파일명은 위에서
설명한 **패턴**의 한 가지 구체적 인스턴스일 뿐이며, 직접 생성하면 달라질 수 있습니다.

**스트레칭 coach 미니게임** showcase(위 Showcase 2)도 동일하게 실행합니다 —
[`dx-agentic-dev-showcase/stretching-coach-mini-game/`](../../dx-agentic-dev-showcase/stretching-coach-mini-game/)에서
`./setup.sh` 후 `./run.sh`(또는 `./run.sh --camera 0`). 두 showcase의 빌드/실행 메트릭은
상단 표와 각 showcase의 `README.md`에 있습니다.

### agent의 세션 들여다보기 — harness를 어떻게 따랐는가

showcase에는 앱을 만들어 낸 **전체 Claude Code 세션**도 함께 들어 있습니다. 이는 결과가
모델의 즉흥 능력이 아니라 *harness 엔지니어링* — 모델을 이끄는 계층적 `CLAUDE.md` / `.deepx/`
instruction, agent, skill — 에서 얼마나 비롯되는지 가장 직접적으로 확인하는 방법입니다:

- **[`claude-code-session.md`](../../dx-agentic-dev-showcase/squat-fitness-mini-game/claude-code-session.md)**
  — GitHub에서 바로 렌더링됨 *(빠르게 읽기 권장)*.
- **`claude-code-session.html`** — 동일한 transcript를 **로컬 브라우저에서 열면** 더 보기 좋게
  스타일된 형태로 볼 수 있습니다 (GitHub는 HTML을 렌더링하지 않고 소스로 표시함).

transcript를 읽으면 harness가 동작하는 모습을 직접 볼 수 있습니다:

- **Instruction-following** — agent는 suite의 HARD GATE를 준수합니다: `[DX-AGENTIC-DEV: START]`
  / `DONE` 세션 sentinel을 출력하고, 모든 산출물을 격리된 세션 디렉토리 안에 유지하며(기존 소스를
  건드리지 않음), placeholder/stub 코드 작성을 거부합니다.
- **Skill·agent 활용** — 필수 skill 시퀀스를 *언급*만 하는 게 아니라 실제 tool call로 invoke합니다 —
  `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd`
  → `dx-agentic-verify`.
- **실제 추론 과정** — 기존 `yolo26n_pose` 예제를 어떻게 살펴보고, knowledge base에서 실제 framework
  API를 확인하고, 측정 데이터로 무릎 각도 threshold를 보정하고, unit test를 먼저 작성(RED)한 뒤,
  앱을 파일 단위로 생성·검증하고 나서야 완료를 선언했는지 따라갈 수 있습니다.

이것이 showcase의 핵심입니다: 품질은 raw 모델보다 harness가 부과하는 **instruction, skill,
verification gate**에서 더 많이 나옵니다.

## 사전 요구사항

| 요구사항 | 세부사항 |
|---|---|
| **DEEPX 개발 환경** | DX-RT SDK 설치 및 `setup_env.sh` 소싱 완료 |
| **AI 코딩 에이전트** (택1) | Claude Code, GitHub Copilot (VS Code), Cursor, OpenCode, 또는 Codex CLI |
| **Python** | 3.10+ (dx-all-suite 패키지 설치 완료) |

## 아키텍처 개요

에이전틱 지식 베이스는 세 개의 독립적인 레이어로 구성됩니다. 각 레이어는
자체 `.deepx/` 디렉토리를 포함하며, 에이전트가 작업 시 읽는 스킬, 지침,
메모리 파일이 들어 있습니다.

### dx_app — 독립형 추론

GStreamer 없이 추론을 실행하는 Python 및 C++ 애플리케이션. 주요 추상화:

- **IFactory** — 모델별 전/후처리 파이프라인 생성
- **SyncRunner / AsyncRunner** — 블로킹/논블로킹 추론 실행기
- **DxInfer** — InferenceEngine을 감싸는 저수준 추론 래퍼

`.deepx/` 지식 베이스는 모델 로딩, `.dxnn` 해석, 배치 처리, 결과 시각화를 다룹니다.

### dx_stream — GStreamer 파이프라인

GStreamer 기반 실시간 비디오 분석. 에이전트는 6개 기능 카테고리(소스, 추론,
오버레이, 인코딩, 스트리밍, 싱크)로 구성된 13개 DEEPX 엘리먼트를 모두 이해하며,
하나의 자연어 프롬프트로 멀티 브랜치 파이프라인을 조립할 수 있습니다.

### dx-runtime — 통합 레이어

크로스 프로젝트 라우팅과 통합 검증. dx-runtime은 나머지 두 레이어 위에 위치하며,
작업을 적절한 서브 프로젝트 빌더에 디스패치하고, 일관된 코딩 표준, 테스트 패턴,
모델 관리 규칙을 적용합니다.

### dx-compiler — 모델 컴파일

DX-COM 기반의 DXNN 모델 컴파일. 에이전트는 전체 컴파일 파이프라인을
이해합니다 — ONNX 모델 검증, config.json 자동 생성, 캘리브레이션 데이터 준비,
INT8 양자화, PPU 설정 — 하나의 자연어 프롬프트로 모델을 컴파일할 수 있습니다.
컴파일 전에 에이전트가 NMS-free 모델 감지, ONNX 단순화, PPU 컴파일에 대한
필수 브레인스토밍 질문을 통해 올바른 설정을 확인합니다.

## 사용 가능한 에이전트 및 스킬

에이전트와 스킬은 리포지토리의 모든 레벨에서 사용할 수 있습니다. 최상위
dx-all-suite는 작업을 분류하고 적절한 서브모듈로 디스패치하는 라우팅
에이전트를 제공합니다.

### 레벨별 에이전트

| 레벨 | 에이전트 | 설명 |
|---|---|---|
| **dx-all-suite** | `@dx-suite-builder` | 최상위 라우터 — 작업을 분류하고 적절한 서브모듈로 라우팅 |
| **dx-all-suite** | `@dx-suite-validator` | 전체 검증 — 3개 레벨 프레임워크 체크 실행 |
| **dx-runtime** | `@dx-runtime-builder` | 크로스 프로젝트 빌더 — dx_app 또는 dx_stream으로 라우팅 |
| **dx-runtime** | `@dx-validator` | 통합 검증 오케스트레이터 (피드백 루프 포함) |
| **dx_app** | `@dx-app-builder` | 독립형 추론 빌더 — 세부 빌더로 라우팅 |
| **dx_app** | `@dx-python-builder` | Python 추론 앱 빌더 (4가지 변형: sync, async, cpp_postprocess, async_cpp_postprocess) |
| **dx_app** | `@dx-cpp-builder` | C++ 추론 앱 빌더 |
| **dx_app** | `@dx-model-manager` | 모델 다운로드 및 레지스트리 관리 |
| **dx_app** | `@dx-validator` | dx_app 검증 및 피드백 루프 |
| **dx_stream** | `@dx-stream-builder` | GStreamer 파이프라인 빌더 — 세부 빌더로 라우팅 |
| **dx_stream** | `@dx-pipeline-builder` | 파이프라인 구성 (6가지 카테고리, 브로커 포함) |
| **dx_stream** | `@dx-validator` | dx_stream 검증 및 피드백 루프 |
| **dx-compiler** | `@dx-compiler-builder` | 모델 컴파일 라우터 — 변환기 또는 컴파일러로 라우팅 |
| **dx-compiler** | `@dx-model-converter` | PyTorch → ONNX 모델 변환기 |
| **dx-compiler** | `@dx-dxnn-compiler` | ONNX → DXNN 컴파일러 (DX-COM) |

### 스킬 (OpenCode 전용)

| 레벨 | 스킬 | 설명 |
|---|---|---|
| **dx-runtime** | `/dx-agentic-runtime-validate` | 검증, 피드백 수집, 수정 적용, 결과 확인 |
| **dx_app** | `/dx-agentic-app-build-python` | Python 추론 앱 빌드 |
| **dx_app** | `/dx-agentic-app-build-cpp` | C++ 추론 앱 빌드 |
| **dx_app** | `/dx-agentic-app-build-async` | 비동기 고성능 앱 빌드 |
| **dx_app** | `/dx-agentic-app-model-management` | 모델 다운로드 및 설정 |
| **dx_app** | `/dx-agentic-app-validate` | 검증 체크 실행 |
| **dx_stream** | `/dx-agentic-stream-build-pipeline` | GStreamer 파이프라인 앱 빌드 |
| **dx_stream** | `/dx-agentic-stream-build-mqtt-kafka` | MQTT/Kafka 파이프라인 앱 빌드 |
| **dx_stream** | `/dx-agentic-stream-validate` | 검증 체크 실행 |
| **dx_stream** | `/dx-agentic-stream-model-management` | 모델 다운로드 및 설정 |
| **dx-compiler** | `/dx-agentic-compiler-convert` | PyTorch 모델을 ONNX로 변환 |
| **dx-compiler** | `/dx-agentic-compiler-compile` | ONNX 모델을 DXNN으로 컴파일 |
| **dx-compiler** | `/dx-agentic-compiler-validate` | 컴파일된 DXNN 출력 검증 |
| **DX All Suite** | `/dx-swe-brainstorm` | 프로세스: 모든 작업 전 협업 설계 세션 |
| **DX All Suite** | `/dx-swe-tdd` | 프로세스: 테스트 주도 개발 — 점진적 검증 |
| **DX All Suite** | `/dx-swe-verify` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |
| **dx-runtime** | `/dx-swe-brainstorm` | 프로세스: 코드 생성 전 협업 설계 세션 |
| **dx-runtime** | `/dx-swe-tdd` | 프로세스: 테스트 주도 개발 — 생성 직후 즉시 검증 |
| **dx-runtime** | `/dx-swe-verify` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |
| **dx_app** | `/dx-swe-brainstorm` | 프로세스: 코드 생성 전 협업 설계 세션 |
| **dx_app** | `/dx-swe-tdd` | 프로세스: 테스트 주도 개발 — 생성 직후 즉시 검증 |
| **dx_app** | `/dx-swe-verify` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |
| **dx_stream** | `/dx-swe-brainstorm` | 프로세스: 코드 생성 전 협업 설계 세션 |
| **dx_stream** | `/dx-swe-tdd` | 프로세스: 테스트 주도 개발 — 생성 직후 즉시 검증 |
| **dx_stream** | `/dx-swe-verify` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |
| **dx-compiler** | `/dx-swe-brainstorm` | 프로세스: 컴파일 전 협업 설계 세션 |
| **dx-compiler** | `/dx-swe-tdd` | 프로세스: 테스트 주도 개발 — 각 단계를 점진적으로 검증 |
| **dx-compiler** | `/dx-swe-verify` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |

> **팁:** 어떤 서브모듈을 대상으로 해야 할지 모르겠다면, 최상위에서
> `@dx-suite-builder`를 사용하세요 — 작업을 분류하고 적절한 빌더로 라우팅합니다.

## 지원 AI 도구

에이전틱 개발은 5가지 AI 코딩 도구에서 작동합니다. 각 도구는 자체 설정
메커니즘을 통해 `.deepx/` 지식 베이스를 자동으로 로드합니다.

| 도구 | 유형 | 자동 로드 메커니즘 | 에이전트 호출 | 스킬 호출 |
|---|---|---|---|---|
| **Claude Code** | CLI | 프로젝트 루트의 `CLAUDE.md` | 자유 형식 대화; Context Routing Table이 자동 디스패치 | — |
| **GitHub Copilot** | VS Code | `.github/copilot-instructions.md` | Copilot Chat에서 `@에이전트명 "프롬프트"` | — |
| **Cursor** | IDE | `.cursor/rules/*.mdc` | 자유 형식 대화; `alwaysApply` 또는 `globs`로 규칙 로드 | — |
| **OpenCode** | CLI | `AGENTS.md` + `opencode.json` | `@에이전트명 "프롬프트"` | `/스킬명` 슬래시 명령 |
| **Codex CLI** | CLI | `AGENTS.md` + `.codex/skills/dx-codex-identity/SKILL.md` | 자유 형식 대화 (`~/bin/codex exec ...`) | `cat .deepx/skills/<name>/SKILL.md` 로 직접 읽기 |

### 자동 로드되는 항목

| 도구 | 전역 컨텍스트 | 파일별 컨텍스트 | 에이전트 | 스킬 |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` | Context Routing Table (수동) | `.claude/agents/*.md` (생성됨) | `.deepx/skills/` (직접 읽기) |
| Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` (`applyTo:` 글로브) | `.github/agents/*.agent.md` | `.github/skills/` (인라인 복사) |
| Cursor | `.cursor/rules/dx-*.mdc` (`alwaysApply: true`) | `.cursor/rules/*.mdc` (`globs: [...]`) | `.cursor/rules/` 에이전트 `.mdc` 파일 | `.cursor/rules/` 스킬 `.mdc` 파일 |
| OpenCode | `AGENTS.md` + `opencode.json` instructions | — | `.opencode/agents/*.md` | `.deepx/skills/*/SKILL.md` |
| Codex CLI | `AGENTS.md` | — | `.deepx/agents/*.md` (직접 `cat`) | `.codex/skills/dx-codex-identity/` (자동) + `.deepx/skills/` (수동 `cat`) |

### 초기 설정

추가 설정이 필요 없습니다. 선호하는 도구에서 프로젝트 디렉토리를 열면
설정 파일이 자동으로 로드됩니다:

```bash
# Claude Code
cd dx-all-suite
claude

# OpenCode
cd dx-all-suite
opencode

# Codex CLI
cd dx-all-suite
~/bin/codex

# GitHub Copilot — VS Code에서 폴더 열기
code dx-all-suite

# Cursor CLI
cd dx-all-suite
cursor-agent
```

### 플랫폼별 파일 참조

각 AI 코딩 에이전트는 Suite 레벨에서 서로 다른 설정 파일을 자동 로딩합니다.
**Auto**로 표시된 파일은 매 대화마다 자동 로딩되고, **@mention** 파일은
에이전트 또는 스킬 명령으로 수동 호출됩니다.

> **Git 서브모듈 경계**: Copilot Chat/CLI, Claude Code, Codex CLI는 현재 git 루트의 파일만
> 인식합니다. `dx-all-suite/`에서 열면 `dx-compiler/`, `dx-runtime/` 등의 하위
> 프로젝트 파일은 자동 로딩되지 않습니다 (별도 git 서브모듈). OpenCode만
> `opencode.json`의 명시적 경로 참조로 이 경계를 넘을 수 있습니다.

#### 자동 로딩 파일

| 파일 | Copilot Chat/CLI | OpenCode | Claude Code | Cursor | 로딩 |
|------|:---:|:---:|:---:|:---:|------|
| `.github/copilot-instructions.md` | ✅ | — | — | — | Auto |
| `CLAUDE.md` | — | — | ✅ | — | Auto |
| `AGENTS.md` + `opencode.json` | — | ✅ | — | — | Auto |
| `.cursor/rules/dx-all-suite.mdc` | — | — | — | ✅ | Auto |

#### 에이전트 파일 (수동 @mention)

| 에이전트 | Copilot (`@mention`) | OpenCode (`@mention`) |
|----------|------|---------|
| `dx-suite-builder` | `.github/agents/dx-suite-builder.agent.md` | `.opencode/agents/dx-suite-builder.md` |
| `dx-suite-validator` | `.github/agents/dx-suite-validator.agent.md` | `.opencode/agents/dx-suite-validator.md` |

> Claude Code는 `.claude/agents/`에 생성된 에이전트 파일이 있습니다 (예: `dx-suite-builder.md`).
> Cursor는 `.cursor/rules/`에 에이전트 `.mdc` 파일이 있습니다 (예: `dx-suite-builder.mdc`).
> Claude Code는 또한 `CLAUDE.md`의 Context Routing Table로 작업을 디스패치합니다.

#### 스킬 파일 (OpenCode 전용 — `/slash-command`)

| 스킬 | 파일 |
|------|------|
| `/dx-swe-brainstorm` | `.deepx/skills/dx-swe-brainstorm/SKILL.md` |
| `/dx-swe-verify` | `.deepx/skills/dx-swe-verify/SKILL.md` |
| `/dx-swe-tdd` | `.deepx/skills/dx-swe-tdd/SKILL.md` |
| `/dx-swe-parallel-agents` | `.deepx/skills/dx-swe-parallel-agents/SKILL.md` |
| `/dx-swe-executing-plans` | `.deepx/skills/dx-swe-executing-plans/SKILL.md` |
| `/dx-swe-receiving-review` | `.deepx/skills/dx-swe-receiving-review/SKILL.md` |
| `/dx-swe-requesting-review` | `.deepx/skills/dx-swe-requesting-review/SKILL.md` |
| `/dx-skill-router` | `.deepx/skills/dx-skill-router/SKILL.md` |
| `/dx-swe-subagent-dev` | `.deepx/skills/dx-swe-subagent-dev/SKILL.md` |
| `/dx-swe-debugging` | `.deepx/skills/dx-swe-debugging/SKILL.md` |
| `/dx-swe-writing-plans` | `.deepx/skills/dx-swe-writing-plans/SKILL.md` |

#### 공유 지식 베이스 (`.deepx/`)

`.deepx/` 디렉토리는 모든 플랫폼별 파일의 **정규 소스** (단일 진실 공급원)입니다.
에이전트, 스킬, 템플릿, 프래그먼트를 플랫폼 중립 형식으로 포함합니다.
`dx-agentic-gen` 생성기가 이를 Copilot (`.github/`), Claude Code (`.claude/`),
OpenCode (`.opencode/`), Cursor (`.cursor/rules/`) 용 플랫폼별 파일로 변환합니다.

| 디렉토리 | 내용 |
|-----------|------|
| `agents/` | `dx-suite-builder`, `dx-suite-validator` |
| `skills/` | 13개 스킬 (도메인 + 공유 프로세스 스킬) |
| `templates/` | `{en,ko}/*.tmpl` — 인스트럭션 파일 템플릿 |
| `templates/fragments/` | `{en,ko}/*.md` — 여러 리포에서 재사용되는 공유 섹션 |
| `memory/` | 세션 간 영속 지식 |
| `knowledge/` | 구조화된 참조 데이터 |
| `instructions/` | 에이전트 내부 지침 |
| `toolsets/` | 도구 참조 문서 |

인스트럭션 파일 (`CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md`, EN+KO)도
템플릿과 프래그먼트에서 생성됩니다 — 직접 편집하면 안 됩니다.

#### 플랫폼 파일 생성

모든 플랫폼별 파일은 `dx-agentic-dev-gen` 패키지에 의해 `.deepx/`에서 생성됩니다.
생성된 파일을 직접 편집하지 마세요.

```bash
pip install -e .deepx/tools   # 생성기 설치
dx-agentic-gen generate                    # 플랫폼 파일 생성
dx-agentic-gen check                       # 드리프트 없는지 확인
```

pre-commit 훅이 생성된 파일의 동기화를 강제합니다:
```bash
.deepx/tools/scripts/install-hooks.sh   # 최초 1회 설정
```

## 도구별 빠른 시작

### dx-all-suite에서 (최상위 라우팅)

최상위 dx-all-suite 디렉토리에서 작업하면 에이전트가 자동으로 적절한
서브모듈로 라우팅합니다:

**프롬프트:**

```
"yolo26n.onnx를 DXNN으로 컴파일하고, 그걸로 사람 감지 Python 앱 만들어줘"
```

| 도구 | 사용 방법 |
|---|---|
| **Claude Code** | `dx-all-suite/`를 열고 프롬프트 입력. `CLAUDE.md`가 dx-compiler로 컴파일, dx_app으로 앱 생성을 라우팅. |
| **GitHub Copilot** | Copilot Chat에서 `@dx-suite-builder` 뒤에 프롬프트 입력. 에이전트가 작업을 분류하고 적절한 서브모듈들로 라우팅. |
| **Cursor** | `dx-all-suite/`를 열고 프롬프트 입력. `alwaysApply` 규칙이 적절한 서브모듈들로 라우팅. |
| **OpenCode** | `dx-all-suite/` 열기: `@dx-suite-builder` 뒤에 프롬프트 입력. 에이전트가 자동 라우팅. |
| **Codex CLI** | `dx-all-suite/`를 열고 프롬프트 입력 (또는 `~/bin/codex exec "<프롬프트>"`). `AGENTS.md`가 자동으로 읽히며 서브모듈들로 라우팅. |

### 서브모듈에서 (직접 접근)

서브모듈 내에서 직접 작업할 때는 해당 서브모듈의 범위에 맞는 프롬프트를 사용합니다:

| 서브모듈 | 예시 프롬프트 |
|---|---|
| **dx-compiler** | `"내 yolo26x.pt를 ONNX로 변환하고 DX-M1용 DXNN으로 컴파일해줘"` |
| **dx_app** | `"yolo26n으로 사람 감지하는 Python 앱 만들어줘"` |
| **dx_stream** | `"RTSP 카메라에서 트래킹 포함 감지 파이프라인 만들어줘"` |

| 도구 | 사용 방법 |
|---|---|
| **Claude Code** | 서브모듈 디렉토리를 열고 프롬프트를 직접 입력. `CLAUDE.md`가 자동으로 읽히며, Context Routing Table이 올바른 `.deepx/` 스킬 파일로 디스패치. |
| **GitHub Copilot** | Copilot Chat 열기: `@dx-app-builder`, `@dx-stream-builder`, 또는 `@dx-compiler-builder` 뒤에 프롬프트 입력. 모든 채팅에서 `.github/copilot-instructions.md` 자동 읽기. |
| **Cursor** | 서브모듈 폴더를 열고 프롬프트를 직접 입력. `alwaysApply: true` 규칙은 모든 대화에서 로드. `globs:` 패턴이 있는 규칙은 매칭 파일 편집 시 활성화. |
| **OpenCode** | 서브모듈 디렉토리를 열고 적절한 에이전트(`@dx-app-builder`, `@dx-stream-builder`, 또는 `@dx-compiler-builder`)를 사용하거나, 해당 스킬 슬래시 명령 사용. |
| **Codex CLI** | 서브모듈 디렉토리를 열고 프롬프트를 직접 입력 (또는 `~/bin/codex exec "<프롬프트>"`). `AGENTS.md`가 자동으로 읽히며, 필요 시 해당 `.deepx/skills/<name>/SKILL.md`를 직접 `cat`. |

## 엔드투엔드 시나리오

여러 서브모듈에 걸친 크로스 프로젝트 워크플로우를 보여주는 시나리오입니다.
서브 프로젝트별 시나리오는 아래 링크된 개별 가이드를 참고하세요.

### 시나리오 1: 커스텀 모델 변환 + SDK 포팅 + 검증

커스텀 모델을 컴파일하고, 추론 코드를 DEEPX SDK로 포팅한 뒤 결과를 검증하는
풀 파이프라인입니다.

**프롬프트:**

```
"내 커스텀 모델 yolo26x-custom.onnx가 ./models/에 있고, onnxruntime으로 추론하는 코드가 ./inference.py에 있어. DXNN으로 변환하고 내 코드를 DEEPX SDK로 포팅해줘"
```

| 도구 | 사용 방법 |
|---|---|
| **Claude Code** | `dx-all-suite/`를 열고 프롬프트 입력. Suite 빌더가 (a) dx-compiler로 ONNX→DXNN 컴파일, (b) dx_app으로 추론 코드 포팅, (c) 검증을 순서대로 오케스트레이션. |
| **GitHub Copilot** | `@dx-suite-builder` 뒤에 프롬프트 입력. 에이전트가 컴파일은 dx-compiler로, 포팅은 dx_app으로 라우팅. |
| **Cursor** | `dx-all-suite/`를 열고 프롬프트 입력. 라우터가 적절한 서브모듈로 디스패치. |
| **OpenCode** | `@dx-suite-builder` 뒤에 프롬프트 입력. |
| **Codex CLI** | `dx-all-suite/`를 열고 프롬프트 입력. `AGENTS.md`가 서브모듈 간 작업을 오케스트레이션. |

이 시나리오는 3단계로 구성됩니다:
1. **dx-compiler**: `yolo26x-custom.onnx` → `yolo26x-custom.dxnn` 컴파일 (자동 추론 설정)
2. **dx_app**: 컴파일된 모델을 사용한 Python 추론 앱 생성 (`InferenceEngine`)
3. **검증**: 포팅된 앱 실행 및 원본 onnxruntime 코드 대비 출력 비교

### 시나리오 2: 모델 컴파일 + 샘플 앱 생성

모델을 컴파일하고 컴파일 결과물을 사용하는 독립형 추론 앱을 생성합니다.
dx-compiler와 dx_app에 걸치는 크로스 프로젝트 시나리오입니다.

**프롬프트:**

```
"yolo26n.onnx를 DXNN으로 컴파일하고, 컴파일된 모델을 사용하는 Python 감지 앱 만들어줘"
```

| 도구 | 사용 방법 |
|---|---|
| **Claude Code** | `dx-all-suite/`를 열고 프롬프트 입력. Suite 빌더가 (a) dx-compiler로 ONNX→DXNN 컴파일, (b) dx_app으로 컴파일된 모델을 참조하는 Python 앱 생성을 오케스트레이션. |
| **GitHub Copilot** | `@dx-suite-builder` 뒤에 프롬프트 입력. 컴파일은 dx-compiler로, 앱 생성은 dx_app으로 라우팅. |
| **Cursor** | `dx-all-suite/`를 열고 프롬프트 입력. 라우터가 두 서브모듈로 디스패치. |
| **OpenCode** | `@dx-suite-builder` 뒤에 프롬프트 입력. |
| **Codex CLI** | `dx-all-suite/`를 열고 프롬프트 입력. `AGENTS.md`가 서브모듈 간 작업을 오케스트레이션. |

이 시나리오는 2단계로 구성됩니다:
1. **dx-compiler**: `yolo26n.onnx` → `yolo26n.dxnn` 컴파일 (자동 추론 설정)
2. **dx_app**: 컴파일된 `.dxnn` 모델을 사용하는 Python 감지 앱 생성

### 시나리오 3: 모델 컴파일 + 스트리밍 파이프라인 생성

모델을 컴파일하고 컴파일 결과물을 사용하는 GStreamer 스트리밍 파이프라인을 생성합니다.
dx-compiler와 dx_stream에 걸치는 크로스 프로젝트 시나리오입니다.

**프롬프트:**

```
"yolo26n.onnx를 DXNN으로 컴파일하고, RTSP 출력 포함 감지 스트리밍 파이프라인 만들어줘"
```

| 도구 | 사용 방법 |
|---|---|
| **Claude Code** | `dx-all-suite/`를 열고 프롬프트 입력. Suite 빌더가 (a) dx-compiler로 ONNX→DXNN 컴파일, (b) dx_stream으로 RTSP 출력 GStreamer 파이프라인 생성을 오케스트레이션. |
| **GitHub Copilot** | `@dx-suite-builder` 뒤에 프롬프트 입력. 컴파일은 dx-compiler로, 파이프라인은 dx_stream으로 라우팅. |
| **Cursor** | `dx-all-suite/`를 열고 프롬프트 입력. 라우터가 두 서브모듈로 디스패치. |
| **OpenCode** | `@dx-suite-builder` 뒤에 프롬프트 입력. |
| **Codex CLI** | `dx-all-suite/`를 열고 프롬프트 입력. `AGENTS.md`가 서브모듈 간 작업을 오케스트레이션. |

이 시나리오는 2단계로 구성됩니다:
1. **dx-compiler**: `yolo26n.onnx` → `yolo26n.dxnn` 컴파일 (자동 추론 설정)
2. **dx_stream**: 컴파일된 모델과 DxInfer를 사용하는 감지 파이프라인 및 RTSP 스트리밍 출력 생성

### 시나리오 4: PPU 모델 컴파일 + 감지 앱

하드웨어 가속 후처리를 위해 PPU(Pre/Post Processing Unit) 지원으로 YOLO 모델을
컴파일한 다음, PPU 모델을 사용하는 앱을 생성합니다.

**프롬프트:**

```
"yolo26n.onnx를 PPU 지원으로 컴파일하고, PPU 모델용 감지 앱 만들어줘"
```

| 도구 | 사용 방법 |
|---|---|
| **Claude Code** | `dx-all-suite/`를 열고 프롬프트 입력. Suite 빌더가 (a) dx-compiler로 PPU 설정 컴파일(YOLO 버전 기반 유형 자동 감지), (b) dx_app으로 간소화된 후처리의 PPU 전용 앱 생성을 오케스트레이션. |
| **GitHub Copilot** | `@dx-suite-builder` 뒤에 프롬프트 입력. PPU 컴파일은 dx-compiler로, PPU 앱 생성은 dx_app으로 라우팅. |
| **Cursor** | `dx-all-suite/`를 열고 프롬프트 입력. 라우터가 두 서브모듈로 디스패치. |
| **OpenCode** | `@dx-suite-builder` 뒤에 프롬프트 입력. |
| **Codex CLI** | `dx-all-suite/`를 열고 프롬프트 입력. `AGENTS.md`가 서브모듈 간 작업을 오케스트레이션. |

이 시나리오는 2단계로 구성됩니다:
1. **dx-compiler**: PPU 설정으로 컴파일 — 에이전트가 PPU 유형 자동 감지 (앵커 기반 YOLO는 Type 0, 앵커 프리 YOLO는 Type 1)
2. **dx_app**: `src/python_example/ppu/`에 간소화된 후처리(하드웨어가 바운딩 박스 디코딩)의 PPU 전용 감지 앱 생성

## 크로스 프로젝트 라우팅

dx-all-suite 메타 가이드는 모든 서브 프로젝트 시나리오로 라우팅합니다. 작업이
서브 프로젝트 가이드의 시나리오와 일치하면, Suite 빌더가 자동으로 해당 프로젝트로
라우팅합니다.

- **dx-runtime 시나리오** (크로스 프로젝트 빌드, 통합 검증): [dx-runtime 가이드](../../../dx-runtime/docs/source/agentic_development.md) 참조
- **dx_app 시나리오** (Python/C++ 추론 앱): [dx_app 가이드](../../../dx_app/docs/source/docs/12_DX-APP_Agentic_Development.md) 참조
- **dx_stream 시나리오** (GStreamer 파이프라인): [dx_stream 가이드](../../../dx_stream/docs/source/docs/08_DX-STREAM_Agentic_Development.md) 참조
- **dx-compiler 시나리오** (모델 컴파일): [dx-compiler 가이드](../../dx-compiler/source/docs/05_DX-COMPILER_Agentic_Development.md) 참조

> **팁:** 서브 프로젝트 디렉토리로 직접 이동할 필요 없습니다. dx-all-suite 레벨에서
> `@dx-suite-builder`를 사용하면 — 어떤 서브 프로젝트로든 자동 라우팅됩니다.

## 서브 프로젝트 가이드

각 서브 프로젝트에는 해당 스킬, 엘리먼트 카탈로그, 예제를 다루는
상세 에이전틱 개발 가이드가 있습니다:

| 서브 프로젝트 | 가이드 |
|---|---|
| **dx-runtime** | [`dx-runtime/docs/source/agentic_development.md`](../../../dx-runtime/docs/source/agentic_development.md) |
| **dx_app** | [`dx_app/docs/source/docs/12_DX-APP_Agentic_Development.md`](../../../dx_app/docs/source/docs/12_DX-APP_Agentic_Development.md) |
| **dx_stream** | [`dx_stream/docs/source/docs/08_DX-STREAM_Agentic_Development.md`](../../../dx_stream/docs/source/docs/08_DX-STREAM_Agentic_Development.md) |
| **dx-compiler** | [`dx-compiler/source/docs/05_DX-COMPILER_Agentic_Development.md`](../../dx-compiler/source/docs/05_DX-COMPILER_Agentic_Development.md) |

## 내부 참고 문서

`.deepx/` canonical source, generator 파이프라인, harness 개발 모델을 더 깊이
파악하려면 다음 문서를 참고하세요 (엔드유저용이 아닌 기여자용):

| 문서 | 범위 |
|---|---|
| [`.deepx/docs/dx-agentic-dev-overview.md`](../../.deepx/docs/dx-agentic-dev-overview.md) | 5개 repo 전체의 `.deepx/` 디렉토리 종합 안내 |
| [`.deepx/README.md`](../../.deepx/README.md) | `.deepx/` knowledge base 최상위 마스터 인덱스 |
| [`.deepx/docs/skill-architecture.md`](../../.deepx/docs/skill-architecture.md) | 3-tier skill 모델 (SWE / Agentic / Harness) |
| [`.deepx/tools/README.md`](../../.deepx/tools/README.md) | `dx-agentic-gen` generator 패키지 가이드 |
| [`.deepx/tools/scripts/README.md`](../../.deepx/tools/scripts/README.md) | 운영 스크립트 (`run_all.sh`, hooks, E2E loop) |

## 산출물 격리

기본적으로 모든 에이전트 생성 코드는 대상 서브 프로젝트 내 `dx-agentic-dev/<session_id>/`에
배치됩니다. 이는 기존 프로덕션 코드의 의도치 않은 수정을 방지합니다.

| 출력 유형 | 경로 | 시점 |
|---|---|---|
| **기본 (격리)** | `dx-agentic-dev/<session_id>/` | 사용자가 달리 지정하지 않는 한 항상 |
| **프로덕션** | `src/` | 사용자가 명시적으로 요청한 경우에만 |

세션 ID 형식: `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` — `<agent>`는 `claude`, `codex`, `copilot`, `cursor`, `opencode` 중 하나.

각 세션 디렉토리에는 다음이 포함됩니다:
- `README.md` — 세션 메타데이터, 생성된 파일 목록, 실행 지침
- `session.json` — 기계 판독 가능한 세션 설정

`dx-agentic-dev/` 디렉토리는 dx_app과 dx_stream 모두에서 git-ignore됩니다.

### dx-compiler 세션 디렉토리

dx-compiler의 경우 세션 디렉토리에 추가로 다음이 포함됩니다:
- `calibration_dataset` — `dx_com/calibration_dataset/`로의 심볼릭 링크
- `config.json` — 상대 캘리브레이션 경로가 포함된 자동 생성 DX-COM 설정
- `compiler.log` — 컴파일 로그 (`--gen_log` 사용 시)

에이전트가 캘리브레이션 데이터를 자동으로 설정합니다 (`dx_com/calibration_dataset/` 확인,
필요시 셋업 스크립트 실행, 상대경로로 심볼릭 링크 생성).

### Suite 레벨 크로스 프로젝트 산출물

dx-all-suite 레벨에서 크로스 프로젝트 작업(예: 컴파일 + 배포)을 실행하면,
각 대상 서브 프로젝트의 `dx-agentic-dev/` 디렉토리에 산출물이 생성됩니다.
또한 `dx-all-suite/dx-agentic-dev/`에 심볼릭 링크가 생성되어 통합 접근이
가능합니다:

```
dx-all-suite/dx-agentic-dev/
├── dx-compiler_20260409-070940_yolo26n_pt_to_dxnn -> ../dx-compiler/dx-agentic-dev/20260409-...
└── dx_app_20260409-071500_yolo26n_detection_app -> ../dx-runtime/dx_app/dx-agentic-dev/20260409-...
```

심볼릭 링크 명명 규칙: `{subproject}_{session_id}`.

## 세션 센티넬

에이전트는 자동화 테스트를 위해 각 작업의 시작과 끝에 고정 마커를 출력합니다:

| 마커 | 출력 시점 |
|---|---|
| `[DX-AGENTIC-DEV: START]` | **필수** — 에이전트 첫 번째 응답의 절대적 첫 줄. 다른 텍스트, tool call, reasoning보다 반드시 먼저 출력. 사용자가 "알아서 진행해"라고 해도 생략 불가 — 자동 테스트가 실패합니다. |
| `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]` | 모든 작업 완료 후 마지막 줄. `<relative_path>`는 프로젝트 루트 기준 세션 산출물 디렉토리의 상대 경로. 생성된 파일이 없으면 `(output-dir: ...)` 부분을 생략. |

**중요**: DONE은 모든 산출물(구현 코드, 스크립트, 설정 파일, 검증 결과)이 생성된
후에만 출력합니다. 기획 산출물(spec, plan, 설계 문서)만 작성하고 실제 코드를
구현하지 않은 상태에서는 DONE을 출력하면 안 됩니다.

## 문제 해결

| 증상 | 원인 | 해결 방법 |
|---|---|---|
| 에이전트가 `.dxnn` 모델을 찾지 못함 | 모델 이름 또는 아키텍처 불일치 | `resources/models/`에 모델이 존재하고 대상 칩(DX-M1, DX-H1)과 일치하는지 확인 |
| `DxInfer` 엘리먼트가 "device not found" 보고 | DX-RT SDK 미로딩 또는 디바이스 미연결 | `source setup_env.sh` 실행 후 `dx-rt list-devices`로 가속기 확인 |
| 파이프라인 시작 후 검은 화면 출력 | 카메라 소스 설정 오류 | `/dev/video` 경로를 하드코딩하지 말고 `--input usb`로 자동 감지 사용 |
| 에이전트가 잘못된 서브 프로젝트에 코드 생성 | 모호한 프롬프트 | 최상위에서 `@dx-suite-builder`로 자동 라우팅 사용, 또는 대상 빌더 이름을 접두사로 사용 (예: `@dx-stream-builder`, `@dx-app-builder`) |
| "unsupported opset" 오류로 컴파일 실패 | ONNX opset 버전이 11-21 범위 밖 | `opset_version=17`로 모델 재변환 |
| 컴파일된 DXNN 정확도 낮음 | 캘리브레이션 데이터가 실제 추론 데이터를 대표하지 못함 | 실제 추론 이미지 사용 및 `calibration_num`을 200 이상으로 증가 |
| 에이전트가 필수 질문을 건너뜀 | 에이전트 지침에 HARD-GATE 적용 안 됨 | 에이전트 파일의 필수 질문 섹션에 `<HARD-GATE>` 태그가 포함되어 있는지 확인 |

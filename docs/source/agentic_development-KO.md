# AI 기반 개발 (Beta)

> **베타 기능** — 에이전틱 개발 지원은 현재 활발히 개발 중입니다.
> 스킬 정의와 라우팅 동작은 릴리스 간에 변경될 수 있습니다.

## 소개

자연어 지시만으로 DEEPX AI 애플리케이션을 구축할 수 있습니다. AI 코딩 에이전트는
DEEPX SDK 생태계를 이해합니다 — GStreamer 파이프라인 구성, `.dxnn` 모델 해석,
InferenceEngine 설정, DxPreprocess/DxInfer 엘리먼트 연결 — 따라서 *무엇*을
원하는지 설명하면 에이전트가 구현 세부사항을 처리합니다.

지원되는 워크플로우:

- `IFactory`, `SyncRunner`, `AsyncRunner`를 사용한 독립형(Standalone) 추론 앱
- DEEPX의 13개 커스텀 엘리먼트를 사용한 6가지 카테고리의 GStreamer 비디오 파이프라인
- dx_app, dx_stream, dx-runtime에 걸친 크로스 프로젝트 빌드
- DX-COM을 통한 ONNX → DXNN 포맷 모델 컴파일 (dx-compiler)

## 사전 요구사항

| 요구사항 | 세부사항 |
|---|---|
| **DEEPX 개발 환경** | DX-RT SDK 설치 및 `setup_env.sh` 소싱 완료 |
| **AI 코딩 에이전트** (택1) | Claude Code, GitHub Copilot (VS Code), Cursor, 또는 OpenCode |
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

DX-COM v2.2.1 기반의 DXNN 모델 컴파일. 에이전트는 전체 컴파일 파이프라인을
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
| **dx-all-suite** | `/dx-validate-all` | 3개 레벨 전체 검증 |
| **dx-runtime** | `/dx-validate-and-fix` | 검증, 피드백 수집, 수정 적용, 결과 확인 |
| **dx_app** | `/dx-build-python-app` | Python 추론 앱 빌드 |
| **dx_app** | `/dx-build-cpp-app` | C++ 추론 앱 빌드 |
| **dx_app** | `/dx-build-async-app` | 비동기 고성능 앱 빌드 |
| **dx_app** | `/dx-model-management` | 모델 다운로드 및 설정 |
| **dx_app** | `/dx-validate` | 검증 체크 실행 |
| **dx_stream** | `/dx-build-pipeline-app` | GStreamer 파이프라인 앱 빌드 |
| **dx_stream** | `/dx-build-mqtt-kafka-app` | MQTT/Kafka 파이프라인 앱 빌드 |
| **dx_stream** | `/dx-validate` | 검증 체크 실행 |
| **dx_stream** | `/dx-model-management` | 모델 다운로드 및 설정 |
| **dx-compiler** | `/dx-convert-model` | PyTorch 모델을 ONNX로 변환 |
| **dx-compiler** | `/dx-compile-model` | ONNX 모델을 DXNN으로 컴파일 |
| **dx-compiler** | `/dx-validate-compile` | 컴파일된 DXNN 출력 검증 |
| **DX All Suite** | `/dx-brainstorm-and-plan` | 프로세스: 모든 작업 전 협업 설계 세션 |
| **DX All Suite** | `/dx-tdd` | 프로세스: 테스트 주도 개발 — 점진적 검증 |
| **DX All Suite** | `/dx-verify-completion` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |
| **dx-runtime** | `/dx-brainstorm-and-plan` | 프로세스: 코드 생성 전 협업 설계 세션 |
| **dx-runtime** | `/dx-tdd` | 프로세스: 테스트 주도 개발 — 생성 직후 즉시 검증 |
| **dx-runtime** | `/dx-verify-completion` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |
| **dx_app** | `/dx-brainstorm-and-plan` | 프로세스: 코드 생성 전 협업 설계 세션 |
| **dx_app** | `/dx-tdd` | 프로세스: 테스트 주도 개발 — 생성 직후 즉시 검증 |
| **dx_app** | `/dx-verify-completion` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |
| **dx_stream** | `/dx-brainstorm-and-plan` | 프로세스: 코드 생성 전 협업 설계 세션 |
| **dx_stream** | `/dx-tdd` | 프로세스: 테스트 주도 개발 — 생성 직후 즉시 검증 |
| **dx_stream** | `/dx-verify-completion` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |
| **dx-compiler** | `/dx-brainstorm-and-plan` | 프로세스: 컴파일 전 협업 설계 세션 |
| **dx-compiler** | `/dx-tdd` | 프로세스: 테스트 주도 개발 — 각 단계를 점진적으로 검증 |
| **dx-compiler** | `/dx-verify-completion` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |

> **팁:** 어떤 서브모듈을 대상으로 해야 할지 모르겠다면, 최상위에서
> `@dx-suite-builder`를 사용하세요 — 작업을 분류하고 적절한 빌더로 라우팅합니다.

## 지원 AI 도구

에이전틱 개발은 4가지 AI 코딩 도구에서 작동합니다. 각 도구는 자체 설정
메커니즘을 통해 `.deepx/` 지식 베이스를 자동으로 로드합니다.

| 도구 | 유형 | 자동 로드 메커니즘 | 에이전트 호출 | 스킬 호출 |
|---|---|---|---|---|
| **Claude Code** | CLI | 프로젝트 루트의 `CLAUDE.md` | 자유 형식 대화; Context Routing Table이 자동 디스패치 | — |
| **GitHub Copilot** | VS Code | `.github/copilot-instructions.md` | Copilot Chat에서 `@에이전트명 "프롬프트"` | — |
| **Cursor** | IDE | `.cursor/rules/*.mdc` | 자유 형식 대화; `alwaysApply` 또는 `globs`로 규칙 로드 | — |
| **OpenCode** | CLI | `AGENTS.md` + `opencode.json` | `@에이전트명 "프롬프트"` | `/스킬명` 슬래시 명령 |

### 자동 로드되는 항목

| 도구 | 전역 컨텍스트 | 파일별 컨텍스트 | 에이전트 | 스킬 |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` | Context Routing Table (수동) | `.claude/agents/*.md` (생성됨) | `.deepx/skills/` (직접 읽기) |
| Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` (`applyTo:` 글로브) | `.github/agents/*.agent.md` | `.github/skills/` (인라인 복사) |
| Cursor | `.cursor/rules/dx-*.mdc` (`alwaysApply: true`) | `.cursor/rules/*.mdc` (`globs: [...]`) | `.cursor/rules/` 에이전트 `.mdc` 파일 | `.cursor/rules/` 스킬 `.mdc` 파일 |
| OpenCode | `AGENTS.md` + `opencode.json` instructions | — | `.opencode/agents/*.md` | `.deepx/skills/*/SKILL.md` |

### 초기 설정

추가 설정이 필요 없습니다. 선호하는 도구에서 프로젝트 디렉토리를 열면
설정 파일이 자동으로 로드됩니다:

```bash
# Claude Code
cd dx-all-suite/dx-runtime/dx_app
claude

# OpenCode
cd dx-all-suite/dx-runtime/dx_app
opencode

# GitHub Copilot — VS Code에서 폴더 열기
code dx-all-suite/dx-runtime/dx_app

# Cursor — Cursor에서 폴더 열기
cursor dx-all-suite/dx-runtime/dx_app
```

### 플랫폼별 파일 참조

각 AI 코딩 에이전트는 Suite 레벨에서 서로 다른 설정 파일을 자동 로딩합니다.
**Auto**로 표시된 파일은 매 대화마다 자동 로딩되고, **@mention** 파일은
에이전트 또는 스킬 명령으로 수동 호출됩니다.

> **Git 서브모듈 경계**: Copilot Chat/CLI와 Claude Code는 현재 git 루트의 파일만
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
| `/dx-brainstorm-and-plan` | `.deepx/skills/dx-brainstorm-and-plan/SKILL.md` |
| `/dx-verify-completion` | `.deepx/skills/dx-verify-completion/SKILL.md` |
| `/dx-validate-all` | `.deepx/skills/dx-validate-all/SKILL.md` |
| `/dx-tdd` | `.deepx/skills/dx-tdd/SKILL.md` |
| `/dx-dispatching-parallel-agents` | `.deepx/skills/dx-dispatching-parallel-agents/SKILL.md` |
| `/dx-executing-plans` | `.deepx/skills/dx-executing-plans/SKILL.md` |
| `/dx-receiving-code-review` | `.deepx/skills/dx-receiving-code-review/SKILL.md` |
| `/dx-requesting-code-review` | `.deepx/skills/dx-requesting-code-review/SKILL.md` |
| `/dx-skill-router` | `.deepx/skills/dx-skill-router/SKILL.md` |
| `/dx-subagent-driven-development` | `.deepx/skills/dx-subagent-driven-development/SKILL.md` |
| `/dx-systematic-debugging` | `.deepx/skills/dx-systematic-debugging/SKILL.md` |
| `/dx-writing-plans` | `.deepx/skills/dx-writing-plans/SKILL.md` |
| `/dx-writing-skills` | `.deepx/skills/dx-writing-skills/SKILL.md` |

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
pip install -e tools/dx-agentic-dev-gen   # 생성기 설치
dx-agentic-gen generate                    # 플랫폼 파일 생성
dx-agentic-gen check                       # 드리프트 없는지 확인
```

pre-commit 훅이 생성된 파일의 동기화를 강제합니다:
```bash
tools/dx-agentic-dev-gen/scripts/install-hooks.sh   # 최초 1회 설정
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

## 산출물 격리

기본적으로 모든 AI 생성 코드는 대상 서브 프로젝트 내 `dx-agentic-dev/<session_id>/`에
배치됩니다. 이는 기존 프로덕션 코드의 의도치 않은 수정을 방지합니다.

| 출력 유형 | 경로 | 시점 |
|---|---|---|
| **기본 (격리)** | `dx-agentic-dev/<session_id>/` | 사용자가 달리 지정하지 않는 한 항상 |
| **프로덕션** | `src/` | 사용자가 명시적으로 요청한 경우에만 |

세션 ID 형식: `YYYYMMDD-HHMMSS_model_task`.

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

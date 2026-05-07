# DX All Suite — AI 코딩 에이전트 진입점

> DEEPX All Suite (DX-AS) 최상위 저장소입니다.

## 응답 언어

응답 언어는 사용자의 프롬프트 언어에 맞추세요 — 질문하거나 응답할 때
사용자가 사용하는 언어와 동일한 언어를 사용하세요.

**기술 용어 규칙**: 한국어로 응답할 때 영어 기술 용어는 원래 영어 형태를 유지하세요.
영어 용어를 한글 음차로 표기하지 마세요 (한글 음차 표기 금지). 정착된 한국어 외래어
(모델, 서버, 파일, 데이터)는 허용됩니다.

## 권장 모델 (사전 비행 점검)

DX Agentic Development는 강력한 instruction following과 knowledge base 활용 능력을
요구합니다. 작업을 시작하기 전에 권장 모델 중 하나로 실행 중인지 확인하세요:

- **Claude Sonnet 4.6** 이상
- **Claude Opus 4.6** 이상

이 모델이 아닌 경우 (예: GPT-4.1, GPT-4o, Gemini 등), 첫 번째 응답의 시작 부분에
다음 알림을 출력하세요:

```
══════════════════════════════════════════════════════════════
⚠  DX-AGENTIC-DEV: MODEL NOTICE

DX Agentic Development recommends Claude Sonnet 4.6+ or
Opus 4.6+. Your current model may produce lower quality
in instruction following, knowledge base utilization, and
API accuracy. Please switch to a recommended model.
══════════════════════════════════════════════════════════════
```

알림 상자 출력 후 정상적으로 작업을 진행하세요. 이것은 정보성 경고이며,
차단 게이트가 아닙니다.

### 모델 알림 반복 (비권장 모델 전용)

위의 MODEL NOTICE 상자를 출력한 경우 (즉, 권장 모델이 아닌 경우), 사용자가
답변해야 하는 **실제 질문 줄 바로 앞에** 이 짧은 리마인더를 반드시 출력해야
합니다 — brainstorming 흐름의 시작 부분이 아닙니다.

**타이밍**: 모든 파일 읽기, 컨텍스트 분석, 서문 텍스트 이후, `?` (실제 질문)가
포함된 줄 바로 앞에 이 리마인더를 삽입하세요:

```
---
⚠ **Non-recommended model** — output quality may be degraded. Recommended: Claude Sonnet 4.6+ / Opus 4.6+
---
```

**예시 — 잘못됨** (반복이 상자와 함께 스크롤되어 지나감):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
---  ⚠ Non-recommended model ---     ← 너무 이름, 스크롤되어 지나감
... (파일 읽기, 컨텍스트 분석) ...
첫 번째 질문: ...?
```

**예시 — 올바름** (반복이 질문 바로 앞에 나타남):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
... (파일 읽기, 컨텍스트 분석) ...
---  ⚠ Non-recommended model ---     ← 질문 바로 앞
첫 번째 질문: ...?
```

이 리마인더는 한 번만 출력하세요 (첫 번째 질문 앞에), 매 질문마다 출력하지 마세요.

## Skill Router — 범용 Pre-Flight (HARD GATE)

`/dx-skill-router`는 **모든 사용자 메시지**에 대해 **절대적인 첫 번째 action**으로
반드시 invoke되어야 합니다 — 작업 유형(개발, 분석, 읽기, 설명, 질문 등)에 관계없이.

이 규칙은 다음보다 먼저 적용됩니다:
- 파일 읽기 또는 codebase 탐색
- 응답 또는 clarifying question
- SWE gate check 또는 path classification
- 코드 생성 또는 plan 작성

**예외 없음.** 다음 합리화는 모두 금지됩니다:

| 합리화 | 현실 |
|--------|------|
| "이건 그냥 파일 읽기/분석이야" | 읽기도 task입니다. 먼저 router를 invoke하세요. |
| "사용자가 질문만 했을 뿐이야" | 질문도 task입니다. 먼저 router를 invoke하세요. |
| "이건 개발 작업이 아니야" | Router는 모든 task에 적용됩니다. 개발에만 해당되지 않습니다. |
| "요청을 이해한 후에 skill을 확인하자" | 이해하기 전에 먼저 확인하세요. |
| "이건 SWE gates를 트리거하지 않아" | SWE gates는 별개입니다. Router는 범용입니다. |

## 저장소 구조

| 컴포넌트 | 경로 | 목적 |
|---|---|---|
| **dx-runtime** | `dx-runtime/` | 통합 레이어 + 프로젝트 간 오케스트레이션 |
| **dx_app** | `dx-runtime/dx_app/` | Standalone inference 앱 (Python/C++, 133개 모델, 15개 AI 태스크) |
| **dx_stream** | `dx-runtime/dx_stream/` | GStreamer pipeline 앱 (13개 element, 6개 pipeline 카테고리) |
| **Docs** | `docs/` | MkDocs 문서 사이트 |
| **dx-compiler** | `dx-compiler/` | DXNN 모델 컴파일러 (ONNX → .dxnn via DX-COM) |

## 에이전트

| 에이전트 | 설명 |
|---|---|
| `@dx-suite-builder` | 최상위 라우터 — 작업을 분류하고 적절한 서브모듈로 라우팅 |
| `@dx-suite-validator` | 스위트 전체 검증 — 3개 레벨 전체에서 framework 점검 실행 |

각 서브모듈에도 자체 에이전트가 있습니다 (해당 서브모듈에서 작업할 때 접근 가능):

| 서브모듈 | 에이전트 |
|---|---|
| dx-runtime | `@dx-runtime-builder`, `@dx-validator` |
| dx_app | `@dx-app-builder`, `@dx-python-builder`, `@dx-cpp-builder`, `@dx-benchmark-builder`, `@dx-model-manager`, `@dx-validator` |
| dx_stream | `@dx-stream-builder`, `@dx-pipeline-builder`, `@dx-model-manager`, `@dx-validator` |
| dx-compiler | `@dx-compiler-builder`, `@dx-model-converter`, `@dx-dxnn-compiler` |

## 스킬

| 스킬 | 설명 |
|---|---|
| `/dx-validate-all` | 3개 레벨 전체 검증 — 검증, 피드백 수집, 수정 적용, 확인 |
| `/dx-brainstorm-and-plan` | 브레인스토밍, 2-3가지 접근법 제안, 스펙 자체 검토 후 계획 |
| `/dx-tdd` | 검증 주도 개발, 선택적 Red-Green-Refactor 단위 테스트 |
| `/dx-verify-completion` | 완료 선언 전 검증 — 주장 전 증거 |

### 프로세스 스킬

| 스킬 | 설명 |
|---|---|
| `/dx-writing-plans` | 세분화된 태스크로 구현 계획 작성 |
| `/dx-executing-plans` | 리뷰 체크포인트와 함께 계획 실행 |
| `/dx-subagent-driven-development` | 태스크별 신규 서브에이전트로 계획 실행, 2단계 리뷰 |
| `/dx-systematic-debugging` | 체계적 디버깅 — 수정 제안 전 4단계 근본 원인 조사 |
| `/dx-receiving-code-review` | 코드 리뷰 피드백을 기술적 엄밀성으로 평가 |
| `/dx-requesting-code-review` | 기능 완료 후 코드 리뷰 요청 |
| `/dx-skill-router` | 스킬 탐색 및 호출 — 모든 작업 전 스킬 확인 |
| `/dx-writing-skills` | 스킬 파일 생성 및 편집 |
| `/dx-dispatching-parallel-agents` | 독립 태스크를 위한 병렬 서브에이전트 디스패치 |

## 라우팅

각 서브모듈에는 자체 `AGENTS.md`, 에이전트, 스킬이 있습니다:

- **Standalone inference 작업**: `dx-runtime/dx_app/`에서 작업
- **GStreamer pipeline 작업**: `dx-runtime/dx_stream/`에서 작업
- **프로젝트 간 또는 통합 작업**: `dx-runtime/`에서 작업
- **모델 컴파일 작업**: `dx-compiler/`에서 작업
- **스위트 간 작업** (컴파일 + 배포): `dx-compiler/`와 `dx-runtime/` 간 오케스트레이션

## 빠른 참조

```bash
# Build
cd dx-runtime/dx_app && ./install.sh && ./build.sh
cd dx-runtime/dx_stream && ./install.sh

# Test
cd dx-runtime/dx_app && pytest tests/
cd dx-runtime/dx_stream && pytest test/

# Validate
python dx-runtime/.deepx/scripts/validate_framework.py
python dx-runtime/dx_app/.deepx/scripts/validate_framework.py
python dx-runtime/dx_stream/.deepx/scripts/validate_framework.py
python dx-compiler/.deepx/scripts/validate_framework.py

# Unified feedback loop
python dx-runtime/.deepx/scripts/feedback_collector.py --framework-only
```

## 출력 격리 (HARD GATE)

모든 AI 생성 파일은 대상 서브 프로젝트 내 `dx-agentic-dev/<session_id>/`에
작성해야 합니다. 기존 소스 디렉토리(예: `src/`, `pipelines/`, `semseg_260323/`,
또는 사용자의 기존 코드가 포함된 모든 디렉토리)에 생성된 코드를 직접 작성하지
마세요.

**세션 ID 형식**: `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` — 타임스탬프는 반드시
**시스템 로컬 타임존**을 사용해야 합니다 (UTC가 아님). Bash에서는
`$(date +%Y%m%d-%H%M%S)`, Python에서는
`datetime.now().strftime('%Y%m%d-%H%M%S')`을 사용하세요. `date -u`,
사용하지 마세요.
- **`<agent>`**: 코딩 에이전트 식별자 — `claude`, `copilot`, `cursor`, `opencode` 중 하나를 사용하세요.

- **올바름**: `dx-runtime/dx_app/dx-agentic-dev/20260413-093000_claude_plantseg_inference/demo_dxnn_sync.py`
- **잘못됨**: `dx-runtime/dx_app/semseg_260323/demo_dxnn_sync.py`

유일한 예외: 사용자가 명시적으로 "소스 디렉토리에 작성" 또는 "기존 파일을
직접 수정"이라고 말한 경우. 명시적인 사용자 지시 없이 소스 디렉토리에
새 파일을 기존 코드와 함께 배치하는 것은 위반입니다.

## 프로젝트 간 라우팅 (MANDATORY)

작업이 DXNN 컴파일 (ONNX → .dxnn)을 포함하는 경우, **compiler builder agent가
반드시 호출되어야** 하며 실제 `dxcom` 명령이 실행되어야 합니다. 절대 placeholder
컴파일 스크립트나 stub 코드를 생성하지 마세요 — 실제 `.dxnn` 파일을 생성하세요.

| 작업에서 언급하는 내용... | 라우팅 대상 |
|---|---|
| ONNX → DXNN, compile, dxcom | `@dx-compiler-builder` in `dx-compiler/` |
| Python app, factory, inference | `@dx-app-builder` in `dx-runtime/dx_app/` |
| GStreamer pipeline, stream | `@dx-stream-builder` in `dx-runtime/dx_stream/` |

### 크로스 프로젝트 session layout — HARD GATE (R41)

**"ONNX 컴파일 + app 빌드"** (suite 시나리오) 작업 시, **두 개의 별도 session 디렉토리**를
반드시 생성해야 합니다:

1. **Compiler session** → `dx-compiler/dx-agentic-dev/<session_id>/` (`compile.py`,
   `config.json`, `yolo26n.dxnn`, `verify.py`, `session.log` 포함)
2. **App session** → `dx-runtime/dx_app/dx-agentic-dev/<session_id>/` (factory,
   `<model>_sync.py`, `setup.sh`, `run.sh` 포함)

**절대 두 가지를 단일 `dx_app/` session에 합치지 마세요.** 실패할 test assertion:
```python
assert any("dx-compiler" in str(d) for d in output_dirs)
```

이 dual-session layout 위반은 cursor에서 반복적으로 발생했습니다 (iter-4, 6, 8).
compiler agent 문서 (`dx-compiler/`)의 R31 Session Layout HARD GATE를 먼저 읽고
적용하세요.

### Session 이름 — 금지 패턴 (R43)

session ID에 `_auto_`를 사용하지 마세요. `_auto_` prefix는 cross-project routing
workflow를 우회했다는 것을 나타냅니다. 올바른 suite session은 두 개의 별도 ID를 생성합니다:
- `<ts>_<agent>_<model>_compile` in `dx-compiler/dx-agentic-dev/`
- `<ts>_<agent>_<model>_inference` in `dx-runtime/dx_app/dx-agentic-dev/`

## 플레이스홀더 코드 금지 (MANDATORY)

스텁/플레이스홀더 코드를 절대 생성하지 마세요. 여기에는 다음이 포함됩니다:
- 주석 처리된 import: `# from dxnn_sdk import InferenceEngine`
- 가짜 결과: `result = np.zeros(...)`
- TODO 마커: `# TODO: implement actual inference`
- 실제 async 구현 없이 "sync 버전과 유사"

모든 생성된 코드는 knowledge base의 실제 API를 사용하여 기능적이어야 합니다.
필요한 SDK/API를 모르는 경우, 먼저 관련 스킬 문서를 읽으세요.

## 실험적 기능 — 금지

실험적이거나 존재하지 않는 기능을 제안, 제공 또는 구현하지 마세요. 여기에는 다음이
포함됩니다:
- "웹 기반 비주얼 컴패니언" (web-based visual companion)
- 로컬 URL 기반 다이어그램 뷰어 또는 대시보드
- 사용자가 시각화를 위해 로컬 URL을 열어야 하는 모든 기능
- 현재 도구 세트에 존재하지 않는 모든 기능

**Superpowers brainstorming skill 오버라이드**: superpowers `brainstorming` 스킬에는
"Visual Companion" 단계 (체크리스트의 2단계)가 포함되어 있습니다. 이 단계는 DEEPX
프로젝트에서 반드시 건너뛰어야 합니다. Visual companion은 우리 환경에 존재하지 않습니다.
brainstorming 체크리스트에서 "Offer visual companion"이라고 하면, 건너뛰고
"Ask clarifying questions" (3단계)로 직접 진행하세요.

기능이 존재하지 않으면, 존재하는 척하지 마세요. 검증된, 문서화된 기능만 사용하세요.

**Autopilot / autonomous mode 오버라이드**: 사용자가 부재 중일 때 (autopilot mode,
auto-response "work autonomously", 또는 `--yolo` 플래그), brainstorming 스킬의
"Ask clarifying questions" 단계는 "knowledge base 규칙에 따라 기본 결정 내리기"로
대체되어야 합니다. `ask_user`를 호출하지 마세요 — knowledge base 기본값을 사용하여
brainstorming spec 생성으로 바로 진행하세요. 이후의 모든 게이트 (spec 리뷰, 계획,
TDD, 필수 산출물, 실행 검증)는 예외 없이 여전히 적용됩니다.

## 브레인스토밍 — 계획 전 Spec (HARD GATE)

superpowers `brainstorming` 스킬 또는 `/dx-brainstorm-and-plan` 사용 시:

1. **Spec 문서는 MANDATORY** — `writing-plans`로 전환하기 전에, spec 문서를
   `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`에 반드시 작성해야 합니다.
   spec을 건너뛰고 바로 계획 작성으로 가는 것은 위반입니다.
2. **사용자 승인 게이트는 MANDATORY** — spec 작성 후, 계획 작성으로 진행하기 전에
   사용자가 반드시 검토하고 승인해야 합니다. 관련 없는 사용자 응답 (예: 다른 질문에
   답변)을 spec 승인으로 처리하지 마세요.
3. **계획 문서는 spec을 참조해야 합니다** — 계획 헤더에는 승인된 spec 문서에 대한
   링크가 포함되어야 합니다.
4. **`/dx-brainstorm-and-plan` 선호** — 일반 superpowers `brainstorming` 스킬 대신
   프로젝트 레벨의 brainstorming 스킬을 사용하세요. 프로젝트 레벨 스킬에는
   도메인별 질문과 사전 점검이 포함되어 있습니다.
5. **규칙 충돌 확인은 MANDATORY** — brainstorming 중, agent는 사용자 요구사항이
   HARD GATE 규칙 (IFactory 패턴, skeleton-first, Output Isolation,
   SyncRunner/AsyncRunner)과 충돌하는지 반드시 확인해야 합니다. 충돌이 감지되면,
   agent는 brainstorming 중에 이를 해결해야 합니다 — 설계 spec에서 위반 요청을
   조용히 따르지 마세요. 위의 "규칙 충돌 해결"을 참조하세요.
## 필수 프로세스 스킬 시퀀스 — 모든 코드 생성 (HARD GATE)

이 gate는 `dx-agentic-dev/<session_id>/`에 코드 artifact를 생성하는 모든 세션에
적용됩니다. "내부 개발" SWE Process Gates와 독립적입니다 — 내부 개발 gate는
dx-agentic-dev infrastructure 작업에 적용되고, 이 gate는 user-facing 코드 생성
(inference app, pipeline, compilation)에 적용됩니다.

### 적용 시점

`dx-agentic-dev/<session_id>/`에 파일을 생성하는 모든 세션은 아래의 완전한
프로세스 스킬 시퀀스를 반드시 따라야 합니다:
- ONNX → DXNN compilation session
- Python/C++ inference app 생성 (dx_app)
- GStreamer pipeline 생성 (dx_stream)
- Cross-project session (compile + deploy)

### 필수 스킬 시퀀스

모든 코드 생성 세션은 이 시퀀스를 순서대로 수행해야 합니다.
**이 시퀀스가 완료되기 전에는 코드 생성 금지.**

**Autopilot 모드도 이 시퀀스를 면제하지 않습니다.** "자율적으로 작업"은 물어보지
않고 모든 규칙을 따르라는 뜻이지, 규칙을 건너뛰라는 뜻이 아닙니다. Autopilot에서는
`ask_user` 대신 knowledge base 기반으로 결정하되, 아래 모든 단계는 동일하게
적용됩니다.

| Step | Skill | 요구사항 |
|------|-------|----------|
| 1 | `/dx-skill-router` | **항상** — 어떤 action보다 먼저 호출. `skill-router-mandatory` fragment로 이미 강제됨. |
| 2 | `/dx-brainstorm-and-plan` | **모든 non-trivial 코드 생성** — 요구사항 수집, approach 제안, 승인 후 파일 생성. |
| 3 | `/dx-writing-plans` | **항상** — 복잡도와 무관하게 모든 코드 생성 세션에서 구조화된 구현 계획 작성 필수. |
| 4 | `/dx-tdd` | **항상** — 합격 기준 정의 (Red), artifact 생성 (Green), 즉시 검증 (Verify). |
| 5 | `/dx-verify-completion` | **항상** — DONE 선언 전, 동작하는 artifact의 증거 제시 필수. 증거 없는 주장 금지. |

### 시퀀스 강제 규칙

1. **단계 생략 금지** — 각 단계는 다음 단계 시작 전에 완료되어야 합니다.
   예외: Step 1 (skill-router)은 별도 fragment로 이미 처리됨.
2. **순서 변경 금지** — brainstorm → plan → tdd → verify. 계획 전 코드 생성 금지.
   검증 전 완료 선언 금지.
3. **파일 생성 전 plan 필수** — 단일 파일 세션이라도 plan이 필요합니다
   (간략해도 되지만 명시적이어야 합니다).
4. **검증은 실제 실행 기반** — `python file.py`, `bash -n script.sh`,
   `import` 확인. "동작할 것이다"라는 주장은 실행 없이 불가.

### Trivial 변경 예외

Steps 2–3 (brainstorm/plan)은 다음 경우에만 생략 가능:
- 단일 config.json 필드 변경 (예: threshold 조정)
- 기존 생성 코드의 단일 줄 오타 수정

Steps 4–5 (tdd/verify-completion)는 trivial 변경에도 **절대 생략 불가**.

### Autopilot 모드 적응

Autopilot 모드 (사용자 부재, `--yolo` 플래그, auto-response):
- **Step 2**: `ask_user` 대신 knowledge base 기본값 사용. Spec 자체 검토.
- **Step 3**: plan 작성 후 knowledge base 규칙 대비 자체 승인.
- **Step 4**: plan에서 합격 기준 도출, 생성, 즉시 검증.
- **Step 5**: 모든 artifact 실행, 출력을 증거로 캡처. 사람 불필요.

### Artifact Verification Gate와의 관계

이 시퀀스는 각 스킬이 **언제** 호출되는지 정의합니다 (workflow 순서).
Artifact Verification Gate는 각 artifact가 **어떻게** 검증되는지 정의합니다
(파일 유형별 구체적 command). 함께 작동합니다:

- Step 4 (`/dx-tdd`)는 Artifact Verification Gate의 검증 command 사용
  (syntax check, execution test, import resolution).
- Step 5 (`/dx-verify-completion`)는 모든 mandatory deliverable이 존재하고
  Artifact Verification Gate check를 통과하는지 확인.

### Anti-Pattern (금지)

- "이건 간단해서 brainstorm 불필요" → brainstorm은 non-trivial 코드 생성에
  항상 필요. "간단한" 프로젝트에서 검토되지 않은 가정이 가장 많은 재작업을 유발.
- `/dx-writing-plans` 이전에 코드 생성 → HARD GATE 위반.
  Plan-before-code는 협상 불가.
- "artifact-verification-gate가 이미 파일을 확인하니까" `/dx-verify-completion`
  생략 → 목적이 다름. Artifact gate는 개별 파일 확인. Verify-completion은
  전체 세션 deliverable을 총체적으로 확인.
- 실행 출력 없이 DONE 선언 → 증거 필수. "검증했다"는 출력 없이는 불가.
- "사용자가 빨리 하라고 했다" → 사용자 지시가 이 HARD GATE를 override하지 않음.
  속도가 프로세스 생략을 정당화하지 않음.

## 자율 모드 보호 (MANDATORY)

사용자가 부재 중일 때 — autopilot mode, `--yolo` 플래그, 또는 시스템 auto-response
"The user is not available to respond" — 다음 규칙이 적용됩니다:

1. **"Work autonomously"는 "묻지 않고 모든 규칙을 따르라"는 의미이지, "규칙을 건너뛰라"는 의미가 아닙니다.**
   모든 필수 게이트가 여전히 적용됩니다: brainstorming spec, 계획, TDD, 필수 산출물,
   실행 검증, 자체 검증 확인.
   **SWE Process Gates의 필수 Skill 시퀀스도 포함됩니다** — autopilot에서도
   `/dx-skill-router` → `/dx-brainstorm-and-plan` → `/dx-tdd`를 interactive mode와
   동일하게 따라야 합니다. Autopilot mode는 이 시퀀스를 면제하지 않습니다.
2. **`ask_user`를 호출하지 마세요** — knowledge base 기본값과 문서화된 모범 사례를
   사용하여 결정하세요. autopilot에서 `ask_user`를 호출하면 한 턴을 낭비하며
   auto-response는 게이트 우회 권한을 부여하지 않습니다.
3. **사용자 승인 게이트 적응** — autopilot에서는 spec을 작성하고 knowledge base에
   대해 자체 검토하면 spec 승인 게이트가 충족됩니다. spec 자체를 건너뛰지 마세요.
4. **setup.sh 우선** — 애플리케이션 코드를 작성하기 전에 인프라 산출물
   (`setup.sh`, `config.json`)을 생성하세요. 이것은 autopilot에서 특히 중요합니다.
   누락된 종속성을 잡아줄 사람이 없기 때문입니다.
5. **실행 검증은 선택 사항이 아닙니다** — 생성된 코드를 실행하고 완료를 선언하기 전에
   작동하는지 확인하세요. autopilot에서는 오류를 잡아줄 사용자가 없습니다.
6. **시간 예산 인식** — Autopilot 세션에는 시간 제약이 있을 수 있습니다.
   효율적으로 행동을 계획하세요:
   - 컴파일 (ONNX → DXNN)은 5분 이상 걸릴 수 있습니다 — 일찍 시작하세요.
   - 시간이 부족하면, 실행 검증보다 산출물 생성을 우선시하세요 — 테스트되지 않은
     완전한 파일 세트가 테스트된 부분 세트보다 낫습니다.
   - 우선순위: `setup.sh` > `run.sh` > app 코드 > `verify.py` > session.log.
   - **컴파일 병렬 워크플로우 (HARD GATE)** — bash 명령으로 `dxcom` 또는
     `dx_com.compile()`을 실행한 후, 기다리지 마세요. 즉시 모든 필수 산출물을
     생성하세요: factory, app 코드, setup.sh, run.sh, verify.py. `.dxnn` 출력은
     다른 모든 산출물이 생성된 후에만 확인하세요. **이 규칙 위반은 세션 실패입니다.**
   - **컴파일을 위한 sleep-poll 금지** — `.dxnn` 파일을 polling하기 위해 `sleep`을
     루프에서 사용하지 마세요. 금지된 패턴:
     `for i in ...; do sleep N; ls *.dxnn; done`,
     `while ! ls *.dxnn; do sleep N; done`,
     반복적인 `ls *.dxnn` / `test -f *.dxnn` 확인과 그 사이의 대기.
     대신: 다른 모든 산출물을 먼저 생성한 후, `.dxnn` 파일이 존재하는지 한 번만
     확인하세요. 아직 존재하지 않으면, 컴파일이 완료될 것이라는 가정 하에 실행
     검증으로 진행하세요.
   - **필수 산출물은 컴파일과 독립적** — `setup.sh`, `run.sh`, `verify.py`, factory,
     app 코드는 `.dxnn` 파일이 존재할 필요가 없습니다. 알려진 모델 이름
     (예: `yolo26n.dxnn`)을 플레이스홀더 경로로 사용하여 생성하세요. 실행 검증만
     실제 `.dxnn`이 필요합니다.
7. **파일 읽기 도구 호출 최소화** — 이미 컨텍스트에 로드된 instruction 파일, agent
   문서, 스킬 문서를 다시 읽지 마세요. 불필요한 `cat` / `bash` 읽기는 각각 5-15초를
   낭비합니다. 시스템 프롬프트와 대화 이력에 있는 지식을 사용하세요.

## 하드웨어

| 아키텍처 | 값 |
|---|---|
| DX-M1 | `dx_m1` |

## Git 안전 — Superpowers 산출물

**`docs/superpowers/` 하위 파일을 절대 `git add`하거나 `git commit`하지 마세요.**
이들은 superpowers 스킬 시스템에서 생성된 임시 계획 산출물 (spec, plan)입니다.
`.gitignore`에 포함되어 있지만, 일부 도구는 `git add -f`로 `.gitignore`를 우회할 수
있습니다. 파일 생성은 괜찮습니다 — 커밋은 금지입니다.

## 세션 센티넬 (자동화 테스트용 MANDATORY)

사용자 프롬프트를 처리할 때, 테스트 하네스의 자동화된 세션 경계 감지를 위해
이 정확한 마커를 출력하세요:

- **응답의 첫 번째 줄**: `[DX-AGENTIC-DEV: START]`
- **모든 작업 완료 후 마지막 줄**: `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]`
  여기서 `<relative_path>`는 세션 출력 디렉토리입니다 (예: `dx-agentic-dev/20260409-143022_yolo26n_detection/`)

규칙:
1. **중요 — `[DX-AGENTIC-DEV: START]`를 첫 번째 응답의 절대적인 첫 줄로 출력하세요.**
   이것은 다른 어떤 텍스트, 도구 호출, 추론보다 먼저 나타나야 합니다.
   사용자가 "그냥 진행하라" 또는 "자체 판단을 사용하라"고 지시해도,
   START 센티넬은 협상 불가입니다 — 자동화 테스트는 이것 없이 실패합니다.
2. 모든 작업, 검증, 파일 생성이 완료된 후 맨 마지막 줄에 `[DX-AGENTIC-DEV: DONE (output-dir: <path>)]`를
   출력하세요
3. 상위 레벨 agent에 의해 handoff/routing으로 호출된 **서브 agent**인 경우,
   이 센티넬을 출력하지 마세요 — 최상위 agent만 출력합니다
4. 사용자가 세션에서 여러 프롬프트를 보내면, 각 프롬프트에 대해 START/DONE을 출력하세요
5. DONE의 `output-dir`은 프로젝트 루트에서 세션 출력 디렉토리까지의 상대 경로여야 합니다.
   파일이 생성되지 않았다면, `(output-dir: ...)` 부분을 생략하세요.
   **Cross-project 태스크** (예: compile + app 생성)의 경우, 모든 output directory를
   ` + ` 구분자로 나열하세요:
   ```
   [DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260409-143022_copilot_yolo26n_compile/ + dx-runtime/dx_app/dx-agentic-dev/20260409-143022_copilot_yolo26n_inference/)]
   ```
6. **계획 산출물만 생성한 후에는 절대 DONE을 출력하지 마세요** (spec, plan, 설계
   문서). DONE은 모든 산출물이 생성되었음을 의미합니다 — 구현 코드, 스크립트,
   설정, 검증 결과. brainstorming 또는 계획 단계를 완료했지만 실제 코드를 아직
   구현하지 않았다면, DONE을 출력하지 마세요. 대신, 구현으로 진행하거나
   사용자에게 진행 방법을 물어보세요.
7. **DONE 전 필수 산출물 확인**: DONE을 출력하기 전에, 아래의 자체 검증 확인을
   실행하세요. 필수 파일이 누락된 경우, DONE을 출력하기 전에 생성하세요.
   **이 단계를 절대 건너뛰지 마세요.**
   ```bash
   WORK_DIR="<session_output_directory>"
   echo "=== Mandatory Deliverable Check ==="
   for f in setup.sh run.sh verify.py session.log README.md config.json; do
       [ -f "${WORK_DIR}/$f" ] && echo "  ✓ $f" || echo "  ✗ MISSING: $f"
   done
   ls "${WORK_DIR}"/*.dxnn 2>/dev/null && echo "  ✓ .dxnn model" || echo "  ✗ MISSING: .dxnn model"
   ```
   산출물 중 MISSING이 있으면, 돌아가서 생성하세요. 누락된 산출물이 있는 상태에서
   최종 보고서를 제시하거나 DONE을 출력하지 마세요.
8. **세션 내보내기 안내**: DONE 센티넬 줄 바로 앞에, CLI 플랫폼에 맞는 세션 저장
   안내를 출력하세요:

   | 플랫폼 | 명령 | 형식 |
   |--------|------|------|
   | **Copilot CLI** | `/share html` | HTML 트랜스크립트 |
   | **Cursor CLI** (`agent`) | 내장 내보내기 없음 — 테스트 하네스가 `--output-format stream-json`으로 자동 저장 | JSON stream |
   | **OpenCode** | `/export` | JSON |
   | **Claude Code** (`claude`) | `/export` | TXT 트랜스크립트 — `<workdir>/YYYY-MM-DD-HHMMSS-<title>.txt`로 저장 |

   Copilot CLI의 경우: `To save this session as HTML, type: /share html`
   OpenCode의 경우: `To save this session as JSON, type: /export`
   Claude Code의 경우: `To save this session as a text transcript, type: /export`
   Cursor CLI의 경우: 사용자 작업이 필요 없습니다 — 테스트 하네스가 출력을 자동 캡처합니다.

   테스트 하네스 (`test.sh`)는 내보낸 아티팩트를 자동으로 감지하고
   세션 출력 디렉토리에 복사합니다.

## 필수 산출물

모든 컴파일 또는 앱 생성 세션은 DONE을 출력하기 전에 세션 출력 디렉토리
(`dx-agentic-dev/<session_id>/`)에 다음 파일을 생성해야 합니다. 이것은
**모든 작업 유형**에 적용됩니다 — compiler-only, app-only, cross-project.

| 파일 | 목적 | 필요한 경우 |
|------|------|-------------|
| `setup.sh` | 환경 설정 (sanity check, dxcom 설치, venv, pip deps) | 항상 |
| `run.sh` | venv activation을 포함한 원커맨드 inference 실행기 | 항상 |
| `README.md` | 세션 요약, 빠른 시작, 파일 목록 | 항상 |
| `verify.py` | ONNX vs DXNN 수치 비교 | 컴파일 포함 시 |
| `session.log` | 실제 명령 출력 로그 (손으로 작성한 요약이 아님) | 항상 |
| `config.json` | dxcom 컴파일 설정 | 컴파일 포함 시 |
| `*.dxnn` | 컴파일된 모델 바이너리 | 컴파일 포함 시 |

이것들은 애플리케이션별 아티팩트 (factory/inference 패턴을 가진 Python 파일,
GStreamer pipeline 코드 등)에 추가됩니다.

각 서브 프로젝트도 해당 agent/skill 문서에서 이 파일들의 템플릿을 정의합니다
(예: `dx-compiler/.deepx/agents/dx-dxnn-compiler.md` Phase 5.5).

### Cross-project suite 작업 — pre-DONE `.dxnn` 확인 (HARD GATE, REC-X4)

**컴파일이 포함된 모든 작업**에서 DONE sentinel을 출력하기 전에, `.dxnn` 파일이
compiler session 디렉토리에 존재하는지 확인하세요:

```bash
COMPILER_SESSION="<compiler_session_dir>"   # 예: dx-compiler/dx-agentic-dev/20260430-..._compile
test -f "${COMPILER_SESSION}/yolo26n.dxnn" \
  || { echo "BLOCKED: yolo26n.dxnn not found — 컴파일이 아직 실행 중입니다. compile.pid가 종료될 때까지 기다리세요."; exit 1; }
```

`yolo26n.dxnn`이 없는 상태에서 DONE을 출력하면 백그라운드 컴파일이 나중에 완료되더라도
`test_dxnn_compiled`가 실패합니다. Phase 5.8을 참조하세요: `dx-compiler/.deepx/agents/dx-dxnn-compiler.md`.

## Artifact 검증 게이트 (HARD GATE — 모든 코드 생성)

이 게이트는 코드 artifact를 생성하는 모든 session에 적용됩니다 (compilation,
app 생성, pipeline 생성). "Internal Development" SWE Process Gates와 독립적입니다
— 그것은 dx-agentic-dev feature 작업에 적용되고, 이 게이트는 사용자 대상
deliverable에 적용됩니다.

### 이 게이트가 적용되는 경우

`dx-agentic-dev/<session_id>/`에 파일을 생성하는 모든 session은 DONE 선언 전에
해당 파일을 검증해야 합니다:
- Compilation session (ONNX → DXNN)
- App 생성 session (dx_app factory + runner)
- Pipeline session (dx_stream pipeline)
- Cross-project session (compile + deploy)

### 필수 검증 단계

각 artifact 생성 후 즉시 검증 (끝에 몰아서 하지 말 것):

| Artifact | 검증 명령 | 통과 조건 |
|----------|----------|-----------|
| `setup.sh` | `bash -n setup.sh && bash setup.sh` | Exit code 0, 에러 없음 |
| `run.sh` | `bash -n run.sh` | 문법 OK (전체 실행은 model 필요) |
| `verify.py` | `python verify.py; echo "exit: $?"` | Exit code 0, 출력에 "RESULT: PASS" 포함 |
| `*.py` (factory) | `python -c "import py_compile; py_compile.compile('<file>', doraise=True)"` | 문법 OK |
| `*.py` (app) | `PYTHONPATH=. python -c "import py_compile; py_compile.compile('<file>', doraise=True)"` | 문법 OK |
| `config.json` | `python -c "import json; json.load(open('config.json'))"` | 유효한 JSON |

### verify.py 실행 테스트 (MANDATORY)

`verify.py`는 venv를 수동으로 활성화하지 않은 상태에서 실행해 self-contained 여부를 확인해야 합니다:

```bash
python verify.py    # NOT: source venv/bin/activate && python verify.py
echo "Exit code: $?"
```

필수 동작:
1. ONNX와 DXNN 추론이 모두 성공하면 **exit code 0**
2. 추론이 하나라도 실패하면 **exit code 1** (ImportError, RuntimeError 등)
3. **Self-contained**: 호출자의 venv 활성화 없이 내부에서 필요한 site-packages를 `sys.path`에 자동 추가

verify.py가 "ONNX inference failed" 또는 "DXNN inference failed"를 출력하면서 exit 0을 반환하면 **버그**입니다. 진행 전에 exit code를 수정하세요.

일반적인 실패 원인:
- `No module named 'onnxruntime'` → verify.py가 compiler venv site-packages를 sys.path에 추가해야 함
- `No module named 'dx_engine'` → verify.py가 runtime venv site-packages를 sys.path에 추가해야 함
- "failed" 출력 후 exit 0 → 실패 분기에 `sys.exit(1)` 추가 필요

### setup.sh 실행 테스트 (MANDATORY)

`setup.sh`는 session directory에서 실행해야 합니다 (문법 체크만이 아님).
실패 시:
1. 에러 진단
2. script 수정
3. 통과할 때까지 재실행

테스트할 일반적 실패 원인:
- PEP 668 "externally-managed-environment" → venv 사용 필수
- 비공개 package에 대한 `pip install <package>` → local install 또는 사전 설치된 venv 사용
- symlink된 directory에서 상대 경로 해석 → `$(cd "$(dirname "$0")" && pwd -P)` 패턴 사용
- 누락된 dependency → `pip install` 목록 완전성 확인

### Import 해석 테스트 (Python app에 MANDATORY)

모든 Python 파일 생성 후, **외부 PYTHONPATH 없이** session 디렉토리에서 실행:
— 이 방식은 생성된 `_sync.py`의 dynamic walker가 `src/python_example/common`을
스스로 올바르게 해석하는지 검증합니다:

```bash
cd <session_dir>
python <model>_sync.py --help 2>&1 | head -10
```

기대 결과: `--help` 출력(usage/argparse 텍스트). `ImportError: No module named 'common'`가
나타나면, `_sync.py`의 dynamic path walker가 실패한 것 — `PYTHONPATH=../../`로 우회하지 말고
`_sync.py`의 walker를 직접 수정하세요.

**금지 패턴**:
```bash
# 잘못된 방법 — agent 환경에서 통과해도 생성 코드의 broken path를 숨김
PYTHONPATH=../../ python -c "from factory import <Model>Factory; print('import OK')"
```

### session.log는 실제 출력이어야 함 (MANDATORY)

`session.log`는 실제 터미널 명령 출력을 포함해야 합니다:
```bash
command 2>&1 | tee session.log
```

다음 패턴은 session.log에 대해 금지됨:
- `cat << 'EOF' > session.log` (heredoc 조작)
- `cat << 'LOGEOF' > session.log` (heredoc 조작)
- `echo "..." > session.log` (수작업 요약)
- `printf "..." > session.log` (수작업 요약)
- 명령을 실행하지 않고 메모리에서 session.log 내용 작성

### dx-tdd 및 프로세스 스킬 시퀀스 (모든 코드 생성에 MANDATORY)

완전한 프로세스 스킬 시퀀스 (`/dx-brainstorm-and-plan` → `/dx-writing-plans`
→ `/dx-tdd` → `/dx-verify-completion`)는 모든 artifact 생성 session에서
MANDATORY입니다. 전체 시퀀스 정의와 강제 규칙은 **"필수 프로세스 스킬 시퀀스 —
모든 코드 생성"** 섹션을 참조하세요.

이 Artifact Verification Gate 내에서 `/dx-tdd` Red-Green-Verify cycle은
각 artifact에 적용됩니다:
1. **RED**: 각 artifact가 만족해야 할 조건 정의 (문법, 실행, import)
2. **GREEN**: artifact 생성
3. **VERIFY**: 생성 직후 즉시 체크 실행 (이 섹션 위에 정의된 verification
   command 사용)

Autopilot mode에서도 선택사항이 아닙니다. 코드 생성에서 어떤 프로세스 스킬을
건너뛰는 것은 task가 "internal development"인지 "user-facing"인지에 관계없이
session 실패 위반입니다.

## 사전 요구사항 점검 (HARD GATE)

코드 생성, 파일 생성, 또는 sub-agent 라우팅 전에, 다음 환경 점검이 반드시
통과해야 합니다. 이 게이트는 스위트 수준에서 적용됩니다 — 브레인스토밍이 spec과
plan을 생성했더라도, 이 점검은 구현 전에 반드시 실행되어야 합니다.

```bash
# 1. dx-runtime sanity check (MANDATORY — 건너뛰지 마세요)
bash dx-runtime/scripts/sanity_check.sh --dx_rt
# 중요: 종료 코드가 아닌 텍스트 출력으로 PASS/FAIL을 판단하세요.
# Agent는 종종 `| tail` 또는 `| head`를 통해 파이프하는데, 이는 실제 종료 코드를
# tail의 종료 코드 (항상 0)로 조용히 대체합니다.
# PASS = 출력에 "Sanity check PASSED!"가 포함되고 [ERROR] 줄이 없음
# FAIL = 출력에 "Sanity check FAILED!"가 포함되거나 [ERROR] 줄이 있음
# 절대 tail/head/grep을 통해 파이프하지 마세요 — 명령을 직접 실행하세요.
# FAIL인 경우 → install을 실행한 다음, 재확인:
bash dx-runtime/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse
bash dx-runtime/scripts/sanity_check.sh --dx_rt  # install 후 반드시 PASS해야 함

# 2. dx_engine import 점검 (앱 생성 작업에 MANDATORY)
python -c "import dx_engine; print('dx_engine OK')" 2>/dev/null || {
    echo "dx_engine not available. Run: cd dx-runtime/dx_app && ./install.sh && ./build.sh"
}

# 3. dxcom 가용성 점검 (컴파일 작업에 MANDATORY)
python -c "import dx_com; print('dxcom OK')" 2>/dev/null || {
    echo "dxcom not available."
    # 설치 폴백:
    #   1. pip install dxcom (venv인 경우)
    #   2. bash dx-compiler/install.sh (가능한 경우)
    #   3. source dx-compiler/venv-dx-compiler-local/bin/activate (존재하는 경우)
    # 모두 실패하면 → 중지하고 사용자에게 알리세요. 절대 dxcom 없이 진행하지 마세요.
}
```

**이것은 HARD GATE입니다:**
- 이 점검이 통과할 때까지 구현 코드를 생성하지 마세요
- 브레인스토밍이나 계획이 완료되었다고 이 점검을 건너뛰지 마세요
- 각 서브 프로젝트 빌더에도 자체 Step 0 Prerequisites가 있습니다 — 이것들은
  이 스위트 수준 점검의 대체가 아닌 추가 점검입니다
- 점검이 실패하면, 정확한 수정 명령과 함께 사용자에게 알리고 중지하세요

### dxcom Anti-Fabrication (컴파일 작업에 MANDATORY)

dxcom이 사용 가능하고 컴파일이 진행되는 경우:
- **절대 기억에서 dxcom API 호출을 조작하지 마세요.** 항상 toolset 파일을 읽으세요:
  - CLI: `dx-compiler/.deepx/toolsets/dxcom-cli.md`
  - Python API: `dx-compiler/.deepx/toolsets/dxcom-api.md`
  - Config schema: `dx-compiler/.deepx/toolsets/config-schema.md`
- **올바른 import**: `import dx_com; dx_com.compile(...)` (`from dxcom import dxcom`이 아님)
- **절대 `compiler.properties`를 수정하지 마세요** — 설치 프로그램이 관리하는 시스템 파일입니다.
  `dx-compiler/.deepx/memory/common_pitfalls.md` Pitfalls #21과 #22를 참조하세요.

### Background Compilation (RECOMMENDED)

`subprocess.Popen`을 사용한 컴파일은 에이전트의 tool-call 스레드가 10분 이상
블록되는 것을 방지하여 병렬 artifact 생성을 가능하게 합니다.

**권장 패턴** — `compile.pid` 파일과 함께 `subprocess.Popen` 사용:
```python
import subprocess, os
compile_script = f"{work_dir}/compile.py"
compile_out = open(f"{work_dir}/compile_out.log", "w")
proc = subprocess.Popen(
    ["python3", compile_script],
    stdout=compile_out, stderr=subprocess.STDOUT,
    cwd=work_dir, start_new_session=True,
)
with open(f"{work_dir}/compile.pid", "w") as f:
    f.write(str(proc.pid))
# 이제 compile.pid / .dxnn 존재 여부 확인 전에 다른 모든 artifact를 생성하세요.
# (factory, sync.py, setup.sh, run.sh, verify.py 등 모든 artifact 생성 후 확인)
```

동기 컴파일도 에이전트가 블록 시간을 감당할 수 있다면 허용되지만,
timeout 방지를 위해 background 컴파일이 권장됩니다.

### Sanity Check 실패 복구 (MANDATORY)

`sanity_check.sh --dx_rt`가 FAIL을 반환하면, 다음 정확한 복구 순서를 따르세요:

1. **install.sh 실행** 위에 표시된 명령으로
2. **sanity_check.sh 재실행** — install 후 점검이 반드시 통과해야 합니다
3. **여전히 실패하는 경우**: **compiler-only 작업**인지 아닌지 확인:

   **A. Compiler-only 작업** (ONNX → DXNN 컴파일, dx_app/dx_stream 작업 없음):
   - 사용자에게 sanity check가 실패했고 NPU 기반 검증이 건너뛰어질 것임을 알리세요.
   - **컴파일 진행** — `dxcom`은 CPU에서 실행되며 NPU 하드웨어가 필요하지 않습니다.
   - 컴파일 성공 후, `verify.py`를 **SKIPPED** (PASS가 아님)로 표시하세요.
   - verify.py가 NPU 기반 점검을 감지하고 건너뛸 수 있도록 `DX_SANITY_FAILED=1`을
     설정하세요.
   - session.log에 기록: `sanity_check=FAIL, compilation=<result>, verification=SKIPPED`.
   - 사용자에게 알리세요:
     ```
     NPU hardware initialization failed. Compilation completed successfully,
     but DXNN verification (verify.py) requires a working NPU.
     After resolving the NPU issue (cold boot recommended), run:
       cd <session_dir> && python verify.py
     ```

   **B. Cross-project 작업** (컴파일 + dx_app/dx_stream 데모 앱) 또는 dx_app/dx_stream만:
   - **무조건 중지** — 사용자가 "그냥 계속해", "완료까지 작업해", "기본값 사용",
     또는 "점검 건너뛰기"라고 말하더라도, agent는 절대 진행해서는 안 됩니다.
     사용자의 계속 지시는 이 HARD GATE를 오버라이드하지 않습니다.
   - 사용자를 수동 복구로 안내:
     - 실패가 **"Device initialization failed"**, **"Fail to initialize device"**,
       또는 **NPU 하드웨어 오류**를 언급하는 경우: NPU는 콜드 부트 (전체 전원
       차단) 또는 시스템 재부팅이 필요합니다. 소프트웨어만으로는 하드웨어
       초기화 실패를 수정할 수 없습니다. 사용자에게 알리세요:
       ```
       NPU hardware initialization failed. This issue cannot be resolved by software installation alone.
       Please follow these steps:
       1. Fully shut down the system (power off — a cold boot is recommended, not just a reboot)
       2. Wait 10-30 seconds
       3. Power on the system
       4. After restart, verify NPU status with the sanity check:
          bash dx-runtime/scripts/sanity_check.sh --dx_rt
       5. Once the sanity check PASSES, please retry this task.
       ```
     - 실패가 다른 오류인 경우: 사용자에게 특정 오류와 권장 수정 명령을
       보여주고 중지하세요.

4. **절대 우회 금지** (non-compiler-only 작업의 경우) — sanity check는 전체
   dx-runtime 환경이 작동하는지 확인하기 위해 존재합니다. dx_app/dx_stream
   작업에서 복구를 건너뛰면 데모/검증 스크립트가 실패합니다.
   다음은 모두 우회로 간주되며 금지됩니다:
   - dx_engine 아티팩트를 가리키도록 PYTHONPATH 또는 LD_LIBRARY_PATH를 수동 설정
   - 다른 저장소의 venv (예: compiler venv)를 dx_engine import에 사용
   - dx_engine이 import되는 venv를 여러 개 검색
   - 출력 텍스트에 FAILED 또는 [ERROR]가 표시될 때 "종료 코드가 0이었으므로
     통과"라고 결론
   - sanity_check.sh를 `| tail` / `| head` / `| grep`을 통해 파이프하고
     파이프의 종료 코드를 사용
   - 사용자의 "그냥 계속해" / "완료까지 작업해" / "기본값 사용" / autopilot
     지시를 HARD GATE를 오버라이드하는 권한으로 재해석
   - 실제로 실패한 prerequisite 점검을 "완료" 또는 "통과"로 표시
   참고: compiler-only 작업 (항목 3A 위)은 이 중지에서 면제 — 컴파일은
   진행되지만, 검증은 PASS가 아닌 SKIPPED로 표시됩니다.
5. **일반적인 실패 원인**:
   - NPU 드라이버 미설치 → `install.sh` with `dx_rt_npu_linux_driver` target
   - dx_engine 빌드 아티팩트 누락 → `cd dx_app && ./install.sh && ./build.sh`
   - PEP 668 (Ubuntu 24.04+) pip 차단 → venv를 사용해야 함 (절대 `--break-system-packages` 사용 금지)

## 규칙 충돌 해결 (HARD GATE)

사용자의 요청이 HARD GATE 규칙과 충돌할 때, agent는 반드시:

1. **사용자의 의도를 인정** — 원하는 것을 이해했음을 보여주세요.
2. **충돌을 설명** — 구체적인 규칙과 그 이유를 인용하세요.
3. **올바른 대안을 제안** — 프레임워크 내에서 사용자의 목표를 달성하는 방법을
   보여주세요. 예를 들어, 사용자가 직접 `InferenceEngine.run()` 사용을 요청하면,
   IFactory 패턴이 동일한 API를 래핑함을 설명하고 factory 기반 동등물을 제안하세요.
4. **올바른 접근 방식으로 진행** — 규칙 위반 요청을 조용히 따르지 마세요.
   "옵션 A vs 옵션 B"로 제시하지 마세요.

**일반적인 충돌 패턴** (실제 세션에서):
- 사용자가 "use `InferenceEngine.Run()`"이라고 말함 → IFactory 패턴 사용 필수
  (engine 호출은 SyncRunner/AsyncRunner가 내부에서 처리함; IFactory 5-method
  구현 필수: `create_preprocessor`, `create_postprocessor`, `create_visualizer`,
  `get_model_name`, `get_task_type`)
- 사용자가 "clone demo.py and swap onnxruntime"이라고 말함 → `src/python_example/`에서
  skeleton-first 사용 필수, 사용자 스크립트 clone 금지
- 사용자가 "create demo_dxnn_sync.py"라고 말함 → SyncRunner와 함께
  `<model>_sync.py` 네이밍 사용 필수, standalone 스크립트 금지
- 사용자가 "use `run_async()` directly"라고 말함 → 수동 async 루프가 아닌
  AsyncRunner 사용 필수

**이 규칙은 명시적 사용자 오버라이드를 무시하지 않습니다**: 사용자가 충돌에 대해
안내받은 후, 명시적으로 "규칙을 이해합니다, 직접 API 사용으로 진행하세요"라고
말하면, 따르세요. 하지만 agent는 충돌을 먼저 설명해야 합니다 — 조용한 순응은
항상 위반입니다.

## 서브 프로젝트 개발 규칙 (MANDATORY — 자체 완결)

이 규칙들은 **권위적이고 자체 완결적**입니다. 서브 프로젝트 파일이 로드되었는지
여부에 관계없이 반드시 따라야 합니다. interactive mode에서는 git submodule
경계로 인해 서브 프로젝트 파일이 로드되지 않습니다 — 이 규칙들이 유일한
보호입니다.

**중요**: 이것들은 선택적 요약이 아닙니다. 아래의 모든 규칙은 HARD GATE입니다.
규칙을 위반하면 (예: skeleton-first 건너뛰기, IFactory 미사용, 소스 디렉토리에
쓰기) 진행 전에 수정해야 하는 차단 오류입니다.

**추가 컨텍스트**: 서브 프로젝트에서 작업할 때, 해당 서브 프로젝트의
`AGENTS.md`도 읽어 확장된 컨텍스트 (model registry, import 패턴 등)를
확인하세요. 하지만 아래 규칙들은 서브 프로젝트 파일을 읽지 않아도 올바른
코드 생성에 충분합니다.

### dx_app 규칙 (Standalone Inference)

1. **Skeleton-first 개발** — 코드를 작성하기 전에
   `dx-runtime/dx_app/.deepx/skills/dx-build-python-app.md` skeleton 템플릿을
   읽으세요. `src/python_example/<task>/<model>/`에서 가장 가까운 기존 예제를
   복사하고 모델별 부분 (factory, postprocessor)만 수정하세요. 절대 데모
   스크립트를 처음부터 작성하지 마세요. 절대 프레임워크를 우회하는 독립
   스크립트를 제안하지 마세요.
2. **IFactory 패턴은 MANDATORY** — 모든 inference 앱은 IFactory 5-method 패턴
   (create_preprocessor, create_postprocessor, create_visualizer, get_model_name, get_task_type)을 사용해야
   합니다. 대안적인 inference 구조를 발명하지 마세요. 독립 스크립트에서의 직접
   `InferenceEngine` 사용은 위반입니다 — factory 패턴을 통해야 합니다.
   **사용자가 명시적으로 API 메서드를 지정하더라도** (예: "`InferenceEngine.run()`
   사용", "`run_async()` 사용"), agent는 IFactory 패턴 안에 해당 호출을 래핑하고
   사용자에게 규칙을 설명해야 합니다. 위의 "규칙 충돌 해결"을 참조하세요.
3. **SyncRunner/AsyncRunner만** — 프레임워크의 SyncRunner (단일 모델) 또는
   AsyncRunner (다중 모델)를 사용하세요. 절대 대안적 실행 접근법을 제안하지
   마세요 (독립 스크립트, 직접 API 호출, 커스텀 러너, 수동 `run_async()` 루프).
4. **대안 제안 금지** — 앱 아키텍처에 대해 "옵션 A vs 옵션 B" 선택지를 제시하지
   마세요. 프레임워크가 변형별로 하나의 올바른 패턴을 지시합니다.
5. **Registry key ≠ class name** — `model_registry.json`의 모델 레지스트리 키는
   lookup을 통해 postprocessor 클래스에 매핑됩니다. 올바른 매핑을 찾기 위해
   레지스트리를 읽으세요.
6. **기존 예제 MANDATORY** — 새로운 앱을 작성하기 전에, `src/python_example/`에서
   동일한 AI 태스크의 기존 예제를 검색하세요. 참조로 사용하세요.
7. **DXNN 입력 형식 자동 감지** — 전처리 차원이나 형식을 절대 하드코딩하지 마세요.
   DXNN 모델은 `dx_engine`을 통해 입력 요구사항을 자체 기술합니다.
8. **출력 격리** — 모든 생성된 코드는 `dx-agentic-dev/<session_id>/`에 있어야
   합니다. 사용자가 명시적으로 "소스 디렉토리에 작성"이라고 말하지 않는 한,
   기존 소스 디렉토리 (예: `src/`, `semseg_260323/`, 또는 사용자의 기존 코드가
   포함된 모든 디렉토리)에 절대 쓰지 마세요.

### dx-compiler 규칙 (Model Compilation)

1. **이전 세션 참조 금지** — 이전 agentic 세션의 결과를 절대 참조하거나 재사용하지
   마세요. 각 세션은 새로 시작합니다.
2. **session.log = 실제 명령 출력** — 세션 로그는 실제 터미널 출력을 포함해야
   합니다. 절대 손으로 작성한 요약이나 `cat << 'EOF'` 블록을 생성하지 마세요.
3. **config.json schema** — config.json을 작성하기 전에 항상
   `dx-compiler/.deepx/toolsets/config-schema.md`를 읽으세요. 절대 schema 필드를
   조작하지 마세요.
4. **dxcom fabrication 패턴** — 위의 "dxcom Anti-Fabrication" 섹션을 참조하세요.
5. **setup.sh 5단계 템플릿** — mandatory setup.sh 구조를 위해
   `dx-compiler/.deepx/agents/dx-dxnn-compiler.md` Phase 5.5를 읽으세요.

### dx_stream 규칙 (GStreamer Pipelines)

1. **x264enc tune=zerolatency** — x264enc element에 항상 `tune=zerolatency`를
   설정하세요.
2. **처리 단계 사이의 Queue** — GStreamer 데드락을 방지하기 위해 처리 단계 사이에
   항상 `queue` element를 추가하세요.
3. **기존 pipeline MANDATORY** — 새로운 pipeline 설정을 만들기 전에 `pipelines/`에서
   기존 예제를 검색하세요.

### 공통 규칙 (모든 서브 프로젝트)

1. **PPU 모델 자동 감지** — postprocessor 코드를 라우팅하거나 생성하기 전에
   모델 이름 접미사 (`_ppu`), README, 또는 registry에서 PPU 플래그를 확인하세요.
2. **빌드 순서** — dx_rt → dx_app → dx_stream. 절대 순서를 바꾸지 마세요.
3. **서브 프로젝트 컨텍스트 로딩** — 서브 프로젝트로 라우팅하거나 서브 프로젝트
   내에서 작업할 때, 항상 해당 서브 프로젝트의 `AGENTS.md`를 먼저 읽으세요.

## 계획 출력 (MANDATORY)

계획 문서를 생성할 때 (예: writing-plans 또는 brainstorming 스킬을 통해),
파일을 저장한 직후 **대화 출력에 전체 계획 내용을 항상 인쇄하세요**. 파일 경로만
언급하지 마세요 — 사용자가 별도의 파일을 열지 않고 프롬프트에서 직접 계획을
검토할 수 있어야 합니다.


---

## SWE 프로세스 게이트 — 내부 개발 (HARD GATE)

AI 에이전트(Claude Code, Copilot CLI, Cursor CLI, Copilot Chat (VS Code),
Cursor (IDE), OpenCode, 기타 모든 도구)를 사용하여 내부 dx-agentic-dev 기능을
개발하거나 수정할 때는 전체 소프트웨어 엔지니어링 규율이 **필수**입니다.
내부 dx-agentic-dev 기능에 해당하거나 관련된 모든 작업에 적용됩니다.
다음 경로들이 적용 대상입니다 (비-완전 목록 — 확실하지 않을 경우 SWE 규율을 적용하세요):

| 경로 | 예시 |
|------|------|
| `tests/test_agentic_e2e_scenarios/` | `conftest.py`, `test_*.py` fixture |
| `tests/test_agentic_scenarios/` | 시나리오 테스트 케이스 |
| `tests/test.sh` | 수동/자동 shell runner |
| `tests/conftest.py`, `tests/parse_copilot_session.py` | 공유 테스트 인프라 |
| `tools/dx-agentic-dev-gen/` | generator 소스, CLI, transformer |
| `tools/*.sh` | loop 스크립트 및 orchestration runner (예: `run-e2e-improvement-loop.sh`) |
| `.deepx/` | agent, skill, 템플릿, fragment (canonical source) |

이 규칙은 아래 **Instruction File Verification Loop**에 **추가로** 적용됩니다.

### 필수 Skill 시퀀스 (비-trivial 변경)

모든 비-trivial 내부 변경은 반드시 이 시퀀스를 거쳐야 합니다.
**이 시퀀스가 완료되기 전까지 코드 작성 금지.**

**Autopilot mode는 이 시퀀스를 면제하지 않습니다.** "자율적으로 작업하라"는
"묻지 말고 모든 규칙을 따르라"는 의미이지, "규칙을 건너뛰어도 된다"는 의미가 아닙니다.
Autopilot에서는 `ask_user` 대신 knowledge base 기본값으로 결정하되,
아래 모든 단계는 그대로 적용됩니다.

| 단계 | Skill | 적용 시점 |
|------|-------|-----------|
| 1 | `/dx-skill-router` | **HARD GATE** — 경로 분류 전, SWE 게이트 체크 전, 파일 읽기 전에 반드시 호출. 어떤 조건에서도 이 단계를 건너뛰거나 미룰 수 없습니다. |
| 2 | `/dx-brainstorm-and-plan` | 기능 추가, 동작 변경, 구조적 리팩토링 시 |
| 3 | `/dx-writing-plans` | 승인된 계획이 >2 구현 단계를 포함할 때 |
| 4 | `/dx-tdd` | 모든 코드 변경 — 구현 전 테스트/검증을 먼저 확인하거나 작성 |
| 5 | Verification loop | 모든 변경 후 — generator + drift check + test 실행 |
| 6 | `/dx-verify-completion` | 완료 선언 전 — 주장이 아닌 증거 필요 |

**Non-trivial 판단 기준**: 변경이 ≥2개 파일 또는 ≥2개 레포에 영향을 미치면
Non-trivial로 간주하며, Trivial 변경 예외가 적용되지 않습니다. **이 기준은
위의 SWE 경로 목록과 독립적으로 적용됩니다** — 목록에 없는 경로의 파일이라도
≥2개를 변경하면 `/dx-brainstorm-and-plan`이 필요합니다.

### "테스트 우선"의 의미

내부 개발 맥락에서 `/dx-tdd`:

- **`tests/` 변경** — 기존 suite를 실행하여 구현 전 **RED** 상태를 확인합니다.
  코드를 작성하기 전에 예상된 이유로 테스트가 실패해야 합니다.
- **`.deepx/` 변경** — 편집 전 `dx-agentic-gen check` 기준 출력을 캡처합니다.
  변경 후 재실행하여 의도한 drift만 나타나는지 확인합니다.
- **`tools/` 변경** — 변경이 해소해야 할 구체적인 실패 모드(잘못된 경로, 잘못된 출력,
  누락된 규칙)를 식별합니다. 이를 포착하는 테스트를 작성하거나 가리킵니다.
- **`test.sh` 변경** — 편집 전 실행 경로를 수동으로 추적하거나 (`bash -n` 구문 검사).
  필요 시 `bash -x`로 영향받는 코드 경로를 확인합니다.

### Trivial 변경 예외

다음의 경우에만 2–3단계(brainstorm/plan)를 건너뛸 수 있습니다:
- 한 줄 오탈자 또는 문구 수정
- 순수 서식 변경 (공백, 빈 줄)
- 명백하고 격리된 원인을 가진 단일 변수 이름 변경

4–6단계(TDD, verification, completion check)는 trivial 변경에도 **절대 건너뛸 수 없습니다**.

### Hard Gate

| Gate | 규칙 |
|------|------|
| **계획 없이 코드 작성 금지** | >1 파일에 영향을 미치는 변경은 먼저 승인된 계획 필요 |
| **실패하는 테스트 없이 기능 추가 금지** | RED 확인 후에만 구현 |
| **증거 없이 완료 선언 금지** | pytest/generator 출력 제시 — 완료 주장 불가 |
| **생성된 파일 직접 편집 금지** | `CLAUDE.md`, `AGENTS.md`, `.claude/` → `.deepx/` source 편집 |

### 흔한 안티패턴 (금지)

- "변경이 명확하다"는 이유로 `/dx-brainstorm-and-plan` 건너뛰기 — 절대 명확하지 않음
- 테스트 suite 실행 없이 fixture 추가 또는 `conftest.py` 변경 (눈먼 변경)
- 실제 pytest 출력 또는 `dx-agentic-gen check` 출력 없이 완료 주장
- "마지막에 검증하겠다" 방식 — `/dx-tdd`에 따라 파일별로 검증
- generator 출력 파일 직접 편집 — 다음 `dx-agentic-gen generate` 실행 시 덮어씌워짐
- `/dx-skill-router` 호출 전 구현 시작
- **Autopilot mode를 면제로 오해** — autopilot은 "묻지 않기"를 의미할 뿐,
  "규칙 없음"이 아닙니다. Autopilot에서도 필수 Skill 시퀀스는 완전히 적용됩니다.
- `tools/*.sh` 스크립트를 `tools/dx-agentic-dev-gen/`에 없다는 이유로 "내부 개발 아님"으로 취급하기 —
  `tools/` 하위의 모든 loop 및 orchestration 스크립트는 내부 dx-agentic-dev 기능이며 SWE 규율이 적용됩니다
- **`dx-systematic-debugging` 완료를 SWE gate 면제로 취급** — Phase 1–3 (근본 원인 파악)을
  완료했다고 해서 구현 작업이 SWE 필수 시퀀스에서 면제되는 것은 아닙니다. Phase 4 구현이
  `.deepx/`, `tests/`, 또는 `tools/`를 포함할 경우, 이는 **새로운 내부 개발 작업**으로서
  `/dx-skill-router`부터 시퀀스를 **재시작**해야 합니다.
  `dx-systematic-debugging` Phase 4의 SWE Gate Pre-Flight를 참조하세요.
- **이전 Skill 호출을 현재 메시지 적용 범위로 취급** — `/dx-skill-router`는 **각 사용자
  메시지** 시작 시 호출되어야 합니다. 이전 메시지의 호출은 이월되지 않습니다.
  "이미 이 세션에서 호출했다"는 합리화입니다.

---

## Instruction File Verification Loop (HARD GATE) — 내부 개발 전용

canonical source 수정 시 — `**/.deepx/**/*.md` 파일(agents, skills, templates,
fragments 포함) — 작업 완료 선언 전에 다음 루프를 **반드시** 수행해야 합니다:

1. **Generator 실행** — `.deepx/` 변경을 모든 플랫폼으로 전파:
   ```bash
   dx-agentic-gen generate
   # Suite 전체: bash tools/dx-agentic-dev-gen/scripts/run_all.sh generate
   ```
2. **Drift 검증** — 생성물과 commit 상태 일치 확인:
   ```bash
   dx-agentic-gen check
   ```
   drift 발견 시 1단계로 복귀.
3. **자동화 테스트 루프** — 테스트는 generator 출력이 정책을 만족하는지 검증:
   ```bash
   python -m pytest tests/test_agentic_scenarios/ -v --tb=short
   ```
   실패 처리:
   - generator 버그 → generator 수정 → 1단계
   - `.deepx/` 콘텐츠 누락 → `.deepx/` 수정 → 1단계
   - 테스트 규칙 부족 → 테스트 강화 → 1단계
4. **수동 감사** — 테스트 결과에 의존하지 않고, 생성된 파일들을 독립적으로 읽어
   크로스 플랫폼 sync(CLAUDE vs AGENTS vs copilot)와 레벨 간 sync(suite → 하위)를
   검증.
5. **갭 분석** — 수동 감사에서 발견한 이슈:
   - generator가 놓친 경우 → **generator 규칙 수정** 후 1단계
   - 테스트가 놓친 경우 → **테스트 강화** 후 1단계
6. **반복** — 3~5단계 모두 통과할 때까지.

### Pre-flight Classification (MANDATORY)

저장소 내의 `.md` 또는 `.mdc` 파일을 수정하기 전에, 반드시 다음 3가지 카테고리
중 하나로 분류하세요. **이 단계를 절대 건너뛰지 마세요** — generator 관리 파일을
직접 수정하면 다음 generate에서 조용히 덮어써지는 사일런트 손상이 됩니다.

**모든 파일 편집 전 다음 세 가지 질문에 순서대로 답하세요:**

> **Q1. 파일 경로가 `**/.deepx/**` 내부에 있나요?**
> - YES → **Canonical source.** 직접 수정 후 `dx-agentic-gen generate` + `check` 실행.
> - NO → Q2로 이동.
>
> **Q2. 파일 경로 또는 이름이 다음 중 하나와 일치하나요?**
> ```
> .github/agents/    .github/skills/    .opencode/agents/
> .claude/agents/    .claude/skills/    .cursor/rules/
> CLAUDE.md          CLAUDE-KO.md       AGENTS.md    AGENTS-KO.md
> copilot-instructions.md               copilot-instructions-KO.md
> ```
> - YES → **Generator output. 직접 수정 금지.**
>   `.deepx/` source(template, fragment, 또는 agent/skill)를 찾아 수정한 후
>   `dx-agentic-gen generate`를 실행하세요.
> - NO → Q3으로 이동.
>
> **Q3. 파일이 `<!-- AUTO-GENERATED`로 시작하나요?**
> - YES → **Generator output. 직접 수정 금지.** Q2와 동일.
> - NO → **Independent source.** 직접 수정 가능. 수정 후 `dx-agentic-gen check`를 한 번 실행.

1. **Canonical source** (`**/.deepx/**/*.md`) — 직접 수정 후 위의 Verification
   Loop을 실행합니다.
2. **Generator output** — 알려진 출력 경로의 파일:
   `CLAUDE.md`, `CLAUDE-KO.md`, `AGENTS.md`, `AGENTS-KO.md`,
   `copilot-instructions.md`, `.github/agents/`, `.github/skills/`,
   `.claude/agents/`, `.claude/skills/`, `.opencode/agents/`, `.cursor/rules/`
   → **직접 수정 금지.** `.deepx/` source(template, fragment, 또는
   agent/skill)를 찾아 수정한 후 `dx-agentic-gen generate`를 실행하세요.
3. **독립 소스** — 위 두 카테고리에 해당하지 않는 모든 파일 (`docs/source/`,
   `source/docs/`, `tests/`, 서브 프로젝트의 `README.md` 등)
   → 직접 수정 가능. 수정 후 `dx-agentic-gen check`를 한 번 실행하여 예상치
   못한 drift가 없는지 확인하세요.

**Anti-pattern**: 분류 없이 바로 파일을 수정하는 것. 해당 파일이 generator
output인지 확실하지 않으면, 수정 전후에 `dx-agentic-gen check`를 실행하세요
— check가 수정 내용을 덮어쓰면 해당 파일은 generator가 관리하는 파일이므로
`.deepx/` source를 통해 수정해야 합니다.

Pre-commit hook이 generator output 무결성을 강제합니다: 생성된 파일이
최신이 아니면 `git commit`이 실패합니다. Hook 설치:
```bash
tools/dx-agentic-dev-gen/scripts/install-hooks.sh
```

> **KO 대응 파일 규칙**: EN fragment를 편집할 때, KO 대응 파일도 업데이트가
> 필요한지 확인하세요. 단락 1개 이상을 추가하거나 제거했다면, 커밋 전에
> `.deepx/templates/fragments/ko/<stem>.md`를 업데이트하세요. `dx-agentic-gen lint`를
> 실행하여 `[OK]`를 확인하세요 — EN이 KO보다 10줄 이상 많으면 lint가 ERROR를
> 반환합니다.

이 게이트는 `.deepx/` 파일이 작업의 *주요 산출물*인 경우(규칙 추가, 플랫폼 sync,
KO 번역 생성, agents/skills 수정)에 적용됩니다. 기능 구현 중 `.deepx/`에 단순
한 줄 수정이 발생하는 경우에는 적용되지 않습니다.

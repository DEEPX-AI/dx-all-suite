# 3계층 Skill Architecture

> DEEPX All Suite의 skill 명명 및 invocation 시스템에 대한 설계 문서.

## 3계층 분리

Skill은 명명 규칙에 따라 세 계층으로 구성됩니다:

| Tier | Prefix | Scope | Example |
|------|--------|-------|---------|
| **General SWE** | `dx-swe-*` | 모든 개발 task (SDK, docs, 일반 coding) | `dx-swe-tdd` |
| **End-User (Agent-Driven Dev)** | `dx-agent-*` | dx-agent-dev 기능을 통해 app/pipeline 빌드 | `dx-agent-tdd` |
| **Harness Eng** | `dx-harness-*` | 내부 `.deepx/`, `tests/`, `tools/` 유지보수 | `dx-harness-validate` |
| **Meta** | `dx-skill-router` | 모든 tier에서 사용 | — |

### 설계 원칙

1. **`dx-agent-*`는 `dx-swe-*`를 참조한다** — agent-driven skill은 DEEPX 전용
   콘텐츠만 포함하며 "일반 SWE 프로세스는 `dx-swe-*`를 참조하라"고 명시합니다.

2. **`dx-swe-*`는 self-contained하다** — 일반 SWE skill은 DEEPX 전용 컨텍스트
   없이도 독립적으로 동작합니다. SDK source code 개발, 문서 작업, 또는 임의의
   일반 coding task에 사용할 수 있습니다.

3. **`dx-harness-*`는 내부 전용이다** — 이 skill들은 end-user task에서 호출되지
   않습니다. 내부 도구 (`validate_framework.py`, `feedback_collector.py`,
   `dx-agent-gen`) 를 사용합니다.

4. **Domain 전용 skill은 `dx-agent-{subproject}-*` 명명 규칙을 따른다** — 각
   sub-project의 build/validate/model skill은 명확한 namespace 분리를 위해
   해당 sub-project 식별자를 prefix로 가집니다.

## Skill 인벤토리

### Suite 레벨 (`.deepx/skills/`)

#### General SWE (`dx-swe-*`)

| Skill | Purpose |
|-------|---------|
| `dx-swe-brainstorm` | 협업 설계: ask → propose → approve → review |
| `dx-swe-tdd` | Red-Green-Verify cycle, unit test용 Classic TDD |
| `dx-swe-verify` | Gate Function: 완료 주장 전 evidence 요구 |
| `dx-swe-writing-plans` | bite-sized task로 구현 plan 작성 |
| `dx-swe-executing-plans` | review checkpoint를 두고 plan 실행 |
| `dx-swe-subagent-dev` | task별로 fresh subagent를 통해 plan 실행 |
| `dx-swe-parallel-agents` | 독립 task에 대해 parallel subagent 디스패치 |
| `dx-swe-debugging` | 체계적 4-phase 근본 원인 조사 |
| `dx-swe-receiving-review` | code review 피드백을 엄격히 평가 |
| `dx-swe-requesting-review` | 기능 완료 후 code review 요청 |

#### End-User (`dx-agent-*`)

| Skill | Purpose | References |
|-------|---------|------------|
| `dx-agent-brainstorm` | Sub-project routing, model registry, Pre-Flight check | `dx-swe-brainstorm` |
| `dx-agent-tdd` | dx_app, dx_stream, Integration에 대한 Validation Order | `dx-swe-tdd` |
| `dx-agent-verify` | dx_app, dx_stream, Cross-Project에 대한 Checklist | `dx-swe-verify` |

#### Harness Eng (`dx-harness-*`)

| Skill | Purpose |
|-------|---------|
| `dx-harness-validate` | `.deepx/` framework integrity validation |
| `dx-harness-writing-skills` | `.deepx/` skill 파일 생성/편집 |

#### Meta

| Skill | Purpose |
|-------|---------|
| `dx-skill-router` | Skill discovery 및 invocation routing |

### Sub-Project 레벨

Sub-project skill도 동일한 명명 규칙을 따릅니다. 주요 차이점:

- **`dx-agent-*`** sub-project 레벨은 project 전용 세부 사항을 포함합니다
  (예: dx_app의 `dx-agent-tdd`는 133-model validation 세부 사항을 가짐)
- **`dx-swe-*`** sub-project 레벨은 일반적으로 suite 레벨과 동일합니다
- **Domain 전용 skill**은 sub-project별로 고유합니다

### Domain 전용 Skill (Sub-Project별)

#### dx-compiler Domain Skills

| Skill | Purpose |
|-------|---------|
| `dx-agent-compiler-compile` | ONNX → DXNN compilation 단계별 workflow |
| `dx-agent-compiler-convert` | PyTorch → ONNX 변환 단계별 workflow |
| `dx-agent-compiler-validate` | compile된 .dxnn model 출력 validation |

#### dx-runtime Domain Skills

| Skill | Purpose |
|-------|---------|
| `dx-agent-runtime-validate` | Validate, feedback 수집, fix 적용, verify |

#### dx_app Domain Skills

| Skill | Purpose |
|-------|---------|
| `dx-agent-app-build-python` | Python inference app 빌드 (IFactory + SyncRunner) |
| `dx-agent-app-build-cpp` | C++ inference app 빌드 |
| `dx-agent-app-build-async` | async 고성능 app 빌드 (AsyncRunner) |
| `dx-agent-app-model-management` | Model 다운로드 및 설정 |
| `dx-agent-app-validate` | dx_app validation check 실행 |

#### dx_stream Domain Skills

| Skill | Purpose |
|-------|---------|
| `dx-agent-stream-build-pipeline` | GStreamer pipeline app 빌드 |
| `dx-agent-stream-build-mqtt-kafka` | MQTT/Kafka pipeline app 빌드 |
| `dx-agent-stream-model-management` | Model 다운로드 및 설정 |
| `dx-agent-stream-validate` | dx_stream validation check 실행 |

## 필수 Skill Sequence

### End-User Scenario

발동 조건: task가 `dx-agent-dev/<session_id>/`에 파일을 생성할 때

```
dx-skill-router
  → dx-agent-brainstorm    (sub-project로 routing, dx-swe-brainstorm 참조)
  → dx-swe-writing-plans
  → dx-agent-tdd           (dx-swe-tdd 참조)
  → dx-agent-{subproject}-* (domain build skill: compile, build-python 등)
  → dx-agent-verify        (dx-swe-verify 참조)
```

**강제 수단:** `mandatory-process-skill-sequence.md` fragment (path match:
`dx-agent-dev/<session_id>/`)

### SDK Development Scenario

발동 조건: task가 SDK source, docs, 또는 일반 code를 수정할 때 (`.deepx/`,
`tests/`, `tools/`, `dx-agent-dev/`는 제외)

```
dx-skill-router
  → dx-swe-brainstorm
  → dx-swe-writing-plans
  → dx-swe-tdd
  → dx-swe-verify
```

**강제 수단:** 특정 fragment 없음 — 일반 SWE best practice. agent가
`dx-skill-router` 가이드에 따라 skill을 호출합니다.

### Harness Development Scenario

발동 조건: task가 `.deepx/`, `tests/`, `tools/` 경로를 수정할 때

```
dx-skill-router
  → dx-swe-brainstorm
  → dx-swe-writing-plans
  → dx-swe-tdd
  → dx-swe-verify
  → dx-harness-validate      (+ validate_framework.py, dx-agent-gen check)
```

**강제 수단:** `swe-process-gates-internal-dev.md` fragment (path match:
`.deepx/`, `.deepx/tests/test_agent_*/`, `.deepx/tools/`)

## Scenario 분류

분류는 `dx-skill-router`가 수행하지 않습니다 — `AGENTS.md` / `CLAUDE.md`에 임베드된
instruction fragment의 **path matching**으로 결정됩니다:

| Fragment | Path Match | Scenario |
|----------|-----------|----------|
| `mandatory-process-skill-sequence.md` | `dx-agent-dev/<session_id>/` | End-User |
| `swe-process-gates-internal-dev.md` | `.deepx/`, `tests/`, `tools/` | Harness Dev |
| 어느 것도 매치되지 않음 | — | SDK Dev (General) |

## 참조 패턴

`dx-agent-*` skill은 `dx-swe-*`를 직접 참조합니다:

```markdown
# dx-agent-tdd

> 일반적인 Red-Green-Verify cycle은 `dx-swe-tdd`를 참조하세요.
> 이 skill은 DEEPX build 전용 validation order와 check를 추가합니다.

## Validation Order — dx_app
...
```

이렇게 하면 DEEPX 전용 콘텐츠는 한 곳에, 일반 SWE 프로세스는 다른 곳에 보관됩니다.
일반 프로세스가 진화할 때 `dx-swe-tdd`만 업데이트하면 됩니다.

## Harness 파일 레이아웃

모든 harness 개발 파일은 `.deepx/` 하위에 위치합니다:

```
.deepx/
  agents/           — agent 정의 (canonical source)
  docs/             — harness 설계 문서 (이 파일)
  memory/           — knowledge base
  skills/           — skill 정의 (canonical source)
  templates/        — generator template + fragment
  tests/            — suite conformance test
    conftest.py           — agent-driven marker 등록 + collect_ignore
    conformance/          — 정적 KB/생성물 정책 검사
  e2e/              — end-to-end 하니스 (분리됨)
    e2e_runner.py · e2e_monitor.py · test.sh   — 라운드 오케스트레이션 + 러너
    test_agent_e2e_scenarios/   — E2E agent 실행 test
    agent_analyzer/     — run-id 인지 결과 분석기
  tools/            — 툴링 패키지 + 개발 스크립트
    README.md                     — 툴링 가이드
    pyproject.toml                — 패키지 정의; src/ 두 패키지 자동 발견
    src/dx_agent_dev_gen/       — generator 패키지 (cli, generator, transformers, frontmatter, constants)
    src/dx_transcripts/           — 공유 세션 파서 + transcript 렌더러
    tests/                        — src/ 미러 (dx_agent_dev_gen/, dx_transcripts/)
    scripts/
      README.md                       — scripts/ 가이드
      run_all.sh                      — 멀티-repo generate/check/lint 래퍼
      install-hooks.sh                — pre-commit hook 설치
      pre-commit-hook.sh              — drift + lint guard (git이 호출)
      run-e2e-improvement-loop.sh     — E2E improvement loop runner
      README_RUN_E2E_IMPROVEMENT_LOOP.md
      README_RUN_E2E_IMPROVEMENT_LOOP-KO.md
```

Product test infrastructure는 `tests/`에 그대로 유지됩니다 (Docker, local install,
getting-started test). `dx-agent-dev/e2e-tests/`도 현재 위치에 유지됩니다
(test data 및 결과이며, harness source code가 아님).

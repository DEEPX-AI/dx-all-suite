# DEEPX Agent-Driven Development - dx-agent-dev (Beta) — `.deepx/` 구조 종합 안내

> 작성 기준: dx-all-suite, dx-runtime, dx_app, dx_stream, dx-compiler 5개 repo의 `.deepx/` 디렉토리 정적 분석
> 작성일: 2026-05-12 · 브랜치: `merge2.3.2/dx-agent-dev`

---

## 0. 한 줄 요약

DEEPX Agent-Driven Development (dx-agent-dev) 기능은 **`.deepx/`를 canonical source(SoT)** 로 두고, `dx-agent-dev-gen` 제너레이터가 Claude Code / Copilot / Cursor / OpenCode 4개 플랫폼용 파일을 자동 생성하는 **단일 출처 다중 출력(single-source / multi-target)** 아키텍처입니다. 5개 repo(suite, runtime, dx_app, dx_stream, compiler)는 같은 골격(agents/, skills/, memory/, templates/, instructions/, toolsets/)을 공유하면서 도메인별로 특화되어 있고, **HARD GATE / Skill Router / Session Sentinel / Output Isolation** 4가지 강제 규칙으로 자동 일관성을 보장합니다.

---

## 1. DEEPX Agent-Driven Development (dx-agent-dev) 기능 개요

### 1.1 핵심 컨셉

자연어 프롬프트로 DEEPX SDK 기반 AI 애플리케이션을 생성합니다. AI 에이전트가 다음을 이해합니다.

- **dx_app**: IFactory · SyncRunner · AsyncRunner 기반 standalone 추론 (Python/C++)
- **dx_stream**: 13개 GStreamer 엘리먼트 × 6개 파이프라인 카테고리
- **dx-compiler**: ONNX → DXNN 변환 (DX-COM, PPU 자동 감지)
- **cross-project**: 컴파일 + 앱 빌드 + 검증 연쇄

### 1.2 지원 AI 도구 (5종)

| 도구 | 자동 로드 메커니즘 | 에이전트 호출 |
|------|--------------------|---------------|
| **Claude Code** | `CLAUDE.md` + `.claude/agents/` | 자연어 + Context Routing Table |
| **GitHub Copilot** | `.github/copilot-instructions.md` + `.github/agents/` | `@agent-name "prompt"` |
| **Cursor** | `.cursor/rules/*.mdc` (`alwaysApply` / `globs`) | 자연어 |
| **OpenCode** | `AGENTS.md` + `opencode.json` + `.opencode/agents/` + 슬래시 명령 | `@agent-name` 또는 `/skill-name` |
| **Codex CLI** | `AGENTS.md` + `.codex/skills/dx-codex-identity/SKILL.md` | `codex exec --json -s danger-full-access -m <model> -C <workdir>` (기본: `gpt-5.3-codex`, Copilot provider 인증) |

### 1.3 계층 라우팅 구조

```
[dx-all-suite] dx-suite-builder (최상위 분류기)
       ├── [dx-compiler]   dx-compiler-builder → model-converter / dxnn-compiler
       └── [dx-runtime]    dx-runtime-builder
                              ├── [dx_app]    dx-app-builder → python/cpp/benchmark/model-manager/validator
                              └── [dx_stream] dx-stream-builder → pipeline-builder / model-manager / validator
```

### 1.4 Output Isolation 규칙 (HARD GATE)

모든 AI 생성 코드는 `dx-agent-dev/<session_id>/` 아래에 작성됩니다 (기본). 사용자가 명시적으로 `src/`에 쓰라고 지시한 경우만 예외입니다.

- 세션 ID 포맷: `YYYYMMDD-HHMMSS_<agent>_<coding_model>_<target_model>_<task>` (시스템 로컬 타임존, UTC 금지)
- `<agent>`: `claude` / `codex` / `copilot` / `cursor` / `opencode`
- `<coding_model>`: `sonnet46`, `opus46`, `gpt53codex`, `gpt55`
- Cross-project suite 작업은 **2개 세션 디렉토리** 생성 필수 (R41 규칙):
  - `dx-compiler/dx-agent-dev/<id>_compile/`
  - `dx-runtime/dx_app/dx-agent-dev/<id>_inference/`

### 1.5 Session Sentinels (자동 테스트용)

| 마커 | 출력 위치 |
|------|----------|
| `[DX-AGENT-DEV: START]` | 첫 응답의 **절대 첫 줄** |
| `[DX-AGENT-DEV: DONE (output-dir: <relative_path>)]` | 모든 작업·검증·파일 생성 완료 후 마지막 줄 |

---

## 2. `.deepx/` 공통 아키텍처

### 2.1 단일 출처 → 다중 플랫폼 생성

```
.deepx/ (canonical source)
   ├── agents/      ←┐
   ├── skills/      ←┤
   ├── templates/   ←┤  dx-agent-gen generate
   ├── fragments/   ←┘
                          ↓
   ┌──────────────────────┼──────────────────────┐
   ↓                      ↓                      ↓
CLAUDE.md          .github/copilot-       .cursor/rules/*.mdc
AGENTS.md          instructions.md        (Cursor)
.claude/agents/    .github/agents/        .opencode/agents/
```

`dx-agent-gen` 패키지(`.deepx/tools/`)가 변환을 담당하고, 사전 커밋 훅(`install-hooks.sh` → `pre-commit-hook.sh`)이 drift를 차단합니다.

### 2.2 디렉토리 카탈로그 (repo별 존재 여부)

| 디렉토리 | suite | runtime | dx_app | dx_stream | compiler | 역할 |
|----------|:-----:|:-------:|:------:|:---------:|:--------:|------|
| `agents/` | ✅ | ✅ | ✅ | ✅ | ✅ | 도메인 에이전트 정의 (.md) |
| `skills/` | ✅ | ✅ | ✅ | ✅ | ✅ | 슬래시 명령 / 절차 스킬 |
| `templates/en,ko` | ✅ | ✅ | ✅ | ✅ | ✅ | CLAUDE/AGENTS/copilot-instructions tmpl |
| `templates/fragments/` | ✅ (16×2) | — | — | — | — | 모든 레벨에 주입되는 공유 규칙 조각 |
| `memory/` | ✅ | ✅ | ✅ | ✅ | ✅ | 영구 지식 (pitfalls, model_zoo, …) |
| `instructions/` | — | ✅ | ✅ | ✅ | ✅ | 아키텍처·코딩 표준·프로토콜 |
| `knowledge/` | — | ✅ | ✅ | ✅ | — | YAML 형태 룰 / 모델 DB |
| `toolsets/` | — | — | ✅ | ✅ | ✅ | SDK API reference |
| `contextual-rules/` | — | — | ✅ | ✅ | — | glob 기반 규칙 강제 |
| `prompts/` | — | — | ✅ | ✅ | — | 에이전트 입력 템플릿 |
| `scripts/` | — | ✅ | ✅ | ✅ | ✅ | validate / feedback / generate |
| `docs/` | ✅ | — | — | — | — | 프레임워크 자체 가이드 (skill-architecture 등) |
| `tools/` | ✅ | — | — | — | — | 툴링 패키지: `src/{dx_agent_dev_gen, dx_transcripts}` + 미러 `tests/` + `scripts/` |
| `tests/` | ✅ | — | — | — | — | suite **conformance** 테스트 (`conformance/`) — KB / 생성물 정책 검사 |
| `e2e/` | ✅ | — | — | — | — | E2E 하니스: `e2e_runner`/`e2e_monitor`, `test_agent_e2e_scenarios/`, `agent_analyzer/`, `test.sh` |

---

## 3. dx-all-suite `.deepx/` (최상위 라우팅 + 제너레이터)

### 3.1 agents/ — 최상위 라우터 2종

| 에이전트 | 책임 | HARD GATE |
|---------|------|-----------|
| **`dx-suite-builder.md`** | 작업 분류 → dx-compiler / dx_app / dx_stream / cross-project 라우팅 | cross-project 단계 전환 시 재-brainstorm 필수 |
| **`dx-suite-validator.md`** | 3개 레벨(framework) 검증 오케스트레이션 | 5단계 워크플로우(validate → collect → apply → re-validate) |

### 3.2 docs/ — 프레임워크 자체 가이드

| 파일 | 내용 |
|------|------|
| `skill-architecture.md` (+ KO) | 3-계층 분리, mandatory skill sequence, end-user / SDK / harness 시나리오 분류 |
| `fragment-authoring-guide.md` (+ KO) | Fragment 4규칙: EN+KO 동시 생성, 구조적 마커 보존, lint 검증, 본문 한글 금지(예외 있음) |

### 3.3 memory/sdk_grounding_reference.md

API hallucination 방지용 grounding 문서. 검증된 심볼만 나열:
- `IFactory` 5-메서드, `SyncRunner`, `AsyncRunner`
- `dx_com.compile(...)` (`from dxcom import dxcom` 패턴 금지)
- 13개 GStreamer 엘리먼트
- 모든 instruction의 API 이름은 이 문서에서 교차 검증 필수

### 3.4 templates/fragments/ — 16개 공유 규칙 조각 (EN+KO 32개)

| Fragment | 역할 |
|----------|------|
| `mandatory-process-skill-sequence.md` | router → brainstorm → plan → tdd → verify 순서 강제 |
| `swe-process-gates-internal-dev.md` | 내부 dx-agent-dev 개발 시 SWE 규율 |
| `artifact-verification-gate.md` | 산출물 verification 체크리스트 |
| `session-sentinels.md` | START/DONE 마커 정의 |
| `rule-conflict-resolution.md` | 룰 충돌 시 우선순위 (user > skill > default) |
| `git-safety-superpowers.md` / `git-operations-user-handles.md` | docs/superpowers/ 커밋 금지, git 작업 위임 |
| `no-placeholder-code.md` / `experimental-features-prohibited.md` | TODO·실험 기능 금지 |
| `response-language.md` / `recommended-model.md` / `skill-router-mandatory.md` | 응답 언어 일치, Claude Sonnet 4.6+ 권장, 라우터 호출 강제 |
| `autopilot-mode-guard.md` | autopilot 모드 가드 ("no asking, but follow all rules") |
| `brainstorming-spec-before-plan.md` / `plan-output.md` / `instruction-verification-loop.md` | 절차 강제 |

이 16개 fragment는 5개 repo의 `CLAUDE.md` / `AGENTS.md` / `copilot-instructions.md`에 **선택적으로 주입**되어 일관된 규칙 베이스를 만듭니다.

### 3.5 skills/ — 14개 공통 스킬

| 카테고리 | 스킬 | 한 줄 설명 |
|----------|------|-----------|
| **SWE 프로세스** | `dx-swe-brainstorm` | 코드 작성 전 2-3 접근법 + 스펙 자체 리뷰 + 사용자 승인 게이트 |
| | `dx-swe-tdd` | Red-Green-Verify, 파일 생성 직후 즉시 검증 |
| | `dx-swe-verify` | 완료 주장 전 fresh evidence 필수 |
| | `dx-swe-debugging` | Phase 1 root cause 분석 없이 fix 금지 |
| | `dx-swe-writing-plans` / `dx-swe-executing-plans` / `dx-swe-subagent-dev` / `dx-swe-parallel-agents` | 플랜 작성/실행/병렬 디스패치 |
| | `dx-swe-receiving-review` / `dx-swe-requesting-review` | 리뷰 수신/요청 |
| **DEEPX 도메인** | `dx-agent-brainstorm` / `dx-agent-tdd` / `dx-agent-verify` | DEEPX 특화 (모델 레지스트리 체크 등) |
| **하네스** | `dx-harness-validate` / `dx-harness-writing-skills` | `.deepx/` 자체 무결성 검증 / 스킬 생성 |
| **메타** | `dx-skill-router` | "1% 확률이라도 적용 가능하면 invoke" 규칙 |

### 3.6 tools/ — 툴링 패키지 + 제너레이터

`tools/src/`에 import 가능한 패키지 2개, 각각 `tools/tests/`에 미러:

| 패키지 (`tools/src/`) | 테스트 (`tools/tests/`) | 역할 |
|----------------------|-------------------------|------|
| `dx_agent_dev_gen` | `dx_agent_dev_gen/` | `dx-agent-gen` 제너레이터 (cli, generator, transformers, frontmatter, constants) |
| `dx_transcripts` | `dx_transcripts/` | 공유 세션 파서 + transcript 렌더러 (`parse_*_session`, `session_common`, `generate_transcripts`, `backfill_claude_html`) — session-sentinel DONE-라인 생성, e2e 하니스, analyzer가 공유 |

| 컴포넌트 | 역할 |
|----------|------|
| `pyproject.toml` | `dx-agent-gen` CLI (Python 3.10+); `packages.find where=["src"]`가 두 패키지 자동 발견 |
| `scripts/run_all.sh generate\|check\|lint\|prune` | 5개 repo 일괄 작업 |
| `scripts/install-hooks.sh` / `pre-commit-hook.sh` | pre-commit 훅: `.deepx/`↔비-`.deepx/` 혼재 경고 + drift check + EN/KO lint |

### 3.7 tests/ — suite conformance

- `conformance/`: CLI/NPU 불필요한 빠른 정적 검사 ~700개 — 가이드 구조, 라우팅 일관성, 시나리오 참조, cross-project handoff, instruction sync, sdk grounding, forbidden patterns. 정확한 수치는 `pytest .deepx/tests/conformance/ --collect-only -q`.

### 3.8 e2e/ — End-to-End 하니스 (분리됨)

- `e2e_runner.py` / `e2e_monitor.py` / `migrate_results_to_run_id.py` / `_cli_env.py` / `test.sh` — 라운드 오케스트레이션·모니터링·결과 이주·공유 러너.
- `test_agent_e2e_scenarios/`: 5개 CLI autopilot 마커(copilot, cursor, opencode, claude-code, codex)로 ~586 collected — 실제 CLI 호출 → 정적 검증. 추가로 인터랙티브 manual 모드(shell).
- `agent_analyzer/`: run-id 인지 결과 분석기 (리포트/인사이트; 자체 `lib/` + `tests/`).

---

## 4. dx-runtime `.deepx/` (통합 라우팅 + 통합 검증)

### 4.1 agents/

| 에이전트 | 역할 | 라우팅 결정 |
|----------|------|------------|
| **`dx-runtime-builder.md`** | dx_app vs dx_stream 분류기 | Python/C++ + IFactory → dx_app, GStreamer + RTSP + DxInfer → dx_stream |
| **`dx-validator.md`** | 3-레벨 통합 검증 + 피드백 루프 | 5단계: framework 검증 → feedback 수집 → 승인 → apply → 재검증 |

**HARD GATE 3종**:
1. `sanity_check.sh --dx_rt` 통과 (출력 텍스트 기준, exit code 무시)
2. Brainstorm 3-질문 (앱 타입 / AI 작업 / 입력 소스)
3. Skill router invoke

### 4.2 memory/common_pitfalls.md (25 항목, 16KB)

도메인 태그 5종 (`[UNIVERSAL]`, `[DX_APP]`, `[DX_STREAM]`, `[PPU]`, `[INTEGRATION]`)으로 분류된 함정 모음:
- 모델명 대소문자 / preprocess-id 매칭 / 비동기 frame_id 미사용 / RTSP DxRate 누락 / PPU 후처리기 / OBB nms_threshold 무시 / DxMsgConv 위치 / 헤드리스 DISPLAY 체크 / Python import 분리

### 4.3 instructions/

| 파일 | 내용 |
|------|------|
| `agent-protocols.md` | Cross-project consistency / Sub-agent routing / Memory feedback 3 프로토콜 |
| `integration.md` | 모델 경로 해석 차이 (dx_app: model_registry.json, dx_stream: model_list.json), 빌드 순서 (`dx_rt → dx_app → dx_stream`), Python import 분리 |

### 4.4 knowledge/feedback_rules.yaml

검증 패턴(정규식) → `.deepx/` 파일 업데이트 매핑. 8개 액션 타입:
`append_pitfall`, `append_rule`, `fix_reference`, `add_domain_tag`, `update_skill`, …

### 4.5 scripts/ — 5개 Python 도구

| 스크립트 | 역할 |
|----------|------|
| `validate_framework.py` | `.deepx/` 구조 / cross-reference / 라우팅 테이블 검증 |
| `validate_app.py` | 앱 코드 패턴 검증 (IFactory, parse_common_args, 상대 import) |
| `feedback_collector.py` | 검증 결과 정규화 → `feedback_rules.yaml` 매칭 → JSON 제안 |
| `apply_feedback.py` | 승인된 제안을 `.deepx/`에 적용 (dry-run 지원) |

### 4.6 skills/

12개 (suite와 동일한 swe-* 8개 + agent-driven-* 3개 + dx-skill-router + 고유 `dx-agent-runtime-validate`)

---

## 5. dx_app `.deepx/` (standalone 추론 — IFactory)

### 5.1 agents/ (6개)

| 에이전트 | 책임 |
|----------|------|
| **`dx-app-builder`** | 마스터 라우터 — 3가지 필수 질문 (언어/작업/모델) 수집 후 전문가에 위임 |
| **`dx-python-builder`** | 4 변형 (sync / async / cpp_postprocess / async_cpp_postprocess) 생성 |
| **`dx-cpp-builder`** | C++ 앱 + CMakeLists.txt + SIGINT 핸들러 / RAII / C++14 |
| **`dx-benchmark-builder`** | `--verbose --loop 3` 실행, 7-필드 메트릭 분석 |
| **`dx-model-manager`** | `config/model_registry.json` 쿼리, 다운로드, 호환성 검증 |
| **`dx-validator`** | 5단계 검증 피라미드 (static → config → component → smoke → accuracy) |

### 5.2 skills/ (도메인 4 + 프로세스 4 + 공통)

| 도메인 스킬 | 핵심 |
|------------|------|
| `dx-agent-app-build-python` | Python 변형, IFactory 5-메서드 |
| `dx-agent-app-build-cpp` | C++ + CMakeLists.txt |
| `dx-agent-app-build-async` | AsyncRunner 프레임 중첩 |
| `dx-agent-app-model-management` | model_registry.json 쿼리/다운로드 |
| `dx-agent-app-validate` | 5단계 검증 |

### 5.3 memory/ (5 파일)

| 파일 | 내용 |
|------|------|
| `MEMORY.md` | 인덱스 + 업데이트 프로토콜 + 도메인 태그 |
| `common_pitfalls.md` (32KB) | 10개 핵심 함정 (`[UNIVERSAL]`, `[DX_APP]`, `[PPU]`) |
| `model_zoo.md` | 133개 모델 (object_detection 50, classification 15, instance_seg 8, pose 6, face 8 …) — 정확한 수는 `model_registry.json`에서 jq 쿼리 |
| `platform_api.md` | DX-M1 NPU, DX-RT 3.0.x, 콜드부트 요구사항, `DXRT_DYNAMIC_CPU_THREAD=ON` |
| `performance_patterns.md` | 7-필드 메트릭 (read/preprocess/inference/postprocess/render/save/display) + 최적화 기법 |

### 5.4 instructions/ (6 파일)

| 파일 | 내용 |
|------|------|
| `architecture.md` | 3-layer 아키텍처 (앱 → framework → C++ core), 37개 postprocess 바인딩 |
| `factory-pattern.md` | IFactory 5-메서드, `_FactoryConfigMixin.load_config(dict)` 메커니즘 |
| `coding-standards.md` | Python `sys.path` 2-parent 패턴, logging, C++14 RAII |
| `agent-protocols.md` | 라우팅 형식, handoff 메시지 |
| `orchestration.md` | 다중 에이전트 TDD 순서, artifact 생성 순서 |
| `testing-patterns.md` | pytest, `DXAPP_VERIFY`, NPU skip, smoke 테스트, 모킹 |

### 5.5 toolsets/ (5 파일, SDK API reference)

| 파일 | API 범위 |
|------|----------|
| `common-framework-api.md` (~1200L) | `SyncRunner`, `AsyncRunner`, `parse_common_args` (11 플래그), IFactory 11 인터페이스 |
| `dx-engine-api.md` (~200L) | `InferenceEngine` (run, run_async, wait, 텐서 정보), `InferenceOption` |
| `dx-postprocess-api.md` (~600L) | 37개 pybind11 바인딩 (Det 11 / Cls 4 / Seg 4 / Pose 2 / Face 3 / PPU 5 / 기타) |
| `model-registry.md` | `model_registry.json` 스키마 + 쿼리 패턴 |
| `dx-model-format.md` | `.dxnn` 텐서 스펙, INT8/UINT8/FP16, 컴파일 흐름 |

### 5.6 contextual-rules/ vs prompts/

| 카테고리 | contextual-rules/ | prompts/ |
|----------|-------------------|----------|
| 목적 | **규칙 강제** (glob 기반) | **에이전트 입력 템플릿** (변수 채우기) |
| 파일 | `python-example.md`, `cpp-example.md`, `postprocess.md`, `tests.md` | `new-python-detection.md`, `new-python-segmentation.md`, `new-cpp-app.md`, `orchestrated-build.md` |
| 예시 | "모든 Python 앱은 `parse_common_args()` 필수" | "Build a `{model_name}` `{variant}` app with `{input_source}`" |

### 5.7 필수 산출물 14종 (모든 세션)

`config.json`, `session.json`, `README.md`, `setup.sh`, `run.sh`, `session.log` (공통 6) + `factory/<model>_factory.py`, `factory/__init__.py`, `<model>_sync.py` (Python 필수 3) + async/cpp_postprocess 변형 옵션 + C++ 변형 옵션.

### 5.8 HARD GATE 요약

1. **skeleton-first**: `src/python_example/<task>/<model>/` 복사 → 모델별 부분만 수정
2. **IFactory 5-메서드**: `create_preprocessor / create_postprocessor / create_visualizer / get_model_name / get_task_type`
3. **SyncRunner / AsyncRunner 전용**: 직접 `InferenceEngine` 호출 금지
4. **`model_registry.json` 쿼리 필수**: 모델명 위조 금지
5. **Output Isolation**: `dx-agent-dev/<session_id>/` 외 작성 금지
6. **PPU 자동 감지**: `_ppu` suffix → `src/python_example/ppu/` 경로 사용
7. **self-contained & portable**: `setup.sh`가 `common` → `./common` vendoring + `<model>_sync.py` walker가 vendored `./common` 우선(`PYTHONPATH` 불필요) → suite 밖으로 복사해도 동작, out-of-suite 검증(`dx_engine`만 외부 의존)

---

## 6. dx_stream `.deepx/` (GStreamer 파이프라인)

### 6.1 agents/ (4개)

| 에이전트 | 역할 |
|----------|------|
| **`dx-stream-builder`** | 마스터 라우터 — Phase 0~6 (사전조건 → 이해 → 컨텍스트 로드 → 빌드 → 정리 → 검증 → 리포트) |
| **`dx-pipeline-builder`** | GStreamer 파이프라인 직접 작성 + Python/Shell 스크립트 + 3단계 검증 |
| **`dx-model-manager`** | `model_list.json` 쿼리, 다운로드, PPU/비-PPU 호환성 검증 |
| **`dx-validator`** | preprocess-id/inference-id 매칭, 큐 배치, 모델·라이브러리 경로 존재성, 엘리먼트 등록 검사 |

### 6.2 13개 GStreamer 엘리먼트 (toolsets/`dx-stream-elements.md`)

| # | 엘리먼트 | 역할 |
|---|----------|------|
| 1 | `DxPreprocess` | resize / normalize / letterbox / 2차 ROI |
| 2 | `DxInfer` | NPU `.dxnn` 실행 |
| 3 | `DxPostprocess` | 텐서 → 객체 메타데이터 (`libpostprocess_*.so`) |
| 4 | `DxTracker` | OC-SORT 다중 객체 추적 |
| 5 | `DxOsd` | 박스/라벨/신뢰도 OSD |
| 6 | `DxRate` | 프레임율 제어 (RTSP 버퍼 방지) |
| 7 | `DxScale` | 프레임 크기 조정 |
| 8 | `DxConvert` | 색상 변환 |
| 9 | `DxGather` | N:1 멀티플렉싱 (cascaded) |
| 10 | `DxInputSelector` | N:1 라운드-로빈 |
| 11 | `DxOutputSelector` | 1:N 디멀티플렉싱 |
| 12 | `DxTile` | 고해상도 입력 분할 |
| 13 | `DxDeTile` | 타일 결과 재조립 |

추가 메시징 엘리먼트(`architecture.md`): `DxMsgConv`, `DxMsgBroker`.

### 6.3 6개 파이프라인 카테고리

| 카테고리 | 핵심 체인 | 도메인 스킬 |
|----------|----------|------------|
| Single-model | `src ! DxPreprocess ! queue ! DxInfer ! queue ! DxPostprocess ! queue ! DxOsd ! sink` | `build-pipeline` |
| Multi-stream | N × (preprocess→infer→postprocess→osd→DxScale) ! compositor ! sink | `build-pipeline` |
| Tracking | `... ! DxPostprocess ! queue ! DxTracker ! queue ! DxOsd ! ...` | `build-pipeline` |
| Cascaded (Secondary) | `... ! primary ! tee ! t. ! sec_A ! gather.sink_0  t. ! sec_B ! gather.sink_1  DxGather ! ...` | `build-pipeline` |
| RTSP | `urisourcebin ! decodebin ! DxRate ! DxInputSelector ! ...` | `build-pipeline` |
| Broker | `... ! DxPostprocess ! queue ! DxMsgConv ! queue ! DxMsgBroker` | `build-mqtt-kafka` |

### 6.4 skills/ (도메인 4 + 공통)

| 도메인 스킬 | 핵심 차이 |
|------------|----------|
| `dx-agent-stream-build-pipeline` | 파이프라인 **구성** (엘리먼트 + 순서) |
| `dx-agent-stream-build-mqtt-kafka` | 파이프라인 **메시징** (결과 외부 전송) |
| `dx-agent-stream-model-management` | 모델 **레지스트리** (`model_list.json`) |
| `dx-agent-stream-validate` | 검증 **체계** (validate_app / validate_framework) |

### 6.5 memory/ (4 파일)

| 파일 | 내용 |
|------|------|
| `MEMORY.md` | 인덱스 + 업데이트 프로토콜 |
| `common_pitfalls.md` | 14개 도메인-태그 함정 |
| `pipeline_optimization.md` | 처리량/지연시간 튜닝 |
| `platform_api.md` | DX-RT 플랫폼 감지 / 버전 체크 |

### 6.6 instructions/ (6 파일)

`architecture.md`, `agent-protocols.md`, `coding-standards.md`, **`gstreamer-pipeline.md`** (13개 엘리먼트 상세, 각 15-25줄), `orchestration.md`, `testing-patterns.md`

### 6.7 toolsets/ (4 파일)

| 파일 | 범위 |
|------|------|
| `dx-stream-elements.md` | 13개 엘리먼트 모두 (부동산 / Pad / 예제 / 함정) |
| `dx-stream-metadata.md` | `pydxs` Python 바인딩 (`DXFrameMeta`, `DXObjectMeta`, `DXTensorMeta`) |
| `dx-engine-api.md` | dx_app과 공통 |
| `model-registry.md` | v2.3.0 / 14개 모델 / task ↔ postprocess `.so` 매핑 |

### 6.8 핵심 HARD GATE 11종

1. 사전조건 (`sanity_check.sh --dx_rt`, `gst-inspect-1.0 dxinfer`)
2. 기존 파이프라인 검색 (`dx_stream/pipelines/`)
3. 8개 mandatory artifact 생성
4. `x264enc tune=zerolatency` (없으면 데드락)
5. preprocess-id / inference-id 매칭
6. Queue 배치 (preprocess ↔ infer ↔ postprocess ↔ tracker)
7. DxTracker는 DxPostprocess 다음 (DxInfer 직후 금지)
8. DxMsgConv → DxMsgBroker 순서
9. RTSP에서 DxRate 필수
10. 절대 경로 (`/usr/local/share/gstdxstream/lib/...`)
11. PPU 모델 자동 감지 (`_ppu` suffix → DxPostprocess 생략)

---

## 7. dx-compiler `.deepx/` (참고: ONNX → DXNN)

> 사용자가 명시한 4개 repo 외이지만, dx-agent-dev cross-project 시나리오에서 핵심 역할이므로 요약 포함.

### 7.1 agents/ (3개)

| 에이전트 | 역할 |
|----------|------|
| `dx-compiler-builder.md` | converter / dxnn-compiler 라우팅 |
| `dx-dxnn-compiler.md` (48KB) | ONNX → DXNN (DX-COM, PPU 자동 감지, 칼리브레이션) |
| `dx-model-converter.md` | PyTorch → ONNX |

### 7.2 핵심 규칙

- `import dx_com; dx_com.compile(...)` (NOT `from dxcom import dxcom`)
- `compiler.properties` 수정 금지 (시스템 파일)
- Cross-project 시 `SUITE_ROOT` 자동 감지 패턴 사용 (`../../` 하드코드 금지)
- 백그라운드 컴파일 + parallel artifact 생성 (sleep-poll 금지)
- Pre-DONE `.dxnn` 존재 체크 (R-X4 게이트)

### 7.3 toolsets/

`dxcom-cli.md`, `dxcom-api.md`, `config-schema.md` — API hallucination 방지를 위해 fabrication 시 반드시 참조.

---

## 8. 핵심 워크플로우 5단계 (모든 코드 생성 세션)

```
1. /dx-skill-router          ← Universal Pre-Flight (HARD GATE, 매 사용자 메시지)
2. /dx-agent-brainstorm    ← 요구사항 + 2-3 접근법 + 사용자 승인
3. /dx-swe-writing-plans     ← 구조화된 plan
4. /dx-agent-tdd           ← Red(criteria) → Green(generate) → Verify(즉시)
5. /dx-agent-verify        ← 최종 evidence (실행 출력, 의식적 단언 금지)
```

**자율 모드(autopilot, `--yolo`)에서도 모든 단계 적용**. 차이는 `ask_user`를 knowledge base default로 대체할 뿐.

---

## 9. 검증 인프라 (`.deepx/tests/`)

### 9.1 Conformance (~700 tests, ~1초)

| 모듈 | 검증 항목 |
|------|----------|
| `test_guide_structure.py` | 가이드 문서 헤딩, 시나리오 번호, EN/KO 동기화 |
| `test_routing_consistency.py` | CLAUDE.md, AGENTS.md, copilot-instructions.md, .cursorrules 라우팅 일관성 |
| `test_scenario_references.py` | 에이전트/스킬 참조와 실제 인프라 매칭 |
| `test_cross_project_scenarios.py` | handoff 체인, validation 스크립트, output isolation |

### 9.2 E2E 시나리오 (~586 pytest + manual)

| 도구 | autopilot 플래그 | 자동승인 / 질문 차단 | 세션 export |
|------|------------------|---------------------|------------|
| Copilot CLI | `--yolo --no-ask-user -s` | `--yolo` / `--no-ask-user` | `--share=<file>` (HTML via `/share html`) |
| Cursor CLI (`agent`) | `-p --force --output-format stream-json` | `--force` / 프롬프트 지시 | stream-json stdout |
| OpenCode | `run --format json` | `run` 모드 자동 / 프롬프트 지시 | `/export` → `session-*.md` |
| Claude Code (`claude`) | `-p --dangerously-skip-permissions --output-format stream-json` | `--dangerously-skip-permissions` / 프롬프트 지시 | `/export` → `*.txt` |
| Codex CLI (`codex`) | `exec --json -s danger-full-access -m <model>` | `-s danger-full-access` / 프롬프트 지시 | `~/.codex/sessions/YYYY/MM/DD/rollout-*-<thread_id>.jsonl` |

5개 시나리오 × 5개 도구 = 25 시나리오. 검증은 **정적 분석만**(file existence, AST, JSON, 패턴) — 실제 HW 추론은 수행하지 않음.

---

## 10. 한눈에 보는 5-repo 비교표

| 측면 | dx-all-suite | dx-runtime | dx_app | dx_stream | dx-compiler |
|------|--------------|-----------|--------|-----------|-------------|
| **에이전트 수** | 2 | 2 | 6 | 4 | 3 |
| **도메인 스킬 수** | 0 (메타만) | 1 | 5 | 4 | 3 |
| **메모리 파일 수** | 1 | 1 | 5 | 4 | 2 |
| **toolsets/** | — | — | 5 | 4 | 3 |
| **instructions/** | — | 2 | 6 | 6 | 2 |
| **knowledge/** | — | feedback_rules.yaml | knowledge_base.yaml | knowledge_base.yaml | — |
| **scripts/** | tools/ 제너레이터 | 5 | 3 | 3 | 1 |
| **contextual-rules/** | — | — | 4 | 3 | — |
| **prompts/** | — | — | 4 | 3 | — |
| **고유 책임** | 라우팅 + 제너레이터 + 테스트 | 통합 검증 + 라우팅 | IFactory 추론 앱 | GStreamer 파이프라인 | ONNX → DXNN |

---

## 11. 결론 및 인상

1. **단일 출처(SoT) 설계가 견고**: `.deepx/` → `dx-agent-gen` → 4개 플랫폼. drift는 pre-commit 훅이 차단.
2. **HARD GATE 다층 강제**: skill router(메타) → 프로세스 시퀀스 → 도메인 규칙(IFactory, preprocess-id 등) → 산출물 검증. 무성한 실패(silent failure) 방지에 집중.
3. **테스트 자동화 폭이 넓다**: ~700 conformance + ~586 E2E + 5개 도구 cross-validation. 자율 모드(`--yolo`)에서도 동일 규칙 강제.
4. **모듈별 자율성 + 공통 백본**: 각 sub-project가 자체 `.deepx/`를 보유해 독립 작업 가능하나, 16개 fragment + skill router + Output Isolation 규칙으로 일관성 유지.
5. **확장 지점**: 새 도메인 추가 시 ① `.deepx/agents/` ② `.deepx/skills/` ③ `.deepx/memory/common_pitfalls.md` ④ `.deepx/toolsets/` ⑤ `instructions/` 5가지를 작성하면 자동으로 4개 플랫폼에 반영.

---

## 부록 A. 주요 명령어 치트시트

```bash
# 제너레이터 (canonical → platforms)
pip install -e .deepx/tools
dx-agent-gen generate                                 # 단일 repo
dx-agent-gen check                                    # drift 검사
bash .deepx/tools/scripts/run_all.sh generate           # 5개 repo 일괄
bash .deepx/tools/scripts/run_all.sh check
bash .deepx/tools/scripts/install-hooks.sh              # 1회 훅 설치

# 검증
python dx-runtime/.deepx/scripts/validate_framework.py
python dx-runtime/dx_app/.deepx/scripts/validate_framework.py
python dx-runtime/dx_stream/.deepx/scripts/validate_framework.py
python dx-compiler/.deepx/scripts/validate_framework.py
python dx-runtime/.deepx/scripts/feedback_collector.py --framework-only

# 테스트
cd .deepx/e2e
./test.sh agent-driven                                       # ~700 conformance tests
./test.sh agent-driven-e2e-claude-code-autopilot             # Claude Code E2E
./test.sh agent-driven-e2e-copilot-cli-autopilot
./test.sh agent-driven-e2e-cursor-cli-autopilot
./test.sh agent-driven-e2e-opencode-cli-autopilot
./test.sh agent-driven-e2e-codex-cli-autopilot               # Codex CLI E2E
```

## 부록 B. 환경 변수 (E2E 테스트)

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `DX_AGENT_E2E_MODEL` | `claude-sonnet-4.6` | Copilot CLI 모델 |
| `DX_AGENT_E2E_TIMEOUT` | `300` | Copilot CLI 타임아웃 |
| `DX_AGENT_E2E_CURSOR_MODEL` | `claude-4.6-sonnet-medium` | Cursor CLI 모델 |
| `DX_AGENT_E2E_OPENCODE_MODEL` | `github-copilot/claude-sonnet-4.6` | OpenCode 모델 |
| `DX_AGENT_E2E_CLAUDE_CODE_MODEL` | `claude-sonnet-4-6` | Claude Code 모델 |
| `DX_AGENT_E2E_CODEX_MODEL` | `gpt-5.3-codex` | Codex CLI 모델 |
| `DX_AGENT_E2E_CODEX_TIMEOUT` | `600` | Codex CLI 타임아웃 (초) |
| `DX_AGENT_E2E_CLEANUP_ARTIFACTS` | (unset) | 1 = 성공 후 산출물 삭제 |

---

*리포트 끝.*

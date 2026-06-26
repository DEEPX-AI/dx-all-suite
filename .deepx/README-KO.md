# `.deepx/` — DEEPX All Suite Agent-Driven Knowledge (최상위 레벨)

> dx-all-suite 최상위 레벨의 DEEPX Agent-Driven Development (`dx-agent-dev`)
> canonical source에 대한 마스터 인덱스.
>
> 최종 사용자 사용법은 [`docs/source/00_Agent_Driven_Development.md`](../docs/source/00_Agent_Driven_Development.md)를 참조.
> 5개 repo 전반의 모든 `.deepx/` 디렉토리에 대한 포괄적인 워크스루는
> [`docs/dx-agent-dev-overview.md`](docs/dx-agent-dev-overview.md)를 참조.

---

## 1. 목적

`.deepx/` 디렉토리는 DEEPX Agent-Driven Development를 구동하는 모든 것의
**canonical source of truth (SoT)** 입니다:

- 에이전트 정의 (router agents, builder agents, validators)
- Skill 워크플로우 (build, validate, brainstorm, TDD 등)
- 명령어 템플릿 (`CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md`)
- 모든 플랫폼 출력에 주입되는 공유 fragment (4개 tool × 5개 repo)
- Memory (pitfalls, knowledge base 항목)
- Tests (~700개 conformance + ~586개 E2E)
- `.deepx/` 콘텐츠를 모든 플랫폼으로 fan-out하는 `dx-agent-gen` generator

> **Generator 출력을 직접 수정하지 마세요.** `CLAUDE.md`, `AGENTS.md`,
> `.claude/agents/`, `.github/agents/`, `.opencode/agents/`, `.cursor/rules/`
> 같은 파일은 `.deepx/`로부터 생성됩니다. `.deepx/` 하위의 해당 source를 수정한 뒤,
> `dx-agent-gen generate`를 실행하세요.

---

## 2. 5-Repo 레이아웃

dx-all-suite는 5개의 repo를 포함하며, 각각 자체 `.deepx/`를 가집니다:

| Level | Path | Role | Sub-README |
|-------|------|------|------------|
| **Suite (this)** | `.deepx/` | 최상위 레벨 라우팅 + generator + tests | (this file) |
| **dx-runtime** | `dx-runtime/.deepx/` | 통합 레이어 (cross-project routing/validation) | [`dx-runtime/.deepx/README.md`](../dx-runtime/.deepx/README.md) |
| **dx_app** | `dx-runtime/dx_app/.deepx/` | 단독 inference 앱 (Python/C++) | [`dx-runtime/dx_app/.deepx/README.md`](../dx-runtime/dx_app/.deepx/README.md) |
| **dx_stream** | `dx-runtime/dx_stream/.deepx/` | GStreamer 파이프라인 | [`dx-runtime/dx_stream/.deepx/README.md`](../dx-runtime/dx_stream/.deepx/README.md) |
| **dx-compiler** | `dx-compiler/.deepx/` | ONNX → DXNN compilation | [`dx-compiler/.deepx/README.md`](../dx-compiler/.deepx/README.md) |

각 sub-project `.deepx/`는 자체 완결적입니다. 이 최상위 레벨 `.deepx/`는 다음을 추가합니다:
- Suite 전역 router agents (`dx-suite-builder`, `dx-suite-validator`)
- 5개의 모든 repo에 주입되는 16개의 공유 fragment (rename gates, session sentinels,
  process gates, autopilot guard 등)
- `dx-agent-gen` generator (5개의 모든 repo를 처리하는 단일 도구)
- 모든 agent-driven 테스트 인프라 (`tests/` conformance + `e2e/`)

---

## 3. 디렉토리 구조

```
.deepx/
├── README.md                    ← This file (top-level master index)
├── README-KO.md                 ← Korean translation
│
├── agents/                      ← Suite-level routing agents (2)
│   ├── dx-suite-builder.md      ← Top-level task classifier → sub-projects
│   └── dx-suite-validator.md    ← Cross-level framework validator
│
├── skills/                      ← Reusable skill workflows (14)
│   ├── dx-skill-router/         ← Meta — universal pre-flight
│   ├── dx-swe-*/                ← General SWE process (10: brainstorm/tdd/verify/…)
│   ├── dx-agent-*/            ← DEEPX-specific (3: brainstorm/tdd/verify)
│   └── dx-harness-*/            ← Internal harness dev (2: validate/writing-skills)
│
├── templates/                   ← Generator templates
│   ├── en/                      ← English instruction templates
│   │   ├── CLAUDE.md.tmpl
│   │   ├── AGENTS.md.tmpl
│   │   └── copilot-instructions.md.tmpl
│   ├── ko/                      ← Korean instruction templates
│   │   ├── CLAUDE-KO.md.tmpl
│   │   ├── AGENTS-KO.md.tmpl
│   │   └── copilot-instructions-KO.md.tmpl
│   └── fragments/               ← 32 shared fragments (16 EN + 16 KO)
│       ├── en/
│       └── ko/
│
├── memory/                      ← Persistent knowledge
│   └── sdk_grounding_reference.md   ← Anti-hallucination grounding facts
│
├── docs/                        ← Harness design docs (not auto-loaded)
│   ├── skill-architecture.md             ← 3-tier skill model
│   ├── fragment-authoring-guide.md       ← Rules for writing fragments
│   └── dx-agent-dev-overview.md        ← Comprehensive .deepx/ walk-through
│
├── tests/                       ← suite conformance 테스트
│   ├── README.md                ← 테스트 범주 및 실행법
│   └── conformance/             ← ~700 정적 KB/생성물 정책 검사 (CLI/NPU 불필요)
│
├── e2e/                         ← End-to-end 하니스 (분리됨)
│   ├── e2e_runner.py · e2e_monitor.py · test.sh   ← 라운드 오케스트레이션 + 러너
│   ├── test_agent_e2e_scenarios/  ← ~586 E2E 테스트 (5 CLI × 시나리오)
│   └── agent_analyzer/        ← E2E 결과 분석기 (리포트, 인사이트)
│
└── tools/                       ← 툴링 패키지 + 오케스트레이션 스크립트
    ├── README.md                ← 툴링 가이드
    ├── pyproject.toml           ← `dx-agent-gen` CLI; src/ 두 패키지 자동 발견
    ├── src/
    │   ├── dx_agent_dev_gen/  ← 제너레이터 (cli, generator, transformers, frontmatter, constants)
    │   └── dx_transcripts/      ← 공유 세션 파서 + transcript 렌더러
    ├── tests/                   ← src/ 미러 (dx_agent_dev_gen/, dx_transcripts/)
    └── scripts/
        ├── README.md                          ← scripts/ guide
        ├── run_all.sh                         ← Multi-repo generate/check/lint
        ├── install-hooks.sh                   ← Pre-commit hook installer
        ├── pre-commit-hook.sh                 ← Drift + lint check on commit
        ├── run-e2e-improvement-loop.sh        ← Self-improving E2E loop
        ├── README_RUN_E2E_IMPROVEMENT_LOOP.md
        └── README_RUN_E2E_IMPROVEMENT_LOOP-KO.md
```

---

## 4. Canonical → Multi-Target 생성 흐름

```
                    .deepx/  (canonical source)
                       │
                       │  dx-agent-gen generate
                       ▼
   ┌────────────────────────────────────────────────────────────┐
   │                                                            │
   ▼                ▼                ▼                ▼          ▼
CLAUDE.md     .github/         .claude/         .opencode/   .cursor/
AGENTS.md     copilot-         agents/          agents/      rules/
CLAUDE-KO.md  instructions.md  skills/          (config)     *.mdc
AGENTS-KO.md  agents/                                        skills
copilot-      skills/
instructions  instructions/
.md           (KO variants)
```

Generator는:
1. `.deepx/`로부터 agent/skill `.md` 파일을 읽음
2. `.deepx/templates/{en,ko}/`로부터 명령어 템플릿을 로드
3. `{{FRAGMENT:<name>}}` placeholder를 `.deepx/templates/fragments/`에 대해 resolve
4. 4개의 플랫폼별 출력 (Copilot, Claude Code, OpenCode, Cursor)을 생성
5. `run_all.sh` 사용 시 5개의 모든 repo (suite + 4개 sub-project)에 대해 반복

Pre-commit hook (`scripts/pre-commit-hook.sh`)은 generator 출력이 source로부터
drift된 경우 `git commit`을 차단합니다.

---

## 5. 빠른 시작 (Harness 개발)

```bash
# 1. Install the generator
pip install -e .deepx/tools

# 2. Single-repo operations (from the repo root)
dx-agent-gen generate    # Regenerate platform files
dx-agent-gen check       # Verify no drift
dx-agent-gen lint        # Verify EN/KO fragment parity
dx-agent-gen prune       # Remove stale orphan outputs (renamed/removed sources)
dx-agent-gen generate --prune   # Regenerate AND self-clean orphans in one pass

# 3. Suite-wide (process all 5 repos)
bash .deepx/tools/scripts/run_all.sh generate
bash .deepx/tools/scripts/run_all.sh check
bash .deepx/tools/scripts/run_all.sh lint
bash .deepx/tools/scripts/run_all.sh prune

# 4. Install pre-commit hooks (one-time)
bash .deepx/tools/scripts/install-hooks.sh

# 5. Tests
cd .deepx/e2e
./test.sh agent-driven                          # ~700 conformance tests (~1s)
./test.sh agent-driven-e2e-claude-code-autopilot # Claude Code E2E
./test.sh agent-driven-e2e-copilot-cli-autopilot # Copilot CLI E2E
```

---

## 6. Skill 계층 (Tiered 모델)

| Tier | Prefix | Scope | Example |
|------|--------|-------|---------|
| **General SWE** | `dx-swe-*` | 모든 SDK / docs / general coding | `dx-swe-tdd` |
| **End-User (Agent-Driven Dev)** | `dx-agent-*` | dx-agent-dev를 통한 앱/파이프라인 빌드 | `dx-agent-tdd` |
| **Harness Eng** | `dx-harness-*` | 내부 `.deepx/`, `tests/`, `tools/` 유지보수 | `dx-harness-validate` |
| **Internal Business** | `dx-internal-*` | 하네스를 *사용하는* 내부 업무 (model/agent 성능 eval) | `dx-internal-model-eval` |
| **Meta** | `dx-skill-router` | 모든 tier에서 사용 (universal pre-flight) | — |

`dx-agent-*` skill은 대응하는 `dx-swe-*` skill을 참조하고 DEEPX 고유 콘텐츠
(model registry 검사, sub-project 라우팅 등)를 추가합니다.

전체 설계는 [`docs/skill-architecture.md`](docs/skill-architecture.md)를 참조.

---

## 7. 필수 Pre-Flight (HARD GATE)

`/dx-skill-router`는 **모든 사용자 메시지에 대해 절대적인 첫 번째 액션**으로
호출되어야 합니다. 모든 시나리오에 적용됩니다:

| Scenario | Trigger | Mandatory Sequence |
|----------|---------|--------------------|
| **End-User** | `dx-agent-dev/<session_id>/`에 쓰는 task | router → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |
| **Harness Dev** | `.deepx/`, `tests/`, `tools/`를 건드리는 task | router → `dx-swe-brainstorm` → `dx-swe-writing-plans` → `dx-swe-tdd` → `dx-swe-verify` → `dx-harness-validate` |
| **SDK Dev** | SDK source / docs를 건드리는 task (general) | router → `dx-swe-brainstorm` → `dx-swe-writing-plans` → `dx-swe-tdd` → `dx-swe-verify` |

모든 `CLAUDE.md` / `AGENTS.md` / `copilot-instructions.md`에 내장된
`mandatory-process-skill-sequence.md` 및 `swe-process-gates-internal-dev.md`
fragment에 의해 강제됩니다.

---

## 8. 공유 Fragments (16 EN + 16 KO)

Fragment는 5개의 모든 repo의 명령어 파일에 주입되는 재사용 가능한 rule block입니다.
Fragment를 한 번 수정하면 `dx-agent-gen generate`를 통해 변경 사항이 모든 곳에
전파됩니다.

| Fragment | Purpose |
|----------|---------|
| `mandatory-process-skill-sequence` | 코드 생성을 위한 필수 skill 순서 |
| `swe-process-gates-internal-dev` | 내부 harness 작업을 위한 SWE 규율 |
| `skill-router-mandatory` | Universal pre-flight rule |
| `session-sentinels` | `[DX-AGENT-DEV: START/DONE]` 마커 |
| `artifact-verification-gate` | Artifact별 검증 명령어 |
| `brainstorming-spec-before-plan` | Spec → user approval → plan 순서 |
| `rule-conflict-resolution` | 사용자 요청이 HARD GATE와 충돌할 때 수행할 동작 |
| `autopilot-mode-guard` | 사용자가 부재할 때의 동작 |
| `instruction-verification-loop` | Generator + drift check + lint loop |
| `no-placeholder-code` | TODO / stub / 주석 처리된 코드 금지 |
| `experimental-features-prohibited` | Visual companion / 가짜 기능 금지 |
| `response-language` | EN/KO 매칭 + 기술 용어 규칙 |
| `recommended-model` | Claude Sonnet/Opus 4.6+ notice |
| `git-operations-user-handles` | git PR / merge에 대해 묻지 말 것 |
| `git-safety-superpowers` | docs/superpowers/ commit 금지 |
| `plan-output` | 저장 후 chat에 전체 plan 출력 |

Fragment를 추가하거나 수정하는 방법은
[`docs/fragment-authoring-guide.md`](docs/fragment-authoring-guide.md)를 참조.

---

## 9. 추가 자료

| Topic | Document |
|-------|----------|
| 최종 사용자 사용법 (one-liner prompts, scenarios) | [`docs/source/00_Agent_Driven_Development.md`](../docs/source/00_Agent_Driven_Development.md) |
| 포괄적인 `.deepx/` 워크스루 (5개의 모든 repo) | [`docs/dx-agent-dev-overview.md`](docs/dx-agent-dev-overview.md) |
| 3-tier skill 아키텍처 및 네이밍 | [`docs/skill-architecture.md`](docs/skill-architecture.md) |
| 새로운 fragment 작성 방법 | [`docs/fragment-authoring-guide.md`](docs/fragment-authoring-guide.md) |
| `dx-agent-gen` generator 패키지 | [`tools/README.md`](tools/README.md) |
| 운영 스크립트 (`run_all.sh`, hooks, E2E loop) | [`tools/scripts/README.md`](tools/scripts/README.md) |
| E2E 결과 분석기 (리포트, 차트, 대시보드) | [`e2e/agent_analyzer/README-KO.md`](e2e/agent_analyzer/README-KO.md) |
| Showcase 재현성 검증 (verbatim-prompt 평가) | [`e2e/showcase_repro/README-KO.md`](e2e/showcase_repro/README-KO.md) |
| 테스트 카테고리 및 실행 방법 | [`tests/README.md`](tests/README.md) |
| Sub-project 세부 사항 | sub-project `.deepx/README.md` (위 §2에 링크됨) |

---

## 10. Showcase 재현성 하니스 (`e2e/showcase_repro/`)

`e2e/showcase_repro/`는 각 `dx-agent-dev-showcase/<name>/`의 **verbatim 프롬프트**를 autopilot
coding agent(claude-code, cursor, …)로 재실행해 결과가 *equivalent·self-contained·portable*
한지 **등급 평가**합니다. pass/fail 기능 smoke인 `e2e/test_agent_e2e_scenarios/`의 **평가용
짝**으로, 둘은 공존합니다(verbatim 재현 등급 vs 짧은 프롬프트 smoke).

- `showcase_registry.py`가 단일 소스(showcase별 verbatim prompt · route · checker · ground
  truth); `run_repro.py`가 N-showcase × M-agent 매트릭스를 구동해 archive `report.md` +
  `results.json` 생성(e2e conftest autopilot 러너 재사용).
- `checks.py`는 3 tier(artifacts / gates / metrics) + cross-cutting **portability** gate(suite
  밖으로 복사해도 실행되어야 함)로 채점하고, **B2 Output-Isolation guard**가 source dir 쓰기를
  자동 복원 → verdict `EQUIVALENT` / `DEGRADED` / `FAILED` / `BLOCKED`.
- `test_checks.py`는 커밋된 원본으로 각 checker를 단위 검증(회귀 가드); `test_repro_scenarios.py`는
  CI 게이팅용 얇은 **opt-in** pytest 래퍼(`DX_REPRO_RUN=1`).

전체 사용법 및 showcase 추가/갱신 방법: [`e2e/showcase_repro/README-KO.md`](e2e/showcase_repro/README-KO.md).

---

## 11. 용어집

| Term | Meaning |
|------|---------|
| `dx-agent-dev` | DEEPX Agent-Driven Development 기능 (이 시스템 전체). 세션별 출력 디렉토리이기도 함: `dx-agent-dev/<session_id>/`. |
| `dx-agent-gen` | `.deepx/`를 모든 플랫폼별 파일로 fan-out하는 Python CLI. 패키지 source는 `tools/src/dx_agent_dev_gen/` 하위. |
| Fragment | `.deepx/templates/fragments/{en,ko}/` 하위의 재사용 가능한 rule block. 항상 EN + KO 쌍으로 작성됨. |
| Canonical source | `**/.deepx/**` 하위의 파일 — 수정해야 할 유일한 위치. |
| Generator output | 플랫폼별 파일 (`CLAUDE.md`, `.claude/`, `.github/`, `.cursor/`, `.opencode/`). 직접 수정 금지. |
| Session sentinel | 테스트 harness가 사용하는 `[DX-AGENT-DEV: START]` / `[DX-AGENT-DEV: DONE]` 마커. |
| HARD GATE | 협상 불가능한 rule. 사용자가 "그냥 진행"으로 override할 수 없음. |

# `.deepx/tools/` — DEEPX Agent-Driven Development Generator

> `.deepx/` 정본(canonical) 소스를 Claude Code, GitHub Copilot, Cursor, OpenCode용
> 플랫폼별 파일로 변환하는 `dx-agent-gen` Python CLI로, dx-all-suite의 5개
> 저장소 전체에 걸쳐 동작한다.

---

## 1. 개요

`dx-agent-gen`은 generator 경계 아래의 모든 작업을 책임지는 **단일 도구**이다:

- `.deepx/agents/` 와 `.deepx/skills/` 에서 agent/skill 읽기
- fragment 플레이스홀더(`{{FRAGMENT:<name>}}`)를
  `.deepx/templates/fragments/{en,ko}/` 에 대해 해석(resolve)
- 저장소당 4개 플랫폼 출력 렌더링 (Copilot, Claude Code, OpenCode, Cursor)
- 출력이 동기 상태인지 (`check`), 그리고 EN/KO fragment가 일관성 있는지 (`lint`) 검증

한 번 설치되며 dx-all-suite의 5개 저장소 전반에서 사용된다.

---

## 2. 패키지 레이아웃

```
.deepx/tools/
├── README.md                      ← 이 파일
├── README-KO.md                   ← 한국어 번역
├── pyproject.toml                 ← 패키지 정의; `packages.find where=["src"]`가 두 패키지 모두 발견
├── src/
│   ├── dx_agent_dev_gen/        ← 제너레이터 패키지
│   │   ├── __init__.py
│   │   ├── cli.py                 ← `dx-agent-gen` 엔트리포인트
│   │   ├── generator.py           ← 핵심 generate/check/lint/prune 오케스트레이션
│   │   ├── transformers.py        ← 플랫폼별 출력 transformer
│   │   ├── frontmatter.py         ← YAML frontmatter 처리
│   │   └── constants.py           ← 플랫폼 경로, 저장소 정의
│   └── dx_transcripts/            ← 공유 세션 파싱 + transcript 렌더링 라이브러리
│       ├── session_common.py      ← 공유 세션 모델/유틸
│       ├── parse_{claude,codex,copilot,cursor,opencode}_session.py
│       ├── generate_transcripts.py ← DONE-라인 transcript 렌더러 (session sentinel이 실행)
│       └── backfill_claude_html.py
├── tests/                         ← src/ 미러 — 도구별 테스트를 패키지 옆에
│   ├── dx_agent_dev_gen/        ← test_generator.py, test_generator_lint.py
│   └── dx_transcripts/            ← test_parse_*, test_generate_transcripts
└── scripts/                       ← 운영 스크립트 (scripts/README.md 참조)
    ├── run_all.sh
    ├── install-hooks.sh
    ├── pre-commit-hook.sh
    └── run-e2e-improvement-loop.sh
```

> **워크스페이스에 패키지 2개.** `dx_agent_dev_gen`은 제너레이터, `dx_transcripts`는
> session-sentinel DONE-라인 생성·e2e 하니스(`.deepx/e2e/`)·analyzer가 공유하는
> 세션 파싱/transcript 라이브러리. 둘 다 `packages.find where=["src"]`로 발견되고,
> 테스트는 `tools/tests/<package>/`가 `tools/src/<package>/`를 미러합니다.

---

## 3. 모듈 책임

### `cli.py`
`pyproject.toml`을 통해 `dx-agent-gen`으로 노출되는 엔트리포인트. 인자를 파싱하여
`generator.py`의 `generate`, `check`, `lint`, `prune` 액션으로 디스패치한다.

```bash
dx-agent-gen generate [--repo <path>] [--prune] [--dry-run]
dx-agent-gen check    [--repo <path>]
dx-agent-gen lint     [--repo <path>]
dx-agent-gen prune    [--repo <path>] [--dry-run]
```

`--repo` 없이 실행하면 CLI는 현재 작업 디렉터리의 `.deepx/`에 대해 동작한다.

### `generator.py`
핵심 오케스트레이션:
1. `.deepx/agents/` 와 `.deepx/skills/` 를 탐색하여 소스 발견
2. `.deepx/templates/{en,ko}/*.tmpl` 로드
3. `{{FRAGMENT:<name>}}` 플레이스홀더를
   `.deepx/templates/fragments/{en,ko}/<name>.md` 에 대해 해석
4. `transformers.py` 의 플랫폼별 transformer 호출
5. 알려진 타깃 경로로 출력 기록, (`check` 모드에서는) 커밋된 상태와 비교

### `transformers.py`
플랫폼별로 하나의 transformer가 있으며, 플랫폼 고유 관례를 인코딩한다:

| 플랫폼 | 출력 타깃 |
|----------|----------------|
| Claude Code | `CLAUDE.md`, `.claude/agents/`, `.claude/skills/` (얇은 wrapper) |
| GitHub Copilot | `.github/copilot-instructions.md`, `.github/agents/`, `.github/skills/`, `.github/instructions/` |
| OpenCode | `AGENTS.md`, `opencode.json`, `.opencode/agents/` |
| Cursor | `alwaysApply` / `globs` 메타데이터를 갖는 `.cursor/rules/*.mdc` |

각 transformer는:
- 정본 `.md` 파일을 읽음 (YAML frontmatter 포함)
- 플랫폼별 frontmatter 적용 (예: Cursor `globs`, Copilot agent 필드)
- `<!-- AUTO-GENERATED -->` 헤더와 함께 타깃 위치로 기록

### `frontmatter.py`
각 agent/skill 파일 상단의 YAML frontmatter를 파싱/직렬화한다. frontmatter는
skill의 `name`, `description`, 그리고 플랫폼별 필드(예: Cursor `globs`)를
담는다.

### `constants.py`
다음을 선언한다:
- 각 플랫폼의 타깃 파일/디렉터리 경로
- 5개 저장소 세트 (suite, dx-runtime, dx-runtime/dx_app, dx-runtime/dx_stream, dx-compiler)
- lint EN/KO 패리티 체크용 파일 패턴

---

## 4. CLI 명령어

### `generate`
대상 저장소의 모든 플랫폼별 파일을 재생성한다.

```bash
# 저장소 루트에서:
dx-agent-gen generate

# 또는 명시적으로:
dx-agent-gen generate --repo /abs/path/to/repo

# 스위트 전체 (5개 저장소 모두):
bash .deepx/tools/scripts/run_all.sh generate
```

효과:
- `CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md` (+KO 변종) 덮어쓰기
- `.claude/agents/`, `.claude/skills/`,
  `.github/agents/`, `.github/skills/`, `.opencode/agents/`, `.cursor/rules/`
  아래 모든 파일 덮어쓰기
- 각 출력은 `<!-- AUTO-GENERATED -->` 로 시작 (Cursor `.mdc` 는 예외)

### `check`
생성된 출력이 최신 상태인지 수정하지 않고 검증한다.

```bash
dx-agent-gen check
```

- 종료 코드 0 + `All generated files are up-to-date.` → OK
- 종료 코드 0이 아님 + `CHANGED:` / `MISSING:` 줄 → drift 감지됨

pre-commit 훅 (`scripts/pre-commit-hook.sh`)은 모든 `git commit` 시 이를
호출하며, drift가 있으면 커밋을 차단한다.

### `lint`
EN/KO fragment 패리티와 "EN 파일에 한국어 없음" 규칙을 검증한다.

```bash
dx-agent-gen lint
```

검사 항목:
1. 모든 `.deepx/templates/fragments/en/<name>.md` 가 대응하는
   `.deepx/templates/fragments/ko/<name>.md` 를 가짐
2. EN 파일 줄 수가 KO를 ≥ 10줄 초과하지 않음 (KO drift 표시)
3. EN/비-KO 파일에 한국어 문자 없음 (단,
   `<!-- KOREAN-OK: <reason> -->` 로 주석된 경우 제외)

전체 규칙 세트는
[`../docs/fragment-authoring-guide.md`](../docs/fragment-authoring-guide.md)
를 참고하라.

### `prune`
**stale orphan 출력물**을 제거한다 — `.deepx/` 소스가 rename/삭제되어 생성기가 더는
만들지 않는 플랫폼 파일. `check`는 "생성할 파일"만 검증하므로 이런 orphan을 잡지 못하고,
rename 시 구 출력물이 남는다.

```bash
dx-agent-gen prune --dry-run     # 삭제 대상 목록만 출력 (먼저 권장)
dx-agent-gen prune               # orphan 삭제
bash .deepx/tools/scripts/run_all.sh prune   # suite 전체

# rename 시 한 번에 self-clean 하려면 generate에 연동:
dx-agent-gen generate --prune
dx-agent-gen generate --prune --dry-run    # generate + prune 미리보기
```

안전성 — prune은 생성기가 단독 소유하는 위치에서, 생성기 고유 패턴에 맞고, 현재 기대
출력 집합에 없는 파일만 삭제한다:
- skill 디렉터리 `.github/skills/<name>/`, `.claude/skills/<name>/` (1 디렉터리 == 1 skill)
- cursor skill 규칙 `.cursor/rules/skill-*.mdc` (`skill-` 접두어는 생성기 전용)
- agent 파일 `.github/agents/*.agent.md`, `.claude/agents/*.md`, `.opencode/agents/*.md`
- cursor agent 규칙 `.cursor/rules/<stem>.mdc` 은 **`AUTO-GENERATED` 헤더가 있을 때만** —
  따라서 hand-authored `.mdc` 규칙은 절대 건드리지 않는다

---

## 5. Fragment 해석

템플릿은 다음과 같은 플레이스홀더를 포함한다:

```
{{FRAGMENT:mandatory-process-skill-sequence}}
```

EN 타깃(예: `CLAUDE.md`)을 생성할 때, generator는 이를
`.deepx/templates/fragments/en/mandatory-process-skill-sequence.md` 에 대해 해석한다.
KO 타깃(`CLAUDE-KO.md`)의 경우
`.deepx/templates/fragments/ko/mandatory-process-skill-sequence.md` 에 대해 해석한다.

KO 카운터파트가 없으면 **KO 출력이 조용히 망가진다** (플레이스홀더가
사라지거나 원본 텍스트로 표시됨). `lint` 액션이 이를 잡아내며,
`fragment-authoring-guide.md` 규칙 1이 EN+KO 쌍을 강제한다.

---

## 6. 편집 워크플로우

```
1. .deepx/ 소스 편집                  ← 정본
2. dx-agent-gen generate           ← 전파
3. dx-agent-gen check              ← 검증 (clean 이어야 함)
4. dx-agent-gen lint               ← EN/KO 패리티 검증
5. git commit                        ← pre-commit 훅이 check + lint 재실행
```

2단계를 건너뛰는 것이 가장 흔한 조용한 손상의 원인이다: 생성된 파일
(`CLAUDE.md` 등)에 대한 편집은 다음 `generate` 시 덮어써진다.

### Pre-flight 파일 분류

어떤 `.md` 든 편집하기 전에:

| 질문 | YES → | NO → |
|----------|-------|------|
| 경로가 `**/.deepx/**` 안에 있는가? | **정본** — 직접 편집 | 다음으로 이동 |
| 알려진 generator 출력 경로인가? | **생성됨** — `.deepx/` 소스를 대신 편집 | 다음으로 이동 |
| `<!-- AUTO-GENERATED` 로 시작하는가? | **생성됨** — 위와 동일 | **독립** — 직접 편집 |

생성 경로: `CLAUDE.md`, `CLAUDE-KO.md`, `AGENTS.md`, `AGENTS-KO.md`,
`copilot-instructions.md`, `copilot-instructions-KO.md`, `.github/agents/`,
`.github/skills/`, `.claude/agents/`, `.claude/skills/`, `.opencode/agents/`,
`.cursor/rules/`.

---

## 7. 설치

```bash
# CLI 설치 (editable 모드 — src/ 변경 사항이 즉시 반영됨)
pip install -e .deepx/tools

# 설치 검증
dx-agent-gen --help
```

Python 3.10+ 필요. 의존성 (자동 설치됨):
- `jinja2 >= 3.1` — 템플릿 렌더링
- `pyyaml >= 6.0` — YAML frontmatter

---

## 8. Generator 확장

### 새 플랫폼 타깃 추가

1. agent/skill 소스를 받아 새 플랫폼의 디렉터리 레이아웃에 기록하는 transformer
   클래스를 `transformers.py` 에 추가한다.
2. `generator.py` 의 디스패치 테이블에 transformer를 등록한다.
3. `constants.py` 에 타깃 경로를 추가한다.
4. `dx-agent-gen generate` 를 실행하고 새 출력을 검증한다.

### 새 fragment 추가

[`../docs/fragment-authoring-guide.md`](../docs/fragment-authoring-guide.md) 참조.

### 새 skill 또는 agent 추가

1. `.deepx/skills/<name>/SKILL.md` 또는 `.deepx/agents/<name>.md` 아래에
   정본 `.md` 를 작성한다.
2. `dx-agent-gen generate` 실행 — 플랫폼별 복사본이 자동으로 나타난다.

---

## 9. Generator 테스트

```bash
# 스위트 전반의 conformance 테스트 (~700개, ~1초)
cd .deepx/e2e
./test.sh agent-driven

# 이것이 검사하는 것 (generator 관련):
# - 가이드 문서 구조: 존재 여부, 헤딩, 시나리오 번호 매김
# - 라우팅 일관성: CLAUDE.md, AGENTS.md, copilot-instructions.md
# - 시나리오 참조: agent/skill 이름이 실제 인프라와 일치
# - 크로스-프로젝트 시나리오: handoff 체인, 검증 스크립트
```

---

## 10. 관련 문서

| 주제 | 문서 |
|-------|----------|
| 최상위 `.deepx/` 인덱스 | [`../README.md`](../README.md) |
| 운영 스크립트 (`run_all.sh`, 훅, E2E 루프) | [`scripts/README.md`](scripts/README.md) |
| Skill 3-tier 아키텍처 | [`../docs/skill-architecture.md`](../docs/skill-architecture.md) |
| Fragment 작성 규칙 | [`../docs/fragment-authoring-guide.md`](../docs/fragment-authoring-guide.md) |
| 최종 사용자 기능 문서 | [`../../docs/source/00_Agent_Driven_Development.md`](../../docs/source/00_Agent_Driven_Development.md) |
| 종합 `.deepx/` 안내 | [`../docs/dx-agent-dev-overview.md`](../docs/dx-agent-dev-overview.md) |

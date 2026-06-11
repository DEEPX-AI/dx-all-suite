# `.deepx/tools/scripts/` — 운영 스크립트

> dx-all-suite의 5개 repo 전체에 걸쳐 `dx-agent-gen` generator를 오케스트레이션하고,
> git hook을 설치하며, 자가 개선 E2E loop을 실행하는 shell 스크립트.

---

## 1. 구성

| 스크립트 | 목적 |
|--------|---------|
| `run_all.sh` | dx-all-suite의 5개 repo 전체에서 `dx-agent-gen <action>` 실행 |
| `install-hooks.sh` | suite root와 모든 submodule에 pre-commit drift+lint hook 설치 |
| `pre-commit-hook.sh` | pre-commit hook 본체 — git이 호출하며 사용자가 직접 호출하지 않음 |
| `run-e2e-improvement-loop.sh` | 자가 개선 E2E loop (4개 CLI 병렬 실행 + 자동 수정) |
| `README_RUN_E2E_IMPROVEMENT_LOOP.md` (+ KO) | E2E loop 상세 가이드 |

---

## 2. `run_all.sh` — 멀티 repo wrapper

dx-all-suite의 5개 repo 전체 (suite root + dx-compiler + dx-runtime +
dx-runtime/dx_app + dx-runtime/dx_stream)에서 `dx-agent-gen` action을 실행한다.

### 사용법

```bash
# suite root에서:
bash .deepx/tools/scripts/run_all.sh generate
bash .deepx/tools/scripts/run_all.sh check
bash .deepx/tools/scripts/run_all.sh lint
```

### 사용 시점

| 상황 | 명령 |
|-----------|---------|
| `.deepx/templates/fragments/` 아래의 공유 fragment를 편집한 경우 | `generate` (5개 repo 전체에 전파) |
| push 전에 어떤 repo에도 drift가 없는지 검증하고 싶을 때 | `check` |
| fragment를 추가/편집하고 전 repo에서 EN/KO 정합성을 검증하고 싶을 때 | `lint` |
| 단일 repo workflow (현재 repo만) | `run_all.sh` 대신 `dx-agent-gen <action>`을 직접 사용 |

### Exit code

- 5개 repo 모두 성공하면 0 반환
- 어떤 repo라도 실패하면 1 반환 (스크립트는 모든 repo를 끝까지 진행하며
  repo별 상태를 보고하므로 모든 실패를 한 번에 확인할 수 있음)

### 내부 동작

스크립트는 고정된 repo 경로 목록을 순회하며 generator를 Python 모듈
entry point로 호출한다 (CLI shim이 `PATH`에 등록되기 전에도 동작하도록):

```python
from dx_agent_dev_gen.cli import main
sys.exit(main(['<action>', '--repo', '<repo>']))
```

---

## 3. `install-hooks.sh` — 일회성 pre-commit 설정

`pre-commit-hook.sh`를 모든 git hooks 디렉토리에 설치하여 drift나 EN/KO
fragment lint 실패 시 commit이 차단되도록 한다.

### 사용법

```bash
# suite root에서 clone당 한 번만 실행:
bash .deepx/tools/scripts/install-hooks.sh
```

### 동작 내용

`pre-commit-hook.sh`를 다음 위치에 복사한다:

| Hook 위치 | Repo |
|---------------|------|
| `.git/hooks/pre-commit` | dx-all-suite root |
| `.git/modules/dx-compiler/hooks/pre-commit` | dx-compiler (submodule) |
| `.git/modules/dx-runtime/hooks/pre-commit` | dx-runtime (submodule) |
| `.git/modules/dx-runtime/modules/dx_app/hooks/pre-commit` | dx_app (중첩 submodule) |
| `.git/modules/dx-runtime/modules/dx_stream/hooks/pre-commit` | dx_stream (중첩 submodule) |

특정 위치에 이미 pre-commit hook이 존재하면, 스크립트는 대신
`pre-commit.dx-agent-gen`로 기록하고 기존 hook에서 chain하는 방법을 안내한다.

### Hook 건너뛰기 (필요 시)

```bash
git commit --no-verify   # 모든 hook 우회
```

drift 결과를 이해한 경우에만 사용 (예: WIP commit).

---

## 4. `pre-commit-hook.sh` — Drift + Lint 가드

매 `git commit`마다 git이 자동으로 실행한다. 세 가지 검사를 수행한다:

### 검사 1: Staged 파일 범위 경고

`.deepx/` 파일과 `.deepx/` 외부 파일이 동일 commit에 함께 staged된 경우,
`.deepx/` 외부 파일 목록을 출력하는 경고를 표시한다. 이는 정보성이며 — commit은
그대로 진행된다 — 의도치 않은 `git add -A`로 무관한 변경이 포함되는 것을 잡기 위한 것이다.

### 검사 2: Drift 검사 (commit에 의해 영향받는 repo별)

`.deepx/`가 범위에 포함된 각 repo에 대해:

```bash
dx-agent-gen check --repo <repo>
```

어떤 repo라도 drift를 보고하면, commit이 **차단**되며 다음 안내가 표시된다:

```
ERROR: Generated files out-of-date in <repo>

Fix: dx-agent-gen generate --repo <repo>
  or: .deepx/tools/scripts/run_all.sh generate
```

### 검사 3: EN/KO fragment 정합성 lint (`.deepx/` 파일이 staged된 경우)

staged된 `.deepx/` 변경이 있는 각 repo에 대해:

```bash
dx-agent-gen lint --repo <repo>
```

lint가 `[ERROR]` (KO 짝 누락, KO가 너무 짧음, EN 파일에 한국어 텍스트 존재)를
보고하면, commit이 **차단**된다.

### Hook 건너뛰기

```bash
git commit --no-verify
```

---

## 5. `run-e2e-improvement-loop.sh` — 자가 개선 E2E loop

4개 CLI (Copilot, Cursor, OpenCode, Claude Code) 전체에 걸쳐 agent-driven E2E
테스트를 병렬로 실행하고, 비교 리포트를 생성하며, orchestrator 에이전트를 통해
자동 개선을 적용한다. 그리고 이를 반복한다.

이는 장기 실행 오케스트레이션 스크립트이며 (반복당 수 시간 소요), 자체 상세
가이드를 가진다:

- EN: [`README_RUN_E2E_IMPROVEMENT_LOOP.md`](README_RUN_E2E_IMPROVEMENT_LOOP.md)
- KO: [`README_RUN_E2E_IMPROVEMENT_LOOP-KO.md`](README_RUN_E2E_IMPROVEMENT_LOOP-KO.md)

### 빠른 참조

```bash
# 표준 실행 (5회 반복, suite 시나리오)
bash .deepx/tools/scripts/run-e2e-improvement-loop.sh

# 커스텀 반복 횟수로 백그라운드 실행
bash .deepx/tools/scripts/run-e2e-improvement-loop.sh --max-iterations 10 &

# 최신 실행으로부터 재개
bash .deepx/tools/scripts/run-e2e-improvement-loop.sh --resume

# 다른 orchestrator 선택
bash .deepx/tools/scripts/run-e2e-improvement-loop.sh --orchestrator copilot
```

옵션 상세, 중단 조건, orchestrator 선택은 전용 README를 참고할 것.

---

## 6. 운영 레시피

### 공유 fragment 편집 후

```bash
# 1. 5개 repo 전체에 전파
bash .deepx/tools/scripts/run_all.sh generate

# 2. drift 없음을 검증
bash .deepx/tools/scripts/run_all.sh check

# 3. EN/KO 정합성 검증
bash .deepx/tools/scripts/run_all.sh lint

# 4. Commit (hook도 안전망으로 check + lint 실행)
git add .deepx/ CLAUDE.md AGENTS.md CLAUDE-KO.md AGENTS-KO.md \
        .github/ .claude/ .cursor/ .opencode/
git commit -m "fragments: <description>"
```

### 새 clone 설정

```bash
git clone <suite-url>
cd dx-all-suite
git submodule update --init --recursive
pip install -e .deepx/tools
bash .deepx/tools/scripts/install-hooks.sh
bash .deepx/tools/scripts/run_all.sh check   # sanity check
```

### Pre-commit hook이 차단할 때

```bash
# 보통 fragment를 편집한 후 generator를 재실행하지 않은 경우임
bash .deepx/tools/scripts/run_all.sh generate
git add -p   # generator가 변경한 내용 검토
git commit
```

---

## 7. 관련 문서

| 주제 | 문서 |
|-------|----------|
| `dx-agent-gen` 패키지 (CLI 내부 동작) | [`../README.md`](../README.md) |
| 최상위 `.deepx/` 인덱스 | [`../../README.md`](../../README.md) |
| Fragment 작성 규칙 | [`../../docs/fragment-authoring-guide.md`](../../docs/fragment-authoring-guide.md) |
| 내부 SWE 프로세스 gate | CLAUDE.md / AGENTS.md에 임베드됨 (fragment: `swe-process-gates-internal-dev`) |

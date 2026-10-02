# `.deepx/tools/scripts/` — 운영 스크립트

> dx-all-suite의 5개 repo 전체에 걸쳐 `dx-agent-gen` generator를 오케스트레이션하고,
> git hook을 설치하며, 자가 개선 E2E loop을 실행하는 shell 스크립트.

---

## 1. 구성

| 스크립트 | 목적 |
|--------|---------|
| `run_all.sh` | dx-all-suite의 5개 repo 전체에서 `dx-agent-gen <action>` 실행 |
| `subrepo_check.sh` | 독립된 sub-repo checkout 내부에서 generator의 drift 검사를 실행 (CI의 sub-repo gate가 사용) |
| `harness_gate.sh` | suite CI gate(`harness-gate`)를 CI와 로컬에서 동일한 명령 집합으로 실행 — `deps\|check\|lint\|tests\|e2e-sh\|all` |
| `gate_mode.sh` | suite gate 모드 결정: push/PR 범위에 submodule gitlink 변경이 있거나(→ `pointer`) dispatch로 요청한 경우가 아니면 `branch-tip` |
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

## 3. `subrepo_check.sh` — Sub-Repo Drift Gate

`dx-agent-gen` generator와 그것이 렌더링하는 공유 fragment
(`.deepx/templates/fragments`)는 dx-all-suite root에만 존재한다. 따라서
독립된 sub-repo checkout(dx-compiler, dx-runtime, dx_app, dx_stream — CI가 PR을
보는 방식)은 그 자체로는 `dx-agent-gen check`를 실행할 수 없다: fragment를 찾을
suite tree가 그 위에 없기 때문이다. `subrepo_check.sh`는 이 간극을 메운다 — suite
checkout(`--suite-dir`로 지정한 기존 checkout, 또는 새로 shallow clone한 것)을
확보한 뒤, 일회용 "shell" tree(`$WORK/suite/.deepx`는 실제 suite의 `.deepx`로의
symlink이고, 여기에 sub-repo를 canonical한 중첩 경로에 복사)를 구성하여 generator의
fragment lookup이 성공하도록 한다. 이를 통해 CI는 suite가 submodule pointer를
bump하는 시점이 아니라 sub-repo의 commit/PR 시점에 `.deepx/` drift를 잡을 수 있다.

### 사용법

```
subrepo_check.sh --subrepo-path <dx-compiler|dx-runtime|dx-runtime/dx_app|dx-runtime/dx_stream>
                  [--repo-dir DIR]           # sub-repo checkout to check (default: $PWD)
                  [--suite-dir DIR]          # existing suite checkout (skips clone); must
                                             #   contain .deepx/tools/src/dx_agent_dev_gen/cli.py
                                             #   AND .deepx/templates/fragments
                  [--suite-url URL]          # default: origin URL of --repo-dir, last
                                             #   path component swapped for dx-all-suite(.git)
                  [--suite-ref REF]          # default: current branch of --repo-dir
                                             #   (detached HEAD -> remote default branch)
                  [--mode archive|worktree]  # archive (default) = committed HEAD via
                                             #   `git archive` (requires --repo-dir to be a
                                             #   git repo); worktree = working tree incl.
                                             #   uncommitted changes, .git excluded
                  [--work DIR]               # scratch dir (default: fresh mktemp -d). A
                                             #   user-supplied --work dir is NEVER deleted
                                             #   by this script, regardless of --keep.
                  [--keep]                   # keep the mktemp'd scratch dir (only relevant
                                             #   when --work is NOT given — a user-supplied
                                             #   --work dir is already never deleted)
                  [--strict-validator]       # validate_framework.py failures become fatal
                  [--print-suite-url]        # print the derived/given suite URL and exit 0
                                             #   (does not require --subrepo-path)
                  [--help|-h]                # print this usage and exit 0
```

### 대표 실행 예시

| 상황 | 명령 |
|---------|---------|
| CI (sub-repo gate workflow) | `bash suite/.deepx/tools/scripts/subrepo_check.sh --subrepo-path dx-compiler --repo-dir "$GITHUB_WORKSPACE/self" --suite-dir "$GITHUB_WORKSPACE/suite"` |
| Local, suite checkout에서 실행 (같은 branch) | `bash .deepx/tools/scripts/subrepo_check.sh --subrepo-path dx-compiler --repo-dir /path/to/dx-compiler --suite-dir . --mode worktree` |
| 독립 sub-repo clone (suite checkout 없음) | `bash .deepx/tools/scripts/subrepo_check.sh --subrepo-path dx-compiler` (기본값: dx-all-suite의 동일 이름 branch를 clone하며, 해당 branch가 없으면 default branch로 fallback) |

### Exit code

| 코드 | 의미 |
|------|---------|
| 0 | Clean — 생성된 파일이 `.deepx/` 소스와 일치 (`--strict-validator` 지정 시 `validate_framework.py`도 통과) |
| 1 | drift 발견 (`dx-agent-gen check`가 `MISSING:`/`CHANGED:` 보고), 또는 `--strict-validator` 지정 상태에서 `validate_framework.py` 실패 |
| 2 | 설정/사용/도구 오류 — 잘못된 `--subrepo-path`, suite 접근 불가/없음, `python3` 없음 또는 3.8 미만, 또는 generator 자체 crash (`Traceback` / rc ≥ 2 는 **drift가 아님**으로 보고 — 재생성할 것이 없으며 tool/runner를 고쳐야 함) |

### 실패했을 때

sub-repo와 **동일한 branch**의 suite checkout에서, sub-repo를 canonical한
위치에 둔 채로:

```bash
bash .deepx/tools/scripts/run_all.sh generate
bash .deepx/tools/scripts/run_all.sh check   # 반드시 clean해야 함
```

그런 다음 sub-repo에서 재생성된 파일을 commit한다. sub-repo 혼자서는 이를
고칠 수 없다 — generator와 공유 fragment는 dx-all-suite에만 존재한다.

### Validator

`validate_framework.py`(sub-repo에 존재하는 경우)는 drift 검사 이후 실행되며
**기본적으로 non-blocking**이다 — 실패해도 `WARNING`만 출력하고 exit code에는
영향을 주지 않는다. `--strict-validator`를 넘기면 실패를 fatal(exit 1)로 만든다.

### 호출 workflow

`.github/workflows/dx-agent-dev-subrepo-gate-{ghes,cloud}.yml`(job `subrepo-gate`)에서
호출하며, 4개 sub-repo(dx-compiler, dx-runtime, dx-runtime/dx_app,
dx-runtime/dx_stream) 각각에 존재한다. 이 gate가 suite 수준의
`dx-agent-dev-gate-{ghes,cloud}.yml`(`harness-gate`)과 어떻게 연관되는지는 §8 "관련 문서" —
최상위 `.deepx/README.md`와 `dx-agent-dev-overview.md`를 참고할 것.

---

## 3b. `harness_gate.sh` — Suite Gate 로컬 실행

suite 수준 CI gate(`harness-gate`, `.github/workflows/dx-agent-dev-gate-{ghes,cloud}.yml`)는
모든 검사를 이 스크립트를 통해 실행하므로, 개발자 머신에서도 동일한 명령 집합이
재현된다 — 로컬에서 `harness_gate.sh all`이 green이면 CI gate도 green이다.

### 사용법

```
harness_gate.sh <stage> [--python PY]

  deps     python is >= 3.8 and has jinja2 + pyyaml + pytest + rich (prints a hint if not)
  check    bash .deepx/tools/scripts/run_all.sh check        (drift, all 5 levels)
  lint     bash .deepx/tools/scripts/run_all.sh lint         (EN/KO fragment parity)
  tests    python -m pytest --rootdir=<suite> .deepx/tests/conformance .deepx/tools/tests .deepx/e2e/tests
  e2e-sh   bash .deepx/e2e/tests/test_run_model_eval.sh      (run_model_eval.sh dry-run tests)
  all      deps, then check, lint, tests, e2e-sh — keeps going after a failure,
           prints a summary, exits 1 if any stage failed

  --python PY   interpreter to use (default: $DX_GATE_PYTHON, else python3); a path's
                bin dir is prepended to PATH so run_all.sh's python3 matches
```

suite root는 스크립트 자신의 위치에서 찾으므로 어느 디렉터리에서든 호출할 수 있다.

### Exit code

| Code | 의미 |
|------|---------|
| 0 | 요청한 stage 모두 통과 |
| 1 | stage 실패 (또는 `deps`가 누락 모듈을 발견) |
| 2 | Usage / setup 오류 (알 수 없는 stage, 잘못된 `--python`) |

CI 측(runner, token, 환경별 onboarding)은 [`../../docs/ci-gates-KO.md`](../../docs/ci-gates-KO.md)를 참고.

---

## 4. `install-hooks.sh` — 일회성 pre-commit 설정

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

## 5. `pre-commit-hook.sh` — Drift + Lint 가드

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

## 6. `run-e2e-improvement-loop.sh` — 자가 개선 E2E loop

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

## 7. 운영 레시피

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
pipx install --force --editable .deepx/tools   # PEP 668-safe
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

## 8. 관련 문서

| 주제 | 문서 |
|-------|----------|
| `dx-agent-gen` 패키지 (CLI 내부 동작) | [`../README.md`](../README.md) |
| 최상위 `.deepx/` 인덱스 | [`../../README.md`](../../README.md) |
| Fragment 작성 규칙 | [`../../docs/fragment-authoring-guide.md`](../../docs/fragment-authoring-guide.md) |
| 내부 SWE 프로세스 gate | CLAUDE.md / AGENTS.md에 임베드됨 (fragment: `swe-process-gates-internal-dev`) |
| Sub-repo gate 호출 workflow | `.github/workflows/dx-agent-dev-subrepo-gate-{ghes,cloud}.yml` (sub-repo별) |
| Suite 수준 통합 gate | `.github/workflows/dx-agent-dev-gate-{ghes,cloud}.yml` (job `harness-gate`, suite root) |

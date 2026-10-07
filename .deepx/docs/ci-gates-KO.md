# dx-agent-dev CI Gates — GHES · 미러 · 공개 채널에서의 harness-gate / subrepo-gate

이 문서는 dx-agent-dev harness(`.deepx/` canonical source → 생성되는 `CLAUDE.md` /
`AGENTS.md` / `.claude` / `.github` / `.cursor` / `.opencode`)를 보호하는 두 CI gate가
세 hosting 환경에서 각각 어떻게 실행되는지, 실제로 실행하는 정확한 명령, 로컬 재현
방법, 그리고 각 환경의 onboarding / 검증 절차를 다룬다.

## 1. 세 가지 환경

| 환경 | Host | Repo 공개 여부 | Runner | Token secret | 실행되는 workflow 파일 |
|---|---|---|---|---|---|
| 폐쇄망 GHES (개발) | `gh.deepx.ai/deepx/*` | private | `self-hosted` (이미 등록됨) | `GH_DCI_TOKEN` (이미 존재) | `*-ghes.yml` |
| 미러 (github.com) | `github.com/deepx-dhyang/*` | private | GitHub 제공 `ubuntu-latest` (self-hosted runner 없음) | `GC_DCI_TOKEN` — fine-grained PAT, dx-all-suite, dx-runtime, dx-compiler, dx_app, dx_stream에 *Contents: Read-only* (admin이 등록해야 함) | `*-cloud.yml` |
| 공개 채널 (엔드유저) | `github.com/DEEPX-AI/*` | public | GitHub 제공 `ubuntu-latest` | 불필요 (`github.token`으로 public repo 읽기 가능) | `*-cloud.yml` |

한 gate의 두 변형은 내부 repo 안에 나란히 존재한다. 각 job에는 host guard —
`if: github.server_url != 'https://github.com'` (ghes) 또는 `== 'https://github.com'`
(cloud) — 가 있어, 어느 host에서든 쌍 중 정확히 하나만 실행되고 나머지는 즉시
skip된다(runner 큐에 들어가지 않음). 미러는 GHES의 git 미러이므로 두 파일을 모두
받는데, 이 guard 덕분에 ghes 파일이 존재하지 않는 self-hosted 큐에서 영원히
대기하는 일이 없다.

두 gate 모두 NPU나 coding CLI가 필요하지 않다: drift check, EN/KO lint, pytest
(conformance + generator tools + e2e unit test), `run_model_eval.sh --dry-run`
shell test는 모두 pure Python이다. 그래서 github.com 변형은 self-hosted runner가
연결된 곳에서도 GitHub 제공 `ubuntu-latest`를 사용한다.

## 2. 파일

| Gate | Job / required-check 이름 | 위치 | 파일 |
|---|---|---|---|
| Suite gate | `harness-gate` | dx-all-suite | `.github/workflows/dx-agent-dev-gate-ghes.yml`, `.github/workflows/dx-agent-dev-gate-cloud.yml` |
| Sub-repo gate | `subrepo-gate` | dx-compiler, dx-runtime, dx-runtime/dx_app, dx-runtime/dx_stream (각각) | `.github/workflows/dx-agent-dev-subrepo-gate-ghes.yml`, `.github/workflows/dx-agent-dev-subrepo-gate-cloud.yml` |
| 공용 스크립트 (suite gate) | — | dx-all-suite | `.deepx/tools/scripts/harness_gate.sh` |
| 공용 스크립트 (sub-repo gate) | — | dx-all-suite | `.deepx/tools/scripts/subrepo_check.sh` (참고: `tools/scripts/README-KO.md` §3) |

2026-09-08에 제거되고 위의 쌍으로 대체됨: `dx-agent-dev-gate.yml`, `gh-drift-check.yml` (suite), `dx-agent-dev-subrepo-gate.yml` (sub-repo).

쌍을 이루는 두 파일은 `runs-on`, token secret, host guard, Python bootstrap step,
header 주석만 다르다. pass/fail을 결정하는 부분은 완전히 동일하며, conformance test
`test_suite_gate_workflows.py::test_ghes_and_cloud_share_the_same_stage_commands`와
`test_subrepo_gate_workflows.py::test_ghes_and_cloud_differ_only_in_expected_places`가
이를 강제한다.

## 3. 각 gate가 실행하는 것 — 정확한 명령

### 3.1 Suite gate (`harness-gate`)

Trigger: `pull_request`, `main` / `staging*` / `feature/**` 로의 `push`,
`workflow_dispatch` (입력 `mode`: `branch-tip`(기본) 또는 `pointer`).

**모드 선택** (step `mode`, `.deepx/tools/scripts/gate_mode.sh`가 결정):

| 상황 | Event | 검사 범위 | 모드 |
|---|---|---|---|
| `update-submodule.yml`이 `ci(<date>): Update dx-runtime` commit을 만들어 `main`에 push | `push` | `github.event.before` .. `github.sha` | submodule gitlink 변경 있음 → **`pointer`** (기록된 조합 검증) |
| 개발자가 feature 브랜치에 `.deepx/` 변경을 push | `push` | `before` .. `sha` | gitlink 변경 없음 → **`branch-tip`** |
| `.deepx/` / 문서 / workflow만 바꾼 PR | `pull_request` | merge commit의 first parent(현재 base tip) .. merge commit | gitlink 변경 없음 → **`branch-tip`** — `base.sha` 이후 `main`이 pointer를 bump했어도 |
| submodule pointer를 수동으로 bump한 PR | `pull_request` | merge commit의 first parent .. merge commit | gitlink 변경 있음 → **`pointer`** |
| 수동 실행 | `workflow_dispatch` | 입력 `mode` | 선택한 값 (`branch-tip` 기본) |

이 step은 base commit을 header 인증으로 fetch한 뒤(checkout은 depth 1)
`gate_mode.sh --event … --from <base> --to $GITHUB_SHA`를 호출한다. base가 없거나
접근 불가하면(새 브랜치, history rewrite) `branch-tip`으로 fallback하고 그 사실을 job
summary와 `::notice`에 남긴다. 선택된 모드와 이유는 run의 summary 페이지에 기록된다.

| Step | 명령 (cwd = suite root) |
|---|---|
| Checkout | `actions/checkout@v4`, `submodules: false`, `fetch-depth: 1`, `persist-credentials: false` |
| 모드 선택 | `bash .deepx/tools/scripts/gate_mode.sh --event <event> --from <base> --to $GITHUB_SHA --input-mode <dispatch 입력>` → `mode=branch-tip|pointer` (위 *모드 선택* 참고) |
| 필수 submodule init | `git -c http.extraheader="AUTHORIZATION: basic <x-access-token:TOKEN의 base64>" submodule update --init --depth 1 -- dx-runtime dx-compiler`, 이어서 `-C dx-runtime … -- dx_app dx_stream`. `branch-tip` 모드면 4개 각각에 대해 `ls-remote --heads origin <branch>`(suite branch와 같은 이름, 없으면 remote default branch) → `fetch --depth 1 origin <branch>` → `checkout --detach FETCH_HEAD` |
| Python deps | ghes: 시스템 `python3`로 `bash .deepx/tools/scripts/harness_gate.sh deps`, 실패 시 `python3 -m venv .gate-venv && .gate-venv/bin/pip install "jinja2>=3.1" "pyyaml>=6.0" "pytest>=8,<9" "rich>=13"` 로 fallback. cloud: `actions/setup-python@v5` (3.12) → `python -m pip install -e .deepx/tools "pytest>=8,<9" "rich>=13"` → `harness_gate.sh deps` |
| Drift check | `bash .deepx/tools/scripts/harness_gate.sh check` → `bash .deepx/tools/scripts/run_all.sh check` (5 level 전체) |
| EN/KO lint | `bash .deepx/tools/scripts/harness_gate.sh lint` → `bash .deepx/tools/scripts/run_all.sh lint` |
| Tests | `bash .deepx/tools/scripts/harness_gate.sh tests` → `python -m pytest --rootdir=. .deepx/tests/conformance .deepx/tools/tests .deepx/e2e/tests -q --no-header -p no:cacheprovider` |
| Shell tests | `bash .deepx/tools/scripts/harness_gate.sh e2e-sh` → `bash .deepx/e2e/tests/test_run_model_eval.sh` |

submodule을 4개만 init하고 `submodules: recursive`를 쓰지 않는 이유: gate에는
`.deepx/`를 가진 정확히 네 repo만 필요하다. `dx_rt`, `dx_fw`,
`dx_rt_npu_linux_driver`, `dx-modelzoo`는 gate와 무관하고 모든 host에 존재하지도
않으므로(미러에는 `dx_fw`가 없음), recursive checkout은 harness와 무관한 이유로
실패한다.

두 모드가 있는 이유: `pointer`는 suite가 실제로 기록한 sub-repo commit — 통합
관점의 정답 — 을 검사하므로, 진행 중인 sub-repo 작업보다 pointer가 뒤처져 있으면
언제나 red다(모든 feature 브랜치, 그리고 pointer를 bump하지 않는 미러). `branch-tip`은
같은 이름 브랜치들이 merge된 뒤 존재할 상태를 검증하며, PR이 알고 싶은 것이 바로
그것이다. pointer 검사는 pointer가 바뀔 때(gitlink diff) 또는 명시적으로 요청할 때만
수행된다.

### 3.2 Sub-repo gate (`subrepo-gate`, sub-repo별 1개)

Trigger: 위와 동일한 event (입력 없음).

| Step | 명령 (cwd = `$GITHUB_WORKSPACE`) |
|---|---|
| 이 repo checkout | `actions/checkout@v4`를 `self/`로, `fetch-depth: 1`, `persist-credentials: false` |
| suite clone | `URL=https://<host>/<owner>/dx-all-suite.git`; `git -c http.extraheader=… ls-remote --heads "$URL" "<branch>"` → 같은 이름 branch가 있으면 그것(sync 도구가 dx-all-suite를 sub-repo 뒤에 push하므로 최대 `SUITE_BRANCH_WAIT` = 180초 polling), 없으면 default branch; `git -c http.extraheader=… clone -q --depth 1 --no-recurse-submodules --branch <use> "$URL" suite`; `subrepo_check.sh`가 없는 suite는 `::error::`로 거부(suite 먼저 sync 후 re-run) |
| Python deps | ghes: 시스템 `python3`가 **3.8 이상**이어야 하고(fail-fast) `jinja2`와 `yaml`을 import할 수 있어야 하며, 아니면 `.gate-venv` fallback. cloud: `actions/setup-python@v5` (3.12) → `python -m pip install "jinja2>=3.1" "pyyaml>=6.0"` |
| Drift check | `bash suite/.deepx/tools/scripts/subrepo_check.sh --subrepo-path <dx-compiler \| dx-runtime \| dx-runtime/dx_app \| dx-runtime/dx_stream> --repo-dir "$GITHUB_WORKSPACE/self" --suite-dir "$GITHUB_WORKSPACE/suite"` |
| Cleanup (`if: always()`) | `rm -rf "$GITHUB_WORKSPACE/suite"` (ghes는 `.gate-venv`도 함께) |

모든 파일이 공유하는 보안 규칙: `permissions: contents: read`; token은
`git -c http.extraheader=…`로 전달하며 URL에 넣지 않는다(self-hosted runner의
`.git/config`에 영구 저장되기 때문); `set -x`는 사용하지 않는다; fork에서 온 pull
request에서는 job이 실행되지 않는다
(`github.event.pull_request.head.repo.full_name == github.repository`).

## 4. 로컬 재현 (CI와 동일한 명령)

네 sub-repo가 init된 dx-all-suite checkout에서:

```bash
# whole suite gate, one command — per-stage summary, exit 1 if any stage failed
bash .deepx/tools/scripts/harness_gate.sh all

# individual stages
bash .deepx/tools/scripts/harness_gate.sh deps      # jinja2 / pyyaml / pytest / rich present?
bash .deepx/tools/scripts/harness_gate.sh check     # drift, all 5 levels
bash .deepx/tools/scripts/harness_gate.sh lint      # EN/KO fragment parity
bash .deepx/tools/scripts/harness_gate.sh tests     # pytest conformance + tools + e2e unit
bash .deepx/tools/scripts/harness_gate.sh e2e-sh    # run_model_eval.sh dry-run tests

# use a specific interpreter (e.g. a venv on a PEP 668 host)
python3 -m venv .gate-venv && .gate-venv/bin/pip install "jinja2>=3.1" "pyyaml>=6.0" "pytest>=8,<9" "rich>=13"
bash .deepx/tools/scripts/harness_gate.sh all --python .gate-venv/bin/python

# sub-repo gate for one repo, against THIS suite checkout, including uncommitted changes
bash .deepx/tools/scripts/subrepo_check.sh --subrepo-path dx-compiler          --repo-dir dx-compiler          --suite-dir . --mode worktree
bash .deepx/tools/scripts/subrepo_check.sh --subrepo-path dx-runtime           --repo-dir dx-runtime           --suite-dir . --mode worktree
bash .deepx/tools/scripts/subrepo_check.sh --subrepo-path dx-runtime/dx_app    --repo-dir dx-runtime/dx_app    --suite-dir . --mode worktree
bash .deepx/tools/scripts/subrepo_check.sh --subrepo-path dx-runtime/dx_stream --repo-dir dx-runtime/dx_stream --suite-dir . --mode worktree
```

`harness_gate.sh`는 자기 위치에서 suite root를 찾으므로 어느 디렉터리에서든 호출할
수 있다. Exit code: 0 pass · 1 stage 실패 · 2 usage 또는 setup 오류.
`--mode worktree`를 빼면 commit된 HEAD만 검사한다(CI가 보는 것과 동일).

## 5. 환경별 onboarding / 검증

### 5.1 미러 — github.com/deepx-dhyang/*

1. 5개 repo 각각의 Actions 정책(Settings → Actions → General → *Actions permissions*)이
   gate가 사용하는 GitHub 소유 action(`actions/checkout@v4`, `actions/setup-python@v5`)을
   허용해야 한다: *Allow all actions and reusable workflows*, 또는 *Allow deepx-dhyang, and
   select non-deepx-dhyang, actions and reusable workflows*에 **Allow actions created by
   GitHub**를 체크. 더 좁은 *Allow deepx-dhyang actions and reusable workflows*
   (`allowed_actions: local_only`)는 workflow 파일 자체를 거부하므로 — 두 변형 모두, 모든
   실행이 0초 만에 job 0개인 `startup_failure`로 끝난다 ("This run likely failed because of
   a workflow file issue"). 확인:
   `gh api repos/deepx-dhyang/<repo>/actions/permissions --jq .allowed_actions`
   (`all` 또는 `selected`면 정상, `local_only`면 안 됨).
2. **fine-grained personal access token**을 만든다: resource owner `deepx-dhyang`,
   repository `dx-all-suite`, `dx-runtime`, `dx-compiler`, `dx_app`, `dx_stream`,
   repository permission *Contents: Read-only*. 이를 5개 repo 각각의 Actions secret
   **`GC_DCI_TOKEN`**으로 등록한다 (Settings → Secrets and variables → Actions → New
   repository secret). 없으면 private submodule init / suite clone이 실패한다
   (`cannot reach …` 또는 authentication error).
3. branch를 push한다 (push되는 branch에 workflow 파일이 있어야 함). `push` trigger로
   `dx-agent-dev gate (cloud)`와 각 sub-repo의 `dx-agent-dev sub-repo gate (cloud)`가
   실행되고, ghes 쌍은 *skipped*로 표시된다.
4. push·PR로 실행되는 suite run은 `branch-tip`(gitlink 변경 없음)이므로, 같은 이름의
   sub-repo 브랜치에 재생성 파일이 들어 있는 한 green이다. 미러는 submodule pointer를
   bump하지 **않으므로**, 수동 `pointer` run은 pointer가 bump되기 전까지 red인 것이 정상:

```bash
gh workflow run "dx-agent-dev gate (cloud)" -R deepx-dhyang/dx-all-suite --ref feature/dx-agent-dev -f mode=branch-tip
gh workflow run "dx-agent-dev gate (cloud)" -R deepx-dhyang/dx-all-suite --ref feature/dx-agent-dev -f mode=pointer      # integration truth
gh run list  -R deepx-dhyang/dx-all-suite --workflow "dx-agent-dev gate (cloud)" -L 3
gh run watch -R deepx-dhyang/dx-all-suite            # or: gh run view <id> --log-failed

for R in dx-compiler dx-runtime dx_app dx_stream; do
  gh workflow run "dx-agent-dev sub-repo gate (cloud)" -R deepx-dhyang/$R --ref feature/dx-agent-dev
done
gh run list -R deepx-dhyang/dx_app --workflow "dx-agent-dev sub-repo gate (cloud)" -L 3
```

### 5.2 폐쇄망 GHES — gh.deepx.ai/deepx/*

- `GH_DCI_TOKEN`은 이미 존재하고, Actions와 `self-hosted` runner도 이미 등록되어 있다.
- self-hosted runner image는 **3.8 이상**(ASIC pool의 Ubuntu 20.04 runner가 정확히 3.8이며 이것이 gate의 하한)이고 `jinja2`, `pyyaml`, `pytest`, `rich`를 import할 수 있는 `python3`를 제공해야
  한다 (`apt install python3-jinja2 python3-yaml python3-pytest python3-rich` 또는 venv);
  `rich`는 `.deepx/e2e/e2e_monitor.py` / `e2e_runner.py`가 import하며 그 unit test가 gate에 포함된다. 없으면 job이
  `python3 -m venv .gate-venv` + `pip install`을 시도하는데 — 이는 내부 PyPI mirror가 있을
  때만 동작한다 — 그래도 실패하면 누락 패키지를 명시한 `::error::`로 실패한다.
- ghes 변형은 Python toolchain을 다운로드하지 않는다 (`actions/setup-python`은 cloud 변형만
  사용); `actions/checkout@v4`는 GHES에 번들되어 있다.
- 폐쇄망 내부 host에서 검증 (`gh auth login --hostname gh.deepx.ai`):

```bash
gh workflow run "dx-agent-dev gate (ghes)" -R deepx/dx-all-suite --ref <branch>
gh run list -R deepx/dx-all-suite --workflow "dx-agent-dev gate (ghes)" -L 3
for R in dx-compiler dx-runtime dx_app dx_stream; do
  gh workflow run "dx-agent-dev sub-repo gate (ghes)" -R deepx/$R --ref <branch>
done
```

### 5.3 공개 채널 — github.com/DEEPX-AI/*

모든 repo의 `.github/release-excluded`에 `.github/workflows/`가 들어 있으므로, release
export(`public-release.yml` → `deepx/do_workflows-central`)는 workflow 파일을 절대
복사하지 않는다 — 바로 이 규칙이 export를 거쳐도 공개 repo 전용 `gh-cloud-*.yml`
파일이 살아남는 이유이기도 하다. 따라서 **cloud** gate 파일은 `gh-cloud-*.yml`과
같은 방식으로 공개 repo에 **수동으로** 올린다:

```bash
# from the internal suite checkout; requires push rights on DEEPX-AI/*
for R in dx-all-suite dx-compiler dx-runtime dx_app dx_stream; do
  case $R in
    dx-all-suite)     SRC=.github/workflows/dx-agent-dev-gate-cloud.yml ;;
    dx_app|dx_stream) SRC=dx-runtime/$R/.github/workflows/dx-agent-dev-subrepo-gate-cloud.yml ;;
    *)                SRC=$R/.github/workflows/dx-agent-dev-subrepo-gate-cloud.yml ;;
  esac
  T=$(mktemp -d) && git clone -q --depth 1 https://github.com/DEEPX-AI/$R "$T/r" \
    && mkdir -p "$T/r/.github/workflows" && cp "$SRC" "$T/r/.github/workflows/" \
    && git -C "$T/r" checkout -q -b ci/dx-agent-dev-gate && git -C "$T/r" add .github/workflows \
    && git -C "$T/r" commit -q -m "ci: add dx-agent-dev gate (cloud variant)" \
    && git -C "$T/r" push -q origin ci/dx-agent-dev-gate \
    && gh pr create -R DEEPX-AI/$R --head ci/dx-agent-dev-gate --fill
  rm -rf "$T"
done
```

`*-ghes.yml` 파일은 절대 공개 repo에 복사하지 않는다. cloud gate 파일이 내부에서
바뀌면 복사를 반복한다. 공개 repo에는 token이 필요 없다: suite와 네 sub-repo가 모두
public이므로 `github.token`으로 충분하다.

## 6. Required status check

각 repo에서: Settings → Branches (또는 Rules → Rulesets) → `main` / `staging*` 보호 →
*Require status checks to pass* → **`harness-gate`**(suite) 또는 **`subrepo-gate`**
(sub-repo)를 추가한다. job 이름은 두 변형에서 동일하므로 required-check 항목 하나가
해당 host에서 실행되는 변형을 모두 커버한다. 항상 job 이름을 참조하고 workflow
이름은 참조하지 않는다 (workflow 이름은 `dx-agent-dev gate (ghes)` vs
`dx-agent-dev gate (cloud)`로 다름).

### `dev`에만 있는 변경까지 포함해 `main` 검증하기 — `submodule_refs`

dx_app·dx_stream은 `dev`에서, dx-runtime·dx-all-suite는 `main`에서 통합된다. 따라서 suite `main`의
`push` run은 sub-repo들의 `main`(branch-tip)을 검사하므로 dx_app/dx_stream 변경이 `main`에 도달하기
전까지 red가 유지된다 — drift가 아니라 예상된 상태다. **main + dev 통합 뷰**를 보려면 gate를 수동 실행한다:

- UI: Actions → *dx-agent-dev gate (ghes|cloud)* → **Run workflow** → branch `main`,
  `mode = branch-tip`, `submodule_refs = dx_app=dev dx_stream=dev`
- CLI: `gh workflow run dx-agent-dev-gate-ghes.yml -R gh.deepx.ai/deepx/dx-all-suite --ref main -f mode=branch-tip -f submodule_refs='dx_app=dev dx_stream=dev'`

`submodule_refs`는 지정한 sub-repo(`dx-runtime dx-compiler dx_app dx_stream`)만 해당 브랜치 tip에
고정하고 나머지는 기존 같은-이름 규칙을 따른다. `mode=branch-tip`에서만 유효하며, 존재하지 않는
브랜치는 init step이 `::error::`로 실패시킨다. `main` `push` run이 실패하면 *How to fix* step이 이
후속 run을 자동 dispatch 시도하고(`actions:write` 권한 토큰 필요; `GH_DCI_TOKEN` / `GC_DCI_TOKEN`),
불가하면 위 두 명령을 안내한다. 로컬에서는 `main` checkout에서
`git -C dx-runtime/dx_app checkout dev && git -C dx-runtime/dx_stream checkout dev` 후
`bash .deepx/tools/scripts/harness_gate.sh all`이 같은 뷰다.

## 7. Gate가 red일 때

| 증상 | 조치 |
|---|---|
| `MISSING:` / `CHANGED:` 라인 (drift) | 같은 branch의 suite checkout에서 `bash .deepx/tools/scripts/run_all.sh generate && bash .deepx/tools/scripts/run_all.sh check` 실행 후, 영향받은 repo에서 재생성된 파일을 commit. `CLAUDE.md` / `AGENTS.md` / `.claude` / `.github` / `.cursor` / `.opencode`를 직접 수정하지 말 것. |
| `[ERROR] … EN exceeds KO` (lint) | `.deepx/templates/fragments/ko/<stem>.md`를 추가/보강하고 재생성. |
| pytest 실패 | `bash .deepx/tools/scripts/harness_gate.sh tests`로 재현; conformance test가 문제 파일을 알려준다. |
| `cannot reach https://…/dx-all-suite.git (auth/network)` 또는 `Authentication failed` | `GC_DCI_TOKEN`(미러) / `GH_DCI_TOKEN`(GHES) 누락 또는 만료; 공개 채널에서라면 suite repo가 public이 아니라는 뜻. |
| `fatal: … dx_fw` 등 무관한 submodule 오류 | gate는 submodule 4개만 init한다; `recursive` checkout 또는 `git submodule status --recursive`가 다시 들어간 것 — 명시적 init step / 4개 경로 목록으로 복구. self-hosted runner에서는 checkout 전에 *Reset the reused workspace* step이 돌아야 한다(다른 job이 남긴 submodule 트리를 지움). |
| PR이 submodule을 건드리지 않았는데 `pointer` 모드가 선택됨 | `gate_mode.sh`는 test merge를 그 first parent와 비교한다; 모드 step이 그 parent를 fetch하지 못하면 `base.sha..merge`로 되돌아가 그 사이 `main`이 한 bump까지 포함된다 — 모드 step의 "merge parent … not fetchable" 줄을 확인. |
| `pointer` 모드에서만 suite gate red | 기록된 pointer가 sub-repo 작업보다 뒤처짐(모든 feature 브랜치, 그리고 pointer bump 전의 미러에서 예상되는 상태); merge 후 상태가 clean한지는 `branch-tip` run이 알려준다. 모드와 이유는 job summary에 있다. |
| Job이 시작되지 않음 (queued) | 이 host에서 잘못된 변형이 실행됨 — job `if:` host guard 확인; ghes는 `self-hosted` runner가 필요. |
| 두 변형 모두 `startup_failure`, 0초, job 0개 ("workflow file issue") | repo의 Actions 정책이 `local_only`여서 `actions/checkout` / `actions/setup-python`이 차단됨 — GitHub 소유 action 허용 (§5.1 1번). |
| dx_app/dx_stream 작업이 `dev`에 있는 동안 `main` `push` run이 red | 해당 변경이 `main`에 도달할 때까지 예상된 상태. *Run workflow*에 `submodule_refs='dx_app=dev dx_stream=dev'`로 main + dev 뷰 실행(실패 run의 How-to-fix step이 dispatch 또는 안내). |
| 테스트에서 `error: unknown switch 'b'`(git init) / `extractall() got an unexpected keyword argument 'filter'` | runner image가 Ubuntu 20.04: git 2.25, Python 3.8.10. 테스트 코드는 `git init -b`·`tarfile.extractall(filter=)`를 쓰면 안 되며, 이제 `test_py38_compat.py`가 로컬에서 잡아낸다. |
| `runtime`(또는 특정 sub-repo)만 `test_all_four_workflows_identical_modulo_path` / gate workflow 테스트에 실패 | 그 sub-repo의 통합 브랜치(`main`, dx_app/dx_stream은 `dev`)에 workflow 변경이 아직 안 들어옴 — 해당 repo의 `feature/dx-agent-dev` PR을 merge(또는 `submodule_refs='dx-runtime=feature/dx-agent-dev'`로 미리보기). |
| `test_suite_url_derivation`이 `git@…`를 기대했는데 `https://…`가 나옴 | runner의 git 설정에 `url.<https>.insteadOf git@…`가 있음(credential manager / CI image). 수정됨: `subrepo_check.sh`는 `git remote get-url` 대신 설정값 `remote.origin.url`로 suite URL을 도출. |
| self-hosted runner에서 `deps MISSING` | runner image에 `python3-jinja2 python3-yaml python3-pytest python3-rich`를 설치하거나 내부 PyPI mirror 제공. |
| e2e monitor test에서 `NameError: name 'Table' is not defined` | gate의 Python에 `rich`가 없음 — `harness_gate.sh deps`가 검사하는 항목이므로 deps 재실행 / `rich>=13` 설치. |
| drift-check step의 `TypeError: 'type' object is not subscriptable` (또는 임의의 `Traceback`) | generator crash — **drift가 아니므로** 재생성하지 말 것. 실제 사례(run 982): Python 3.8 runner가 guard 없는 `dict[str, …]` annotation에서 실패. 2026-09-10부터 generator는 3.8-clean(`test_py38_compat.py`가 보장)이고 `subrepo_check.sh`는 crash를 exit 2로 보고. runner의 `python3 --version`(>= 3.8)과 suite branch에 수정이 포함됐는지 확인. |

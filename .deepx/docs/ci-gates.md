# dx-agent-dev CI Gates — harness-gate and subrepo-gate across GHES, the mirror and the public channel

This guide covers the two CI gates that protect the dx-agent-dev harness
(`.deepx/` canonical source → generated `CLAUDE.md` / `AGENTS.md` / `.claude` /
`.github` / `.cursor` / `.opencode`), how they run in each of the three hosting
environments, the exact commands they execute, how to reproduce them locally,
and how to onboard or verify each environment.

## 1. The three environments

| Environment | Host | Repos | Runner | Token secret | Workflow files that run |
|---|---|---|---|---|---|
| Closed-network GHES (development) | `gh.deepx.ai/deepx/*` | private | `self-hosted` (already registered) | `GH_DCI_TOKEN` (already present) | `*-ghes.yml` |
| Mirror (github.com) | `github.com/deepx-dhyang/*` | private | GitHub-hosted `ubuntu-latest` (no self-hosted runners) | `GC_DCI_TOKEN` — fine-grained PAT, *Contents: Read-only* on dx-all-suite, dx-runtime, dx-compiler, dx_app, dx_stream (must be added by an admin) | `*-cloud.yml` |
| Public channel (end users) | `github.com/DEEPX-AI/*` | public | GitHub-hosted `ubuntu-latest` | none (`github.token` can read public repos) | `*-cloud.yml` |

Both variants of a gate live side by side in the internal repos. Each job has a
host guard — `if: github.server_url != 'https://github.com'` (ghes) or
`== 'https://github.com'` (cloud) — so on any host exactly one of the pair runs
and the other is skipped instantly (no runner is ever queued for it). The mirror
is a git mirror of GHES and therefore receives both files; the guard is what
keeps the ghes file from waiting forever on a self-hosted queue that does not
exist there.

Nothing in either gate needs an NPU or a coding CLI: the drift check, the EN/KO
lint, pytest (conformance + generator tools + e2e unit tests) and the
`run_model_eval.sh --dry-run` shell tests are pure Python. That is why the
github.com variants use GitHub-hosted `ubuntu-latest` even where self-hosted
runners are also connected.

## 2. Files

| Gate | Job / required-check name | Where | Files |
|---|---|---|---|
| Suite gate | `harness-gate` | dx-all-suite | `.github/workflows/dx-agent-dev-gate-ghes.yml`, `.github/workflows/dx-agent-dev-gate-cloud.yml` |
| Sub-repo gate | `subrepo-gate` | dx-compiler, dx-runtime, dx-runtime/dx_app, dx-runtime/dx_stream (each) | `.github/workflows/dx-agent-dev-subrepo-gate-ghes.yml`, `.github/workflows/dx-agent-dev-subrepo-gate-cloud.yml` |
| Shared script (suite gate) | — | dx-all-suite | `.deepx/tools/scripts/harness_gate.sh` |
| Shared script (sub-repo gate) | — | dx-all-suite | `.deepx/tools/scripts/subrepo_check.sh` (reference: `tools/scripts/README.md` §3) |

Removed on 2026-09-08 and replaced by the pairs above: `dx-agent-dev-gate.yml` and `gh-drift-check.yml` (suite), `dx-agent-dev-subrepo-gate.yml` (sub-repos).

The two files of a pair differ only in `runs-on`, the token secret, the host
guard, the Python bootstrap step and the header comment. Everything that decides
pass/fail is identical — the conformance tests
`test_suite_gate_workflows.py::test_ghes_and_cloud_share_the_same_stage_commands`
and `test_subrepo_gate_workflows.py::test_ghes_and_cloud_differ_only_in_expected_places`
enforce this.

## 3. What each gate runs — exact commands

### 3.1 Suite gate (`harness-gate`)

Trigger: `pull_request`, `push` to `main` / `staging*` / `feature/**`,
`workflow_dispatch` (input `mode`: `branch-tip` (default) or `pointer`).

**Mode selection** (step `mode`, decided by `.deepx/tools/scripts/gate_mode.sh`):

| Situation | Event | Range inspected | Mode |
|---|---|---|---|
| `update-submodule.yml` commits `ci(<date>): Update dx-runtime` and pushes to `main` | `push` | `github.event.before` .. `github.sha` | submodule gitlink changed → **`pointer`** (validate the recorded combination) |
| A developer pushes `.deepx/` changes to a feature branch | `push` | `before` .. `sha` | no gitlink change → **`branch-tip`** |
| A PR that only touches `.deepx/` / docs / workflows | `pull_request` | merge commit's first parent (current base tip) .. merge commit | no gitlink change → **`branch-tip`** — even when `main` bumped pointers after `base.sha` |
| A PR that bumps a submodule pointer by hand | `pull_request` | merge commit's first parent .. merge commit | gitlink changed → **`pointer`** |
| Manual run | `workflow_dispatch` | input `mode` | as chosen (`branch-tip` default) |

The step fetches the base commit with header auth (the checkout is depth 1) and
calls `gate_mode.sh --event … --from <base> --to $GITHUB_SHA`; a missing or
unreachable base (new branch, rewritten history) falls back to `branch-tip` and
says so in the job summary and a `::notice`. The chosen mode and the reason are
written to the run's summary page.

| Step | Command (cwd = suite root) |
|---|---|
| Checkout | `actions/checkout@v4` with `submodules: false`, `fetch-depth: 1`, `persist-credentials: false` |
| Select mode | `bash .deepx/tools/scripts/gate_mode.sh --event <event> --from <base> --to $GITHUB_SHA --input-mode <dispatch input>` → `mode=branch-tip|pointer` (see *Mode selection* above) |
| Init required submodules | `git -c http.extraheader="AUTHORIZATION: basic <base64 of x-access-token:TOKEN>" submodule update --init --depth 1 -- dx-runtime dx-compiler`, then the same with `-C dx-runtime … -- dx_app dx_stream`. In `branch-tip` mode, for each of the 4: `ls-remote --heads origin <branch>` (same name as the suite branch, else the remote default branch) → `fetch --depth 1 origin <branch>` → `checkout --detach FETCH_HEAD` |
| Python deps | ghes: `bash .deepx/tools/scripts/harness_gate.sh deps` on the system `python3`, falling back to `python3 -m venv .gate-venv && .gate-venv/bin/pip install "jinja2>=3.1" "pyyaml>=6.0" "pytest>=8,<9" "rich>=13"`. cloud: `actions/setup-python@v5` (3.12) → `python -m pip install -e .deepx/tools "pytest>=8,<9" "rich>=13"` → `harness_gate.sh deps` |
| Drift check | `bash .deepx/tools/scripts/harness_gate.sh check` → `bash .deepx/tools/scripts/run_all.sh check` (all 5 levels) |
| EN/KO lint | `bash .deepx/tools/scripts/harness_gate.sh lint` → `bash .deepx/tools/scripts/run_all.sh lint` |
| Tests | `bash .deepx/tools/scripts/harness_gate.sh tests` → `python -m pytest --rootdir=. .deepx/tests/conformance .deepx/tools/tests .deepx/e2e/tests -q --no-header -p no:cacheprovider` |
| Shell tests | `bash .deepx/tools/scripts/harness_gate.sh e2e-sh` → `bash .deepx/e2e/tests/test_run_model_eval.sh` |

Why only four submodules and never `submodules: recursive`: the gate needs
exactly the four repos that carry `.deepx/`. `dx_rt`, `dx_fw`,
`dx_rt_npu_linux_driver` and `dx-modelzoo` are irrelevant to it, and not every
host has all of them (the mirror has no `dx_fw`), so a recursive checkout would
fail for reasons unrelated to the harness.

Why two modes: `pointer` checks the sub-repo commits the suite actually
records — the integration truth — and therefore is red whenever the pointers
lag behind sub-repo work in flight (every feature branch, and any host that
does not bump pointers, such as the mirror). `branch-tip` validates the state
that will exist once the same-name branches are merged, which is what a PR
needs to know. Pointers are checked exactly when they change (gitlink diff) or
when asked for explicitly.

### 3.2 Sub-repo gate (`subrepo-gate`, one per sub-repo)

Trigger: same events as above (no inputs).

| Step | Command (cwd = `$GITHUB_WORKSPACE`) |
|---|---|
| Checkout this repo | `actions/checkout@v4` into `self/`, `fetch-depth: 1`, `persist-credentials: false` |
| Clone the suite | `URL=https://<host>/<owner>/dx-all-suite.git`; `git -c http.extraheader=… ls-remote --heads "$URL" "<branch>"` → same-name branch if it exists (polled for up to `SUITE_BRANCH_WAIT` = 180 s, because the sync tool pushes dx-all-suite after the sub-repos), else the default branch; `git -c http.extraheader=… clone -q --depth 1 --no-recurse-submodules --branch <use> "$URL" suite`; a suite without `subrepo_check.sh` is refused with `::error::` (sync the suite first, re-run) |
| Python deps | ghes: system `python3` must be **>= 3.8** (fail-fast) and import `jinja2` and `yaml`, else `.gate-venv` fallback. cloud: `actions/setup-python@v5` (3.12) → `python -m pip install "jinja2>=3.1" "pyyaml>=6.0"` |
| Drift check | `bash suite/.deepx/tools/scripts/subrepo_check.sh --subrepo-path <dx-compiler \| dx-runtime \| dx-runtime/dx_app \| dx-runtime/dx_stream> --repo-dir "$GITHUB_WORKSPACE/self" --suite-dir "$GITHUB_WORKSPACE/suite"` |
| Cleanup (`if: always()`) | `rm -rf "$GITHUB_WORKSPACE/suite"` (plus `.gate-venv` on ghes) |

Security rules shared by every file: `permissions: contents: read`; the token is
passed with `git -c http.extraheader=…` and never placed in a URL (git would
persist it into `.git/config` on a self-hosted runner); `set -x` is never used;
the job does not run for pull requests from forks
(`github.event.pull_request.head.repo.full_name == github.repository`).

## 4. Reproduce locally (same commands as CI)

From a dx-all-suite checkout with the four sub-repos initialised:

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

`harness_gate.sh` resolves the suite root from its own location, so it can be
called from any directory. Exit codes: 0 pass · 1 a stage failed · 2 usage or
setup error. Drop `--mode worktree` to check the committed HEAD only (what CI sees).

## 5. Onboarding / verifying each environment

### 5.1 Mirror — github.com/deepx-dhyang/*

1. The Actions policy on each of the 5 repos (Settings → Actions → General → *Actions
   permissions*) must allow the GitHub-owned actions the gates use (`actions/checkout@v4`,
   `actions/setup-python@v5`): choose *Allow all actions and reusable workflows*, or
   *Allow deepx-dhyang, and select non-deepx-dhyang, actions and reusable workflows* with
   **Allow actions created by GitHub** ticked. The narrower *Allow deepx-dhyang actions and
   reusable workflows* (`allowed_actions: local_only`) rejects the workflow file itself —
   every run, both variants, ends as `startup_failure` with 0 jobs after 0 s ("This run
   likely failed because of a workflow file issue"). Check with
   `gh api repos/deepx-dhyang/<repo>/actions/permissions --jq .allowed_actions`
   (`all` or `selected` is fine, `local_only` is not).
2. Create a **fine-grained personal access token**: resource owner `deepx-dhyang`,
   repositories `dx-all-suite`, `dx-runtime`, `dx-compiler`, `dx_app`, `dx_stream`,
   repository permission *Contents: Read-only*. Add it as the Actions secret
   **`GC_DCI_TOKEN`** on each of the 5 repos (Settings → Secrets and variables →
   Actions → New repository secret). Without it the private submodule init / suite
   clone fails (`cannot reach …` or an authentication error).
3. Push the branch (the workflow files must exist on the pushed branch). The `push`
   trigger runs `dx-agent-dev gate (cloud)` and, in each sub-repo,
   `dx-agent-dev sub-repo gate (cloud)`; the ghes twins show as *skipped*.
4. Push- and PR-triggered suite runs use `branch-tip` (no gitlink change), so they
   are green as long as the same-name sub-repo branches carry the regenerated files.
   The mirror does **not** bump submodule pointers; a manual `pointer` run there is
   expected to be red until the pointers are bumped:

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

### 5.2 Closed-network GHES — gh.deepx.ai/deepx/*

- `GH_DCI_TOKEN` already exists; Actions and the `self-hosted` runners are already registered.
- The self-hosted runner image must provide `python3` **>= 3.8** (the ASIC pool's Ubuntu 20.04 runners ship exactly 3.8, which is the gate's floor) with `jinja2`, `pyyaml`, `pytest` and `rich`
  importable (`apt install python3-jinja2 python3-yaml python3-pytest python3-rich`, or a venv);
  `rich` is imported by `.deepx/e2e/e2e_monitor.py` / `e2e_runner.py`, whose unit tests are part of the gate. If they are
  missing the job tries `python3 -m venv .gate-venv` + `pip install` — that only works with an
  internal PyPI mirror — and otherwise fails with an explicit `::error::` naming the packages.
- The ghes variant never downloads a Python toolchain (`actions/setup-python` is used by the
  cloud variant only); `actions/checkout@v4` is bundled with GHES.
- Verify from a host inside the closed network (`gh auth login --hostname gh.deepx.ai`):

```bash
gh workflow run "dx-agent-dev gate (ghes)" -R deepx/dx-all-suite --ref <branch>
gh run list -R deepx/dx-all-suite --workflow "dx-agent-dev gate (ghes)" -L 3
for R in dx-compiler dx-runtime dx_app dx_stream; do
  gh workflow run "dx-agent-dev sub-repo gate (ghes)" -R deepx/$R --ref <branch>
done
```

### 5.3 Public channel — github.com/DEEPX-AI/*

`.github/workflows/` is listed in every repo's `.github/release-excluded`, so the
release export (`public-release.yml` → `deepx/do_workflows-central`) never copies
workflow files — that is also what keeps the public-only `gh-cloud-*.yml` files
alive across exports. Consequently the **cloud** gate files are placed on the
public repos **by hand**, exactly like `gh-cloud-*.yml`:

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

Never copy a `*-ghes.yml` file to a public repo. When a cloud gate file changes
internally, repeat the copy. No token is needed on the public repos: the suite
and all four sub-repos are public there, so `github.token` suffices.

## 6. Required status checks

On each repo: Settings → Branches (or Rules → Rulesets) → protect `main` /
`staging*` → *Require status checks to pass* → add **`harness-gate`** (suite) or
**`subrepo-gate`** (sub-repos). The job names are identical in both variants, so
one required-check entry covers whichever variant runs on that host. Always
reference the job name, never the workflow name (the workflow names differ:
`dx-agent-dev gate (ghes)` vs `dx-agent-dev gate (cloud)`).

### Validating `main` against work that is still on `dev` — `submodule_refs`

dx_app and dx_stream integrate on `dev`; dx-runtime and dx-all-suite integrate on `main`.
A `push` run on suite `main` therefore checks the sub-repos' own `main` (branch-tip) and
stays red until the dx_app/dx_stream changes reach their `main` — that is expected, not drift.
To see the **main + dev integration view** run the gate manually:

- UI: Actions → *dx-agent-dev gate (ghes|cloud)* → **Run workflow** → branch `main`,
  `mode = branch-tip`, `submodule_refs = dx_app=dev dx_stream=dev`
- CLI: `gh workflow run dx-agent-dev-gate-ghes.yml -R gh.deepx.ai/deepx/dx-all-suite --ref main -f mode=branch-tip -f submodule_refs='dx_app=dev dx_stream=dev'`

`submodule_refs` pins the named sub-repos (`dx-runtime dx-compiler dx_app dx_stream`) to the
given branch; the others follow the normal same-name rule. It requires `mode=branch-tip`, and a
branch that does not exist fails the init step with `::error::`. When a `push` run on `main`
fails, the *How to fix* step tries to dispatch exactly this follow-up run (needs a token with
`actions:write`; `GH_DCI_TOKEN` / `GC_DCI_TOKEN`) and otherwise prints the two commands above.
Locally the same view is `git -C dx-runtime/dx_app checkout dev && git -C dx-runtime/dx_stream checkout dev`
in a `main` checkout, then `bash .deepx/tools/scripts/harness_gate.sh all`.

## 7. When a gate is red

| Symptom | Fix |
|---|---|
| `MISSING:` / `CHANGED:` lines (drift) | From a suite checkout on the same branch: `bash .deepx/tools/scripts/run_all.sh generate && bash .deepx/tools/scripts/run_all.sh check`, then commit the regenerated files in the affected repo(s). Never hand-edit `CLAUDE.md` / `AGENTS.md` / `.claude` / `.github` / `.cursor` / `.opencode`. |
| `[ERROR] … EN exceeds KO` (lint) | Add or extend `.deepx/templates/fragments/ko/<stem>.md`, regenerate. |
| pytest failures | Reproduce with `bash .deepx/tools/scripts/harness_gate.sh tests`; conformance tests name the offending file. |
| `cannot reach https://…/dx-all-suite.git (auth/network)` or `Authentication failed` | Missing/expired `GC_DCI_TOKEN` (mirror) or `GH_DCI_TOKEN` (GHES); on the public channel this means the suite repo is not public. |
| `fatal: … dx_fw` or another unrelated submodule | The gate only inits four submodules; a `recursive` checkout or a `git submodule status --recursive` was re-introduced — restore the explicit init step / the four-path listing. On a self-hosted runner the *Reset the reused workspace* step must run before checkout (it wipes submodule trees other jobs left behind). |
| `pointer` mode chosen although the PR touched no submodule | `gate_mode.sh` compares the test merge with its first parent; if the mode step could not fetch that parent it falls back to `base.sha..merge`, which includes bumps `main` made in between — check the "merge parent … not fetchable" line in the mode step. |
| Suite gate red in `pointer` mode only | The recorded pointers lag the sub-repo work (expected on every feature branch and on the mirror until pointers are bumped); the `branch-tip` run tells you whether the merged state is clean. The mode and reason are in the job summary. |
| Job never starts (queued) | The wrong variant ran on this host — check the job `if:` host guard; ghes needs a `self-hosted` runner. |
| `startup_failure`, 0 s, 0 jobs, both variants ("workflow file issue") | The repo's Actions policy is `local_only` and blocks `actions/checkout` / `actions/setup-python` — allow GitHub-owned actions (§5.1 step 1). |
| `push` run on `main` red while dx_app/dx_stream work is on `dev` | Expected until those reach `main`. Run the main + dev view: *Run workflow* with `submodule_refs='dx_app=dev dx_stream=dev'` (the failed run's How-to-fix step dispatches or prints it). |
| `error: unknown switch 'b'` (git init) / `extractall() got an unexpected keyword argument 'filter'` in tests | The runner image is Ubuntu 20.04: git 2.25 and Python 3.8.10. Test code must not use `git init -b` or `tarfile.extractall(filter=)`; `test_py38_compat.py` now fails locally on such constructs. |
| Only `runtime` (or one sub-repo) fails `test_all_four_workflows_identical_modulo_path` / gate-workflow tests | That sub-repo's integration branch (`main`, or `dev` for dx_app/dx_stream) has not received the workflow update yet — merge its `feature/dx-agent-dev` PR (or preview with `submodule_refs='dx-runtime=feature/dx-agent-dev'`). |
| `test_suite_url_derivation` expects `git@…` but got `https://…` | The runner's git config has `url.<https>.insteadOf git@…` (credential manager / CI image). Fixed: `subrepo_check.sh` derives the suite URL from the configured `remote.origin.url`, not from `git remote get-url`. |
| `deps MISSING` on a self-hosted runner | Install `python3-jinja2 python3-yaml python3-pytest python3-rich` on the runner image or provide an internal PyPI mirror. |
| `NameError: name 'Table' is not defined` in e2e monitor tests | `rich` is missing from the gate's Python — it is part of `harness_gate.sh deps`; re-run deps / install `rich>=13`. |
| `TypeError: 'type' object is not subscriptable` (or any `Traceback`) in the drift-check step | The generator crashed — **not drift**, do not regenerate. Cause seen in the wild (run 982): a Python 3.8 runner hit an un-guarded `dict[str, …]` annotation; the generator is 3.8-clean since 2026-09-10 (`test_py38_compat.py` guards it) and `subrepo_check.sh` now exits 2 for a crash. Check `python3 --version` on the runner (>= 3.8) and that the suite branch carries the fix. |

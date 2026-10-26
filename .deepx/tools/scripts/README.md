# `.deepx/tools/scripts/` — Operational Scripts

> Shell scripts that orchestrate the `dx-agent-gen` generator across all 5
> dx-all-suite repos, install git hooks, and run the self-improving E2E loop.

---

## 1. Contents

| Script | Purpose |
|--------|---------|
| `run_all.sh` | Run `dx-agent-gen <action>` across all 5 repos in dx-all-suite |
| `subrepo_check.sh` | Run the generator's drift check from inside a standalone sub-repo checkout (used by CI's sub-repo gate) |
| `harness_gate.sh` | The suite CI gate (`harness-gate`) as one command set — `deps\|check\|lint\|tests\|e2e-sh\|all` — for CI and local use |
| `gate_mode.sh` | Suite gate mode decision: `branch-tip` unless the push/PR range changed a submodule gitlink (→ `pointer`) or dispatch asked for it |
| `install-hooks.sh` | Install the pre-commit drift+lint hook into suite root and all submodules |
| `pre-commit-hook.sh` | The pre-commit hook itself — invoked by git, not by users |
| `run-e2e-improvement-loop.sh` | Self-improving E2E loop (4 CLIs in parallel + auto-fix) |
| `README_RUN_E2E_IMPROVEMENT_LOOP.md` (+ KO) | Detailed guide for the E2E loop |

---

## 2. `run_all.sh` — Multi-Repo Wrapper

Runs a `dx-agent-gen` action across all 5 repos in dx-all-suite (suite root +
dx-compiler + dx-runtime + dx-runtime/dx_app + dx-runtime/dx_stream).

### Usage

```bash
# From the suite root:
bash .deepx/tools/scripts/run_all.sh generate
bash .deepx/tools/scripts/run_all.sh check
bash .deepx/tools/scripts/run_all.sh lint
```

### When to use

| Situation | Command |
|-----------|---------|
| You edited a shared fragment under `.deepx/templates/fragments/` | `generate` (propagate to all 5 repos) |
| You want to verify no repo has drift before pushing | `check` |
| You added/edited a fragment and want to verify EN/KO parity everywhere | `lint` |
| Single-repo workflow (just your current repo) | Use `dx-agent-gen <action>` directly, not `run_all.sh` |

### Exit code

- Returns 0 if all 5 repos succeed
- Returns 1 if any repo fails (the script continues through all repos and
  reports per-repo status, so you see all failures at once)

### Internals

The script iterates a fixed list of repo paths and invokes the generator via
its Python module entry point (so it works even before the CLI shim is on
`PATH`):

```python
from dx_agent_dev_gen.cli import main
sys.exit(main(['<action>', '--repo', '<repo>']))
```

---

## 3. `subrepo_check.sh` — Sub-Repo Drift Gate

The `dx-agent-gen` generator and the shared fragments it renders from
(`.deepx/templates/fragments`) exist ONLY at the dx-all-suite root, so a
standalone sub-repo checkout (dx-compiler, dx-runtime, dx_app, dx_stream — as
CI sees a PR) cannot run `dx-agent-gen check` on itself: there is no suite
tree above it to find the fragments in. `subrepo_check.sh` bridges that gap —
it acquires a suite checkout (an existing one via `--suite-dir`, or a fresh
shallow clone) and builds a disposable "shell" tree (`$WORK/suite/.deepx` as a
symlink to the real suite's `.deepx`, plus a copy of the sub-repo at its
canonical nested path) so the generator's fragment lookup succeeds. This lets
CI catch `.deepx/` drift at sub-repo commit/PR time instead of only when the
suite bumps its submodule pointers.

### Usage

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

### Typical invocations

| Context | Command |
|---------|---------|
| CI (sub-repo gate workflow) | `bash suite/.deepx/tools/scripts/subrepo_check.sh --subrepo-path dx-compiler --repo-dir "$GITHUB_WORKSPACE/self" --suite-dir "$GITHUB_WORKSPACE/suite"` |
| Local, from a suite checkout (same branch) | `bash .deepx/tools/scripts/subrepo_check.sh --subrepo-path dx-compiler --repo-dir /path/to/dx-compiler --suite-dir . --mode worktree` |
| Standalone sub-repo clone (no suite checkout at hand) | `bash .deepx/tools/scripts/subrepo_check.sh --subrepo-path dx-compiler` (default: clones the same-name branch of dx-all-suite, falling back to its default branch if that branch doesn't exist) |

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Clean — generated files match `.deepx/` sources (and, with `--strict-validator`, `validate_framework.py` also passed) |
| 1 | Drift detected (`dx-agent-gen check` reported `MISSING:`/`CHANGED:`), or `--strict-validator` was set and `validate_framework.py` failed |
| 2 | Setup/usage/tool error — bad `--subrepo-path`, missing/unreachable suite, `python3` missing or older than 3.8, or the generator itself crashed (a `Traceback` / rc ≥ 2 is reported as **NOT drift** — nothing to regenerate; fix the tool/runner). |

### When it fails

From a suite checkout on the **same branch** as the sub-repo, with the
sub-repo at its canonical position inside that tree:

```bash
bash .deepx/tools/scripts/run_all.sh generate
bash .deepx/tools/scripts/run_all.sh check   # must be clean
```

Then commit the regenerated files in the sub-repo. A sub-repo checkout can
never fix this on its own — the generator and shared fragments live only in
dx-all-suite.

### Validator

`validate_framework.py` (when present in the sub-repo) runs after the drift
check and is **non-blocking by default** — a failure prints a `WARNING` but
does not affect the exit code. Pass `--strict-validator` to make its failures
fatal (exit 1).

### Caller workflow

Invoked by `.github/workflows/dx-agent-dev-subrepo-gate-{ghes,cloud}.yml` (job
`subrepo-gate`), present in each of the 4 sub-repos (dx-compiler, dx-runtime,
dx-runtime/dx_app, dx-runtime/dx_stream). See §8 "Related Documents" — the
top-level `.deepx/README.md` and `dx-agent-dev-overview.md` describe how this
gate relates to the suite-level `dx-agent-dev-gate-{ghes,cloud}.yml` (`harness-gate`).

---

## 3b. `harness_gate.sh` — Suite Gate, Locally

The suite-level CI gate (`harness-gate`, `.github/workflows/dx-agent-dev-gate-{ghes,cloud}.yml`)
runs every check through this script, so the same command set reproduces on a
developer machine — a green `harness_gate.sh all` locally means a green gate in CI.

### Usage

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

The suite root is resolved from the script's own location, so it can be called
from any directory.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | All requested stages passed |
| 1 | A stage failed (or `deps` found python < 3.8 / a missing module) |
| 2 | Usage / setup error (unknown stage, bad `--python`) |

See [`../../docs/ci-gates.md`](../../docs/ci-gates.md) for the CI side (runners,
tokens, per-environment onboarding).

---

## 4. `install-hooks.sh` — One-Time Pre-Commit Setup

Installs `pre-commit-hook.sh` into every git hooks directory so commits are
blocked on drift or EN/KO fragment lint failures.

### Usage

```bash
# From the suite root, run ONCE per clone:
bash .deepx/tools/scripts/install-hooks.sh
```

### What it does

Copies `pre-commit-hook.sh` to:

| Hook Location | Repo |
|---------------|------|
| `.git/hooks/pre-commit` | dx-all-suite root |
| `.git/modules/dx-compiler/hooks/pre-commit` | dx-compiler (submodule) |
| `.git/modules/dx-runtime/hooks/pre-commit` | dx-runtime (submodule) |
| `.git/modules/dx-runtime/modules/dx_app/hooks/pre-commit` | dx_app (nested submodule) |
| `.git/modules/dx-runtime/modules/dx_stream/hooks/pre-commit` | dx_stream (nested submodule) |

If a pre-commit hook already exists at any location, the script writes
`pre-commit.dx-agent-gen` instead and prints instructions to chain it from
your existing hook.

### Skipping the hook (when needed)

```bash
git commit --no-verify   # Bypass all hooks
```

Use only when you understand the drift consequences (e.g., a WIP commit).

---

## 5. `pre-commit-hook.sh` — Drift + Lint Guard

Run automatically by git on every `git commit`. Performs three checks:

### Check 1: Staged-file scope warning

If both `.deepx/` files and non-`.deepx/` files are staged in the same commit,
prints a warning listing the non-`.deepx/` files. This is informational — the
commit still proceeds — but is meant to catch unintended `git add -A` of
unrelated changes.

### Check 2: Drift check (per repo touched by the commit)

For each repo whose `.deepx/` is in scope:

```bash
dx-agent-gen check --repo <repo>
```

If any repo reports drift, the commit is **blocked** with instructions:

```
ERROR: Generated files out-of-date in <repo>

Fix: dx-agent-gen generate --repo <repo>
  or: .deepx/tools/scripts/run_all.sh generate
```

### Check 3: EN/KO fragment parity lint (when `.deepx/` files are staged)

For each repo with staged `.deepx/` changes:

```bash
dx-agent-gen lint --repo <repo>
```

If lint reports `[ERROR]` (missing KO counterpart, KO too short, Korean text
in EN file), the commit is **blocked**.

### Skip the hook

```bash
git commit --no-verify
```

---

## 6. `run-e2e-improvement-loop.sh` — Self-Improving E2E Loop

Runs the agent-driven E2E tests across all 4 CLIs (Copilot, Cursor, OpenCode, Claude
Code) in parallel, generates a comparison report, and applies auto-improvements
via an orchestrator agent. Then repeats.

This is a long-running orchestration script (multiple hours per iteration) and
has its own detailed guide:

- EN: [`README_RUN_E2E_IMPROVEMENT_LOOP.md`](README_RUN_E2E_IMPROVEMENT_LOOP.md)
- KO: [`README_RUN_E2E_IMPROVEMENT_LOOP-KO.md`](README_RUN_E2E_IMPROVEMENT_LOOP-KO.md)

### Quick reference

```bash
# Standard run (5 iterations, suite scenario)
bash .deepx/tools/scripts/run-e2e-improvement-loop.sh

# Background run with custom iteration cap
bash .deepx/tools/scripts/run-e2e-improvement-loop.sh --max-iterations 10 &

# Resume from the latest run
bash .deepx/tools/scripts/run-e2e-improvement-loop.sh --resume

# Pick a different orchestrator
bash .deepx/tools/scripts/run-e2e-improvement-loop.sh --orchestrator copilot
```

See the dedicated README for option details, stop conditions, and orchestrator
selection.

---

## 7. Operational Recipes

### After editing a shared fragment

```bash
# 1. Propagate to all 5 repos
bash .deepx/tools/scripts/run_all.sh generate

# 2. Verify no drift
bash .deepx/tools/scripts/run_all.sh check

# 3. Verify EN/KO parity
bash .deepx/tools/scripts/run_all.sh lint

# 4. Commit (hook also runs check + lint as a safety net)
git add .deepx/ CLAUDE.md AGENTS.md CLAUDE-KO.md AGENTS-KO.md \
        .github/ .claude/ .cursor/ .opencode/
git commit -m "fragments: <description>"
```

### Fresh-clone setup

```bash
git clone <suite-url>
cd dx-all-suite
git submodule update --init --recursive
pipx install --force --editable .deepx/tools   # PEP 668-safe
bash .deepx/tools/scripts/install-hooks.sh
bash .deepx/tools/scripts/run_all.sh check   # sanity check
```

### When the pre-commit hook blocks you

```bash
# Usually means a fragment was edited without re-running the generator
bash .deepx/tools/scripts/run_all.sh generate
git add -p   # review what generator changed
git commit
```

---

## 8. Related Documents

| Topic | Document |
|-------|----------|
| `dx-agent-gen` package (CLI internals) | [`../README.md`](../README.md) |
| Top-level `.deepx/` index | [`../../README.md`](../../README.md) |
| Fragment authoring rules | [`../../docs/fragment-authoring-guide.md`](../../docs/fragment-authoring-guide.md) |
| Internal SWE process gates | embedded in CLAUDE.md / AGENTS.md (fragment: `swe-process-gates-internal-dev`) |
| Sub-repo gate caller workflow | `.github/workflows/dx-agent-dev-subrepo-gate-{ghes,cloud}.yml` (per sub-repo) |
| Suite-level integration gate | `.github/workflows/dx-agent-dev-gate-{ghes,cloud}.yml` (job `harness-gate`, suite root) |

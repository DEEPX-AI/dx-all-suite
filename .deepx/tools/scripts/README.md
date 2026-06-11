# `.deepx/tools/scripts/` — Operational Scripts

> Shell scripts that orchestrate the `dx-agent-gen` generator across all 5
> dx-all-suite repos, install git hooks, and run the self-improving E2E loop.

---

## 1. Contents

| Script | Purpose |
|--------|---------|
| `run_all.sh` | Run `dx-agent-gen <action>` across all 5 repos in dx-all-suite |
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

## 3. `install-hooks.sh` — One-Time Pre-Commit Setup

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

## 4. `pre-commit-hook.sh` — Drift + Lint Guard

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

## 5. `run-e2e-improvement-loop.sh` — Self-Improving E2E Loop

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

## 6. Operational Recipes

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
pip install -e .deepx/tools
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

## 7. Related Documents

| Topic | Document |
|-------|----------|
| `dx-agent-gen` package (CLI internals) | [`../README.md`](../README.md) |
| Top-level `.deepx/` index | [`../../README.md`](../../README.md) |
| Fragment authoring rules | [`../../docs/fragment-authoring-guide.md`](../../docs/fragment-authoring-guide.md) |
| Internal SWE process gates | embedded in CLAUDE.md / AGENTS.md (fragment: `swe-process-gates-internal-dev`) |

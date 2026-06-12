# Frontier Model Comparison Eval — Runbook (status snapshot)

> **Purpose of this worktree (`dx-all-suite-frontier-eval`)**: when a new frontier model ships,
> use `e2e_runner` (autopilot E2E execution) + `agent_analyzer` (analysis) to **compare its
> performance against the existing frontier model** and generate a report.
>
> This document is a *status snapshot (runbook)* that captures the standard procedure for running
> a comparison eval **without code changes**, plus the path/labeling caveats you must know. (Not a
> generator-managed file — standalone doc.) Korean version: `reference-KO.md`.
>
> Written: 2026-06-12 · Reference code: `.deepx/e2e/e2e_runner.py`, `.deepx/e2e/agent_analyzer/`

---

## 0. At a glance — one comparison cycle

To compare a new model `NEW` against an existing model `OLD`, drive the two tools in this order:

```
①  e2e_runner.py  (N rounds, model OLD)   →  run_id = RID_OLD
②  e2e_runner.py  (N rounds, model NEW)   →  run_id = RID_NEW
③  analyze.py --run-id RID_OLD            →  report dir REP_OLD
④  analyze.py --run-id RID_NEW            →  report dir REP_NEW
⑤  build_comparison.py  REP_OLD vs REP_NEW  →  comparison.html  (side-by-side delta)
```

> Key principle: **"swap the model" at the run level.** Never mix multiple models inside a single
> run (model labels get blended and you hit the §6 caveat). One model → one run → one run_id → one
> analysis report is the canonical shape.

---

## 1. Tool locations

| Tool | Path | Role |
|------|------|------|
| E2E runner | `.deepx/e2e/e2e_runner.py` | Runs autopilot E2E (6 scenarios) for N rounds across 5 CLI agents |
| Run wrapper | `.deepx/e2e/test.sh` | Invokes the actual `agent-driven-e2e-<tool>-autopilot` tests |
| Analyzer | `.deepx/e2e/agent_analyzer/analyze.py` | Per-run_id scoring + report generation |
| Comparison report | `.deepx/e2e/agent_analyzer/build_comparison.py` | Side-by-side delta of two analysis report dirs |
| Analyzer deep doc | `.deepx/e2e/agent_analyzer/README.md` | Full pipeline / metrics / score formulas |

5 target tools: `claude-code` · `copilot-cli` · `cursor-cli` · `opencode-cli` · `codex-cli`
6 scenarios: `compiler` · `dx_app` · `dx_stream` · `cascaded` · `runtime` · `suite`

---

## 2. STEP 1·2 — E2E execution (`e2e_runner.py`)

### 2.1 How to pin the model (the heart of frontier comparison)

Per-tool flags are translated internally into env vars injected into the autopilot session
(`e2e_runner.py:1896` `_MODEL_ENV_MAP`):

| CLI flag | Translated env var | Target tool |
|----------|--------------------|-------------|
| `--claude-model X`   | `DX_AGENT_E2E_CLAUDE_CODE_MODEL=X` | claude-code |
| `--copilot-model X`  | `DX_AGENT_E2E_MODEL=X`             | copilot-cli |
| `--codex-model X`    | `DX_AGENT_E2E_MODEL=X`             | codex-cli |
| `--opencode-model X` | `DX_AGENT_E2E_OPENCODE_MODEL=X`    | opencode-cli |
| `--cursor-model X`   | `DX_AGENT_E2E_CURSOR_MODEL=X`      | cursor-cli |

> ⚠ **copilot and codex share the same `DX_AGENT_E2E_MODEL`.** You cannot pin different models for
> both tools in a single invocation (conflict). Split the invocations to evaluate both.
>
> Model id format differs per tool: the claude CLI uses hyphens (`claude-opus-4-8`), copilot uses
> dots (`claude-opus-4.8`). cursor effectively only exposes `auto` (unsuitable for pinned comparison
> → §6).

### 2.2 Selecting the tool scope (`--tools`)

Narrow the scope to the situation (varies per request):

```bash
# (a) all 5 tools, as before
python .deepx/e2e/e2e_runner.py --rounds 5

# (b) copilot only
python .deepx/e2e/e2e_runner.py --rounds 5 --tools copilot-cli

# (c) claude-code only
python .deepx/e2e/e2e_runner.py --rounds 5 --tools claude-code
```

### 2.3 Actual invocation for model comparison (e.g. opus46 vs opus48 in copilot)

```bash
# run A — existing model
python .deepx/e2e/e2e_runner.py --rounds 5 --tools copilot-cli \
    --copilot-model claude-opus-4.6
#   → prints [model override] DX_AGENT_E2E_MODEL=claude-opus-4.6, assigns a run_id

# run B — new model
python .deepx/e2e/e2e_runner.py --rounds 5 --tools copilot-cli \
    --copilot-model claude-opus-4.8
```

To compare in claude-code:

```bash
python .deepx/e2e/e2e_runner.py --rounds 5 --tools claude-code --claude-model claude-opus-4-6
python .deepx/e2e/e2e_runner.py --rounds 5 --tools claude-code --claude-model claude-opus-4-8
```

### 2.4 Frequently used options

| Option | Meaning |
|--------|---------|
| `--rounds N` | Round (repeat) count. Usually 5+ for variance |
| `--parallel` | Run tools concurrently (default is sequential — more accurate duration) |
| `--thinking` | High-reasoning mode (claude/copilot `--effort xhigh`, opencode `--variant high`, codex `reasoning_effort=xhigh`; cursor unsupported) |
| `--status` / `--list` | Progress / list of past runs |
| `--stop --run-id <id>` | **Graceful stop** (finishes current round then exits — preserves partial data). Preferred over `--abort` |
| `--resume --run-id <id> --rounds N` | Continue a stopped run to target |
| `--redo-env-failures [--dry-run]` | Detect env-failed rounds (cert/SSL · codex model-refresh · copilot empty-unknown), delete them, reset state for resume |

> Sequential execution should run **round-major** — spreads tool quota walls across rounds and
> enables mid-run partial reports.

### 2.5 Result location (current path)

```
dx-agent-dev/e2e-tests/results/<run_id>/<timestamp_hash>_<tool>-autopilot/
    ├── manifest.json        # exit code, artifacts, timing, applied thinking env
    ├── session.log / session.json
    └── <per-scenario artifacts>   # *_sync.py, factory, *.dxnn, pipeline.py, config.json ...
runner_state/<run_id>/state.json   # per-tool progress / timestamps / exit codes
```

(`RESULTS_ROOT = REPO_ROOT/"dx-agent-dev/e2e-tests/results"`, `e2e_runner.py:84`)

---

## 3. STEP 3·4 — Analysis (`analyze.py`)

```bash
cd .deepx/e2e/agent_analyzer

# single run_id → analyzer_reports/<run_id>/<ts>/
python3 analyze.py --run-id <RID_OLD>
python3 analyze.py --run-id <RID_NEW>

# multiple run_ids combined → analyzer_reports/multi_<sha8>/<ts>/  (+ multi_manifest.json)
python3 analyze.py --run-id <RID_OLD> <RID_NEW>

# tool/scenario/round filters
python3 analyze.py --run-id <RID> --tool copilot-cli --round 1 2 3 --scenario compiler dx_app
```

Outputs (per dir): `analysis.{md,html,json}` · `per_session.csv` · `comprehensive_report.{md,html}`
· `dashboard.html` · (optional) `insights.md` · `runnability_report.md` · `hypothesis.json`.

Score dimensions: **Compliance / Quality / Verdict / ExecutionTrace / Runnability → Overall (weighted)**
+ cost (estimated USD). See `agent_analyzer/README.md` for the score formulas and the 8-stage pipeline.

> Default output base: `<suite-root>/dx-agent-dev/e2e-tests/analyzer_reports/...` (`analyze.py:86-87`)

### Model/CLI policy (insights · runnability · hypothesis stages)

- Default (free): all 3 LLM stages use **cursor + `auto`** (subscription, `--insights` default).
- Paid fallback: `--insights copilot --insights-model claude-sonnet-4.6 --insights-allow-paid`.
- Reuse runnability: `--existing-runnability <prev>/runnability_report.md` (cache the slow eval).
- Disable all LLM calls: `--insights off` (quantitative report only).

---

## Durable output (MANDATORY) — archive root
Reports + bundles MUST be written to the durable archive, NOT the gitignored worktree path
(`dx-agent-dev/e2e-tests/...` is lost on worktree cleanup — confirmed prior data loss).
- Archive root: env `DX_MODEL_EVAL_ARCHIVE`, default `$HOME/shared/coding_agent_diff_report`.
- Analyze straight into it: `analyze.py --run-id <RID> --output-dir "$DX_MODEL_EVAL_ARCHIVE/<label>/"`.
- Bundle raw results: `bundle_raw_results.py --results-dir <results/<run_id>> --out "$DX_MODEL_EVAL_ARCHIVE/<label>/raw/"`.
- Do NOT edit `analyze.py`'s built-in default (`DEFAULT_REPORTS_BASE`) — override per-run instead.

---

## 4. STEP 5 — Comparison report (`build_comparison.py`)

Delta between two analysis report dirs (each containing `per_session.csv` + `comprehensive_report.html`).

```bash
python3 build_comparison.py \
  --non-thinking-dir <REP_OLD> \
  --thinking-dir     <REP_NEW> \
  --non-thinking-run-id <RID_OLD> \
  --thinking-run-id     <RID_NEW> \
  --output <out>/comparison.html
```

Output: single HTML — per-tool aggregate delta table (Compliance/Quality/ExecutionTrace/Runnability/
Overall) + per-(tool × scenario) delta table + the two source reports as side-by-side iframes.
CSV aggregation only, no LLM calls.

> ⚠ **Naming caveat**: the flags are named `--non-thinking-dir` / `--thinking-dir`. The tool was
> originally built for a *thinking vs non-thinking* axis, so using it for frontier *model vs model*
> comparison labels the report "Thinking/Non-Thinking". The comparison itself (run A vs run B delta)
> works fine, but the labels won't match intent. → Relabeling the axis to "model vs model" is a
> **separate follow-up** (proceed if the user picks "model vs model comparison flow cleanup").
>
> The past `opus46_vs_opus48` (§5) was built with **multi-run analyze** (combining run_ids into one
> report) instead of build_comparison. Both approaches are valid.

---

## 5. Where to reference past model scores

Existing reports are preserved under `~/shared/coding_agent_diff_report/`, so past model scores can
be referenced.

| Directory | Contents | run_ids (multi_manifest) |
|-----------|----------|--------------------------|
| `20260528-202548_v3-MULTI-15R/` | 5-tool, 15-round combined analysis | `20260521_202016`, `20260522_195812`, `20260526_204111` |
| `20260604-073803_v3-opus46_vs_opus48/` | opus46↔opus48 comparison (copilot) | `20260526_204111`, `20260529_183101`, `20260529_231925`, `20260530_044017` (digest `946422be`) |
| (top-level) `sonnet_vs_opus_report.html`, `nth_vs_th_report.html`, `r8_vs_r9_root_cause.html` | build_comparison-style one-off comparison HTML | — |

Each directory contains `analysis.{md,html,json}` · `per_session.csv` · `comprehensive_report.{md,html}`
· `dashboard.html` · `insights.md` · `runnability_report.{md,html}` · `hypothesis.json`.

---

## 6. ⚠ Known caveats / limitations (confirmed in this status check)

### 6.1 Path slug rebrand (dx-agentic-dev → dx-agent-dev)

- Past sessions used the slug **`dx-agentic-dev`** and the repo path was **`dx-all-suite-full-e2e`**.
  (e.g. past reports contain `.../dx-all-suite-full-e2e/dx-runtime/dx_app/dx-agentic-dev/2026...`, 264 hits)
- **Now everything is generated under `dx-agent-dev/`** for e2e-tests results and reports (this
  worktree: `dx-all-suite-frontier-eval`). The code's `RESULTS_ROOT` / report base are all
  `dx-agent-dev/e2e-tests/`.
- Therefore **paths written in past reports no longer exist if followed verbatim.** Treat past
  reports as *score references only*, and reinterpret paths against the current slug (`dx-agent-dev`).

### 6.2 Model label not reflected in the `model` column (important)

- Inspecting `20260604-073803_v3-opus46_vs_opus48/per_session.csv`, **all 120 rows show
  `model=claude-sonnet-4.6`** (the config default). The real model distinction survives only in the
  session_id directory name (`..._opus46_...`).
- That is, the past comparison *did* split runs per model, but the analyzer's **model detection failed
  to read the actual model from the session and fell back to config `default_models`.** Do not trust
  the CSV `model` column alone to judge "the two models are mixed / identical".
- Run comparisons **split by run_id (= model)** and separately record the run_id ↔ pinned-model mapping
  for safety. (Improving model-detection / exec-scoring accuracy is a separate backlog item.)

### 6.3 Per-tool characteristics

- **cursor-cli**: effectively only exposes `auto` → unsuitable for pinned frontier-model comparison.
  Also no thinking mode.
- **copilot/codex**: share `DX_AGENT_E2E_MODEL` → cannot evaluate both with different models in one call.
- copilot `gpt-4.1` is deprecated. Model id format (hyphen vs dot) differs per tool → rejected on mismatch.

### 6.4 Token/cost semantics

- `input_tokens` means different things per tool (Claude/Cursor=fresh, Copilot/OpenCode=total,
  Codex=includes cached). The analyzer normalizes to fresh before cost estimation. **Relative
  comparison across models within the same tool** is more reliable than absolute cost.

### Raw results are not naively copyable — use bundle_raw_results.py
`results/<run_id>/...` holds SYMLINKS to the real output dirs (`conftest.py:1114`), and the
generated code is scattered across sub-project dirs (`dx-runtime/dx_app/dx-agent-dev/<session>/`,
`dx-compiler/dx-agent-dev/<session>/`, …) per Output Isolation; `manifest.json` stores absolute
paths. A plain `cp` leaves dangling links + stale paths. `bundle_raw_results.py` dereferences
symlinks, gathers the scattered dirs by `manifest.relative_path`, excludes large files
(`.dxnn`/`venv/`/`*.onnx`), and rewrites manifest paths to be bundle-relative.
Best-effort manual alternative (incomplete): `cp -rL --exclude='*.dxnn' …`.

---

## 7. Checklist (per comparison cycle)

- [ ] Fix the `OLD` / `NEW` model ids (per-tool format — mind hyphen/dot)
- [ ] Fix the tool scope (`--tools`: all 5 / copilot / claude-code)
- [ ] Run run A (OLD) and run B (NEW) **separately** → record the 2 run_ids (note run_id ↔ model mapping)
- [ ] `analyze.py --run-id ...` for each run_id → 2 reports
- [ ] `build_comparison.py` delta HTML (aware of the label caveat) or multi-run analyze
- [ ] Reference past scores under `~/shared/coding_agent_diff_report/`, reinterpreting paths as `dx-agent-dev`
- [ ] Check for `model` column fallback (§6.2) — attribute models by run_id

# dx-agent-dev E2E Analyzer

> Reusable analysis tool — evaluates autopilot test results in
> `dx-agent-dev/e2e-tests/results/` across **tool × round × scenario** dimensions,
> producing comprehensive reports on HARD GATE compliance, code quality, execution
> traces, runnability, token costs, and overall scores.

---

## 1. Quick Start

### 1.1 Static Analysis (analyze.py)

```bash
cd .deepx/e2e/agent_analyzer

# Analyze all rounds (default: ../results)
python3 analyze.py

# Filter by tool / round / scenario
python3 analyze.py --tool claude-code copilot-cli --round 1 2 3 --scenario compiler dx_app

# Custom results location
python3 analyze.py --results-root /path/to/results --output-dir ./reports/custom-run

# Skip runnability evaluation (faster — reuse existing runnability_report.md)
python3 analyze.py --no-insights-runnability

# Override insights CLI agent / model (paid fallback — copilot uses the dotted id)
python3 analyze.py --insights copilot --insights-model claude-sonnet-4.6 --insights-allow-paid
```

Output files (default: `<suite-root>/dx-agent-dev/e2e-tests/analyzer_reports/<timestamp>/`):
- `analysis.md` — Markdown report (main human-readable output)
- `analysis.html` — HTML version of analysis.md
- `analysis.json` — Machine-readable full data
- `per_session.csv` — Flat table for spreadsheet import
- `comprehensive_report.md` — Unified report (analysis + insights + runnability)
- `comprehensive_report.html` — HTML version with Chart.js interactive charts (Executive Summary + visual comparisons)
- `dashboard.html` — Standalone interactive dashboard (Chart.js — overall ranking, radar, round trends, scenario breakdown)

> **I/O directories**: Tool code lives in `.deepx/e2e/agent_analyzer/` (git tracked).
> Input (results) and output (analyzer_reports) live in `dx-agent-dev/e2e-tests/` (gitignored).
> Tools are deployed to all clones; runtime data stays local.

### 1.2 Agent-Driven Insights (insights.py)

Passes the analysis report to an LLM agent for per-tool strengths/weaknesses analysis
or end-user runnability evaluation.

```bash
# Per-tool strengths/weaknesses insights (Korean markdown)
python3 insights.py --mode insights --report-dir reports/<TS>/ --cli claude

# End-user runnability evaluation on 8 sample sessions
python3 insights.py --mode runnability --report-dir reports/<TS>/ --cli copilot --sample 8

# Exhaustive runnability (all sessions)
python3 insights.py --mode runnability --report-dir reports/<TS>/ --cli copilot --all

# Supported CLI agents: claude / codex / copilot / cursor / opencode
# If a CLI is not installed, the prompt file is saved for manual execution
```

Output:
- `insights_prompt.md` — Prompt sent to agent (saved even on CLI failure)
- `insights.md` — Agent response (top 3 strengths/weaknesses per tool, scenario recommendations, learning patterns)
- `runnability_report.md` — Agent reads session README/setup.sh/run.sh and evaluates end-user runnability

### 1.3 Hypothesis Generation (insights.py)

Generates pre-experiment hypotheses based on external benchmarks (SWE-Bench, Aider,
Artificial Analysis, EvalPlus) by invoking an LLM with a structured prompt.

```bash
# Generate hypothesis.json from the default prompt template
python3 insights.py --mode hypothesis --report-dir reports/<TS>/ --cli copilot \
    --prompt prompts/hypothesis_prompt.md

# Use a pre-built hypothesis.json directly (no LLM call)
python3 insights.py --mode hypothesis --report-dir reports/<TS>/ \
    --prompt my_hypothesis.json

# Via analyze.py (integrated pipeline — Stage 4.5)
python3 analyze.py --hypothesis prompts/hypothesis_prompt.md
```

Output:
- `hypothesis.json` — Structured hypotheses with benchmark references

When `hypothesis.json` exists in the report directory:
- **§0 실험 설계** is enriched with purpose, benchmarks, and hypotheses in `comprehensive_report.md`
- **§8 가설 검증** is added to `insights.md` comparing predictions vs actual data
- **Hypothesis vs Actual chart** appears in `dashboard.html`

### 1.4 CLI Flags Reference

| Flag | Default | Description |
|------|---------|-------------|
| `--results-root` | `dx-agent-dev/e2e-tests/results` | Path to results directory |
| `--config` | `./config.yaml` | Config file path |
| `--output-dir` | `<reports_base>/<timestamp>/` | Report output directory |
| `--tool` | all | Filter by tool (repeatable) |
| `--scenario` | all | Filter by scenario (repeatable) |
| `--round` | all | Filter by round number (repeatable) |
| `--insights` | `auto` | Insights CLI agent: `off`, `auto`, `copilot`, `claude`, `cursor`, `opencode`, `codex` |
| `--no-insights-runnability` | (enabled) | Skip runnability evaluation |
| `--insights-model` | CLI default | Override model for insights agent |
| `--insights-allow-paid` / `--no-insights-allow-paid` | mode-specific | Allow/deny paid models. Default varies by mode: runnability=free, insights/hypothesis=paid. Required when using `--insights-model` with a paid model. |
| `--hypothesis` | none | Path to hypothesis prompt (.md) or pre-built (.json). Generates hypothesis.json via LLM and adds §0/§8 to report |
| `--existing-runnability` | none | Path to existing `runnability_report.md` for incremental evaluation |

### 1.5 Comparison Reports (build_comparison.py)

Generate a side-by-side comparison between two analyzer report directories
(e.g. non-thinking vs thinking mode, baseline vs experimental):

```bash
python3 build_comparison.py \
  --non-thinking-dir <path_to_NT_report_dir> \
  --thinking-dir <path_to_TH_report_dir> \
  --non-thinking-run-id <NT_run_id> \
  --thinking-run-id <TH_run_id> \
  --output <output_dir>/comparison.html
```

Inputs: two analyzer report directories that each contain a `per_session.csv`
and `comprehensive_report.html`.

Output: single HTML page with:
- Per-tool aggregate delta table (5 metrics: Compliance, Quality, ExecutionTrace, Runnability, Overall — values + colored Δ)
- Per-(tool × scenario) delta table (5 tools × 6 scenarios = 30 rows)
- Side-by-side iframes of both source `comprehensive_report.html` files

No LLM calls — pure CSV aggregation. Suitable for visualizing the impact of
prompt/config changes, thinking-mode toggles, or harness fixes.

## 2. Pipeline Stages — What `analyze.py` Does

When you run `python3 analyze.py`, the following stages execute in order:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        analyze.py Pipeline                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Stage 1: Discovery                                                 │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ discover.py: scan results/ directory                 │            │
│  │  → ResultDir (per tool×round) + ScenarioRef (per     │            │
│  │    scenario within each result dir)                  │            │
│  │  → Round numbering by timestamp sort                 │            │
│  │  → JSONL file matching (tool-specific patterns)      │            │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 2: Per-Session Evaluation (for each ScenarioRef)             │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ 2a. session.py: parse transcript + JSONL             │            │
│  │     → sentinel detection, model, duration, tokens,   │            │
│  │       tool calls, premium requests                   │            │
│  │ 2b. compliance.py: HARD GATE checks                  │            │
│  │     → sentinel, isolation, session ID, factory,      │            │
│  │       deliverables, suite dual-dir                   │            │
│  │ 2c. quality.py: static code quality                  │            │
│  │     → py_compile, json parse, bash -n,               │            │
│  │       placeholder/direct-engine penalties             │            │
│  │ 2d. functional.py: verdict inference                  │            │
│  │     → PASS/PARTIAL/FAIL/UNKNOWN per scenario          │            │
│  │ 2e. execution.py: execution trace analysis            │            │
│  │     → session.log + compile_out.log evidence          │            │
│  │                                                       │            │
│  │ ⇒ composite_score() → Overall (4-factor, no Runn)    │            │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 3: Cost Estimation (post-pass)                               │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ cost.py: cross-tool calibration                      │            │
│  │  → copilot-cli tokens/premium ratio → estimate       │            │
│  │    premium counts for opencode/codex                  │            │
│  │  → token × pricing table → estimated USD              │            │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 4: Report Generation                                         │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ report.py: write outputs                              │            │
│  │  → analysis.md + analysis.html                        │  ← (A)   │
│  │  → analysis.json                                      │  ← (B)   │
│  │  → per_session.csv                                    │  ← (C)   │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 4.5: Hypothesis Generation (optional)                    │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ insights.py --mode hypothesis (if --hypothesis)      │        │
│  │  → LLM generates hypotheses from benchmarks          │        │
│  │  → hypothesis.json                                   │ ← (A½) │
│  └─────────────────────────────────────────────────────┘        │
│          ↓                                                      │
│  Stage 5: Runnability Evaluation (on by default; skip with --no-insights-runnability) │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ insights.py --mode runnability                        │            │
│  │  → LLM agent reads session README/setup.sh/run.sh    │            │
│  │  → Scores: Verdict, README, Setup, Run, Verification  │            │
│  │  → runnability_report.md                              │  ← (D)   │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 6: Runnability Merge (rewrites Stage 4 outputs)              │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ runnability_parser.py: parse runnability scores       │            │
│  │  → merge into SessionEval.runnability_score           │            │
│  │  → recompute Overall (5-factor, with Runnability)     │            │
│  │  → REWRITE analysis.md/html/json/csv                  │  ← (A')  │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 7: Qualitative Insights                                      │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ insights.py --mode insights                           │            │
│  │  → LLM agent reads UPDATED analysis.md (with Runn)   │            │
│  │  → Per-tool strengths/weaknesses, recommendations     │            │
│  │  → insights.md                                        │  ← (E)   │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 8: Comprehensive Report Assembly                             │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ Part 0: 실험 설계 (experiment design — always shown;        │            │
│  │         enriched with hypothesis when available)             │            │
│  │ Part 1: Executive Summary (sorted tool rankings)            │            │
│  │ Part 2: analysis.md (quantitative)                          │            │
│  │ Part 3: insights.md (qualitative, with §8 gap if hyp)      │            │
│  │ Part 4: runnability summary (slim)                          │            │
│  │  → comprehensive_report.md                            │  ← (F)   │
│  │  → comprehensive_report.html (with Chart.js charts)   │  ← (G)   │
│  │  → dashboard.html (standalone interactive dashboard)  │  ← (H)   │
│  └─────────────────────────────────────────────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stage Output Summary

| Stage | Output File | Description |
|-------|------------|-------------|
| 4 (A) | `analysis.md` / `analysis.html` | Main quantitative report — per-tool/round/scenario tables, Overall scores |
| 4 (B) | `analysis.json` | Machine-readable full evaluation data |
| 4 (C) | `per_session.csv` | Flat table for spreadsheet import |
| 4.5 (A½) | `hypothesis.json` | Pre-experiment hypotheses from external benchmarks (optional — requires `--hypothesis`) |
| 5 (D) | `runnability_report.md` | LLM agent's end-user runnability evaluation per session |
| 6 (A') | `analysis.md` (rewritten) | Updated with Runnability scores merged into Overall |
| 7 (E) | `insights.md` | LLM agent's qualitative analysis (reads updated analysis.md) |
| 8 (F) | `comprehensive_report.md` | Unified report — experiment design + Executive Summary + Parts 1+2+3+4 |
| 8 (G) | `comprehensive_report.html` | HTML with embedded Chart.js charts (bar, radar, trend, sentinel) |
| 8 (H) | `dashboard.html` | Standalone interactive dashboard (Chart.js — 6 chart types, sortable ranking) |

> **Pipeline ordering matters**: Runnability (Stage 5) runs BEFORE insights (Stage 7)
> so that the qualitative analysis in insights.md reflects the updated Overall scores
> that include Runnability data.
>
> **Stage 5 vs Stage 6 independence**: Stage 6 (merge) triggers whenever
> `runnability_report.md` exists in the output directory — it does **not** check
> whether Stage 5 produced it in the current run. This means you can:
> 1. Skip Stage 5 with `--no-insights-runnability`
> 2. Copy a previous `runnability_report.md` into the output directory
> 3. Re-run the analyzer — Stage 6 will parse and merge the pre-existing file
>
> This is useful for reusing expensive runnability evaluations across report
> regenerations without re-running the LLM evaluation.
>
> **Skip flags**: `--no-insights-runnability` skips Stage 5 only (Stage 6 still
> runs if `runnability_report.md` is present). `--insights off` skips
> Stages 5–7 entirely (report only, no LLM calls).
>
> **Incremental runnability** (`--existing-runnability` / `--existing-report`):
> When adding new rounds to an existing dataset (e.g., rounds 11-20 to a
> 10-round report), pass a previous `runnability_report.md` to skip
> already-evaluated sessions:
> ```bash
> # Via analyze.py (full pipeline — recommended; --insights defaults to cursor)
> python3 analyze.py results/ --insights cursor \
>     --existing-runnability path/to/old/runnability_report.md
>
> # Via insights.py directly
> python3 insights.py --mode runnability --report-dir reports/<ts>/ \
>     --existing-report path/to/old/runnability_report.md
> ```
> The existing report is parsed; sessions with valid evaluations (PASS/PARTIAL/FAIL
> verdict) are skipped. New results are merged with existing sections in the output.
> Session counts reflect `{existing_reused} + {newly_evaluated}` totals.

## 3. Dependencies

- Python 3.10+
- PyYAML (`pip install pyyaml`)
- `bash` (for code quality checks via `bash -n`)

### Running the unit-test suite

All analyzer unit tests live under `tests/` and are wired via `pytest.ini`
(`testpaths = tests`). Run the whole suite with:

```bash
cd .deepx/e2e/agent_analyzer && pytest        # auto-discovers tests/
# or from anywhere:
python -m pytest .deepx/e2e/agent_analyzer/tests/ -q
```

## 4. Default Model Policy

The analyzer uses different default models depending on the stage to balance
cost and quality:

| Stage | Default CLI + Model | Cost | Rationale |
|-------|---------------------|------|-----------|
| Runnability (Stage 5) | **cursor + `auto`** | free (subscription) | one short call per session |
| Insights (Stage 7) | **cursor + `auto`** | free | single large prompt |
| Hypothesis (Stage 4.5) | **cursor + `auto`** | free | single large prompt |

> **Model policy (2026-06):** Default is **cursor + `auto`** (Composer, subscription → free) for all
> three LLM stages — it is now the `--insights` default. A free-vs-paid comparison showed cursor `auto`
> output is **not inferior** to paid sonnet (complete §1–8 insights + §8 hypothesis verification,
> same key conclusions), so free is kept as default.
>
> - **Default (free):** `python analyze.py --run-id ...` → cursor `auto` for all stages. ⚠ cursor
>   runnability is ~24s/call (~slow over 120 sessions) and occasionally times out — add
>   `--existing-runnability <prev>/runnability_report.md` to reuse a prior eval and skip re-judging.
> - **Paid fallback** (cursor unavailable / want max detail): runnability → claude-code +
>   `claude-sonnet-4-6` (hyphens; many small calls OK); insights/hypothesis → copilot +
>   `claude-sonnet-4.6` (dotted). Simplest single command:
>   `--insights copilot --insights-model claude-sonnet-4.6 --insights-allow-paid`.
>   (claude-code `-p` **times out (>900s)** on the single huge insights prompt, so it is NOT used there.)
>
> Notes / gotchas:
> - `invoke_cli` now sets the system **CA bundle** env (`NODE_EXTRA_CA_CERTS` + `--use-system-ca`) and
>   `stdin=DEVNULL` itself, so node CLIs (cursor/copilot/opencode) work headless without the caller
>   exporting env. (Previously cursor failed TLS with `Connection lost, reconnecting`.)
> - copilot `gpt-4.1` (the old free default) was **deprecated** — `Model "gpt-4.1" ... is not available`.
> - cursor model id = `auto` (only id exposed by `agent --list-models`); claude CLI uses hyphens
>   (`claude-sonnet-4-6`); copilot uses the dotted form (`claude-sonnet-4.6`). Mismatched forms are rejected.

Override the CLI/model with `--insights <cli>` + `--insights-model <model>`, and toggle
paid models with `--insights-allow-paid` / `--no-insights-allow-paid` in `analyze.py`
(or `--allow-paid` / `--no-allow-paid` in `insights.py`).

## 5. Analysis Dimensions

### 5.1 Metric Tiers

| Tier | Checks | Implementation |
|------|--------|---------------|
| **T1 Artifacts** | Mandatory files exist (setup.sh, run.sh, README.md, session.log, factory, *_sync.py, config.json, .dxnn, etc.) | `compliance.py` |
| **T2 Syntax** | Python `py_compile`, JSON parse, Bash `bash -n` | `quality.py` |
| **T3 Compliance** | START/DONE sentinel, Session ID format, Output Isolation, IFactory 5-method, suite dual-dir | `compliance.py` |
| **T4 Code Quality** | Placeholder code (TODO/`np.zeros`/commented imports), direct `InferenceEngine.run()` | `quality.py` |
| **T5 Duration** | `result.duration_ms` from stream.jsonl (Claude Code/Cursor) or first/last timestamp delta | `session.py` |
| **T6 Verdict** | Scenario artifact existence → PASS/PARTIAL/FAIL/UNKNOWN | `functional.py` |
| **T7 ExecutionTrace** | Actual command execution evidence in session.log + compile_out.log + success/failure markers | `execution.py` |
| **T9 Bias check** | Cursor "auto" model bias detection (cross-tool metric comparison) | `bias_check.py` |
| **T10 Agent-Driven insight** | Secondary CLI agent call for per-tool strengths/weaknesses + end-user runnability | `insights.py` |
| **T11 Cost** | Token usage → estimated USD cost + premium request estimation via calibration | `cost.py` |

### 5.2 Aggregation Dimensions

- **per tool** (claude-code / copilot-cli / cursor-cli / opencode-cli / codex-cli)
- **per round** (1–N — auto-extends as rounds are added)
- **per scenario** (compiler / dx_app / dx_stream / dx_stream_cascaded / runtime / suite)
- **per model** (config.yaml model overrides — flags non-standard cases like Cursor "auto")

### 5.3 Scoring Formulas

```
Compliance %   = (passed checks / total checks) × 100
Quality %      = syntax_pct − 5 × placeholder_hits − 5 × direct_engine_use  (penalty capped)
Runnability %  = 0.4×Verdict(PASS=100/PARTIAL=50/FAIL=0)
               + 0.2×README(1–5 → 0–100) + 0.2×Setup(1–5 → 0–100)
               + 0.15×Run(1–5 → 0–100) + 0.05×Verification(Y=100/N=0)
Overall %      = 0.25·Compliance + 0.20·Quality + 0.10·Verdict
               + 0.25·ExecutionTrace + 0.15·Runnability
               + 2.5(START) + 2.5(DONE)
```

> **Sessions without Runnability data**: The remaining 4 factors are proportionally
> redistributed (backward compatible).
>
> **Verdict weight 10%**: Only checks file existence, so low weight. Execution (25%)
> and Runnability (15%) carry higher weight as they measure actual functionality.

## 6. Directory Structure

```
agent_analyzer/
├── README.md                 # This document (English)
├── README-KO.md              # Korean version
├── analyze.py                # Main CLI entry — static analysis + report generation
├── insights.py               # Secondary agent-driven CLI call — insights + runnability
├── config.yaml               # Tool/scenario/model/rule definitions (extend without code changes)
├── lib/
│   ├── discover.py           # results/ scan → ResultDir + ScenarioRef, round grouping
│   ├── session.py            # session.md + stream.jsonl parsing (sentinel, model, duration, tokens, tool calls)
│   ├── compliance.py         # HARD GATE checks (sentinel, isolation, factory methods, suite dual-dir)
│   ├── quality.py            # Static code quality (py_compile, JSON, bash -n, regex anti-patterns)
│   ├── functional.py         # Verdict inference (PASS/PARTIAL/FAIL) + LOC count
│   ├── execution.py          # ExecutionTrace — session.log + compile_out.log execution evidence
│   ├── cost.py               # Token → USD cost estimation + premium request calibration
│   ├── runnability_parser.py # Runnability report parsing → per-session quantitative scores
│   ├── bias_check.py         # Cursor auto model bias detection (cross-tool metrics)
│   ├── aggregate.py          # SessionEval + per-tool/round/scenario aggregation + stdev
│   └── report.py             # MD + HTML + JSON + CSV output
└── reports/<timestamp>/      # Output (gitignore recommended)
    ├── analysis.md
    ├── analysis.html
    ├── analysis.json
    ├── per_session.csv
    ├── insights_prompt.md
    ├── insights.md
    ├── runnability_report.md
    ├── comprehensive_report.md
    └── comprehensive_report.html
```

## 7. Adding New Tools / Models

Extend via `config.yaml` only — **no code changes required**.

### 7.1 New Tool (e.g., OpenAI Codex CLI)

```yaml
tools:
  codex-cli:
    dir_suffix: "codex-cli-autopilot"
    artifact_prefix: "codex_cli"
    binary: "codex"
    notes: "OpenAI Codex CLI"
```

Prerequisites:
- Result directory naming: `<timestamp>_<hash>_codex-cli-autopilot`
- manifest.json artifact keys prefixed: `codex_cli__<scenario>`
- Scenario directory contains `<scenario>-codex-session.md` + `*-stream.jsonl` or `*-events-*.jsonl`

### 7.2 Model Mapping Changes

```yaml
default_models:
  codex-cli: "gpt-5.3-codex"

model_overrides:
  - session_id_pattern: "20260601_"
    model: "gpt-5.4-codex"
    note: "GPT-5.4 codex rollout starting Jun 1"
```

### 7.3 New Scenario

```yaml
scenarios:
  benchmark:
    description: "Performance benchmark scenario"
    expected_output_dirs: ["dx-runtime/dx_app"]
    mandatory_files:
      - "setup.sh"
      - "run.sh"
      - "benchmark.py"
      - "results.json"
    file_globs:
      - "**/results.json"
```

## 8. Cumulative Analysis

Round numbering is **automatic**. When new round results appear in `results/`,
they are sorted by timestamp and assigned sequential round numbers.

```bash
# After R1–R10 complete, add R11–R15 → same command for cumulative analysis
python3 analyze.py

# Compare specific round groups
python3 analyze.py --round 1 2 3 4 5      # Initial 5 rounds
python3 analyze.py --round 6 7 8 9 10     # Additional 5 rounds
```

## 9. Token Semantics Per Tool

Each tool reports token usage differently. The analyzer normalizes to "fresh input
tokens" (tokens actually billed) before cost estimation:

| Tool | `input_tokens` meaning | Normalization |
|------|----------------------|---------------|
| **Claude Code** | NEW-only (fresh) | Stored as-is |
| **Cursor CLI** | NEW-only (`tokens.input`) | Stored as-is |
| **Copilot CLI** | TOTAL (new + cache_read + cache_write) | `raw_input − cache_read − cache_write` |
| **OpenCode** | TOTAL (copilot format) | Same as copilot |
| **Codex CLI** | TOTAL (includes cached) | `max(0, input_tokens − cached_input_tokens)` |

> **Premium request estimation**: Copilot CLI reports `premium_requests` directly.
> For other tools using copilot provider (OpenCode, Codex), the analyzer calibrates
> using copilot-cli's observed `tokens-per-premium-request` ratio.

## 10. Methodology — How Scores Are Computed

### Compliance (HARD GATE Checks)

Check items (variable by scenario; up to ~8):

1. `sentinel_start` — `[DX-AGENT-DEV: START]` in first line of response
2. `sentinel_done` — `[DX-AGENT-DEV: DONE (output-dir: ...)]` in last line
3. `output_isolation_present` — Artifacts under `dx-agent-dev/<session_id>/`
4. `session_id_format` — `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` pattern
5. `mandatory_deliverables` — All scenario-required files exist
6. `ifactory_5_methods` — factory in dx_app/runtime/suite implements 5-method pattern
7. `session_log_authentic` — session.log contains real command output (not heredoc)
8. `suite_dual_session_dirs` — suite scenario produces 2 separate sub-project dirs

### Quality (Static Code Quality)

- All `.py` files: `py_compile` → pass rate
- All `.json` files: `json.load` → pass rate
- All `.sh` files: `bash -n` → pass rate
- **Placeholder hits** (penalty): `# TODO: implement`, commented `dx_engine`/`dxnn_sdk` imports, `result = np.zeros(...)`, etc.
- **Direct engine use** (penalty): `engine.run()` / `engine.run_async()` outside factory (HARD GATE violation)
- Penalty: 5 points per hit; cap 30 (placeholder), cap 15 (engine)

### Verdict (Scenario Artifact Inference)

```
Verdict = PASS(100) / PARTIAL(50) / FAIL(0) / UNKNOWN(0)
```

- `compiler` PASS = `.dxnn` + `config.json` / FAIL = no `.dxnn`
- `dx_app` PASS = factory + `*_sync.py` both / PARTIAL = factory only
- `dx_stream` PASS = `pipeline.py` + `run_*.sh` / PARTIAL = pipeline only
- `runtime` PASS = at least one sub-project output validates
- `suite` PASS = both dx-compiler and dx_app have separate dirs (R41 HARD GATE)

### Overall (Composite)

```
Overall = 0.25 × Compliance% + 0.20 × Quality% + 0.10 × Verdict%
        + 0.25 × ExecutionTrace% + 0.15 × Runnability%
        + 2.5(START) + 2.5(DONE)
```

- Capped at 100
- Weights: Compliance(25%) + Execution(25%) > Quality(20%) > Runnability(15%) > Verdict(10%)
- Sentinel bonus: 5 points — markers that automated test infrastructure depends on
- **pytest exit_status NOT included in Overall** — round-level (one round has 6 scenarios; any single assertion failure → exit 1), cannot decompose to scenario-level scores

### Cost Estimation

Token usage is converted to estimated USD using pricing tables in `config.yaml`:

- **Anthropic models** (Claude Sonnet 4.6): input/output/cache_read/cache_write per-million rates
- **Copilot premium requests**: USD per request (Pro tier reference: $0.033/req)
- **Cross-tool calibration**: copilot-cli's observed `tokens/premium-request` ratio is applied to estimate premium request counts for tools that don't report them directly

## 11. Known Limitations / Future Improvements

| Limitation | Current Status |
|-----------|---------------|
| **No functional verification** — `verify.py` NPU execution not tested statically | **Improved**: Verdict column (PASS/PARTIAL/FAIL/UNKNOWN) infers from artifact existence. NPU execution collection available as separate option |
| **Token counting** — Varies per tool | **Improved**: All 5 tools now have normalization (fresh tokens extracted). Codex cached subtraction fixed. See §7 |
| **Equal scenario weights** — compiler vs dx_app difficulty differs | Explicit per-scenario Verdict table + duration provided. Config `weight` activation possible |
| **No visualization** | Tables suffice in console/MD; HTML reports provide styled alternative |
| **Drill-down** | **Improved**: Round × Scenario × Tool Verdict matrix + per-session detail table |
| **Round consistency** | **Improved**: σ(Overall) / σ(Duration) — stdev columns added |
| **Per-scenario pass/fail** | **Improved**: Verdict inference — beyond pytest round-level exit code |
| **Codex CLI dual-JSONL** | **Improved**: Parser handles both `*-stream.jsonl` and `*-events-*.jsonl` patterns |
| **HTML reports** | **Improved**: All MD reports now have HTML counterparts with styled tables |

## 12. License / Ownership

Internal tool. Part of the dx-all-suite `dx-agent-dev` infrastructure. This
directory follows the `.gitignore` policy of the dx-all-suite repo.

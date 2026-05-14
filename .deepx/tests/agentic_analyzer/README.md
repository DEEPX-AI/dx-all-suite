# dx-agentic-dev E2E Analyzer

> Reusable analysis tool — evaluates autopilot test results in
> `dx-agentic-dev/e2e-tests/results/` across **tool × round × scenario** dimensions,
> producing comprehensive reports on HARD GATE compliance, code quality, execution
> traces, runnability, token costs, and overall scores.

---

## 1. Quick Start

### 1.1 Static Analysis (analyze.py)

```bash
cd .deepx/tests/agentic_analyzer

# Analyze all rounds (default: ../results)
python3 analyze.py

# Filter by tool / round / scenario
python3 analyze.py --tool claude-code copilot-cli --round 1 2 3 --scenario compiler dx_app

# Custom results location
python3 analyze.py --results-root /path/to/results --output-dir ./reports/custom-run

# Skip runnability evaluation (faster — reuse existing runnability_report.md)
python3 analyze.py --no-insights-runnability

# Override insights CLI agent / model
python3 analyze.py --insights claude --insights-model claude-sonnet-4.6
```

Output files (default: `<suite-root>/dx-agentic-dev/e2e-tests/analyzer_reports/<timestamp>/`):
- `analysis.md` — Markdown report (main human-readable output)
- `analysis.html` — HTML version of analysis.md
- `analysis.json` — Machine-readable full data
- `per_session.csv` — Flat table for spreadsheet import
- `comprehensive_report.md` — Unified report (analysis + insights + runnability)
- `comprehensive_report.html` — HTML version of comprehensive report

> **I/O directories**: Tool code lives in `.deepx/tests/agentic_analyzer/` (git tracked).
> Input (results) and output (analyzer_reports) live in `dx-agentic-dev/e2e-tests/` (gitignored).
> Tools are deployed to all clones; runtime data stays local.

### 1.2 Agentic Insights (insights.py)

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

### 1.3 CLI Flags Reference

| Flag | Default | Description |
|------|---------|-------------|
| `--results-root` | `dx-agentic-dev/e2e-tests/results` | Path to results directory |
| `--config` | `./config.yaml` | Config file path |
| `--output-dir` | `<reports_base>/<timestamp>/` | Report output directory |
| `--tool` | all | Filter by tool (repeatable) |
| `--scenario` | all | Filter by scenario (repeatable) |
| `--round` | all | Filter by round number (repeatable) |
| `--insights` | `auto` | Insights CLI agent: `off`, `auto`, `copilot`, `claude`, `cursor`, `opencode`, `codex` |
| `--no-insights-runnability` | (enabled) | Skip runnability evaluation |
| `--insights-sample` | 8 | Number of sample sessions for runnability |
| `--insights-all` | false | Evaluate every session (exhaustive runnability) |
| `--insights-model` | CLI default | Override model for insights agent |
| `--insights-allow-paid` | false | Allow paid/billed model selections |

## 2. Dependencies

- Python 3.10+
- PyYAML (`pip install pyyaml`)
- `bash` (for code quality checks via `bash -n`)

## 3. Analysis Dimensions

### 3.1 Metric Tiers

| Tier | Checks | Implementation |
|------|--------|---------------|
| **T1 Artifacts** | Mandatory files exist (setup.sh, run.sh, README.md, session.log, factory, *_sync.py, config.json, .dxnn, etc.) | `compliance.py` |
| **T2 Syntax** | Python `py_compile`, JSON parse, Bash `bash -n` | `quality.py` |
| **T3 Compliance** | START/DONE sentinel, Session ID format, Output Isolation, IFactory 5-method, suite dual-dir | `compliance.py` |
| **T4 Code Quality** | Placeholder code (TODO/`np.zeros`/commented imports), direct `InferenceEngine.run()` | `quality.py` |
| **T5 Duration** | `result.duration_ms` from stream.jsonl (Claude Code/Cursor) or first/last timestamp delta | `session.py` |
| **T6 Verdict** | Scenario artifact existence → PASS/PARTIAL/FAIL/UNKNOWN | `functional.py` |
| **T7 ExecutionTrace** | Actual command execution evidence in session.log + compile_out.log + success/failure markers | `execution.py` |
| **T8 Pytest assertion** | (informational) pytest-json-report data if available; NOT included in Overall | `pytest_data.py` |
| **T9 Bias check** | Cursor "auto" model bias detection (cross-tool metric comparison) | `bias_check.py` |
| **T10 Agentic insight** | Secondary CLI agent call for per-tool strengths/weaknesses + end-user runnability | `insights.py` |
| **T11 Cost** | Token usage → estimated USD cost + premium request estimation via calibration | `cost.py` |

### 3.2 Aggregation Dimensions

- **per tool** (claude-code / copilot-cli / cursor-cli / opencode-cli / codex-cli)
- **per round** (1–N — auto-extends as rounds are added)
- **per scenario** (compiler / dx_app / dx_stream / dx_stream_cascaded / runtime / suite)
- **per model** (config.yaml model overrides — flags non-standard cases like Cursor "auto")

### 3.3 Scoring Formulas

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

## 4. Directory Structure

```
agentic_analyzer/
├── README.md                 # This document (English)
├── README-KO.md              # Korean version
├── analyze.py                # Main CLI entry — static analysis + report generation
├── insights.py               # Secondary agentic CLI call — insights + runnability
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
│   ├── pytest_data.py        # pytest assertion data (json-report parsing, if available)
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

## 5. Adding New Tools / Models

Extend via `config.yaml` only — **no code changes required**.

### 5.1 New Tool (e.g., OpenAI Codex CLI)

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

### 5.2 Model Mapping Changes

```yaml
default_models:
  codex-cli: "gpt-5.3-codex"

model_overrides:
  - session_id_pattern: "20260601_"
    model: "gpt-5.4-codex"
    note: "GPT-5.4 codex rollout starting Jun 1"
```

### 5.3 New Scenario

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

## 6. Cumulative Analysis

Round numbering is **automatic**. When new round results appear in `results/`,
they are sorted by timestamp and assigned sequential round numbers.

```bash
# After R1–R10 complete, add R11–R15 → same command for cumulative analysis
python3 analyze.py

# Compare specific round groups
python3 analyze.py --round 1 2 3 4 5      # Initial 5 rounds
python3 analyze.py --round 6 7 8 9 10     # Additional 5 rounds
```

## 7. Token Semantics Per Tool

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

## 8. Methodology — How Scores Are Computed

### Compliance (HARD GATE Checks)

Check items (variable by scenario; up to ~8):

1. `sentinel_start` — `[DX-AGENTIC-DEV: START]` in first line of response
2. `sentinel_done` — `[DX-AGENTIC-DEV: DONE (output-dir: ...)]` in last line
3. `output_isolation_present` — Artifacts under `dx-agentic-dev/<session_id>/`
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

## 9. Known Limitations / Future Improvements

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

## 10. License / Ownership

Internal tool. Part of the dx-all-suite `dx-agentic-dev` infrastructure. This
directory follows the `.gitignore` policy of the dx-all-suite repo.

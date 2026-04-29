# run-e2e-improvement-loop.sh

Self-improving Agentic E2E test loop. Runs all 4 AI coding tools, generates a comparison report, and applies improvements — then repeats until no actionable improvements remain or the iteration limit is reached.

## How It Works

Each iteration runs these 4 steps:

```
Step 1  Run all 4 autopilot E2E tests in parallel
          copilot / cursor / opencode / claude_code

Step 2  Collect generated artifact listings
          (pipeline.py, session.json, README, run script, etc.)

Step 3  Call Claude → generate comparison report
          iteration-N-report.md  +  iteration-N-report-KO.md

Step 4  Call Claude → apply improvements to test files / SKILL.md
          Followed by: dx-agentic-gen generate (drift guard)
```

**Stop conditions:**
- `no_actionable_improvements` — Claude found nothing new to fix
- `max_iterations_reached` — hit the `--max-iterations` ceiling

Each run is stored in a timestamped directory so multiple runs never overwrite each other.

## Quick Start

```bash
# Standard run (5 iterations max, dx_stream scenario)
bash tools/run-e2e-improvement-loop.sh

# Background run (recommended for long sessions)
bash tools/run-e2e-improvement-loop.sh &
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--max-iterations N` | `5` | Maximum number of iterations |
| `--scenario KEY` | `dx_stream` | pytest `-k` filter applied to all tool tests |
| `--resume` | off | Resume from the latest existing run |
| `--run-dir PATH` | auto | Use a specific run directory instead of auto-timestamped |
| `--orchestrator TYPE` | `claude` | Orchestrator for report+improve steps: `claude`, `copilot`, `cursor`, or `opencode` |
| `--claude-bin PATH` | `claude` | Path to the Claude CLI binary |
| `--copilot-bin PATH` | `copilot` | Path to the Copilot CLI binary |
| `--cursor-bin PATH` | `agent` | Path to the Cursor CLI binary |
| `--opencode-bin PATH` | `opencode` | Path to the OpenCode binary |
| `--model MODEL` | `claude-sonnet-4-6` | Model used for report generation and improvements |
| `--suite-root PATH` | auto-detect | Path to the dx-all-suite root directory |
| `--dry-run` | off | Print commands without executing |
| `-h, --help` | | Show help |

## Output Structure

Each run creates a timestamped subdirectory:

```
doc/reports/e2e-loop/
└── YYYYMMDD-HHMMSS/
    ├── state.json                          — live loop state (iteration, applied list, status)
    ├── LOOP_SUMMARY.md                     — final summary of all applied improvements
    ├── LOOP_SUMMARY-KO.md                  — Korean translation
    ├── iteration-N-copilot-pytest.log      — raw pytest output per tool
    ├── iteration-N-cursor-pytest.log
    ├── iteration-N-opencode-pytest.log
    ├── iteration-N-claude_code-pytest.log
    ├── iteration-N-copilot-pytest.json     — synthesised result (pass/fail/auth_error/quota_error)
    ├── iteration-N-cursor-pytest.json
    ├── iteration-N-opencode-pytest.json
    ├── iteration-N-claude_code-pytest.json
    ├── iteration-N-artifacts.txt           — listing of generated files in dx-agentic-dev/
    ├── iteration-N-context.json            — context passed to Claude for report generation
    ├── iteration-N-report.md               — Claude's comparison report (EN)
    ├── iteration-N-report-KO.md            — Korean translation
    ├── iteration-N-changes.md              — log of changes applied this iteration
    ├── iteration-N-result.json             — Claude's improvement decision (done/applied list)
    └── iteration-N-improve.log             — raw Claude output from improvement step
```

## Common Usage Scenarios

### Run with more iterations

```bash
bash tools/run-e2e-improvement-loop.sh --max-iterations 10
```

### Continue a completed run

`--resume` finds the latest timestamped run directory, loads its `state.json`, and picks up from the next iteration. **Important:** `--resume` alone is not enough if the previous run hit `max_iterations_reached` — you must also raise `--max-iterations` above the current iteration count.

```bash
# Resume latest run, extend to 10 iterations total
bash tools/run-e2e-improvement-loop.sh --resume --max-iterations 10
```

The `improvements_applied` history is preserved, so already-applied items (R1, R2, …) are never re-applied.

### Resume a specific run directory

```bash
bash tools/run-e2e-improvement-loop.sh \
  --run-dir doc/reports/e2e-loop/2026-04-28-175036 \
  --resume \
  --max-iterations 10
```

### Dry run (verify config without running tests)

```bash
bash tools/run-e2e-improvement-loop.sh --dry-run
```

## What `--resume` Does NOT Do

`--resume` does **not** re-use the previous iteration's report. Each resumed iteration always:
1. Re-runs all 4 tool tests from scratch
2. Generates a fresh comparison report from those new results
3. Applies any remaining improvements

The only thing carried over is the `improvements_applied` list (to avoid duplicates).

## Improvement Categories

Claude tags each recommendation with one of these categories:

| Tag | Meaning |
|-----|---------|
| `[test_coverage]` | Add or strengthen test assertions |
| `[runner_code]` | Fix test harness / conftest logic |
| `[skill_md]` | Update SKILL.md templates or rules |
| `[timeout]` | Adjust timeout values |
| `[tooling]` | Account/quota issues — not fixable in code, skipped |

## Stop Reasons

| Reason | Meaning |
|--------|---------|
| `no_actionable_improvements` | Claude applied zero improvements this iteration |
| `max_iterations_reached` | Hit the `--max-iterations` ceiling |
| `report_missing` | Report file was not created (Claude error) |
| `result_not_written` | Result JSON was not written (Claude error) |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ORCHESTRATOR` | Override orchestrator: `claude`, `copilot`, `cursor`, or `opencode` (same as `--orchestrator`) |
| `CLAUDE_BIN` | Override Claude binary path (same as `--claude-bin`) |
| `COPILOT_BIN` | Override Copilot binary path (same as `--copilot-bin`) |
| `CURSOR_BIN` | Override Cursor CLI binary path (same as `--cursor-bin`) |
| `OPENCODE_BIN` | Override OpenCode binary path (same as `--opencode-bin`) |
| `CLAUDE_MODEL` | Override model (same as `--model`) |

## Prerequisites

- `python3` on PATH
- `claude` CLI authenticated (`claude auth login`) — if using `--orchestrator claude` (default)
- `copilot` CLI installed and authenticated — if using `--orchestrator copilot`
- `agent` (Cursor CLI) installed and authenticated — if using `--orchestrator cursor`
- `opencode` CLI installed — if using `--orchestrator opencode`
- `dx-agentic-gen` on PATH (for post-improvement drift guard)
- `tests/test.sh` present in suite root

## Running with Copilot CLI Orchestrator

```bash
# Use Copilot CLI for Steps 3 and 4 (report + improve), while still running all 4 tool E2E tests in Step 1
bash tools/run-e2e-improvement-loop.sh --orchestrator copilot

# Specify explicit binary path
bash tools/run-e2e-improvement-loop.sh --orchestrator copilot --copilot-bin /usr/local/bin/copilot

# Via environment variable
ORCHESTRATOR=copilot bash tools/run-e2e-improvement-loop.sh
```

> **Note:** `--orchestrator` controls which AI CLI runs the **orchestration steps** (report generation and improvement application). The E2E tests in Step 1 always run all 4 tools (copilot/cursor/opencode/claude_code) regardless of this setting.

## Running with Cursor CLI Orchestrator

```bash
# Use Cursor CLI for Steps 3 and 4 (report + improve)
bash tools/run-e2e-improvement-loop.sh --orchestrator cursor

# Specify explicit binary path
bash tools/run-e2e-improvement-loop.sh --orchestrator cursor --cursor-bin /usr/local/bin/agent

# Via environment variable
ORCHESTRATOR=cursor bash tools/run-e2e-improvement-loop.sh
```

> **Note:** The Cursor CLI binary is named `agent`. Ensure it is on PATH or specify the path with `--cursor-bin`.

## Running with OpenCode Orchestrator

```bash
# Use OpenCode for Steps 3 and 4 (report + improve)
bash tools/run-e2e-improvement-loop.sh --orchestrator opencode

# Specify explicit binary path
bash tools/run-e2e-improvement-loop.sh --orchestrator opencode --opencode-bin /usr/local/bin/opencode

# With a specific model (use OpenCode's provider-prefixed model format)
bash tools/run-e2e-improvement-loop.sh --orchestrator opencode --model "anthropic/claude-sonnet-4-5"

# Via environment variable
ORCHESTRATOR=opencode bash tools/run-e2e-improvement-loop.sh
```

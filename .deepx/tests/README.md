# DX-ALL-SUITE Agent-Driven Development Tests

## 📋 Overview

Agent-Driven development test suite for the DX-ALL-SUITE project. These tests validate
the AI coding agent infrastructure and run end-to-end scenarios with multiple CLI tools.

For product tests (docker_install, local_install, getting_started), see [`tests/README.md`](../../tests/README.md).

## ✅ Test Suite Categories

### 1. conformance — Agent-Driven Development Infrastructure Validation
Validates the agent-driven development infrastructure across all 5 project levels (suite, compiler, runtime, dx_app, dx_stream).

**What it tests:**
- Guide document structure: existence, headings, scenario numbering, EN/KO synchronization
- Routing consistency: CLAUDE.md, AGENTS.md, copilot-instructions.md, copilot.json, .cursorrules
- Scenario references: agent/skill references in guides match actual infrastructure
- Cross-project scenarios: handoff chains, validation scripts, output isolation

**Total tests:** ~700 infra checks — run `pytest .deepx/tests/conformance/ --collect-only -q` for the live count. These need no CLI/NPU, so effectively all pass; a few skip when an optional dependency is absent.

### 2. test_agent_e2e_scenarios — Agent-Driven End-to-End Scenario Tests (Copilot CLI + Cursor CLI + OpenCode CLI + Claude Code CLI + Codex CLI)
Runs actual CLI agent invocations for representative scenarios from each project level, then statically verifies the generated output files.

**Modes:** five CLI autopilot modes (pytest) + interactive manual modes (shell).
- **copilot autopilot**: Fully autonomous with `--no-ask-user`. CI/CD optimized. Uses Copilot CLI (`copilot`). Runs via pytest.
- **cursor autopilot**: Fully autonomous via Cursor CLI (`agent -p --force`). Same scenarios and assertions. Runs via pytest.
- **opencode autopilot**: Fully autonomous via OpenCode CLI (`opencode run --format json`). Same scenarios and assertions. Runs via pytest.
- **claude-code autopilot**: Fully autonomous via Claude Code CLI (`claude -p --dangerously-skip-permissions`). Same scenarios and assertions. Runs via pytest.
- **codex autopilot**: Fully autonomous via Codex CLI (`codex exec`). Same scenarios and assertions. Runs via pytest.
- **copilot manual**: Interactive shell-based mode (no pytest). User interacts with Copilot CLI TUI directly, then shell validates output.
- **cursor manual**: Interactive shell-based mode (no pytest). User interacts with Cursor CLI TUI directly, then shell validates output.
- **opencode manual**: Interactive shell-based mode (no pytest). User interacts with OpenCode TUI, types `/export` to save session, then shell validates output.
- **claude-code manual**: Interactive shell-based mode (no pytest). User interacts with Claude Code CLI, types `/export` to save transcript, then shell validates output.

**Output isolation:** Prompts do NOT specify an output directory. Each sub-project's agent configuration (`copilot-instructions.md` for OpenCode, `.cursor/rules/*.mdc` for Cursor) enforces Output Isolation, automatically writing generated files to `dx-agent-dev/<session_id>/`. The test framework auto-detects new session directories by comparing pre/post snapshots of each scenario's search paths.

**What it tests:**
- **dx_app Scenario #1:** Build a yolo26n person detection app (IFactory pattern, config.json, runner)
- **dx_stream Scenario #1:** Build a detection pipeline with tracking (GStreamer elements, RTSP, tracker)
- **dx-compiler Scenario #2:** Generate compilation config for ONNX to DXNN (config.json structure)
- **dx-runtime Scenario #2:** Build standalone detection app via routing (routing verification)
- **dx-all-suite Scenario #2:** Cross-project compile + app generation (both compiler and app artifacts)

**Verification approach:** Static analysis only (file existence, Python syntax via `ast.parse`, JSON structure, required patterns). No actual HW inference.

**Total tests:** ~586 collected across the five CLI autopilot markers (copilot, cursor, opencode, claude-code, codex) — run `pytest .deepx/e2e/test_agent_e2e_scenarios/ --collect-only -q` for the live count; plus shell-based manual modes.

**Markers (pytest only):**
- `pytest.mark.agent_e2e_copilot_cli_autopilot` — Copilot CLI fully autonomous (CI/CD)
- `pytest.mark.agent_e2e_cursor_cli_autopilot` — Cursor CLI fully autonomous (CI/CD)
- `pytest.mark.agent_e2e_opencode_cli_autopilot` — OpenCode CLI fully autonomous (CI/CD)
- `pytest.mark.agent_e2e_claude_code_autopilot` — Claude Code CLI fully autonomous (CI/CD)
- `pytest.mark.agent_e2e_codex_cli_autopilot` — Codex CLI fully autonomous (CI/CD)

## 🔄 E2E Runner & Monitor

Reusable tools for running multiple rounds in parallel and monitoring progress in real time.
Located at `.deepx/e2e/e2e_runner.py` and `.deepx/e2e/e2e_monitor.py`.

### e2e_runner.py

Runs 5 tools for N rounds with state tracking, stop/abort, and resume capabilities.
Tools run **sequentially by default** (one at a time) so per-tool duration metrics
are not skewed by NPU/CPU contention. Pass `--parallel` to fan out across all tools
when throughput matters more than measurement fidelity.

`--rounds` is **required** for actions that launch or resume a run (status/list/
stop/abort/cleanup do not need it).

```bash
# Run all tools for 5 rounds sequentially (default)
python .deepx/e2e/e2e_runner.py --rounds 5

# Parallel mode — fan out across all 5 tools at once
#   → faster wall-clock but per-tool durations include contention overhead
python .deepx/e2e/e2e_runner.py --rounds 5 --parallel

# Run specific tools only
python .deepx/e2e/e2e_runner.py --rounds 5 --tools claude-code,copilot-cli

# Enable thinking / high-reasoning mode (xhigh effort)
python .deepx/e2e/e2e_runner.py --rounds 5 --thinking

# Resume: auto-detect completed rounds, continue to target
python .deepx/e2e/e2e_runner.py --rounds 10 --resume

# Resume a specific previous run
python .deepx/e2e/e2e_runner.py --rounds 10 --resume --run-id 20260521_100000

# List all run IDs
python .deepx/e2e/e2e_runner.py --list

# Show detailed status (mode/per-round/scenario timing)
python .deepx/e2e/e2e_runner.py --status
python .deepx/e2e/e2e_runner.py --status --run-id 20260521_135734

# Graceful stop (finish current round, then exit)
python .deepx/e2e/e2e_runner.py --stop

# Immediate abort (kill processes, remove in-progress artifacts)
python .deepx/e2e/e2e_runner.py --abort
python .deepx/e2e/e2e_runner.py --abort --force   # skip confirmation prompt

# Delete artifacts for specific rounds
python .deepx/e2e/e2e_runner.py --cleanup --round 3
python .deepx/e2e/e2e_runner.py --cleanup --round 3 --tool claude-code
python .deepx/e2e/e2e_runner.py --cleanup --round 2,3,4
```

**Sequential vs Parallel:**

| Mode | Concurrent tools | Use case |
|------|------------------|----------|
| (default) | 1 | Eliminate NPU/CPU contention; accurate per-tool measurement |
| `--parallel` | N (tool count, e.g. 5) | Fast batch throughput |

The runner persists the chosen mode in `state.json` (`"mode": "sequential" | "parallel"`)
and shows it in `--status` output.

**Per-scenario timeouts** (subprocess.run timeout per agent invocation):

| Scenario | Default | Env override |
|----------|---------|--------------|
| compiler           | 1800s (30m) | `DX_TIMEOUT_COMPILER` |
| dx_app             | 900s (15m)  | `DX_TIMEOUT_DX_APP` |
| dx_stream          | 900s (15m)  | `DX_TIMEOUT_DX_STREAM` |
| dx_stream_cascaded | 1200s (20m) | `DX_TIMEOUT_DX_STREAM_CASCADED` |
| runtime            | 1200s (20m) | `DX_TIMEOUT_RUNTIME` |
| suite              | 2400s (40m) | `DX_TIMEOUT_SUITE` |
| (fallback)         | 7200s       | `DX_E2E_TIMEOUT` |

Defaults are tuned for **sequential** baseline durations. Parallel mode may need
longer timeouts due to contention — bump them as needed:
```bash
DX_TIMEOUT_COMPILER=3600 DX_TIMEOUT_SUITE=4800 python .deepx/e2e/e2e_runner.py --rounds 5
```

**Stop & Resume:**

| Command | Behavior | Child processes | In-progress artifacts |
|---------|----------|-----------------|----------------------|
| `--stop` | Graceful — finish current round, then exit | Natural completion | Kept |
| `--abort` | Immediate — kill all now | SIGTERM sent | Deleted |
| `--resume --rounds N` | Continue from completed count to N | — | — |

**Thinking mode** (per-tool env vars):

| Tool | Thinking mode env var |
|---|---|
| `claude-code` | `DX_AGENT_E2E_CLAUDE_CODE_EXTRA_ARGS=--effort xhigh` |
| `copilot-cli` | `DX_AGENT_E2E_COPILOT_EXTRA_ARGS=--effort xhigh` |
| `opencode-cli` | `DX_AGENT_E2E_OPENCODE_EXTRA_ARGS=--variant high` |
| `codex-cli` | `DX_AGENT_E2E_CODEX_EXTRA_ARGS=-c model_reasoning_effort="xhigh"` |
| `cursor-cli` | No thinking mode (quota exceeded; auto fallback) |

**State files** (`.deepx/e2e/runner_state/<run_id>/`):
- `state.json` — round completion status, timing, artifact paths, exit codes, PIDs
- `logs/<tool>.log` — per-tool full stdout/stderr log
- `STOP` / `ABORT` — sentinel files (created by --stop/--abort)
- `latest` symlink — always points to the most recent run

**Resume priority:**
1. `--run-id` specified: load that state.json
2. Not specified: load via `runner_state/latest` symlink
3. Fallback: create a fresh run state (legacy flat results must be converted with
   `migrate_results_to_run_id.py` first)

### results/ Layout (run-id keyed)

Per-round outputs are isolated under a run-id directory so different batches no
longer mix in the same flat namespace:

```
dx-agent-dev/e2e-tests/results/
├── 20260521_135734/                       ← run_id from e2e_runner
│   ├── 20260521_174857_e25076_claude-code-autopilot/
│   │   ├── manifest.json
│   │   ├── SUMMARY.md
│   │   └── ...
│   └── 20260521_155006_824828_copilot-cli-autopilot/
├── 20260520_193327/                       ← a different run
│   └── ...
├── manual/                                ← manual `pytest` invocations (no DX_RUN_ID)
│   └── 20260519_103045_xxxxxx_claude-code-autopilot/
└── legacy/                                ← legacy flat results moved here by migration
    └── 20260511_194755_d31c86_cursor-cli-autopilot/
```

Mechanism: `e2e_runner.py` propagates `DX_RUN_ID=<run_id>` to the subprocess env;
`conftest.py:pytest_sessionfinish` reads it and writes outputs to
`results/<run_id>/<session_id>/`. Manual invocations land under `results/manual/`.

### Migrating Legacy flat results/

```bash
# Dry-run preview
python .deepx/e2e/migrate_results_to_run_id.py

# Apply moves (matched → results/<run_id>/, unmatched → results/legacy/)
python .deepx/e2e/migrate_results_to_run_id.py --apply

# Keep unmatched sessions flat (do not create legacy/)
python .deepx/e2e/migrate_results_to_run_id.py --apply --skip-legacy
```

The migration script reads `runner_state/*/state.json` to build a
`result_dir_name → run_id` map. The analyzer supports both layouts simultaneously,
so migration is recommended but not required.

### e2e_monitor.py

Rich-based Live TUI monitor for real-time runner progress.

```bash
# Monitor latest run (progress table only, no logs)
python .deepx/e2e/e2e_monitor.py

# Monitor specific run
python .deepx/e2e/e2e_monitor.py --run-id 20260521_100000

# Show all tool logs
python .deepx/e2e/e2e_monitor.py --tool all

# Focus on specific tool (logs + scenario timing)
python .deepx/e2e/e2e_monitor.py --tool claude-code --tail 30

# List all run IDs
python .deepx/e2e/e2e_monitor.py --list

# Print snapshot once and exit (no live update)
python .deepx/e2e/e2e_monitor.py --once
```

**`--tool` option:**

| Option | Behavior |
|--------|----------|
| (not specified) | Progress table only, no log panels |
| `--tool all` | Show tail logs for all 5 tools |
| `--tool <name>` | Show that tool's tail log + per-scenario timing |

**Monitor display:**
- Round Progress table: Done / Fail / Remaining / Status / Timing / Scenarios
- Timing column: current round start + elapsed (e.g., `R3 14:30 (42m+)`)
- Scenario icons: ✓(done) ▶(running) ·(pending)
- Log panels (when `--tool` specified): per-tool real-time tail output
- Scenario timing panel (when `--tool <name>`): per-scenario start/end/duration

## 📊 Analyzer Reports (run-id aware)

Generate quantitative + qualitative reports after one or more E2E runs:

```bash
cd .deepx/e2e/agent_analyzer

# Aggregate every run (and legacy flat results)
#   → analyzer_reports/_all/<timestamp>/
python analyze.py

# Single run only
#   → analyzer_reports/<run_id>/<timestamp>/
python analyze.py --run-id 20260521_135734

# Combine multiple runs into one report
#   → analyzer_reports/multi_<sha8>/<timestamp>/  (+ multi_manifest.json listing the inputs)
python analyze.py --run-id 20260521_135734 --run-id 20260520_193327

# Combine with other filters
python analyze.py --run-id 20260521_135734 --tool claude-code --round 1 --round 2
```

**analyzer_reports/ layout:**

```
dx-agent-dev/e2e-tests/analyzer_reports/
├── _all/<timestamp>/                     ← no --run-id (everything aggregated)
├── 20260521_135734/<timestamp>/          ← single --run-id
├── multi_a3f2b1c4/<timestamp>/           ← multiple --run-id (SHA-8 of sorted IDs)
│   └── multi_manifest.json               ← records the run-id inputs
```

**Round indexing:** rounds are numbered per `(run_id, tool)` — `R1` of one run never
collides with `R1` of another. Multi-run reports automatically add a `Run` column to
the per-session detail table.

## 🚀 Quick Start

```bash
cd .deepx/e2e

# Agent-Driven infrastructure validation (~704 tests, ~1 second)
./test.sh agent-driven

# Agent-Driven E2E scenario tests
./test.sh agent-driven-e2e-copilot-cli-autopilot     # Copilot CLI, fully autonomous (CI/CD)
./test.sh agent-driven-e2e-cursor-cli-autopilot      # Cursor CLI, fully autonomous (CI/CD)
./test.sh agent-driven-e2e-opencode-cli-autopilot    # OpenCode CLI, fully autonomous (CI/CD)
./test.sh agent-driven-e2e-claude-code-autopilot     # Claude Code CLI, fully autonomous (CI/CD)
./test.sh agent-driven-e2e-codex-cli-autopilot       # Codex CLI, fully autonomous (CI/CD)
./test.sh agent-driven-e2e-copilot-cli-manual        # Copilot CLI, interactive (shell-based)
./test.sh agent-driven-e2e-cursor-cli-manual         # Cursor CLI, interactive (shell-based)
./test.sh agent-driven-e2e-opencode-cli-manual       # OpenCode CLI, interactive (shell-based)
./test.sh agent-driven-e2e-claude-code-manual        # Claude Code CLI, interactive (shell-based)
./test.sh agent-driven-e2e-codex-cli-manual          # Codex CLI, interactive (shell-based)
```

## 💡 Key Commands

### Test Suite Commands

```bash
./test.sh agent-driven          # Agent-Driven infrastructure (~704 tests, ~1 second)
./test.sh agent-driven-e2e-claude-code-autopilot   # Agent-Driven E2E Claude Code autonomous
./test.sh agent-driven-e2e-copilot-cli-autopilot   # Agent-Driven E2E Copilot CLI autonomous
./test.sh agent-driven-e2e-opencode-cli-autopilot  # Agent-Driven E2E Opencode CLI autonomous
./test.sh agent-driven-e2e-cursor-cli-autopilot    # Agent-Driven E2E Cursor CLI autonomous
./test.sh agent-driven-e2e-codex-cli-autopilot     # Agent-Driven E2E Codex CLI autonomous
./test.sh agent-driven-e2e-claude-code-manual      # Agent-Driven E2E Claude Code interactive
./test.sh agent-driven-e2e-copilot-cli-manual      # Agent-Driven E2E Copilot CLI interactive
./test.sh agent-driven-e2e-opencode-cli-manual     # Agent-Driven E2E OpenCode CLI interactive
./test.sh agent-driven-e2e-cursor-cli-manual       # Agent-Driven E2E Cursor CLI interactive
```

### Marker Filters

```bash
./test.sh -m "agent_e2e_copilot_cli_autopilot"  # Only Copilot CLI agent-driven E2E
./test.sh -m "agent_e2e_cursor_cli_autopilot"   # Only Cursor CLI agent-driven E2E
./test.sh -m "agent_e2e_opencode_cli_autopilot" # Only OpenCode CLI agent-driven E2E
./test.sh -m "agent_e2e_claude_code_autopilot"  # Only Claude Code CLI agent-driven E2E
```

## 🎨 Usage Examples

### Example 1: Agent-Driven E2E — Copilot CLI Autopilot (CI/CD)

```bash
# Run all Copilot CLI E2E tests in autopilot mode (fully autonomous)
./test.sh agent-driven-e2e-copilot-cli-autopilot

# Filter to compiler scenario only
./test.sh agent-driven-e2e-copilot-cli-autopilot -k compiler

# With custom model and extended timeout
DX_AGENT_E2E_TIMEOUT=900 DX_AGENT_E2E_MODEL="claude-opus-4.6" \
  ./test.sh agent-driven-e2e-copilot-cli-autopilot
```

### Example 2: Agent-Driven E2E — Cursor CLI Autopilot (CI/CD)

```bash
# Run all Cursor CLI E2E tests (default model: claude-4.6-sonnet-medium)
./test.sh agent-driven-e2e-cursor-cli-autopilot

# Filter to dx_stream scenario only
./test.sh agent-driven-e2e-cursor-cli-autopilot -k dx_stream

# With different model
DX_AGENT_E2E_CURSOR_MODEL="claude-opus-4-7-thinking-high" \
  ./test.sh agent-driven-e2e-cursor-cli-autopilot
```

### Example 3: Agent-Driven E2E — Copilot CLI Manual (Interactive)

```bash
# Interactive mode — runs Copilot CLI TUI directly (no pytest)
./test.sh agent-driven-e2e-copilot-cli-manual

# Auto-select a specific scenario
./test.sh agent-driven-e2e-copilot-cli-manual -k compiler
./test.sh agent-driven-e2e-copilot-cli-manual -k dx_app
```

### Example 4: Agent-Driven E2E — Cursor CLI Manual (Interactive)

```bash
# Interactive mode — runs Cursor CLI TUI directly (no pytest)
./test.sh agent-driven-e2e-cursor-cli-manual

# Auto-select a specific scenario
./test.sh agent-driven-e2e-cursor-cli-manual -k dx_stream
```

## 🤖 Agent-Driven E2E — Copilot CLI Autonomous Execution

The agent-driven E2E test suite (`test_agent_e2e_scenarios/`) runs real Copilot CLI
sessions against the dx-all-suite codebase. This section explains how autonomous
(auto-approve) execution works.

### Two Execution Modes

| Mode | Entry Point | OpenCode Flags | User Interaction |
|------|-------------|----------------|------------------|
| **Autopilot** | `./test.sh agent-driven-e2e-copilot-cli-autopilot` | `--yolo --no-ask-user -s` | None (fully autonomous) |
| **Manual** | `./test.sh agent-driven-e2e-copilot-cli-manual` | `--yolo` | Interactive TUI |

### Copilot CLI Flags Explained

| Flag | Meaning | When Used |
|------|---------|-----------|
| `--yolo` | Alias for `--allow-all-tools --allow-all-paths --allow-all-urls` — auto-approves ALL tool calls (file writes, bash commands, web fetches) without confirmation prompts | Both modes |
| `--no-ask-user` | Disables the `ask_user` tool so the agent never blocks waiting for user input | Autopilot only |
| `-s` | Silent mode — shows only agent response, no TUI chrome | Autopilot only |
| `-p <prompt>` | Non-interactive prompt mode (agent runs and exits) | Autopilot only |
| `-i <prompt>` | Interactive prompt mode (opens TUI with initial prompt) | Manual only |
| `--share=<file>` | Saves session transcript to a file | Autopilot only |
| `--model <name>` | Selects the LLM model to use | Both modes |

### Autopilot Mode — How It Works

The `CopilotRunnerAutopilot` class in `conftest.py` constructs and executes:

```bash
copilot -p "<prompt> IMPORTANT: This is an automated test run. ..." \
  --yolo \
  --no-ask-user \
  -s \
  --share=<session_log> \
  --model claude-sonnet-4.6
```

Key behaviors:
- **`--yolo`** auto-approves all tool calls — the agent can read/write files,
  run shell commands, and fetch URLs without human confirmation.
- **`--no-ask-user`** prevents the agent from ever asking questions — if it
  encounters an ambiguity, it must decide on its own.
- The **AUTOPILOT_DIRECTIVE** (appended to every prompt) reinforces autonomous
  behavior at the prompt level.
- The session runs with a **timeout** (default 300s, configurable via
  `DX_AGENT_E2E_TIMEOUT`). If the agent exceeds the timeout, the process
  is killed and the test fails.

### Manual Mode — How It Works

Manual mode opens the Copilot TUI directly:

```bash
copilot -i "<prompt>" --yolo --model claude-sonnet-4.6
```

Key behaviors:
- **`--yolo`** still auto-approves tool calls, but the user can interact
  with the agent through the TUI.
- **No `--no-ask-user`** — the agent CAN ask clarifying questions, and the
  user responds via the TUI.
- After the session, `test.sh` runs shell-based validation (file existence,
  syntax checks) on the generated artifacts.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DX_AGENT_E2E_MODEL` | `claude-sonnet-4.6` | LLM model for Copilot CLI |
| `DX_AGENT_E2E_TIMEOUT` | `300` | Timeout in seconds per scenario |
| `DX_AGENT_E2E_CLEANUP_ARTIFACTS` | (unset) | Set to `1` to delete generated `dx-agent-dev/` directories after test run (default: keep) |
| `DX_AGENT_E2E_MODE` | (set by test.sh) | `autopilot` or `manual` — set automatically by `test.sh` |

### Running with Different Models

```bash
# Claude Sonnet 4.6 (recommended)
DX_AGENT_E2E_MODEL="claude-sonnet-4.6" ./test.sh agent-driven-e2e-copilot-cli-autopilot

# GPT-4.1 (not recommended — may fabricate APIs)
DX_AGENT_E2E_MODEL="gpt-4.1" DX_AGENT_E2E_TIMEOUT=600 \
  ./test.sh agent-driven-e2e-copilot-cli-autopilot

# Claude Opus 4.6 (highest quality, slower)
DX_AGENT_E2E_MODEL="claude-opus-4.6" DX_AGENT_E2E_TIMEOUT=900 \
  ./test.sh agent-driven-e2e-copilot-cli-autopilot
```

### Session Output and Artifacts

Each scenario generates artifacts in `dx-agent-dev/<session_id>/` within
the target sub-project. The test framework auto-detects new session directories
by comparing pre/post directory snapshots.

After a test run, artifacts include:
- Generated code files (Python scripts, configs, shell scripts)
- `session.log` — command execution transcript
- Copilot session transcript (saved via `--share=<file>`)
- HTML export (if `test.sh` detects it was generated via `/share html`)

Generated artifacts are preserved by default for debugging.
Set `DX_AGENT_E2E_CLEANUP_ARTIFACTS=1` to delete them after a successful run.

### Differences from Copilot CLI Tests

The Cursor CLI E2E tests (`test_cursor_*_agent_e2e.py`) run the same scenarios as
the Copilot CLI tests, but using the Cursor CLI (`agent`) instead.

---

## 🖥 Agent-Driven E2E — Cursor CLI Autonomous Execution

The Cursor CLI E2E tests (`test_cursor_*_agent_e2e.py`) run the same scenarios as
the Copilot CLI tests, but using the Cursor CLI (`agent`) instead.

### How It Works

The `CursorRunnerAutopilot` class in `conftest.py` constructs and executes:

```bash
agent -p --force --output-format stream-json \
  "<prompt> IMPORTANT: This is an automated test run. ..."
```

Key behaviors:
- **`-p`** (print mode) runs non-interactively — no TUI, agent runs and exits.
- **`--force`** auto-approves all file writes and tool calls (equivalent to
  Copilot's `--yolo`).
- **`--output-format stream-json`** provides structured NDJSON events that are
  parsed for session metadata (session_id, assistant text, duration).
- The **AUTOPILOT_DIRECTIVE** (appended to every prompt) reinforces autonomous
  behavior.
- Rules are loaded from `.cursor/rules/*.mdc` files (Cursor's equivalent of
  `copilot-instructions.md`).

### Running Cursor CLI E2E Tests

```bash
# Run all Cursor CLI scenarios (uses claude-4.6-sonnet-medium by default)
./test.sh agent-driven-e2e-cursor-cli-autopilot

# Filter to specific scenario
./test.sh agent-driven-e2e-cursor-cli-autopilot -k dx_app
./test.sh agent-driven-e2e-cursor-cli-autopilot -k compiler

# With custom model (override default)
DX_AGENT_E2E_CURSOR_MODEL="claude-opus-4-7-thinking-high" \
  ./test.sh agent-driven-e2e-cursor-cli-autopilot

# With extended timeout
DX_AGENT_E2E_CURSOR_TIMEOUT=900 \
  ./test.sh agent-driven-e2e-cursor-cli-autopilot
```

### Environment Variables (Cursor-specific)

| Variable | Default | Description |
|----------|---------|-------------|
| `DX_AGENT_E2E_CURSOR_MODEL` | `claude-4.6-sonnet-medium` | LLM model for Cursor CLI |
| `DX_AGENT_E2E_CURSOR_TIMEOUT` | `300` | Timeout in seconds per scenario |
| `DX_AGENT_E2E_CLEANUP_ARTIFACTS` | (unset) | Set to `1` to delete generated artifacts after a successful run (default: keep) |
| `CURSOR_API_KEY` | (from login) | API key for headless authentication |

### Prerequisites

1. **Install the Cursor CLI:**

```bash
curl https://cursor.com/install -fsS | bash
```

2. **Verify installation:**

```bash
agent --version
```

3. **Authenticate** (required before first run):

```bash
# Interactive browser-based login
agent login

# Or set API key for headless/CI environments
export CURSOR_API_KEY="your-api-key"
```

The test framework automatically checks authentication status before running.
If not authenticated, all Cursor CLI tests are gracefully **skipped** with a
clear message (not failed).

### Available Models

List models supported by your account:

```bash
agent models
```

Common model IDs for E2E testing:

| Model ID | Description | Recommended |
|----------|-------------|-------------|
| `claude-4.6-sonnet-medium` | Claude Sonnet 4.6 1M (default) | Yes — best balance of quality and speed |
| `claude-4.6-opus-high` | Claude Opus 4.6 1M | Highest quality, slower |
| `claude-opus-4-7-thinking-high` | Claude Opus 4.7 1M Thinking | Complex reasoning tasks |
| `composer-2-fast` | Cursor Composer 2 Fast | Fast but lower quality |

### Tested Results (Claude Sonnet 4.6)

| Scenario | Tests | Result | Duration |
|----------|-------|--------|----------|
| **dx_app** | 10/10 | ALL PASSED | ~1.5 min |
| **compiler** | 14/14 | ALL PASSED | ~18 min |
| **dx_stream** | 15/15 | ALL PASSED | ~2.5 min |
| **runtime** | 10/10 | ALL PASSED | ~3 min |
| **suite** | 14/14 | ALL PASSED | ~16 min |
| **Total** | **63/63** | **ALL PASSED** | ~41 min |

### Differences from Copilot CLI Tests

| Aspect | Copilot CLI | Cursor CLI | OpenCode CLI | Claude Code CLI |
|--------|-------------|------------|--------------|-----------------|
| Binary | `copilot` | `agent` | `opencode` | `claude` |
| Auto-approve | `--yolo` | `--force` | Automatic in `run` mode | `--dangerously-skip-permissions` |
| No questions | `--no-ask-user` flag | Prompt directive only | Prompt directive only | Prompt directive only |
| Session log | `--share=<file>` | Parsed from stream-json stdout | Parsed from JSON stdout | Parsed from stream-json stdout |
| Rules file | `copilot-instructions.md` | `.cursor/rules/*.mdc` | `.opencode/agents/` | `CLAUDE.md` / `.claude/agents/` |
| Session events | `~/.copilot/session-state/events.jsonl` | Stream-json NDJSON from stdout | JSON from stdout | Stream-json NDJSON from stdout |
| Output format | Plain text (stdout) | `--output-format stream-json` | `--format json` | `--output-format stream-json` |
| Auth check | Session-based | `agent login` / `CURSOR_API_KEY` | Provider-based (`opencode auth`) | `claude auth status` |
| Export command | `/share html` | N/A (stream-json) | `/export` → `session-*.md` | `/export` → `*.txt` transcript |

---

## 🖥 Agent-Driven E2E — OpenCode CLI Autonomous Execution

The OpenCode CLI E2E tests (`test_opencode_*_agent_e2e.py`) run the same scenarios
using the OpenCode CLI (`opencode`) with structured JSON output.

### How It Works

The `OpenCodeRunnerAutopilot` class in `conftest.py` constructs and executes:

```bash
opencode run --format json --model <model> "<prompt> IMPORTANT: This is an automated test run. ..."
```

Key behaviors:
- **`run`** subcommand runs non-interactively — no TUI, agent runs and exits.
- **`--format json`** provides structured JSON output for session metadata parsing.
- OpenCode auto-approves all tool calls in `run` mode (no explicit flag needed).
- The **AUTOPILOT_DIRECTIVE** (appended to every prompt) reinforces autonomous
  behavior.
- Rules are loaded from `.opencode/agents/` and `copilot-instructions.md`.

### Running OpenCode CLI E2E Tests

```bash
# Run all OpenCode CLI scenarios (uses github-copilot/claude-sonnet-4.6 by default)
./test.sh agent-driven-e2e-opencode-cli-autopilot

# Filter to specific scenario
./test.sh agent-driven-e2e-opencode-cli-autopilot -k dx_app
./test.sh agent-driven-e2e-opencode-cli-autopilot -k compiler

# With custom model
DX_AGENT_E2E_OPENCODE_MODEL="anthropic/claude-opus-4.6" \
  ./test.sh agent-driven-e2e-opencode-cli-autopilot

# With extended timeout
DX_AGENT_E2E_OPENCODE_TIMEOUT=900 \
  ./test.sh agent-driven-e2e-opencode-cli-autopilot
```

### Manual Mode — How It Works

Manual mode opens the OpenCode TUI directly:

```bash
opencode --model <model> --prompt "<prompt>"
```

Key behaviors:
- OpenCode TUI launches with the prompt pre-filled via `--prompt`.
- The user can interact with the agent through the TUI.
- Before exiting, type `/export` to save the session as a Markdown file
  (`session-<session_id>.md`) in the working directory.
- After the session, `test.sh` runs shell-based validation on the generated artifacts.

### Environment Variables (OpenCode-specific)

| Variable | Default | Description |
|----------|---------|-------------|
| `DX_AGENT_E2E_OPENCODE_MODEL` | `github-copilot/claude-sonnet-4.6` | LLM model for OpenCode CLI |
| `DX_AGENT_E2E_OPENCODE_TIMEOUT` | `600` | Timeout in seconds per scenario |
| `DX_OPENCODE_CASCADED_TIMEOUT` | `720` | Timeout for cascaded (multi-session) scenarios |
| `DX_AGENT_E2E_CLEANUP_ARTIFACTS` | (unset) | Set to `1` to delete generated artifacts after a successful run (default: keep) |

### Prerequisites

1. **Install OpenCode CLI:**

```bash
curl -fsSL https://opencode.ai/install | bash
```

2. **Verify installation:**

```bash
opencode --version
```

3. **Configure a provider** (OpenCode uses `provider/model` notation):

```bash
# GitHub Copilot (default for this test suite)
opencode auth github-copilot

# Or set ANTHROPIC_API_KEY for direct Anthropic access
export ANTHROPIC_API_KEY="your-key"
```

### Session Archiving (`/export`)

In manual mode, OpenCode saves the session as `session-<session_id>.md` in the
working directory when the user types `/export`. The test harness automatically
detects and archives this file to the scenario artifact directory.

---

## 🖥 Agent-Driven E2E — Claude Code CLI Autonomous Execution

The Claude Code CLI E2E tests (`test_claude_code_*_agent_e2e.py`) run the same
scenarios using the Claude Code CLI (`claude`) from Anthropic.

### How It Works

The `ClaudeCodeRunnerAutopilot` class in `conftest.py` constructs and executes:

```bash
claude -p --dangerously-skip-permissions --output-format stream-json \
  "<prompt> IMPORTANT: This is an automated test run. ..."
```

Key behaviors:
- **`-p`** (print mode) runs non-interactively — no TUI, agent runs and exits.
- **`--dangerously-skip-permissions`** auto-approves all file writes and bash
  commands (equivalent to Copilot's `--yolo`).
- **`--output-format stream-json`** provides structured NDJSON events parsed
  for session metadata (session_id, assistant text, duration).
- The **AUTOPILOT_DIRECTIVE** (appended to every prompt) reinforces autonomous
  behavior.
- Rules are loaded from `.claude/agents/` and `CLAUDE.md`.
- Authentication is verified via `claude auth status` before each run.
  If not authenticated (exit code 77), all Claude Code tests are gracefully **skipped**.

### Running Claude Code CLI E2E Tests

```bash
# Run all Claude Code CLI scenarios (uses claude-sonnet-4-6 by default)
./test.sh agent-driven-e2e-claude-code-autopilot

# Filter to specific scenario
./test.sh agent-driven-e2e-claude-code-autopilot -k dx_app
./test.sh agent-driven-e2e-claude-code-autopilot -k compiler

# With custom model
DX_AGENT_E2E_CLAUDE_CODE_MODEL="claude-opus-4-6" \
  ./test.sh agent-driven-e2e-claude-code-autopilot

# With extended timeout and cleanup
DX_AGENT_E2E_CLAUDE_CODE_TIMEOUT=900 DX_AGENT_E2E_CLEANUP_ARTIFACTS=1 \
  ./test.sh agent-driven-e2e-claude-code-autopilot -k dx_stream
```

### Manual Mode — How It Works

Manual mode opens the Claude Code CLI:

```bash
claude
```

The user interacts with the Claude Code TUI, providing the prompt manually.
Before exiting, type `/export` to save a TXT transcript
(`YYYY-MM-DD-HHMMSS-<title>.txt`) in the working directory.
After the session, `test.sh` runs shell-based validation on the generated artifacts.

### Environment Variables (Claude Code-specific)

| Variable | Default | Description |
|----------|---------|-------------|
| `DX_AGENT_E2E_CLAUDE_CODE_MODEL` | `claude-sonnet-4-6` | LLM model for Claude Code CLI |
| `DX_AGENT_E2E_CLAUDE_CODE_TIMEOUT` | `600` | Timeout in seconds per scenario |
| `DX_AGENT_E2E_CLAUDE_QUOTA_POLL_INTERVAL` | `3600` | Seconds to wait between quota-limit retries |
| `DX_AGENT_E2E_CLAUDE_QUOTA_MAX_POLLS` | `8` | Max retry polls on quota/rate limit |
| `DX_AGENT_E2E_CLEANUP_ARTIFACTS` | (unset) | Set to `1` to delete generated artifacts after a successful run (default: keep) |

### Prerequisites

1. **Install Claude Code CLI:**

```bash
npm install -g @anthropic-ai/claude-code
```

2. **Verify installation:**

```bash
claude --version
```

3. **Authenticate:**

```bash
# Interactive browser-based login
claude auth login

# Verify auth status
claude auth status
```

### Session Archiving (`/export`)

In manual mode, Claude Code saves a TXT transcript
(`YYYY-MM-DD-HHMMSS-<title>.txt`) in the working directory when the user types
`/export`. The test harness automatically detects and archives this file.

---

## 📊 Expected Execution Time

| Test Suite | Test Count | Expected Time | Use Case |
|-----------|------------|---------------|----------|
| **agent-driven** | ~704 | ~1 second | Agent-Driven infrastructure validation |
| **agent_e2e (copilot-cli)** | ~114 | ~30-45 minutes | Agent-Driven E2E Copilot CLI scenario tests |
| **agent_e2e (cursor-cli)** | ~113 | ~40-45 minutes | Agent-Driven E2E Cursor CLI scenario tests (Claude Sonnet 4.6) |
| **agent_e2e (opencode-cli)** | ~116 | ~45-60 minutes | Agent-Driven E2E OpenCode CLI scenario tests |
| **agent_e2e (claude-code-cli)** | ~116 | ~45-60 minutes | Agent-Driven E2E Claude Code CLI scenario tests |
| **agent_e2e (codex-cli)** | ~116 | ~45-60 minutes | Agent-Driven E2E Codex CLI scenario tests |

## 🔧 Environment Variables

```bash
# Agent-Driven E2E test configuration (Copilot CLI)
export DX_AGENT_E2E_TIMEOUT=900           # Copilot CLI timeout in seconds (default: 300)
export DX_AGENT_E2E_MODEL="claude-opus-4.6"       # OpenCode model to use (default: claude-sonnet-4.6)
# export DX_AGENT_E2E_CLEANUP_ARTIFACTS=1  # Delete artifacts after successful run (default: keep)

# Agent-Driven E2E test configuration (Cursor CLI)
export DX_AGENT_E2E_CURSOR_MODEL="claude-4.6-sonnet-medium"  # Cursor model (default: claude-4.6-sonnet-medium)
export DX_AGENT_E2E_CURSOR_TIMEOUT=300    # Cursor CLI timeout in seconds (default: 300)
export CURSOR_API_KEY="your-api-key"        # API key for headless/CI (alternative to 'agent login')

# Agent-Driven E2E test configuration (OpenCode CLI)
export DX_AGENT_E2E_OPENCODE_MODEL="github-copilot/claude-sonnet-4.6"  # OpenCode model (default)
export DX_AGENT_E2E_OPENCODE_TIMEOUT=600  # OpenCode CLI timeout in seconds (default: 600)
export DX_OPENCODE_CASCADED_TIMEOUT=720     # OpenCode cascaded scenario timeout (default: 720)

# Agent-Driven E2E test configuration (Claude Code CLI)
export DX_AGENT_E2E_CLAUDE_CODE_MODEL="claude-sonnet-4-6"  # Claude Code model (default)
export DX_AGENT_E2E_CLAUDE_CODE_TIMEOUT=600  # Claude Code CLI timeout in seconds (default: 600)
```

## 🔄 E2E Runner & Monitor

Reusable tools for running multi-round E2E tests and monitoring progress.
Located at `.deepx/e2e/e2e_runner.py` and `.deepx/e2e/e2e_monitor.py`.

### e2e_runner.py

Runs all 5 tools for N rounds with state tracking and resume support.
**Sequential by default**; pass `--parallel` for concurrent execution.
`--rounds` is required when starting or resuming a run.

```bash
# Run 5 rounds for all tools sequentially (default)
python .deepx/e2e/e2e_runner.py --rounds 5

# Parallel mode (one thread per tool — original behavior)
python .deepx/e2e/e2e_runner.py --rounds 5 --parallel

# Run for specific tools only
python .deepx/e2e/e2e_runner.py --rounds 5 --tools claude-code,copilot-cli

# Enable thinking / high-reasoning mode (xhigh effort)
python .deepx/e2e/e2e_runner.py --rounds 5 --thinking

# Resume: auto-detect completed rounds and continue to target
python .deepx/e2e/e2e_runner.py --rounds 10 --resume

# Resume a specific previous run by ID
python .deepx/e2e/e2e_runner.py --rounds 10 --resume --run-id 20260521_100000

# Show status of the latest run
python .deepx/e2e/e2e_runner.py --status

# Delete artifacts for a specific round
python .deepx/e2e/e2e_runner.py --cleanup --round 3
python .deepx/e2e/e2e_runner.py --cleanup --round 3 --tool claude-code
python .deepx/e2e/e2e_runner.py --cleanup --round 2,3,4
```

**Thinking mode** per tool:

| Tool | Thinking mode env var |
|---|---|
| `claude-code` | `DX_AGENT_E2E_CLAUDE_CODE_EXTRA_ARGS=--effort xhigh` |
| `copilot-cli` | `DX_AGENT_E2E_COPILOT_EXTRA_ARGS=--effort xhigh` |
| `opencode-cli` | `DX_AGENT_E2E_OPENCODE_EXTRA_ARGS=--variant high` |
| `codex-cli` | `DX_AGENT_E2E_CODEX_EXTRA_ARGS=-c model_reasoning_effort="xhigh"` |
| `cursor-cli` | No thinking mode (quota fallback to auto) |

**State files** are stored under `.deepx/e2e/runner_state/<run_id>/`:
- `state.json` — round completion status, artifact dirs, exit codes
- `logs/<tool>.log` — full stdout/stderr per tool
- `latest` symlink — always points to the most recent run

**Resume logic:**
1. If `--run-id` given: load that state.json
2. Otherwise: load via `runner_state/latest` symlink
3. Fallback: scan `dx-agent-dev/e2e-tests/results/` and build state from existing dirs

### e2e_monitor.py

Live TUI monitor (using `rich`) to watch runner progress in real-time.

```bash
# Watch latest run (live TUI, updates every 3 seconds)
python .deepx/e2e/e2e_monitor.py

# Watch a specific run
python .deepx/e2e/e2e_monitor.py --run-id 20260521_100000

# Focus on one tool's log
python .deepx/e2e/e2e_monitor.py --tool claude-code --tail 30

# Print snapshot once and exit (no live update)
python .deepx/e2e/e2e_monitor.py --once
```

**Monitor layout:**
- Round Progress table: Done / Fail / Remaining / Status / Last result dir
- Log panels: tail output of currently running tools (up to 3 side-by-side)
- Timeline: new result dirs as they appear in `results/`

---

## 🔄 CI/CD Integration

### Recommended CI/CD Strategy

**Pull Request (Fast Feedback):**
```bash
./test.sh agent-driven                     # Agent-Driven infrastructure (~1 sec)
```

**Main/Develop Branch (Comprehensive):**
```bash
./test.sh agent-driven-e2e-copilot-cli-autopilot    # Agent-Driven E2E Copilot CLI scenarios
./test.sh agent-driven-e2e-cursor-cli-autopilot     # Agent-Driven E2E Cursor CLI scenarios
```

## 📁 File Structure

```
.deepx/
├── tests/                          # ← suite conformance (this README)
│   ├── conftest.py                 # marker registration + collect_ignore
│   └── conformance/                # KB / generated-output policy checks (~700, no CLI/NPU)
│       ├── conftest.py             # ProjectInfra/GuidePair, path constants, helpers
│       ├── test_guide_structure.py · test_routing_consistency.py
│       ├── test_scenario_references.py · test_instruction_sync.py
│       ├── test_sdk_grounding.py · test_forbidden_patterns.py
│       └── test_cross_project_scenarios.py · test_e2e_suite_structure.py
│
├── e2e/                            # ← end-to-end harness (sections above)
│   ├── e2e_runner.py · e2e_monitor.py · migrate_results_to_run_id.py · _cli_env.py · test.sh
│   ├── runner_state/               # per-run state (auto-created, gitignored)
│   ├── test_agent_e2e_scenarios/ # ~586 across 5 CLIs — conftest + test_<cli>_<scenario>.py
│   ├── agent_analyzer/           # run-id-aware result analyzer (lib/ + tests/)
│   └── tests/test_e2e_runner_env_redo.py
│
└── tools/                          # ← tooling packages (see tools/README.md)
    ├── src/{dx_agent_dev_gen, dx_transcripts}     # generator + shared transcript lib
    └── tests/{dx_agent_dev_gen, dx_transcripts}   # mirrors src/
```

> The session parsers + transcript renderer (`parse_*_session`,
> `generate_transcripts`, …) now live in the `dx_transcripts` package under
> `.deepx/tools/src/` (shared by the sentinel, the e2e harness, and the analyzer).

---

**Total Agent-Driven Tests:**
~1279 (agent-driven: ~704 | agent_e2e_copilot_cli: ~114 | agent_e2e_cursor_cli: ~113 | agent_e2e_opencode_cli: ~116 | agent_e2e_claude_code_cli: ~116 | agent_e2e_codex_cli: ~116) — run `pytest --collect-only -q` for live counts

# DX-ALL-SUITE Agentic Development Tests

## 📋 Overview

Agentic development test suite for the DX-ALL-SUITE project. These tests validate
the AI coding agent infrastructure and run end-to-end scenarios with multiple CLI tools.

For product tests (docker_install, local_install, getting_started), see [`tests/README.md`](../../tests/README.md).

## ✅ Test Suite Categories

### 1. test_agentic_scenarios — Agentic Development Infrastructure Validation
Validates the agentic development infrastructure across all 5 project levels (suite, compiler, runtime, dx_app, dx_stream).

**What it tests:**
- Guide document structure: existence, headings, scenario numbering, EN/KO synchronization
- Routing consistency: CLAUDE.md, AGENTS.md, copilot-instructions.md, copilot.json, .cursorrules
- Scenario references: agent/skill references in guides match actual infrastructure
- Cross-project scenarios: handoff chains, validation scripts, output isolation

**Total tests:** 199 (186 passed, 13 skipped)

### 2. test_agentic_e2e_scenarios — Agentic End-to-End Scenario Tests (Copilot CLI + Cursor CLI + OpenCode CLI + Claude Code CLI)
Runs actual CLI agent invocations for representative scenarios from each project level, then statically verifies the generated output files.

**Six modes:**
- **copilot autopilot**: Fully autonomous with `--no-ask-user`. CI/CD optimized. Uses Copilot CLI (`copilot`). Runs via pytest.
- **cursor autopilot**: Fully autonomous via Cursor CLI (`agent -p --force`). Same scenarios and assertions. Runs via pytest.
- **opencode autopilot**: Fully autonomous via OpenCode CLI (`opencode run --format json`). Same scenarios and assertions. Runs via pytest.
- **claude-code autopilot**: Fully autonomous via Claude Code CLI (`claude -p --dangerously-skip-permissions`). Same scenarios and assertions. Runs via pytest.
- **copilot manual**: Interactive shell-based mode (no pytest). User interacts with Copilot CLI TUI directly, then shell validates output.
- **cursor manual**: Interactive shell-based mode (no pytest). User interacts with Cursor CLI TUI directly, then shell validates output.
- **opencode manual**: Interactive shell-based mode (no pytest). User interacts with OpenCode TUI, types `/export` to save session, then shell validates output.
- **claude-code manual**: Interactive shell-based mode (no pytest). User interacts with Claude Code CLI, types `/export` to save transcript, then shell validates output.

**Output isolation:** Prompts do NOT specify an output directory. Each sub-project's agent configuration (`copilot-instructions.md` for OpenCode, `.cursor/rules/*.mdc` for Cursor) enforces Output Isolation, automatically writing generated files to `dx-agentic-dev/<session_id>/`. The test framework auto-detects new session directories by comparing pre/post snapshots of each scenario's search paths.

**What it tests:**
- **dx_app Scenario #1:** Build a yolo26n person detection app (IFactory pattern, config.json, runner)
- **dx_stream Scenario #1:** Build a detection pipeline with tracking (GStreamer elements, RTSP, tracker)
- **dx-compiler Scenario #2:** Generate compilation config for ONNX to DXNN (config.json structure)
- **dx-runtime Scenario #2:** Build standalone detection app via routing (routing verification)
- **dx-all-suite Scenario #2:** Cross-project compile + app generation (both compiler and app artifacts)

**Verification approach:** Static analysis only (file existence, Python syntax via `ast.parse`, JSON structure, required patterns). No actual HW inference.

**Total tests:** 67 (copilot) + 63 (cursor) + 112 (opencode) + 110 (claude-code) = 352 (pytest), plus shell: manual mode

**Markers (pytest only):**
- `pytest.mark.agentic_e2e_copilot_cli_autopilot` — Copilot CLI fully autonomous (CI/CD)
- `pytest.mark.agentic_e2e_cursor_cli_autopilot` — Cursor CLI fully autonomous (CI/CD)
- `pytest.mark.agentic_e2e_opencode_cli_autopilot` — OpenCode CLI fully autonomous (CI/CD)
- `pytest.mark.agentic_e2e_claude_code_autopilot` — Claude Code CLI fully autonomous (CI/CD)

## 🚀 Quick Start

```bash
cd tests

# Agentic infrastructure validation (199 tests, ~1 second)
./test.sh agentic

# Agentic E2E scenario tests
./test.sh agentic-e2e-copilot-cli-autopilot     # Copilot CLI, fully autonomous (CI/CD)
./test.sh agentic-e2e-cursor-cli-autopilot      # Cursor CLI, fully autonomous (CI/CD)
./test.sh agentic-e2e-opencode-cli-autopilot    # OpenCode CLI, fully autonomous (CI/CD)
./test.sh agentic-e2e-claude-code-autopilot     # Claude Code CLI, fully autonomous (CI/CD)
./test.sh agentic-e2e-copilot-cli-manual        # Copilot CLI, interactive (shell-based)
./test.sh agentic-e2e-cursor-cli-manual         # Cursor CLI, interactive (shell-based)
./test.sh agentic-e2e-opencode-cli-manual       # OpenCode CLI, interactive (shell-based)
./test.sh agentic-e2e-claude-code-manual        # Claude Code CLI, interactive (shell-based)
```

## 💡 Key Commands

### Test Suite Commands

```bash
./test.sh agentic          # Agentic infrastructure (199 tests, ~1 second)
./test.sh agentic-e2e-claude-code-autopilot   # Agentic E2E Claude Code autonomous
./test.sh agentic-e2e-copilot-cli-autopilot   # Agentic E2E Copilot CLI autonomous
./test.sh agentic-e2e-opencode-cli-autopilot  # Agentic E2E Opencode CLI autonomous
./test.sh agentic-e2e-cursor-cli-autopilot    # Agentic E2E Cursor CLI autonomous
./test.sh agentic-e2e-claude-code-manual      # Agentic E2E Claude Code interactive
./test.sh agentic-e2e-copilot-cli-manual      # Agentic E2E Copilot CLI interactive
./test.sh agentic-e2e-opencode-cli-manual     # Agentic E2E OpenCode CLI interactive
./test.sh agentic-e2e-cursor-cli-manual       # Agentic E2E Cursor CLI interactive
```

### Marker Filters

```bash
./test.sh -m "agentic_e2e_copilot_cli_autopilot"  # Only Copilot CLI agentic E2E
./test.sh -m "agentic_e2e_cursor_cli_autopilot"   # Only Cursor CLI agentic E2E
./test.sh -m "agentic_e2e_opencode_cli_autopilot" # Only OpenCode CLI agentic E2E
./test.sh -m "agentic_e2e_claude_code_autopilot"  # Only Claude Code CLI agentic E2E
```

## 🎨 Usage Examples

### Example 1: Agentic E2E — Copilot CLI Autopilot (CI/CD)

```bash
# Run all Copilot CLI E2E tests in autopilot mode (fully autonomous)
./test.sh agentic-e2e-copilot-cli-autopilot

# Filter to compiler scenario only
./test.sh agentic-e2e-copilot-cli-autopilot -k compiler

# With custom model and extended timeout
DX_AGENTIC_E2E_TIMEOUT=900 DX_AGENTIC_E2E_MODEL="claude-opus-4.6" \
  ./test.sh agentic-e2e-copilot-cli-autopilot
```

### Example 2: Agentic E2E — Cursor CLI Autopilot (CI/CD)

```bash
# Run all Cursor CLI E2E tests (default model: claude-4.6-sonnet-medium)
./test.sh agentic-e2e-cursor-cli-autopilot

# Filter to dx_stream scenario only
./test.sh agentic-e2e-cursor-cli-autopilot -k dx_stream

# With different model
DX_AGENTIC_E2E_CURSOR_MODEL="claude-opus-4-7-thinking-high" \
  ./test.sh agentic-e2e-cursor-cli-autopilot
```

### Example 3: Agentic E2E — Copilot CLI Manual (Interactive)

```bash
# Interactive mode — runs Copilot CLI TUI directly (no pytest)
./test.sh agentic-e2e-copilot-cli-manual

# Auto-select a specific scenario
./test.sh agentic-e2e-copilot-cli-manual -k compiler
./test.sh agentic-e2e-copilot-cli-manual -k dx_app
```

### Example 4: Agentic E2E — Cursor CLI Manual (Interactive)

```bash
# Interactive mode — runs Cursor CLI TUI directly (no pytest)
./test.sh agentic-e2e-cursor-cli-manual

# Auto-select a specific scenario
./test.sh agentic-e2e-cursor-cli-manual -k dx_stream
```

## 🤖 Agentic E2E — Copilot CLI Autonomous Execution

The agentic E2E test suite (`test_agentic_e2e_scenarios/`) runs real Copilot CLI
sessions against the dx-all-suite codebase. This section explains how autonomous
(auto-approve) execution works.

### Two Execution Modes

| Mode | Entry Point | OpenCode Flags | User Interaction |
|------|-------------|----------------|------------------|
| **Autopilot** | `./test.sh agentic-e2e-copilot-cli-autopilot` | `--yolo --no-ask-user -s` | None (fully autonomous) |
| **Manual** | `./test.sh agentic-e2e-copilot-cli-manual` | `--yolo` | Interactive TUI |

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
  `DX_AGENTIC_E2E_TIMEOUT`). If the agent exceeds the timeout, the process
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
| `DX_AGENTIC_E2E_MODEL` | `claude-sonnet-4.6` | LLM model for Copilot CLI |
| `DX_AGENTIC_E2E_TIMEOUT` | `300` | Timeout in seconds per scenario |
| `DX_AGENTIC_E2E_CLEANUP_ARTIFACTS` | (unset) | Set to `1` to delete generated `dx-agentic-dev/` directories after test run (default: keep) |
| `DX_AGENTIC_E2E_MODE` | (set by test.sh) | `autopilot` or `manual` — set automatically by `test.sh` |

### Running with Different Models

```bash
# Claude Sonnet 4.6 (recommended)
DX_AGENTIC_E2E_MODEL="claude-sonnet-4.6" ./test.sh agentic-e2e-copilot-cli-autopilot

# GPT-4.1 (not recommended — may fabricate APIs)
DX_AGENTIC_E2E_MODEL="gpt-4.1" DX_AGENTIC_E2E_TIMEOUT=600 \
  ./test.sh agentic-e2e-copilot-cli-autopilot

# Claude Opus 4.6 (highest quality, slower)
DX_AGENTIC_E2E_MODEL="claude-opus-4.6" DX_AGENTIC_E2E_TIMEOUT=900 \
  ./test.sh agentic-e2e-copilot-cli-autopilot
```

### Session Output and Artifacts

Each scenario generates artifacts in `dx-agentic-dev/<session_id>/` within
the target sub-project. The test framework auto-detects new session directories
by comparing pre/post directory snapshots.

After a test run, artifacts include:
- Generated code files (Python scripts, configs, shell scripts)
- `session.log` — command execution transcript
- Copilot session transcript (saved via `--share=<file>`)
- HTML export (if `test.sh` detects it was generated via `/share html`)

Generated artifacts are preserved by default for debugging.
Set `DX_AGENTIC_E2E_CLEANUP_ARTIFACTS=1` to delete them after a successful run.

### Differences from Copilot CLI Tests

The Cursor CLI E2E tests (`test_cursor_*_agentic_e2e.py`) run the same scenarios as
the Copilot CLI tests, but using the Cursor CLI (`agent`) instead.

---

## 🖥 Agentic E2E — Cursor CLI Autonomous Execution

The Cursor CLI E2E tests (`test_cursor_*_agentic_e2e.py`) run the same scenarios as
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
./test.sh agentic-e2e-cursor-cli-autopilot

# Filter to specific scenario
./test.sh agentic-e2e-cursor-cli-autopilot -k dx_app
./test.sh agentic-e2e-cursor-cli-autopilot -k compiler

# With custom model (override default)
DX_AGENTIC_E2E_CURSOR_MODEL="claude-opus-4-7-thinking-high" \
  ./test.sh agentic-e2e-cursor-cli-autopilot

# With extended timeout
DX_AGENTIC_E2E_CURSOR_TIMEOUT=900 \
  ./test.sh agentic-e2e-cursor-cli-autopilot
```

### Environment Variables (Cursor-specific)

| Variable | Default | Description |
|----------|---------|-------------|
| `DX_AGENTIC_E2E_CURSOR_MODEL` | `claude-4.6-sonnet-medium` | LLM model for Cursor CLI |
| `DX_AGENTIC_E2E_CURSOR_TIMEOUT` | `300` | Timeout in seconds per scenario |
| `DX_AGENTIC_E2E_CLEANUP_ARTIFACTS` | (unset) | Set to `1` to delete generated artifacts after a successful run (default: keep) |
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

## 🖥 Agentic E2E — OpenCode CLI Autonomous Execution

The OpenCode CLI E2E tests (`test_opencode_*_agentic_e2e.py`) run the same scenarios
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
./test.sh agentic-e2e-opencode-cli-autopilot

# Filter to specific scenario
./test.sh agentic-e2e-opencode-cli-autopilot -k dx_app
./test.sh agentic-e2e-opencode-cli-autopilot -k compiler

# With custom model
DX_AGENTIC_E2E_OPENCODE_MODEL="anthropic/claude-opus-4.6" \
  ./test.sh agentic-e2e-opencode-cli-autopilot

# With extended timeout
DX_AGENTIC_E2E_OPENCODE_TIMEOUT=900 \
  ./test.sh agentic-e2e-opencode-cli-autopilot
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
| `DX_AGENTIC_E2E_OPENCODE_MODEL` | `github-copilot/claude-sonnet-4.6` | LLM model for OpenCode CLI |
| `DX_AGENTIC_E2E_OPENCODE_TIMEOUT` | `600` | Timeout in seconds per scenario |
| `DX_OPENCODE_CASCADED_TIMEOUT` | `720` | Timeout for cascaded (multi-session) scenarios |
| `DX_AGENTIC_E2E_CLEANUP_ARTIFACTS` | (unset) | Set to `1` to delete generated artifacts after a successful run (default: keep) |

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

## 🖥 Agentic E2E — Claude Code CLI Autonomous Execution

The Claude Code CLI E2E tests (`test_claude_code_*_agentic_e2e.py`) run the same
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
./test.sh agentic-e2e-claude-code-autopilot

# Filter to specific scenario
./test.sh agentic-e2e-claude-code-autopilot -k dx_app
./test.sh agentic-e2e-claude-code-autopilot -k compiler

# With custom model
DX_AGENTIC_E2E_CLAUDE_CODE_MODEL="claude-opus-4-6" \
  ./test.sh agentic-e2e-claude-code-autopilot

# With extended timeout and cleanup
DX_AGENTIC_E2E_CLAUDE_CODE_TIMEOUT=900 DX_AGENTIC_E2E_CLEANUP_ARTIFACTS=1 \
  ./test.sh agentic-e2e-claude-code-autopilot -k dx_stream
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
| `DX_AGENTIC_E2E_CLAUDE_CODE_MODEL` | `claude-sonnet-4-6` | LLM model for Claude Code CLI |
| `DX_AGENTIC_E2E_CLAUDE_CODE_TIMEOUT` | `600` | Timeout in seconds per scenario |
| `DX_AGENTIC_E2E_CLAUDE_QUOTA_POLL_INTERVAL` | `3600` | Seconds to wait between quota-limit retries |
| `DX_AGENTIC_E2E_CLAUDE_QUOTA_MAX_POLLS` | `8` | Max retry polls on quota/rate limit |
| `DX_AGENTIC_E2E_CLEANUP_ARTIFACTS` | (unset) | Set to `1` to delete generated artifacts after a successful run (default: keep) |

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
| **agentic** | 199 | ~1 second | Agentic infrastructure validation |
| **agentic_e2e (copilot-cli)** | 67 | ~30-45 minutes | Agentic E2E Copilot CLI scenario tests |
| **agentic_e2e (cursor-cli)** | 63 | ~40-45 minutes | Agentic E2E Cursor CLI scenario tests (Claude Sonnet 4.6) |
| **agentic_e2e (opencode-cli)** | 112 | ~45-60 minutes | Agentic E2E OpenCode CLI scenario tests |
| **agentic_e2e (claude-code-cli)** | 110 | ~45-60 minutes | Agentic E2E Claude Code CLI scenario tests |

## 🔧 Environment Variables

```bash
# Agentic E2E test configuration (Copilot CLI)
export DX_AGENTIC_E2E_TIMEOUT=900           # Copilot CLI timeout in seconds (default: 300)
export DX_AGENTIC_E2E_MODEL="claude-opus-4.6"       # OpenCode model to use (default: claude-sonnet-4.6)
# export DX_AGENTIC_E2E_CLEANUP_ARTIFACTS=1  # Delete artifacts after successful run (default: keep)

# Agentic E2E test configuration (Cursor CLI)
export DX_AGENTIC_E2E_CURSOR_MODEL="claude-4.6-sonnet-medium"  # Cursor model (default: claude-4.6-sonnet-medium)
export DX_AGENTIC_E2E_CURSOR_TIMEOUT=300    # Cursor CLI timeout in seconds (default: 300)
export CURSOR_API_KEY="your-api-key"        # API key for headless/CI (alternative to 'agent login')

# Agentic E2E test configuration (OpenCode CLI)
export DX_AGENTIC_E2E_OPENCODE_MODEL="github-copilot/claude-sonnet-4.6"  # OpenCode model (default)
export DX_AGENTIC_E2E_OPENCODE_TIMEOUT=600  # OpenCode CLI timeout in seconds (default: 600)
export DX_OPENCODE_CASCADED_TIMEOUT=720     # OpenCode cascaded scenario timeout (default: 720)

# Agentic E2E test configuration (Claude Code CLI)
export DX_AGENTIC_E2E_CLAUDE_CODE_MODEL="claude-sonnet-4-6"  # Claude Code model (default)
export DX_AGENTIC_E2E_CLAUDE_CODE_TIMEOUT=600  # Claude Code CLI timeout in seconds (default: 600)
```

## 🔄 CI/CD Integration

### Recommended CI/CD Strategy

**Pull Request (Fast Feedback):**
```bash
./test.sh agentic                     # Agentic infrastructure (~1 sec)
```

**Main/Develop Branch (Comprehensive):**
```bash
./test.sh agentic-e2e-copilot-cli-autopilot    # Agentic E2E Copilot CLI scenarios
./test.sh agentic-e2e-cursor-cli-autopilot     # Agentic E2E Cursor CLI scenarios
```

## 📁 File Structure

```
tests/
├── 🐍 test_agentic_scenarios/       # Agentic infrastructure validation
│   ├── conftest.py                  # ProjectInfra dataclass, path constants, helpers
│   ├── test_guide_structure.py      # Guide existence, headings, numbering, EN/KO sync
│   ├── test_routing_consistency.py  # CLAUDE.md, AGENTS.md, copilot-instructions consistency
│   ├── test_scenario_references.py  # Agent/skill references match infrastructure
│   └── test_cross_project_scenarios.py  # Handoff chains, validation scripts
├── 🐍 test_agentic_e2e_scenarios/   # Agentic E2E scenario tests (Copilot + Cursor CLI)
│   ├── conftest.py                  # CopilotRunnerAutopilot, CursorRunnerAutopilot, ScenarioResult, helpers
│   ├── test_dx_app_agentic_e2e.py   # dx_app — Copilot CLI (11 tests)
│   ├── test_dx_stream_agentic_e2e.py # dx_stream — Copilot CLI (18 tests)
│   ├── test_compiler_agentic_e2e.py # dx-compiler — Copilot CLI (14 tests)
│   ├── test_runtime_agentic_e2e.py  # dx-runtime — Copilot CLI (10 tests)
│   ├── test_suite_agentic_e2e.py    # dx-all-suite — Copilot CLI (14 tests)
│   ├── test_cursor_dx_app_agentic_e2e.py    # dx_app — Cursor CLI (10 tests)
│   ├── test_cursor_dx_stream_agentic_e2e.py # dx_stream — Cursor CLI (15 tests)
│   ├── test_cursor_compiler_agentic_e2e.py  # dx-compiler — Cursor CLI (14 tests)
│   ├── test_cursor_runtime_agentic_e2e.py   # dx-runtime — Cursor CLI (10 tests)
│   ├── test_cursor_suite_agentic_e2e.py     # dx-all-suite — Cursor CLI (14 tests)
│   ├── test_opencode_dx_app_agentic_e2e.py       # dx_app — OpenCode CLI (10 tests)
│   ├── test_opencode_dx_stream_agentic_e2e.py    # dx_stream — OpenCode CLI (32 tests)
│   ├── test_opencode_dx_stream_cascaded_e2e.py   # dx_stream cascaded — OpenCode CLI (25 tests)
│   ├── test_opencode_compiler_agentic_e2e.py     # dx-compiler — OpenCode CLI (14 tests)
│   ├── test_opencode_runtime_agentic_e2e.py      # dx-runtime — OpenCode CLI (9 tests)
│   ├── test_opencode_suite_agentic_e2e.py        # dx-all-suite — OpenCode CLI (22 tests)
│   ├── test_claude_code_dx_app_agentic_e2e.py    # dx_app — Claude Code CLI (10 tests)
│   ├── test_claude_code_dx_stream_agentic_e2e.py # dx_stream — Claude Code CLI (32 tests)
│   ├── test_claude_code_dx_stream_cascaded_e2e.py # dx_stream cascaded — Claude Code CLI (24 tests)
│   ├── test_claude_code_compiler_agentic_e2e.py  # dx-compiler — Claude Code CLI (14 tests)
│   ├── test_claude_code_runtime_agentic_e2e.py   # dx-runtime — Claude Code CLI (9 tests)
│   └── test_claude_code_suite_agentic_e2e.py     # dx-all-suite — Claude Code CLI (21 tests)
├── 🔍 parse_copilot_session.py        # Copilot CLI events.jsonl → Markdown report parser
└── 🔧 conftest.py                   # Shared pytest fixtures and utilities
```

---

**Total Agentic Tests:**
551 (agentic: 199 | agentic_e2e_copilot_cli: 67 | agentic_e2e_cursor_cli: 63 | agentic_e2e_opencode_cli: 112 | agentic_e2e_claude_code_cli: 110)

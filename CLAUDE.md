# DX All Suite — Claude Code Entry Point

> Top-level repository for the DEEPX All Suite (DX-AS).

## Response Language

Match your response language to the user's prompt language — when asking questions
or responding, use the same language the user is using.

**Technical term rule**: When responding in Korean, keep English technical terms in
their original English form. Do NOT transliterate English terms into Korean phonetics
(한글 음차 표기 금지). Established Korean loanwords (모델, 서버, 파일, 데이터) are acceptable.

## Recommended Model (Pre-Flight Check)

DX Agentic Development requires strong instruction following and knowledge base
utilization. Before starting any task, check if you are running as one of the
recommended models:

- **Claude Sonnet 4.6** or later
- **Claude Opus 4.6** or later

If you are NOT one of these models (e.g., GPT-4.1, GPT-4o, Gemini, etc.),
output the following notice at the beginning of your first response:

```
══════════════════════════════════════════════════════════════
⚠  DX-AGENTIC-DEV: MODEL NOTICE

DX Agentic Development recommends Claude Sonnet 4.6+ or
Opus 4.6+. Your current model may produce lower quality
in instruction following, knowledge base utilization, and
API accuracy. Please switch to a recommended model.
══════════════════════════════════════════════════════════════
```

After the box notice, proceed with the task normally. This is an informational
warning, not a blocking gate.

### Model Notice Repeat (Non-Recommended Model Only)

If you output the MODEL NOTICE box above (i.e., you are NOT a recommended model),
you MUST also output this shortened reminder **immediately before the actual question
line** that the user needs to answer — NOT at the beginning of the brainstorming flow.

**Timing**: After all file reading, context analysis, and preamble text, right before
the line that contains the `?` (the actual question), insert this reminder:

```
---
⚠ **Non-recommended model** — output quality may be degraded. Recommended: Claude Sonnet 4.6+ / Opus 4.6+
---
```

**Example — WRONG** (repeat scrolls past with the box):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
---  ⚠ Non-recommended model ---     ← TOO EARLY, scrolls past
... (reads files, analyzes context) ...
First question: ...?
```

**Example — CORRECT** (repeat appears right before the question):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
... (reads files, analyzes context) ...
---  ⚠ Non-recommended model ---     ← RIGHT BEFORE the question
First question: ...?
```

Only output this reminder ONCE (before the first question), not before every question.

## Skill Router — Universal Pre-Flight (HARD GATE)

`/dx-skill-router` MUST be invoked as the **absolute first action** for
**every user message** — regardless of task type (development, analysis,
reading, explanation, or clarification).

This rule applies before:
- Any file read or codebase exploration
- Any response or clarifying question
- Any SWE gate check or path classification
- Any code generation or plan creation

**No exceptions.** The following rationalizations are ALL prohibited:

| Rationalization | Reality |
|----------------|---------|
| "This is just reading/analyzing files" | Reading IS a task. Invoke router first. |
| "The user only asked a question" | Questions are tasks. Invoke router first. |
| "This is not a development task" | Router applies to ALL tasks, not only dev. |
| "I'll check for skills after I understand the request" | Check BEFORE understanding. |
| "This doesn't trigger SWE gates" | SWE gates are separate. Router is universal. |

## Repository Structure

| Component | Path | Purpose |
|---|---|---|
| **dx-runtime** | `dx-runtime/` | Integration layer + cross-project orchestration |
| **dx_app** | `dx-runtime/dx_app/` | Standalone inference apps (Python/C++, 133 models, 15 AI tasks) |
| **dx_stream** | `dx-runtime/dx_stream/` | GStreamer pipeline apps (13 elements, 6 pipeline categories) |
| **Docs** | `docs/` | MkDocs documentation site |
| **dx-compiler** | `dx-compiler/` | DXNN model compiler (ONNX → .dxnn via DX-COM) |

## Routing

Each submodule has its own `CLAUDE.md` with full context:

| Working on... | Read first |
|---|---|
| Standalone inference (Python/C++) | `dx-runtime/dx_app/CLAUDE.md` |
| GStreamer pipelines | `dx-runtime/dx_stream/CLAUDE.md` |
| Cross-project integration | `dx-runtime/CLAUDE.md` |
| Model compilation (ONNX → DXNN) | `dx-compiler/CLAUDE.md` |
| Cross-suite (compile + deploy) | `dx-compiler/CLAUDE.md` + `dx-runtime/CLAUDE.md` |

## Skills

| Skill | Description |
|---|---|
| `/dx-validate-all` | Full validation across all 3 levels — validate, collect feedback, apply fixes, verify |
| `/dx-brainstorm-and-plan` | Brainstorm, propose 2-3 approaches, spec self-review, then plan |
| `/dx-tdd` | Validation-driven development with optional Red-Green-Refactor for unit tests |
| `/dx-verify-completion` | Verify before claiming completion — evidence before assertions |

### Process Skills

| Skill | Description |
|---|---|
| `/dx-writing-plans` | Write implementation plans with bite-sized tasks |
| `/dx-executing-plans` | Execute plans with review checkpoints |
| `/dx-subagent-driven-development` | Execute plans via fresh subagent per task with two-stage review |
| `/dx-systematic-debugging` | Systematic debugging — 4-phase root cause investigation before proposing fixes |
| `/dx-receiving-code-review` | Evaluate code review feedback with technical rigor |
| `/dx-requesting-code-review` | Request code review after completing features |
| `/dx-skill-router` | Skill discovery and invocation — check skills before any action |
| `/dx-writing-skills` | Create and edit skill files |
| `/dx-dispatching-parallel-agents` | Dispatch parallel subagents for independent tasks |

## Quick Reference

```bash
# Build
cd dx-runtime/dx_app && ./install.sh && ./build.sh
cd dx-runtime/dx_stream && ./install.sh

# Test
cd dx-runtime/dx_app && pytest tests/
cd dx-runtime/dx_stream && pytest test/

# Validate
python dx-runtime/.deepx/scripts/validate_framework.py
python dx-runtime/dx_app/.deepx/scripts/validate_framework.py
python dx-runtime/dx_stream/.deepx/scripts/validate_framework.py
python dx-compiler/.deepx/scripts/validate_framework.py

# Unified feedback loop
python dx-runtime/.deepx/scripts/feedback_collector.py --framework-only
```

## Output Isolation (HARD GATE)

ALL AI-generated files MUST be written to `dx-agentic-dev/<session_id>/` within the
target sub-project. NEVER write generated code directly into existing source directories
(e.g., `src/`, `pipelines/`, `semseg_260323/`, or any directory containing user's
existing code).

**Session ID format**: `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` — the timestamp MUST use the
**system local timezone** (NOT UTC). Use `$(date +%Y%m%d-%H%M%S)` in Bash or
`datetime.now().strftime('%Y%m%d-%H%M%S')` in Python. Do NOT use `date -u`,
`datetime.utcnow()`, or `datetime.now(timezone.utc)`.
- **`<agent>`**: the coding agent identifier — use `claude`, `copilot`, `cursor`, or `opencode`.

- **Correct**: `dx-runtime/dx_app/dx-agentic-dev/20260413-093000_claude_plantseg_inference/demo_dxnn_sync.py`
- **Wrong**: `dx-runtime/dx_app/semseg_260323/demo_dxnn_sync.py`

The ONLY exception: when the user EXPLICITLY says "write to the source directory" or
"modify the existing file in-place". Placing new files alongside existing code in a
source directory without explicit user instruction is a violation.

## Cross-Project Routing (MANDATORY)

When a task involves DXNN compilation (ONNX → .dxnn), the **compiler builder agent
MUST be invoked** and the actual `dxcom` command MUST be executed. Never generate
placeholder compilation scripts or stub code — produce the real `.dxnn` file.

| Task mentions... | Route to |
|---|---|
| ONNX → DXNN, compile, dxcom | `dx-compiler/CLAUDE.md` |
| Python app, factory, inference | `dx-runtime/dx_app/CLAUDE.md` |
| GStreamer pipeline, stream | `dx-runtime/dx_stream/CLAUDE.md` |

### Cross-Project Session Layout — HARD GATE (R41)

When the task is **"compile ONNX + build app"** (suite scenario), you MUST produce
**two separate session directories**:

1. **Compiler session** → `dx-compiler/dx-agentic-dev/<session_id>/` (contains
   `compile.py`, `config.json`, `yolo26n.dxnn`, `verify.py`, `session.log`)
2. **App session** → `dx-runtime/dx_app/dx-agentic-dev/<session_id>/` (contains
   factory, `<model>_sync.py`, `setup.sh`, `run.sh`)

**NEVER merge both into a single `dx_app/` session.** The test assertion that will fail:
```python
assert any("dx-compiler" in str(d) for d in output_dirs)
```

This dual-session layout violation has occurred repeatedly in cursor (iter-4, iter-6,
iter-8). The compiler agent document (`dx-compiler/CLAUDE.md`) contains the R31 Session
Layout HARD GATE. You MUST read and apply it before writing any files.

### Session Naming — PROHIBITED Patterns (R43)

Do NOT use `_auto_` in the session ID. The `_auto_` prefix indicates the tool bypassed
the cross-project routing workflow. A correct suite session produces TWO separate IDs:
- `<ts>_<agent>_<model>_compile` in `dx-compiler/dx-agentic-dev/`
- `<ts>_<agent>_<model>_inference` in `dx-runtime/dx_app/dx-agentic-dev/`

## No Placeholder Code (MANDATORY)

NEVER generate stub/placeholder code. This includes:
- Commented-out imports: `# from dxnn_sdk import InferenceEngine`
- Fake results: `result = np.zeros(...)`
- TODO markers: `# TODO: implement actual inference`
- "Similar to sync version" without actual async implementation

All generated code MUST be functional, using real APIs from the knowledge base.
If the required SDK/API is unknown, read the relevant skill document first.

## Experimental Features — Prohibited

Do NOT offer, suggest, or implement experimental or non-existent features. This includes:
- "웹 기반 비주얼 컴패니언" (web-based visual companion)
- Local URL-based diagram viewers or dashboards
- Any feature requiring the user to open a local URL for visualization
- Any capability that does not exist in the current toolset

**Superpowers brainstorming skill override**: The superpowers `brainstorming` skill
includes a "Visual Companion" step (step 2 in its checklist). This step MUST be
SKIPPED in the DEEPX project. The visual companion does not exist in our environment.
When the brainstorming checklist says "Offer visual companion", skip it and proceed
directly to "Ask clarifying questions" (step 3).

If a feature does not exist, do not pretend it does. Stick to proven, documented
capabilities only.

**Autopilot / autonomous mode override**: When the user is absent (autopilot mode,
auto-response "work autonomously", or `--yolo` flag), the brainstorming skill's
"Ask clarifying questions" step MUST be replaced with "Make default decisions per
knowledge base rules". Do NOT call `ask_user` — skip straight to producing the
brainstorming spec using knowledge base defaults. All subsequent gates (spec review,
plan, TDD, mandatory artifacts, execution verification) still apply without exception.

## Brainstorming — Spec Before Plan (HARD GATE)

When using the superpowers `brainstorming` skill or `/dx-brainstorm-and-plan`:

1. **Spec document is MANDATORY** — Before transitioning to `writing-plans`, a spec
   document MUST be written to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`.
   Skipping the spec and going directly to plan writing is a violation.
2. **User approval gate is MANDATORY** — After writing the spec, the user MUST review
   and approve it before proceeding to plan writing. Do NOT treat unrelated user
   responses (e.g., answering a different question) as spec approval.
3. **Plan document MUST reference the spec** — The plan header must include a link
   to the approved spec document.
4. **Prefer `/dx-brainstorm-and-plan`** — Use the project-level brainstorming skill
   instead of the generic superpowers `brainstorming` skill. The project-level skill
    has domain-specific questions and pre-flight checks.
5. **Rule conflict check is MANDATORY** — During brainstorming, the agent MUST check
   whether any user requirement conflicts with HARD GATE rules (IFactory pattern,
   skeleton-first, Output Isolation, SyncRunner/AsyncRunner). If a conflict is
   detected, the agent MUST resolve it during brainstorming — not silently comply
   with the violating request in the design spec. See the "Rule Conflict Resolution" section.

## Autopilot Mode Guard (MANDATORY)

When the user is absent — autopilot mode, `--yolo` flag, or system auto-response
"The user is not available to respond" — the following rules apply:

1. **"Work autonomously" means "follow all rules without asking", NOT "skip rules".**
   Every mandatory gate still applies: brainstorming spec, plan, TDD, mandatory
   artifacts, execution verification, and self-verification checks.
   **This includes the SWE Process Gates Mandatory Skill Sequence** — in autopilot,
   `/dx-skill-router` → `/dx-brainstorm-and-plan` → `/dx-tdd` must be followed
   exactly as in interactive mode. Autopilot mode does NOT waive this sequence.
2. **Do NOT call `ask_user`** — Make decisions using knowledge base defaults and
   documented best practices. Calling `ask_user` in autopilot wastes a turn and
   the auto-response does not grant permission to bypass any gate.
3. **User approval gate adaptation** — In autopilot, the spec approval gate is
   satisfied by writing the spec and self-reviewing it against the knowledge base.
   Do NOT skip the spec entirely.
4. **setup.sh FIRST** — Generate infrastructure artifacts (`setup.sh`, `config.json`)
   before writing any application code. This is especially critical in autopilot
   because there is no human to catch missing dependencies.
5. **Execution verification is NOT optional** — Run the generated code and verify it
   works before declaring completion. In autopilot, there is no user to catch errors.
6. **Time budget awareness** — Autopilot sessions may have time constraints.
   Plan your actions efficiently:
   - Compilation (ONNX → DXNN) may take 5+ minutes — start it early.
   - If time is short, prioritize artifact GENERATION over execution
     verification — a complete set of untested files is better than a partial
     set of tested ones.
   - Priority order: `setup.sh` > `run.sh` > app code > `verify.py` > session.log.
   - **Compilation-parallel workflow (HARD GATE)** — After launching `dxcom` or
     `dx_com.compile()` in a bash command, do NOT wait for it. Immediately
     proceed to generate ALL mandatory artifacts: factory, app code, setup.sh,
     run.sh, verify.py. Check `.dxnn` output only AFTER all other artifacts
     are created. **Violation of this rule fails the session.**
   - **NEVER sleep-poll for compilation** — Do NOT use `sleep` in a loop to
     poll for `.dxnn` files. Prohibited patterns include:
     `for i in ...; do sleep N; ls *.dxnn; done`,
     `while ! ls *.dxnn; do sleep N; done`,
     repeated `ls *.dxnn` / `test -f *.dxnn` checks with waits between them.
     Instead: generate all other artifacts first, then check ONCE whether the
     `.dxnn` file exists. If it does not exist yet, proceed to execution
     verification with the assumption that compilation will complete.
   - **Mandatory artifacts are compilation-independent** — `setup.sh`, `run.sh`,
     `verify.py`, factory, and app code do NOT require the `.dxnn` file to exist.
     Generate them using the known model name (e.g., `yolo26n.dxnn`) as a
     placeholder path. Only execution verification requires the actual `.dxnn`.
7. **Minimize file-reading tool calls** — Do NOT re-read instruction files,
   agent docs, or skill docs that are already loaded in your context. Each
   unnecessary `cat` / `bash` read wastes 5-15 seconds. Use the knowledge
   already in your system prompt and conversation history.

## Hardware

| Architecture | Value |
|---|---|
| DX-M1 | `dx_m1` |

## Git Safety — Superpowers Artifacts

**NEVER `git add` or `git commit` files under `docs/superpowers/`.** These are temporary
planning artifacts generated by the superpowers skill system (specs, plans). They are
`.gitignore`d, but some tools may bypass `.gitignore` with `git add -f`. Creating the
files is fine — committing them is forbidden.

## Session Sentinels (MANDATORY for Automated Testing)

When processing a user prompt, output these exact markers for automated session
boundary detection by the test harness:

- **First line of your response**: `[DX-AGENTIC-DEV: START]`
- **Last line after ALL work is complete**: `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]`
  where `<relative_path>` is the session output directory (e.g., `dx-agentic-dev/20260409-143022_yolo26n_detection/`)

Rules:
1. **CRITICAL — Output `[DX-AGENTIC-DEV: START]` as the absolute first line of your
   first response.** This must appear before ANY other text, tool calls, or reasoning.
   Even if the user instructs you to "just proceed" or "use your own judgment",
   the START sentinel is non-negotiable — automated tests WILL fail without it.
2. Output `[DX-AGENTIC-DEV: DONE (output-dir: <path>)]` as the very last line after all work, validation,
   and file generation is complete
3. If you are a **sub-agent** invoked via handoff/routing from a higher-level agent,
   do NOT output these sentinels — only the top-level agent outputs them
4. If the user sends multiple prompts in a session, output START/DONE for each prompt
5. The `output-dir` in DONE must be the relative path from the project root to the
   session output directory. If no files were generated, omit the `(output-dir: ...)` part.
   **For cross-project tasks** (e.g., compile + app generation), list ALL output directories
   separated by ` + `:
   ```
   [DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260409-143022_copilot_yolo26n_compile/ + dx-runtime/dx_app/dx-agentic-dev/20260409-143022_copilot_yolo26n_inference/)]
   ```
6. **NEVER output DONE after only producing planning artifacts** (specs, plans, design
   documents). DONE means all deliverables are produced — implementation code, scripts,
   configs, and validation results. If you completed a brainstorming or planning phase
   but have not yet implemented the actual code, do NOT output DONE. Instead, proceed
   to implementation or ask the user how to proceed.
7. **Pre-DONE mandatory deliverable check**: Before outputting DONE, verify that all
   mandatory deliverables exist in the session directory. If any mandatory file is
   missing, create it before outputting DONE. Each sub-project defines its own mandatory
   file list in its skill document (e.g., `dx-build-pipeline-app.md` File Creation Checklist).
8. **Session export guidance**: Immediately before the DONE sentinel line, output
   the appropriate session-save instruction based on the CLI platform:

   | Platform | Command | Format |
   |----------|---------|--------|
   | **Copilot CLI** | `/share html` | HTML transcript |
   | **Cursor CLI** (`agent`) | No built-in export — session is saved automatically by the test harness via `--output-format stream-json` | JSON stream |
   | **OpenCode** | `/export` | JSON |
   | **Claude Code** (`claude`) | `/export` | TXT transcript — written to `<workdir>/YYYY-MM-DD-HHMMSS-<title>.txt` |

   For Copilot CLI, output: `To save this session as HTML, type: /share html`
   For OpenCode, output: `To save this session as JSON, type: /export`
   For Claude Code, output: `To save this session as a text transcript, type: /export`
   For Cursor CLI, no user action is needed — the test harness captures output automatically.

   The test harness (`test.sh`) will automatically detect and copy exported artifacts
   to the session output directory.

## Mandatory Deliverables

ALL compilation or app-generation sessions MUST produce the following files in the
session output directory (`dx-agentic-dev/<session_id>/`) before outputting DONE.
This applies to **every task type** — compiler-only, app-only, and cross-project.

| File | Purpose | Required when |
|------|---------|---------------|
| `setup.sh` | Environment setup (sanity check, dxcom install, venv, pip deps) | Always |
| `run.sh` | One-command inference launcher with venv activation | Always |
| `README.md` | Session summary, quick start, file list | Always |
| `verify.py` | ONNX vs DXNN numerical comparison | Compilation involved |
| `session.log` | Actual command output log (NOT hand-written summary) | Always |
| `config.json` | dxcom compilation configuration | Compilation involved |
| `*.dxnn` | Compiled model binary | Compilation involved |

These are in ADDITION to any application-specific artifacts (Python files with
factory/inference patterns, GStreamer pipeline code, etc.).

Each sub-project also defines templates for these files in its agent/skill documents
(e.g., `dx-compiler/.deepx/agents/dx-dxnn-compiler.md` Phase 5.5).

### Cross-project suite tasks — pre-DONE `.dxnn` check (HARD GATE, REC-X4)

**For any task involving compilation**, before emitting the DONE sentinel, verify that
the `.dxnn` file exists in the compiler session directory:

```bash
COMPILER_SESSION="<compiler_session_dir>"   # e.g., dx-compiler/dx-agentic-dev/20260430-..._compile
test -f "${COMPILER_SESSION}/yolo26n.dxnn" \
  || { echo "BLOCKED: yolo26n.dxnn not found — compilation still running. Wait for compile.pid to exit before emitting DONE."; exit 1; }
```

Emitting DONE while `yolo26n.dxnn` is absent causes `test_dxnn_compiled` to fail even if
background compilation eventually produces it (the test harness collects files at DONE time).
See Phase 5.8 in `dx-compiler/.deepx/agents/dx-dxnn-compiler.md` for the full pre-DONE gate.

## Artifact Verification Gate (HARD GATE — All Code Generation)

This gate applies to ALL sessions that generate code artifacts (compilation,
app generation, pipeline creation). It is independent of the "Internal Development"
SWE Process Gates — those apply to dx-agentic-dev feature work; THIS gate applies
to user-facing deliverables.

### When This Gate Applies

Any session that produces files in `dx-agentic-dev/<session_id>/` MUST verify
those files before declaring DONE. This includes:
- Compilation sessions (ONNX → DXNN)
- App generation sessions (dx_app factories + runners)
- Pipeline sessions (dx_stream pipelines)
- Cross-project sessions (compile + deploy)

### Mandatory Verification Steps

After generating each artifact, verify it IMMEDIATELY (not at the end):

| Artifact | Verification Command | Must Pass |
|----------|---------------------|-----------|
| `setup.sh` | `bash -n setup.sh && bash setup.sh` | Exit code 0, no errors |
| `run.sh` | `bash -n run.sh` | Syntax OK (full run needs model) |
| `verify.py` | `python -c "import py_compile; py_compile.compile('verify.py', doraise=True)"` | Syntax OK |
| `*.py` (factory) | `python -c "import py_compile; py_compile.compile('<file>', doraise=True)"` | Syntax OK |
| `*.py` (app) | `PYTHONPATH=. python -c "import py_compile; py_compile.compile('<file>', doraise=True)"` | Syntax OK |
| `config.json` | `python -c "import json; json.load(open('config.json'))"` | Valid JSON |

### setup.sh Execution Test (MANDATORY)

`setup.sh` MUST be executed (not just syntax-checked) in the session directory.
If it fails:
1. Diagnose the error
2. Fix the script
3. Re-run until it passes

Common failures to test for:
- PEP 668 "externally-managed-environment" → must use venv
- `pip install <package>` for private packages → must use local install or pre-installed venv
- Relative path resolution from symlinked directories → use `$(cd "$(dirname "$0")" && pwd -P)` patterns
- Missing dependencies → verify `pip install` list is complete

### Import Resolution Test (MANDATORY for Python apps)

After all Python files are generated, run:
```bash
cd <session_dir>
python -c "from factory import <Model>Factory; print('import OK')"
```

If this fails, the factory uses an incorrect import path. Fix it before proceeding.

### session.log Must Be Real Output (MANDATORY)

`session.log` MUST contain actual terminal command output captured via:
```bash
command 2>&1 | tee session.log
```

The following patterns are PROHIBITED for session.log:
- `cat << 'EOF' > session.log` (heredoc fabrication)
- `cat << 'LOGEOF' > session.log` (heredoc fabrication)
- `echo "..." > session.log` (hand-written summary)
- `printf "..." > session.log` (hand-written summary)
- Writing session.log content from memory without running commands

### dx-tdd Invocation (MANDATORY for All Code Generation)

The `/dx-tdd` skill MUST be invoked for ALL artifact generation sessions — this
includes user-facing compilation, app generation, and pipeline tasks. It is NOT
limited to "internal development" tasks.

Its "Red-Green-Verify" cycle applies:
1. **RED**: Define what each artifact must satisfy (syntax, execution, imports)
2. **GREEN**: Generate the artifact
3. **VERIFY**: Run the check immediately after creation

This is NOT optional even in autopilot mode. Skipping dx-tdd for code generation
is a session-failing violation regardless of whether the task is "internal
development" or "user-facing."

**Rationale**: The SWE Process Gates "Mandatory Skill Sequence" is scoped to
internal dx-agentic-dev development. This Artifact Verification Gate extends
the same discipline to all generated deliverables. Without it, agents produce
untested setup.sh, broken imports, and fabricated session.log files.

## Prerequisites Check (HARD GATE)

Before generating ANY code, creating files, or routing to sub-agents, the following
environment checks MUST pass. This gate applies at the suite level — even if
brainstorming produced a spec and plan, these checks MUST execute before implementation.

```bash
# 1. dx-runtime sanity check (MANDATORY — do NOT skip)
bash dx-runtime/scripts/sanity_check.sh --dx_rt
# IMPORTANT: Judge PASS/FAIL by the TEXT OUTPUT, not the exit code.
# Agents often pipe through `| tail` or `| head`, which silently
# replaces the real exit code with tail's exit code (always 0).
# PASS = output contains "Sanity check PASSED!" and NO [ERROR] lines
# FAIL = output contains "Sanity check FAILED!" or ANY [ERROR] lines
# NEVER pipe through tail/head/grep — run the command directly.
# If FAIL → run install, then RE-CHECK:
bash dx-runtime/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse
bash dx-runtime/scripts/sanity_check.sh --dx_rt  # Must PASS after install

# 2. dx_engine import check (MANDATORY for app generation tasks)
python -c "import dx_engine; print('dx_engine OK')" 2>/dev/null || {
    echo "dx_engine not available. Run: cd dx-runtime/dx_app && ./install.sh && ./build.sh"
}

# 3. dxcom availability check (MANDATORY for compilation tasks)
python -c "import dx_com; print('dxcom OK')" 2>/dev/null || {
    echo "dxcom not available."
    # Installation fallback:
    #   1. pip install dxcom (if in venv)
    #   2. bash dx-compiler/install.sh (if available)
    #   3. source dx-compiler/venv-dx-compiler-local/bin/activate (if exists)
    # If ALL fail → STOP and inform user. NEVER proceed without dxcom.
}
```

**This is a HARD GATE:**
- Do NOT generate any implementation code until these checks pass
- Do NOT skip these checks because brainstorming or planning was completed
- Each sub-project builder also has its own Step 0 Prerequisites — those are
  ADDITIONAL checks, not replacements for these suite-level checks
- If a check fails, inform the user with the exact fix command and STOP

### dxcom Anti-Fabrication (MANDATORY for compilation tasks)

When dxcom is available and compilation proceeds:
- **NEVER fabricate dxcom API calls from memory.** Always read the toolset files:
  - CLI: `dx-compiler/.deepx/toolsets/dxcom-cli.md`
  - Python API: `dx-compiler/.deepx/toolsets/dxcom-api.md`
  - Config schema: `dx-compiler/.deepx/toolsets/config-schema.md`
- **Correct import**: `import dx_com; dx_com.compile(...)` (NOT `from dxcom import dxcom`)
- **NEVER modify `compiler.properties`** — system file managed by the installer.
  See `dx-compiler/.deepx/memory/common_pitfalls.md` Pitfalls #21 and #22.

### Background Compilation (MANDATORY — R42)

**WARNING — Synchronous `dx_com.compile()` in the main process is PROHIBITED (R42).**

Calling `dx_com.compile()` directly blocks the agent's tool-call thread for 10+ minutes.
During that time the agent cannot generate other artifacts in parallel, making it
vulnerable to timeout and missing the concurrent artifact generation requirement.

**ALWAYS use `subprocess.Popen` with a `compile.pid` file:**
```python
import subprocess, os
compile_script = f"{work_dir}/compile.py"
compile_out = open(f"{work_dir}/compile_out.log", "w")
proc = subprocess.Popen(
    ["python3", compile_script],
    stdout=compile_out, stderr=subprocess.STDOUT,
    cwd=work_dir, start_new_session=True,
)
with open(f"{work_dir}/compile.pid", "w") as f:
    f.write(str(proc.pid))
# Now generate ALL other artifacts (factory, sync.py, setup.sh, run.sh, verify.py)
# BEFORE checking compile.pid / .dxnn existence.
```

Evidence: copilot iter-11 and cursor iter-11 produced no `compile.pid` and used
synchronous compilation — this is the pattern to avoid. claude_code and opencode
(via subagent) correctly use `subprocess.Popen` + PID file.

### Sanity Check Failure Recovery (MANDATORY)

When `sanity_check.sh --dx_rt` returns FAIL, follow this exact recovery sequence:

1. **Run install.sh** with the command shown above
2. **Re-run sanity_check.sh** — the check MUST pass after install
3. **If still failing**: check whether this is a **compiler-only task** or not:

   **A. Compiler-only task** (ONNX → DXNN compilation, no dx_app/dx_stream work):
   - Inform the user that the sanity check failed and NPU-based verification will be skipped.
   - **Proceed with compilation** — `dxcom` runs on CPU and does not require NPU hardware.
   - After compilation succeeds, mark `verify.py` as **SKIPPED** (not PASS).
   - Set `DX_SANITY_FAILED=1` so verify.py can detect and skip NPU-based checks.
   - Record in session.log: `sanity_check=FAIL, compilation=<result>, verification=SKIPPED`.
   - Tell the user:
     ```
     NPU hardware initialization failed. Compilation completed successfully,
     but DXNN verification (verify.py) requires a working NPU.
     After resolving the NPU issue (cold boot recommended), run:
       cd <session_dir> && python verify.py
     ```

   **B. Cross-project task** (compilation + dx_app/dx_stream demo app) or dx_app/dx_stream only:
   - **STOP unconditionally** — even if the user says "just continue",
     "work to completion", "use defaults", or "skip checks", the agent MUST NOT
     proceed. The user's instruction to continue does NOT override this HARD GATE.
   - Guide the user through manual recovery:
     - If the failure mentions **"Device initialization failed"**, **"Fail to initialize device"**,
       or **NPU hardware errors**: the NPU requires a cold boot (full power cycle) or
       system reboot. Software-only install cannot fix hardware initialization failures.
       Tell the user:
       ```
       NPU hardware initialization failed. This issue cannot be resolved by software installation alone.
       Please follow these steps:
       1. Fully shut down the system (power off — a cold boot is recommended, not just a reboot)
       2. Wait 10-30 seconds
       3. Power on the system
       4. After restart, verify NPU status with the sanity check:
          bash dx-runtime/scripts/sanity_check.sh --dx_rt
       5. Once the sanity check PASSES, please retry this task.
       ```
     - If the failure is a different error: show the user the specific error and
       recommended fix command, then STOP.

4. **NEVER bypass** (for non-compiler-only tasks) — the sanity check exists
   to ensure the full dx-runtime environment is operational. For dx_app/dx_stream
   tasks, skipping recovery means demo/verification scripts will fail.
   The following are ALL considered bypass and are PROHIBITED:
   - Setting PYTHONPATH or LD_LIBRARY_PATH manually to point at dx_engine artifacts
   - Using a venv from another repository (e.g., compiler venv) for dx_engine imports
   - Searching multiple venvs to find one where dx_engine happens to import
   - Concluding "exit code was 0, so it passed" when output text shows FAILED or [ERROR]
   - Piping sanity_check.sh through `| tail` / `| head` / `| grep` and using the pipe's exit code
   - Reinterpreting the user's "just continue" / "work to completion" / "use defaults"
     / autopilot instructions as permission to override the HARD GATE
   - Marking the prerequisite check as "done" or "passed" when it actually failed
   Note: compiler-only tasks (item 3A above) are exempt from this STOP — compilation
   proceeds, but verification is marked SKIPPED, not PASS.
5. **Common failure causes**:
   - NPU driver not installed → `install.sh` with `dx_rt_npu_linux_driver` target
   - dx_engine build artifacts missing → `cd dx_app && ./install.sh && ./build.sh`
   - PEP 668 (Ubuntu 24.04+) blocking pip → must use venv (never `--break-system-packages`)

## Rule Conflict Resolution (HARD GATE)

When a user's request conflicts with a HARD GATE rule, the agent MUST:

1. **Acknowledge the user's intent** — Show that you understand what they want.
2. **Explain the conflict** — Cite the specific rule and why it exists.
3. **Propose the correct alternative** — Show how to achieve the user's goal
   within the framework. For example, if the user asks for direct
   `InferenceEngine.run()` usage, explain that the IFactory pattern wraps
   the same API and propose the factory-based equivalent.
4. **Proceed with the correct approach** — Do NOT silently comply with the
   rule-violating request. Do NOT present it as "Option A vs Option B".

**Common conflict patterns** (from real sessions):
- User says "use `InferenceEngine.Run()`" → Must use IFactory pattern (engine
  calls are handled internally by SyncRunner/AsyncRunner; implement the 5 IFactory
  methods: `create_preprocessor`, `create_postprocessor`, `create_visualizer`,
  `get_model_name`, `get_task_type`)
- User says "clone demo.py and swap onnxruntime" → Must use skeleton-first
  from `src/python_example/`, not clone user scripts
- User says "create demo_dxnn_sync.py" → Must use `<model>_sync.py` naming
  with SyncRunner, not a standalone script
- User says "use `run_async()` directly" → Must use AsyncRunner, not manual
  async loops

**This rule does NOT override explicit user overrides**: If the user, after being
informed of the conflict, explicitly says "I understand the rule, proceed with
direct API usage anyway", then comply. But the agent MUST explain the conflict
FIRST — silent compliance is always a violation.

## Sub-Project Development Rules (MANDATORY — SELF-CONTAINED)

These rules are **authoritative and self-contained**. They MUST be followed regardless
of whether sub-project files are loaded. In interactive mode, sub-project files are
NOT loaded due to git submodule boundaries — these rules are the ONLY protection.

**CRITICAL**: These are NOT optional summaries. Every rule below is a HARD GATE.
Violating any rule (e.g., skipping skeleton-first, not using IFactory, writing to
source directories) is a blocking error that must be corrected before proceeding.

**Additional context**: When working in a sub-project, also read that sub-project's
`CLAUDE.md` for extended context (model registry, import patterns, etc.). But the
rules below are sufficient for correct code generation even without reading
sub-project files.

### dx_app Rules (Standalone Inference)

1. **Skeleton-first development** — Read `dx-runtime/dx_app/.deepx/skills/dx-build-python-app.md`
   skeleton template BEFORE writing any code. Copy the closest existing example from
   `src/python_example/<task>/<model>/` and modify ONLY model-specific parts (factory,
   postprocessor). NEVER write demo scripts from scratch. NEVER propose standalone
   scripts that bypass the framework.
2. **IFactory pattern is MANDATORY** — All inference apps MUST use the IFactory 5-method
   pattern (create_preprocessor, create_postprocessor, create_visualizer, get_model_name, get_task_type).
   Never invent alternative inference structures. Direct `InferenceEngine` usage in
   a standalone script is a violation — it MUST go through the factory pattern.
   **Even if the user explicitly names API methods** (e.g., "use `InferenceEngine.run()`",
   "use `run_async()`"), the agent MUST wrap those calls inside the IFactory pattern
   and explain the rule to the user. See the "Rule Conflict Resolution" section.
3. **SyncRunner/AsyncRunner ONLY** — Use SyncRunner (single-model) or AsyncRunner
   (multi-model) from the framework. NEVER propose alternative execution approaches
   (standalone scripts, direct API calls, custom runners, manual `run_async()` loops).
4. **No alternative proposals** — Do NOT present "Option A vs Option B" choices for
   app architecture. The framework dictates one correct pattern per variant.
5. **Registry key ≠ class name** — Model registry keys in `model_registry.json` map
   to postprocessor classes via a lookup. Read the registry to find the correct mapping.
6. **Existing examples MANDATORY** — Before writing any new app, search
   `src/python_example/` for existing examples of the same AI task. Use them as reference.
7. **DXNN input format auto-detection** — NEVER hardcode preprocessing dimensions or
   formats. The DXNN model self-describes its input requirements via `dx_engine`.
8. **Output Isolation** — ALL generated code MUST go to `dx-agentic-dev/<session_id>/`.
   NEVER write into existing source directories (e.g., `src/`, `semseg_260323/`, or
   any directory containing user's existing code) unless the user EXPLICITLY says
   "write to the source directory".

### dx-compiler Rules (Model Compilation)

1. **Previous session reference PROHIBITED** — Never reference or reuse results from
   previous agentic sessions. Each session starts fresh.
2. **session.log = actual command output** — Session logs MUST contain real terminal
   output. NEVER generate hand-written summaries or `cat << 'EOF'` blocks.
3. **config.json schema** — Always read `dx-compiler/.deepx/toolsets/config-schema.md`
   before writing config.json. Never fabricate schema fields.
4. **dxcom fabrication patterns** — See "dxcom Anti-Fabrication" section above.
5. **setup.sh 5-step template** — Read `dx-compiler/.deepx/agents/dx-dxnn-compiler.md`
   Phase 5.5 for the mandatory setup.sh structure.

### dx_stream Rules (GStreamer Pipelines)

1. **x264enc tune=zerolatency** — Always set `tune=zerolatency` for x264enc elements.
2. **Queue between processing stages** — Always add `queue` elements between processing
   stages to prevent GStreamer deadlocks.
3. **Existing pipelines MANDATORY** — Search `pipelines/` for existing examples before
   creating new pipeline configurations.

### Common Rules (All Sub-Projects)

1. **PPU model auto-detection** — Check model name suffix (`_ppu`), README, or registry
   for PPU flag before routing or generating postprocessor code.
2. **Build order** — dx_rt → dx_app → dx_stream. Never build out of order.
3. **Sub-project context loading** — When routing to or working within a sub-project,
   ALWAYS read that sub-project's `CLAUDE.md` first.

## Plan Output (MANDATORY)

When generating a plan document (e.g., via writing-plans or brainstorming skills),
**always print the full plan content in the conversation output** immediately after
saving the file. Do NOT only mention the file path — the user should be able to
review the plan directly in the prompt without opening a separate file.


---

## SWE Process Gates — Internal Development (HARD GATE)

When any AI agent (Claude Code, Copilot CLI, Cursor CLI, Copilot Chat (VS Code),
Cursor (IDE), OpenCode, or any other tool) is used to develop or modify internal
dx-agentic-dev features, the full Software Engineering discipline is **MANDATORY**.
This applies to any task that IS or INVOLVES an internal dx-agentic-dev feature.
The following paths are covered (non-exhaustive — when in doubt, apply the SWE
discipline):

| Path | Examples |
|------|---------|
| `tests/test_agentic_e2e_scenarios/` | `conftest.py`, `test_*.py` fixtures |
| `tests/test_agentic_scenarios/` | scenario test cases |
| `tests/test.sh` | manual/autopilot shell runner |
| `tests/conftest.py`, `tests/parse_copilot_session.py` | shared test infrastructure |
| `tools/dx-agentic-dev-gen/` | generator source, CLI, transformers |
| `tools/*.sh` | loop scripts and orchestration runners (e.g. `run-e2e-improvement-loop.sh`) |
| `.deepx/` | agents, skills, templates, fragments (canonical source) |

These rules apply **in addition to** the Instruction File Verification Loop below.

### Mandatory Skill Sequence (Non-Trivial Changes)

Every non-trivial internal change MUST flow through this sequence.
**No code before this sequence completes.**

**Autopilot mode does NOT waive this sequence.** "Work autonomously" means follow
all rules without asking — NOT skip rules. In autopilot, make default decisions
using the knowledge base instead of calling `ask_user`, but every step below
still applies.

| Step | Skill | When required |
|------|-------|--------------|
| 1 | `/dx-skill-router` | **HARD GATE** — invoke BEFORE any path classification, BEFORE any SWE gate check, BEFORE any file read. No condition allows skipping or deferring this step. |
| 2 | `/dx-brainstorm-and-plan` | Any feature addition, behavior change, or structural refactor |
| 3 | `/dx-writing-plans` | When the approved plan has >2 implementation steps |
| 4 | `/dx-tdd` | All code changes — identify or write the test/validation BEFORE implementing |
| 5 | Verification loop | After every change — generator + drift check + test run |
| 6 | `/dx-verify-completion` | Before claiming done — evidence required, not assertions |

**Non-trivial judgment**: if the change touches ≥2 files OR ≥2 repos, it is
Non-trivial and the Trivial Change Exception does NOT apply. **This check is
independent of the SWE path list above** — a change to files outside the
listed paths but touching ≥2 files still requires `/dx-brainstorm-and-plan`.

### What "Test First" Means Here

`/dx-tdd` in the internal development context:

- **`tests/` changes** — run the existing suite to confirm **RED** before implementing.
  The test must fail for the expected reason before you write any code.
- **`.deepx/` changes** — capture `dx-agentic-gen check` baseline output before editing.
  After the change, re-run and confirm only the intended drift appears.
- **`tools/` changes** — identify the specific failure mode (wrong path, wrong output,
  missing rule) that the change must close. Write or point to the test that catches it.
- **`test.sh` changes** — trace the execution path manually (or `bash -n` syntax-check)
  before editing. Confirm the affected code path with `bash -x` if needed.

### Trivial Change Exception

Steps 2–3 (brainstorm/plan) may be skipped ONLY for:
- Single-line typo or wording correction
- Pure formatting change (whitespace, blank lines)
- Single variable rename with obvious, isolated root cause

Steps 4–6 (TDD, verification, completion check) are **NEVER** skipped, even for trivial changes.

### Hard Gates

| Gate | Rule |
|------|------|
| **No code without a plan** | Any change touching >1 file requires an approved plan first |
| **No feature without a failing test** | Implement only after confirming RED |
| **No "done" without evidence** | Show pytest/generator output — do not assert completion |
| **No direct edit to generated files** | `CLAUDE.md`, `AGENTS.md`, `.claude/` → edit `.deepx/` source |

### Common Anti-Patterns (PROHIBITED)

- Skipping `/dx-brainstorm-and-plan` because "the change is obvious" — it is never obvious
- Adding fixtures or changing `conftest.py` without running the test suite first (blind changes)
- Claiming completion without showing actual pytest output or `dx-agentic-gen check` output
- Treating "I'll validate at the end" as acceptable — validate file-by-file, per `/dx-tdd`
- Editing generator output files directly — they are overwritten on next `dx-agentic-gen generate`
- Starting implementation before `/dx-skill-router` has been invoked
- **Treating autopilot mode as a waiver** — autopilot means "no asking",
  NOT "no rules". The Mandatory Skill Sequence applies in full in autopilot mode.
- Treating `tools/*.sh` scripts as "not internal dev" because they are not in
  `tools/dx-agentic-dev-gen/` — all loop and orchestration scripts under `tools/`
  are internal dx-agentic-dev features and the SWE discipline applies

---

## Instruction File Verification Loop (HARD GATE) — Internal Development Only

When modifying the canonical source — files in `**/.deepx/**/*.md`
(agents, skills, templates, fragments) — the following verify-fix loop is
**MANDATORY** before claiming work is complete:

1. **Generator execution** — Propagate `.deepx/` changes to all platforms:
   ```bash
   dx-agentic-gen generate
   # Suite-wide: bash tools/dx-agentic-dev-gen/scripts/run_all.sh generate
   ```
2. **Drift verification** — Confirm generated output matches committed state:
   ```bash
   dx-agentic-gen check
   ```
   If drift is detected, return to step 1.
3. **Automated test loop** — Tests verify generator output satisfies policies:
   ```bash
   python -m pytest tests/test_agentic_scenarios/ -v --tb=short
   ```
   Failure handling:
   - Generator bug → fix generator → step 1
   - `.deepx/` content gap → fix `.deepx/` → step 1
   - Insufficient test rules → strengthen tests → step 1
4. **Manual audit** — Independently (without relying on test results) read
   generated files to verify cross-platform sync (CLAUDE vs AGENTS vs copilot)
   and level-to-level sync (suite → sub-levels).
5. **Gap analysis** — For issues found by manual audit:
   - Generator missed a case → **fix generator rules** → step 1
   - Tests missed a case → **strengthen tests** → step 1
6. **Repeat** — Continue until steps 3–5 all pass.

### Pre-flight Classification (MANDATORY)

Before modifying ANY `.md` or `.mdc` file in the repository, classify it into
one of three categories. **Never skip this step** — editing a generator-managed
file directly is a silent corruption that will be overwritten on next generate.

**Answer these three questions in order before every file edit:**

> **Q1. Is the file path inside `**/.deepx/**`?**
> - YES → **Canonical source.** Edit directly, then run `dx-agentic-gen generate` + `check`.
> - NO → go to Q2.
>
> **Q2. Does the file path or name match any of these?**
> ```
> .github/agents/    .github/skills/    .opencode/agents/
> .claude/agents/    .claude/skills/    .cursor/rules/
> CLAUDE.md          CLAUDE-KO.md       AGENTS.md    AGENTS-KO.md
> copilot-instructions.md               copilot-instructions-KO.md
> ```
> - YES → **Generator output. DO NOT edit directly.**
>   Find the `.deepx/` source (template, fragment, or agent/skill) and edit that instead,
>   then run `dx-agentic-gen generate`.
> - NO → go to Q3.
>
> **Q3. Does the file begin with `<!-- AUTO-GENERATED`?**
> - YES → **Generator output. DO NOT edit directly.** Same as Q2.
> - NO → **Independent source.** Edit directly. Run `dx-agentic-gen check` once afterward.

1. **Canonical source** (`**/.deepx/**/*.md`) — Modify directly, then run the
   Verification Loop above.
2. **Generator output** — Files at known output paths:
   `CLAUDE.md`, `CLAUDE-KO.md`, `AGENTS.md`, `AGENTS-KO.md`,
   `copilot-instructions.md`, `.github/agents/`, `.github/skills/`,
   `.claude/agents/`, `.claude/skills/`, `.opencode/agents/`, `.cursor/rules/`
   → **Do NOT edit directly.** Find and modify the `.deepx/` source
   (template, fragment, or agent/skill), then `dx-agentic-gen generate`.
3. **Independent source** — Everything else (`docs/source/`, `source/docs/`,
   `tests/`, `README.md` in sub-projects, etc.)
   → Edit directly. Run `dx-agentic-gen check` once afterward to confirm no
   unexpected drift.

**Anti-pattern**: Modifying a file without first classifying it. If you are
unsure whether a file is generator output, run `dx-agentic-gen check` before
AND after the edit — if the check overwrites your change, the file is managed
by the generator and must be edited via `.deepx/` source instead.

A pre-commit hook enforces generator output integrity: `git commit` will fail
if generated files are out-of-date. Install hooks with:
```bash
tools/dx-agentic-dev-gen/scripts/install-hooks.sh
```

This gate applies when `.deepx/` files are the *primary deliverable* (e.g., adding
rules, syncing platforms, creating KO translations, modifying agents/skills). It
does NOT apply when a feature implementation incidentally triggers a single-line
change in `.deepx/`.

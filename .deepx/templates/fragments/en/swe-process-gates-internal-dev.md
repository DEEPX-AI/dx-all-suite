## SWE Process Gates — Internal Development (HARD GATE)

When any AI agent (Claude Code, Copilot CLI, Cursor CLI, Copilot Chat (VS Code),
Cursor (IDE), OpenCode, or any other tool) is used to develop or modify internal
dx-agent-dev features, the full Software Engineering discipline is **MANDATORY**.
This applies to any task that IS or INVOLVES an internal dx-agent-dev feature.
The following paths are covered (non-exhaustive — when in doubt, apply the SWE
discipline):

| Path | Examples |
|------|---------|
| `.deepx/e2e/test_agent_e2e_scenarios/` | `conftest.py`, `test_*.py` fixtures |
| `.deepx/tests/conformance/` | KB / generated-output conformance + policy checks |
| `.deepx/e2e/test.sh` | manual/autopilot shell runner |
| `.deepx/tests/conftest.py`, `.deepx/tools/src/dx_transcripts/session_common.py`, `.deepx/tools/src/dx_transcripts/parse_copilot_session.py`, `.deepx/tools/src/dx_transcripts/parse_cursor_session.py`, `.deepx/tools/src/dx_transcripts/parse_claude_session.py` | shared test infrastructure |
| `.deepx/tools/` (dx-agent-dev-gen) | generator source, CLI, transformers |
| `.deepx/tools/scripts/*.sh` | loop scripts and orchestration runners (e.g. `run-e2e-improvement-loop.sh`, `run_all.sh`, `install-hooks.sh`, `pre-commit-hook.sh`) |
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
| 2 | `/dx-swe-brainstorm` | Any feature addition, behavior change, or structural refactor |
| 3 | `/dx-swe-writing-plans` | When the approved plan has >2 implementation steps |
| 4 | `/dx-swe-tdd` | All code changes — identify or write the test/validation BEFORE implementing |
| 5 | Verification loop | After every change — generator + drift check + test run |
| 6 | `/dx-swe-verify` | Before claiming done — evidence required, not assertions |

**Non-trivial judgment**: if the change touches ≥2 files OR ≥2 repos, it is
Non-trivial and the Trivial Change Exception does NOT apply. **This check is
independent of the SWE path list above** — a change to files outside the
listed paths but touching ≥2 files still requires `/dx-swe-brainstorm`.

### What "Test First" Means Here

`/dx-swe-tdd` in the internal development context:

- **`tests/` changes** — run the existing suite to confirm **RED** before implementing.
  The test must fail for the expected reason before you write any code.
- **`.deepx/` changes** — capture `dx-agent-gen check` baseline output before editing.
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

### "Invoke" = Actual `skill` Tool Call (MANDATORY)

"Invoke a skill" means calling the **`skill` tool** (or the platform equivalent)
to load and activate the skill. The following are NOT valid invocations:

- Writing "Using dx-swe-tdd for this task" in text → **NOT an invocation**
- Mentally deciding to follow a skill's rules → **NOT an invocation**
- Referencing a skill in a plan or description → **NOT an invocation**

Each step in the Mandatory Skill Sequence requires a real tool call. If the
`skill` tool was not called, the step was not completed.

### Pre-Implementation Checklist (MANDATORY)

Before writing ANY code (including the first `edit` or `create` call), the agent
MUST verify these conditions are met. This is a self-check — output the checklist
in the conversation:

```
SWE Pre-Implementation Checklist:
[ ] /dx-skill-router invoked (this message)
[ ] /dx-swe-brainstorm invoked AND user approved plan
[ ] /dx-swe-tdd invoked AND RED baseline captured
[ ] Files to modify identified and classified (canonical vs generated)
```

If ANY box cannot be checked, STOP and complete the missing step before proceeding.

### Common Anti-Patterns (PROHIBITED)

- Skipping `/dx-swe-brainstorm` because "the change is obvious" — it is never obvious
- Adding fixtures or changing `conftest.py` without running the test suite first (blind changes)
- Claiming completion without showing actual pytest output or `dx-agent-gen check` output
- Treating "I'll validate at the end" as acceptable — validate file-by-file, per `/dx-swe-tdd`
- Editing generator output files directly — they are overwritten on next `dx-agent-gen generate`
- Starting implementation before `/dx-skill-router` has been invoked
- **Treating autopilot mode as a waiver** — autopilot means "no asking",
  NOT "no rules". The Mandatory Skill Sequence applies in full in autopilot mode.
- Treating `.deepx/tools/scripts/*.sh` scripts as "not internal dev" — all loop and
  orchestration scripts under `.deepx/tools/scripts/` are internal dx-agent-dev
  features and the SWE discipline applies
- **Treating `dx-swe-debugging` completion as a SWE gate waiver** — finishing
  Phases 1–3 (root cause identified) does NOT exempt the implementation from the
  SWE mandatory sequence. When Phase 4 implementation involves `.deepx/`, `tests/`,
  or `tools/`, it is a **NEW internal dev task** that MUST restart the skill sequence
  from `/dx-skill-router`. See the SWE Gate Pre-Flight in `dx-swe-debugging` Phase 4.
- **Treating previous skill invocation as current-message coverage** — `/dx-skill-router`
  MUST be invoked at the start of **each user message**. Invocation in a prior message
  does NOT carry forward. "I already invoked it this session" is a rationalization.
- **Text mention ≠ skill invocation** — writing "Using dx-swe-tdd" or "Following
  dx-swe-brainstorm" in the response text is NOT the same as calling the
  `skill` tool. The skill MUST be loaded via tool call to count as invoked.
- **Conversation continuity rationalization** — "We already discussed this in
  previous messages" does NOT exempt the current feature from the full sequence.
  Each feature addition is an independent unit that requires its own brainstorm,
  plan, and TDD cycle — regardless of how much context exists in the conversation.

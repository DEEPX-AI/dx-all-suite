## SWE Process Gates — Internal Development (HARD GATE)

When any AI agent (Claude Code, Copilot CLI, Cursor CLI, Copilot Chat (VS Code),
Cursor (IDE), OpenCode, or any other tool) is used to develop or modify internal
dx-agentic-dev features, the full Software Engineering discipline is **MANDATORY**.
This applies to any task touching the following paths:

| Path | Examples |
|------|---------|
| `tests/test_agentic_e2e_scenarios/` | `conftest.py`, `test_*.py` fixtures |
| `tests/test_agentic_scenarios/` | scenario test cases |
| `tests/test.sh` | manual/autopilot shell runner |
| `tests/conftest.py`, `tests/parse_copilot_session.py` | shared test infrastructure |
| `tools/dx-agentic-dev-gen/` | generator source, CLI, transformers |
| `.deepx/` | agents, skills, templates, fragments (canonical source) |

These rules apply **in addition to** the Instruction File Verification Loop below.

### Mandatory Skill Sequence (Non-Trivial Changes)

Every non-trivial internal change MUST flow through this sequence.
**No code before this sequence completes.**

| Step | Skill | When required |
|------|-------|--------------|
| 1 | `/dx-skill-router` | **Always** — identify applicable skills before any action |
| 2 | `/dx-brainstorm-and-plan` | Any feature addition, behavior change, or structural refactor |
| 3 | `/dx-writing-plans` | When the approved plan has >2 implementation steps |
| 4 | `/dx-tdd` | All code changes — identify or write the test/validation BEFORE implementing |
| 5 | Verification loop | After every change — generator + drift check + test run |
| 6 | `/dx-verify-completion` | Before claiming done — evidence required, not assertions |

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

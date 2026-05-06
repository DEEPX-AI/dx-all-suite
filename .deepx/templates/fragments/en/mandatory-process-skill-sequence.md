## Mandatory Process Skill Sequence — All Code Generation (HARD GATE)

This gate applies to ALL sessions that generate code artifacts in
`dx-agentic-dev/<session_id>/`. It is independent of the "Internal Development"
SWE Process Gates — those apply to dx-agentic-dev infrastructure work; THIS gate
applies to user-facing code generation (inference apps, pipelines, compilation).

### When This Gate Applies

Any session that produces files in `dx-agentic-dev/<session_id>/` MUST follow
the complete process skill sequence below. This includes:
- ONNX → DXNN compilation sessions
- Python/C++ inference app generation (dx_app)
- GStreamer pipeline creation (dx_stream)
- Cross-project sessions (compile + deploy)

### Mandatory Skill Sequence

Every code generation session MUST flow through this sequence in order.
**No code generation before this sequence completes.**

**Autopilot mode does NOT waive this sequence.** "Work autonomously" means follow
all rules without asking — NOT skip rules. In autopilot, make default decisions
using the knowledge base instead of calling `ask_user`, but every step below
still applies.

| Step | Skill | Requirement |
|------|-------|-------------|
| 1 | `/dx-skill-router` | **Always** — invoke BEFORE any action. Already enforced by `skill-router-mandatory` fragment. |
| 2 | `/dx-brainstorm-and-plan` | **All non-trivial code generation** — gather requirements, propose approaches, get approval before any file creation. |
| 3 | `/dx-writing-plans` | **Always** — produce a structured implementation plan for every code generation session, regardless of complexity. |
| 4 | `/dx-tdd` | **Always** — define acceptance criteria (Red), generate artifacts (Green), verify immediately (Verify). |
| 5 | `/dx-verify-completion` | **Always** — before declaring DONE, provide evidence of working artifacts. Assertions without evidence are prohibited. |

### Sequence Enforcement Rules

1. **No skipping steps** — Each step MUST complete before the next begins.
   Exception: Step 1 (skill-router) is already handled by a separate fragment.
2. **No reordering** — brainstorm → plan → tdd → verify. Never generate code
   before planning. Never declare done before verifying.
3. **Plan MUST exist before any file creation** — Even a single-file session
   requires a plan (can be brief, but must be explicit).
4. **Verification MUST use actual execution** — `python file.py`, `bash -n script.sh`,
   `import` checks. Never claim "it should work" without running it.

### Trivial Change Exception

Steps 2–3 (brainstorm/plan) may be skipped ONLY for:
- Single config.json field change (e.g., threshold adjustment)
- Single-line typo fix in existing generated code

Steps 4–5 (tdd/verify-completion) are **NEVER** skipped, even for trivial changes.

### Autopilot Mode Adaptation

In autopilot mode (user absent, `--yolo` flag, or auto-response):
- **Step 2**: Replace `ask_user` with knowledge base defaults. Self-review spec.
- **Step 3**: Write plan and self-approve against knowledge base rules.
- **Step 4**: Define acceptance criteria from plan, generate, verify immediately.
- **Step 5**: Execute all artifacts, capture output as evidence. No human needed.

### Relationship with Artifact Verification Gate

This sequence defines **WHEN** each skill is invoked (workflow order).
The Artifact Verification Gate defines **HOW** each artifact is verified
(specific commands per file type). They work together:

- Step 4 (`/dx-tdd`) uses the verification commands from the Artifact
  Verification Gate (syntax checks, execution tests, import resolution).
- Step 5 (`/dx-verify-completion`) confirms all mandatory deliverables
  exist and pass the Artifact Verification Gate checks.

### Anti-Patterns (PROHIBITED)

- "This is simple, brainstorm is unnecessary" → brainstorm is ALWAYS required
  for non-trivial code generation. "Simple" is where unexamined assumptions
  cause the most wasted work.
- Generating code before `/dx-writing-plans` produces a plan → HARD GATE violation.
  Plan-before-code is non-negotiable.
- Skipping `/dx-verify-completion` because "artifact-verification-gate already
  checks files" → they serve different purposes. Artifact gate checks individual
  files. Verify-completion checks the ENTIRE session deliverables holistically.
- Declaring DONE without showing execution output → evidence is mandatory.
  "I verified it works" without showing the output is not acceptable.
- "The user said just do it quickly" → user instructions do NOT override this
  HARD GATE. Speed does not justify skipping process.

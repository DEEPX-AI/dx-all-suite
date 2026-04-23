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

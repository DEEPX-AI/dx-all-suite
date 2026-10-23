## Brainstorming — Spec Before Plan (HARD GATE)

Applies to **every** brainstorming entry point — the superpowers `brainstorming`
skill, `/dx-swe-brainstorm`, and `/dx-agent-brainstorm`. Which one exists depends
on the level: the suite ships both, the sub-projects ship `/dx-agent-brainstorm`
only. Reaching the spec gate is not conditional on which one you invoked.

1. **Spec document is MANDATORY** — Before transitioning to `writing-plans`, a spec
   document MUST be written to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`.
   Skipping the spec and going directly to plan writing is a violation.
2. **User approval gate is MANDATORY** — After writing the spec, the user MUST review
   and approve it before proceeding to plan writing. Do NOT treat unrelated user
   responses (e.g., answering a different question) as spec approval.
   **In autopilot (user absent, `--yolo`, auto-response), this gate is satisfied by
   writing the spec and self-reviewing it against the knowledge base** — see the
   Autopilot Mode Guard. Absence of a reviewer never waives writing the spec, and
   never blocks progress either.
3. **Plan document MUST reference the spec** — The plan header must include a link
   to the approved spec document.
4. **Prefer the project-level brainstorming skill** — `/dx-swe-brainstorm` at the
   suite, `/dx-agent-brainstorm` in a sub-project — over the generic superpowers
   `brainstorming` skill. The project-level skills carry domain-specific questions
   and pre-flight checks. Invoking the one your level ships does NOT exempt you
   from the spec gate above.
5. **Rule conflict check is MANDATORY** — During brainstorming, the agent MUST check
   whether any user requirement conflicts with HARD GATE rules (IFactory pattern,
   skeleton-first, Output Isolation, SyncRunner/AsyncRunner). If a conflict is
   detected, the agent MUST resolve it during brainstorming — not silently comply
   with the violating request in the design spec. See the "Rule Conflict Resolution" section.

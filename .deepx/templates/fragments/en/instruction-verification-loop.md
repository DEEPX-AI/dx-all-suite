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

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

**Do NOT edit platform files directly.** Files outside `.deepx/` — including
CLAUDE.md, AGENTS.md, copilot-instructions.md, `.github/agents/`,
`.github/skills/`, `.claude/agents/`, `.claude/skills/`, `.opencode/agents/`,
`.cursor/rules/` — are all generator output and will be overwritten on
next generate. A pre-commit hook enforces this: `git commit` will fail if
generated files are out-of-date. Install hooks with:
```bash
tools/dx-agentic-dev-gen/scripts/install-hooks.sh
```

This gate applies when `.deepx/` files are the *primary deliverable* (e.g., adding
rules, syncing platforms, creating KO translations, modifying agents/skills). It
does NOT apply when a feature implementation incidentally triggers a single-line
change in `.deepx/`.

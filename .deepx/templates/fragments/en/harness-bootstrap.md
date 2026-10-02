## Standalone Checkout — Harness Bootstrap (HARD GATE)

This repo is a sub-project of dx-all-suite, but it can also be cloned **on its
own**. In that standalone case the harness tooling is simply not present:

| Present in this repo | Ships only with dx-all-suite |
|---|---|
| `.deepx/{agents,skills,templates/{en,ko},scripts,memory,instructions,toolsets}` | `.deepx/tools/` — the `dx-agent-gen` generator |
| `.deepx/scripts/validate_framework.py` | `.deepx/templates/fragments/` — the shared fragments |
| this instruction file (already generated) | `.deepx/tests/conformance/` |

The Instruction File Verification Loop above tells you to run
`dx-agent-gen generate` / `check` and the conformance tests. In a standalone
checkout **none of those commands can work** — which is exactly how `.deepx/`
edits get committed unverified and become drift that only CI catches.

### Required before the FIRST `.deepx/` edit

```bash
bash .deepx/scripts/harness_bootstrap.sh --check
```

It resolves a real dx-all-suite checkout in this order — explicit
`--suite-dir` / `$DX_SUITE_DIR`, then a parent directory (the normal nested
case: nothing is downloaded), then a previously acquired `.dx-harness/suite`
cache, then a shallow clone into `.dx-harness/` — and then runs **the same
verification the CI `subrepo-gate` runs**: the generator drift check plus this
repo's `validate_framework.py`.

`.dx-harness/` is git-ignored, so nothing it downloads can reach the index.

### When it exits 3 — STOP

Exit code 3 means no suite could be acquired (no local suite, no cache, no
network). Then:

- **Do NOT edit any file under `**/.deepx/**`** in this checkout. Without the
  generator and the fragments you cannot regenerate `CLAUDE.md` / `AGENTS.md` /
  `.claude/` / `.github/` / `.cursor/` / `.opencode/`, so every edit ships as
  drift.
- **Do NOT work around it.** Specifically, if the generator reports
  `unresolved template variables` listing `FRAGMENT` placeholders, those
  fragments are **missing, not wrong**. Editing the templates, renaming
  fragments, or adding variables to `_build_template_context()` turns a missing
  input into a second, worse drift that is committed.
- Say so plainly, and offer the two documented ways forward:
  `--suite-dir /path/to/dx-all-suite`, `$DX_SUITE_DIR`, or doing the harness
  work from a full dx-all-suite checkout.

Non-harness work is unaffected: application code, `src/`, docs, tests and
`dx-agent-dev/<session_id>/` outputs proceed normally when bootstrap fails.

### Scope note

`--check` deliberately does **not** run the suite conformance suite. Those
checks are cross-level — they compare all 5 levels against each other — so they
cannot be satisfied when the other sub-repos are absent. Matching the
`subrepo-gate` scope exactly is what makes "local green" mean "CI green".

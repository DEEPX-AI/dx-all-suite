# `.deepx/` — DEEPX All Suite Agent-Driven Knowledge (Top-Level)

> Master index for the DEEPX Agent-Driven Development (`dx-agent-dev`) canonical
> source at the dx-all-suite top level.
>
> For end-user usage, see [`docs/source/00_Agent_Driven_Development.md`](../docs/source/00_Agent_Driven_Development.md).
> For a comprehensive walk-through of every `.deepx/` directory across all 5
> repos, see [`docs/dx-agent-dev-overview.md`](docs/dx-agent-dev-overview.md).

---

## 1. Purpose

The `.deepx/` directory is the **canonical source of truth (SoT)** for everything
that powers DEEPX Agent-Driven Development:

- Agent definitions (router agents, builder agents, validators)
- Skill workflows (build, validate, brainstorm, TDD, etc.)
- Instruction templates (`CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md`)
- Shared fragments injected into every platform output (4 tools × 5 repos)
- Memory (pitfalls, knowledge base entries)
- Tests (~700 conformance + ~586 E2E)
- The `dx-agent-gen` generator that fans out `.deepx/` content to all platforms

> **Never edit generator output directly.** Files like `CLAUDE.md`, `AGENTS.md`,
> `.claude/agents/`, `.github/agents/`, `.opencode/agents/`, `.cursor/rules/`
> are produced from `.deepx/`. Edit the corresponding source under `.deepx/`,
> then run `dx-agent-gen generate`.

---

## 2. The 5-Repo Layout

dx-all-suite contains five repos, each with its own `.deepx/`:

| Level | Path | Role | Sub-README |
|-------|------|------|------------|
| **Suite (this)** | `.deepx/` | Top-level routing + generator + tests | (this file) |
| **dx-runtime** | `dx-runtime/.deepx/` | Integration layer (cross-project routing/validation) | [`dx-runtime/.deepx/README.md`](../dx-runtime/.deepx/README.md) |
| **dx_app** | `dx-runtime/dx_app/.deepx/` | Standalone inference apps (Python/C++) | [`dx-runtime/dx_app/.deepx/README.md`](../dx-runtime/dx_app/.deepx/README.md) |
| **dx_stream** | `dx-runtime/dx_stream/.deepx/` | GStreamer pipelines | [`dx-runtime/dx_stream/.deepx/README.md`](../dx-runtime/dx_stream/.deepx/README.md) |
| **dx-compiler** | `dx-compiler/.deepx/` | ONNX → DXNN compilation | [`dx-compiler/.deepx/README.md`](../dx-compiler/.deepx/README.md) |

Each sub-project `.deepx/` is self-contained. This top-level `.deepx/` adds:
- Suite-wide router agents (`dx-suite-builder`, `dx-suite-validator`)
- 16 shared fragments injected into all 5 repos (rename gates, session sentinels,
  process gates, autopilot guard, etc.)
- The `dx-agent-gen` generator (single tool that processes all 5 repos)
- All agent-driven test infrastructure (`tests/` conformance + `e2e/`)

---

## 3. Directory Structure

```
.deepx/
├── README.md                    ← This file (top-level master index)
├── README-KO.md                 ← Korean translation
│
├── agents/                      ← Suite-level routing agents (2)
│   ├── dx-suite-builder.md      ← Top-level task classifier → sub-projects
│   └── dx-suite-validator.md    ← Cross-level framework validator
│
├── skills/                      ← Reusable skill workflows (14)
│   ├── dx-skill-router/         ← Meta — universal pre-flight
│   ├── dx-swe-*/                ← General SWE process (10: brainstorm/tdd/verify/…)
│   ├── dx-agent-*/            ← DEEPX-specific (3: brainstorm/tdd/verify)
│   └── dx-harness-*/            ← Internal harness dev (2: validate/writing-skills)
│
├── templates/                   ← Generator templates
│   ├── en/                      ← English instruction templates
│   │   ├── CLAUDE.md.tmpl
│   │   ├── AGENTS.md.tmpl
│   │   └── copilot-instructions.md.tmpl
│   ├── ko/                      ← Korean instruction templates
│   │   ├── CLAUDE-KO.md.tmpl
│   │   ├── AGENTS-KO.md.tmpl
│   │   └── copilot-instructions-KO.md.tmpl
│   └── fragments/               ← 32 shared fragments (16 EN + 16 KO)
│       ├── en/
│       └── ko/
│
├── memory/                      ← Persistent knowledge
│   └── sdk_grounding_reference.md   ← Anti-hallucination grounding facts
│
├── docs/                        ← Harness design docs (not auto-loaded)
│   ├── skill-architecture.md             ← 3-tier skill model
│   ├── fragment-authoring-guide.md       ← Rules for writing fragments
│   └── dx-agent-dev-overview.md        ← Comprehensive .deepx/ walk-through
│
├── tests/                       ← Suite conformance tests
│   ├── README.md                ← Test categories and how to run them
│   └── conformance/             ← ~700 static KB/generated-output policy checks (no CLI/NPU)
│
├── e2e/                         ← End-to-end harness (separated)
│   ├── e2e_runner.py · e2e_monitor.py · test.sh   ← round orchestration + runner
│   ├── test_agent_e2e_scenarios/  ← ~586 E2E tests (5 CLIs × scenarios)
│   └── agent_analyzer/        ← E2E result analyzer (reports, insights)
│
└── tools/                       ← Tooling packages + orchestration scripts
    ├── README.md                ← tooling guide
    ├── pyproject.toml           ← `dx-agent-gen` CLI; discovers both src/ packages
    ├── src/
    │   ├── dx_agent_dev_gen/  ← generator (cli, generator, transformers, frontmatter, constants)
    │   └── dx_transcripts/      ← shared session parsers + transcript renderer
    ├── tests/                   ← mirrors src/ (dx_agent_dev_gen/, dx_transcripts/)
    └── scripts/
        ├── README.md                          ← scripts/ guide
        ├── run_all.sh                         ← Multi-repo generate/check/lint
        ├── install-hooks.sh                   ← Pre-commit hook installer
        ├── pre-commit-hook.sh                 ← Drift + lint check on commit
        ├── run-e2e-improvement-loop.sh        ← Self-improving E2E loop
        ├── README_RUN_E2E_IMPROVEMENT_LOOP.md
        └── README_RUN_E2E_IMPROVEMENT_LOOP-KO.md
```

---

## 4. Canonical → Multi-Target Generation Flow

```
                    .deepx/  (canonical source)
                       │
                       │  dx-agent-gen generate
                       ▼
   ┌────────────────────────────────────────────────────────────┐
   │                                                            │
   ▼                ▼                ▼                ▼          ▼
CLAUDE.md     .github/         .claude/         .opencode/   .cursor/
AGENTS.md     copilot-         agents/          agents/      rules/
CLAUDE-KO.md  instructions.md  skills/          (config)     *.mdc
AGENTS-KO.md  agents/                                        skills
copilot-      skills/
instructions  instructions/
.md           (KO variants)
```

The generator:
1. Reads agent/skill `.md` files from `.deepx/`
2. Loads instruction templates from `.deepx/templates/{en,ko}/`
3. Resolves `{{FRAGMENT:<name>}}` placeholders against `.deepx/templates/fragments/`
4. Produces 4 platform-specific outputs (Copilot, Claude Code, OpenCode, Cursor)
5. Repeats across all 5 repos (suite + 4 sub-projects) when `run_all.sh` is used

A pre-commit hook (`scripts/pre-commit-hook.sh`) blocks `git commit` if generated
outputs drift from source.

---

## 5. Quick Start (Harness Development)

```bash
# 1. Install the generator
pip install -e .deepx/tools

# 2. Single-repo operations (from the repo root)
dx-agent-gen generate    # Regenerate platform files
dx-agent-gen check       # Verify no drift
dx-agent-gen lint        # Verify EN/KO fragment parity
dx-agent-gen prune       # Remove stale orphan outputs (renamed/removed sources)
dx-agent-gen generate --prune   # Regenerate AND self-clean orphans in one pass

# 3. Suite-wide (process all 5 repos)
bash .deepx/tools/scripts/run_all.sh generate
bash .deepx/tools/scripts/run_all.sh check
bash .deepx/tools/scripts/run_all.sh lint
bash .deepx/tools/scripts/run_all.sh prune

# 4. Install pre-commit hooks (one-time)
bash .deepx/tools/scripts/install-hooks.sh

# 5. Tests
cd .deepx/e2e
./test.sh agent-driven                          # ~700 conformance tests (~1s)
./test.sh agent-driven-e2e-claude-code-autopilot # Claude Code E2E
./test.sh agent-driven-e2e-copilot-cli-autopilot # Copilot CLI E2E
```

---

## 6. Skill Tiers (Tiered Model)

| Tier | Prefix | Scope | Example |
|------|--------|-------|---------|
| **General SWE** | `dx-swe-*` | Any SDK / docs / general coding | `dx-swe-tdd` |
| **End-User (Agent-Driven Dev)** | `dx-agent-*` | Building apps/pipelines via dx-agent-dev | `dx-agent-tdd` |
| **Harness Eng** | `dx-harness-*` | Internal `.deepx/`, `tests/`, `tools/` maintenance | `dx-harness-validate` |
| **Internal Business** | `dx-internal-*` | Internal ops that USE the harness (model/agent perf evals) | `dx-internal-model-eval` |
| **Meta** | `dx-skill-router` | Used in all tiers (universal pre-flight) | — |

`dx-agent-*` skills reference the corresponding `dx-swe-*` skill and add DEEPX-
specific content (model registry checks, sub-project routing, etc.).

See [`docs/skill-architecture.md`](docs/skill-architecture.md) for the full design.

---

## 7. Mandatory Pre-Flight (HARD GATE)

`/dx-skill-router` MUST be invoked as the **absolute first action for every user
message**. This applies to all scenarios:

| Scenario | Trigger | Mandatory Sequence |
|----------|---------|--------------------|
| **End-User** | task writes to `dx-agent-dev/<session_id>/` | router → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |
| **Harness Dev** | task touches `.deepx/`, `tests/`, `tools/` | router → `dx-swe-brainstorm` → `dx-swe-writing-plans` → `dx-swe-tdd` → `dx-swe-verify` → `dx-harness-validate` |
| **SDK Dev** | task touches SDK source / docs (general) | router → `dx-swe-brainstorm` → `dx-swe-writing-plans` → `dx-swe-tdd` → `dx-swe-verify` |

Enforced by the `mandatory-process-skill-sequence.md` and
`swe-process-gates-internal-dev.md` fragments embedded in every `CLAUDE.md` /
`AGENTS.md` / `copilot-instructions.md`.

---

## 8. Shared Fragments (16 EN + 16 KO)

Fragments are reusable rule blocks injected into instruction files across all 5
repos. Editing a fragment once propagates the change everywhere via
`dx-agent-gen generate`.

| Fragment | Purpose |
|----------|---------|
| `mandatory-process-skill-sequence` | Required skill order for code generation |
| `swe-process-gates-internal-dev` | SWE discipline for internal harness work |
| `skill-router-mandatory` | Universal pre-flight rule |
| `session-sentinels` | `[DX-AGENT-DEV: START/DONE]` markers |
| `artifact-verification-gate` | Per-artifact verification commands |
| `brainstorming-spec-before-plan` | Spec → user approval → plan order |
| `rule-conflict-resolution` | What to do when user request conflicts with HARD GATE |
| `autopilot-mode-guard` | Behavior when user is absent |
| `instruction-verification-loop` | Generator + drift check + lint loop |
| `no-placeholder-code` | TODO / stub / commented-out code prohibition |
| `experimental-features-prohibited` | Visual companion / fake features ban |
| `response-language` | EN/KO matching + technical-term rule |
| `recommended-model` | Claude Sonnet/Opus 4.6+ notice |
| `git-operations-user-handles` | Don't ask about git PRs / merges |
| `git-safety-superpowers` | docs/superpowers/ commit ban |
| `plan-output` | Print full plan in chat after saving |

See [`docs/fragment-authoring-guide.md`](docs/fragment-authoring-guide.md) for
how to add or modify a fragment.

---

## 9. Where to Read More

| Topic | Document |
|-------|----------|
| End-user usage (one-liner prompts, scenarios) | [`docs/source/00_Agent_Driven_Development.md`](../docs/source/00_Agent_Driven_Development.md) |
| Comprehensive `.deepx/` walk-through (all 5 repos) | [`docs/dx-agent-dev-overview.md`](docs/dx-agent-dev-overview.md) |
| 3-tier skill architecture and naming | [`docs/skill-architecture.md`](docs/skill-architecture.md) |
| How to author a new fragment | [`docs/fragment-authoring-guide.md`](docs/fragment-authoring-guide.md) |
| `dx-agent-gen` generator package | [`tools/README.md`](tools/README.md) |
| Operational scripts (`run_all.sh`, hooks, E2E loop) | [`tools/scripts/README.md`](tools/scripts/README.md) |
| E2E result analyzer (reports, charts, dashboard) | [`e2e/agent_analyzer/README.md`](e2e/agent_analyzer/README.md) |
| Showcase reproducibility verification (verbatim-prompt eval) | [`e2e/showcase_repro/README.md`](e2e/showcase_repro/README.md) |
| Test categories and how to run them | [`tests/README.md`](tests/README.md) |
| Sub-project specifics | the sub-project `.deepx/README.md` (linked above in §2) |

---

## 10. Showcase Reproducibility Harness (`e2e/showcase_repro/`)

`e2e/showcase_repro/` re-runs each `dx-agent-dev-showcase/<name>/` **verbatim prompt** through
autopilot coding agents (claude-code, cursor, …) and grades whether the result is *equivalent,
self-contained, and portable*. It is the **evaluation** companion to the pass/fail functional
`e2e/test_agent_e2e_scenarios/` — the two coexist (verbatim-reproduction grading vs short-prompt
smoke).

- `showcase_registry.py` is the single source of truth (per-showcase verbatim prompt · route ·
  checker · ground truth); `run_repro.py` drives an N-showcase × M-agent matrix → an archive
  `report.md` + `results.json`, reusing the e2e conftest autopilot runners.
- `checks.py` scores 3 tiers (artifacts / gates / metrics) plus a cross-cutting **portability**
  gate (must run when copied OUTSIDE the suite), and a **B2 Output-Isolation guard** auto-reverts
  any write into a source dir → verdict `EQUIVALENT` / `DEGRADED` / `FAILED` / `BLOCKED`.
- `test_checks.py` unit-tests every checker against the committed originals (regression guard);
  `test_repro_scenarios.py` is a thin **opt-in** pytest wrapper (`DX_REPRO_RUN=1`) for CI gating.

Full usage and how to add/refresh a showcase: [`e2e/showcase_repro/README.md`](e2e/showcase_repro/README.md).

---

## 11. Glossary

| Term | Meaning |
|------|---------|
| `dx-agent-dev` | The DEEPX Agent-Driven Development feature (this whole system). Also the per-session output directory: `dx-agent-dev/<session_id>/`. |
| `dx-agent-gen` | The Python CLI that fans `.deepx/` out to all platform-specific files. Package source under `tools/src/dx_agent_dev_gen/`. |
| Fragment | A reusable rule block under `.deepx/templates/fragments/{en,ko}/`. Always written in EN + KO pairs. |
| Canonical source | Files under `**/.deepx/**` — the only place to edit. |
| Generator output | Platform-specific files (`CLAUDE.md`, `.claude/`, `.github/`, `.cursor/`, `.opencode/`). Never edit directly. |
| Session sentinel | `[DX-AGENT-DEV: START]` / `[DX-AGENT-DEV: DONE]` markers used by test harness. |
| HARD GATE | A non-negotiable rule. User cannot override with "just proceed". |

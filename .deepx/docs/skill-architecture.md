# 3-Tier Skill Architecture

> Design document for the DEEPX All Suite skill naming and invocation system.

## 3-Tier Separation

Skills are organized into three tiers by naming convention:

| Tier | Prefix | Scope | Example |
|------|--------|-------|---------|
| **General SWE** | `dx-swe-*` | All development tasks (SDK, docs, general coding) | `dx-swe-tdd` |
| **End-User (Agent-Driven Dev)** | `dx-agent-*` | Building apps/pipelines via dx-agent-dev features | `dx-agent-tdd` |
| **Harness Eng** | `dx-harness-*` | Internal `.deepx/`, `tests/`, `tools/` maintenance | `dx-harness-validate` |
| **Meta** | `dx-skill-router` | Used in all tiers | — |

### Design Principles

1. **`dx-agent-*` references `dx-swe-*`** — The agent-driven skill contains
   DEEPX-specific content only and states "for general SWE process, see
   `dx-swe-*`".

2. **`dx-swe-*` is self-contained** — General SWE skills work independently
   without any DEEPX-specific context. They can be used for SDK source code
   development, documentation work, or any general coding task.

3. **`dx-harness-*` is internal-only** — These skills are never invoked for
   end-user tasks. They use internal tools (`validate_framework.py`,
   `feedback_collector.py`, `dx-agent-gen`).

4. **Domain-specific skills follow `dx-agent-{subproject}-*` convention** — Each
   sub-project's build/validate/model skills are prefixed with their sub-project
   identifier for clear namespace separation.

## Skill Inventory

### Suite Level (`.deepx/skills/`)

#### General SWE (`dx-swe-*`)

| Skill | Purpose |
|-------|---------|
| `dx-swe-brainstorm` | Collaborative design: ask → propose → approve → review |
| `dx-swe-tdd` | Red-Green-Verify cycle, Classic TDD for unit tests |
| `dx-swe-verify` | Gate Function: evidence before completion claims |
| `dx-swe-writing-plans` | Write implementation plans with bite-sized tasks |
| `dx-swe-executing-plans` | Execute plans with review checkpoints |
| `dx-swe-subagent-dev` | Execute plans via fresh subagent per task |
| `dx-swe-parallel-agents` | Dispatch parallel subagents for independent tasks |
| `dx-swe-debugging` | Systematic 4-phase root cause investigation |
| `dx-swe-receiving-review` | Evaluate code review feedback with rigor |
| `dx-swe-requesting-review` | Request code review after completing features |

#### End-User (`dx-agent-*`)

| Skill | Purpose | References |
|-------|---------|------------|
| `dx-agent-brainstorm` | Sub-project routing, model registry, Pre-Flight check | `dx-swe-brainstorm` |
| `dx-agent-tdd` | Validation Order for dx_app, dx_stream, Integration | `dx-swe-tdd` |
| `dx-agent-verify` | Checklists for dx_app, dx_stream, Cross-Project | `dx-swe-verify` |

#### Harness Eng (`dx-harness-*`)

| Skill | Purpose |
|-------|---------|
| `dx-harness-validate` | `.deepx/` framework integrity validation |
| `dx-harness-writing-skills` | Create/edit `.deepx/` skill files |

#### Meta

| Skill | Purpose |
|-------|---------|
| `dx-skill-router` | Skill discovery and invocation routing |

### Sub-Project Level

Sub-project skills follow the same naming convention. Key differences:

- **`dx-agent-*`** at sub-project level contains project-specific details
  (e.g., dx_app's `dx-agent-tdd` has 133-model validation details)
- **`dx-swe-*`** at sub-project level are typically identical to suite level
- **Domain-specific skills** are unique per sub-project

### Domain-Specific Skills (by Sub-Project)

#### dx-compiler Domain Skills

| Skill | Purpose |
|-------|---------|
| `dx-agent-compiler-compile` | Step-by-step ONNX to DXNN compilation workflow |
| `dx-agent-compiler-convert` | Step-by-step PyTorch to ONNX conversion workflow |
| `dx-agent-compiler-validate` | Validate compiled .dxnn model output |

#### dx-runtime Domain Skills

| Skill | Purpose |
|-------|---------|
| `dx-agent-runtime-validate` | Validate, collect feedback, apply fixes, verify |

#### dx_app Domain Skills

| Skill | Purpose |
|-------|---------|
| `dx-agent-app-build-python` | Build Python inference app (IFactory + SyncRunner) |
| `dx-agent-app-build-cpp` | Build C++ inference app |
| `dx-agent-app-build-async` | Build async high-performance app (AsyncRunner) |
| `dx-agent-app-model-management` | Download and configure models |
| `dx-agent-app-validate` | Run dx_app validation checks |

#### dx_stream Domain Skills

| Skill | Purpose |
|-------|---------|
| `dx-agent-stream-build-pipeline` | Build GStreamer pipeline app |
| `dx-agent-stream-build-mqtt-kafka` | Build MQTT/Kafka pipeline app |
| `dx-agent-stream-model-management` | Download and configure models |
| `dx-agent-stream-validate` | Run dx_stream validation checks |

## Mandatory Skill Sequences

### End-User Scenario

Triggered when: task produces files in `dx-agent-dev/<session_id>/`

```
dx-skill-router
  → dx-agent-brainstorm    (routes to sub-project, refs dx-swe-brainstorm)
  → dx-swe-writing-plans
  → dx-agent-tdd           (refs dx-swe-tdd)
  → dx-agent-{subproject}-* (domain build skills: compile, build-python, etc.)
  → dx-agent-verify        (refs dx-swe-verify)
```

**Enforced by:** `mandatory-process-skill-sequence.md` fragment (path match:
`dx-agent-dev/<session_id>/`)

### SDK Development Scenario

Triggered when: task modifies SDK source, docs, or general code (NOT
`.deepx/`, `tests/`, `tools/`, or `dx-agent-dev/`)

```
dx-skill-router
  → dx-swe-brainstorm
  → dx-swe-writing-plans
  → dx-swe-tdd
  → dx-swe-verify
```

**Enforced by:** No specific fragment — general SWE best practice. Skills
are invoked by the agent based on `dx-skill-router` guidance.

### Harness Development Scenario

Triggered when: task modifies `.deepx/`, `tests/`, `tools/` paths

```
dx-skill-router
  → dx-swe-brainstorm
  → dx-swe-writing-plans
  → dx-swe-tdd
  → dx-swe-verify
  → dx-harness-validate      (+ validate_framework.py, dx-agent-gen check)
```

**Enforced by:** `swe-process-gates-internal-dev.md` fragment (path match:
`.deepx/`, `.deepx/tests/test_agent_*/`, `.deepx/tools/`)

## Scenario Classification

Classification is NOT done by `dx-skill-router` — it's determined by **path
matching** in instruction fragments embedded in `AGENTS.md` / `CLAUDE.md`:

| Fragment | Path Match | Scenario |
|----------|-----------|----------|
| `mandatory-process-skill-sequence.md` | `dx-agent-dev/<session_id>/` | End-User |
| `swe-process-gates-internal-dev.md` | `.deepx/`, `tests/`, `tools/` | Harness Dev |
| Neither matches | — | SDK Dev (General) |

## Reference Pattern

`dx-agent-*` skills reference `dx-swe-*` directly:

```markdown
# dx-agent-tdd

> For the general Red-Green-Verify cycle, see `dx-swe-tdd`.
> This skill adds DEEPX build-specific validation order and checks.

## Validation Order — dx_app
...
```

This keeps DEEPX-specific content in one place and general SWE process in
another. When the general process evolves, only `dx-swe-tdd` needs updating.

## Harness File Layout

All harness development files live under `.deepx/`:

```
.deepx/
  agents/           — agent definitions (canonical source)
  docs/             — harness design documents (this file)
  memory/           — knowledge base
  skills/           — skill definitions (canonical source)
  templates/        — generator templates + fragments
  tests/            — suite conformance tests
    conftest.py           — agent-driven marker registration + collect_ignore
    conformance/          — static KB/generated-output policy checks
  e2e/              — end-to-end harness (separated)
    e2e_runner.py · e2e_monitor.py · test.sh   — round orchestration + runner
    test_agent_e2e_scenarios/   — E2E agent execution tests
    agent_analyzer/     — run-id-aware result analyzer
  tools/            — tooling packages + dev scripts
    README.md                     — tooling guide
    pyproject.toml                — package definition; discovers both src/ packages
    src/dx_agent_dev_gen/       — generator package (cli, generator, transformers, frontmatter, constants)
    src/dx_transcripts/           — shared session parsers + transcript renderer
    tests/                        — mirrors src/ (dx_agent_dev_gen/, dx_transcripts/)
    scripts/
      README.md                       — scripts/ guide
      run_all.sh                      — multi-repo generate/check/lint wrapper
      install-hooks.sh                — pre-commit hook installer
      pre-commit-hook.sh              — drift + lint guard (invoked by git)
      run-e2e-improvement-loop.sh     — E2E improvement loop runner
      README_RUN_E2E_IMPROVEMENT_LOOP.md
      README_RUN_E2E_IMPROVEMENT_LOOP-KO.md
```

Product test infrastructure remains at `tests/` (Docker, local install,
getting-started tests). `dx-agent-dev/e2e-tests/` remains at its current
location (test data and results, not harness source code).

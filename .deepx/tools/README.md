# `.deepx/tools/` — DEEPX Agent-Driven Development Generator

> The `dx-agent-gen` Python CLI that transforms `.deepx/` canonical source
> into platform-specific files for Claude Code, GitHub Copilot, Cursor, and
> OpenCode across all 5 dx-all-suite repos.

---

## 1. Overview

`dx-agent-gen` is the **single tool** responsible for everything under the
generator boundary:

- Reading agents/skills from `.deepx/agents/` and `.deepx/skills/`
- Resolving fragment placeholders (`{{FRAGMENT:<name>}}`) against
  `.deepx/templates/fragments/{en,ko}/`
- Rendering 4 platform outputs per repo (Copilot, Claude Code, OpenCode, Cursor)
- Verifying outputs are in sync (`check`) and EN/KO fragments are consistent (`lint`)

It is installed once and used across all 5 repos in dx-all-suite.

---

## 2. Package Layout

```
.deepx/tools/
├── README.md                      ← This file
├── README-KO.md                   ← Korean translation
├── pyproject.toml                 ← Package definition; `packages.find where=["src"]` discovers BOTH packages
├── src/
│   ├── dx_agent_dev_gen/        ← Generator package
│   │   ├── __init__.py
│   │   ├── cli.py                 ← `dx-agent-gen` entry point
│   │   ├── generator.py           ← Core generate/check/lint/prune orchestration
│   │   ├── transformers.py        ← Per-platform output transformers
│   │   ├── frontmatter.py         ← YAML frontmatter handling
│   │   └── constants.py           ← Platform paths, repo definitions
│   └── dx_transcripts/            ← Shared session-parsing + transcript-rendering library
│       ├── session_common.py      ← shared session model/utilities
│       ├── parse_{claude,codex,copilot,cursor,opencode}_session.py
│       ├── generate_transcripts.py ← DONE-line transcript renderer (run by the session sentinel)
│       └── backfill_claude_html.py
├── tests/                         ← Mirrors src/ — each tool's tests beside its package
│   ├── dx_agent_dev_gen/        ← test_generator.py, test_generator_lint.py
│   └── dx_transcripts/            ← test_parse_*, test_generate_transcripts
└── scripts/                       ← Operational scripts (see scripts/README.md)
    ├── run_all.sh
    ├── install-hooks.sh
    ├── pre-commit-hook.sh
    └── run-e2e-improvement-loop.sh
```

> **Two packages, one workspace.** `dx_agent_dev_gen` is the generator;
> `dx_transcripts` is the session-parsing/transcript library shared by the
> session-sentinel DONE-line generation, the e2e harness (`.deepx/e2e/`), and the
> analyzer. Both are discovered by `packages.find where=["src"]`. Tests live in
> `tools/tests/<package>/` mirroring `tools/src/<package>/`.

---

## 3. Module Responsibilities

### `cli.py`
Entry point exposed via `pyproject.toml` as `dx-agent-gen`. Parses arguments
and dispatches to the `generate`, `check`, `lint`, or `prune` action in `generator.py`.

```bash
dx-agent-gen generate [--repo <path>] [--prune] [--dry-run]
dx-agent-gen check    [--repo <path>]
dx-agent-gen lint     [--repo <path>]
dx-agent-gen prune    [--repo <path>] [--dry-run]
```

Without `--repo`, the CLI operates on the current working directory's `.deepx/`.

### `generator.py`
Core orchestration:
1. Walks `.deepx/agents/` and `.deepx/skills/` to discover sources
2. Loads `.deepx/templates/{en,ko}/*.tmpl`
3. Resolves `{{FRAGMENT:<name>}}` placeholders against
   `.deepx/templates/fragments/{en,ko}/<name>.md`
4. Invokes per-platform transformers from `transformers.py`
5. Writes outputs to known target paths and (in `check` mode) compares against
   the committed state

### `transformers.py`
One transformer per platform, encoding platform-specific conventions:

| Platform | Output Targets |
|----------|----------------|
| Claude Code | `CLAUDE.md`, `.claude/agents/`, `.claude/skills/` (thin wrappers) |
| GitHub Copilot | `.github/copilot-instructions.md`, `.github/agents/`, `.github/skills/`, `.github/instructions/` |
| OpenCode | `AGENTS.md`, `opencode.json`, `.opencode/agents/` |
| Cursor | `.cursor/rules/*.mdc` with `alwaysApply` / `globs` metadata |

Each transformer:
- Reads canonical `.md` files (with YAML frontmatter)
- Applies platform-specific frontmatter (e.g., Cursor `globs`, Copilot agent fields)
- Writes to the target location with a `<!-- AUTO-GENERATED -->` header

### `frontmatter.py`
Parses/serializes the YAML frontmatter at the top of each agent/skill file. The
frontmatter carries the skill `name`, `description`, and platform-specific
fields (e.g., Cursor `globs`).

### `constants.py`
Declares:
- Target file/directory paths for each platform
- The 5-repo set (suite, dx-runtime, dx-runtime/dx_app, dx-runtime/dx_stream, dx-compiler)
- File patterns for the lint EN/KO parity check

---

## 4. CLI Commands

### `generate`
Regenerate all platform-specific files for the target repo.

```bash
# In a repo root:
dx-agent-gen generate

# Or explicitly:
dx-agent-gen generate --repo /abs/path/to/repo

# Suite-wide (all 5 repos):
bash .deepx/tools/scripts/run_all.sh generate
```

Effects:
- Overwrites `CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md` (+KO variants)
- Overwrites all files under `.claude/agents/`, `.claude/skills/`,
  `.github/agents/`, `.github/skills/`, `.opencode/agents/`, `.cursor/rules/`
- Each output begins with `<!-- AUTO-GENERATED -->` (Cursor `.mdc` excepted)

### `check`
Verify generated outputs are up-to-date without modifying them.

```bash
dx-agent-gen check
```

- Exit code 0 + `All generated files are up-to-date.` → OK
- Exit code != 0 + `CHANGED:` / `MISSING:` lines → drift detected

The pre-commit hook (`scripts/pre-commit-hook.sh`) calls this on every `git
commit` and blocks the commit on drift.

### `lint`
Verify EN/KO fragment parity and "no Korean in EN files" rule.

```bash
dx-agent-gen lint
```

Checks:
1. Every `.deepx/templates/fragments/en/<name>.md` has a matching
   `.deepx/templates/fragments/ko/<name>.md`
2. EN file line count does not exceed KO by ≥ 10 lines (indicates KO drift)
3. No Korean characters in EN/non-KO files (except where annotated with
   `<!-- KOREAN-OK: <reason> -->`)

See [`../docs/fragment-authoring-guide.md`](../docs/fragment-authoring-guide.md)
for the full rule set.

### `prune`
Remove **stale orphan outputs** — platform files the generator no longer produces
because their `.deepx/` source was renamed or removed. `check` cannot catch these
(it only verifies files it *would* generate), so a rename leaves the old output behind.

```bash
dx-agent-gen prune --dry-run     # list what would be removed (recommended first)
dx-agent-gen prune               # delete the orphans
bash .deepx/tools/scripts/run_all.sh prune   # suite-wide

# Or fold it into generate so a rename self-cleans in one pass:
dx-agent-gen generate --prune
dx-agent-gen generate --prune --dry-run    # preview generate + prune together
```

Safety — prune only deletes inside locations the generator solely owns, matched by
generator-specific patterns, and absent from the current expected output set:
- skill dirs `.github/skills/<name>/`, `.claude/skills/<name>/` (one dir == one skill)
- cursor skill rules `.cursor/rules/skill-*.mdc` (the `skill-` prefix is ours)
- agent files `.github/agents/*.agent.md`, `.claude/agents/*.md`, `.opencode/agents/*.md`
- cursor agent rules `.cursor/rules/<stem>.mdc` **only if they carry the
  `AUTO-GENERATED` header** — so hand-authored `.mdc` rules are never touched

---

## 5. Fragment Resolution

Templates contain placeholders like:

```
{{FRAGMENT:mandatory-process-skill-sequence}}
```

When generating for an EN target (e.g., `CLAUDE.md`), the generator resolves
this against `.deepx/templates/fragments/en/mandatory-process-skill-sequence.md`.
For KO targets (`CLAUDE-KO.md`), it resolves against
`.deepx/templates/fragments/ko/mandatory-process-skill-sequence.md`.

A missing KO counterpart **silently breaks the KO output** (the placeholder
disappears or shows as raw text). The `lint` action catches this, and
`fragment-authoring-guide.md` Rule 1 mandates EN+KO pairs.

---

## 6. Editing Workflow

```
1. Edit .deepx/ source              ← canonical
2. dx-agent-gen generate           ← propagate
3. dx-agent-gen check              ← verify (must be clean)
4. dx-agent-gen lint               ← verify EN/KO parity
5. git commit                        ← pre-commit hook runs check + lint again
```

Skipping step 2 is the most common source of silent corruption: edits to
generated files (`CLAUDE.md`, etc.) are overwritten on the next `generate`.

### Pre-flight File Classification

Before editing any `.md`:

| Question | YES → | NO → |
|----------|-------|------|
| Is the path inside `**/.deepx/**`? | **Canonical** — edit directly | go to next |
| Is it a known generator output path? | **Generated** — edit `.deepx/` source instead | go to next |
| Does it begin with `<!-- AUTO-GENERATED`? | **Generated** — same as above | **Independent** — edit directly |

Generated paths: `CLAUDE.md`, `CLAUDE-KO.md`, `AGENTS.md`, `AGENTS-KO.md`,
`copilot-instructions.md`, `copilot-instructions-KO.md`, `.github/agents/`,
`.github/skills/`, `.claude/agents/`, `.claude/skills/`, `.opencode/agents/`,
`.cursor/rules/`.

---

## 7. Installation

```bash
# Install the CLI (editable mode — changes to src/ take effect immediately)
pip install -e .deepx/tools

# Verify installation
dx-agent-gen --help
```

Python 3.10+ required. Dependencies (installed automatically):
- `jinja2 >= 3.1` — template rendering
- `pyyaml >= 6.0` — YAML frontmatter

---

## 8. Extending the Generator

### Adding a new platform target

1. Add a transformer class to `transformers.py` that takes an agent/skill
   source and writes to the new platform's directory layout.
2. Register the transformer in `generator.py`'s dispatch table.
3. Add target paths to `constants.py`.
4. Run `dx-agent-gen generate` and verify the new outputs.

### Adding a new fragment

See [`../docs/fragment-authoring-guide.md`](../docs/fragment-authoring-guide.md).

### Adding a new skill or agent

1. Write the canonical `.md` under `.deepx/skills/<name>/SKILL.md` or
   `.deepx/agents/<name>.md`.
2. Run `dx-agent-gen generate` — platform-specific copies appear automatically.

---

## 9. Testing the Generator

```bash
# Suite-wide conformance tests (~700, ~1s)
cd .deepx/e2e
./test.sh agent-driven

# What this checks (relevant to the generator):
# - Guide document structure: existence, headings, scenario numbering
# - Routing consistency: CLAUDE.md, AGENTS.md, copilot-instructions.md
# - Scenario references: agent/skill names match actual infrastructure
# - Cross-project scenarios: handoff chains, validation scripts
```

---

## 10. Related Documents

| Topic | Document |
|-------|----------|
| Top-level `.deepx/` index | [`../README.md`](../README.md) |
| Operational scripts (`run_all.sh`, hooks, E2E loop) | [`scripts/README.md`](scripts/README.md) |
| Skill 3-tier architecture | [`../docs/skill-architecture.md`](../docs/skill-architecture.md) |
| Fragment authoring rules | [`../docs/fragment-authoring-guide.md`](../docs/fragment-authoring-guide.md) |
| End-user feature documentation | [`../../docs/source/00_Agent_Driven_Development.md`](../../docs/source/00_Agent_Driven_Development.md) |
| Comprehensive `.deepx/` walk-through | [`../docs/dx-agent-dev-overview.md`](../docs/dx-agent-dev-overview.md) |

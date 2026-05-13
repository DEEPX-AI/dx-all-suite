---
name: dx-codex-identity
description: >
  ALWAYS active when running as OpenAI Codex CLI. Establishes your agent identity
  as 'codex' for session directory naming and artifact generation. This skill
  applies to EVERY task without exception.
---

# Codex CLI Agent Identity

You are running as **OpenAI Codex CLI** — the 5th supported AI coding agent in the
DEEPX Agentic Development framework.

## Agent Identifier (MANDATORY)

When creating session directories, use `codex` as your `<agent>` identifier:

```
YYYYMMDD-HHMMSS_codex_<model>_<task>
```

**Examples:**
- `20260513-100000_codex_yolo26n_compile`
- `20260513-100000_codex_yolo26n_inference`

**NEVER** use `copilot`, `cursor`, `claude`, or `opencode` as the agent identifier.
You are Codex CLI — always use `codex`.

## Session ID Generation

```bash
SESSION_ID="$(date +%Y%m%d-%H%M%S)_codex_${MODEL_NAME}_${TASK}"
```

## Knowledge Base

The DEEPX Agentic Development knowledge base is in `.deepx/` at each project level:
- `.deepx/agents/` — agent definitions
- `.deepx/skills/` — skill instructions (read with `cat`)
- `.deepx/memory/` — common pitfalls and patterns
- `.deepx/toolsets/` — API references (dxcom, dx_engine)

To read a skill: `cat .deepx/skills/<skill-name>/SKILL.md`

## Tool Availability

Standard shell tools are available: `bash`, `python3`, `find`, `grep`, `cat`, `sed`.
Note: `rg` (ripgrep) may not be available — use `grep -r` instead.

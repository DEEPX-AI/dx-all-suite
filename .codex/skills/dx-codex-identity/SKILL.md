---
name: dx-codex-identity
description: >
  ALWAYS active when running as OpenAI Codex CLI. Establishes your agent identity
  as 'codex' for session directory naming and artifact generation. This skill
  applies to EVERY task without exception.
---

# Codex CLI Agent Identity

You are running as **OpenAI Codex CLI** — the 5th supported AI coding agent in the
DEEPX Agent-Driven Development framework.

## Agent Identifier (MANDATORY)

When creating session directories, use `codex` as your `<agent>` identifier:

```
YYYYMMDD-HHMMSS_codex_<coding_model>_<target_model>_<task>
```

- **`<coding_model>`**: your AI model name, shortened — e.g., `gpt53codex` for gpt-5.3-codex, `gpt55` for gpt-5.5
- **`<target_model>`**: the inference model being compiled/deployed — e.g., `yolo26n`, `plantseg`

**Examples:**
- `20260513-100000_codex_gpt53codex_yolo26n_compile`
- `20260513-100000_codex_gpt53codex_yolo26n_inference`

**NEVER** use `copilot`, `cursor`, `claude`, or `opencode` as the agent identifier.
You are Codex CLI — always use `codex`.

**NEVER** confuse the coding model (gpt-5.3-codex) with the target model (yolo26n).
The coding model is YOUR model. The target model is the user's inference model.

## Session ID Generation

```bash
SESSION_ID="$(date +%Y%m%d-%H%M%S)_codex_gpt53codex_${TARGET_MODEL}_${TASK}"
```

## Knowledge Base

The DEEPX Agent-Driven Development knowledge base is in `.deepx/` at each project level:
- `.deepx/agents/` — agent definitions
- `.deepx/skills/` — skill instructions (read with `cat`)
- `.deepx/memory/` — common pitfalls and patterns
- `.deepx/toolsets/` — API references (dxcom, dx_engine)

To read a skill: `cat .deepx/skills/<skill-name>/SKILL.md`

## Tool Availability

Standard shell tools are available: `bash`, `python3`, `find`, `grep`, `cat`, `sed`.
Note: `rg` (ripgrep) may not be available — use `grep -r` instead.

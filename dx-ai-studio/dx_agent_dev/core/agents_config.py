"""Per-agent CLI and model settings.

Checked against the installed CLIs (claude/copilot/cursor-agent/opencode) and the codex docs; claude and copilot
last refreshed 2026-09-30. Vendors change their model lists often, so this table is **date-sensitive**. It is
only a fallback: agents that can be queried always prefer the live CLI result (see environment.agent_model_info):
  cursor    `cursor-agent --list-models`
  opencode  `opencode models`
  copilot   ACP `session/new`, the models this account may use (adapters/copilot.py). The table here is the
            fallback and also the full list, so models missing from the account show as visible but not selectable.
claude and codex have no models-list command, so the static list is the only source; claude therefore puts the
aliases first (the CLI always resolves them to the newest model).
"""

AGENTS = {
    "copilot": {
        "cli_bin": "copilot",
        # Fallback + "everything" list. The live list comes from ACP per account (adapters/copilot.py);
        # this is that list as measured 2026-09-30 (copilot CLI 1.0.89, a company account) plus the
        # older ids other accounts may still have. Default "auto": which models an account may use
        # differs per plan and org policy, so a fixed default can be refused for an account. The live
        # default (currentModelId) replaces it.
        "models": [
            "auto",
            "claude-sonnet-5.5", "claude-sonnet-5", "claude-opus-5.5", "claude-opus-5",
            "claude-opus-4.8", "claude-opus-4.7", "claude-haiku-4.5",
            "claude-fable-5.1", "claude-fable-5", "claude-sonnet-4.6", "claude-opus-4.6",
            "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra",
            "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.6-sol", "gpt-5.5", "gpt-5.4", "gpt-5.4-mini",
            "gpt-5.3-codex", "gpt-5-mini",
            "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash",
            "grok-4.7", "grok-4.6", "grok-4.5",
            "mai-code-1.1-flash",
        ],
        "default_model": "auto",
        "output_format": "text",
        # copilot CLI: `--effort/--reasoning-effort <level>` — verbatim from `copilot --help`:
        # none|low|medium|high|xhigh|max.
        "reasoning_efforts": ["none", "low", "medium", "high", "xhigh", "max"],
        "default_effort": "medium",
    },
    "codex": {
        "cli_bin": "codex",
        # codex CLI not installed here → web-verified only (not runtime-checked). Current
        # gpt-5-codex/gpt-5 entries were stale; replaced with the live gpt-5.4/5.5/5.6 family.
        "models": ["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.5", "gpt-5.4", "gpt-5.4-mini"],
        "default_model": "gpt-5.6-terra",
        "output_format": "json",
        # codex has NO --effort flag; effort is a config override on `codex exec`:
        # `-c model_reasoning_effort=<level>` (see adapters/codex.py). Levels per docs.
        "reasoning_efforts": ["minimal", "low", "medium", "high", "xhigh"],
        "default_effort": "medium",
    },
    "claude": {
        "cli_bin": "claude",
        # claude CLI has no model-list command; `--model` accepts an alias ('opus','sonnet','fable',
        # 'haiku') or a full name. The aliases come first: the CLI resolves them to the newest model
        # of that family, so they stay current when this table does not. Full names as of
        # 2026-09-30 (Fable 5.1 · Opus 5.5 · Sonnet 5.5 · Haiku 4.5), then the previous generation.
        "models": [
            "opus", "sonnet", "fable", "haiku",
            "claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-4-5",
            "claude-fable-5", "claude-opus-5", "claude-sonnet-5",
            "claude-opus-4-8", "claude-opus-4-7", "claude-sonnet-4-6",
        ],
        "default_model": "claude-sonnet-5-5",
        "output_format": "stream-json",
        # `claude --effort <level>` — verbatim from `claude --help`: low|medium|high|xhigh|max.
        "reasoning_efforts": ["low", "medium", "high", "xhigh", "max"],
        "default_effort": "medium",
    },
    "opencode": {
        "cli_bin": "opencode",
        # Lists dynamically via `opencode models` (OpenCodeAdapter.list_models) — this static
        # list is only the fallback when that call fails/times out. Refreshed to include the
        # claude-sonnet-5 + gpt-5.6-* family (verified live via `opencode models`).
        # Default matches the original harness (.deepx/e2e/test.sh:
        # DX_AGENT_E2E_OPENCODE_MODEL=github-copilot/claude-sonnet-4.6).
        "models": [
            "github-copilot/claude-sonnet-4.6", "github-copilot/claude-sonnet-5",
            "github-copilot/claude-opus-4.6", "github-copilot/claude-opus-4.8",
            "github-copilot/gpt-5.2", "github-copilot/gpt-5.6-terra", "github-copilot/gpt-5.6-sol",
        ],
        "default_model": "github-copilot/claude-sonnet-4.6",
        "output_format": "text",
        # opencode CLI: `--variant <level>` — provider-specific reasoning effort, NOT a fixed
        # enum (varies per model). Best-effort common set; don't over-promise xhigh/max — some
        # providers only expose a subset. CLI errors on an unsupported variant for a given model.
        "reasoning_efforts": ["minimal", "low", "medium", "high", "max"],
        "default_effort": "high",
    },
    "cursor": {
        "cli_bin": "cursor-agent",
        # Enumerated dynamically via `cursor-agent --list-models` (CursorAdapter.list_models,
        # runtime-verified — returns 200+ real model IDs). This static list is only the
        # fallback when that call fails/times out. The old "sonnet-4.6" entry was a FAKE id
        # that does not exist in the real catalog — removed.
        "models": ["auto", "claude-sonnet-5-medium", "gpt-5.3-codex", "claude-opus-4-8"],
        "default_model": "auto",
        "output_format": "stream-json",
        # cursor-agent: effort via bracket override e.g. claude-sonnet-5[effort=high], OR baked
        # into the model id itself (e.g. claude-sonnet-5-high). Levels vary per model family —
        # not uniform (some expose none/low/medium/high/xhigh/max, others fewer). Best-effort
        # superset here; CLI errors if a level isn't valid for the selected family.
        "reasoning_efforts": ["none", "low", "medium", "high", "xhigh", "max"],
        "default_effort": "medium",
    },
}

# Short model names for the session_id. Unlisted models use the full name.
MODEL_SHORT = {
    "claude-fable-5": "fable5",
    "claude-opus-4-8": "opus48",
    "claude-opus-4-7": "opus47",
    "claude-opus-4-6": "opus46",
    "claude-sonnet-5": "sonnet5",
    "claude-sonnet-4-6": "sonnet46",
    "claude-sonnet-4-5": "sonnet45",
    "claude-haiku-4-5": "haiku45",
    # copilot dotted-version variants (same tiers, different string form)
    "claude-opus-4.5": "opus45",
    "claude-opus-4.6": "opus46",
    "claude-opus-4.7": "opus47",
    "claude-opus-4.8": "opus48",
    "claude-sonnet-4": "sonnet4",
    "claude-sonnet-4.5": "sonnet45",
    "claude-sonnet-4.6": "sonnet46",
    "claude-haiku-4.5": "haiku45",
    "gpt-5-codex": "gpt5codex",
    "gpt-5": "gpt5",
    "gpt-5-mini": "gpt5mini",
    "gpt-5.2": "gpt52",
    "gpt-5.2-codex": "gpt52codex",
    "gpt-5.3-codex": "gpt53codex",
    "gpt-5.4": "gpt54",
    "gpt-5.4-mini": "gpt54mini",
    "gpt-5.4-nano": "gpt54nano",
    "gpt-5.5": "gpt55",
    "gpt-5.6-luna": "gpt56luna",
    "gpt-5.6-sol": "gpt56sol",
    "gpt-5.6-terra": "gpt56terra",
    "anthropic/claude-sonnet-4-6": "sonnet46",
    "openai/gpt-5": "gpt5",
    "github-copilot/claude-sonnet-4.6": "sonnet46",
    "github-copilot/claude-sonnet-5": "sonnet5",
    "sonnet-4.6": "sonnet46",
}

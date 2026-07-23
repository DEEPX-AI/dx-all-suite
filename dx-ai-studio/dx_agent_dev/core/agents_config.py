"""에이전트별 CLI/모델 설정 테이블.

verified 2026-07-19 against installed CLIs (claude/copilot/cursor-agent/opencode) + codex docs
(codex CLI 미설치 → web-verified, 실행 미검증). 모델 목록은 각 벤더가 수시로 변경하므로
**날짜에 민감**하다 — 이 테이블은 폴백일 뿐, 동적 조회(list_models)가 가능한 agent
(cursor/opencode)는 항상 실 CLI 결과를 우선한다(environment.list_agent_models 참고).
정기적으로(또는 배포마다) 일반망에서 재검증해 이 표를 갱신할 것.
copilot/claude/codex는 CLI에 models-list 커맨드가 없어 정적 목록이 유일한 소스다.
"""

AGENTS = {
    "copilot": {
        "cli_bin": "copilot",
        # copilot has no model-list command (only `--model` + BYOK `providers`); static set
        # derived from the live GitHub Copilot catalog (the github-copilot/* provider that
        # `opencode models` enumerates, prefix stripped — the copilot CLI accepts these bare).
        # Default matches the original harness (.deepx/e2e/test.sh:
        # DX_AGENT_E2E_COPILOT_MODEL=claude-sonnet-4.6).
        "models": [
            "auto",
            "claude-fable-5",
            "claude-haiku-4.5",
            "claude-opus-4.5", "claude-opus-4.6", "claude-opus-4.7", "claude-opus-4.8",
            "claude-sonnet-4", "claude-sonnet-4.5", "claude-sonnet-4.6", "claude-sonnet-5",
            "gpt-4.1", "gpt-5-mini", "gpt-5.2", "gpt-5.2-codex", "gpt-5.3-codex",
            "gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano", "gpt-5.5",
            "gpt-5.6-luna", "gpt-5.6-sol", "gpt-5.6-terra",
            "gemini-2.5-pro", "gemini-3-flash-preview", "gemini-3.1-pro-preview", "gemini-3.5-flash",
            "kimi-k2.7-code", "mai-code-1-flash-picker",
        ],
        "default_model": "claude-sonnet-4.6",
        "output_format": "text",
        # copilot CLI: `--effort/--reasoning-effort <level>` — verbatim from `copilot --help`:
        # none|low|medium|high|xhigh|max (previously missing "none").
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
        # claude CLI has no model-list command; `--model` accepts an alias ('opus','sonnet',
        # 'haiku','fable') or a full name. Full current catalog (claude-api skill is authoritative,
        # cross-checked against `claude --help`).
        "models": [
            "claude-fable-5",
            "claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6",
            "claude-sonnet-5", "claude-sonnet-4-6", "claude-sonnet-4-5",
            "claude-haiku-4-5",
        ],
        "default_model": "claude-sonnet-4-6",
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

# session_id 짧은형 매핑(spec §10). 미등록 모델은 원문 사용.
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

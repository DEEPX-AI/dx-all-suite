---
name: dx-internal-model-eval
description: >
  Internal skill — evaluate and compare coding-agent / model performance via the e2e-test
  autopilot harness. Use when comparing coding agents (claude-code vs copilot vs cursor vs
  opencode vs codex), comparing models (e.g. a new frontier model vs the existing one,
  "opus4.8 vs fable5"), or comparing thinking / reasoning-effort levels (TH vs NTH).
  Triggers (EN): "model eval", "coding agent comparison", "frontier model", "thinking mode comparison".
  Triggers (KO): "신규/프론티어 모델 성능 비교", "thinking 모드 비교", "reasoning effort 비교", "e2e 비교평가".  <!-- KOREAN-OK: KO trigger phrases enable Korean-prompt auto-detection -->
  Explicit: /dx-internal-model-eval.
---

# Skill: dx-internal-model-eval

> Internal-business skill. Drives the existing tools (`.deepx/e2e/e2e_runner.py`,
> `.deepx/e2e/agent_analyzer/`) — it does not reimplement them. Full detail in
> `reference.md` (`reference-KO.md` for Korean). Ledger contract in `registry-schema.md`.

## When to use — three eval purposes

| Purpose | Mechanism |
|---------|-----------|
| Coding-agent comparison | `e2e_runner --tools <all>` → multi-tool analyze |
| Model comparison (new frontier vs existing) | `e2e_runner --<tool>-model OLD` vs `NEW` → 2 run_ids → build_comparison |
| Thinking / reasoning-effort comparison | `e2e_runner --thinking` vs non → build_comparison |

## Procedure (one cycle)

1. Confirm: purpose, tool scope (`--tools`), OLD/NEW model ids (hyphen for claude CLI,
   dot for copilot), round count, thinking on/off.
2. Run each model/condition via the resilient controller (auto-recovers from usage limits):
   `python3 .deepx/e2e/e2e_resilient_run.py --tool claude-code --model <id> --rounds N [--thinking]`
   (wraps e2e_runner with redo-env-failures + wait-for-reset + --resume; see reference.md "Usage-limit resilience"). Record each run_id ↔ model.
3. Analyze each run_id, **writing into the durable archive** (never the gitignored worktree):
   `python3 analyze.py --run-id <RID> --output-dir "$DX_MODEL_EVAL_ARCHIVE/<label>/"`
   where `DX_MODEL_EVAL_ARCHIVE` defaults to `$HOME/shared/coding_agent_diff_report`.
4. Compare: `build_comparison.py` between the two report dirs (mind the Thinking/Non-Thinking
   label caveat — see reference.md), or multi-run analyze.
5. Bundle raw results for durability: `python3 .deepx/e2e/bundle_raw_results.py
   --results-dir <results/<run_id>> --out "$DX_MODEL_EVAL_ARCHIVE/<label>/raw/"` (excludes
   `.dxnn`/`venv`/`*.onnx`; see reference.md for the symlink/scattered-dir rationale).
6. Append one ledger row per cycle per `registry-schema.md`.

## Hard rules

- Reports + bundles ALWAYS go to `$DX_MODEL_EVAL_ARCHIVE` (worktree-local
  `dx-agent-dev/e2e-tests/` is gitignored and lost on worktree cleanup).
- Attribute models by `run_id`, NOT the CSV `model` column (it can fall back to config
  default — see reference.md §6.2).
- Do not change `analyze.py`'s built-in default output dir; override per-invocation.

## See also
- `reference.md` / `reference-KO.md` — full command reference, caveats, past-report index.
- `registry-schema.md` — ledger columns + append procedure.

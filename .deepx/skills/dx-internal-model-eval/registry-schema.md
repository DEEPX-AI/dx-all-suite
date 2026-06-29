# Model-eval registry (ledger) — schema & append procedure

**Live data file (NOT git-versioned):** `$DX_MODEL_EVAL_ARCHIVE/MODEL_EVAL_REGISTRY.md`
(default `$HOME/shared/coding_agent_diff_report/MODEL_EVAL_REGISTRY.md`). This file is the
durable, cross-cycle index; only THIS schema is git-versioned.

## Columns

| Column | Meaning |
|--------|---------|
| `date` | YYYY-MM-DD (system local) of the eval cycle |
| `purpose` | `agent` / `model` / `thinking` |
| `comparison` | e.g. `opus4.8 vs fable5 (NTH)` |
| `tool_scope` | e.g. `claude-code` / `all-5` |
| `run_ids` | `OLD=<rid> NEW=<rid>` (models attributed by run_id, not CSV model col) |
| `rounds` | e.g. `1-10` |
| `overall_delta` | per-tool Overall OLD→NEW (e.g. `claude-code 72→78`) |
| `cost` | estimated USD (from analyzer) |
| `report` | relative link into `$DX_MODEL_EVAL_ARCHIVE/<label>/comprehensive_report.html` |
| `notes` | gotchas (e.g. model-label fallback, env failures) |

## Append procedure (per cycle)

1. Compute the row values from the analyzer report (`per_session.csv` / `analysis.json`).
2. Append exactly one markdown table row to the live file (create the file with the header
   above if absent). Never rewrite prior rows.
3. The `report` link is relative to the archive root so it resolves from the registry's dir.

## Example row

| 2026-06-12 | model | opus4.8 vs fable5 (NTH) | claude-code | OLD=20260612_aaa NEW=20260612_bbb | 1-10 | claude-code 74→79 | $X.XX | ./20260612_opus48_vs_fable5_NTH/comprehensive_report.html | model attributed by run_id |

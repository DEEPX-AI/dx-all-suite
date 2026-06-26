# `showcase_repro` — Showcase Reproducibility Verification

Re-runs each `dx-agent-dev-showcase/<name>/` **verbatim prompt** through autopilot coding
agents (claude-code, cursor, …) and scores whether the result is *equivalent* to the
checked-in showcase. Answers: "if an end user types the showcase prompt, do they get an
equivalent, self-contained, portable result?"

This is the **evaluation** companion to `../test_agent_e2e_scenarios/` (which is a
pass/fail functional smoke of the agent harness using short hardcoded prompts). They
**coexist** — different purpose: verbatim-reproduction grading vs functional smoke.

## Files
| file | role |
|------|------|
| `showcase_registry.py` | single source of truth: per-showcase `prompt` (verbatim) · `route` · `checker` · `ground_truth` · `active` |
| `checks.py` | per-type checkers (`export`/`squat`/`stretch`/`ocr`/`generic_app`/`retrain_eval`) → 3 tiers (artifacts/gates/metrics) + cross-cutting **portability** gate; `evaluate_showcase()` → verdict |
| `isolation.py` | Output-Isolation guard helpers (escaping-symlink + source-reference) used by the driver |
| `run_repro.py` | the N-showcase × M-agent matrix driver → archive `report.md` + `results.json`; reuses the e2e conftest autopilot runners; B2 Output-Isolation guard + auto-revert |
| `test_checks.py` | unit tests — every original showcase self-verifies EQUIVALENT (regression guard for the checkers) |
| `test_repro_scenarios.py` | **thin pytest wrapper** (opt-in via `DX_REPRO_RUN=1`) — one test per (active showcase × agent) asserting `verdict != FAILED`, for CI gating |

## Verdict tiers
`EQUIVALENT` (all 3 tiers within tolerance) · `DEGRADED` (artifacts ok, a gate/metric short)
· `FAILED` (core artifact missing/broken) · `BLOCKED` (agent CLI unavailable — env, not a repro failure).
A cross-cutting **portability** gate (static + copy-outside-the-suite) and the **B2
Output-Isolation guard** (auto-revert any write into a source dir) apply to every showcase.

## Run a cycle
```bash
# fast: confirm the checkers still recognize the committed originals
python -m pytest .deepx/e2e/showcase_repro/test_checks.py -q

# evaluation matrix (real autopilot runs → archive report)
python .deepx/e2e/showcase_repro/run_repro.py \
    --showcases mini-game-squat-fitness,ultralytics-yolo-deepx-export \
    --agents claude-code,cursor \
    --archive "$HOME/shared/coding_agent_diff_report/showcase_repro/<label>"
#   --dry-run  : print the matrix, run nothing
# CI gating (opt-in, heavy): DX_REPRO_RUN=1 python -m pytest .deepx/e2e/showcase_repro/test_repro_scenarios.py
```
Reports/raw bundles go to `$DX_MODEL_EVAL_ARCHIVE` (default `~/shared/coding_agent_diff_report`) —
the worktree-local `dx-agent-dev/` output is gitignored and lost on cleanup.

## Add / refresh a showcase (per release)
1. Add (or update) the entry in `showcase_registry.py`: the **verbatim** prompt (from the
   showcase's `claude-code-session.md`, NOT the abbreviated README — the full prompt can hide
   an input path), `route`, `checker`, `active=True`. Make code/model input paths
   **suite-root-relative** (`dx-agent-dev-showcase/<name>/sample/...`); a build-time `/tmp/...`
   path breaks a fresh end user.
2. If a new app type, implement its `checker` in `checks.py` (ground truth from the showcase's
   `report.md`/`metrics.json`/`session.log`) and register it in `_CHECKERS`.
3. Add a RED unit test in `test_checks.py`: the committed original self-verifies EQUIVALENT.
4. Run `run_repro.py --showcases <name> --agents claude-code,cursor`.

## Cautions
- **Self-contained & portable is the bar**: the produced app must run when copied OUTSIDE the
  suite — vendor the pipeline (`./common`, a fork's `engine/`/`rapid_doc/`) INTO the session;
  never in-place-import a showcase, symlink a source dir, or point a model dir at the source.
- **Do NOT pre-run sanity/setup** for the agent — whether it resolves prereqs inside the prompt
  is part of the test.
- **Retrain showcases** need GPU (40-epoch train) + NPU (INT8); ~1h+ each; "equivalent" = the
  4-way table (base/retrained × fp32-GPU/INT8-NPU mAP+FPS) reproduced with the documented
  accuracy-gain trend, NOT exact numbers (training is nondeterministic).
- **Cross-project (suite) showcases** split artifacts across a compiler + an app session dir —
  the driver scores the **union** of a cell's output dirs, and an mtime fallback recovers a
  cell's dir(s) even when the agent mislabels the session id with another agent's name (so a
  truly-incomplete run still fails, while a merely-split-or-mislabeled one is scored correctly).

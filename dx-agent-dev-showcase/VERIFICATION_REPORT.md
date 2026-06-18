# Showcase Verification + KB-Fix Resolution Report

**Date**: 2026-06-18 · **Branch**: `feature/frontier-model-eval`

## Part 1 — End-user verification (7 showcases, baseline)

Ran each showcase's README procedure (`setup.sh` → `run.sh`) headless as an end user.
(braintumor + pills excluded — user verified manually.)

| Showcase | Baseline | Defect class |
|---|:---:|---|
| ultralytics-yolo-deepx-export | ✅ PASS | — |
| ultralytics-retrain-eval-…-wildlife | ✅ PASS | — (self-contained pipeline) |
| mini-game-squat-fitness | ❌ | A — run.sh model discovery |
| mini-game-stretching-coach | ❌ | B — setup.sh dx_engine bridge |
| ultralytics-retrain-eval-…-ppe | ❌ | C — train_result.json absolute path |
| paddleocr-video-ocr | ⚠️ ENV | sdk.deepx.ai CDN blocked (not a defect) |
| rapiddoc-pdf2md | ⚠️ ENV | sdk.deepx.ai CDN blocked (not a defect) |

## Part 2 — Fix strategy: KB, not artifacts

Per user direction, the fix targets the **knowledge base** so that re-running each
showcase's build prompt regenerates a correct, relocatable showcase — then regenerate
and confirm. Plus a `dx-showcase-gen verify` regression gate. (paddleocr/rapiddoc = ENV,
out of scope.)

**verify gate (C)** — `dx_showcase_gen` now statically fails three regressions:
`runsh_model_discovery_broken` (empty-default `${VAR:-}/assets/models`),
`setupsh_local_venv_without_bridge` (local venv, no `.pth`), `scan_nonportable(strict=True)`
(build-session `dx-agent-dev/<ts>_` + `/tmp`, skips ephemeral dirs). RED baseline on the
current artifacts matched exactly: squat→model FAIL, stretching→bridge FAIL, ppe→portable
FAIL; yolo-export + wildlife → all PASS (no false positives).

**KB patterns (A)** — dx_app `dx-agent-app-build-python` SKILL (run.sh canonical
model-resolution + setup.sh venv-search broadening + dx_engine bridge .pth),
`ultralytics-train-eval.md` §6 relocatable HARD GATE, `dx-agent-showcase-build` rule 10.

## Part 3 — Regeneration via build prompt (gold standard) — ALL RESOLVED

Each showcase rebuilt via `claude -p "<README ## The prompt>" --model claude-opus-4-8`
in this worktree (fixed KB), then gate-checked + run end-user (relocated simulation).

| Showcase | Gate (3 detectors) | End-user run | Notes |
|---|:---:|:---:|---|
| **squat** (A) | ✅ all clean | ✅ relocated, 313f @31.4 FPS | model via correct `$RUNTIME_DIR/dx_app/assets/models` |
| **stretching** (B) | ✅ all clean | ✅ 721f @33 FPS, `[OK] dx_engine` | setup.sh reuses venv-dx-runtime (no FATAL) |
| **ppe** (C) | ✅ all clean | ✅ self-contained pipeline ran, 4-way report | `pipeline.py` HERE-relative, weights bundled |

### Key finding — prose KB notes are insufficient; concrete patterns work
- **squat (A)**: the first rebuild **reproduced** the `${DX_APP_ROOT:-}/assets/models`
  ancestor-walk despite the prose anti-pattern note → gate caught it. Strengthening the KB
  with a **forceful canonical run.sh model-resolution block + WRONG/RIGHT example** changed
  the agent's behavior → second rebuild clean. (Validates the gate as a real backstop.)
- **stretching (B)**: fixed first try — the setup.sh **template code** change (broaden venv
  search + bridge `.pth`) propagated directly into the generated script.
- **ppe (C)**: fixed first try — §6 prose worked because it gave a **concrete pattern**
  (the wildlife self-contained `pipeline.py`, regenerate-if-missing, HERE-relative).

**Lesson**: KB fixes that change agent output reliably = template code or a concrete
copy-paste pattern; a "don't do X" prose note alone is insufficient — pair it with the
verify gate.

## Status
- Phase 1–3 complete on `feature/frontier-model-eval`. Conformance + tools tests: **709
  passed**; generator drift **0** across 5 levels; KO lint **[OK]**.
- **ENV-deferred**: paddleocr-video-ocr, rapiddoc-pdf2md — re-verify on a network that can
  reach `sdk.deepx.ai`.
- **Optional follow-up**: consolidate the regenerated artifacts INTO the committed showcase
  dirs (full re-promotion via dx-agent-showcase-build: transcript/GIF/README/regen-docs).
  The KB fix already guarantees correct *future* end-user regenerations.

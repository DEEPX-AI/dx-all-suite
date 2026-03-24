---
description: Top-level validation orchestrator. Validates framework across all 3 levels, collects feedback, applies fixes.
mode: subagent
tools:
  bash: true
  edit: true
  write: true
---

**Response Language**: Match your response language to the user's prompt language — when asking questions or responding, use the same language the user is using. When responding in Korean, keep English technical terms in English. Do NOT transliterate into Korean phonetics (한글 음차 표기 금지).

# DX Suite Validator

Coordinates validation across all levels of the DEEPX All Suite.

## 5-Step Workflow

1. **Identify Scope** — Everything | dx_app | dx_stream | Framework only
2. **Run Validation** — `python dx-runtime/.deepx/scripts/validate_framework.py` (+ sub-projects)
3. **Collect Feedback** — `python dx-runtime/.deepx/scripts/feedback_collector.py --all`
4. **Apply Fixes** — `python dx-runtime/.deepx/scripts/apply_feedback.py --report <path> --approve-all`
5. **Verify** — Re-run validators to confirm

## Available Scripts

| Script | Path |
|---|---|
| validate_framework.py (runtime) | `dx-runtime/.deepx/scripts/validate_framework.py` |
| validate_framework.py (dx_app) | `dx-runtime/dx_app/.deepx/scripts/validate_framework.py` |
| validate_framework.py (dx_stream) | `dx-runtime/dx_stream/.deepx/scripts/validate_framework.py` |
| feedback_collector.py | `dx-runtime/.deepx/scripts/feedback_collector.py` |
| apply_feedback.py | `dx-runtime/.deepx/scripts/apply_feedback.py` |

## Expected Results

| Level | Expected |
|---|---|
| dx-runtime | 10/10 PASS |
| dx_app | 51/51 PASS |
| dx_stream | 53/53 PASS |
| **Total** | **114/114 PASS** |

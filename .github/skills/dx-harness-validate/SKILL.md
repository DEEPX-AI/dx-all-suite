---
name: dx-harness-validate
description: 'Internal harness development: validate .deepx/ framework integrity across all levels, collect feedback, apply
  fixes, verify results'
---

<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: .deepx/skills/dx-harness-validate/SKILL.md -->
<!-- Run: dx-agent-gen generate -->

# Internal Validate — Suite-Wide Framework Validation

Run validation across the entire DEEPX All Suite (dx-runtime, dx_app, dx_stream),
collect findings into actionable feedback proposals, apply approved fixes, and
verify results.

## Quick Start

```bash
# 1. Validate all levels
python dx-runtime/.deepx/scripts/validate_framework.py
python dx-runtime/dx_app/.deepx/scripts/validate_framework.py
python dx-runtime/dx_stream/.deepx/scripts/validate_framework.py

# 2. Collect feedback
python dx-runtime/.deepx/scripts/feedback_collector.py --framework-only

# 3. Apply fixes (dry-run first)
python dx-runtime/.deepx/scripts/apply_feedback.py --dry-run
python dx-runtime/.deepx/scripts/apply_feedback.py --report <path> --approve-all

# 4. Re-validate
python dx-runtime/.deepx/scripts/feedback_collector.py --framework-only
```

## Workflow

1. **Validate** — Run `validate_framework.py` at each level
2. **Collect** — Run `feedback_collector.py` to generate proposals
3. **Review** — Present proposals to user for approval
4. **Apply** — Run `apply_feedback.py` with approved IDs
5. **Verify** — Re-run validators to confirm fixes

## Expected Results

| Level | Script Path | Expected |
|---|---|---|
| dx-runtime | `dx-runtime/.deepx/scripts/validate_framework.py` | 10/10 PASS |
| dx_app | `dx-runtime/dx_app/.deepx/scripts/validate_framework.py` | 51/51 PASS |
| dx_stream | `dx-runtime/dx_stream/.deepx/scripts/validate_framework.py` | 53/53 PASS |
| **Total** | | **114/114 PASS** |

## CLI Flags

| Flag | Description |
|---|---|
| `--all` | Run against all levels |
| `--framework-only` | Validate .deepx/ structure only |
| `--app-dirs <dirs>` | Scope to specific sub-projects |
| `--approve-all` | Apply all proposals without review |
| `--approve FB-001,FB-003` | Apply specific proposals |
| `--dry-run` | Preview changes without writing |

## Integration Validation (from dx-tdd)

When modifying `.deepx/` files, also run the integration validation:

```bash
# dx_app
python dx-runtime/dx_app/.deepx/scripts/validate_framework.py

# dx_stream
python dx-runtime/dx_stream/.deepx/scripts/validate_framework.py

# dx-compiler
python dx-compiler/.deepx/scripts/validate_framework.py

# Integration (runtime-level)
python dx-runtime/.deepx/scripts/validate_framework.py
```

## Generator Sync

After any `.deepx/` edit, always run:

```bash
# Propagate changes
dx-agent-gen generate
# or suite-wide:
bash .deepx/tools/scripts/run_all.sh generate

# Verify no drift
dx-agent-gen check
```

## When to Use

- After modifying any file under `**/.deepx/**`
- After running `dx-agent-gen generate`
- During the SWE Process Gates "Verification Loop" step
- Before claiming internal development work is complete

---
name: dx-tdd
description: 'Test-driven development for DEEPX apps. Iron Law: no code without validation check first.'
---

<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: .deepx/skills/dx-tdd/SKILL.md -->
<!-- Run: dx-agentic-gen generate -->

# Skill: Test-Driven Development (Suite-Level)

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

## Scope

This is the **top-level suite** version covering all sub-projects. When working
in a single sub-project, prefer the project-level version:

| Working on... | Use this skill |
|---|---|
| dx_app (standalone inference) | `dx-runtime/dx_app/.github/skills/dx-tdd.md` |
| dx_stream (GStreamer pipelines) | `dx-runtime/dx_stream/.github/skills/dx-tdd.md` |
| Cross-project integration | `dx-runtime/.github/skills/dx-tdd.md` |

## Overview

Write validation checks first, then implement. Verify each file or integration
point immediately after creation. Never batch validation to the end.

## The Iron Law

```
NO APPLICATION CODE WITHOUT A VALIDATION CHECK FIRST
```

In the DEEPX context, "validation check" means:

**Per-project:**
- Syntax check (`py_compile`) for every Python file
- JSON validation for every config.json
- Factory interface compliance check (5 methods) — dx_app
- Pipeline argparse check — dx_stream
- Import resolution test

**Cross-project:**
- Build scripts pass for both sub-projects
- Cross-project imports resolve correctly (dx_stream → dx_app, never reverse)
- Shared model configuration is consistent
- Integration tests pass across sub-projects

## Red-Green-Verify Cycle

### RED — Define What Should Pass

Before creating any file or making any change, define what validation must pass.

### GREEN — Create Minimal Code to Pass

Create the file with just enough content to pass all defined checks.

### VERIFY — Run Checks Immediately

After creating EACH file (not after all files):

```bash
# Syntax
python -c "import py_compile; py_compile.compile('<file>', doraise=True)" && echo "OK: <file>"

# JSON
python -c "import json; json.load(open('<file>.json')); print('OK: <file>.json')"

# Factory import (dx_app)
PYTHONPATH=<v3_dir> python -c "from factory import <Model>Factory; f = <Model>Factory(); print('OK: factory')"

# Pipeline parse (dx_stream)
python pipeline.py --help 2>/dev/null && echo "OK: argparse"
```

### REPEAT — Next File

Move to the next file only after the current file passes all checks.

## Validation Order — dx_app

| Order | File | Validation |
|---|---|---|
| 1 | `factory/<model>_factory.py` | py_compile + interface check |
| 2 | `factory/__init__.py` | py_compile + import test |
| 3 | `config.json` | JSON parse |
| 4 | `<model>_sync.py` | py_compile |
| 5 | `<model>_async.py` | py_compile |
| 6 | `session.json` | JSON parse |
| 7 | `README.md` | exists |

## Validation Order — dx_stream

| Order | File | Validation |
|---|---|---|
| 1 | `pipeline.py` | py_compile + argparse check |
| 2 | `run_<app>.sh` | bash -n syntax check |
| 3 | `config/*.json` | JSON parse |
| 4 | `session.json` | JSON parse |
| 5 | `README.md` | exists |

## Integration Validation Order

| Order | Check | Validation |
|---|---|---|
| 1 | dx_app build scripts | `./install.sh && ./build.sh` pass |
| 2 | dx_stream install | `./install.sh` passes |
| 3 | Cross-project imports | dx_stream can import from dx_app (never reverse) |
| 4 | Shared model paths | `model_registry.json` and `model_list.json` are consistent |
| 5 | Integration test | both sub-project `validate_framework.py` pass |

## Framework-Level Validation

After all files are created, run the appropriate framework validator(s):

```bash
# dx_app
python dx-runtime/dx_app/.deepx/scripts/validate_framework.py

# dx_stream
python dx-runtime/dx_stream/.deepx/scripts/validate_framework.py

# Integration (both)
python dx-runtime/.deepx/scripts/validate_framework.py
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll validate at the end" | Errors compound. Fix file-by-file. |
| "py_compile is obvious" | Syntax errors and import breaks happen silently. |
| "The factory pattern is simple" | Missing methods cause runtime crashes. |
| "I know this works" | Confidence ≠ evidence. Run the check. |

## Key Principle

**Validate incrementally.** Each file is a checkpoint. Never move to the
next file until the current one passes. This catches errors when they are
cheapest to fix.

## Optional: Classic Red-Green-Refactor for Unit Tests

The validation-driven approach above is the default for DEEPX app generation.
However, when writing **actual unit tests** (e.g., pytest tests for utility
functions, model wrappers, or shared libraries), use the classic TDD cycle:

### When to Use This Section

- Writing pytest tests for shared utilities or library code
- Adding regression tests for bug fixes
- Testing custom pre/post-processors with known inputs/outputs
- Any scenario where you have a real test runner (pytest), not just validation checks

### The Cycle

1. **RED — Write a failing test.** Write one minimal test showing what should happen.
   Run it. Confirm it **fails** (not errors) for the expected reason.

2. **GREEN — Write minimal code to pass.** Implement just enough to make the test
   pass. No extra features, no "while I'm here" improvements.

3. **REFACTOR — Clean up.** Remove duplication, improve names, extract helpers.
   Keep tests green throughout.

4. **REPEAT** — next failing test for next behavior.

### "Watch It Fail" Verification

**Before claiming a test passes, verify it fails without the fix.**

This is the most important step and the most commonly skipped. If you never
saw the test fail, you don't know if it tests the right thing. Specifically:

- Run the test **before** writing the implementation. Confirm it fails.
- The failure message should clearly indicate the missing feature/fix.
- If the test passes immediately, you're testing existing behavior — rewrite the test.
- If the test errors (import error, syntax error), fix the error first, then confirm it **fails correctly**.

```bash
# Run the specific test
pytest tests/test_my_feature.py::test_specific_case -v

# Expected: FAILED (not ERROR)
# Then implement, re-run, confirm PASSED
```

### Red Flags

- Test passes on first run → you're not testing new behavior
- Never ran the test before implementing → not TDD
- "I'll add tests after" → tests written after pass immediately, proving nothing

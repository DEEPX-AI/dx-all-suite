---
name: dx-swe-tdd
description: 'Test-driven development. Iron Law: no code without validation check first.'
---

<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: .deepx/skills/dx-swe-tdd/SKILL.md -->
<!-- Run: dx-agent-gen generate -->

# Skill: Test-Driven Development

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

## Overview

Write validation checks first, then implement. Verify each file or component
immediately after creation. Never batch validation to the end.

## The Iron Law

```
NO APPLICATION CODE WITHOUT A VALIDATION CHECK FIRST
```

"Validation check" means verifying each artifact immediately after creation:

- Syntax check (`py_compile`) for every Python file
- JSON validation for every config/data file
- Shell script syntax (`bash -n`) for every shell script
- Import resolution test for every module

## Red-Green-Verify Cycle

### RED — Define What Should Pass

Before creating any file or making any change, define what validation must pass.

### GREEN — Create Minimal Code to Pass

Create the file with just enough content to pass all defined checks.

### VERIFY — Run Checks Immediately

After creating EACH file (not after all files):

```bash
# Python syntax
python -c "import py_compile; py_compile.compile('<file>', doraise=True)" && echo "OK: <file>"

# JSON
python -c "import json; json.load(open('<file>.json')); print('OK: <file>.json')"

# Shell script syntax
bash -n <script>.sh && echo "OK: <script>.sh"
```

### REPEAT — Next File

Move to the next file only after the current file passes all checks.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll validate at the end" | Errors compound. Fix file-by-file. |
| "py_compile is obvious" | Syntax errors and import breaks happen silently. |
| "I know this works" | Confidence ≠ evidence. Run the check. |

## Key Principle

**Validate incrementally.** Each file is a checkpoint. Never move to the
next file until the current one passes. This catches errors when they are
cheapest to fix.

## Optional: Classic Red-Green-Refactor for Unit Tests

The validation-driven approach above is the default for artifact generation.
However, when writing **actual unit tests** (e.g., pytest tests for utility
functions, wrappers, or shared libraries), use the classic TDD cycle:

### When to Use This Section

- Writing pytest tests for shared utilities or library code
- Adding regression tests for bug fixes
- Testing custom processors with known inputs/outputs
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

---
name: dx-verify-completion
description: 'Verify before claiming completion. Iron Law: no claims without fresh evidence.'
---

<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: .deepx/skills/dx-verify-completion/SKILL.md -->
<!-- Run: dx-agentic-gen generate -->

# Skill: Verify Before Completion (Suite-Level)

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

## Scope

This is the **top-level suite** version covering all sub-projects. When working
in a single sub-project, prefer the project-level version:

| Working on... | Use this skill |
|---|---|
| dx_app (standalone inference) | `dx-runtime/dx_app/.github/skills/dx-verify-completion.md` |
| dx_stream (GStreamer pipelines) | `dx-runtime/dx_stream/.github/skills/dx-verify-completion.md` |
| Cross-project integration | `dx-runtime/.github/skills/dx-verify-completion.md` |

## Overview

Never claim any task is complete without running verification commands
and confirming their output. Evidence before assertions, always.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this response, you cannot
claim it passes.

## The Gate Function

```
BEFORE claiming any build is complete:

1. IDENTIFY: What commands prove this claim?
2. RUN: Execute ALL verification commands (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim
```

## Verification Checklist — dx_app Python Apps

```bash
# 1. Syntax check all Python files
for f in factory/*_factory.py *_sync.py *_async.py; do
    [ -f "$f" ] && python -c "import py_compile; py_compile.compile('$f', doraise=True)" && echo "OK: $f"
done

# 2. JSON validation
python -c "import json; json.load(open('config.json')); print('OK: config.json')"
python -c "import json; json.load(open('session.json')); print('OK: session.json')"

# 3. Factory compliance (5 methods)
PYTHONPATH=<v3_dir> python -c "
from factory import <Model>Factory
f = <Model>Factory()
for m in ['create_preprocessor','create_postprocessor','create_visualizer','get_model_name','get_task_type']:
    assert hasattr(f, m), f'Missing {m}'
print(f'OK: {f.get_model_name()} / {f.get_task_type()}')
"

# 4. Framework validator
python dx-runtime/dx_app/.deepx/scripts/validate_framework.py
```

## Verification Checklist — dx_stream Pipelines

```bash
# 1. Python syntax
python -c "import py_compile; py_compile.compile('pipeline.py', doraise=True)" && echo "OK: pipeline.py"

# 2. Shell script syntax
bash -n run_*.sh && echo "OK: shell scripts"

# 3. JSON configs
for f in config/*.json session.json; do
    [ -f "$f" ] && python -c "import json; json.load(open('$f')); print('OK: $f')"
done

# 4. Pipeline parse test
python pipeline.py --help 2>/dev/null && echo "OK: argparse"

# 5. Framework validator
python dx-runtime/dx_stream/.deepx/scripts/validate_framework.py
```

## Verification Checklist — Cross-Project Integration

```bash
# 1. dx_app framework validator
python dx-runtime/dx_app/.deepx/scripts/validate_framework.py && echo "OK: dx_app framework"

# 2. dx_stream framework validator
python dx-runtime/dx_stream/.deepx/scripts/validate_framework.py && echo "OK: dx_stream framework"

# 3. Cross-project imports
python -c "
from dx_app.src.python_example.common.utils.model_utils import load_model_config
print('OK: dx_stream can import from dx_app')
"

# 4. Shared model configuration consistency
python -c "
import json
app_reg = json.load(open('dx-runtime/dx_app/config/model_registry.json'))
stream_list = json.load(open('dx-runtime/dx_stream/model_list.json'))
print(f'OK: dx_app has {len(app_reg)} models, dx_stream has {len(stream_list)} models')
"

# 5. Build order verification (dx_app first, then dx_stream)
cd dx-runtime/dx_app && ./install.sh && ./build.sh && echo "OK: dx_app build"
cd dx-runtime/dx_stream && ./install.sh && echo "OK: dx_stream install"
```

## Red Flags — STOP

- Using "should pass", "probably works", "looks correct"
- Expressing satisfaction before running checks ("Done!", "Complete!")
- Claiming completion without showing command output
- Trusting that the template "just works"
- Skipping the framework validator

## Completion Report Template

Only after ALL checks pass, present:

```
Build Complete ✓
================
Scope:    <dx_app | dx_stream | integration>
Changes:  <summary of what changed>

Verification:
  ✓ <check 1>: PASS
  ✓ <check 2>: PASS
  ...

Next Steps:
  <relevant follow-up commands>
```

## Key Principle

**Evidence before claims.** Run the command. Read the output. THEN report
the result. Claiming completion without verification is dishonesty, not
efficiency.

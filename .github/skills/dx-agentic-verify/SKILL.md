---
name: dx-agentic-verify
description: DEEPX build verification checklists — dx_app, dx_stream, and cross-project.
---

<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: .deepx/skills/dx-agentic-verify/SKILL.md -->
<!-- Run: dx-agentic-gen generate -->

# Skill: DEEPX Build Verification Checklists

> For the general verification gate function and completion report template,
> see `dx-swe-verify`. This skill covers DEEPX-specific verification checklists.

## Scope

This is the **top-level suite** version covering all sub-projects. When working
in a single sub-project, prefer the project-level version:

| Working on... | Use this skill |
|---|---|
| dx_app (standalone inference) | `dx-runtime/dx_app/.github/skills/dx-verify-completion.md` |
| dx_stream (GStreamer pipelines) | `dx-runtime/dx_stream/.github/skills/dx-verify-completion.md` |
| Cross-project integration | `dx-runtime/.github/skills/dx-verify-completion.md` |

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
```

## Verification Checklist — Cross-Project Integration

```bash
# 1. Cross-project imports
python -c "
from dx_app.src.python_example.common.utils.model_utils import load_model_config
print('OK: dx_stream can import from dx_app')
"

# 2. Shared model configuration consistency
python -c "
import json
app_reg = json.load(open('dx-runtime/dx_app/config/model_registry.json'))
stream_list = json.load(open('dx-runtime/dx_stream/model_list.json'))
print(f'OK: dx_app has {len(app_reg)} models, dx_stream has {len(stream_list)} models')
"

# 3. Build order verification (dx_app first, then dx_stream)
cd dx-runtime/dx_app && ./install.sh && ./build.sh && echo "OK: dx_app build"
cd dx-runtime/dx_stream && ./install.sh && echo "OK: dx_stream install"
```

## session.log Authenticity (HARD GATE)

For ANY scenario that produces a `dx-agentic-dev/<sid>/session.log`, the log
MUST be the tee-captured stdout of real command execution — never a heredoc
template or programmatic write.

| ✓ Allowed | ✗ Prohibited |
|---|---|
| `python <runner>.py ... 2>&1 \| tee session.log` | `cat << 'EOF' > session.log ... EOF` |
| `bash run.sh 2>&1 \| tee session.log` | `printf "..." > session.log` |
| `dxcom <cfg> 2>&1 \| tee compile_out.log` (compiler) | `Path("session.log").write_text(...)` |
| `gst-launch-1.0 ... 2>&1 \| tee session.log` (dx_stream) | `awk ... > session.log` / `base64 -d ... > session.log` |

**Cross-project (runtime / suite) — dual session.log**:
Each sub-project gets its OWN session.log, each captured from its OWN command
execution. Writing one sub-project's session.log from a different directory
via heredoc (e.g., `cat << 'EOF' > dx-runtime/dx_app/.../session.log`) is a
legitimate cross-project write that the analyzer recognizes (the false-positive
guard checks the target path); the rule still requires real execution capture
for each sub-project, not template content.

The analyzer's `session_log_authentic` compliance check:
  - Hard-fail for `compiler` / `dx_app` / `dx_stream` / `dx_stream_cascaded` / `suite`
  - Soft-warning only for `runtime` (multi-domain scenario where a unified
    top-level session.log is structurally unnatural; the underlying
    `ExecutionTrace` rubric still demands real logs in each sub-project).


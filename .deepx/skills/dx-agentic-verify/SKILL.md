---
name: dx-agentic-verify
description: "DEEPX build verification checklists — dx_app, dx_stream, and cross-project."
---

# Skill: DEEPX Build Verification Checklists

> For the general verification gate function and completion report template,
> see `dx-swe-verify`. This skill covers DEEPX-specific verification checklists.

## Scope

This is the **top-level suite** version covering all sub-projects. When working
in a single sub-project, prefer the project-level version:

| Working on... | Use this skill |
|---|---|
| dx_app (standalone inference) | `dx-runtime/dx_app/.deepx/skills/dx-verify-completion.md` |
| dx_stream (GStreamer pipelines) | `dx-runtime/dx_stream/.deepx/skills/dx-verify-completion.md` |
| Cross-project integration | `dx-runtime/.deepx/skills/dx-verify-completion.md` |

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

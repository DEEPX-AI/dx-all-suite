---
name: dx-agent-verify
description: DEEPX build verification checklists — dx_app, dx_stream, and cross-project.
---

<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: .deepx/skills/dx-agent-verify/SKILL.md -->
<!-- Run: dx-agent-gen generate -->

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
# 1. Cross-project model consistency (sub-projects share .dxnn models via the registries, NOT Python imports)
python -c "
import json
app_reg = json.load(open('dx-runtime/dx_app/config/model_registry.json'))
stream_list = json.load(open('dx-runtime/dx_stream/model_list.json'))
print(f'OK: dx_app has {len(app_reg)} models, dx_stream has {len(stream_list)} models')
"

# 2. Build order verification (dx_app first, then dx_stream)
cd dx-runtime/dx_app && ./install.sh && ./build.sh && echo "OK: dx_app build"
cd dx-runtime/dx_stream && ./install.sh && echo "OK: dx_stream install"
```

## session.log Authenticity (HARD GATE)

For ANY scenario that produces a `dx-agent-dev/<sid>/session.log`, the log
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

## Session-ID Freshness (HARD GATE)

Each agent invocation MUST produce a **fresh** session directory whose name
starts with the current local timestamp. **Reusing a previous round's session
directory — even one created earlier today — is a HARD GATE violation** (see
AGENTS.md / CLAUDE.md: "Previous session reference PROHIBITED"). The harness
now scrubs stale state-marker files between rounds AND asserts the parsed
session-id timestamp falls within the current round's window. Sessions whose
timestamp predates the round start by >60 s fail `test_session_freshness`.

**Prohibited patterns** (reading any of these files is forbidden — they may
carry a prior round's session_id):

```bash
# ✗ Do NOT do this — these files leak prior session paths
cat .codex_current_work_dir          .codex_session_id
cat .cursor_current_session_id        .copilot_current_work_dir
cat .current_dx_session_id           .current_dx_work_dir
cat .active_session_id               .active_work_dir
cat .tmp_dx_workdir                  .dx_session_*
ls dx-agent-dev/                    # discovering prior sessions
find . -name "20*_yolo*_compile"     # path globs that match prior runs
```

**Required pattern** — always synthesise a new session-id from scratch:

```bash
# ✓ Correct — fresh timestamp from system clock
SESSION_ID="$(date +%Y%m%d-%H%M%S)_<agent>_<coding_model>_<target_model>_<task>"
WORK_DIR="dx-agent-dev/${SESSION_ID}"
mkdir -p "${WORK_DIR}"
```

Even if a prior session-dir exists with the same model/task and looks
"complete", do not re-enter it. The harness expects each round to be an
independent, end-to-end re-execution; reusing prior artifacts causes:

1. conftest's `_detect_new_sessions` to skip the dir (pre-existed in
   snapshot) → manifest.json has no output symlink → analyzer scores
   Compliance 40% for that scenario.
2. Round-N's session timestamp predates round-N start → `test_session_freshness`
   FAIL.
3. Cross-round pollution: round-N's analyzer report attributes round-K's
   artifacts to round-N, distorting per-round metrics.

If you find the round taking unreasonably long because compilation is slow,
fix the slowness — **do not** "skip" by reusing a prior compile result.

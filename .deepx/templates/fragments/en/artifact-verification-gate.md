## Artifact Verification Gate (HARD GATE — All Code Generation)

This gate applies to ALL sessions that generate code artifacts (compilation,
app generation, pipeline creation). It is independent of the "Internal Development"
SWE Process Gates — those apply to dx-agent-dev feature work; THIS gate applies
to user-facing deliverables.

### When This Gate Applies

Any session that produces files in `dx-agent-dev/<session_id>/` MUST verify
those files before declaring DONE. This includes:
- Compilation sessions (ONNX → DXNN)
- App generation sessions (dx_app factories + runners)
- Pipeline sessions (dx_stream pipelines)
- Cross-project sessions (compile + deploy)

### Mandatory Verification Steps

After generating each artifact, verify it IMMEDIATELY (not at the end):

| Artifact | Verification Command | Must Pass |
|----------|---------------------|-----------|
| `setup.sh` | `bash -n setup.sh && bash setup.sh` | Exit code 0, no errors |
| `run.sh` | `bash -n run.sh` | Syntax OK (full run needs model) |
| `verify.py` | `python verify.py; echo "exit: $?"` | Exit code 0 and output contains "RESULT: PASS" |
| `*.py` (factory) | `python -c "import py_compile; py_compile.compile('<file>', doraise=True)"` | Syntax OK |
| `*.py` (app) | `PYTHONPATH=. python -c "import py_compile; py_compile.compile('<file>', doraise=True)"` | Syntax OK |
| `config.json` | `python -c "import json; json.load(open('config.json'))"` | Valid JSON |

### verify.py Execution Test (MANDATORY)

`verify.py` MUST be executed with the session venv activated (created by `setup.sh`):

```bash
source venv/bin/activate   # activate the venv created by setup.sh
python verify.py
echo "Exit code: $?"
deactivate
```

Required behavior:
1. **Exit code 0** when both ONNX and DXNN inference succeed
2. **Exit code 1** when any inference fails (ImportError, RuntimeError, etc.)
3. **venv provides dependencies**: `setup.sh` creates the venv with all required packages
   (`onnxruntime`, `numpy`, etc.). `verify.py` focuses on verification logic only.

If `verify.py` prints "ONNX inference failed" or "DXNN inference failed" but
exits 0, it is BROKEN. Fix the exit code before proceeding.

Common failures:
- `No module named 'onnxruntime'` → run `setup.sh` first to create venv with dependencies
- `No module named 'dx_engine'` → ensure `setup.sh` adds runtime site-packages to venv
- Prints "failed" but exits 0 → add `sys.exit(1)` in the failure branch

### Cross-Project Path Resolution — SUITE_ROOT (HARD GATE)

When `setup.sh`, `run.sh`, or any generated script references a path **outside
its own sub-project** (e.g., a compiler session referencing `dx-runtime`, or an
app session referencing `dx-compiler`), the script MUST use `SUITE_ROOT`
auto-detection — NEVER hardcoded relative paths like `../../dx-runtime`.

**Why**: Session directory depth varies by sub-project:
- `dx-compiler/dx-agent-dev/<session>/` = 3 levels from suite root
- `dx-runtime/dx_app/dx-agent-dev/<session>/` = 4 levels from suite root
- `dx-runtime/dx_stream/dx-agent-dev/<session>/` = 4 levels from suite root

Hardcoded `../../` or `../../../` paths break when the agent miscounts depth
(a recurring failure pattern).

**Mandatory SUITE_ROOT pattern** — use this in ALL generated `setup.sh` / `run.sh`:
```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Auto-detect suite root (walks up until dx-runtime/ and dx-compiler/ siblings are found)
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: Cannot find dx-all-suite root (expected dx-runtime/ and dx-compiler/ siblings)"
    exit 1
fi

RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
COMPILER_DIR="$SUITE_ROOT/dx-compiler"
```

**Within-project relative paths** (e.g., `../../assets/models/` from a dx_app
session to `dx_app/assets/`) are acceptable because the depth within a single
sub-project is fixed. But cross-project references MUST use `$SUITE_ROOT`.

**Prohibited patterns** in generated `setup.sh` / `run.sh`:
```bash
# ALL of these are PROHIBITED for cross-project references:
RUNTIME_DIR="../../dx-runtime"           # Wrong depth assumption
RUNTIME_DIR="../../../dx-runtime"        # Still fragile
--input ../../dx-runtime/dx_app/sample/  # Inline hardcoded relative path
REF_DXNN="../../dx-runtime/dx_app/assets/models/..."  # Cross-project without SUITE_ROOT
```

**Correct patterns**:
```bash
# Cross-project references — always use SUITE_ROOT
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
COMPILER_DIR="$SUITE_ROOT/dx-compiler"
--input "$SUITE_ROOT/dx-runtime/dx_app/sample/img/sample_dog.jpg"
REF_DXNN="$SUITE_ROOT/dx-runtime/dx_app/assets/models/${MODEL_NAME}.dxnn"
```

### setup.sh Execution Test (MANDATORY)

`setup.sh` MUST be executed (not just syntax-checked) in the session directory.
If it fails:
1. Diagnose the error
2. Fix the script
3. Re-run until it passes

Common failures to test for:
- PEP 668 "externally-managed-environment" → must use venv
- `pip install <package>` for private packages → must use local install or pre-installed venv
- Relative path resolution from symlinked directories → use `$(cd "$(dirname "$0")" && pwd -P)` patterns
- Missing dependencies → verify `pip install` list is complete
- Cross-project paths using `../../` instead of `SUITE_ROOT` → use the SUITE_ROOT pattern above

### Import Resolution Test (MANDATORY for Python apps)

After all Python files are generated, run the following from the session directory.
**CRITICAL**: Run WITHOUT any manually set PYTHONPATH — this verifies the generated
`_sync.py` dynamic walker correctly resolves `src/python_example/common` on its own:

```bash
cd <session_dir>
python <model>_sync.py --help 2>&1 | head -10
```

Expected: `--help` output (usage/argparse text). If `ImportError: No module named 'common'`
appears, the dynamic path walker in `_sync.py` failed — do NOT use `PYTHONPATH=../../`
as a workaround. Fix the walker in `_sync.py` instead.

**Anti-pattern (PROHIBITED)**:
```bash
# WRONG — masks broken path setup; passes in agent env even when generated code is broken
PYTHONPATH=../../ python -c "from factory import <Model>Factory; print('import OK')"
```

### session.log Must Be Real Output (MANDATORY)

`session.log` MUST contain actual terminal command output captured via:
```bash
command 2>&1 | tee session.log
```

The following patterns are PROHIBITED for session.log:
- `cat << 'EOF' > session.log` (heredoc fabrication)
- `cat << 'LOGEOF' > session.log` (heredoc fabrication)
- `echo "..." > session.log` (hand-written summary)
- `printf "..." > session.log` (hand-written summary)
- Writing session.log content from memory without running commands

### dx-agent-tdd and Process Skill Sequence (MANDATORY for All Code Generation)

The complete process skill sequence (`/dx-agent-brainstorm` → `/dx-swe-writing-plans`
→ `/dx-agent-tdd` → `/dx-agent-verify`) is MANDATORY for ALL artifact generation
sessions. See the **"Mandatory Process Skill Sequence — All Code Generation"**
section for the full sequence definition and enforcement rules.

Within this Artifact Verification Gate, the `/dx-agent-tdd` Red-Green-Verify cycle
applies to each artifact:
1. **RED**: Define what each artifact must satisfy (syntax, execution, imports)
2. **GREEN**: Generate the artifact
3. **VERIFY**: Run the check immediately after creation (using the verification
   commands defined above in this section)

This is NOT optional even in autopilot mode. Skipping any process skill for code
generation is a session-failing violation regardless of whether the task is
"internal development" or "user-facing."

## Artifact Verification Gate (HARD GATE — All Code Generation)

This gate applies to ALL sessions that generate code artifacts (compilation,
app generation, pipeline creation). It is independent of the "Internal Development"
SWE Process Gates — those apply to dx-agentic-dev feature work; THIS gate applies
to user-facing deliverables.

### When This Gate Applies

Any session that produces files in `dx-agentic-dev/<session_id>/` MUST verify
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

`verify.py` MUST be executed WITHOUT manual venv activation to confirm it is
self-contained:

```bash
python verify.py    # NOT: source venv/bin/activate && python verify.py
echo "Exit code: $?"
```

Required behavior:
1. **Exit code 0** when both ONNX and DXNN inference succeed
2. **Exit code 1** when any inference fails (ImportError, RuntimeError, etc.)
3. **Self-contained**: auto-adds required site-packages to `sys.path` internally
   — no manual `source venv/bin/activate` required by the caller

If `verify.py` prints "ONNX inference failed" or "DXNN inference failed" but
exits 0, it is BROKEN. Fix the exit code before proceeding.

Common failures:
- `No module named 'onnxruntime'` → verify.py must add compiler venv site-packages to sys.path
- `No module named 'dx_engine'` → verify.py must add runtime venv site-packages to sys.path
- Prints "failed" but exits 0 → add `sys.exit(1)` in the failure branch

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

### Import Resolution Test (MANDATORY for Python apps)

After all Python files are generated, run:
```bash
cd <session_dir>
python -c "from factory import <Model>Factory; print('import OK')"
```

If this fails, the factory uses an incorrect import path. Fix it before proceeding.

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

### dx-tdd Invocation (MANDATORY for All Code Generation)

The `/dx-tdd` skill MUST be invoked for ALL artifact generation sessions — this
includes user-facing compilation, app generation, and pipeline tasks. It is NOT
limited to "internal development" tasks.

Its "Red-Green-Verify" cycle applies:
1. **RED**: Define what each artifact must satisfy (syntax, execution, imports)
2. **GREEN**: Generate the artifact
3. **VERIFY**: Run the check immediately after creation

This is NOT optional even in autopilot mode. Skipping dx-tdd for code generation
is a session-failing violation regardless of whether the task is "internal
development" or "user-facing."

**Rationale**: The SWE Process Gates "Mandatory Skill Sequence" is scoped to
internal dx-agentic-dev development. This Artifact Verification Gate extends
the same discipline to all generated deliverables. Without it, agents produce
untested setup.sh, broken imports, and fabricated session.log files.

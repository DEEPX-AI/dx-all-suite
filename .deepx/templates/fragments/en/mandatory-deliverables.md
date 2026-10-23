## Mandatory Deliverables

ALL compilation or app-generation sessions MUST produce the following files in the
session output directory (`dx-agent-dev/<session_id>/`) before outputting DONE.
This applies to **every task type** — compiler-only, app-only, and cross-project.

| File | Purpose | Required when |
|------|---------|---------------|
| `setup.sh` | Environment setup (sanity check, dxcom install, venv, pip deps) | Always |
| `run.sh` | One-command inference launcher with venv activation | Always |
| `README.md` | Session summary, quick start, file list | Always |
| `verify.py` | ONNX vs DXNN numerical comparison | Compilation involved |
| `session.log` | Actual command output log (NOT hand-written summary) | Always |
| `config.json` | dxcom compilation configuration | Compilation involved |
| `*.dxnn` | Compiled model binary | Compilation involved |
| `*.onnx` / `*.pt` | The source model, kept next to the `.dxnn` it produced | Compilation involved |

These are in ADDITION to any application-specific artifacts (Python files with
factory/inference patterns, GStreamer pipeline code, etc.).

**Every deliverable must be produced by THIS session.** Copying a file out of
another session's output directory — another agent's, another round's, your own
earlier one — and presenting it as this session's work is prohibited, with or
without edits. It is not a shortcut to the same result: the point of the
directory is to show what this run produced. The same rule already covers
`session.log` (no heredoc, no `echo`, no hand-written summary); it applies to
every file in the table. If a prerequisite is missing, say so and stop — do not
borrow one.

Each sub-project also defines templates for these files in its agent/skill documents
(e.g. Phase 5.5 of the **dx-compiler** repo's `.deepx/agents/` dx-dxnn-compiler.md).

### Cross-project suite tasks — pre-DONE `.dxnn` check (HARD GATE, REC-X4)

**For any task involving compilation**, before emitting the DONE sentinel, verify that
the `.dxnn` file exists in the compiler session directory:

```bash
COMPILER_SESSION="<compiler_session_dir>"   # e.g., dx-compiler/dx-agent-dev/20260430-..._compile
test -f "${COMPILER_SESSION}/yolo26n.dxnn" \
  || { echo "BLOCKED: yolo26n.dxnn not found — compilation still running. Wait for compile.pid to exit before emitting DONE."; exit 1; }
```

Emitting DONE while `yolo26n.dxnn` is absent causes `test_dxnn_compiled` to fail even if
background compilation eventually produces it (the test harness collects files at DONE time).
See Phase 5.8 of the **dx-compiler** repo's `.deepx/agents/` dx-dxnn-compiler.md for the full pre-DONE gate.

## Prerequisites Check (HARD GATE)

Before generating ANY code, creating files, or routing to sub-agents, the following
environment checks MUST pass. This gate applies at the suite level — even if
brainstorming produced a spec and plan, these checks MUST execute before implementation.

```bash
# 1. dx-runtime sanity check (MANDATORY — do NOT skip)
bash dx-runtime/scripts/sanity_check.sh --dx_rt
# IMPORTANT: Judge PASS/FAIL by the TEXT OUTPUT, not the exit code.
# Agents often pipe through `| tail` or `| head`, which silently
# replaces the real exit code with tail's exit code (always 0).
# PASS = output contains "Sanity check PASSED!" and NO [ERROR] lines
# FAIL = output contains "Sanity check FAILED!" or ANY [ERROR] lines
# NEVER pipe through tail/head/grep — run the command directly.
# If FAIL → run install, then RE-CHECK:
bash dx-runtime/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse
bash dx-runtime/scripts/sanity_check.sh --dx_rt  # Must PASS after install

# 2. dx_engine import check (MANDATORY for app generation tasks)
python -c "import dx_engine; print('dx_engine OK')" 2>/dev/null || {
    echo "dx_engine not available. Run: cd dx-runtime/dx_app && ./install.sh && ./build.sh"
}

# 3. dxcom availability check (MANDATORY for compilation tasks)
python -c "import dx_com; print('dxcom OK')" 2>/dev/null || {
    echo "dxcom not available."
    # Installation fallback:
    #   1. pip install dxcom (if in venv)
    #   2. bash dx-compiler/install.sh (if available)
    #   3. source dx-compiler/venv-dx-compiler-local/bin/activate (if exists)
    # If ALL fail → STOP and inform user. NEVER proceed without dxcom.
}
```

**This is a HARD GATE:**
- Do NOT generate any implementation code until these checks pass
- Do NOT skip these checks because brainstorming or planning was completed
- Each sub-project builder also has its own Step 0 Prerequisites — those are
  ADDITIONAL checks, not replacements for these suite-level checks
- If a check fails, inform the user with the exact fix command and STOP

### dxcom Anti-Fabrication (MANDATORY for compilation tasks)

When dxcom is available and compilation proceeds:
- **NEVER fabricate dxcom API calls from memory.** Always read the toolset files,
  which live in the **dx-compiler** repo under `.deepx/toolsets/`:
  - CLI: `dxcom-cli.md`
  - Python API: `dxcom-api.md`
  - Config schema: `config-schema.md`
- **Correct import**: `import dx_com; dx_com.compile(...)` (NOT `from dxcom import dxcom`)
- **NEVER modify `compiler.properties`** — system file managed by the installer.
  See Pitfalls #21 and #22 in the **dx-compiler** repo's `.deepx/memory/`
  common_pitfalls.md.

### Background Compilation (RECOMMENDED)

Using `subprocess.Popen` for compilation avoids blocking the agent's tool-call
thread for 10+ minutes, allowing parallel artifact generation.

**Recommended pattern** — `subprocess.Popen` with a `compile.pid` file:
```python
import subprocess, os
compile_script = f"{work_dir}/compile.py"
compile_out = open(f"{work_dir}/compile_out.log", "w")
proc = subprocess.Popen(
    ["python3", compile_script],
    stdout=compile_out, stderr=subprocess.STDOUT,
    cwd=work_dir, start_new_session=True,
)
with open(f"{work_dir}/compile.pid", "w") as f:
    f.write(str(proc.pid))
# Now generate ALL other artifacts (factory, sync.py, setup.sh, run.sh, verify.py)
# BEFORE checking compile.pid / .dxnn existence.
```

Synchronous compilation is acceptable when the agent can tolerate the blocking
time, but background compilation is preferred for timeout avoidance.

### Sanity Check Failure Recovery (MANDATORY)

When `sanity_check.sh --dx_rt` returns FAIL, follow this exact recovery sequence:

1. **Run install.sh** with the command shown above
2. **Re-run sanity_check.sh** — the check MUST pass after install
3. **If still failing**: check whether this is a **compiler-only task** or not:

   **A. Compiler-only task** (ONNX → DXNN compilation, no dx_app/dx_stream work):
   - Inform the user that the sanity check failed and NPU-based verification will be skipped.
   - **Proceed with compilation** — `dxcom` runs on CPU and does not require NPU hardware.
   - After compilation succeeds, mark `verify.py` as **SKIPPED** (not PASS).
   - Set `DX_SANITY_FAILED=1` so verify.py can detect and skip NPU-based checks.
   - Record in session.log: `sanity_check=FAIL, compilation=<result>, verification=SKIPPED`.
   - Tell the user:
     ```
     NPU hardware initialization failed. Compilation completed successfully,
     but DXNN verification (verify.py) requires a working NPU.
     After resolving the NPU issue (cold boot recommended), run:
       cd <session_dir> && python verify.py
     ```

   **B. Cross-project task** (compilation + dx_app/dx_stream demo app) or dx_app/dx_stream only:
   - **STOP unconditionally** — even if the user says "just continue",
     "work to completion", "use defaults", or "skip checks", the agent MUST NOT
     proceed. The user's instruction to continue does NOT override this HARD GATE.
   - Guide the user through manual recovery:
     - If the failure mentions **"Device initialization failed"**, **"Fail to initialize device"**,
       or **NPU hardware errors**: the NPU requires a cold boot (full power cycle) or
       system reboot. Software-only install cannot fix hardware initialization failures.
       Tell the user:
       ```
       NPU hardware initialization failed. This issue cannot be resolved by software installation alone.
       Please follow these steps:
       1. Fully shut down the system (power off — a cold boot is recommended, not just a reboot)
       2. Wait 10-30 seconds
       3. Power on the system
       4. After restart, verify NPU status with the sanity check:
          bash dx-runtime/scripts/sanity_check.sh --dx_rt
       5. Once the sanity check PASSES, please retry this task.
       ```
     - If the failure is a different error: show the user the specific error and
       recommended fix command, then STOP.

4. **NEVER bypass** (for non-compiler-only tasks) — the sanity check exists
   to ensure the full dx-runtime environment is operational. For dx_app/dx_stream
   tasks, skipping recovery means demo/verification scripts will fail.
   The following are ALL considered bypass and are PROHIBITED:
   - Setting PYTHONPATH or LD_LIBRARY_PATH manually to point at dx_engine artifacts
   - Using a venv from another repository (e.g., compiler venv) for dx_engine imports
   - Searching multiple venvs to find one where dx_engine happens to import
   - Concluding "exit code was 0, so it passed" when output text shows FAILED or [ERROR]
   - Piping sanity_check.sh through `| tail` / `| head` / `| grep` and using the pipe's exit code
   - Reinterpreting the user's "just continue" / "work to completion" / "use defaults"
     / autopilot instructions as permission to override the HARD GATE
   - Marking the prerequisite check as "done" or "passed" when it actually failed
   Note: compiler-only tasks (item 3A above) are exempt from this STOP — compilation
   proceeds, but verification is marked SKIPPED, not PASS.
5. **Common failure causes**:
   - NPU driver not installed → `install.sh` with `dx_rt_npu_linux_driver` target
   - dx_engine build artifacts missing → `cd dx_app && ./install.sh && ./build.sh`
   - PEP 668 (Ubuntu 24.04+) blocking pip → must use venv (never `--break-system-packages`)

## Autopilot Mode Guard (MANDATORY)

When the user is absent — autopilot mode, `--yolo` flag, or system auto-response
"The user is not available to respond" — the following rules apply:

1. **"Work autonomously" means "follow all rules without asking", NOT "skip rules".**
   Every mandatory gate still applies: brainstorming spec, plan, TDD, mandatory
   artifacts, execution verification, and self-verification checks.
   **This includes the SWE Process Gates Mandatory Skill Sequence** — in autopilot,
   `/dx-skill-router` → `/dx-agent-brainstorm` → `/dx-agent-tdd` must be followed
   exactly as in interactive mode. Autopilot mode does NOT waive this sequence.
2. **Do NOT call `ask_user`** — Make decisions using knowledge base defaults and
   documented best practices. Calling `ask_user` in autopilot wastes a turn and
   the auto-response does not grant permission to bypass any gate.
3. **User approval gate adaptation** — In autopilot, the spec approval gate is
   satisfied by writing the spec and self-reviewing it against the knowledge base.
   Do NOT skip the spec entirely.
4. **setup.sh FIRST** — Generate infrastructure artifacts (`setup.sh`, `config.json`)
   before writing any application code. This is especially critical in autopilot
   because there is no human to catch missing dependencies.
5. **Execution verification is NOT optional** — Run the generated code and verify it
   works before declaring completion. In autopilot, there is no user to catch errors.
6. **Time budget awareness** — Autopilot sessions may have time constraints.
   Plan your actions efficiently:
   - Compilation (ONNX → DXNN) may take 5+ minutes — start it early.
   - If time is short, prioritize artifact GENERATION over execution
     verification — a complete set of untested files is better than a partial
     set of tested ones.
   - Priority order: `setup.sh` > `run.sh` > app code > `verify.py` > session.log.
   - **Compilation-parallel workflow (HARD GATE)** — After launching `dxcom` or
     `dx_com.compile()` in a bash command, do NOT wait for it. Immediately
     proceed to generate ALL mandatory artifacts: factory, app code, setup.sh,
     run.sh, verify.py. Check `.dxnn` output only AFTER all other artifacts
     are created. **Violation of this rule fails the session.**
   - **NEVER sleep-poll for compilation** — Do NOT use `sleep` in a loop to
     poll for `.dxnn` files. Prohibited patterns include:
     `for i in ...; do sleep N; ls *.dxnn; done`,
     `while ! ls *.dxnn; do sleep N; done`,
     repeated `ls *.dxnn` / `test -f *.dxnn` checks with waits between them.
     Instead: generate all other artifacts first, then check ONCE whether the
     `.dxnn` file exists. If it does not exist yet, proceed to execution
     verification with the assumption that compilation will complete.
   - **NEVER use `pgrep -f` to monitor compile.pid process** — `pgrep -f
     "path/to/compile.py"` matches the bash shell that is running the pgrep
     command itself, causing an **infinite loop** that never exits even after
     compilation finishes. Always use `kill -0 <PID>` to check if a specific
     PID is still alive:
     ```bash
     # CORRECT — check by PID, not by name
     COMPILE_PID=$(cat compile.pid)
     while kill -0 "$COMPILE_PID" 2>/dev/null; do sleep 10; done
     echo "Compilation PID=$COMPILE_PID has exited"
     ```
     **Prohibited patterns** (self-referential, cause infinite loops):
     ```bash
     while pgrep -f "compile.py" >/dev/null 2>&1; do sleep 20; done   # PROHIBITED
     pgrep -f "session_dir/compile.py"                                 # PROHIBITED
     ```
   - **NEVER end your turn to wait for a background task (HARD GATE)** — a
     headless `claude -p` run has NO resume: ending the turn terminates the
     session, so a scheduled wakeup or a "wait for the completion notification"
     never fires and the DONE sentinel is never emitted — the round is recorded
     as *incomplete* (this is a real, recurring failure on the hardest scenarios,
     e.g. `suite`). PROHIBITED: calling `ScheduleWakeup` (or any
     wait-for-notification / "I'll continue once the background task notifies me"
     pattern) and then ending the turn. If you genuinely must wait for a
     backgrounded compile, block IN THE SAME TURN with
     `while kill -0 "$COMPILE_PID" 2>/dev/null; do sleep 10; done` — or,
     preferably, generate every other artifact first and check `.dxnn` ONCE.
     Never yield the turn expecting to be re-invoked.
   - **Mandatory artifacts are compilation-independent** — `setup.sh`, `run.sh`,
     `verify.py`, factory, and app code do NOT require the `.dxnn` file to exist.
     Generate them using the known model name (e.g., `yolo26n.dxnn`) as a
     placeholder path. Only execution verification requires the actual `.dxnn`.
7. **Minimize file-reading tool calls** — Do NOT re-read instruction files,
   agent docs, or skill docs that are already loaded in your context. Each
   unnecessary `cat` / `bash` read wastes 5-15 seconds. Use the knowledge
   already in your system prompt and conversation history.

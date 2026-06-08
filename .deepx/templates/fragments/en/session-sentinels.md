## Session Sentinels (MANDATORY for Automated Testing)

When processing a user prompt, output these exact markers for automated session
boundary detection by the test harness:

- **First line of your response**: `[DX-AGENTIC-DEV: START]`
- **Last line after ALL work is complete**: `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]`
  where `<relative_path>` is the session output directory (e.g., `dx-agentic-dev/20260409-143022_yolo26n_detection/`)

### DEEPX Banner (MANDATORY — print with the sentinels)

Render the DEEPX logo banner **verbatim** at two points: **immediately after** the
`[DX-AGENTIC-DEV: START]` line, and **immediately before** the
`[DX-AGENTIC-DEV: DONE ...]` line. Print it exactly as below (a fenced block is fine):

```
 ███████████   █████████ ████████ ████████  ████      ████
 ███     █████ ███░░░░░░░███░░░░░░███   ███  ░████   ████░░
 ███        ██░███░      ██░░     ███   ███░   █████████░░
 ███        ████████████ ████████ ████████░░    ░█████░░░
 ███        ██░███░░░░░░░██░░░░░░░███░░░░░░  ██████████
 ███     █████░███░      ██░      ███░   ████████░░░░████
 ███████████░░░█████████ ████████ ██████████░░░░░░    ████
  ░░░░░░░░░░░   ░░░░░░░░░ ░░░░░░░░ ░░░░░░░░░░          ░░░░
        DX-AGENTIC-DEV · on-device NPU
```

The banner is decorative; it never replaces or moves the sentinel lines (START stays
the absolute first line, DONE stays the very last line).

Rules:
1. **CRITICAL — Output `[DX-AGENTIC-DEV: START]` as the absolute first line of your
   first response.** This must appear before ANY other text, tool calls, or reasoning.
   Even if the user instructs you to "just proceed" or "use your own judgment",
   the START sentinel is non-negotiable — automated tests WILL fail without it.
   **Immediately after the START line, print the DEEPX banner** (see "DEEPX Banner" above).
2. **Immediately before the DONE line, print the DEEPX banner again**, then output
   `[DX-AGENTIC-DEV: DONE (output-dir: <path>)]` as the very last line after all work,
   validation, and file generation is complete
3. If you are a **sub-agent** invoked via handoff/routing from a higher-level agent,
   do NOT output these sentinels — only the top-level agent outputs them
4. If the user sends multiple prompts in a session, output START/DONE for each prompt
5. The `output-dir` in DONE must be the relative path from the project root to the
   session output directory. If no files were generated, omit the `(output-dir: ...)` part.
   **For cross-project tasks** (e.g., compile + app generation), list ALL output directories
   separated by ` + `:
   ```
   [DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260409-143022_copilot_yolo26n_compile/ + dx-runtime/dx_app/dx-agentic-dev/20260409-143022_copilot_yolo26n_inference/)]
   ```
6. **NEVER output DONE after only producing planning artifacts** (specs, plans, design
   documents). DONE means all deliverables are produced — implementation code, scripts,
   configs, and validation results. If you completed a brainstorming or planning phase
   but have not yet implemented the actual code, do NOT output DONE. Instead, proceed
   to implementation or ask the user how to proceed.
7. **Pre-DONE mandatory deliverable check**: Before outputting DONE, verify that all
   mandatory deliverables exist in the session directory. If any mandatory file is
   missing, create it before outputting DONE. Each sub-project defines its own mandatory
   file list in its skill document (e.g., `dx-agentic-stream-build-pipeline.md` File Creation Checklist).
8. **Session transcript — generate it RIGHT AFTER the DONE line (claude / copilot)**:

   **Auto-transcript is supported on `claude` and `copilot` only.** Emit the DONE
   sentinel line FIRST, then — as the single final housekeeping step — render this
   session's transcript with the shared generator **directly into the session output
   dir(s)** (the same dir(s) you listed in DONE). Running it *after* DONE means the
   CLI's session store has already committed the DONE turn, so the rendered transcript
   is complete (rendering *before* DONE truncates the tail). Needs **no hook**:

   ```bash
   # Locate the shared generator (walk up to the suite root), then render THIS
   # session's transcript INTO the session output dir(s). Pass EVERY output dir you
   # created (space-separated) — the transcript is copied into each (cross-project:
   # both the compiler and app dirs). The session id is auto-resolved from this CLI's
   # own env var (CLAUDE_CODE_SESSION_ID / COPILOT_AGENT_SESSION_ID).
   GT="$(d="$PWD"; while [ "$d" != / ]; do [ -f "$d/.deepx/tests/generate_transcripts.py" ] && { echo "$d/.deepx/tests/generate_transcripts.py"; break; }; d="$(dirname "$d")"; done)"
   python3 "$GT" --tool <CLI> --project "$PWD" \
       --into-output-dirs <output-dir> [<output-dir-2> ...]
   ```

   `<CLI>` is `claude` or `copilot`. The generator reuses the **same renderers as the
   test harness** (`parse_<tool>_session`) and writes `<CLI>-session.md` +
   `<CLI>-session.html` + `<CLI>-stream.jsonl` into each output dir. **If you produced
   NO output dir** (e.g. a pure question with no files), pass no dir and generation is
   **skipped** — expected, not an error. After it runs, state the path on the final
   line, e.g. `Session transcript (md/html/jsonl) saved to: <output-dir>/<CLI>-session.*`.

   **`codex`, `opencode`, `cursor` are NOT auto-supported** — do NOT run the generator
   in-session for them (it cannot produce a complete/usable transcript: codex and
   opencode commit their final turn only at process exit; cursor redacts the assistant
   text in its store). Instead, tell the user how to generate it manually:
   - **codex / opencode**: after the session ends, run
     `python3 <generate_transcripts.py> --tool <codex|opencode> --project . --out-dir <DIR>`
     — the finalized store then renders a complete transcript.
   - **cursor**: capture the run with `agent -p --output-format stream-json > run.jsonl`
     and render with `--tool cursor --stream-json run.jsonl`, or use IDE session history.
   (If you invoke the generator with `--into-output-dirs` on these tools, it safely
   skips and prints this same guidance — that is expected.)

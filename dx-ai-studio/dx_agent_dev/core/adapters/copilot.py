"""copilot -p 비대화형 어댑터(--add-dir 격리)."""
from dx_agent_dev.core.adapters.base import SubprocessAdapter


class CopilotAdapter(SubprocessAdapter):
    cli_bin = "copilot"
    # harness: cwd = target workdir so the agent discovers project CLAUDE.md + skills,
    # matching the original `cd "$_workdir" && copilot -i "$_prompt" --yolo ...`.
    cwd_mode = "harness"
    creds_relpath = (".copilot", "session-store.db")
    login_cmd_hint = "copilot  (first run opens GitHub device login)"

    def build_command(self, prompt, session_dir, harness_dirs, run_ctx=None):
        # --yolo: full tool autonomy (= original harness), supersedes granular --allow-tool.
        cmd = [self._cli, "-p", prompt, "--yolo", "--add-dir", str(session_dir)]
        for h in harness_dirs:
            cmd += ["--add-dir", str(h)]
        # "auto" is the studio's "let the CLI pick" sentinel, not a real copilot model id —
        # passing `--model auto` makes the copilot CLI reject the run (no output / no answer).
        # Omit the flag for auto so copilot uses its own default model selection.
        if self.model and self.model != "auto":
            cmd += ["--model", self.model]  # original: copilot -i ... --model "$AGENT_MODEL"
        # "none" is offered in the UI (copilot --help lists it) but the copilot BACKEND rejects
        # it for some models — e.g. model=auto resolves to gpt-5-mini, which 400s with
        # "'none' is not supported … Supported: minimal/low/medium/high", producing no answer.
        # Treat "none" as "omit --effort" (use the model's default reasoning) so every model works.
        if self.effort and self.effort != "none":
            cmd += ["--effort", self.effort]  # low|medium|high|xhigh|max
        # Autopilot: disable copilot's ask_user tool so the agent never blocks on user input.
        # claude/cursor/opencode already pass full-permission flags (--yolo / --dangerously-skip-permissions)
        # and rely on the autopilot prompt directive, so no extra flag is needed for those adapters.
        if run_ctx and getattr(run_ctx, "autopilot", False):
            cmd += ["--no-ask-user"]
        return cmd

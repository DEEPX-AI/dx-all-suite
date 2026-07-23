"""claude -p stream-json 어댑터(--add-dir 격리). normalize JSON 매핑은 provisional."""
import json

from dx_agent_dev.core.adapters.base import SubprocessAdapter, _map_json_event, classify_plain_line


class ClaudeAdapter(SubprocessAdapter):
    cli_bin = "claude"
    # harness: cwd = target workdir so the agent discovers project CLAUDE.md + .claude/skills,
    # matching the original `cd "$_workdir" && claude --dangerously-skip-permissions ...`
    # (.deepx/e2e/test.sh).
    cwd_mode = "harness"
    creds_relpath = (".claude", ".credentials.json")  # OAuth 자격증명(일반망 검증)
    creds_key = "claudeAiOauth"
    login_cmd_hint = "claude  (실행 후 브라우저 OAuth 로그인)"

    def build_command(self, prompt, session_dir, harness_dirs, run_ctx=None):
        # --dangerously-skip-permissions: full tool autonomy, same as the original harness.
        cmd = [self._cli, "-p", prompt, "--dangerously-skip-permissions", "--add-dir", str(session_dir)]
        for h in harness_dirs:
            cmd += ["--add-dir", str(h)]
        if self.model and self.model != "auto":
            cmd += ["--model", self.model]  # "auto" = studio sentinel for "CLI default", not a real id
        if self.effort and self.effort != "none":
            cmd += ["--effort", self.effort]  # low|medium|high|xhigh|max ("none" = omit → default)
        cmd += ["--output-format", "stream-json", "--verbose", "--include-partial-messages"]
        cmd = self._apply_cli_resume(cmd, run_ctx)
        return cmd

    def normalize(self, line):
        try:
            obj = json.loads(line)
        except (json.JSONDecodeError, ValueError, TypeError):
            return classify_plain_line(line)
        return _map_json_event(obj, line)

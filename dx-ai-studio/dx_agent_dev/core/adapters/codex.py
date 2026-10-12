"""codex exec --json adapter (cwd=harness, -C). Streams NDJSON line by line.

With ``exec --json`` Codex prints thread/turn/item.* events live. The codex branch of
_map_json_event (parse_codex_session schema) maps them to UI slots.

Written from the codex docs; not run against an installed codex CLI.
Codex has NO `--effort` flag (unlike claude/copilot). Reasoning effort is a
`-c` config override on `codex exec`: `-c model_reasoning_effort=<level>`
(levels: minimal|low|medium|high|xhigh, per codex docs).
"""
import json

from dx_agent_dev.core.adapters.base import SubprocessAdapter, _map_json_event, classify_plain_line


class CodexAdapter(SubprocessAdapter):
    cli_bin = "codex"
    cwd_mode = "harness"

    def build_command(self, prompt, session_dir, harness_dirs, run_ctx=None):
        work = harness_dirs[0] if harness_dirs else session_dir
        cmd = [self._cli, "exec", prompt, "--json", "-s", "danger-full-access"]
        if self.model and self.model != "auto":
            cmd += ["-m", self.model]  # "auto" = studio sentinel for "CLI default", not a real id
        if self.effort and self.effort != "none":
            # NOT --effort — codex takes reasoning effort via -c model_reasoning_effort=<level>
            # ("none" = omit → model default, avoiding an unsupported-value backend error)
            cmd += ["-c", f"model_reasoning_effort={self.effort}"]
        cmd += ["-C", str(work)]
        return cmd

    def normalize(self, line):
        try:
            obj = json.loads(line)
        except (json.JSONDecodeError, ValueError, TypeError):
            return classify_plain_line(line)
        return _map_json_event(obj, line)

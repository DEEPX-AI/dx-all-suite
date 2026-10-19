"""cursor-agent adapter (stream-json). Binary name and flags are provisional."""
import json
import re
import subprocess

from dx_agent_dev.core.adapters.base import SubprocessAdapter, _map_json_event, classify_plain_line

_MODEL_LINE = re.compile(r"^(\S+)\s+-\s+")  # `auto - Auto`, `gpt-5.3-codex - Codex 5.3`


class CursorAdapter(SubprocessAdapter):
    cli_bin = "cursor-agent"
    cwd_mode = "harness"
    creds_relpath = (".cursor", "cli-config.json")  # contains authInfo
    creds_key = "authInfo"
    login_cmd_hint = "cursor-agent login"

    def build_command(self, prompt, session_dir, harness_dirs, run_ctx=None):
        cmd = [self._cli, "-p", prompt, "--trust", "--force"]
        cmd = self._apply_cli_resume(cmd, run_ctx)
        model = self._resolved_model()
        if model:
            cmd += ["--model", model]
        cmd += ["--output-format", "stream-json", "--stream-partial-output"]
        return cmd

    def _resolved_model(self):
        """Apply optional [effort=…] bracket when model id has no existing params."""
        model = (self.model or "").strip()
        if not model:
            return None
        if not self.effort or "[" in model or model == "auto":
            return model
        return f"{model}[effort={self.effort}]"

    @staticmethod
    def _parse_models(text: str) -> list:
        """Extract model ids from `cursor-agent --list-models` output (skipping headers and blank lines)."""
        out = []
        for line in (text or "").splitlines():
            m = _MODEL_LINE.match(line.strip())
            if m and m.group(1) not in out:
                out.append(m.group(1))
        return out

    def list_models(self):
        """Query the real model list via `cursor-agent --list-models` (None on failure -> static fallback)."""
        if not self._cli:
            return None
        try:
            proc = subprocess.run([self._cli, "--list-models"],
                                  capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if proc.returncode != 0:
            return None
        models = self._parse_models(proc.stdout)
        return models or None

    def normalize(self, line):
        try:
            obj = json.loads(line)
        except (json.JSONDecodeError, ValueError, TypeError):
            return classify_plain_line(line)
        return _map_json_event(obj, line)

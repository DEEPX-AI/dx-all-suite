"""opencode run 어댑터(cwd=harness, 텍스트 출력 → 기본 normalize 상속)."""
import re
import subprocess

from dx_agent_dev.core.adapters.base import SubprocessAdapter

_MODEL_LINE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.:-]+$")  # provider/model


class OpenCodeAdapter(SubprocessAdapter):
    cli_bin = "opencode"
    cwd_mode = "harness"
    login_cmd_hint = "opencode auth login"

    def list_models(self):
        """Dynamic model list via `opencode models` (real configured providers)."""
        if not self._cli:
            return None
        try:
            out = subprocess.run([self._cli, "models"], capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            return None
        models = [ln.strip() for ln in out.stdout.splitlines() if _MODEL_LINE.match(ln.strip())]
        return models or None

    def build_command(self, prompt, session_dir, harness_dirs, run_ctx=None):
        # --dangerously-skip-permissions: full tool autonomy in headless `run` (parity with
        # claude/copilot/cursor) — also prevents a permission prompt from hanging the stream.
        cmd = [self._cli, "run", prompt, "--dangerously-skip-permissions"]
        if self.model:
            cmd += ["-m", self.model]
        if self.effort:
            cmd += ["--variant", self.effort]  # provider-specific reasoning effort
        return cmd
    # normalize: 텍스트 휴리스틱 상속

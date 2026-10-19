"""copilot -p non-interactive adapter (--add-dir isolation).

Model list: the copilot CLI has no list command, but ACP mode (`copilot --acp --stdio`, the JSON-RPC used by
IDEs) answers `session/new` with **the models this account may use** (plan and company policy applied; blocked
models are left out) and their price multipliers (`_meta.copilotUsage`). No prompt is sent, so it costs nothing
(about 1.7 s).
"""
import json
import os
import re
import select
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from dx_agent_dev.core.adapters.base import (SubprocessAdapter, _hidden_status, _message_event,
                                             _tool_arg_hint, classify_plain_line, find_cli)

_ACP_TIMEOUT = 12.0


class CopilotAdapter(SubprocessAdapter):
    cli_bin = "copilot"
    # harness: cwd = target workdir so the agent discovers project CLAUDE.md + skills,
    # matching the original `cd "$_workdir" && copilot -i "$_prompt" --yolo ...`.
    cwd_mode = "harness"
    login_cmd_hint = "copilot login"

    def __init__(self, cli_path=None, model=None, effort=None):
        super().__init__(cli_path=cli_path or find_cli(self.cli_bin), model=model, effort=effort)

    def list_models(self):
        got = self.account_models()
        return [m["id"] for m in got["models"] if m["enabled"]] if got else None

    def account_models(self):
        """Ask ACP for this account's models. {"models": [{id, name, usage, enabled}], "default": id} or None.

        The list only comes with an open session, so one is opened and closed. The CLI leaves the session folder
        behind (`~/.copilot/session-state/<id>`), so the folder of the id just opened is removed; otherwise one
        would pile up every two minutes."""
        if not self._cli:
            return None
        if os.environ.get("DX_AGENT_NO_REAL_RUN") == "1" and self._is_the_installed_cli():
            return None     # tests never call the real CLI (tests/conftest.py)
        proc = None
        sid = None
        try:
            proc = subprocess.Popen([self._cli, "--acp", "--stdio"], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                    cwd=tempfile.gettempdir())
            deadline = time.monotonic() + _ACP_TIMEOUT

            def call(rid, method, params):
                proc.stdin.write((json.dumps({"jsonrpc": "2.0", "id": rid, "method": method,
                                              "params": params}) + "\n").encode())
                proc.stdin.flush()
                while time.monotonic() < deadline:
                    ready, _, _ = select.select([proc.stdout], [], [], 0.25)
                    if not ready:
                        if proc.poll() is not None:
                            return None
                        continue
                    line = proc.stdout.readline()
                    if not line:
                        return None
                    try:
                        msg = json.loads(line)
                    except ValueError:
                        continue
                    if msg.get("id") == rid:
                        return msg.get("result")
                return None

            if call(1, "initialize", {"protocolVersion": 1, "clientCapabilities": {}}) is None:
                return None
            res = call(2, "session/new", {"cwd": tempfile.gettempdir(), "mcpServers": []})
            if not res:
                return None
            sid = res.get("sessionId")
            call(3, "session/close", {"sessionId": sid})
            listed = (res.get("models") or {}).get("availableModels") or []
            seen, models = set(), []
            for m in listed:
                mid = m.get("modelId")
                if not mid or mid in seen:
                    continue
                seen.add(mid)
                meta = m.get("_meta") or {}
                models.append({"id": mid, "name": m.get("name") or mid,
                               "usage": meta.get("copilotUsage"),
                               "enabled": meta.get("copilotEnablement", "enabled") != "disabled"})
            if not models:
                return None
            return {"models": models, "default": (res.get("models") or {}).get("currentModelId")}
        except (OSError, ValueError):
            return None
        finally:
            if proc is not None:
                try:
                    proc.stdin.close()
                    proc.wait(timeout=3)
                except Exception:
                    proc.kill()
            if sid and re.fullmatch(r"[0-9a-fA-F-]{8,64}", sid):
                # Where the CLI writes = the inherited $HOME (tests may patch Path.home() separately)
                home = Path(os.path.expanduser("~"))
                shutil.rmtree(home / ".copilot" / "session-state" / sid, ignore_errors=True)

    def build_command(self, prompt, session_dir, harness_dirs, run_ctx=None):
        self._reset_stream()
        # --yolo: full tool autonomy (= original harness), supersedes granular --allow-tool.
        # --output-format json: JSONL events. The text mode handed the whole CLI transcript
        # (● tool lines, │ commands, tool output, the "AI Credits / Tokens / Resume" footer) to
        # the chat as one reply and left the Activity panel empty.
        cmd = [self._cli, "-p", prompt, "--yolo", "--output-format", "json",
               "--add-dir", str(session_dir)]
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

    # ── `--output-format json` → AgentEvent ────────────────────────────────────────────
    # copilot CLI JSONL: assistant.message_delta (reply tokens), tool.execution_start /
    # tool.execution_complete (one tool call), result (exitCode). The rest is session
    # bookkeeping. One adapter serves one run, so the per-run state lives on it.

    def _reset_stream(self):
        self._started = False
        self._spoke = False        # a reply delta went out — the next message gets a blank line
        self._last_reply = ""

    def normalize(self, line):
        try:
            obj = json.loads(line)
        except (ValueError, TypeError):
            return classify_plain_line(line)
        if not isinstance(obj, dict) or not isinstance(obj.get("type"), str):
            return classify_plain_line(line)
        if not hasattr(self, "_started"):
            self._reset_stream()
        kind = obj["type"]
        data = obj.get("data") if isinstance(obj.get("data"), dict) else {}

        if kind == "model.call_start" and not self._started:
            self._started = True
            return {"type": "status", "text": f"Session started ({data.get('model') or 'copilot'})"}
        if kind == "assistant.message_start":
            if self._spoke:
                return {"type": "message", "text": "\n\n", "delta": True}
            return _hidden_status()
        if kind == "assistant.message_delta":
            text = data.get("deltaContent") or ""
            if not text:
                return _hidden_status()
            self._spoke = True
            return {"type": "message", "text": text, "delta": True}
        if kind == "assistant.message":
            content = data.get("content") or ""
            if isinstance(content, str) and content.strip():
                self._last_reply = content
            return _hidden_status()
        if kind == "tool.execution_start":
            name = data.get("toolName") or "tool"
            hint = _tool_arg_hint(data.get("arguments") or "")
            return {"type": "command", "text": (f"→ {name}: {hint}" if hint else f"→ {name}")[:500]}
        if kind == "tool.execution_complete":
            result = data.get("result") if isinstance(data.get("result"), dict) else {}
            text = result.get("content") or ""
            if not data.get("success", True):
                return {"type": "log", "text": ("✗ " + str(text or data.get("toolName") or "tool failed"))[:2000]}
            return {"type": "log", "text": str(text)[:2000]} if text else _hidden_status()
        if kind == "result":
            code = obj.get("exitCode")
            if code not in (0, None):
                return {"type": "error", "text": f"copilot exited with code {code}"}
            if self._last_reply:
                return _message_event(self._last_reply, final=True, sanitize=True)
            return _hidden_status()
        if kind.endswith("error") or kind.endswith(".error"):
            msg = data.get("message") or data.get("error") or obj.get("message") or kind
            return {"type": "error", "text": str(msg)[:2000]}
        return _hidden_status()

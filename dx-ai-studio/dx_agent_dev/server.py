#!/usr/bin/env python3
"""DX Agent Dev Server — interactive console (port 8099)."""
from __future__ import annotations

import json
import os
from http.server import ThreadingHTTPServer
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

from dx_agent_dev.core.config import (DEFAULT_PORT, STATIC_DIR, TEMPLATES_DIR, SERVER_NAME,
                         WORKSPACE_ROOT, PROMPT_MAX_LEN, resolve_target)
from dx_agent_dev.core import environment
from dx_agent_dev.core.agent_runner import AgentRunner, CopilotAdapter, MockAdapter
from dx_agent_dev.core.live_run import LiveRun
from dx_agent_dev.core.conversation_store import ConversationStore
from dx_agent_dev.core.message_pipeline import CLI_RESUME_AGENTS, prepare_sse_event
from dx_agent_dev.core.prompt_wrap import wrap_autopilot_prompt, wrap_console_prompt, wrap_with_conversation_history
from dx_agent_dev.core.run_context import RunContext
from dx_agent_dev.core.adapters import make_adapter
from dx_agent_dev.core.showcases import load_showcases
from shared import agent_cli
from shared.dx_server import DXBaseHandler
from shared.chat import ChatEngine
from shared.chat import module_fallbacks as _module_fallbacks
from shared.shell import ShellSpec

PORT = DEFAULT_PORT

_chat_engine = ChatEngine(
    app_name="dx_agent_dev",
    fallback_rules=_module_fallbacks.rules("dx_agent_dev"),
)


# Human-readable agent display names for degraded guidance (order matches the install
# guidance text: Claude Code, GitHub Copilot CLI, Cursor, Codex, OpenCode).
_DEGRADED_AGENT_ORDER = ["claude", "copilot", "cursor", "codex", "opencode"]
_AGENT_DISPLAY_NAME = {
    "claude": "Claude Code",
    "copilot": "GitHub Copilot CLI",
    "cursor": "Cursor",
    "codex": "Codex",
    "opencode": "OpenCode",
}

_DEGRADED_TITLE = {
    "cli_missing": {
        "en": "No coding-agent CLI found",
        "ko": "코딩 에이전트 CLI를 찾을 수 없습니다",
        "ja": "コーディングエージェント CLI が見つかりません",
        "zh-CN": "未找到编码代理 CLI",
        "zh-TW": "找不到程式碼代理 CLI",
        "es": "No se encontró ninguna CLI de agente de código",
    },
    "harness_missing": {
        "en": "Harness directory not found",
        "ko": "하니스 디렉터리를 찾을 수 없습니다",
        "ja": "ハーネスディレクトリが見つかりません",
        "zh-CN": "未找到 harness 目录",
        "zh-TW": "找不到 harness 目錄",
        "es": "No se encontró el directorio del harness",
    },
    "unavailable": {
        "en": "Agent console unavailable",
        "ko": "에이전트 콘솔을 사용할 수 없습니다",
        "ja": "エージェントコンソールは利用できません",
        "zh-CN": "代理控制台不可用",
        "zh-TW": "代理主控台無法使用",
        "es": "Consola de agente no disponible",
    },
}

_DEGRADED_DETAIL = {
    "cli_missing": {
        "en": "No installed and authenticated coding-agent CLI was found. Install and log into "
              "one of: Claude Code (`claude`), GitHub Copilot CLI (`copilot`), Cursor "
              "(`cursor-agent`), Codex (`codex`), or OpenCode (`opencode`), then reload this page. "
              "(The 💬 chat button is separate — it answers SDK questions and doesn't need a CLI.)",
        "ko": "설치 및 인증된 코딩 에이전트 CLI를 찾을 수 없습니다. 다음 중 하나를 설치하고 로그인한 "
              "후 이 페이지를 새로고침하세요: Claude Code(`claude`), GitHub Copilot CLI(`copilot`), "
              "Cursor(`cursor-agent`), Codex(`codex`), OpenCode(`opencode`). "
              "(💬 채팅 버튼은 별개입니다 — SDK 질문에 답하며 CLI가 필요 없습니다.)",
        "ja": "インストール済みかつ認証済みのコーディングエージェント CLI が見つかりません。次のいずれ"
              "かをインストールしてログインした後、このページを再読み込みしてください: Claude Code"
              "(`claude`)、GitHub Copilot CLI(`copilot`)、Cursor(`cursor-agent`)、Codex(`codex`)、"
              "OpenCode(`opencode`)。(💬 チャットボタンは別機能です — SDK に関する質問に答えるもの"
              "で、CLI は不要です。)",
        "zh-CN": "未找到已安装并完成认证的编码代理 CLI。请安装并登录以下任意一个，然后重新加载此页面："
                 "Claude Code(`claude`)、GitHub Copilot CLI(`copilot`)、Cursor(`cursor-agent`)、"
                 "Codex(`codex`)、OpenCode(`opencode`)。"
                 "(💬 聊天按钮是独立功能 — 用于回答 SDK 问题，不需要 CLI。)",
        "zh-TW": "找不到已安裝並完成驗證的程式碼代理 CLI。請安裝並登入下列其中一項，然後重新載入此頁"
                 "面：Claude Code(`claude`)、GitHub Copilot CLI(`copilot`)、Cursor(`cursor-agent`)、"
                 "Codex(`codex`)、OpenCode(`opencode`)。"
                 "(💬 聊天按鈕是獨立功能 — 用於回答 SDK 問題，不需要 CLI。)",
        "es": "No se encontró ninguna CLI de agente de código instalada y autenticada. Instale e "
              "inicie sesión en una de las siguientes y luego recargue esta página: Claude Code "
              "(`claude`), GitHub Copilot CLI (`copilot`), Cursor (`cursor-agent`), Codex (`codex`) "
              "u OpenCode (`opencode`). (El botón de chat 💬 es independiente — responde preguntas "
              "sobre el SDK y no necesita una CLI.)",
    },
    "harness_missing": {
        "en": "The `.deepx` harness directory (agent knowledge/skills) wasn't found. Point at it "
              "by setting the `DX_HARNESS_ROOT` environment variable to your dx-all-suite checkout, "
              "or run DX AI Studio from within the suite, then reload this page.",
        "ko": "`.deepx` 하니스 디렉터리(에이전트 지식/스킬)를 찾을 수 없습니다. `DX_HARNESS_ROOT` "
              "환경 변수를 dx-all-suite 체크아웃 경로로 설정하거나, DX AI Studio를 suite 내부에서 "
              "실행한 뒤 이 페이지를 새로고침하세요.",
        "ja": "`.deepx` ハーネスディレクトリ(エージェントの知識/スキル)が見つかりません。"
              "`DX_HARNESS_ROOT` 環境変数を dx-all-suite のチェックアウトパスに設定するか、"
              "suite 内で DX AI Studio を実行してから、このページを再読み込みしてください。",
        "zh-CN": "未找到 `.deepx` harness 目录（代理知识/技能来源）。请将 `DX_HARNESS_ROOT` 环境变量"
                 "设置为您的 dx-all-suite 检出路径，或在 suite 内运行 DX AI Studio，然后重新加载此"
                 "页面。",
        "zh-TW": "找不到 `.deepx` harness 目錄（代理知識/技能來源）。請將 `DX_HARNESS_ROOT` 環境變數"
                 "設定為您的 dx-all-suite 簽出路徑，或在 suite 內執行 DX AI Studio，然後重新載入此"
                 "頁面。",
        "es": "No se encontró el directorio del harness `.deepx` (fuente del conocimiento/habilidades "
              "del agente). Configure la variable de entorno `DX_HARNESS_ROOT` apuntando a su copia "
              "de dx-all-suite, o ejecute DX AI Studio desde dentro del suite, y luego recargue esta "
              "página.",
    },
    "unavailable": {
        "en": "The agent console isn't available in this environment. Browse the showcases below "
              "instead.",
        "ko": "이 환경에서는 에이전트 콘솔을 사용할 수 없습니다. 대신 아래 쇼케이스를 둘러보세요.",
        "ja": "この環境ではエージェントコンソールを利用できません。代わりに下のショーケースをご覧く"
              "ださい。",
        "zh-CN": "此环境中无法使用代理控制台。请浏览下方的展示内容。",
        "zh-TW": "此環境中無法使用代理主控台。請瀏覽下方的展示內容。",
        "es": "La consola de agente no está disponible en este entorno. Explore los showcases a "
              "continuación.",
    },
}


def _agent_install_options():
    """Per-CLI install/login guidance for the cli_missing degraded reason.

    Reuses the same cheap, local-only checks as ``_login_status`` (binary presence via
    ``adapter.is_available()``, cheap credential-file check via ``adapter.is_authenticated()``)
    — no subprocess calls, safe to compute for every known agent on every degraded response.
    """
    from dx_agent_dev.core.adapters import make_adapter as _make_adapter
    options = []
    for name in _DEGRADED_AGENT_ORDER:
        try:
            adapter = _make_adapter(name)
        except Exception:
            adapter = None
        installed = bool(adapter and adapter.is_available())
        authenticated = adapter.is_authenticated() if adapter else None
        login_hint = getattr(adapter, "login_cmd_hint", None) if adapter else None
        options.append({
            "agent": name,
            "displayName": _AGENT_DISPLAY_NAME.get(name, name),
            "installed": installed,
            "authenticated": authenticated,
            "loginHint": login_hint,
        })
    return options


def _degraded_payload(env):
    """Degraded-mode SSE payload. A pure function, unit-tested.

    ``reason``/``text`` stay backward-compatible (raw reason code + short EN summary); ``title``/
    ``detail`` add localized (6-lang) guidance so a first-time user knows exactly what to do, and
    ``installOptions`` (cli_missing only) lists each supported coding-agent CLI with its
    install/login status.
    """
    reason = env.get("reason") or "unavailable"
    payload = {
        "type": "degraded",
        "reason": reason,
        "text": _DEGRADED_TITLE.get(reason, _DEGRADED_TITLE["unavailable"])["en"],
        "title": _DEGRADED_TITLE.get(reason, _DEGRADED_TITLE["unavailable"]),
        "detail": _DEGRADED_DETAIL.get(reason, _DEGRADED_DETAIL["unavailable"]),
    }
    if reason == "cli_missing":
        payload["installOptions"] = _agent_install_options()
    return payload


def _make_runner():
    env = environment.detect_environment()
    if env.get("forced_mock") or not env["available"]:
        adapter = MockAdapter()
    else:
        adapter = CopilotAdapter(env["cli"])
    return AgentRunner(adapter, WORKSPACE_ROOT)


_runner = _make_runner()

# Slot that detaches a run from the HTTP response. If the handler drove the _runner.run() generator
# itself, a browser dropping the stream would mean GeneratorExit -> agent_runner's finally ->
# subprocess killed. Details: dx_agent_dev/core/live_run.py
_live = LiveRun()
_conversations = ConversationStore()



# ── Shared App Shell ──────────────────────────────────────────
# A single console screen has no tab row, so the template root carries .dx-shell--no-tabs.
DX_AGENT_DEV_SHELL = ShellSpec(
    module_key="agent",
    toolbar_extra="",
)

class AgentDevHandler(DXBaseHandler):
    server_name = SERVER_NAME
    static_dir = STATIC_DIR
    templates_dir = TEMPLATES_DIR
    shell_spec = DX_AGENT_DEV_SHELL
    log_filter = ["/static/", "/api/agent/status"]

    def route(self):
        if self.handle_chat_routes(_chat_engine):
            return
        if self.route_common():
            return
        if self.command == "GET":
            if self.url_path == "/api/agent/status":
                return self.send_json(self._status())
            if self.url_path == "/api/agent/run/events":
                return self._attach_sse()
            if self.url_path == "/api/agent/showcases":
                return self.send_json({"showcases": load_showcases()})
            if self.url_path == "/api/agent/login/status":
                return self.send_json(self._login_status())
            if self.url_path == "/api/agent/models":
                return self.send_json(self._agent_models())
        if self.command == "POST":
            if self.url_path == "/api/agent/run":
                return self._run_sse()
            if self.url_path == "/api/agent/cancel":
                _runner.cancel()
                return self.send_json({"ok": True})
        self.route_legacy()

    def _status(self):
        env = environment.detect_environment()
        forced = env.get("forced_mock", False)
        available = env["available"] or forced
        # Even under mock, pinned agents (DX_AGENT_DEV_PIN_AGENTS: visual regression, browser tests) are
        # shown: the screen picks like the real thing and mock takes the run.
        pinned = os.environ.get("DX_AGENT_DEV_PIN_AGENTS") is not None
        agents = environment.detect_available_agents() if (pinned or not forced) else []
        snap = _live.snapshot()
        status = {
            "available": available,
            "reason": env.get("reason"),
            "busy": _runner.is_busy(),
            "showcase_count": len(load_showcases()),
            "agents": agents,
            # Home and this console start with the same agent
            "studio_agent": agent_cli.studio_agent(),
            # Where to attach: which run, and how many events so far.
            "run_id": snap["run_id"],
            "event_count": snap["count"],
            "run_done": snap["done"],
            # Whoever takes over (home -> Agent Dev) knows the first line, conversation and mode
            "run_prompt": snap["info"].get("prompt"),
            "run_conversation_id": snap["info"].get("conversation_id"),
            "run_mode": snap["info"].get("mode"),
        }
        if not available:
            # Same localized guidance as the SSE degraded event (see _degraded_payload) — this
            # is the path the console actually hits on page load (checkStatus()), before the
            # user ever gets a chance to submit a prompt and trigger /api/agent/run.
            degraded = _degraded_payload(env)
            status["title"] = degraded["title"]
            status["detail"] = degraded["detail"]
            if "installOptions" in degraded:
                status["installOptions"] = degraded["installOptions"]
        return status

    def _agent_models(self):
        """?agent=<name> -> live model list (+default). The static config fallback lives in list_agent_models."""
        from urllib.parse import urlparse, parse_qs
        agent = (parse_qs(urlparse(self.path).query).get("agent", [""])[0] or "").strip()
        if not agent:
            return {"agent": agent, "models": [], "default_model": None}
        info = environment.agent_model_info(agent)
        out = {"agent": agent, "models": info["models"], "default_model": info["default_model"]}
        if info.get("catalog"):
            out["catalog"] = info["catalog"]   # everything + enabled; only models the account may pick are enabled
        return out

    def _login_status(self):
        """In-UI login help: ?agent=<name> -> install/auth state plus the login command.

        Interactive OAuth needs a browser anyway, so this gives the exact login command and lets
        is_authenticated() confirm completion (avoiding false negatives: None=unknown).
        """
        from urllib.parse import urlparse, parse_qs
        from dx_agent_dev.core.adapters import make_adapter
        agent = (parse_qs(urlparse(self.path).query).get("agent", [""])[0] or "").strip()
        adapter = make_adapter(agent) if agent else None
        if adapter is None:
            return {"agent": agent, "installed": False, "authenticated": None, "hint": None}
        return {
            "agent": agent,
            "installed": adapter.is_available(),
            "authenticated": adapter.is_authenticated(),
            "hint": adapter.login_cmd_hint,
        }


    def _stream_live(self, from_index: int, conversation_id: str = ""):
        """Stream the buffer as SSE. A disconnected consumer does not affect the run."""
        self.start_sse()
        try:
            for ev in _live.events(from_index):
                if ev.get("type") == "session":
                    status_text = ev.get("status_text")
                    if status_text:
                        if not self.send_sse_data(json.dumps(
                            {"type": "status", "text": status_text}, ensure_ascii=False,
                        )):
                            return
                    continue
                if ev.get("type") == "done" and conversation_id:
                    ev = dict(ev)
                    ev["conversation_id"] = conversation_id
                out = prepare_sse_event(ev)
                if out is None:
                    continue
                if not self.send_sse_data(json.dumps(out, ensure_ascii=False)):
                    return
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self.end_sse()

    def _attach_sse(self):
        """Attach to a running (or just finished) run.

        This is how Agent Dev shows a run started from home, and how a window that left and came back
        picks it up again.
        """
        from urllib.parse import parse_qs, urlparse
        q = parse_qs(urlparse(self.path).query)
        try:
            from_index = int((q.get("from") or ["0"])[0])
        except ValueError:
            from_index = 0
        self._stream_live(max(0, from_index))

    def _run_sse(self):
        body = self.read_json_body()
        raw_prompt = (body.get("prompt") or "").strip()
        if not raw_prompt:
            return self.send_error_json(400, "empty prompt")
        if len(raw_prompt) > PROMPT_MAX_LEN:
            return self.send_error_json(400, "prompt too long")

        conversation_id = (body.get("conversation_id") or "").strip() or None
        conv = _conversations.get(conversation_id) if conversation_id else None

        env = environment.detect_environment()
        forced = env.get("forced_mock", False)
        if not (env["available"] or forced):
            self.start_sse()
            self.send_sse_data(json.dumps(_degraded_payload(env)))
            self.end_sse()
            return

        mode = (body.get("mode") or "interactive").strip()
        autopilot = (mode == "autopilot")

        agent = (body.get("agent") or "").strip() or None
        model = (body.get("model") or "").strip() or None
        effort = (body.get("effort") or "").strip() or None
        target = (body.get("target") or "").strip() or None
        adapter = None
        if agent is not None:
            adapter = make_adapter(agent, model, effort)
            if adapter is None:
                return self.send_error_json(400, "unknown agent")
            if not forced:
                # Reuse the agents list detect_environment() already computed above
                # instead of calling detect_available_agents() a second time.
                available = {a["name"] for a in env.get("agents", [])}
                if agent not in available:
                    return self.send_error_json(400, "unknown agent")
        if forced:
            adapter = None

        if conv is None:
            conv = _conversations.create(agent=agent, model=model, effort=effort)
        else:
            if agent and conv.agent and conv.agent != agent:
                return self.send_error_json(400, "agent mismatch for conversation")
            conv.agent = conv.agent or agent
            conv.model = model or conv.model
            conv.effort = effort or conv.effort

        agent_name = agent or conv.agent or ""
        if autopilot:
            # One-shot run: no resume, no interactive history, autopilot directive only.
            prompt = wrap_autopilot_prompt(raw_prompt)
            run_ctx = RunContext(
                conversation_id=conv.id,
                is_followup=False,
                cli_session_id=None,
                supports_cli_resume=False,
                autopilot=True,
            )
        else:
            is_followup = conv.is_followup
            if is_followup and agent_name not in CLI_RESUME_AGENTS:
                prompt = wrap_with_conversation_history(raw_prompt, conv)
            else:
                prompt = wrap_console_prompt(raw_prompt, is_followup=is_followup)
            run_ctx = RunContext(
                conversation_id=conv.id,
                is_followup=is_followup,
                cli_session_id=conv.cli_session_id,
                supports_cli_resume=agent_name in CLI_RESUME_AGENTS,
            )
        if len(prompt) > PROMPT_MAX_LEN:
            return self.send_error_json(400, "prompt too long")

        if _runner.is_busy():
            return self.send_error_json(409, "agent busy")

        conv.add_user(raw_prompt)
        # cwd = the selected target workdir (harness_dirs[0]), so the agent discovers that
        # project's CLAUDE.md + .claude/skills — mirrors the original SCENARIO_WORKDIRS.
        target_dir = str(resolve_target(target))
        harness = [target_dir] + [h for h in env.get("harness_dirs", []) if h != target_dir]
        assistant_chunks: list[str] = []
        session_dir_bound = bool(conv.session_dir)

        # Binding events to the conversation happens on the **pump side**: it must happen even with
        # no consumer, so it cannot live in the response (closing the window would lose the result).
        state = {"chunks": [], "bound": bool(conv.session_dir)}

        def _absorb(ev):
            t = ev.get("type")
            if t == "session":
                sid = ev.get("cli_session_id")
                if sid:
                    _conversations.bind_cli_session(conv, sid)
            elif t == "message":
                text = ev.get("text") or ""
                if ev.get("final"):
                    state["chunks"] = [text]
                else:
                    state["chunks"].append(text)
            elif t == "done":
                if not state["bound"] and ev.get("session_dir"):
                    _conversations.bind_session_dir(conv, ev["session_dir"])
                    state["bound"] = True
                assistant_text = "".join(state["chunks"]).strip()
                if assistant_text:
                    from dx_agent_dev.core.message_sanitize import sanitize_assistant_text
                    conv.add_assistant(sanitize_assistant_text(assistant_text))
                _conversations.save(conv)

        source = _runner.run(
            prompt, harness, adapter=adapter, conversation=conv, run_ctx=run_ctx,
        )
        try:
            _live.start(source, cancel=_runner.cancel, on_event=_absorb,
                        info={"prompt": raw_prompt, "conversation_id": conv.id,
                              "mode": "autopilot" if autopilot else "interactive"})
        except RuntimeError:
            return self.send_error_json(409, "agent busy")

        self._stream_live(0, conversation_id=conv.id)


def create_server(port: int = PORT):
    return ThreadingHTTPServer(("127.0.0.1", port), AgentDevHandler)


if __name__ == "__main__":
    from shared.dx_server import DXServer
    DXServer(AgentDevHandler, SERVER_NAME, PORT).start()

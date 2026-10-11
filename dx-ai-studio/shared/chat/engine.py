"""ChatEngine — orchestrates config, prompt building, provider calls, and fallback."""
from __future__ import annotations

import os
from pathlib import Path
from shared.agent_cli import LOGIN_HINTS, detect, resolve_chat_source
from .config import load_config, mask_api_key
from .providers import stream_chat, ChatAPIError
from .prompt_builder import build_system_prompt
from .fallback import FallbackEngine

_knowledge_synced = False


def _maybe_sync_knowledge():
    """Regenerate SDK knowledge from .deepx if stale. Opt-in + once-per-process."""
    global _knowledge_synced
    if _knowledge_synced or os.environ.get("DX_CHAT_KNOWLEDGE_SYNC") != "1":
        return
    _knowledge_synced = True
    try:
        from .knowledge_sync import sync_if_stale
        sync_if_stale()
    except Exception:
        pass  # knowledge sync is best-effort; never block chat


class ChatEngine:
    def __init__(self, app_name: str, context_callback=None, fallback_rules=None):
        """
        app_name: "dx_app", "dx_stream", "dx_modelzoo", "dx_compiler", etc.
        context_callback: callable returning dict (runtime context for prompt)
        fallback_rules: list of (keywords, response) tuples for app-specific fallback
        """
        self.app_name = app_name
        self.context_callback = context_callback
        self.fallback = FallbackEngine(app_rules=fallback_rules or [])
        self._knowledge_dir = Path(__file__).parent / "knowledge"

    def stream(
        self,
        message: str,
        history: list | None = None,
        lang: str = "en",
        runtime_context: dict | None = None,
    ):
        """Generator[str] — yields tokens from LLM or fallback response."""
        # 0. Lazily sync SDK knowledge from the live .deepx warehouse. Normally a no-op: the
        #    launcher pre-syncs once at boot (see launcher.main()) so the shared knowledge
        #    files are already fresh by the time any module server serves a chat. This
        #    env-gated lazy path is an opt-in fallback for a module server started standalone
        #    (without the launcher), and stays off by default so tests/imports are
        #    side-effect-free.
        _maybe_sync_knowledge()
        config = load_config()
        source = resolve_chat_source(config)
        if source["kind"] == "none":
            yield from self._fallback_response(message, lang=lang)
            return
        if source["kind"] == "saved":
            provider, api_key = config["provider"], config.get("api_key", "")
            model, endpoint = config["model"], config.get("endpoint")
            temperature = config.get("temperature", 0.7)
        else:   # Studio agent or the first logged-in CLI — no setup needed (spec 2026-10-11 chat settings §3.1)
            provider, api_key, endpoint, temperature = "agent-cli", "", None, 0.7
            model = source["agent"] + (f"::{source['model']}" if source["model"] else "")

        if runtime_context is None and self.context_callback is not None:
            try:
                runtime_context = self.context_callback()
            except Exception:
                runtime_context = None

        system_prompt = build_system_prompt(
            knowledge_dir=self._knowledge_dir,
            app_name=self.app_name,
            user_message=message,
            runtime_context=runtime_context,
        )

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        try:
            yield from stream_chat(
                provider=provider,
                api_key=api_key,
                model=model,
                messages=messages,
                endpoint=endpoint,
                temperature=temperature,
            )
        except ChatAPIError as exc:
            # key 를 넣은 사용자에게 offline fallback ("No AI model connected") 을 보이면 틀린 말이 된다 —
            # 무엇이 실패했는지 말한다 (2026-10-11, 실제 Anthropic 401 로 확인).
            yield self._api_error_text(provider, exc, lang, agent=source.get("agent"))
        except Exception as exc:
            yield from self._error_response(type(exc).__name__, str(exc), lang=lang)

    def get_config_status(self) -> dict:
        """Chat config for the UI: what is saved, who answers now, and the coding-agent CLIs on this PC."""
        config = load_config()
        status = {"configured": config is not None, "source": resolve_chat_source(config), "agents": detect()}
        if config is not None:
            status.update({
                "provider": config.get("provider"),
                "model": config.get("model"),
                "api_key": mask_api_key(config.get("api_key")),
                "endpoint": config.get("endpoint", ""),
                "temperature": config.get("temperature", 0.7),
            })
        return status

    def _fallback_response(self, message: str, lang: str = "en"):
        """Generator[str] — yields fallback response as a single chunk."""
        result = self.fallback.respond(message, lang=lang)
        yield result["reply"]

    _API_ERROR_TEXT = {
        "invalid_api_key": {
            "en": "{provider} rejected the API key.",
            "ko": "{provider}에서 API key 를 거부했습니다.",
            "ja": "{provider} が API key を拒否しました。",
            "es": "{provider} rechazó la API key.",
            "zh-CN": "{provider} 拒绝了该 API key。",
            "zh-TW": "{provider} 拒絕了該 API key。",
        },
        "rate_limit": {
            "en": "{provider} refused the request: rate limit or quota reached.",
            "ko": "{provider}에서 요청을 거절했습니다: 사용 한도 (rate limit · quota) 에 닿았습니다.",
            "ja": "{provider} がリクエストを拒否しました: 利用上限 (rate limit · quota) に達しました。",
            "es": "{provider} rechazó la solicitud: se alcanzó el límite de uso (rate limit o cuota).",
            "zh-CN": "{provider} 拒绝了请求：已达到使用上限（rate limit · quota）。",
            "zh-TW": "{provider} 拒絕了請求：已達到使用上限（rate limit · quota）。",
        },
        "unreachable": {
            "en": "Studio could not reach {provider}.",
            "ko": "Studio 가 {provider} 에 연결하지 못했습니다.",
            "ja": "Studio は {provider} に接続できませんでした。",
            "es": "Studio no pudo conectar con {provider}.",
            "zh-CN": "Studio 无法连接到 {provider}。",
            "zh-TW": "Studio 無法連線到 {provider}。",
        },
        "timeout": {
            "en": "{provider} stopped answering.",
            "ko": "{provider} 의 응답이 멈췄습니다.",
            "ja": "{provider} の応答が止まりました。",
            "es": "{provider} dejó de responder.",
            "zh-CN": "{provider} 停止了响应。",
            "zh-TW": "{provider} 停止了回應。",
        },
        "api_error": {
            "en": "{provider} returned an error.",
            "ko": "{provider}에서 오류를 돌려줬습니다.",
            "ja": "{provider} がエラーを返しました。",
            "es": "{provider} devolvió un error.",
            "zh-CN": "{provider} 返回了错误。",
            "zh-TW": "{provider} 回傳了錯誤。",
        },
    }
    _API_ERROR_HINT = {
        "en": "Check the provider, model and key in **chat settings** (⚙️ in the chat header) — saving there checks the connection first.",
        "ko": "**채팅 설정**(채팅창 상단의 ⚙️)에서 provider · model · key 를 확인하세요 — 저장할 때 연결을 먼저 확인합니다.",
        "ja": "**チャット設定**（チャットヘッダーの⚙️）で provider・model・key を確認してください。保存時に接続を先に確認します。",
        "es": "Revise el proveedor, el modelo y la key en la **configuración del chat** (⚙️ en el encabezado); al guardar se comprueba primero la conexión.",
        "zh-CN": "请在**聊天设置**（聊天标题栏的⚙️）中检查 provider、model 和 key；保存时会先检查连接。",
        "zh-TW": "請在**聊天設定**（聊天標題列的⚙️）中檢查 provider、model 和 key；儲存時會先檢查連線。",
    }
    _PROVIDER_NAMES = {"openai": "OpenAI", "anthropic": "Anthropic", "google": "Google (Gemini)",
                       "github": "GitHub Models", "custom": "Custom endpoint", "local": "local LLM server"}

    _LOGIN_LINE = {
        "en": "If the login expired, sign in again in a terminal: `{cmd}`",
        "ko": "로그인이 만료됐다면 터미널에서 다시 로그인하세요: `{cmd}`",
        "ja": "ログインが切れた場合はターミナルで再ログインしてください: `{cmd}`",
        "es": "Si la sesión caducó, vuelva a iniciarla en una terminal: `{cmd}`",
        "zh-CN": "如果登录已过期，请在终端重新登录：`{cmd}`",
        "zh-TW": "如果登入已過期，請在終端機重新登入：`{cmd}`",
    }

    def _api_error_text(self, provider: str, exc: ChatAPIError, lang: str = "en", agent: str | None = None) -> str:
        """What failed, in the user's language, with the provider's own reason as detail. A coding-agent CLI is
        named by itself (claude, copilot …) and gets the command that signs it in again."""
        texts = self._API_ERROR_TEXT.get(exc.error_type, self._API_ERROR_TEXT["api_error"])
        if provider == "agent-cli" and agent:
            name = agent
        else:
            name = self._PROVIDER_NAMES.get(provider, provider or "API")
        head = texts.get(lang, texts["en"]).format(provider=name)
        detail = str(exc).strip()
        login = ""
        if provider == "agent-cli" and agent in LOGIN_HINTS and exc.error_type != "rate_limit":
            login = "\n\n" + self._LOGIN_LINE.get(lang, self._LOGIN_LINE["en"]).format(cmd=LOGIN_HINTS[agent])
        hint = self._API_ERROR_HINT.get(lang, self._API_ERROR_HINT["en"])
        return f"⚠️ **{head}**" + (f"\n\n`{detail}`" if detail else "") + login + f"\n\n{hint}"

    def _error_response(self, error_type: str, detail: str, lang: str = "en"):
        """Generator[str] — yields error message as a single chunk."""
        messages = {
            "en": "Please check API settings in **chat settings** (⚙️ in the chat header).",
            "ko": "**채팅 설정**(채팅창 상단의 ⚙️)에서 API 설정을 확인해주세요.",
            "ja": "チャットヘッダーの⚙️にある**チャット設定**でAPI設定を確認してください。",
            "es": "Compruebe la configuración de API en la **configuración del chat** (⚙️ en el encabezado del chat).",
            "zh-CN": "请在聊天标题栏的⚙️中检查**聊天设置**里的 API 设置。",
            "zh-TW": "請在聊天標題列的⚙️中檢查**聊天設定**裡的 API 設定。",
        }
        yield f"⚠️ **{error_type}**: {detail}\n\n{messages.get(lang, messages['en'])}"

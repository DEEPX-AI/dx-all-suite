"""ChatEngine — orchestrates config, prompt building, provider calls, and fallback."""
from __future__ import annotations

import os
from pathlib import Path
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
        if config is None:
            yield from self._fallback_response(message, lang=lang)
            return

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
                provider=config["provider"],
                api_key=config["api_key"],
                model=config["model"],
                messages=messages,
                endpoint=config.get("endpoint"),
                temperature=config.get("temperature", 0.7),
            )
        except ChatAPIError:
            yield from self._fallback_response(message, lang=lang)
        except Exception as exc:
            yield from self._error_response(type(exc).__name__, str(exc), lang=lang)

    def get_config_status(self) -> dict:
        """Returns chat config status for UI."""
        config = load_config()
        if config is None:
            return {"configured": False}
        return {
            "configured": True,
            "provider": config.get("provider"),
            "model": config.get("model"),
            "api_key": mask_api_key(config.get("api_key")),
            "endpoint": config.get("endpoint", ""),
            "temperature": config.get("temperature", 0.7),
        }

    def _fallback_response(self, message: str, lang: str = "en"):
        """Generator[str] — yields fallback response as a single chunk."""
        result = self.fallback.respond(message, lang=lang)
        yield result["reply"]

    def _error_response(self, error_type: str, detail: str, lang: str = "en"):
        """Generator[str] — yields error message as a single chunk."""
        messages = {
            "en": "Please check API settings in **chat settings** (⚙️ in the chat header).",
            "ko": "**채팅 설정**(채팅창 상단의 ⚙️)에서 API 설정을 확인해주세요.",
            "ja": "チャットヘッダーの⚙️にある**チャット設定**でAPI設定を確認してください。",
            "es": "Comprueba la configuración de API en la **configuración del chat** (⚙️ en el encabezado del chat).",
            "zh-CN": "请在聊天标题栏的⚙️中检查**聊天设置**里的 API 设置。",
            "zh-TW": "請在聊天標題列的⚙️中檢查**聊天設定**裡的 API 設定。",
        }
        yield f"⚠️ **{error_type}**: {detail}\n\n{messages.get(lang, messages['en'])}"

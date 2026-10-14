"""Rule-based fallback engine for when no AI answers (no signed-in coding agent, local server or API key)."""
from __future__ import annotations

import re


def _keyword_matches(keyword: str, lower_message: str) -> bool:
    """Match keyword in message: word-boundary for short ASCII, substring for CJK."""
    kw = keyword.lower()
    if not kw:
        return False
    if len(kw) <= 3 and re.fullmatch(r"[a-z0-9_+-]+", kw):
        return re.search(rf"(?<![a-z0-9_+-]){re.escape(kw)}(?![a-z0-9_+-])", lower_message) is not None
    return kw in lower_message


COMMON_RULES: list[tuple[list[str], dict[str, str]]] = [
    (
        ["안녕", "hello", "hi", "hey", "반가", "こんにちは", "你好"],
        {
            "ko": "안녕하세요! 🤖 **DX Assistant**입니다.\n"
                  "DEEPX Edge AI 플랫폼에 대해 무엇이든 물어보세요!\n\n"
                  "💡 터미널에서 coding agent (claude · copilot · cursor) 에 로그인하면 설정 없이 AI 가 답합니다. local LLM server 나 cloud API 키는 채팅 설정(⚙️)에서 고릅니다.",
            "en": "Hello! 🤖 I'm **DX Assistant**.\n"
                  "Ask me anything about the DEEPX Edge AI platform!\n\n"
                  "💡 Sign in to a coding agent (claude · copilot · cursor) in a terminal and the AI answers with no setup. A local LLM server or a cloud API key is picked in chat settings (⚙️).",
            "ja": "こんにちは! 🤖 **DX Assistant** です。\n"
                  "DEEPX Edge AI プラットフォームについて何でも質問してください!\n\n"
                  "💡 ターミナルでコーディングエージェント (claude · copilot · cursor) にログインすると、設定なしで AI が回答します。ローカル LLM サーバーやクラウド API キーはチャット設定(⚙️)で選びます。",
            "zh-CN": "你好！🤖 我是 **DX Assistant**。\n"
                     "欢迎询问任何有关 DEEPX Edge AI 平台的问题！\n\n"
                     "💡 在终端登录编码智能体 (claude · copilot · cursor) 后，AI 无需设置即可回答。本地 LLM 服务器或云 API 密钥可在聊天设置(⚙️)中选择。",
            "zh-TW": "你好！🤖 我是 **DX Assistant**。\n"
                     "歡迎詢問任何關於 DEEPX Edge AI 平台的問題！\n\n"
                     "💡 在終端機登入編碼智能體 (claude · copilot · cursor) 後，AI 無需設定即可回答。本機 LLM 伺服器或雲端 API 金鑰可在聊天設定(⚙️)中選擇。",
            "es": "¡Hola! 🤖 Soy **DX Assistant**.\n"
                  "Pregúnteme lo que desee sobre la plataforma DEEPX Edge AI.\n\n"
                  "💡 Inicie sesión en un agente de codificación (claude · copilot · cursor) en una terminal y la IA responde sin configurar nada. Un servidor LLM local o una clave API en la nube se eligen en la configuración del chat (⚙️).",
        },
    ),
    (
        ["도움", "help", "사용법", "기능", "ヘルプ", "帮助", "說明",
         "what does this app do", "이 앱", "このアプリ", "这个应用", "這個應用"],
        {
            "ko": "**DX AI Studio** 주요 기능:\n"
                  "- **DX App** — NPU 실시간 추론, 데모 실행, 모델 비교\n"
                  "- **DX Stream** — GStreamer 영상 파이프라인 · 데모\n"
                  "- **DX Model Zoo** — 약 500개 DEEPX 모델 카탈로그\n"
                  "- **DX Compiler** — ONNX → DXNN 컴파일\n"
                  "- **DX Benchmark** — 보드별 실측 성능\n"
                  "- **DX Monitor** — NPU · 시스템 실시간 상태\n"
                  "- **DX EdgeGuide** — 작업에 맞는 보드 · 호스트 추천\n"
                  "- **DX Agent Dev** — 자연어로 NPU 앱 만들기\n"
                  "- **DX Edge** — AWS 클라우드 컴파일과 엣지 배포",
            "en": "**DX AI Studio** key features:\n"
                  "- **DX App** — real-time NPU inference, demos, model comparison\n"
                  "- **DX Stream** — GStreamer video pipelines and demos\n"
                  "- **DX Model Zoo** — catalog of nearly 500 DEEPX models\n"
                  "- **DX Compiler** — ONNX → DXNN compilation\n"
                  "- **DX Benchmark** — measured performance per board\n"
                  "- **DX Monitor** — live NPU and system status\n"
                  "- **DX EdgeGuide** — board and host recommendation for a workload\n"
                  "- **DX Agent Dev** — build NPU apps in natural language\n"
                  "- **DX Edge** — AWS cloud compile and edge deployment",
            "ja": "**DX AI Studio** の主な機能:\n"
                  "- **DX App** — NPU リアルタイム推論、デモ実行、モデル比較\n"
                  "- **DX Stream** — GStreamer 映像パイプラインとデモ\n"
                  "- **DX Model Zoo** — 約 500 の DEEPX モデルカタログ\n"
                  "- **DX Compiler** — ONNX → DXNN コンパイル\n"
                  "- **DX Benchmark** — ボードごとの実測性能\n"
                  "- **DX Monitor** — NPU とシステムのリアルタイム状態\n"
                  "- **DX EdgeGuide** — ワークロードに合うボードとホストの推奨\n"
                  "- **DX Agent Dev** — 自然言語で NPU アプリを作成\n"
                  "- **DX Edge** — AWS クラウドコンパイルとエッジデプロイ",
            "zh-CN": "**DX AI Studio** 主要功能:\n"
                     "- **DX App** — NPU 实时推理、演示运行、模型对比\n"
                     "- **DX Stream** — GStreamer 视频管道与演示\n"
                     "- **DX Model Zoo** — 近 500 个 DEEPX 模型目录\n"
                     "- **DX Compiler** — ONNX → DXNN 编译\n"
                     "- **DX Benchmark** — 各开发板的实测性能\n"
                     "- **DX Monitor** — NPU 与系统实时状态\n"
                     "- **DX EdgeGuide** — 按工作负载推荐开发板与主机\n"
                     "- **DX Agent Dev** — 用自然语言构建 NPU 应用\n"
                     "- **DX Edge** — AWS 云端编译与边缘部署",
            "zh-TW": "**DX AI Studio** 主要功能:\n"
                     "- **DX App** — NPU 即時推論、示範執行、模型比較\n"
                     "- **DX Stream** — GStreamer 影像管線與示範\n"
                     "- **DX Model Zoo** — 近 500 個 DEEPX 模型目錄\n"
                     "- **DX Compiler** — ONNX → DXNN 編譯\n"
                     "- **DX Benchmark** — 各開發板的實測效能\n"
                     "- **DX Monitor** — NPU 與系統即時狀態\n"
                     "- **DX EdgeGuide** — 依工作負載推薦開發板與主機\n"
                     "- **DX Agent Dev** — 用自然語言建立 NPU 應用程式\n"
                     "- **DX Edge** — AWS 雲端編譯與邊緣部署",
            "es": "Funciones principales de **DX AI Studio**:\n"
                  "- **DX App** — inferencia NPU en tiempo real, demos y comparación de modelos\n"
                  "- **DX Stream** — pipelines de video GStreamer y demos\n"
                  "- **DX Model Zoo** — catálogo de casi 500 modelos DEEPX\n"
                  "- **DX Compiler** — compilación ONNX → DXNN\n"
                  "- **DX Benchmark** — rendimiento medido por placa\n"
                  "- **DX Monitor** — estado en vivo de la NPU y del sistema\n"
                  "- **DX EdgeGuide** — recomendación de placa y host para una carga de trabajo\n"
                  "- **DX Agent Dev** — cree apps para NPU en lenguaje natural\n"
                  "- **DX Edge** — compilación en AWS y despliegue edge",
        },
    ),
]

# The three ways to connect, in the order a user should try them: a logged-in CLI (no setup) → local server → cloud key.
SETUP_BANNER = {
    "ko": "⚠️ 연결된 AI 가 없습니다 — Studio 는 **모델을 내장하지 않습니다** (오프라인 우선 설계).\n"
          "• 터미널에서 coding agent (claude · copilot · cursor …) 에 로그인하면 **설정 없이** 그 계정으로 답합니다.\n"
          "• 또는 **채팅 설정**(⚙️)에서 내 local LLM server (Ollama 호환) 나 cloud API 키 (OpenAI · Anthropic · Google …) 를 고르세요.",
    "en": "⚠️ No AI connected — Studio ships with **no bundled model** (offline by design).\n"
          "• Sign in to a coding agent (claude · copilot · cursor …) in a terminal and Chat answers through it **with no setup**.\n"
          "• Or pick your local LLM server (Ollama-compatible) or a cloud API key (OpenAI · Anthropic · Google …) in **chat settings** (⚙️).",
    "ja": "⚠️ 接続された AI がありません — Studio は**モデルを同梱していません**(オフライン設計)。\n"
          "• ターミナルでコーディングエージェント (claude · copilot · cursor …) にログインすると、**設定なしで**そのアカウントで回答します。\n"
          "• または**チャット設定**(⚙️)で自分のローカル LLM サーバー (Ollama 互換) かクラウド API キー (OpenAI · Anthropic · Google …) を選んでください。",
    "zh-CN": "⚠️ 尚未连接 AI — Studio **不内置任何模型**(按设计离线运行)。\n"
             "• 在终端登录编码智能体 (claude · copilot · cursor …) 后，聊天会**无需设置**直接用该账号回答。\n"
             "• 或在**聊天设置**(⚙️)中选择您的本地 LLM 服务器 (兼容 Ollama) 或云 API 密钥 (OpenAI · Anthropic · Google …)。",
    "zh-TW": "⚠️ 尚未連接 AI — Studio **不內建任何模型**(依設計離線運作)。\n"
             "• 在終端機登入編碼智能體 (claude · copilot · cursor …) 後，聊天會**無需設定**直接用該帳號回答。\n"
             "• 或在**聊天設定**(⚙️)中選擇您的本機 LLM 伺服器 (相容 Ollama) 或雲端 API 金鑰 (OpenAI · Anthropic · Google …)。",
    "es": "⚠️ No hay ninguna IA conectada — Studio **no incluye ningún modelo** (diseñado para funcionar sin conexión).\n"
          "• Inicie sesión en un agente de codificación (claude · copilot · cursor …) en una terminal y el chat responde con esa cuenta **sin configurar nada**.\n"
          "• O elija su servidor LLM local (compatible con Ollama) o una clave API en la nube (OpenAI · Anthropic · Google …) en la **configuración del chat** (⚙️).",
}

DEFAULT_RESPONSE = {
    "ko": "죄송합니다, 지금은 연결된 AI 가 없어 자세한 답변이 어렵습니다.\n\n"
          "터미널에서 coding agent (claude · copilot · cursor) 에 로그인하면 설정 없이 답합니다. "
          "local LLM server 나 cloud API 키는 **채팅 설정**(⚙️)에서 고릅니다.",
    "en": "Sorry, no AI is connected right now for detailed answers.\n\n"
          "Sign in to a coding agent (claude · copilot · cursor) in a terminal and Chat answers with no setup. "
          "A local LLM server or a cloud API key is picked in **chat settings** (⚙️).",
    "ja": "申し訳ありません。現在 AI が接続されていないため、詳細な回答はできません。\n\n"
          "ターミナルでコーディングエージェント (claude · copilot · cursor) にログインすると設定なしで回答します。"
          "ローカル LLM サーバーやクラウド API キーは**チャット設定**(⚙️)で選びます。",
    "zh-CN": "抱歉，当前未连接 AI，无法提供详细回答。\n\n"
             "在终端登录编码智能体 (claude · copilot · cursor) 后无需设置即可回答。"
             "本地 LLM 服务器或云 API 密钥可在**聊天设置**(⚙️)中选择。",
    "zh-TW": "抱歉，目前未連接 AI，無法提供詳細回答。\n\n"
             "在終端機登入編碼智能體 (claude · copilot · cursor) 後無需設定即可回答。"
             "本機 LLM 伺服器或雲端 API 金鑰可在**聊天設定**(⚙️)中選擇。",
    "es": "Lo sentimos, ahora no hay ninguna IA conectada para respuestas detalladas.\n\n"
          "Inicie sesión en un agente de codificación (claude · copilot · cursor) en una terminal y el chat responde sin configurar nada. "
          "Un servidor LLM local o una clave API en la nube se eligen en la **configuración del chat** (⚙️).",
}

# Keyword lists for identifying match type
_GREETING_KEYWORDS = COMMON_RULES[0][0]
_HELP_KEYWORDS = COMMON_RULES[1][0]


class FallbackEngine:
    def __init__(self, app_rules: list[tuple[list[str], str | dict]] | None = None):
        """app_rules: list of (keywords, response) tuples for app-specific rules."""
        self._app_rules = app_rules or []

    def respond(self, message: str, lang: str = "en") -> dict:
        """Returns {"reply": str, "is_fallback": True, "suggestions": list[str]}."""
        lower = message.lower()

        for keywords, response in self._app_rules:
            if any(_keyword_matches(kw, lower) for kw in keywords):
                if isinstance(response, dict):
                    resp_text = response.get(lang) or response.get("en") or next(iter(response.values()), "")
                else:
                    resp_text = response
                banner = SETUP_BANNER.get(lang, SETUP_BANNER["en"])
                reply = f"{banner}\n\n---\n\n{resp_text}"
                return {
                    "reply": reply,
                    "is_fallback": True,
                    "suggestions": self._suggestions(lang),
                }

        for keywords, response in COMMON_RULES:
            if any(_keyword_matches(kw, lower) for kw in keywords):
                resp_text = response.get(lang) or response.get("en") or next(iter(response.values()), "")
                banner = SETUP_BANNER.get(lang, SETUP_BANNER["en"])
                reply = f"{banner}\n\n---\n\n{resp_text}"
                suggestions = self._suggestions_for(keywords, lang)
                return {
                    "reply": reply,
                    "is_fallback": True,
                    "suggestions": suggestions,
                }

        banner = SETUP_BANNER.get(lang, SETUP_BANNER["en"])
        default = DEFAULT_RESPONSE.get(lang, DEFAULT_RESPONSE["en"])
        reply = f"{banner}\n\n---\n\n{default}"
        return {
            "reply": reply,
            "is_fallback": True,
            "suggestions": self._suggestions(lang),
        }

    def _suggestions(self, lang: str) -> list[str]:
        suggestions = {
            "ko": ["안녕", "도움말", "이 앱 기능이 뭐야?"],
            "en": ["Hello", "Help", "What does this app do?"],
            "ja": ["こんにちは", "ヘルプ", "このアプリは何ができますか？"],
            "zh-CN": ["你好", "帮助", "这个应用能做什么？"],
            "zh-TW": ["你好", "說明", "這個應用可以做什麼？"],
            "es": ["Hola", "Ayuda", "¿Qué hace esta aplicación?"],
        }
        return suggestions.get(lang, suggestions["en"])

    @staticmethod
    def _suggestions_for(keywords: list[str], lang: str) -> list[str]:
        greeting = {
            "ko": ["이 앱은 뭐하는 앱이야?", "도움말"],
            "en": ["What does this app do?", "Help"],
            "ja": ["このアプリは何ができますか？", "ヘルプ"],
            "zh-CN": ["这个应用能做什么？", "帮助"],
            "zh-TW": ["這個應用可以做什麼？", "說明"],
            "es": ["¿Qué hace esta aplicación?", "Ayuda"],
        }
        more = {
            "ko": ["더 자세히 알려줘"],
            "en": ["Tell me more"],
            "ja": ["詳しく教えて"],
            "zh-CN": ["请更详细地说明"],
            "zh-TW": ["請更詳細說明"],
            "es": ["Cuénteme más"],
        }
        if keywords is _GREETING_KEYWORDS:
            return greeting.get(lang, greeting["en"])
        if keywords is _HELP_KEYWORDS:
            return []
        return more.get(lang, more["en"])

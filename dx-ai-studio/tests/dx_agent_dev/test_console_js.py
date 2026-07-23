"""console.js 드롭다운/페이로드 계약(정적 소스 검증)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = ROOT / "dx_agent_dev" / "static" / "js" / "console.js"


def test_populates_agent_select_from_status():
    src = JS.read_text(encoding="utf-8")
    assert "agent-select" in src
    assert "model-select" in src
    assert "agents" in src  # status.agents 사용


def test_run_payload_includes_agent_and_model():
    src = JS.read_text(encoding="utf-8")
    compact = src.replace(" ", "").replace("\n", "")
    assert "agent:" in compact
    assert "model:" in compact


def test_agent_change_updates_models():
    src = JS.read_text(encoding="utf-8")
    assert "addEventListener('change'" in src or 'addEventListener("change"' in src


def test_console_chat_turn_markup():
    src = JS.read_text(encoding="utf-8")
    assert "chat-turn" in src
    assert "activity-panel" in src
    assert "renderMarkdown" in src
    assert "applySpecLayout" in src
    assert "DXMarkdownRender" in src
    assert "sanitizeAssistantText" in src
    assert "agent-auth-badge" in src
    assert "updateModelQualityHint" in src
    assert "extractModelNotice" in src


def test_console_streaming_defers_heavy_markdown():
    src = JS.read_text(encoding="utf-8")
    assert "paintStreamingAssistant" in src
    assert "scheduleStreamingRender" in src
    assert "assistant-body--streaming" in src
    assert "updateAssistantView(true)" in src
    assert "renderMermaidBlocks(_turn.assistantBody)" in src


def test_console_follow_up_uses_conversation_id():
    src = JS.read_text(encoding="utf-8")
    assert "_conversationId" in src
    assert "conversation_id:" in src.replace(" ", "")
    assert "buildPromptWithContext" not in src
    assert "_chatHistory" not in src


def test_console_follow_up_preserves_input_when_busy():
    src = JS.read_text(encoding="utf-8")
    assert "releaseRunLock" in src
    assert "Agent is still running" in src
    submit = src[src.index("form.addEventListener('submit'"):]
    submit = submit[:submit.index("runPrompt(prompt)")]
    assert "if (_running)" in submit
    assert submit.index("if (_running)") < submit.index("input.value = ''")


def test_ui_controls_in_header():
    html = (ROOT / "dx_agent_dev" / "templates" / "index.html").read_text(encoding="utf-8")
    assert "console-select" in html
    assert "model-quality-hint" in html
    assert html.index('class="console-header"') < html.index('id="agent-controls"')
    assert html.index('id="agent-controls"') < html.index('id="console-output"')

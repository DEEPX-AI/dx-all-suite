"""Harness noise removal from assistant messages."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))

from core.message_sanitize import (  # noqa: E402
    extract_model_notice,
    is_harness_status_line,
    sanitize_assistant_text,
)


SAMPLE = """[DX-AGENT-DEV: START]

███████████ DEEPX
 DX-AGENT-DEV · on-device NPU

══════════════════════════════════════════════════════════════
⚠ DX-AGENT-DEV: MODEL NOTICE

DX Agent-Driven Development recommends Claude Sonnet 4.6+ or
Opus 4.6+. Your current model may produce lower quality.
══════════════════════════════════════════════════════════════

/dx-skill-router 기준으로 요구사항을 정리했습니다.

Syntax error in text
mermaid version 11.12.3

## 목표 정리

활동량 분석
"""


def test_strips_inline_start_banner_fence():
    raw = (
        "[DX-AGENT-DEV:START]```██████████████████ on-device NPU```\n\n"
        "## 목표\n\n실제 내용"
    )
    out = sanitize_assistant_text(raw)
    assert "on-device NPU" not in out
    assert "████████" not in out
    assert "목표" in out


def test_strips_sentinel_and_banner():
    out = sanitize_assistant_text(SAMPLE)
    assert "[DX-AGENT-DEV" not in out
    assert "████████" not in out
    assert "on-device NPU" not in out
    assert "Syntax error in text" not in out
    assert "목표 정리" in out


def test_extract_model_notice():
    body, notice = extract_model_notice(SAMPLE)
    assert notice
    assert "Sonnet 4.6" in notice
    assert "MODEL NOTICE" not in body


def test_harness_status_line_detection():
    assert is_harness_status_line("[DX-AGENT-DEV: START]")
    assert is_harness_status_line("Syntax error in text")
    assert not is_harness_status_line("Plan A for soccer tracking")


def test_classify_plain_harness_line_hidden():
    from core.adapters.base import classify_plain_line

    ev = classify_plain_line("[DX-AGENT-DEV: START]")
    assert ev.get("hidden") is True


def test_final_result_sanitized():
    from core.adapters.base import _map_json_event
    import json

    raw = json.dumps({
        "type": "result",
        "subtype": "success",
        "result": "[DX-AGENT-DEV: START]\n\nHello world",
    })
    ev = _map_json_event(json.loads(raw), raw)
    assert ev["type"] == "message"
    assert ev["text"] == "Hello world"
    assert ev.get("final") is True

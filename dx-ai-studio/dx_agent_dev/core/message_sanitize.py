"""Assistant message cleanup: strip DX harness protocol noise from user-facing chat."""
from __future__ import annotations

import re
from typing import Optional

_DX_SENTINEL = re.compile(r"\[DX-AGENT-DEV:\s*(?:START|DONE)", re.I)
_START_ANYWHERE = re.compile(r"\[DX-AGENT-DEV:\s*START\]", re.I)
_DONE_ANYWHERE = re.compile(r"\[DX-AGENT-DEV:\s*DONE[^\]]*\]", re.I)
_INLINE_HARNESS = re.compile(
    r"\[DX-AGENT-DEV:\s*START\][^\n]*on-device NPU[^\n]*",
    re.I,
)
_BANNER_LINE = re.compile(r"[█░]")
_MODEL_NOTICE_HEAD = re.compile(r"DX-AGENT-DEV:\s*MODEL NOTICE", re.I)
_MODEL_NOTICE_BLOCK = re.compile(
    r"(?:^|\n)[═=]{3,}\s*\r?\n⚠\s*DX-AGENT-DEV:\s*MODEL NOTICE([\s\S]*?)(?:[═=]{3,}\s*\r?\n|$)",
    re.I,
)
_MODEL_NOTICE_INLINE = re.compile(
    r"(?:^|\n)⚠\s*DX-AGENT-DEV:\s*MODEL NOTICE([\s\S]*?)(?=\n\n|\r?\n(?=[A-Za-z0-9\u0080-\uFFFF*#]))",
    re.I,
)
_BANNER_BLOCK = re.compile(
    r"(?:^|\n)[^\n]*████████[^\n]*\n(?:[^\n]*[█░][^\n]*\n)+[^\n]*on-device NPU[^\n]*\n?",
    re.I,
)
_SIMPLE_BANNER = re.compile(
    r"(?:^|\n)(?:[^\n]*[█░][^\n]*\n)+[^\n]*on-device NPU[^\n]*\n?",
    re.I,
)
_BANNER_FENCE = re.compile(
    r"```[\s\S]*?████████[\s\S]*?on-device NPU[\s\S]*?```",
    re.I,
)
_MERMAID_JUNK = re.compile(
    r"(?:^|\n)Syntax error in text\s*(?:\n(?:mermaid version[^\n]*)?)?",
    re.I,
)


def is_harness_status_line(line: str) -> bool:
    """True when a single stdout line is harness protocol (not user content)."""
    stripped = (line or "").strip()
    if not stripped:
        return True
    if _DX_SENTINEL.search(stripped):
        return True
    if _INLINE_HARNESS.search(stripped):
        return True
    if _MODEL_NOTICE_HEAD.search(stripped):
        return True
    if _BANNER_LINE.search(stripped) and "on-device NPU" in stripped:
        return True
    if stripped.startswith("═") and len(stripped) >= 10:
        return True
    if _MERMAID_JUNK.match(stripped):
        return True
    return False


def extract_model_notice(text: str) -> tuple[str, Optional[str]]:
    """Return (body_without_notice, notice_body_or_none)."""
    if not text:
        return "", None
    notice = None
    for pat in (_MODEL_NOTICE_BLOCK, _MODEL_NOTICE_INLINE):
        m = pat.search(text)
        if m:
            body = m.group(1) or ""
            notice = re.sub(r"^[═=\s⚠]+", "", body.strip())
            notice = re.sub(r"[═=]{3,}\s*$", "", notice).strip()
            text = (text[: m.start()] + text[m.end() :]).strip()
            break
    return text, notice or None


def sanitize_assistant_text(text: str) -> str:
    """Remove harness markers/banners/junk; keep substantive assistant reply."""
    if not text:
        return ""
    s, _ = extract_model_notice(text)
    s = _INLINE_HARNESS.sub("", s)
    s = _START_ANYWHERE.sub("", s)
    s = _DONE_ANYWHERE.sub("", s)
    s = re.sub(r"^\[DX-AGENT-DEV:\s*START\]\s*\r?\n?", "", s, flags=re.I | re.M)
    s = re.sub(r"^\[DX-AGENT-DEV:\s*DONE[^\]]*\]\s*\r?\n?", "", s, flags=re.I | re.M)
    s = _BANNER_FENCE.sub("", s)
    s = _BANNER_BLOCK.sub("\n", s)
    s = _SIMPLE_BANNER.sub("\n", s)
    s = _MERMAID_JUNK.sub("\n", s)
    return re.sub(r"^\s*\n{2,}", "", s).strip()

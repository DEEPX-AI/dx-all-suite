"""Wrap user prompts for the Agent Dev web console (not an interactive TTY)."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from dx_agent_dev.core.conversation_store import Conversation

_CONSOLE_UX = """[DX Agent Dev Console — interaction rules]
- This is a web chat console: one user message per HTTP request. You cannot read stdin mid-run.
- If you need user input, ask your questions and STOP. Wait for the user's next message.
- Do NOT claim the user "skipped" questions unless they explicitly said "just build it", "use defaults",
  "기본값으로", "기본값으로 진행", or equivalent.
- Short numbered replies in the next message (e.g. "1", "2") are valid answers to your multiple-choice questions.
- Do not continue with default assumptions in the same run after asking questions — end the turn instead.

"""


def wrap_console_prompt(prompt: str, *, is_followup: bool = False) -> str:
    """Prepend console UX rules on the first turn only (follow-ups use CLI resume)."""
    body = (prompt or "").strip()
    if not body:
        return body
    if is_followup or body.startswith("[DX Agent Dev Console"):
        return body
    return _CONSOLE_UX + body


_AUTOPILOT_DIRECTIVE = """[DX Agent Dev — autopilot run]
- This is an automated run. Do NOT ask questions or present options.
- Proceed directly with the most appropriate approach; use sensible defaults from the
  knowledge base. Run to completion and produce the deliverables.

"""


def wrap_autopilot_prompt(prompt: str) -> str:
    """Prepend autopilot directive so the agent proceeds without asking questions."""
    body = (prompt or "").strip()
    if not body or body.startswith("[DX Agent Dev — autopilot"):
        return body
    return _AUTOPILOT_DIRECTIVE + body


def wrap_with_conversation_history(prompt: str, conversation: Optional["Conversation"]) -> str:
    """Fallback for adapters without native CLI resume — attach recent turns."""
    if not conversation or not conversation.turns:
        return prompt
    lines = ["[Conversation context — continue this thread]"]
    for turn in conversation.turns[-10:]:
        label = "User" if turn.role == "user" else "Assistant"
        lines.append(f"{label}: {turn.text}")
    lines.append("")
    lines.append(f"Latest user message: {prompt}")
    return "\n".join(lines)

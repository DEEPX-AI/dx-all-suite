"""Per-run context passed to adapters (multi-turn resume)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class RunContext:
    conversation_id: str
    is_followup: bool = False
    cli_session_id: Optional[str] = None
    supports_cli_resume: bool = True
    # Autopilot (no-interaction) mode: adapters may add flags to suppress interactive prompts.
    autopilot: bool = False

"""Persist Agent Dev chat conversations (multi-turn)."""
from __future__ import annotations

import json
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dx_agent_dev.core.config import STUDIO_DIR
from shared.paths import var_dir

CONVERSATIONS_DIR = var_dir("dx_agent_dev", "conversations")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class ConversationTurn:
    role: str
    text: str
    at: str = field(default_factory=_now_iso)


@dataclass
class Conversation:
    id: str
    agent: Optional[str] = None
    model: Optional[str] = None
    effort: Optional[str] = None
    session_dir: Optional[str] = None
    cli_session_id: Optional[str] = None
    turns: list[ConversationTurn] = field(default_factory=list)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    @property
    def is_followup(self) -> bool:
        return len(self.turns) > 0

    def add_user(self, text: str) -> None:
        self.turns.append(ConversationTurn(role="user", text=text))
        self.updated_at = _now_iso()

    def add_assistant(self, text: str) -> None:
        if not text.strip():
            return
        self.turns.append(ConversationTurn(role="assistant", text=text))
        self.updated_at = _now_iso()

    def to_json(self) -> dict:
        d = asdict(self)
        return d

    @classmethod
    def from_json(cls, data: dict) -> "Conversation":
        turns = [ConversationTurn(**t) for t in (data.get("turns") or [])]
        return cls(
            id=data["id"],
            agent=data.get("agent"),
            model=data.get("model"),
            effort=data.get("effort"),
            session_dir=data.get("session_dir"),
            cli_session_id=data.get("cli_session_id"),
            turns=turns,
            created_at=data.get("created_at") or _now_iso(),
            updated_at=data.get("updated_at") or _now_iso(),
        )


class ConversationStore:
    def __init__(self, root: Path | None = None):
        self._root = root or CONVERSATIONS_DIR
        self._lock = threading.Lock()

    def _path(self, conversation_id: str) -> Path:
        return self._root / f"{conversation_id}.json"

    def create(
        self,
        *,
        agent: Optional[str] = None,
        model: Optional[str] = None,
        effort: Optional[str] = None,
    ) -> Conversation:
        conv = Conversation(id=uuid.uuid4().hex, agent=agent, model=model, effort=effort)
        self.save(conv)
        return conv

    def get(self, conversation_id: str) -> Optional[Conversation]:
        if not conversation_id:
            return None
        path = self._path(conversation_id)
        if not path.is_file():
            return None
        with self._lock:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
        return Conversation.from_json(data)

    def save(self, conv: Conversation) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        path = self._path(conv.id)
        with self._lock:
            path.write_text(json.dumps(conv.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")

    def bind_session_dir(self, conv: Conversation, session_dir: str) -> None:
        conv.session_dir = str(session_dir)
        self.save(conv)

    def bind_cli_session(self, conv: Conversation, cli_session_id: str) -> None:
        if cli_session_id:
            conv.cli_session_id = cli_session_id
            self.save(conv)

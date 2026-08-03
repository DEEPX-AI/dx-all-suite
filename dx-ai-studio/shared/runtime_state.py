"""Atomic Studio-owned state for runtime candidate activation and rollback."""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path

from shared.paths import STUDIO_ROOT


DEFAULT_RUNTIME_STATE_PATH = STUDIO_ROOT / "var" / "runtime" / "state.json"


class RuntimePhase(Enum):
    DISCOVERED = "discovered"
    CANDIDATE_INSTALLING = "candidate_installing"
    CANDIDATE_VALIDATING = "candidate_validating"
    ACTIVE = "active"
    ROLLING_BACK = "rolling_back"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass(frozen=True)
class RuntimeState:
    active_version: str | None = None
    candidate_version: str | None = None
    phase: RuntimePhase = RuntimePhase.DISCOVERED
    reason: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["phase"] = self.phase.value
        return data

    @classmethod
    def from_dict(cls, value: dict) -> "RuntimeState":
        try:
            phase = RuntimePhase(value.get("phase", RuntimePhase.DISCOVERED.value))
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid runtime state phase") from exc
        return cls(
            active_version=value.get("active_version"),
            candidate_version=value.get("candidate_version"),
            phase=phase,
            reason=str(value.get("reason", "")),
        )


class RuntimeStateStore:
    """Persistent state store using write, fsync, and atomic rename."""

    def __init__(self, path: Path = DEFAULT_RUNTIME_STATE_PATH):
        self.path = Path(path)

    def load(self) -> RuntimeState:
        try:
            with self.path.open(encoding="utf-8") as handle:
                value = json.load(handle)
        except FileNotFoundError:
            return RuntimeState()
        except json.JSONDecodeError as exc:
            raise ValueError("Runtime state journal is invalid") from exc
        if not isinstance(value, dict):
            raise ValueError("Runtime state journal must be an object")
        return RuntimeState.from_dict(value)

    def save(self, state: RuntimeState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            prefix=".{}-".format(self.path.name),
            suffix=".tmp",
            dir=str(self.path.parent),
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(state.to_dict(), handle, sort_keys=True, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            try:
                Path(temporary).unlink()
            except FileNotFoundError:
                pass
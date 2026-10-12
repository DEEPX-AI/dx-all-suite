"""Contract for adapter results.

Every metadata adapter function returns a dict shaped like AdapterResult.
Uses only stdlib typing; no external dependencies.
"""

from __future__ import annotations

from typing import TypedDict


class AdapterResult(TypedDict, total=True):
    """Required fields of an adapter return value.

    Required fields:
        adapter: adapter name (e.g. "local_runtime")
        profile: source profile (e.g. "local", "internal")
        fetched_at: ISO 8601 timestamp
        ok: whether it succeeded
        models: model id → field dict
        errors: list of error messages
        warnings: list of warning messages
    """

    adapter: str
    profile: str
    fetched_at: str
    ok: bool
    models: dict[str, dict]
    errors: list[str]
    warnings: list[str]


ADAPTER_RESULT_REQUIRED_KEYS: set[str] = set(AdapterResult.__annotations__)

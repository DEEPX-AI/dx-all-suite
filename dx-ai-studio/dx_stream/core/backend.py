"""PipelineBackend protocol — structural typing contract for pipeline managers.

PipelineManager conforms to this protocol without inheriting from it.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class PipelineBackendProtocol(Protocol):
    """Structural contract for GStreamer pipeline backends."""

    def start(self, pipeline_str: str, extra_env: dict | None = None) -> str:
        """Start a pipeline. Returns a pipeline_id string."""
        ...

    def stop(self) -> None:
        """Stop the currently running pipeline."""
        ...

    def is_running(self) -> bool:
        """Return True if a pipeline is currently active."""
        ...

    def get_pipeline_id(self) -> str | None:
        """Return the current pipeline ID, or None."""
        ...

    def get_last_error(self) -> str | None:
        """Return the last error message, or None."""
        ...

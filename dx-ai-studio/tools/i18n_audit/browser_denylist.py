"""English phrase denylist for post-switch browser copy audit.

When ``locale != 'en'`` and language markers switched successfully, visible UI
samples must not contain these known stale-English fragments (dynamic chrome
that historically failed to refresh).
"""
from __future__ import annotations

# High-signal phrases from runtime refresh rollout (Agent Dev picker, status bar, …)
STALE_ENGLISH_PHRASES: tuple[str, ...] = (
    "Describe what you want to build",
    "Select a model",
    "Agent running",
    "Loading modules...",
    "No models found",
    "Build NPU apps",
    "Natural-Language NPU App Builder",
    "Vision AI Streaming Pipeline",
    "ONNX → .dxnn Compiler GUI",
)


def find_stale_english_phrases(
    locale: str,
    visible_text_sample: tuple[str, ...] | list[str],
    *,
    issue_type: str = "observed",
) -> list[str]:
    """Return denylist hits for a browser observation."""
    if locale == "en" or issue_type != "observed":
        return []
    blob = "\n".join(visible_text_sample)
    return [phrase for phrase in STALE_ENGLISH_PHRASES if phrase in blob]

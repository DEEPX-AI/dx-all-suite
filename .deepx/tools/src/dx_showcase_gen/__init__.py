"""dx-showcase-gen — deterministic mechanics for building dx-agent-dev showcases.

Pairs with the RIGID skill ``dx-agent-showcase-build`` (which orchestrates the
non-deterministic / human-in-the-loop steps). This package owns the parts that are
deterministic and were the source of recurring mistakes:

- screen recording → timelapse GIF (real window, x11grab + post-crop, <10MB)
- COMPLETE transcript render (``--stream-json`` so Wall-clock + Cost are present)
- verification gate (transcript completeness, model/tool, GIFs, artifacts, docs)
- session→showcase artifact copy (+ portability scan)
- idempotent README/docs augmentation
"""

__all__ = ["constants", "recorder", "transcript", "verify", "artifacts", "augment"]
__version__ = "0.1.0"

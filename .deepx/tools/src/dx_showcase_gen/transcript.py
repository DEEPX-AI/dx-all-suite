"""COMPLETE transcript rendering.

The in-session sentinel renders from the session STORE, which has no synthetic
``result`` event — so Wall-clock (duration_ms) and Cost (total_cost_usd) are
missing and the tail "saved to …" narration is truncated. A COMPLETE transcript
requires the ``claude -p --output-format stream-json`` STDOUT (captured to a file)
rendered EXTERNALLY after the process exits. This module enforces that.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from . import constants as C


def metrics_from_stream(stream_json: str) -> Optional[dict]:
    """Pull model/cost/duration/turns/tokens from a stream-json stdout capture.

    Reuses the same extractor the transcript renderer uses, so the numbers match
    what lands in the rendered summary table.
    """
    from dx_transcripts.generate_transcripts import _session_metrics
    return _session_metrics(stream_json)


def is_complete(stream_json: str) -> bool:
    """True iff the stream carries a ``result`` event (⇒ Wall-clock + Cost)."""
    m = metrics_from_stream(stream_json)
    return bool(m and m.get("duration_ms") and m.get("total_cost_usd") is not None)


class IncompleteTranscript(RuntimeError):
    pass


def render(out_dir: str, *, stream_json: str, session_id: Optional[str] = None,
           project: Optional[str] = None, tool: str = C.DEFAULT_TOOL,
           prefix: str = C.TRANSCRIPT_PREFIX, require_complete: bool = True) -> Dict[str, str]:
    """Render md/html/jsonl into ``out_dir`` named ``<prefix>.{md,html,jsonl}``.

    The body comes from the session store (``--session-id``/``--project``); the
    metrics + raw .jsonl come from ``stream_json`` (which carries the result event).
    Raises ``IncompleteTranscript`` when ``require_complete`` and the stream lacks
    a result event.
    """
    if require_complete and not is_complete(stream_json):
        raise IncompleteTranscript(
            "stream-json has no `result` event → Wall-clock/Cost would be missing. "
            "Capture `claude -p --output-format stream-json` stdout and render AFTER "
            "the process exits (the in-session sentinel cannot do this)."
        )
    from dx_transcripts.generate_transcripts import generate
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    # generate() writes <gprefix>-session.md / -session.html / -stream.jsonl
    gprefix = "_scgen"
    written = generate(out_dir=str(out), prefix=gprefix, session_id=session_id,
                       project_path=project, tool=tool, stream_json=stream_json)
    # Normalise to claude-code-session.{md,html,jsonl}
    rename = {
        out / f"{gprefix}-session.md": out / f"{prefix}.md",
        out / f"{gprefix}-session.html": out / f"{prefix}.html",
        out / f"{gprefix}-stream.jsonl": out / f"{prefix}.jsonl",
    }
    result: Dict[str, str] = {}
    for src, dst in rename.items():
        if src.exists():
            src.replace(dst)
            kind = dst.suffix.lstrip(".")
            result[kind] = str(dst)
    # remove any leftover intermediates (e.g. the `<gprefix>-session.jsonl` alias)
    for leftover in out.glob(f"{gprefix}-*"):
        leftover.unlink()
    return result

"""Idempotent, marker-anchored augmentation of READMEs and docs.

Each inserted block is wrapped in ``<!-- dx-showcase:<name>:start/end -->`` markers
so re-running replaces (not duplicates) it. Used to drop the build-GIF block + the
metrics line into the suite README (EN/KO), the showcase README (EN/KO), and the
00_Agentic_Development docs.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


def marker(name: str, kind: str = "gif") -> str:
    return f"dx-showcase:{name}:{kind}"


def gif_block(gif_rel: str, caption: str, width: int = 760) -> str:
    return ('<div align="center">\n'
            f'<img src="{gif_rel}" width="{width}"><br>'
            f'<sub><b>{caption}</b></sub>\n'
            '</div>')


def upsert_block(path: str, *, anchor: str, block: str, mk: str) -> bool:
    """Insert ``block`` (wrapped in markers ``mk``) after the first line containing
    ``anchor`` — or replace the existing marked region. Returns True if changed."""
    p = Path(path)
    if not p.exists():
        return False
    text = p.read_text()
    start = f"<!-- {mk}:start -->"
    end = f"<!-- {mk}:end -->"
    wrapped = f"{start}\n{block}\n{end}"

    if start in text and end in text:
        new = re.sub(re.escape(start) + r".*?" + re.escape(end), wrapped, text,
                     count=1, flags=re.DOTALL)
        if new != text:
            p.write_text(new)
            return True
        return False

    # insert after the anchor line (keep the anchor)
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if anchor in line:
            insert_at = i + 1
            sep = "\n" + wrapped + "\n"
            lines.insert(insert_at, sep + ("" if lines[insert_at:i+1] else "\n"))
            p.write_text("".join(lines))
            return True
    # anchor not found → append
    p.write_text(text.rstrip() + "\n\n" + wrapped + "\n")
    return True


def has_marker(path: str, name: str, kind: str = "gif") -> bool:
    p = Path(path)
    if not p.exists():
        return False
    return f"<!-- {marker(name, kind)}:start -->" in p.read_text(errors="replace")


def augment_readme_gif(path: str, *, name: str, anchor: str, gif_rel: str,
                       caption: str, width: int = 760) -> bool:
    """Upsert a GIF block under ``anchor`` (e.g. the showcase heading line)."""
    return upsert_block(path, anchor=anchor, block=gif_block(gif_rel, caption, width),
                        mk=marker(name, "gif"))

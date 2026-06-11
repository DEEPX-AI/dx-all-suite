"""YAML frontmatter parsing and transformation utilities."""

from __future__ import annotations

import re
from typing import Any

import yaml


def strip_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse and remove YAML frontmatter from markdown content.
    
    Returns:
        (frontmatter_dict, body_without_frontmatter)
    """
    if not content.startswith("---"):
        return {}, content
    
    # Find closing ---
    end = content.find("\n---", 3)
    if end == -1:
        return {}, content
    
    fm_str = content[3:end].strip()
    body = content[end + 4:].lstrip("\n")
    
    try:
        fm = yaml.safe_load(fm_str) or {}
    except yaml.YAMLError:
        return {}, content
    
    return fm, body


def build_frontmatter(data: dict[str, Any], *, sort_keys: bool = False) -> str:
    """Serialize a dict to YAML frontmatter block (with --- delimiters)."""
    yaml_str = yaml.dump(
        data,
        default_flow_style=False,
        sort_keys=sort_keys,
        allow_unicode=True,
        width=120,
    )
    return f"---\n{yaml_str}---\n"


def first_paragraph(content: str, *, max_chars: int = 200) -> str:
    """Extract first meaningful paragraph from markdown, skipping metadata."""
    lines = content.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if result:
                break
            continue
        # Skip headings, frontmatter, code blocks, tables, bullets, quotes
        if stripped.startswith(("#", "---", "```", "|", "-", ">", "<!--")):
            if result:
                break
            continue
        result.append(stripped)
    
    text = " ".join(result)[:max_chars]
    return text.replace('"', '\\"')

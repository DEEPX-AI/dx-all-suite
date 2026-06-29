"""Content transformation utilities for platform-specific file generation."""

from __future__ import annotations

import re


def rewrite_deepx_to_github(body: str) -> str:
    """Rewrite .deepx/ paths to .github/ equivalents in content body.
    
    Must run specific rules before generic ones to avoid partial matches.
    """
    # Specific: .deepx/skills/dx-XXX/SKILL.md -> .github/skills/dx-XXX/SKILL.md
    body = re.sub(
        r"\.deepx/skills/([a-z0-9-]+)/SKILL\.md",
        r".github/skills/\1/SKILL.md",
        body,
    )
    # Specific: .deepx/skills/dx-XXX.md -> .github/skills/dx-XXX.md
    body = re.sub(
        r"\.deepx/skills/([a-z0-9-]+)\.md",
        r".github/skills/\1.md",
        body,
    )
    # Generic directory references
    body = body.replace(".deepx/agents/", ".github/agents/")
    body = body.replace(".deepx/skills/", ".github/skills/")
    body = body.replace(".deepx/instructions/", ".github/instructions/")
    body = body.replace(".deepx/toolsets/", ".github/toolsets/")
    body = body.replace(".deepx/memory/", ".github/memory/")
    body = body.replace(".deepx/knowledge/", ".github/knowledge/")
    # Prose references
    body = body.replace("relative to `.deepx/`", "relative to `.github/`")
    body = body.replace("in `.deepx/`", "in `.github/`")
    
    return body


def capabilities_to_tools(
    capabilities: list[str],
    tool_map: dict[str, list[str]],
) -> list[str]:
    """Expand abstract capabilities to platform-specific tool list."""
    tools: set[str] = set()
    for cap in capabilities:
        tools.update(tool_map.get(cap, []))
    return sorted(tools)


def routes_to_handoffs(routes: list[dict]) -> list[dict]:
    """Convert routes-to entries to Copilot handoffs format."""
    handoffs = []
    for route in routes:
        if isinstance(route, str):
            # Legacy simple string format
            handoffs.append({
                "label": route,
                "agent": route,
                "prompt": f"Hand off to {route}",
                "send": False,
            })
        else:
            handoffs.append({
                "label": route.get("label", route.get("target", "")),
                "agent": route["target"],
                "prompt": route.get("description", ""),
                "send": False,
            })
    return handoffs

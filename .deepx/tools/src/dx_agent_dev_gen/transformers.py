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
    # Specific: .deepx/agents/dx-XXX.md -> .github/agents/dx-XXX.agent.md
    # _generate_copilot always writes agent files as "<stem>.agent.md"
    # (unconditionally, same-repo or not), so any prose reference to an
    # agent's canonical .deepx/ path — same-repo or a cross-repo one like
    # "dx_app/.deepx/agents/dx-app-builder.md" (correct as written for
    # Claude/OpenCode/Cursor, which read .deepx/ directly and never rename
    # the file) — must gain the same suffix for copilot output, or it is
    # left pointing at a filename that only exists on the other 3 platforms.
    body = re.sub(
        r"\.deepx/agents/([\w-]+)\.md",
        r".github/agents/\1.agent.md",
        body,
    )
    # Generic directory references (any leftover bare-directory mention,
    # e.g. "the .deepx/agents/ directory", with no filename attached)
    body = body.replace(".deepx/agents/", ".github/agents/")
    body = body.replace(".deepx/skills/", ".github/skills/")
    # NOTE: .deepx/toolsets/, .deepx/instructions/, .deepx/memory/ and
    # .deepx/knowledge/ are intentionally NOT rewritten — none of them has a
    # real .github/ counterpart in any repo. .deepx/agents/ and .deepx/skills/
    # are the only two dirs the generator itself creates under .github/.
    # toolsets/memory/knowledge have no .github/ equivalent at all; dx_app and
    # dx_stream DO have a .github/instructions/ dir, but it holds a different,
    # hand-authored set of VS Code *.instructions.md files, not a mirror of
    # .deepx/instructions/ — so rewriting would silently point at the wrong
    # (and mostly nonexistent) files.
    #
    # NOTE (polish round F6): a blanket "in `.deepx/`" -> "in `.github/`" /
    # "relative to `.deepx/`" -> "relative to `.github/`" prose rewrite used
    # to run here too. Removed: every occurrence found in canonical agent/
    # skill bodies described the WHOLE framework or a script outside the
    # agents/skills mirror (e.g. "33 files in `.deepx/` including agents,
    # skills, instructions" or "validate_framework.py in `.deepx/`") — a
    # claim that becomes false once "in `.deepx/`" is swapped for
    # "in `.github/`", since copilot only mirrors agents/skills, never the
    # whole framework or its scripts. These sentences must stay `.deepx/`-
    # form for copilot output too, exactly like claude/opencode/cursor
    # (which never rewrite them at all). If a future sentence genuinely
    # needs the `.github/` form (e.g. "the skill lives in `.github/` for
    # Copilot"), write it out explicitly in the source rather than relying
    # on a blanket prose substitution that cannot tell agents/skills apart
    # from the rest of the framework.

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

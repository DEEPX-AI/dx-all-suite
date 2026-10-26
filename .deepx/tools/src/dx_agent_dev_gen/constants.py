"""Platform-specific tool mappings and shared constants."""

from __future__ import annotations

# Capability -> Copilot tool IDs (VS Code)
COPILOT_TOOLS: dict[str, list[str]] = {
    "read": [
        "edit/getDocumentText",
        "edit/getSelectedText",
        "read/readFile",
        "read/readDirectory",
    ],
    "edit": [
        "edit/createDirectory",
        "edit/createFile",
        "edit/editFiles",
        "edit/insertTextAtSelection",
    ],
    "search": [
        "edit/findTextInFiles",
        "git/searchCommits",
    ],
    "execute": [
        "execute/awaitTerminal",
        "execute/createAndRunTask",
        "execute/getTerminalOutput",
        "execute/runInTerminal",
    ],
    "sub-agent": [
        "agent/runSubagent",
    ],
    "ask-user": [
        "agent/askQuestions",
    ],
    "web": [
        "agent/webSearch",
    ],
    "todo": [],
}

# Capability -> Claude Code tool names
CLAUDE_TOOLS: dict[str, list[str]] = {
    "read": ["Read", "Grep", "Glob"],
    "edit": ["Write", "Edit"],
    "search": ["Grep", "Glob"],
    "execute": ["Bash"],
    "sub-agent": ["Agent"],
    "ask-user": ["AskUserQuestion"],
    "web": ["WebFetch"],
    "todo": ["TodoWrite"],
}

# Capability -> OpenCode tool config
OPENCODE_TOOLS: dict[str, dict] = {
    "read": {"mode": "subagent"},
    "edit": {"tools": {"edit": True, "write": True}},
    "search": {"mode": "subagent"},
    "execute": {"tools": {"bash": True}},
    "sub-agent": {"mode": "subagent"},
    "ask-user": {},
    "web": {},
    "todo": {},
}

# Generated file header template
GENERATED_HEADER = """\
<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: {source} -->
<!-- Run: dx-agent-gen generate -->
"""

# Header for generated SHELL assets. The HTML-comment header above is invalid in
# a shell script, and it must be inserted AFTER the shebang, never before it.
GENERATED_HEADER_SH = """\
# AUTO-GENERATED from dx-all-suite .deepx/ — DO NOT EDIT DIRECTLY
# Source: {source}
# Run: dx-agent-gen generate
"""

# Verbatim assets fanned out from the suite into each SUB-REPO (the suite keeps
# only the canonical copy — it is the harness and never bootstraps itself).
# Key: path relative to the suite root. Value: path relative to the target repo.
#
# harness_bootstrap.sh must live inside each sub-repo because a standalone clone
# has no suite above it from which to borrow the script — that is the whole
# chicken-and-egg problem it solves.
SUBREPO_ASSETS: dict[str, str] = {
    ".deepx/templates/assets/harness_bootstrap.sh": ".deepx/scripts/harness_bootstrap.sh",
}

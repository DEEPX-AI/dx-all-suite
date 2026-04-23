"""Platform-specific tool mappings and shared constants."""

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
<!-- Run: dx-agentic-gen generate -->
"""

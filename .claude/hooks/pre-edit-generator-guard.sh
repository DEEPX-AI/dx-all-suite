#!/usr/bin/env bash
# PreToolUse hook: block direct edits to dx-agent-gen generator output files.
#
# Generator output paths (Q2 from the Pre-flight Classification rule):
#   .github/agents/   .github/skills/
#   .opencode/agents/ .claude/agents/  .claude/skills/
#   .cursor/rules/
#   CLAUDE.md  CLAUDE-KO.md  AGENTS.md  AGENTS-KO.md
#   copilot-instructions.md  copilot-instructions-KO.md
#
# Contract (measured against Claude Code 2.110.0 / agent-sdk 0.3.271):
#   - the tool call arrives as JSON on STDIN, not in the environment:
#       {"hook_event_name":"PreToolUse","tool_name":"Edit",
#        "tool_input":{"file_path":"/abs/path",...}}
#   - CLAUDE_TOOL_INPUT_JSON / CLAUDE_FILE_PATHS do NOT exist (issue #186)
#   - exit 2 blocks the tool call and shows STDERR to Claude; stdout is dropped

# Run by hand from a terminal: nothing to judge, and never wait on a tty.
[ -t 0 ] && exit 0

INPUT="$(cat)"
[ -z "$INPUT" ] && exit 0

if command -v jq >/dev/null 2>&1; then
    FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)"
else
    FILE_PATH="$(printf '%s' "$INPUT" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
print((d.get("tool_input") or {}).get("file_path") or "")' 2>/dev/null)"
fi

[ -z "$FILE_PATH" ] && exit 0

# Is this path inside a dx-agent-dev tree? Walk up looking for .deepx/.
#
# INTENTIONAL: a Q2 path outside such a tree is allowed through. The names this
# hook guards are not unique to this repo — an unrelated project's .claude/agents/
# or the user's own ~/.claude/CLAUDE.md must stay editable — and without .deepx/
# there is no generator for the file to be an output of, so there is nothing to
# protect. A dx repo whose .deepx/ is missing is a broken checkout, not a case
# this hook papers over.
in_generated_tree() {
    local abs="$1" dir
    case "$abs" in /*) ;; *) abs="$PWD/$abs" ;; esac
    dir="$(dirname "$abs")"
    while [ -n "$dir" ] && [ "$dir" != "/" ]; do
        [ -d "$dir/.deepx" ] && return 0
        dir="$(dirname "$dir")"
    done
    return 1
}

block() {
    local source_kind="$1"
    {
        echo "BLOCKED: Direct edit to a generator-output file is forbidden."
        echo ""
        echo "  File : $FILE_PATH"
        echo "  Rule : This file is auto-generated from .deepx/ by dx-agent-gen."
        echo "  Fix  : Edit the canonical ${source_kind} in .deepx/ instead, then run:"
        echo "           dx-agent-gen generate"
        echo "         or: .deepx/tools/scripts/run_all.sh generate"
    } >&2
    exit 2
}

# Q2 path pattern check (allowed through outside a .deepx/ tree — see above)
if echo "$FILE_PATH" | grep -qE '(^|/)\.(github/(skills|agents)|opencode/agents|claude/(agents|skills)|cursor/rules)/'; then
    in_generated_tree "$FILE_PATH" && block "source"
fi

# Q2 filename check
BASENAME="$(basename "$FILE_PATH")"
case "$BASENAME" in
    CLAUDE.md|CLAUDE-KO.md|AGENTS.md|AGENTS-KO.md|copilot-instructions.md|copilot-instructions-KO.md)
        # Allowed through outside a .deepx/ tree — see in_generated_tree above
        in_generated_tree "$FILE_PATH" && block "template"
        ;;
esac

exit 0

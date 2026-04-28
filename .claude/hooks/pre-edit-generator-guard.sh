#!/usr/bin/env bash
# PreToolUse hook: block direct edits to dx-agentic-gen generator output files.
#
# Generator output paths (Q2 from the Pre-flight Classification rule):
#   .github/agents/   .github/skills/
#   .opencode/agents/ .claude/agents/  .claude/skills/
#   .cursor/rules/
#   CLAUDE.md  CLAUDE-KO.md  AGENTS.md  AGENTS-KO.md
#   copilot-instructions.md  copilot-instructions-KO.md
#
# Exit 2 → Claude Code blocks the tool call and shows stdout to Claude.

FILE_PATH="$(echo "${CLAUDE_TOOL_INPUT_JSON:-{}}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)"

[ -z "$FILE_PATH" ] && exit 0

# Q2 path pattern check
if echo "$FILE_PATH" | grep -qE '/\.(github/(skills|agents)|opencode/agents|claude/(agents|skills)|cursor/rules)/'; then
    echo "BLOCKED: Direct edit to a generator-output file is forbidden."
    echo ""
    echo "  File : $FILE_PATH"
    echo "  Rule : This file is auto-generated from .deepx/ by dx-agentic-gen."
    echo "  Fix  : Edit the canonical source in .deepx/ instead, then run:"
    echo "           dx-agentic-gen generate"
    echo "         or: tools/dx-agentic-dev-gen/scripts/run_all.sh generate"
    exit 2
fi

# Q2 filename check
BASENAME="$(basename "$FILE_PATH")"
case "$BASENAME" in
    CLAUDE.md|CLAUDE-KO.md|AGENTS.md|AGENTS-KO.md|copilot-instructions.md|copilot-instructions-KO.md)
        echo "BLOCKED: Direct edit to a generator-output file is forbidden."
        echo ""
        echo "  File : $FILE_PATH"
        echo "  Rule : This file is auto-generated from .deepx/ by dx-agentic-gen."
        echo "  Fix  : Edit the canonical template in .deepx/ instead, then run:"
        echo "           dx-agentic-gen generate"
        echo "         or: tools/dx-agentic-dev-gen/scripts/run_all.sh generate"
        exit 2
        ;;
esac

exit 0

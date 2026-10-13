#!/usr/bin/env bash
# PostToolUse hook: report dx-agent-gen drift after a .md/.mdc edit.
#
# Policy: WARN ONLY. The hook never runs `dx-agent-gen generate` itself —
# a single edit must not rewrite platform files behind the agent's back.
# It reports the drift and the command to run.
#
# Contract (measured against Claude Code 2.110.0 / agent-sdk 0.3.271):
#   - the tool call arrives as JSON on STDIN, not in the environment:
#       {"hook_event_name":"PostToolUse","tool_name":"Edit",
#        "tool_input":{"file_path":"/abs/path",...},"tool_response":{...}}
#   - CLAUDE_FILE_PATHS does NOT exist (issue #186)
#   - the hook's cwd is not necessarily the project dir, so paths are resolved
#     from the edited file, not from $PWD
#   - exit 2 surfaces STDERR to Claude; stdout is dropped

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

# Only .md / .mdc edits can cause generator drift
case "$FILE_PATH" in
    *.md|*.mdc) ;;
    *) exit 0 ;;
esac

# Resolve the repo from the edited file (cwd may be an unrelated checkout)
case "$FILE_PATH" in /*) ABS="$FILE_PATH" ;; *) ABS="$PWD/$FILE_PATH" ;; esac
REPO_ROOT="$(git -C "$(dirname "$ABS")" rev-parse --show-toplevel 2>/dev/null)"
[ -z "$REPO_ROOT" ] && REPO_ROOT="${CLAUDE_PROJECT_DIR:-}"
[ -z "$REPO_ROOT" ] && exit 0
[ -d "$REPO_ROOT" ] || exit 0

# Collect all repos with .deepx/ (suite root + nested dx_app / dx_stream).
# This runs BEFORE the binary lookup: REPO_ROOT may have come from the
# CLAUDE_PROJECT_DIR fallback and need not be a repo root at all, in which case
# there is nothing to check and nothing worth telling the agent about.
check_repos=()
[ -d "$REPO_ROOT/.deepx" ] && check_repos+=("$REPO_ROOT")
for sub in dx-runtime/dx_app dx-runtime/dx_stream dx_app dx_stream; do
    candidate="$REPO_ROOT/$sub"
    [ -d "$candidate/.deepx" ] && check_repos+=("$candidate")
done

[ "${#check_repos[@]}" -eq 0 ] && exit 0

# Need dx-agent-gen on PATH
if ! command -v dx-agent-gen >/dev/null 2>&1; then
    echo "[dx-agent-gen] WARNING: binary not found — drift check skipped." >&2
    echo "  Install: pip install -e ${REPO_ROOT}/.deepx/tools" >&2
    exit 0
fi

drifted=()
for repo in "${check_repos[@]}"; do
    if ! dx-agent-gen check --repo "$repo" >/dev/null 2>&1; then
        rel="${repo#"$REPO_ROOT"/}"
        [ "$rel" = "$repo" ] && rel="."
        drifted+=("$rel|$repo")
    fi
done

[ "${#drifted[@]}" -eq 0 ] && exit 0

{
    echo "[dx-agent-gen] Drift detected — platform files no longer match .deepx/:"
    for entry in "${drifted[@]}"; do
        echo "  - ${entry%%|*}:  dx-agent-gen generate --repo ${entry#*|}"
    done
    echo ""
    echo "  Nothing was regenerated. Edit canonical .deepx/ sources only;"
    echo "  generator outputs (.github/, .opencode/, .claude/agents/, .claude/skills/,"
    echo "  .cursor/rules/, CLAUDE.md, AGENTS.md, copilot-instructions.md) are"
    echo "  overwritten by generate — edits to them will be lost."
} >&2
exit 2

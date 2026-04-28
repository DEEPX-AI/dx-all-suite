#!/usr/bin/env bash
# PostToolUse hook: run dx-agentic-gen check after any .md/.mdc edit.
#
# If drift is detected (canonical .deepx/ diverged from platform files),
# auto-regenerates and reports. This replicates the git pre-commit hook so
# drift is caught immediately after every edit, not only at commit time.

FILES="${CLAUDE_FILE_PATHS:-}"
[ -z "$FILES" ] && exit 0

# Only process .md or .mdc edits
has_doc=0
for f in $FILES; do
    case "$f" in *.md|*.mdc) has_doc=1; break ;; esac
done
[ "$has_doc" -eq 0 ] && exit 0

# Must be inside a git repo
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0

# Need dx-agentic-gen on PATH
if ! command -v dx-agentic-gen &>/dev/null; then
    echo "[dx-agentic-gen] WARNING: binary not found — drift check skipped."
    echo "  Install: pip install -e ${REPO_ROOT}/tools/dx-agentic-dev-gen"
    exit 0
fi

# Collect all repos with .deepx/ (suite root + nested dx_app / dx_stream)
check_repos=()
[ -d "$REPO_ROOT/.deepx" ] && check_repos+=("$REPO_ROOT")
for sub in dx-runtime/dx_app dx-runtime/dx_stream dx_app dx_stream; do
    candidate="$REPO_ROOT/$sub"
    [ -d "$candidate/.deepx" ] && check_repos+=("$candidate")
done

[ "${#check_repos[@]}" -eq 0 ] && exit 0

# Check each repo; auto-generate if drift found
any_action=0
for repo in "${check_repos[@]}"; do
    rel="$(python3 -c "import os; print(os.path.relpath('$repo', '$REPO_ROOT'))" 2>/dev/null \
          || echo "$repo")"
    if ! dx-agentic-gen check --repo "$repo" >/dev/null 2>&1; then
        any_action=1
        echo "[dx-agentic-gen] Drift detected in '${rel}' — regenerating..."
        if dx-agentic-gen generate --repo "$repo" >/dev/null 2>&1; then
            echo "[dx-agentic-gen] ✓ '${rel}': platform files updated"
        else
            echo "[dx-agentic-gen] ✗ '${rel}': generate failed — run manually:"
            echo "  dx-agentic-gen generate --repo ${repo}"
        fi
    fi
done

[ "$any_action" -eq 0 ] && exit 0

echo ""
echo "[dx-agentic-gen] Reminder: only edit canonical .deepx/ sources directly."
echo "  Generator outputs (.github/, .opencode/, .claude/agents/, .claude/skills/,"
echo "  .cursor/rules/, CLAUDE.md, AGENTS.md, copilot-instructions.md) are"
echo "  overwritten by generate — edits to them will be lost."
exit 0

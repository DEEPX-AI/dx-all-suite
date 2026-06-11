#!/usr/bin/env bash
# Install dx-agent-gen pre-commit hooks for the suite and its submodules.
#
# Usage (from suite root):
#   .deepx/tools/scripts/install-hooks.sh
#
# This installs the drift-check hook into:
#   .git/hooks/pre-commit                                    (suite root)
#   .git/modules/dx-compiler/hooks/pre-commit
#   .git/modules/dx-runtime/hooks/pre-commit
#   .git/modules/dx-runtime/modules/dx_app/hooks/pre-commit  (nested)
#   .git/modules/dx-runtime/modules/dx_stream/hooks/pre-commit (nested)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SUITE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
HOOK_SRC="$SCRIPT_DIR/pre-commit-hook.sh"

if [ ! -f "$HOOK_SRC" ]; then
    echo "ERROR: Hook script not found: $HOOK_SRC"
    exit 1
fi

install_hook() {
    local hooks_dir="$1"
    local label="$2"
    local target="$hooks_dir/pre-commit"

    mkdir -p "$hooks_dir"

    if [ -f "$target" ]; then
        # Check if it's already our hook
        if grep -q "dx-agent-gen" "$target" 2>/dev/null; then
            echo "  $label: already installed (updating)"
        else
            echo "  $label: existing pre-commit hook found, creating pre-commit.dx-agent-gen instead"
            target="$hooks_dir/pre-commit.dx-agent-gen"
            echo "  NOTE: Manually add 'source $target' to your pre-commit hook"
        fi
    else
        echo "  $label: installing"
    fi

    cp "$HOOK_SRC" "$target"
    chmod +x "$target"
}

echo "Installing dx-agent-gen pre-commit hooks..."
echo ""

# Resolve each repo's hooks dir via git itself so this works for plain clones,
# git worktrees (.git is a file), AND submodules/nested submodules — instead of
# hardcoding "$ROOT/.git/hooks" / "$ROOT/.git/modules/...", which breaks on
# worktrees (where .git is a file, not a directory).
#   suite root + the four .deepx-bearing repos.
REPO_PATHS=(
    "$SUITE_ROOT"
    "$SUITE_ROOT/dx-compiler"
    "$SUITE_ROOT/dx-runtime"
    "$SUITE_ROOT/dx-runtime/dx_app"
    "$SUITE_ROOT/dx-runtime/dx_stream"
)

for repo in "${REPO_PATHS[@]}"; do
    label="${repo#$SUITE_ROOT}"; label="${label#/}"; label="${label:-suite root}"
    if [ ! -e "$repo/.git" ]; then
        echo "  $label: not checked out, skipping"; continue
    fi
    if ! git -C "$repo" rev-parse --git-dir >/dev/null 2>&1; then
        echo "  $label: not a git repo, skipping"; continue
    fi
    # worktree-aware hooks dir (absolute)
    hooks_dir="$(git -C "$repo" rev-parse --git-path hooks)"
    case "$hooks_dir" in /*) ;; *) hooks_dir="$repo/$hooks_dir" ;; esac
    install_hook "$hooks_dir" "$label"
done

echo ""
echo "Done. Hooks will run dx-agent-gen check before each commit."
echo "Skip with: git commit --no-verify"

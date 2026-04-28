#!/usr/bin/env bash
# Install dx-agentic-gen pre-commit hooks for the suite and its submodules.
#
# Usage (from suite root):
#   tools/dx-agentic-dev-gen/scripts/install-hooks.sh
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
        if grep -q "dx-agentic-gen" "$target" 2>/dev/null; then
            echo "  $label: already installed (updating)"
        else
            echo "  $label: existing pre-commit hook found, creating pre-commit.dx-agentic-gen instead"
            target="$hooks_dir/pre-commit.dx-agentic-gen"
            echo "  NOTE: Manually add 'source $target' to your pre-commit hook"
        fi
    else
        echo "  $label: installing"
    fi

    cp "$HOOK_SRC" "$target"
    chmod +x "$target"
}

echo "Installing dx-agentic-gen pre-commit hooks..."
echo ""

# Suite root
install_hook "$SUITE_ROOT/.git/hooks" "suite root"

# Top-level submodules
for module in dx-compiler dx-runtime; do
    module_hooks="$SUITE_ROOT/.git/modules/$module/hooks"
    if [ -d "$(dirname "$module_hooks")" ]; then
        install_hook "$module_hooks" "$module"
    else
        echo "  $module: submodule not found, skipping"
    fi
done

# Nested submodules under dx-runtime (dx_app, dx_stream)
for nested in dx_app dx_stream; do
    nested_hooks="$SUITE_ROOT/.git/modules/dx-runtime/modules/$nested/hooks"
    if [ -d "$(dirname "$nested_hooks")" ]; then
        install_hook "$nested_hooks" "dx-runtime/$nested"
    else
        echo "  dx-runtime/$nested: nested submodule not found, skipping"
    fi
done

echo ""
echo "Done. Hooks will run dx-agentic-gen check before each commit."
echo "Skip with: git commit --no-verify"

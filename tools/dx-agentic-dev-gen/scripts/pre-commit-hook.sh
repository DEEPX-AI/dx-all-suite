#!/usr/bin/env bash
# Pre-commit hook: verify dx-agentic-gen generated files are up-to-date.
#
# Checks .deepx/ → platform files drift for the repo being committed.
# If drift is detected, the commit is blocked with instructions to fix.
#
# Install (from suite root):
#   tools/dx-agentic-dev-gen/scripts/install-hooks.sh

set -euo pipefail

# Resolve the repo root being committed
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Check if dx-agentic-gen is available
if ! command -v dx-agentic-gen &>/dev/null; then
    echo "WARNING: dx-agentic-gen not found in PATH. Skipping drift check."
    echo "  Install: pip install -e tools/dx-agentic-dev-gen"
    exit 0
fi

# Determine which repos to check based on the git root
check_repos=()

# Always check the repo being committed
if [ -d "$REPO_ROOT/.deepx" ]; then
    check_repos+=("$REPO_ROOT")
fi

# If this is the suite root or dx-runtime, also check nested repos
# (dx_app and dx_stream are directories within dx-runtime, not separate git repos)
for sub in dx-runtime/dx_app dx-runtime/dx_stream dx_app dx_stream; do
    candidate="$REPO_ROOT/$sub"
    if [ -d "$candidate/.deepx" ]; then
        check_repos+=("$candidate")
    fi
done

if [ ${#check_repos[@]} -eq 0 ]; then
    exit 0
fi

failed=0
for repo in "${check_repos[@]}"; do
    rel=$(python3 -c "import os; print(os.path.relpath('$repo', '$REPO_ROOT'))")
    if ! dx-agentic-gen check --repo "$repo" >/dev/null 2>&1; then
        echo "ERROR: Generated files out-of-date in $rel"
        dx-agentic-gen check --repo "$repo" 2>&1 | grep -E '^(CHANGED|MISSING):' || true
        failed=1
    fi
done

if [ $failed -ne 0 ]; then
    echo ""
    echo "Fix: dx-agentic-gen generate --repo <repo>"
    echo "  or: tools/dx-agentic-dev-gen/scripts/run_all.sh"
    echo ""
    echo "To skip this check: git commit --no-verify"
    exit 1
fi

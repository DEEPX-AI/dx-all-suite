#!/usr/bin/env bash
# Pre-commit hook: verify dx-agentic-gen generated files are up-to-date.
#
# Checks .deepx/ → platform files drift for the repo being committed.
# If drift is detected, the commit is blocked with instructions to fix.
#
# Also warns when .deepx/ files are staged alongside non-.deepx/ files,
# to prevent unintended pre-existing changes from being mixed into the commit.
#
# Install (from suite root):
#   tools/dx-agentic-dev-gen/scripts/install-hooks.sh

set -euo pipefail

# Resolve the repo root being committed
REPO_ROOT="$(git rev-parse --show-toplevel)"

# ---------------------------------------------------------------------------
# Staged file scope check: warn if .deepx/ and non-.deepx/ files are mixed
# ---------------------------------------------------------------------------

staged_files=$(git diff --cached --name-only 2>/dev/null || true)

if [ -n "$staged_files" ]; then
    deepx_staged=$(echo "$staged_files" | grep -E '(^|/)\.deepx/' || true)
    non_deepx_staged=$(echo "$staged_files" | grep -vE '(^|/)\.deepx/' || true)

    if [ -n "$deepx_staged" ] && [ -n "$non_deepx_staged" ]; then
        echo ""
        echo "WARNING: .deepx/ files staged alongside non-.deepx/ files."
        echo "  This may indicate an accidental 'git add -A' including unrelated changes."
        echo ""
        echo "  Files outside .deepx/ that are staged:"
        echo "$non_deepx_staged" | head -20 | sed 's/^/    - /'
        n_non_deepx=$(echo "$non_deepx_staged" | wc -l)
        if [ "$n_non_deepx" -gt 20 ]; then
            echo "    ... and $((n_non_deepx - 20)) more"
        fi
        echo ""
        echo "  If this is intentional, proceed with: git commit --no-verify"
        echo "  To commit only .deepx/ and generated outputs, use selective git add:"
        echo "    git restore --staged ."
        echo "    git add .deepx/ CLAUDE.md AGENTS.md CLAUDE-KO.md AGENTS-KO.md \\"
        echo "            .github/ .claude/ .cursor/ .opencode/"
        echo ""
    fi
fi

# ---------------------------------------------------------------------------
# Drift check: ensure .deepx/ changes are propagated to generated outputs
# ---------------------------------------------------------------------------

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
    echo "  or: tools/dx-agentic-dev-gen/scripts/run_all.sh generate"
    echo ""
    echo "To skip this check: git commit --no-verify"
    exit 1
fi

# ---------------------------------------------------------------------------
# Lint check: verify EN/KO fragment parity when .deepx/ files are staged
# ---------------------------------------------------------------------------

if [ -n "${deepx_staged:-}" ]; then
    lint_failed=0
    for repo in "${check_repos[@]}"; do
        rel=$(python3 -c "import os; print(os.path.relpath('$repo', '$REPO_ROOT'))")
        if ! dx-agentic-gen lint --repo "$repo" >/dev/null 2>&1; then
            echo "ERROR: EN/KO fragment parity issues in $rel"
            dx-agentic-gen lint --repo "$repo" 2>&1 | grep '\[ERROR\]' || true
            lint_failed=1
        fi
    done

    if [ $lint_failed -ne 0 ]; then
        echo ""
        echo "Fix: update the KO fragment in .deepx/templates/fragments/ko/"
        echo "  then: dx-agentic-gen generate"
        echo ""
        echo "To skip this check: git commit --no-verify"
        exit 1
    fi
fi

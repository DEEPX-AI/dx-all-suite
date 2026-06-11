#!/usr/bin/env bash
# Pre-commit hook: verify dx-agent-gen generated files are up-to-date.
#
# Checks .deepx/ → platform files drift for the repo being committed.
# If drift is detected, the commit is blocked with instructions to fix.
#
# Also warns when .deepx/ files are staged alongside non-.deepx/ files,
# to prevent unintended pre-existing changes from being mixed into the commit.
#
# Install (from suite root):
#   .deepx/tools/scripts/install-hooks.sh

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

# Resolve a working dx-agent-gen invocation. FAIL CLOSED if none works —
# a drift-integrity gate that silently no-ops when the tool is missing is a hole
# (this is exactly how stale generated files got committed before).
find_suite_root() {
    local d="$1"
    while [ "$d" != / ]; do
        if [ -f "$d/.deepx/tools/src/dx_agent_dev_gen/cli.py" ]; then echo "$d"; return 0; fi
        d="$(dirname "$d")"
    done
    return 1
}

GEN_BIN=""
GEN_PYPATH=""
_suite="$(find_suite_root "$REPO_ROOT" || true)"
if [ -n "$_suite" ] && \
   PYTHONPATH="$_suite/.deepx/tools/src" python3 -c "import dx_agent_dev_gen.cli" 2>/dev/null; then
    # Prefer the in-tree source: it is version-matched to this checkout and avoids
    # a stale/broken globally-installed shim (command -v can pass while the binary
    # fails at runtime with ModuleNotFoundError).
    GEN_PYPATH="$_suite/.deepx/tools/src"
elif command -v dx-agent-gen &>/dev/null && dx-agent-gen --help >/dev/null 2>&1; then
    GEN_BIN="dx-agent-gen"
else
    echo "ERROR: dx-agent-gen is not runnable (no importable .deepx/tools/src and no"
    echo "       working dx-agent-gen on PATH). The drift check cannot run."
    echo "       Refusing to commit (fail-closed) to avoid committing stale generated files."
    echo "  Fix: commit from a checkout that has .deepx/tools/src, or pip install -e <suite>/.deepx/tools"
    echo "  To skip this check (NOT recommended): git commit --no-verify"
    exit 1
fi

# gen <subcommand> [args...] — dispatch to the resolved invocation
gen() {
    if [ -n "$GEN_BIN" ]; then
        "$GEN_BIN" "$@"
    else
        PYTHONPATH="$GEN_PYPATH" python3 -c "import sys; from dx_agent_dev_gen.cli import main; sys.exit(main(sys.argv[1:]))" "$@"
    fi
}

# Determine which repos to check based on the git root
check_repos=()

# Always check the repo being committed
if [ -d "$REPO_ROOT/.deepx" ]; then
    check_repos+=("$REPO_ROOT")
fi

# Cross-level propagation guard: a shared .deepx/ fragment edit must regenerate
# EVERY level it feeds, not just the repo being committed. When committing from a
# parent that contains sub-levels, check ALL of them — otherwise a fragment that
# drifts (e.g.) dx-compiler's or dx-runtime's generated files slips through a
# suite-root commit. This is exactly the gap that let stale generated files get
# committed before (dx-compiler and dx-runtime were previously NOT checked from
# a suite-root commit).
#   suite root → dx-compiler, dx-runtime, dx-runtime/dx_app, dx-runtime/dx_stream
#   dx-runtime → dx_app, dx_stream
for sub in dx-compiler dx-runtime dx-runtime/dx_app dx-runtime/dx_stream dx_app dx_stream; do
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
    if ! gen check --repo "$repo" >/dev/null 2>&1; then
        echo "ERROR: Generated files out-of-date in $rel"
        gen check --repo "$repo" 2>&1 | grep -E '^(CHANGED|MISSING):' || true
        failed=1
    fi
done

if [ $failed -ne 0 ]; then
    echo ""
    echo "Fix (regenerate EVERY level — a shared .deepx/ fragment edit drifts all of them):"
    echo "  .deepx/tools/scripts/run_all.sh generate"
    echo ""
    echo "  Per-repo 'dx-agent-gen generate --repo <repo>' fixes only ONE level and is"
    echo "  how stale files slip in — use it only if you are certain a single level is affected."
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
        if ! gen lint --repo "$repo" >/dev/null 2>&1; then
            echo "ERROR: EN/KO fragment parity issues in $rel"
            gen lint --repo "$repo" 2>&1 | grep '\[ERROR\]' || true
            lint_failed=1
        fi
    done

    if [ $lint_failed -ne 0 ]; then
        echo ""
        echo "Fix: update the KO fragment in .deepx/templates/fragments/ko/"
        echo "  then: dx-agent-gen generate"
        echo ""
        echo "To skip this check: git commit --no-verify"
        exit 1
    fi
fi

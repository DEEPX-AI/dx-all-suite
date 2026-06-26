#!/bin/bash
# run_all.sh — Run dx-agent-gen across all 5 repos in dx-all-suite
# Usage: bash .deepx/tools/scripts/run_all.sh generate
#        bash .deepx/tools/scripts/run_all.sh check
#        bash .deepx/tools/scripts/run_all.sh lint
#        bash .deepx/tools/scripts/run_all.sh prune
set -e

SUITE_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

REPOS=(
  "."
  "dx-compiler"
  "dx-runtime"
  "dx-runtime/dx_app"
  "dx-runtime/dx_stream"
)

# Resolve a working dx-agent-gen invocation: prefer the installed CLI, else
# fall back to running the module from the in-tree source (.deepx/tools/src).
# Without this, `python -c "import dx_agent_dev_gen"` fails when the package
# is not pip-installed AND PYTHONPATH is unset (a recurring breakage).
gen() {  # gen <subcommand> --repo <path>
  # Prefer in-tree source (version-matched; avoids a stale/broken installed shim
  # whose `command -v` passes but which fails at runtime with ModuleNotFoundError).
  if PYTHONPATH="$SUITE_ROOT/.deepx/tools/src${PYTHONPATH:+:$PYTHONPATH}" \
       python3 -c "import dx_agent_dev_gen.cli" 2>/dev/null; then
    PYTHONPATH="$SUITE_ROOT/.deepx/tools/src${PYTHONPATH:+:$PYTHONPATH}" \
      python3 -c "import sys; from dx_agent_dev_gen.cli import main; sys.exit(main(sys.argv[1:]))" "$@"
  elif command -v dx-agent-gen &>/dev/null && dx-agent-gen --help >/dev/null 2>&1; then
    dx-agent-gen "$@"
  else
    echo "ERROR: dx-agent-gen is not runnable (no importable .deepx/tools/src and no working CLI)." >&2
    return 2
  fi
}

EXIT_CODE=0
for repo in "${REPOS[@]}"; do
  echo "=== $repo ==="
  if ! gen "$1" --repo "$SUITE_ROOT/$repo" 2>&1; then
    EXIT_CODE=1
  fi
done

exit $EXIT_CODE

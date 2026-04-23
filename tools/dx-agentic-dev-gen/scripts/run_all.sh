#!/bin/bash
# run_all.sh — Run dx-agentic-gen across all 5 repos in dx-all-suite
# Usage: bash tools/dx-agentic-dev-gen/scripts/run_all.sh generate
#        bash tools/dx-agentic-dev-gen/scripts/run_all.sh check
set -e

SUITE_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

REPOS=(
  "."
  "dx-compiler"
  "dx-runtime"
  "dx-runtime/dx_app"
  "dx-runtime/dx_stream"
)

EXIT_CODE=0
for repo in "${REPOS[@]}"; do
  echo "=== $repo ==="
  if ! python -c "
from dx_agentic_dev_gen.cli import main
import sys
sys.exit(main(['$1', '--repo', '$SUITE_ROOT/$repo']))
" 2>&1; then
    EXIT_CODE=1
  fi
done

exit $EXIT_CODE

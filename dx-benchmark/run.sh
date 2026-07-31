#!/usr/bin/env bash
# dx-benchmark launcher — runs the benchmark CLI.
# Usage: ./run.sh <preflight|dry-run|run|report|aggregate|dashboard> [args...]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Activate a local venv if one exists (optional — the benchmark needs no pip deps).
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/venv/bin/activate"
fi

cd "$SCRIPT_DIR"
exec python3 -m benchmark "$@"

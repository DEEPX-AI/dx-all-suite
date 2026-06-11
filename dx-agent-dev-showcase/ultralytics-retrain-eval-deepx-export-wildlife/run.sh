#!/usr/bin/env bash
# run.sh — one-command launcher for the YOLO26n african-wildlife retrain + DeepX benchmark.
# Activates dx-runtime/venv-dx-runtime and runs pipeline.py, teeing output to session.log.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Auto-detect suite root (walks up until dx-runtime/ and dx-compiler/ siblings are found)
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: Cannot find dx-all-suite root (expected dx-runtime/ and dx-compiler/ siblings)"
    exit 1
fi

VENV="$SUITE_ROOT/dx-runtime/venv-dx-runtime"
if [ ! -x "$VENV/bin/python" ]; then
    echo "ERROR: venv not found at $VENV. Run setup.sh first."
    exit 1
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

cd "$SCRIPT_DIR"
echo "==== Running YOLO26n retrain + DeepX benchmark pipeline ===="
python pipeline.py 2>&1 | tee session.log
echo "==== Pipeline finished. See report.md / results.json / sample_detect.jpg ===="

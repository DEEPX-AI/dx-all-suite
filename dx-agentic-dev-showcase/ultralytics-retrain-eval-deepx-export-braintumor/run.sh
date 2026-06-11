#!/usr/bin/env bash
# Re-run the full brain-tumor retrain + 4-way DeepX evaluation pipeline.
# Output (metrics.json, *_deepx_model/, sample_detect.jpg, report inputs) lands
# in this session directory; stdout is mirrored to session.log.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Auto-detect suite root and reuse the runtime venv (full ultralytics+dx_com+dx_engine stack)
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then break; fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: cannot find dx-all-suite root"; exit 1
fi

VENV="$SUITE_ROOT/dx-runtime/venv-dx-runtime"
[ -d "$SCRIPT_DIR/venv" ] && VENV="$SCRIPT_DIR/venv"   # prefer local fallback venv if setup.sh built one
if [ ! -d "$VENV" ]; then
    echo "ERROR: no venv found. Run ./setup.sh first."; exit 1
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

cd "$SCRIPT_DIR"
echo "=== pipeline launch $(date +%F_%H:%M:%S) ===" | tee session.log
python -u pipeline.py 2>&1 | tee -a session.log

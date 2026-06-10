#!/usr/bin/env bash
# run.sh — one-command relauncher for the 4-way evaluation. Assumes train.py +
# export_deepx.py have already produced runs/train/weights/best.pt and the two
# *_deepx_model/ dirs. Re-runs evaluate.py (+ verify.py) against the existing models.
#
# To rebuild from scratch instead:  python train.py && python export_deepx.py all
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Auto-detect suite root (cross-project reference to dx-runtime venv) ---
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
VPY="$VENV/bin/python"

if [ ! -x "$VPY" ]; then
    echo "ERROR: venv-dx-runtime not found at $VENV — run setup.sh first."
    exit 1
fi
# Activate the venv if not already active (provides dx_engine for NPU eval).
if [ "${VIRTUAL_ENV:-}" != "$VENV" ]; then
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
fi

cd "$SCRIPT_DIR"
echo "=== Verifying exported DeepX models on the NPU ==="
python verify.py
echo "=== Running 4-way evaluation (base/retrained x fp32-GPU/INT8-NPU) ==="
python evaluate.py
echo "=== Done. See results.json and report.md ==="

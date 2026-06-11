#!/usr/bin/env bash
# run.sh — one-command launcher: (optional) train -> export+eval -> report -> verify.
# Re-runs the pipeline against the suite's venv-dx-runtime. Training is skipped if
# best.pt already exists (pass --retrain to force).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: Cannot find dx-all-suite root (dx-runtime/ + dx-compiler/ siblings)"
    exit 1
fi
VENV="$SUITE_ROOT/dx-runtime/venv-dx-runtime"
PY="$VENV/bin/python"
if [ ! -x "$PY" ]; then
    echo "ERROR: venv-dx-runtime missing. Run setup.sh / build dx_rt first."
    exit 1
fi

cd "$SCRIPT_DIR"
FORCE_RETRAIN=0
[ "${1:-}" = "--retrain" ] && FORCE_RETRAIN=1

if [ "$FORCE_RETRAIN" = "1" ] || [ ! -f train_result.json ]; then
    echo "=== Training (40 epochs) ==="
    "$PY" -u train.py 2>&1 | tee train.log
else
    echo "=== Skipping training (train_result.json exists; use --retrain to force) ==="
fi

echo "=== Export + 4-way eval + sample ==="
"$PY" -u export_eval.py 2>&1 | tee export_eval.log

echo "=== Report ==="
"$PY" -u make_report.py 2>&1 | tee -a export_eval.log

echo "=== Verify ==="
"$PY" -u verify.py
echo "Exit: $?"

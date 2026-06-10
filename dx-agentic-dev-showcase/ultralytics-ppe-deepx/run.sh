#!/usr/bin/env bash
# One-command driver for the YOLO26n construction-PPE retrain -> DeepX 4-way benchmark.
#
#   ./run.sh            # eval-only: export (if needed) + benchmark 4 forms + report  (default)
#   ./run.sh --full     # full pipeline: retrain (40 epochs) + export + benchmark + report
#
# Reuses dx-runtime/venv-dx-runtime via SUITE_ROOT autodetect.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then break; fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: cannot find dx-all-suite root"; exit 1
fi
PY="$SUITE_ROOT/dx-runtime/venv-dx-runtime/bin/python"
if [ ! -x "$PY" ]; then echo "ERROR: venv missing — run ./setup.sh first"; exit 1; fi

FULL=0
[ "${1:-}" = "--full" ] && FULL=1

BEST="$SCRIPT_DIR/runs/retrained/weights/best.pt"

cd "$SCRIPT_DIR"

if [ "$FULL" = "1" ]; then
    echo "=== [1/4] retrain yolo26n on construction-ppe (40 epochs) ==="
    "$PY" train_ppe.py
fi
[ -f "$BEST" ] || { echo "ERROR: retrained weights not found ($BEST). Run ./run.sh --full"; exit 1; }

echo "=== [2/4] export base + retrained to DeepX (INT8) ==="
[ -d "$SCRIPT_DIR/yolo26n_deepx_model" ]     || "$PY" export_deepx.py --model yolo26n.pt --out-name yolo26n_deepx_model
[ -d "$SCRIPT_DIR/yolo26n_ppe_deepx_model" ] || "$PY" export_deepx.py --model "$BEST"    --out-name yolo26n_ppe_deepx_model

echo "=== [3/4] benchmark 4 forms ==="
"$PY" benchmark.py --model yolo26n.pt              --tag base_fp32_gpu      --device gpu
"$PY" benchmark.py --model yolo26n_deepx_model     --tag base_int8_npu      --device npu
"$PY" benchmark.py --model "$BEST"                 --tag retrained_fp32_gpu --device gpu
"$PY" benchmark.py --model yolo26n_ppe_deepx_model --tag retrained_int8_npu --device npu

echo "=== [4/4] build report + verify ==="
"$PY" make_report.py
"$PY" verify.py

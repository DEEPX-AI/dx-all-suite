#!/usr/bin/env bash
# Wait for the background training PID to finish, then export both models to DeepX,
# benchmark the 4 forms, build report.md, and verify. All real output -> session.log.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
cd "$SCRIPT_DIR"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
SUITE_ROOT="$SCRIPT_DIR"; while [ "$SUITE_ROOT" != / ]; do [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ] && break; SUITE_ROOT="$(dirname "$SUITE_ROOT")"; done
PY="$SUITE_ROOT/dx-runtime/venv-dx-runtime/bin/python"
LOG="$SCRIPT_DIR/session.log"
BEST="$SCRIPT_DIR/runs/retrained/weights/best.pt"

{
  echo "=================================================================="
  echo "FINISH PIPELINE start $(date)"
  echo "=================================================================="
  # 1. wait for training (check by PID, never pgrep/name) ------------------
  if [ -f train.pid ]; then
      TPID="$(cat train.pid)"
      echo "[wait] training PID=$TPID"
      while kill -0 "$TPID" 2>/dev/null; do sleep 10; done
      echo "[wait] training PID=$TPID exited"
  fi
  if [ ! -f "$BEST" ]; then
      echo "ERROR: retrained best.pt not found at $BEST"; exit 1
  fi
  echo "[ok] best.pt present: $BEST"

  # 2. export base + retrained to DeepX (INT8) -----------------------------
  echo "=== export base yolo26n -> DeepX ==="
  "$PY" export_deepx.py --model yolo26n.pt --out-name yolo26n_deepx_model
  echo "=== export retrained -> DeepX ==="
  "$PY" export_deepx.py --model "$BEST" --out-name yolo26n_ppe_deepx_model

  # 3. benchmark the 4 forms ----------------------------------------------
  echo "=== benchmark base fp32 (GPU) ==="
  "$PY" benchmark.py --model yolo26n.pt              --tag base_fp32_gpu      --device gpu
  echo "=== benchmark base INT8 (DX-M1 NPU) ==="
  "$PY" benchmark.py --model yolo26n_deepx_model     --tag base_int8_npu      --device npu
  echo "=== benchmark retrained fp32 (GPU) ==="
  "$PY" benchmark.py --model "$BEST"                 --tag retrained_fp32_gpu --device gpu
  echo "=== benchmark retrained INT8 (DX-M1 NPU) ==="
  "$PY" benchmark.py --model yolo26n_ppe_deepx_model --tag retrained_int8_npu --device npu

  # 4. report + verify -----------------------------------------------------
  echo "=== build report.md ==="
  "$PY" make_report.py
  echo "=== verify ==="
  "$PY" verify.py
  echo "FINISH PIPELINE done $(date)"
} 2>&1 | tee -a "$LOG"

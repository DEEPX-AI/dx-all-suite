#!/usr/bin/env bash
# setup.sh — environment setup + prerequisite checks for the YOLO26n african-wildlife
# retrain + 4-way DeepX eval session. Reuses dx-runtime/venv-dx-runtime (already bundles
# torch+cuda, ultralytics, dx_com, dx_engine). Verifies the stack and the NPU sanity check.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Auto-detect suite root (cross-project reference to dx-runtime) ---
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
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
VPY="$RUNTIME_DIR/venv-dx-runtime/bin/python"

echo "=== SUITE_ROOT: $SUITE_ROOT"
echo "=== Python:     $VPY"
if [ ! -x "$VPY" ]; then
    echo "ERROR: venv-dx-runtime python not found at $VPY"
    echo "Build dx-runtime first: bash $RUNTIME_DIR/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse"
    exit 1
fi

echo "=== [1/2] Verifying venv stack (torch+cuda, ultralytics, dx_com, dx_engine) ==="
"$VPY" - <<'PYEOF'
import importlib, sys
ok = True
for m in ["torch", "ultralytics", "dx_com", "dx_engine", "onnxruntime", "numpy"]:
    try:
        mod = importlib.import_module(m)
        print(f"  OK  {m} {getattr(mod, '__version__', '?')}")
    except Exception as e:
        print(f"  ERR {m}: {type(e).__name__}: {e}"); ok = False
import torch
print(f"  cuda available: {torch.cuda.is_available()} | "
      f"device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'n/a'}")
if not torch.cuda.is_available():
    print("  WARNING: CUDA not available — training will fall back to CPU (slow).")
sys.exit(0 if ok else 1)
PYEOF

echo "=== [2/2] dx_rt NPU sanity check (required for .dxnn NPU eval) ==="
# Judge PASS/FAIL by TEXT OUTPUT, not exit code. Do NOT pipe through tail/head/grep.
bash "$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt

echo "=== setup.sh complete ==="

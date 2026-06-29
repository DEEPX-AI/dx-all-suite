#!/usr/bin/env bash
# Environment setup for the yolo26n brain-tumor retrain + 4-way DeepX eval session.
# Reuses dx-runtime/venv-dx-runtime (full stack: ultralytics + dx_com + dx_engine +
# torch/cuda). Creates a fallback venv only if that runtime venv is missing.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Auto-detect suite root (dx-runtime/ and dx-compiler/ siblings) ----------
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
echo "SUITE_ROOT=$SUITE_ROOT"

# --- 1. DeepX runtime sanity check (NPU INT8 eval needs dx_rt) ----------------
echo "=== [1/3] dx_rt sanity check ==="
if bash "$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt 2>&1 | tee /tmp/braintumor_sanity.log | grep -q "Sanity check PASSED!"; then
    echo "dx_rt sanity: PASS"
else
    echo "WARNING: dx_rt sanity check did not report PASS. NPU INT8 eval will be unavailable."
    echo "  If 'Device initialization failed' -> cold boot the host, then re-run."
fi

# --- 2. Resolve / build the Python environment -------------------------------
echo "=== [2/3] Python environment ==="
RUNTIME_VENV="$RUNTIME_DIR/venv-dx-runtime"
if [ -d "$RUNTIME_VENV" ]; then
    echo "Reusing runtime venv: $RUNTIME_VENV"
    VENV="$RUNTIME_VENV"
else
    echo "Runtime venv missing -> creating local fallback venv (export-only; NPU eval needs dx_rt)"
    VENV="$SCRIPT_DIR/venv"
    python3 -m venv "$VENV"
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
    pip install --upgrade pip
    pip install ultralytics            # dx_com auto-installs on first format=deepx export
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
echo "Python: $(which python) ($(python --version 2>&1))"

# --- 3. Verify the required imports ------------------------------------------
echo "=== [3/3] Import check ==="
python - <<'PY'
import importlib
ok = True
for m in ["torch", "ultralytics", "dx_com", "cv2", "numpy"]:
    try:
        mod = importlib.import_module(m)
        print(f"OK   {m} {getattr(mod, '__version__', '?')}")
    except Exception as e:
        ok = False; print(f"FAIL {m}: {e}")
try:
    import dx_engine; print(f"OK   dx_engine {getattr(dx_engine,'__version__','?')} (NPU INT8 eval available)")
except Exception as e:
    print(f"WARN dx_engine missing ({e}); NPU INT8 eval will be skipped. Build dx_rt:")
    print("     bash $SUITE_ROOT/dx-runtime/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse")
import torch
print("torch.cuda.is_available:", torch.cuda.is_available())
import sys; sys.exit(0 if ok else 1)
PY
echo "Setup complete. Activate with: source $VENV/bin/activate"

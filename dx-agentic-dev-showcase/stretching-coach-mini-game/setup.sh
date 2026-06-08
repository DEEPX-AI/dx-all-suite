#!/usr/bin/env bash
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
# Environment setup for the yolo26n-pose stretch game.
#   - creates an isolated python3.12 venv in this session dir
#   - installs numpy / opencv-python (GUI build) / onnxruntime / requests
#   - builds + installs the ABI-matched dx_engine wheel from dx_rt
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Locate the suite root (dx-runtime/ and dx-compiler/ siblings) ---
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    # Fallback: dx-runtime only (no compiler in this checkout layout).
    SUITE_ROOT="$SCRIPT_DIR"
    while [ "$SUITE_ROOT" != "/" ]; do
        [ -d "$SUITE_ROOT/dx-runtime" ] && break
        SUITE_ROOT="$(dirname "$SUITE_ROOT")"
    done
fi
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: cannot find suite root (expected dx-runtime/ ancestor)"; exit 1
fi
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
DXRT_PKG="$RUNTIME_DIR/dx_rt/python_package"
echo "[setup] SUITE_ROOT = $SUITE_ROOT"

# --- Sanity check (informational; do not hard-fail the env setup) ---
if [ -f "$RUNTIME_DIR/scripts/sanity_check.sh" ]; then
    echo "[setup] running dx_rt sanity check..."
    bash "$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt 2>&1 | tail -3 || true
fi

# --- Create venv (python3.12 required for ABI-matched dx_engine) ---
PY=python3.12
command -v "$PY" >/dev/null 2>&1 || PY=python3
VENV="$SCRIPT_DIR/venv"
if [ ! -d "$VENV" ]; then
    echo "[setup] creating venv with $PY ..."
    "$PY" -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --quiet --upgrade pip

echo "[setup] installing python deps (numpy, opencv-python, onnxruntime, requests)..."
# GUI-capable opencv-python (NOT headless) per suite policy.
python -m pip install --quiet numpy "opencv-python" onnxruntime requests packaging

# --- Build + install dx_engine wheel (ABI-matched to installed dx_rt) ---
if python -c "import dx_engine" 2>/dev/null; then
    echo "[setup] dx_engine already importable in venv."
else
    if [ -d "$DXRT_PKG" ]; then
        echo "[setup] building dx_engine wheel from $DXRT_PKG ..."
        WHEEL_DIR="$SCRIPT_DIR/_wheels"
        mkdir -p "$WHEEL_DIR"
        ( cd "$DXRT_PKG" && python -m pip wheel . --no-deps -w "$WHEEL_DIR" )
        WHL="$(ls -t "$WHEEL_DIR"/dx_engine-*.whl 2>/dev/null | head -1 || true)"
        if [ -n "$WHL" ]; then
            python -m pip install --quiet --force-reinstall --no-deps "$WHL"
        else
            echo "[setup] WARN: no dx_engine wheel produced."
        fi
    else
        echo "[setup] WARN: $DXRT_PKG not found; cannot build dx_engine wheel."
    fi
fi

echo "[setup] verifying imports..."
python - <<'PY'
import numpy, cv2
print("numpy", numpy.__version__, "| opencv", cv2.__version__)
try:
    import dx_engine
    print("dx_engine OK")
except Exception as e:
    print("dx_engine import FAILED:", e)
    raise SystemExit(1)
PY

echo "[setup] DONE. Activate with: source \"$VENV/bin/activate\""

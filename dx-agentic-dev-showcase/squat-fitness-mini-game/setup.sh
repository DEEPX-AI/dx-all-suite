#!/usr/bin/env bash
# Environment setup for the yolo26n_pose squat fitness mini-game.
# Reuses the suite's working dx_engine venv (dx-runtime/venv-dx-runtime) and
# ensures the Python deps needed by the app + its tests are present.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- auto-detect suite root (dx-runtime/ + dx-compiler/ siblings) ---
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: cannot find dx-all-suite root (expected dx-runtime/ + dx-compiler/ siblings)"
    exit 1
fi

RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
DX_APP_DIR="$RUNTIME_DIR/dx_app"
VENV="$RUNTIME_DIR/venv-dx-runtime"
MODEL="$DX_APP_DIR/assets/models/yolo26n-pose.dxnn"

echo "==> SUITE_ROOT  : $SUITE_ROOT"
echo "==> venv        : $VENV"

# --- 1. sanity check the NPU runtime (judge by TEXT, not exit code) ---
echo "==> [1/4] dx_rt sanity check"
( cd "$SUITE_ROOT" && bash dx-runtime/scripts/sanity_check.sh --dx_rt ) > /tmp/squat_sanity.log 2>&1 || true
if grep -q "Sanity check PASSED!" /tmp/squat_sanity.log; then
    echo "    sanity check PASSED"
else
    echo "    WARNING: sanity check did not report PASS — NPU inference may fail."
fi

# --- 2. venv presence ---
echo "==> [2/4] python venv"
if [ ! -x "$VENV/bin/python" ]; then
    echo "ERROR: venv not found at $VENV"
    echo "       Build the dx_engine venv per the suite setup (python3.12 + ABI-matched wheel)."
    exit 1
fi
"$VENV/bin/python" -c "import dx_engine; print('    dx_engine OK')" \
    || { echo "ERROR: dx_engine not importable in venv"; exit 1; }

# --- 3. ensure app + test deps ---
echo "==> [3/4] python dependencies"
"$VENV/bin/python" - <<'PY'
import importlib.util, subprocess, sys
need = {"cv2": "opencv-python-headless", "numpy": "numpy", "pytest": "pytest"}
missing = [pip for mod, pip in need.items() if importlib.util.find_spec(mod) is None]
if missing:
    print("    installing:", missing)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *missing])
else:
    print("    all deps present (cv2, numpy, pytest)")
PY

# --- 4. model presence ---
echo "==> [4/4] model"
if [ -f "$MODEL" ]; then
    echo "    found: $MODEL"
else
    echo "    WARNING: model missing at $MODEL"
    echo "    download with: (cd $DX_APP_DIR && ./setup.sh --models yolo26n-pose)"
fi

echo "==> setup complete."

#!/usr/bin/env bash
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
# setup.sh — prepare a self-contained, portable squat-game app folder.
#
# Steps:
#   1. Resolve the suite root + dx_app root (SUITE_ROOT autodetect).
#   2. Pick a Python with dx_engine (reuse dx-runtime/venv-dx-runtime).
#   3. Vendor the shared framework into ./common so the app runs even when
#      copied entirely outside dx-all-suite.
#   4. Bundle the demo video into ./sample and the model into ./ (best effort).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
cd "$SCRIPT_DIR"
echo "[setup] app dir: $SCRIPT_DIR"

# --- 1. SUITE_ROOT + dx_app root autodetect ---------------------------------
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done

DX_APP_ROOT=""
d="$SCRIPT_DIR"
for _ in $(seq 1 8); do
    if [ -d "$d/src/python_example/common" ]; then DX_APP_ROOT="$d"; break; fi
    d="$(dirname "$d")"
done
echo "[setup] suite root: $SUITE_ROOT"
echo "[setup] dx_app root: ${DX_APP_ROOT:-<not found>}"

# --- 2. Python with dx_engine ------------------------------------------------
PYBIN=""
for cand in "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/.venv/bin/python" \
            "$SUITE_ROOT/dx-runtime/venv-dx-runtime/bin/python"; do
    if [ -x "$cand" ]; then PYBIN="$cand"; break; fi
done
if [ -n "$PYBIN" ]; then
    echo "[setup] python: $PYBIN"
    if "$PYBIN" -c "import dx_engine" >/dev/null 2>&1; then
        echo "[setup] dx_engine import: OK"
    else
        echo "[setup] WARN: dx_engine not importable with $PYBIN."
        echo "        Build/install dx_engine (see dx-runtime/dx_rt/python_package)."
    fi
else
    echo "[setup] WARN: no venv with python found."
    echo "        Expected dx-runtime/venv-dx-runtime or a local ./venv."
fi

# --- 3. Vendor shared framework into ./common --------------------------------
if [ -n "$DX_APP_ROOT" ] && [ -d "$DX_APP_ROOT/src/python_example/common" ]; then
    echo "[setup] vendoring common/ -> ./common"
    rm -rf "$SCRIPT_DIR/common"
    cp -r "$DX_APP_ROOT/src/python_example/common" "$SCRIPT_DIR/common"
    find "$SCRIPT_DIR/common" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
    echo "[setup] vendored common/ ($(find "$SCRIPT_DIR/common" -name '*.py' | wc -l) py files)"
else
    echo "[setup] WARN: could not locate src/python_example/common to vendor."
fi

# --- 4. Bundle demo video + model (best effort) ------------------------------
mkdir -p "$SCRIPT_DIR/sample"
if [ -n "$DX_APP_ROOT" ] && [ -f "$DX_APP_ROOT/sample/squat_demo.mp4" ]; then
    if [ ! -f "$SCRIPT_DIR/sample/squat_demo.mp4" ]; then
        cp "$DX_APP_ROOT/sample/squat_demo.mp4" "$SCRIPT_DIR/sample/squat_demo.mp4"
        echo "[setup] bundled sample/squat_demo.mp4"
    fi
fi
if [ -n "$DX_APP_ROOT" ] && [ -f "$DX_APP_ROOT/assets/models/yolo26n-pose.dxnn" ]; then
    if [ ! -f "$SCRIPT_DIR/yolo26n-pose.dxnn" ]; then
        cp "$DX_APP_ROOT/assets/models/yolo26n-pose.dxnn" "$SCRIPT_DIR/yolo26n-pose.dxnn"
        echo "[setup] bundled yolo26n-pose.dxnn"
    fi
else
    echo "[setup] NOTE: model yolo26n-pose.dxnn not bundled; run.sh will locate it"
    echo "        in assets/models or you can set DXNN_MODEL=<path>."
fi

echo "[setup] done. Run the game with: ./run.sh"

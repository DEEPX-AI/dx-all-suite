#!/usr/bin/env bash
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
# Environment setup for the yolo26n-pose arcade stretching game.
#   - creates a local python3.12 venv
#   - installs GUI-capable opencv-python (NOT headless) + deps
#   - provides dx_engine: builds the ABI-matched wheel from dx_rt if missing
#   - checks the model file exists
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Auto-detect suite root (dx-runtime/ and dx-compiler/ siblings).
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: cannot find suite root (dx-runtime/ + dx-compiler/ siblings)"; exit 1
fi
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
DXAPP_DIR="$RUNTIME_DIR/dx_app"
MODEL_PATH="$DXAPP_DIR/assets/models/yolo26n-pose.dxnn"

echo "==> suite root : $SUITE_ROOT"
echo "==> session dir: $SCRIPT_DIR"

# 1. venv (prefer python3.12 to match the prebuilt dx_engine ABI)
PYBIN="$(command -v python3.12 || command -v python3)"
VENV="$SCRIPT_DIR/venv"
if [ ! -x "$VENV/bin/python" ]; then
    echo "==> creating venv with $PYBIN"
    "$PYBIN" -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --quiet --upgrade pip wheel setuptools

# 2. runtime deps — GUI opencv-python (headless is PROHIBITED in this project)
echo "==> installing python deps (numpy, opencv-python [GUI], onnxruntime, requests, pytest)"
python -m pip install --quiet numpy "opencv-python>=4.8" onnxruntime requests pytest

# 3. dx_engine — build the ABI-matched wheel if not importable
if ! python -c "import dx_engine" >/dev/null 2>&1; then
    echo "==> dx_engine not importable; building ABI-matched wheel from dx_rt"
    PKG_DIR="$RUNTIME_DIR/dx_rt/python_package"
    if [ -d "$PKG_DIR" ]; then
        WHL_DIR="$SCRIPT_DIR/.wheels"
        mkdir -p "$WHL_DIR"
        ( cd "$PKG_DIR" && python -m pip wheel . --no-deps -w "$WHL_DIR" ) || \
            echo "WARN: wheel build failed; run.sh will fall back to dx-runtime/venv-dx-runtime"
        WHL="$(ls -t "$WHL_DIR"/dx_engine-*.whl 2>/dev/null | head -1 || true)"
        if [ -n "$WHL" ]; then
            python -m pip install --quiet --force-reinstall --no-deps "$WHL"
        fi
    else
        echo "WARN: $PKG_DIR not found; run.sh will fall back to dx-runtime/venv-dx-runtime"
    fi
fi
python -c "import dx_engine; print('==> dx_engine OK')" 2>/dev/null || \
    echo "==> dx_engine NOT in local venv (run.sh falls back to dx-runtime/venv-dx-runtime)"

# 4. model presence
if [ -f "$MODEL_PATH" ]; then
    echo "==> model present: $MODEL_PATH"
else
    echo "WARN: model missing: $MODEL_PATH"
    echo "      download with: ( cd '$DXAPP_DIR' && ./setup.sh --models yolo26n-pose )"
fi

echo "==> setup complete."

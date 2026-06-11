#!/usr/bin/env bash
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
# Environment setup for the yolo26n-pose Stretch Arcade mini-game.
#   1. sanity check (informational)
#   2. resolve a Python that imports dx_engine (reuse shared venv, else local venv)
#   3. ensure Python deps (numpy, opencv-python)
#   4. vendor the dx_app `common` framework into ./common  -> portable app folder
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Suite root (dx-runtime/ + dx-compiler/ siblings) ----------------------
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done

# --- dx_app root (contains src/python_example/common) ----------------------
DX_APP_ROOT="$SCRIPT_DIR"
while [ "$DX_APP_ROOT" != "/" ]; do
    if [ -d "$DX_APP_ROOT/src/python_example/common" ]; then
        break
    fi
    DX_APP_ROOT="$(dirname "$DX_APP_ROOT")"
done

RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
echo "[setup] SCRIPT_DIR  = $SCRIPT_DIR"
echo "[setup] SUITE_ROOT  = $SUITE_ROOT"
echo "[setup] DX_APP_ROOT = $DX_APP_ROOT"

# --- 1. sanity check (informational; never blocks setup) -------------------
if [ -f "$RUNTIME_DIR/scripts/sanity_check.sh" ]; then
    echo "[setup] running dx_rt sanity check..."
    bash "$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt 2>&1 | tail -3 || \
        echo "[setup] WARN: sanity check reported issues (NPU needed only at run time)"
fi

# --- 2. pick a Python that imports dx_engine -------------------------------
imports_dx_engine() { "$1" -c "import dx_engine" >/dev/null 2>&1; }

PYBIN=""
for cand in "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/.venv/bin/python" \
            "$RUNTIME_DIR/venv-dx-runtime/bin/python"; do
    if [ -x "$cand" ] && imports_dx_engine "$cand"; then
        PYBIN="$cand"; break
    fi
done

if [ -z "$PYBIN" ]; then
    echo "[setup] no existing venv imports dx_engine — creating local ./venv"
    python3 -m venv "$SCRIPT_DIR/venv"
    PYBIN="$SCRIPT_DIR/venv/bin/python"
    "$PYBIN" -m pip install --upgrade pip >/dev/null
    "$PYBIN" -m pip install numpy "opencv-python" onnxruntime requests
    # ABI-matched dx_engine wheel (built from the in-suite python_package)
    if [ -d "$RUNTIME_DIR/dx_rt/python_package" ] && ! imports_dx_engine "$PYBIN"; then
        echo "[setup] building dx_engine wheel from dx_rt/python_package ..."
        ( cd "$RUNTIME_DIR/dx_rt/python_package" && "$PYBIN" -m pip wheel . --no-deps -w /tmp/dxw )
        "$PYBIN" -m pip install /tmp/dxw/dx_engine-*.whl || true
    fi
fi
echo "[setup] PYBIN = $PYBIN"
"$PYBIN" -c "import dx_engine; print('[setup] dx_engine OK')" || \
    echo "[setup] WARN: dx_engine not importable — NPU runs will fail until resolved"
"$PYBIN" -c "import numpy, cv2; print('[setup] numpy + opencv OK')"

# --- 3. vendor the common framework into ./common --------------------------
SRC_COMMON="$DX_APP_ROOT/src/python_example/common"
if [ -d "$SRC_COMMON" ]; then
    echo "[setup] vendoring common framework -> $SCRIPT_DIR/common"
    rm -rf "$SCRIPT_DIR/common"
    if command -v rsync >/dev/null 2>&1; then
        rsync -a --exclude='__pycache__' --exclude='*.pyc' "$SRC_COMMON/" "$SCRIPT_DIR/common/"
    else
        cp -r "$SRC_COMMON" "$SCRIPT_DIR/common"
        find "$SCRIPT_DIR/common" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
    fi
    echo "[setup] common vendored: $("$PYBIN" - <<PY
import os; print(sum(len(f) for _,_,f in os.walk("$SCRIPT_DIR/common")), "files")
PY
)"
else
    echo "[setup] WARN: $SRC_COMMON not found — cannot vendor common (in-place dev still works)"
fi

# record the resolved interpreter for run.sh
echo "$PYBIN" > "$SCRIPT_DIR/.python_path"
echo "[setup] DONE. Launch with: ./run.sh --video <file>   or   ./run.sh --camera 0"

#!/usr/bin/env bash
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
#
# setup.sh — environment sanity check for the YOLO26n-Pose squat game.
#
# Verifies (does NOT reinstall) the dx-runtime environment this app depends on:
#   * a usable Python venv with dx_engine importable
#   * GUI-capable OpenCV (opencv-python, NOT opencv-python-headless)
#   * the yolo26n-pose .dxnn model present
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

# --- locate dx_app root (dir containing src/python_example/common) ----------
DX_APP_ROOT="$SCRIPT_DIR"
while [ "$DX_APP_ROOT" != "/" ]; do
    if [ -d "$DX_APP_ROOT/src/python_example/common" ]; then break; fi
    DX_APP_ROOT="$(dirname "$DX_APP_ROOT")"
done

# --- locate suite root (dx-runtime/ and dx-compiler/ siblings) --------------
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then break; fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"

echo "==> dx_app root : $DX_APP_ROOT"
echo "==> suite root  : $SUITE_ROOT"

# --- pick a Python venv -----------------------------------------------------
VENV_PY=""
for cand in "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/.venv/bin/python" \
            "$RUNTIME_DIR/venv-dx-runtime/bin/python"; do
    if [ -x "$cand" ]; then VENV_PY="$cand"; break; fi
done
if [ -z "$VENV_PY" ]; then
    echo "[WARN] No project venv found (looked for local venv/.venv and"
    echo "       dx-runtime/venv-dx-runtime). Falling back to system python3."
    VENV_PY="$(command -v python3 || true)"
fi
echo "==> python      : $VENV_PY"
[ -n "$VENV_PY" ] || { echo "[ERROR] No python3 available."; exit 1; }

# --- dx_engine import check -------------------------------------------------
if "$VENV_PY" -c "import dx_engine" 2>/dev/null; then
    echo "[OK] dx_engine importable"
else
    echo "[ERROR] dx_engine not importable with $VENV_PY"
    echo "        Build/install dx_app runtime: (cd $DX_APP_ROOT && ./install.sh && ./build.sh)"
    exit 1
fi

# --- OpenCV check (must be GUI-capable, not headless) -----------------------
if "$VENV_PY" -c "import cv2" 2>/dev/null; then
    echo "[OK] OpenCV importable ($("$VENV_PY" -c 'import cv2;print(cv2.__version__)'))"
    if "$VENV_PY" - <<'PY' 2>/dev/null
import cv2, sys
sys.exit(0 if hasattr(cv2, "imshow") else 1)
PY
    then echo "[OK] OpenCV is GUI-capable"
    else echo "[WARN] OpenCV lacks GUI (headless build) — live --display will be skipped; --save still works"
    fi
else
    echo "[ERROR] OpenCV (cv2) not importable. Install GUI-capable opencv-python (NOT opencv-python-headless)."
    exit 1
fi

# --- model presence ---------------------------------------------------------
MODEL="${MODEL:-$DX_APP_ROOT/assets/models/yolo26n-pose.dxnn}"
if [ -f "$MODEL" ]; then
    echo "[OK] model present: $MODEL"
else
    echo "[WARN] model not found: $MODEL"
    echo "       Download with: (cd $DX_APP_ROOT && ./setup.sh --models yolo26n-pose)"
fi

echo "==> setup.sh complete."

#!/usr/bin/env bash
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
#
# run.sh — one-command launcher for the YOLO26n-Pose squat-counting game.
#
# Relocatable (works after the app is moved out of dx-agentic-dev/):
#   1) venv fallback  : local venv/.venv -> dx-runtime/venv-dx-runtime -> warn
#   2) model guard    : fail early with a download hint if the .dxnn is missing
#   3) bundled-sample-first : prefer app-local sample/, else dx_app/sample/
#
# Usage:
#   ./run.sh                       # video mode on bundled squat_demo.mp4 (+saves annotated mp4)
#   ./run.sh --video path.mp4      # custom video (+saves annotated mp4)
#   ./run.sh --camera 0            # live camera id 0
#   ./run.sh --no-display          # extra args pass through to the app
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

# --- locate dx_app root (dir containing src/python_example/common) ----------
DX_APP_ROOT="$SCRIPT_DIR"
while [ "$DX_APP_ROOT" != "/" ]; do
    if [ -d "$DX_APP_ROOT/src/python_example/common" ]; then break; fi
    DX_APP_ROOT="$(dirname "$DX_APP_ROOT")"
done
if [ "$DX_APP_ROOT" = "/" ]; then
    # Fallback via suite-root detection (dx-runtime/ & dx-compiler/ siblings).
    SUITE_ROOT="$SCRIPT_DIR"
    while [ "$SUITE_ROOT" != "/" ]; do
        if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then break; fi
        SUITE_ROOT="$(dirname "$SUITE_ROOT")"
    done
    [ "$SUITE_ROOT" != "/" ] || { echo "[ERROR] Cannot locate dx_app root."; exit 1; }
    DX_APP_ROOT="$SUITE_ROOT/dx-runtime/dx_app"
fi

# --- venv fallback ----------------------------------------------------------
PY=""
for cand in "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/.venv/bin/python" \
            "$DX_APP_ROOT/../venv-dx-runtime/bin/python"; do
    if [ -x "$cand" ]; then PY="$cand"; break; fi
done
if [ -z "$PY" ]; then
    echo "[WARN] No venv found (local venv/.venv or dx-runtime/venv-dx-runtime); using system python3."
    PY="$(command -v python3 || true)"
fi
[ -n "$PY" ] || { echo "[ERROR] No python3 available."; exit 1; }

# --- model guard ------------------------------------------------------------
MODEL="${MODEL:-$DX_APP_ROOT/assets/models/yolo26n-pose.dxnn}"
if [ ! -f "$MODEL" ]; then
    echo "[ERROR] Model not found: $MODEL"
    echo "        Download it with:"
    echo "          (cd \"$DX_APP_ROOT\" && ./setup.sh --models yolo26n-pose)"
    exit 1
fi

# --- bundled-sample-first ---------------------------------------------------
SAMPLE=""
for cand in "$SCRIPT_DIR/sample/squat_demo.mp4" "$DX_APP_ROOT/sample/squat_demo.mp4"; do
    if [ -f "$cand" ]; then SAMPLE="$cand"; break; fi
done

APP="$SCRIPT_DIR/yolo26n_pose_squat_sync.py"

# --- decide input -----------------------------------------------------------
# If the caller passed any input flag (--video/-v/--camera/-c/--image/-i/--rtsp/-r),
# pass everything straight through. Otherwise default to the bundled sample video
# and save the annotated result.
HAS_INPUT=0
for a in "$@"; do
    case "$a" in
        --video|-v|--camera|-c|--image|-i|--rtsp|-r) HAS_INPUT=1 ;;
    esac
done

echo "==> python : $PY"
echo "==> model  : $MODEL"

if [ "$HAS_INPUT" -eq 1 ]; then
    exec "$PY" "$APP" --model "$MODEL" "$@"
else
    if [ -z "$SAMPLE" ]; then
        echo "[ERROR] No input given and bundled sample squat_demo.mp4 not found"
        echo "        under $SCRIPT_DIR/sample/ or $DX_APP_ROOT/sample/."
        echo "        Provide one:  ./run.sh --video <file>   or   ./run.sh --camera 0"
        exit 1
    fi
    echo "==> input  : $SAMPLE (bundled sample, annotated video will be saved)"
    exec "$PY" "$APP" --model "$MODEL" --video "$SAMPLE" --save --save-dir "$SCRIPT_DIR/output" "$@"
fi

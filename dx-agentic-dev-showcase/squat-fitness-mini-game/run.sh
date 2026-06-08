#!/usr/bin/env bash
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
# run.sh — relocatable launcher for the yolo26n-pose squat mini-game.
#
# Stays runnable after the app folder is moved/copied (even outside the suite):
#   * venv fallback chain: local ./venv|.venv -> dx-runtime/venv-dx-runtime -> python3 (warn)
#   * model-existence guard with a download hint
#   * bundled-sample-first: ./sample/squat_demo.mp4 -> dx_app/sample/squat_demo.mp4
#
# Usage:
#   ./run.sh                       # play on the bundled demo video (+ save annotated output)
#   ./run.sh --camera 0            # live camera
#   ./run.sh --video my.mp4 --save # custom video
#   ./run.sh --target-reps 15 --camera 0
#   DXNN_MODEL=/path/yolo26n-pose.dxnn ./run.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
cd "$SCRIPT_DIR"

# --- suite root + dx_app root autodetect (best effort) ----------------------
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then break; fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
DX_APP_ROOT=""
d="$SCRIPT_DIR"
for _ in $(seq 1 8); do
    if [ -d "$d/src/python_example/common" ] || [ -d "$d/assets/models" ]; then
        DX_APP_ROOT="$d"; break
    fi
    d="$(dirname "$d")"
done

# --- 1. venv fallback chain --------------------------------------------------
PYBIN=""
for cand in "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/.venv/bin/python" \
            "$SUITE_ROOT/dx-runtime/venv-dx-runtime/bin/python"; do
    if [ -x "$cand" ]; then PYBIN="$cand"; break; fi
done
if [ -z "$PYBIN" ]; then
    echo "[run] WARN: no project venv found; falling back to 'python3'." >&2
    echo "[run]       dx_engine must be importable for inference to work." >&2
    PYBIN="python3"
fi

# --- 2. model-existence guard ------------------------------------------------
MODEL="${DXNN_MODEL:-}"
if [ -z "$MODEL" ]; then
    for c in "$SCRIPT_DIR/yolo26n-pose.dxnn" \
             "${DX_APP_ROOT:-}/assets/models/yolo26n-pose.dxnn"; do
        if [ -n "$c" ] && [ -f "$c" ]; then MODEL="$c"; break; fi
    done
fi
if [ -z "$MODEL" ] || [ ! -f "$MODEL" ]; then
    echo "[run] ERROR: yolo26n-pose.dxnn not found." >&2
    echo "[run]   -> Download:  (from dx_app)  ./setup.sh --models yolo26n-pose" >&2
    echo "[run]   -> Or set:    DXNN_MODEL=/path/to/yolo26n-pose.dxnn ./run.sh" >&2
    exit 1
fi
echo "[run] model:  $MODEL"
echo "[run] python: $PYBIN"

# --- 3. launch ---------------------------------------------------------------
if [ "$#" -gt 0 ]; then
    # user supplied their own input/options (e.g. --camera 0)
    exec "$PYBIN" yolo26n_pose_squat_sync.py -m "$MODEL" "$@"
fi

# no args: bundled-sample-first demo (+ save annotated output video)
SAMPLE=""
for c in "$SCRIPT_DIR/sample/squat_demo.mp4" \
         "${DX_APP_ROOT:-}/sample/squat_demo.mp4"; do
    if [ -n "$c" ] && [ -f "$c" ]; then SAMPLE="$c"; break; fi
done
if [ -z "$SAMPLE" ]; then
    echo "[run] no bundled sample video found." >&2
    echo "[run] Provide input explicitly, e.g.:  ./run.sh --camera 0" >&2
    exit 1
fi
echo "[run] demo video: $SAMPLE  (annotated output saved via --save)"
exec "$PYBIN" yolo26n_pose_squat_sync.py -m "$MODEL" --video "$SAMPLE" --save

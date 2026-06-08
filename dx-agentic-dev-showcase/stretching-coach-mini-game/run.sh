#!/usr/bin/env bash
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
# Launcher for the yolo26n-pose arcade stretching mini-game.
#
# Examples:
#   ./run.sh                          # demo: stretching_demo.mp4 -> annotated output (headless)
#   ./run.sh --video clip.mp4         # a specific video file (annotated output saved)
#   ./run.sh --camera 0               # live webcam, on-screen window
#   ./run.sh --camera 0 --no-display  # live webcam, no window
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Locate suite / runtime root ---
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    [ -d "$SUITE_ROOT/dx-runtime" ] && break
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: cannot find dx-runtime root"; exit 1
fi
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
APP_DIR="$RUNTIME_DIR/dx_app"

MODEL="${MODEL:-$APP_DIR/assets/models/yolo26n-pose.dxnn}"

# Prefer the sample video bundled with this showcase; fall back to dx_app/sample.
if [ -f "$SCRIPT_DIR/sample/stretching_demo.mp4" ]; then
    DEMO_VIDEO="${DEMO_VIDEO:-$SCRIPT_DIR/sample/stretching_demo.mp4}"
else
    DEMO_VIDEO="${DEMO_VIDEO:-$APP_DIR/sample/stretching_demo.mp4}"
fi

# --- Model guard: the .dxnn is a large binary fetched by the dx_app setup, not
#     committed. Fail early with a clear instruction instead of a cryptic error. ---
if [ ! -f "$MODEL" ]; then
    echo "ERROR: model not found at:"
    echo "    $MODEL"
    echo "Download it (yolo26n-pose), e.g.:"
    echo "    (cd \"$APP_DIR\" && ./setup.sh --models yolo26n-pose)"
    exit 1
fi

# --- Activate venv: prefer the local one (from setup.sh), else the shared
#     dx-runtime venv (already has dx_engine + GUI opencv-python) ---
if [ -d "$SCRIPT_DIR/venv" ]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -x "$RUNTIME_DIR/venv-dx-runtime/bin/python" ]; then
    # shellcheck disable=SC1091
    source "$RUNTIME_DIR/venv-dx-runtime/bin/activate"
else
    echo "ERROR: no venv found. Run: bash setup.sh"; exit 1
fi

cd "$SCRIPT_DIR"

# --- No args -> headless demo over the bundled video, saving annotated output ---
if [ "$#" -eq 0 ]; then
    echo "[run] demo mode: $DEMO_VIDEO (annotated output saved, headless)"
    unset DISPLAY WAYLAND_DISPLAY || true
    exec python yolo26n_pose_stretch_game_sync.py \
        -m "$MODEL" --video "$DEMO_VIDEO" --save --no-display --show-log
fi

# --- Otherwise pass user args straight through ---
exec python yolo26n_pose_stretch_game_sync.py -m "$MODEL" "$@"

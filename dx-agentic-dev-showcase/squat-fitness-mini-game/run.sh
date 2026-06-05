#!/usr/bin/env bash
# One-command launcher for the yolo26n_pose squat fitness mini-game.
#
#   ./run.sh                       # default: video demo, saves annotated output
#   ./run.sh --camera 0            # live camera (needs a display)
#   ./run.sh --video path.mp4 --save
#
# Any args passed to run.sh are forwarded to the app, overriding the defaults.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- auto-detect suite root ---
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: cannot find dx-all-suite root"; exit 1
fi

RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
DX_APP_DIR="$RUNTIME_DIR/dx_app"
VENV="$RUNTIME_DIR/venv-dx-runtime"
MODEL="$DX_APP_DIR/assets/models/yolo26n-pose.dxnn"

# Prefer the sample video bundled with this showcase; fall back to dx_app/sample.
if [ -f "$SCRIPT_DIR/sample/squat_demo.mp4" ]; then
    VIDEO="$SCRIPT_DIR/sample/squat_demo.mp4"
else
    VIDEO="$DX_APP_DIR/sample/squat_demo.mp4"
fi

# --- model guard: the .dxnn is a large binary fetched by the dx_app setup, not
#     committed. Fail early with a clear instruction instead of a cryptic error. ---
if [ ! -f "$MODEL" ]; then
    echo "ERROR: model not found at:"
    echo "    $MODEL"
    echo "Download it first (yolo26n-pose), e.g.:"
    echo "    (cd \"$DX_APP_DIR\" && ./setup.sh --models yolo26n-pose)"
    echo "or place a yolo26n-pose.dxnn at the path above, then re-run."
    exit 1
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

cd "$SCRIPT_DIR"

if [ "$#" -gt 0 ]; then
    # user provided explicit args (e.g. --camera 0)
    exec python yolo26n_pose_squat_sync.py -m "$MODEL" "$@"
fi

# Default: headless video demo that writes an annotated output video.
# Headless safety: opencv-python-headless throws on destroyAllWindows when
# DISPLAY is set, so clear it for the no-display run.
unset DISPLAY WAYLAND_DISPLAY
exec python yolo26n_pose_squat_sync.py \
    -m "$MODEL" \
    --video "$VIDEO" \
    --save \
    --no-display \
    --save-dir "$SCRIPT_DIR/artifacts"

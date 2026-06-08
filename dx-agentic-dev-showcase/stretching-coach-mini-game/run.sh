#!/usr/bin/env bash
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
# Relocatable launcher for the yolo26n-pose arcade stretching game.
# Stays runnable after the app is moved out of dx-agentic-dev/.
#   - venv fallback chain: local venv/.venv -> dx-runtime/venv-dx-runtime -> warn
#     (picks the first whose python can import dx_engine)
#   - model-existence guard (fails early with a download hint)
#   - bundled-sample-first input resolution
#
# Usage:
#   ./run.sh                                  # default sample clip, saves annotated video
#   ./run.sh --video /path/clip.mp4 --save    # specific video file
#   ./run.sh --camera 0                        # live camera
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Auto-detect suite root (dx-runtime/ + dx-compiler/ siblings).
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
DXAPP_DIR="$RUNTIME_DIR/dx_app"
MODEL_PATH="${DX_MODEL:-$DXAPP_DIR/assets/models/yolo26n-pose.dxnn}"

# 1. pick a python that can import dx_engine
pick_python() {
    for cand in "$SCRIPT_DIR/venv" "$SCRIPT_DIR/.venv" "$RUNTIME_DIR/venv-dx-runtime"; do
        if [ -x "$cand/bin/python" ] && "$cand/bin/python" -c "import dx_engine" >/dev/null 2>&1; then
            echo "$cand/bin/python"; return 0
        fi
    done
    echo ""; return 1
}
PY="$(pick_python || true)"
if [ -z "$PY" ]; then
    echo "WARN: no venv with dx_engine found (tried local venv/.venv and dx-runtime/venv-dx-runtime)."
    echo "      Run ./setup.sh first. Falling back to system python3 (may fail to import dx_engine)."
    PY="$(command -v python3)"
fi
echo "==> python: $PY"

# 2. model guard
if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: model not found: $MODEL_PATH"
    echo "       download with: ( cd '$DXAPP_DIR' && ./setup.sh --models yolo26n-pose )"
    echo "       or set DX_MODEL=/path/to/yolo26n-pose.dxnn"
    exit 1
fi

# 3. forward args; inject defaults when the user gave none
ARGS=("$@")
have_input=0; have_model=0
for a in "$@"; do
    case "$a" in
        -v|--video|-c|--camera|-i|--image|-r|--rtsp) have_input=1 ;;
        -m|--model) have_model=1 ;;
    esac
done

if [ "$have_model" -eq 0 ]; then
    ARGS=(-m "$MODEL_PATH" "${ARGS[@]}")
fi

if [ "$have_input" -eq 0 ]; then
    # bundled-sample-first: app's own sample/, else dx_app/sample/
    for cand in \
        "$SCRIPT_DIR/sample/stretching_demo.mp4" \
        "$DXAPP_DIR/sample/stretching_demo.mp4" \
        "$DXAPP_DIR/sample/stretching_extending_both_arms.mp4"; do
        if [ -f "$cand" ]; then
            echo "==> no input given; using bundled sample: $cand (saving annotated video)"
            ARGS+=(--video "$cand" --save)
            break
        fi
    done
fi

cd "$SCRIPT_DIR"
echo "==> running: $PY stretch_game_sync.py ${ARGS[*]}"
exec "$PY" stretch_game_sync.py "${ARGS[@]}"

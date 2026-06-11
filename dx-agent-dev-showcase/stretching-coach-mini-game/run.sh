#!/usr/bin/env bash
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
# Relocatable launcher for the Stretch Arcade mini-game.
# Stays runnable after this folder is copied out of dx-agent-dev/ (or out of the
# whole suite): venv fallback chain, model-existence guard, bundled-sample-first.
#
#   ./run.sh                       # bundled demo video, saves annotated output
#   ./run.sh --video my_clip.mp4   # a specific video file (auto --save)
#   ./run.sh --camera 0            # live camera, id 0
#   MODEL=/path/yolo26n-pose.dxnn ./run.sh --camera 0
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Suite / dx_app roots (best-effort; may be absent if relocated) --------
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ] && break
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
DX_APP_ROOT="$SCRIPT_DIR"
while [ "$DX_APP_ROOT" != "/" ]; do
    [ -d "$DX_APP_ROOT/src/python_example/common" ] && break
    DX_APP_ROOT="$(dirname "$DX_APP_ROOT")"
done

# --- 1. Python: local venv -> recorded -> shared dx-runtime venv -> warn ----
imports_dx_engine() { "$1" -c "import dx_engine" >/dev/null 2>&1; }
PYBIN=""
CANDS=("$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/.venv/bin/python")
[ -f "$SCRIPT_DIR/.python_path" ] && CANDS+=("$(cat "$SCRIPT_DIR/.python_path")")
[ "$SUITE_ROOT" != "/" ] && CANDS+=("$SUITE_ROOT/dx-runtime/venv-dx-runtime/bin/python")
for c in "${CANDS[@]}"; do
    if [ -x "$c" ] && imports_dx_engine "$c"; then PYBIN="$c"; break; fi
done
if [ -z "$PYBIN" ]; then
    echo "WARN: no venv with dx_engine found — falling back to 'python3'." >&2
    echo "      If imports fail, run ./setup.sh first." >&2
    PYBIN="python3"
fi

# --- 2. Model resolution + existence guard ---------------------------------
MODEL="${MODEL:-}"
if [ -z "$MODEL" ]; then
    for m in "$SCRIPT_DIR/yolo26n-pose.dxnn" \
             "$SCRIPT_DIR/assets/models/yolo26n-pose.dxnn" \
             "$DX_APP_ROOT/assets/models/yolo26n-pose.dxnn"; do
        [ -f "$m" ] && { MODEL="$m"; break; }
    done
fi
# only enforce the guard if the user did not pass their own --model/-m
USER_MODEL=0; for a in "$@"; do [ "$a" = "--model" ] || [ "$a" = "-m" ] && USER_MODEL=1; done
if [ "$USER_MODEL" -eq 0 ] && { [ -z "$MODEL" ] || [ ! -f "$MODEL" ]; }; then
    echo "ERROR: yolo26n-pose.dxnn not found." >&2
    echo "  Provide it with:  MODEL=/path/to/yolo26n-pose.dxnn ./run.sh ..." >&2
    echo "  Or download into dx_app:  (cd \"\$DX_APP_ROOT\" && ./setup.sh --models yolo26n-pose)" >&2
    exit 1
fi

# --- 3. Inputs: pass through; default to bundled sample (sample-first) ------
HAS_INPUT=0; HAS_MODEL=$USER_MODEL; HAS_VIDEO=0; HAS_SAVE=0; HAS_SAVEDIR=0
for a in "$@"; do
    case "$a" in
        --video|-v) HAS_INPUT=1; HAS_VIDEO=1;;
        --camera|-c|--image|-i|--rtsp|-r) HAS_INPUT=1;;
        --save|-s) HAS_SAVE=1;;
        --save-dir) HAS_SAVEDIR=1; HAS_SAVE=1;;
    esac
done

ARGS=("$@")
[ "$HAS_MODEL" -eq 0 ] && ARGS=(-m "$MODEL" "${ARGS[@]}")
# A video file run saves an annotated output by default (the result is reviewable).
if [ "$HAS_VIDEO" -eq 1 ] && [ "$HAS_SAVE" -eq 0 ]; then
    echo "[run] video input — saving annotated output video (--save)"
    ARGS+=(--save); HAS_SAVE=1
fi
# Keep saved output inside the app folder so it works even when relocated.
if [ "$HAS_SAVE" -eq 1 ] && [ "$HAS_SAVEDIR" -eq 0 ]; then
    ARGS+=(--save-dir "$SCRIPT_DIR/output")
fi

if [ "$HAS_INPUT" -eq 0 ]; then
    DEMO=""
    for d in "$SCRIPT_DIR/sample/stretching_demo.mp4" \
             "$DX_APP_ROOT/sample/stretching_demo.mp4"; do
        [ -f "$d" ] && { DEMO="$d"; break; }
    done
    if [ -n "$DEMO" ]; then
        echo "[run] no input given — using bundled demo: $DEMO (saving annotated output)"
        ARGS+=(--video "$DEMO" --save)
    else
        echo "[run] no input and no bundled sample found — defaulting to --camera 0"
        ARGS+=(--camera 0)
    fi
fi

echo "[run] $PYBIN stretch_game_sync.py ${ARGS[*]}"
cd "$SCRIPT_DIR"
exec "$PYBIN" stretch_game_sync.py "${ARGS[@]}"

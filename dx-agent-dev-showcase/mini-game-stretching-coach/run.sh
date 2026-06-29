#!/bin/bash
# One-command launcher for Stretch Arcade (yolo26n-pose) — DX Agent-Driven Dev
#
#   bash run.sh                         # demo video, headless, saves annotated mp4
#   bash run.sh --camera 0              # live camera (needs a display)
#   bash run.sh --video my.mp4 --save   # custom video
#   DXNN_MODEL=/path/yolo26n-pose.dxnn bash run.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Auto-detect suite root (for cross-project references) ---
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
[ "$SUITE_ROOT" = "/" ] && echo "[WARN] suite root not found (dx-runtime/ + dx-compiler/ siblings)"
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"

# --- Activate venv (relocatable; do NOT re-run setup.sh) ---
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
elif [ -x "$RUNTIME_DIR/venv-dx-runtime/bin/python" ]; then
    source "$RUNTIME_DIR/venv-dx-runtime/bin/activate"
else
    echo "[WARN] no venv found — run 'bash setup.sh' first if imports fail"
fi

# --- Model resolution (SUITE_ROOT-derived; bundled-first) ---
MODEL_NAME="yolo26n-pose.dxnn"
MODEL="${DXNN_MODEL:-}"
if [ -z "$MODEL" ]; then
    for _c in "$SCRIPT_DIR/$MODEL_NAME" \
              "$RUNTIME_DIR/dx_app/assets/models/$MODEL_NAME" \
              "$RUNTIME_DIR/dx_app/assets/models"/models-*/"$MODEL_NAME"; do
        if [ -f "$_c" ]; then MODEL="$_c"; break; fi
    done
fi
if [ -z "$MODEL" ] || [ ! -f "$MODEL" ]; then
    echo "[ERROR] $MODEL_NAME not found." >&2
    echo "  searched: ./ and \$SUITE_ROOT/dx-runtime/dx_app/assets/models[/models-*]" >&2
    echo "  -> Set:      DXNN_MODEL=/path/to/$MODEL_NAME bash run.sh" >&2
    echo "  -> Or fetch: (cd \"\$SUITE_ROOT/dx-runtime/dx_app\" && ./setup.sh)" >&2
    exit 1
fi
echo "[INFO] Model: $MODEL"

# --- Standalone PYTHONPATH backup for the dynamic walker ---
if [ -d "$SCRIPT_DIR/common" ]; then
    export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"
else
    _v3="$SCRIPT_DIR"
    while [ "$_v3" != "/" ]; do
        if [ -d "$_v3/src/python_example/common" ]; then
            export PYTHONPATH="$_v3/src/python_example${PYTHONPATH:+:$PYTHONPATH}"; break
        fi
        _v3="$(dirname "$_v3")"
    done
fi

# --- Run ---
# Default demo: bundled video, headless, save annotated output. Pass any args to
# override (e.g. --camera 0, --video path.mp4). Default sample lives beside this app.
DEMO_VIDEO="$SCRIPT_DIR/sample/stretching_demo.mp4"
if [ "$#" -gt 0 ]; then
    python "$SCRIPT_DIR/yolo26n_pose_sync.py" --model "$MODEL" "$@"
else
    python "$SCRIPT_DIR/yolo26n_pose_sync.py" --model "$MODEL" \
        --video "$DEMO_VIDEO" --no-display --save --save-dir "$SCRIPT_DIR/output"
fi

#!/bin/bash
# =============================================================================
# run.sh — one-command launcher for the PP-OCRv5 video/webcam OCR app (DX-M1 NPU)
#
#   ./run.sh                         # process the bundled demo video
#   ./run.sh myclip.mp4              # process a video file
#   ./run.sh myclip.mp4 out.mp4      # ... with a custom output path
#   ./run.sh 0 webcam_out.mp4        # live webcam (camera index 0)
#
# Activates the session venv (created by setup.sh), applies the DX-RT runtime
# optimisation env, and runs OUR entry (ocr_video.py) — never a fork demo.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
cd "$SCRIPT_DIR"

# --- Suite root (for the venv-dx-runtime fallback) ---------------------------
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then break; fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"

# --- Activate venv: prefer the session venv (has shapely/pyclipper + bridge) -
if [ -x "$SCRIPT_DIR/venv/bin/python" ]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -x "$RUNTIME_DIR/venv-dx-runtime/bin/python" ]; then
    echo "[run] WARNING: session venv missing — falling back to venv-dx-runtime."
    echo "[run] If shapely/pyclipper are missing, run ./setup.sh first."
    # shellcheck disable=SC1091
    source "$RUNTIME_DIR/venv-dx-runtime/bin/activate"
else
    echo "[run] ERROR: no venv found. Run ./setup.sh first."
    exit 1
fi

# --- DX-RT runtime optimisation env (PP-OCRv5 defaults) + NPU device ---------
export CUSTOM_INTER_OP_THREADS_COUNT="${CUSTOM_INTER_OP_THREADS_COUNT:-1}"
export CUSTOM_INTRA_OP_THREADS_COUNT="${CUSTOM_INTRA_OP_THREADS_COUNT:-2}"
export DXRT_DYNAMIC_CPU_THREAD="${DXRT_DYNAMIC_CPU_THREAD:-1}"
export DXRT_TASK_MAX_LOAD="${DXRT_TASK_MAX_LOAD:-3}"
export NFH_INPUT_WORKER_THREADS="${NFH_INPUT_WORKER_THREADS:-2}"
export NFH_OUTPUT_WORKER_THREADS="${NFH_OUTPUT_WORKER_THREADS:-4}"
export DXNN_DEVICES="${DXNN_DEVICES:-0}"
export LD_LIBRARY_PATH="${VIRTUAL_ENV:-}/lib:${LD_LIBRARY_PATH:-}"

# --- Model presence guard ----------------------------------------------------
MODEL_DIR="$SCRIPT_DIR/engine/model_files/server"
if [ ! -f "$MODEL_DIR/det_v5_960.dxnn" ]; then
    echo "[run] ERROR: PP-OCRv5 models missing in $MODEL_DIR. Run ./setup.sh to download them."
    exit 1
fi

# --- Resolve source (positional arg, else the bundled demo video) ------------
DEMO_VIDEO="$SCRIPT_DIR/sample/ocr_demo.mp4"
SOURCE="${1:-$DEMO_VIDEO}"
OUTPUT="${2:-$SCRIPT_DIR/ocr_output.mp4}"

if [[ ! "$SOURCE" =~ ^[0-9]+$ ]] && [ ! -f "$SOURCE" ]; then
    echo "[run] ERROR: source not found: $SOURCE"
    echo "[run] Pass a video file path or a webcam index, e.g.: ./run.sh 0"
    exit 1
fi

echo "[run] source=$SOURCE  output=$OUTPUT  DXNN_DEVICES=$DXNN_DEVICES"
python "$SCRIPT_DIR/ocr_video.py" \
    --source "$SOURCE" \
    --output "$OUTPUT" \
    --sample "$SCRIPT_DIR/sample_detect.jpg" \
    --model-dir "$MODEL_DIR" \
    "${@:3}"

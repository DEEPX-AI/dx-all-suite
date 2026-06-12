#!/usr/bin/env bash
# =============================================================================
# run.sh — One-command launcher for the RapidDoc PDF -> Markdown NPU app.
#
# Usage:
#   ./run.sh [PDF_PATH] [PARSE_METHOD]
#     PDF_PATH      input PDF (default: bundled sample_input.pdf)
#     PARSE_METHOD  auto | txt | ocr   (default: auto)
#
#   Env override:  METHOD=ocr ./run.sh mydoc.pdf
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Auto-detect the dx-all-suite root (for the dx_engine venv fallback) ---
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
RUNTIME_VENV="$SUITE_ROOT/dx-runtime/venv-dx-runtime"

# --- venv selection: local session venv (preferred; has deps + dx_engine bridge) ---
if [ -x "$SCRIPT_DIR/venv/bin/python" ]; then
    PY="$SCRIPT_DIR/venv/bin/python"
elif [ -x "$RUNTIME_VENV/bin/python" ]; then
    echo "WARNING: local venv missing; falling back to venv-dx-runtime (RapidDoc deps may be absent)."
    echo "         Run ./setup.sh to build the self-contained session venv."
    PY="$RUNTIME_VENV/bin/python"
else
    echo "ERROR: no usable Python venv found. Run ./setup.sh first."
    exit 1
fi

# --- DX-RT threading env + device selection ---
# shellcheck disable=SC1091
source "$SCRIPT_DIR/deepx_scripts/set_env.sh" 1 2 1 3 2 4
export DXNN_DEVICES=0

# --- Model-existence guard ---
if [ ! -d "$SCRIPT_DIR/dxnn_models" ] || [ -z "$(ls -A "$SCRIPT_DIR/dxnn_models" 2>/dev/null)" ]; then
    echo "ERROR: dxnn_models/ is empty. Run ./setup.sh to download the NPU models."
    exit 1
fi

# --- Resolve input to an ABSOLUTE path (the pipeline runs cwd-independent) ---
INPUT_ARG="${1:-$SCRIPT_DIR/sample_input.pdf}"
METHOD="${2:-${METHOD:-auto}}"
INPUT_ABS="$(cd "$(dirname "$INPUT_ARG")" && pwd -P)/$(basename "$INPUT_ARG")"
if [ ! -f "$INPUT_ABS" ]; then
    echo "ERROR: input PDF not found: $INPUT_ABS"
    exit 1
fi

echo "============================================================"
echo " RapidDoc PDF->Markdown on DX-M1 NPU"
echo "   python  : $PY"
echo "   input   : $INPUT_ABS"
echo "   method  : $METHOD"
echo "   output  : $SCRIPT_DIR/output"
echo "============================================================"

exec "$PY" "$SCRIPT_DIR/pdf_to_markdown.py" \
    "$INPUT_ABS" \
    --parse-method "$METHOD" \
    --output-dir "$SCRIPT_DIR/output"

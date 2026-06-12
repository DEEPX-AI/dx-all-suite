#!/bin/bash
# =============================================================================
# run.sh — One-command PDF->Markdown on the DX-M1 NPU (RapidDoc PP-StructureV3)
#
#   ./run.sh [--input <pdf>] [--parse-method auto|txt|ocr] [--finegrained|--no-async]
#
# Defaults: --input sample_input.pdf, --parse-method auto, finegrained pipeline.
# Drives the RapidDoc fork's NPU pipeline: layout + OCR + table on dxengine (NPU),
# formula on onnxruntime (CPU). Output Markdown+JSON; the rendered .md is copied
# to ./sample_output.md and the per-stage timing report to ./timings.md.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
FORK_DIR="$SCRIPT_DIR/RapidDoc"

# --- Args --------------------------------------------------------------------
INPUT="$SCRIPT_DIR/sample_input.pdf"
PARSE_METHOD="auto"
PIPELINE_FLAG="--finegrained"
while [ $# -gt 0 ]; do
    case "$1" in
        --input)         INPUT="$2"; shift 2 ;;
        --parse-method)  PARSE_METHOD="$2"; shift 2 ;;
        --finegrained)   PIPELINE_FLAG="--finegrained"; shift ;;
        --use-async)     PIPELINE_FLAG="--use-async"; shift ;;
        --no-async)      PIPELINE_FLAG="--no-async"; shift ;;
        -h|--help)
            echo "Usage: ./run.sh [--input <pdf>] [--parse-method auto|txt|ocr] [--finegrained|--use-async|--no-async]"
            exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

case "$PARSE_METHOD" in auto|txt|ocr) ;; *) echo "ERROR: --parse-method must be auto|txt|ocr"; exit 1 ;; esac

# Resolve input to an absolute path: the demo runs with cwd=RapidDoc/, so a
# relative --input would otherwise be resolved against the fork dir and missed.
if [ -f "$INPUT" ]; then INPUT="$(cd "$(dirname "$INPUT")" && pwd -P)/$(basename "$INPUT")"; fi

# --- Suite root + venv (relocatable: local venv -> shared runtime venv) -------
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ] && break
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
RUNTIME_VENV="$SUITE_ROOT/dx-runtime/venv-dx-runtime"

if [ -x "$SCRIPT_DIR/venv/bin/python" ]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -x "$RUNTIME_VENV/bin/python" ]; then
    echo "[run] Local venv missing; falling back to shared runtime venv."
    # shellcheck disable=SC1091
    source "$RUNTIME_VENV/bin/activate"
else
    echo "ERROR: No venv found. Run ./setup.sh first."
    exit 1
fi

# --- Guards ------------------------------------------------------------------
if [ ! -d "$FORK_DIR" ]; then echo "ERROR: $FORK_DIR missing. Run ./setup.sh first."; exit 1; fi
if [ ! -f "$INPUT" ]; then echo "ERROR: input PDF not found: $INPUT"; exit 1; fi
if [ ! -d "$FORK_DIR/dxnn_models" ] || [ -z "$(ls -A "$FORK_DIR/dxnn_models" 2>/dev/null)" ]; then
    echo "ERROR: $FORK_DIR/dxnn_models is empty. Run ./setup.sh to download NPU models."; exit 1
fi
python -c "import dx_engine" 2>/dev/null || { echo "ERROR: dx_engine not importable. Run ./setup.sh."; exit 1; }

# --- DX-RT environment (required, or device init fails) ----------------------
# shellcheck disable=SC1091
source "$FORK_DIR/deepx_scripts/set_env.sh" 1 2 1 3 2 4
export DXNN_DEVICES="${DXNN_DEVICES:-0}"
echo "[run] DXNN_DEVICES=$DXNN_DEVICES  parse-method=$PARSE_METHOD  pipeline=$PIPELINE_FLAG"

# --- Run the NPU pipeline ----------------------------------------------------
OUT_DIR="$SCRIPT_DIR/output-$PARSE_METHOD"
rm -rf "$OUT_DIR"; mkdir -p "$OUT_DIR"
( cd "$FORK_DIR" && python demo/demo_offline.py "$INPUT" --parse-method "$PARSE_METHOD" $PIPELINE_FLAG --output-dir "$OUT_DIR" )

# --- Collect rendered Markdown + timing report -------------------------------
MD="$(find "$OUT_DIR" -name '*.md' ! -name 'performance_summary_*' ! -name 'sample_output.md' -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
if [ -n "${MD:-}" ] && [ -f "$MD" ]; then
    cp -f "$MD" "$SCRIPT_DIR/sample_output.md"
    echo "[run] sample_output.md <- $MD"
else
    echo "[run] WARNING: no Markdown produced under $OUT_DIR"
fi
PERF="$(find "$OUT_DIR" -name 'performance_summary_*.md' -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
if [ -n "${PERF:-}" ] && [ -f "$PERF" ]; then
    cp -f "$PERF" "$SCRIPT_DIR/timings.md"
    echo "[run] timings.md <- $PERF"
fi
echo "[run] DONE."

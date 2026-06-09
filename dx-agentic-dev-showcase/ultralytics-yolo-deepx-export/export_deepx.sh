#!/usr/bin/env bash
# Ultralytics YOLO -> DeepX one-shot export showcase.
# Converts yolo26n.pt to a deployable DeepX NPU model directory in a single command.
set -euo pipefail

MODEL="${MODEL:-yolo26n.pt}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
cd "$SCRIPT_DIR"

# --- HARD constraint: DeepX export (dx_com) is x86-64 Linux only ---
ARCH="$(uname -m)"
OS="$(uname -s)"
if [ "$OS" != "Linux" ] || { [ "$ARCH" != "x86_64" ] && [ "$ARCH" != "amd64" ]; }; then
    echo "ERROR: DeepX export requires x86-64 Linux (dx_com has no ARM64 support)."
    echo "       Detected: $OS / $ARCH. Run the export on an x86-64 Linux host."
    exit 1
fi

# --- venv (PEP 668-safe) ---
if [ ! -d venv ]; then
    python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate

# ultralytics pulls in dx_com automatically on the first format=deepx export.
pip install -q --upgrade pip
pip install -q ultralytics

# --- one-shot export: PT -> ONNX -> INT8 calibration -> dx_com -> package ---
# int8=True is enforced automatically for the deepx format.
echo "Exporting ${MODEL} to DeepX format (format=deepx)..."
yolo export model="${MODEL}" format=deepx

OUT="${MODEL%.pt}_deepx_model"
echo
echo "Done. Exported model directory: ${OUT}/"
ls -la "${OUT}/" 2>/dev/null || echo "(expected ${OUT}/ with <model>.dxnn, config.json, metadata.yaml)"

#!/usr/bin/env bash
# =============================================================================
# setup.sh — Environment setup for the RapidDoc PDF -> Markdown app (DX-M1 NPU)
#
# Steps:
#   1. Sanity: NPU runtime present (dx-runtime sanity check)
#   2. Create a self-contained session venv
#   3. Install the vendored RapidDoc pip dependencies (requirements.deepx.txt)
#   4. Bridge dx_engine (DX-M1 binding) from dx-runtime/venv-dx-runtime via a .pth
#   5. Download the NPU + ONNX models (foreground) via the fork's downloader
# (rapid_doc itself is imported via sys.path — no editable install needed.)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Auto-detect the dx-all-suite root (dx-runtime/ + dx-compiler/ siblings) ---
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: Cannot find dx-all-suite root (expected dx-runtime/ and dx-compiler/ siblings)"
    exit 1
fi
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
RUNTIME_VENV="$RUNTIME_DIR/venv-dx-runtime"

echo "============================================================"
echo " RapidDoc PDF->Markdown — setup.sh"
echo " SCRIPT_DIR  = $SCRIPT_DIR"
echo " SUITE_ROOT  = $SUITE_ROOT"
echo "============================================================"

# --- Step 1: NPU runtime sanity (informational; do not hard-fail the build) ---
echo "[1/5] dx-runtime sanity check (--dx_rt) ..."
if bash "$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt 2>&1 | tee /tmp/_rapiddoc_sanity.log | grep -q "Sanity check PASSED"; then
    echo "      NPU sanity: PASSED"
else
    echo "      WARNING: NPU sanity check did not report PASSED. Inference may fail."
fi

# --- Step 2: session venv ---
echo "[2/5] Creating session venv ..."
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
fi
# shellcheck disable=SC1091
source "$SCRIPT_DIR/venv/bin/activate"
python -m pip install --upgrade pip wheel setuptools >/dev/null

# --- Step 3: vendored RapidDoc deps ---
echo "[3/5] Installing RapidDoc dependencies (requirements.deepx.txt) ..."
pip install -r "$SCRIPT_DIR/requirements.deepx.txt"
# Note: the vendored rapid_doc is imported via sys.path (pdf_to_markdown.py inserts
# the app dir), so no `pip install -e .` is needed — that keeps the app self-contained.

# --- Step 4: dx_engine bridge (.pth into the session venv site-packages) ---
echo "[4/5] Bridging dx_engine from venv-dx-runtime ..."
RT_SITE="$(ls -d "$RUNTIME_VENV"/lib/python3.*/site-packages 2>/dev/null | head -1)"
if [ -z "$RT_SITE" ] || [ ! -d "$RT_SITE/dx_engine" ]; then
    echo "ERROR: dx_engine not found under $RUNTIME_VENV. Build dx-runtime first."
    exit 1
fi
SESSION_SITE="$(python -c 'import site; print(site.getsitepackages()[0])')"
echo "$RT_SITE" > "$SESSION_SITE/dxengine_bridge.pth"
echo "      bridge: $SESSION_SITE/dxengine_bridge.pth -> $RT_SITE"
python -c "import dx_engine; print('      dx_engine OK', getattr(dx_engine,'__version__','?'))"

# --- Step 5: download NPU + ONNX models (foreground, never background) ---
echo "[5/5] Downloading NPU + ONNX models (setup_sample_models.sh, foreground) ..."
chmod +x "$SCRIPT_DIR"/*.sh "$SCRIPT_DIR"/deepx_scripts/*.sh 2>/dev/null || true
# Skip ONLY when BOTH model sets are present — the download provides dxnn_models/ AND
# onnx_models/ (the formula model `onnx_models/pp_formulanet_plus_m.onnx` lives in the
# latter). Keying the skip on dxnn_models alone leaves onnx_models/ empty after a partial
# download and run.sh then fails with a missing-formula-model FileNotFoundError.
if [ -n "$(ls -A "$SCRIPT_DIR/dxnn_models" 2>/dev/null)" ] && \
   [ -n "$(ls -A "$SCRIPT_DIR/onnx_models" 2>/dev/null)" ]; then
    echo "      dxnn_models/ + onnx_models/ already present — skipping download."
else
    ( cd "$SCRIPT_DIR" && ./setup_sample_models.sh --output="$SCRIPT_DIR" --force )
fi

echo "============================================================"
echo " setup.sh complete."
echo "   dxnn_models : $(ls "$SCRIPT_DIR/dxnn_models" 2>/dev/null | wc -l) files"
echo "   onnx_models : $(ls "$SCRIPT_DIR/onnx_models" 2>/dev/null | wc -l) files"
echo "   Run inference with: ./run.sh"
echo "============================================================"
